#!/usr/bin/env python3
"""Two clean-root CockroachDB P6 atomic transaction trials."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from state_machine import LANES, load_canonical, sha256_hex

BASE = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
BIN = next(path for path in BASE.glob("p2-cleanroom/vendor/**/cockroach")
           if "darwin" in str(path))
P3_MIGRATION = BASE / "p3-ledger/migrations/001_ledger.sql"
P6_MIGRATION = HERE / "migrations/001_quorum.sql"
FIXTURES = HERE / "fixtures"


def quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def sql(port: int, statement: str, database: str | None = None,
        expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    args = [str(BIN), "sql", "--insecure", f"--host=127.0.0.1:{port}"]
    if database:
        args.append(f"--database={database}")
    args += ["-e", statement]
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False)
    if expect_ok and result.returncode != 0:
        raise RuntimeError(result.stdout)
    return result


def apply_file(port: int, database: str, path: Path) -> None:
    subprocess.run(
        [str(BIN), "sql", "--insecure", f"--host=127.0.0.1:{port}",
         f"--database={database}", f"--file={path}"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def transaction_sql(intent: dict, receipt: dict, bad_receipt_hash: bool = False) -> str:
    decision = intent["decision_record"]
    receipt_hash = "00" if bad_receipt_hash else receipt["receipt_hash"]
    return (
        "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
        "INSERT INTO p6_transitions VALUES "
        "(%s,%s,%s,%s,%s,decode(%s,'hex'),%s::JSONB,'2026-07-25 00:02:00+00') "
        "ON CONFLICT (task_id) DO NOTHING;"
        "INSERT INTO p6_transition_receipts VALUES "
        "(%s,%s,%s,%s::JSONB,decode(%s,'hex'),'2026-07-25 00:02:01+00') "
        "ON CONFLICT (intent_id) DO NOTHING;"
        "COMMIT;" % (
            quote(decision["task_id"]), quote(intent["intent_id"]),
            quote(decision["candidate_id"]), quote(decision["decision"]),
            quote(decision["reason"]), quote(intent["decision_hash"]),
            quote(json.dumps(decision)), quote(intent["intent_id"]),
            quote(decision["task_id"]), quote(receipt["receipt_id"]),
            quote(json.dumps(receipt)), quote(receipt_hash)))


def trial(label: str, port: int, http_port: int) -> dict[str, object]:
    root = Path(tempfile.mkdtemp(prefix=f"{label}.", dir=HERE))
    fake_home = root / "empty-home"
    fake_home.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(fake_home)
    log_handle = None
    process = None
    try:
        log_handle = (root / "cockroach.log").open("w", encoding="utf-8")
        process = subprocess.Popen(
            [str(BIN), "start-single-node", "--insecure", f"--store={root / 'store'}",
             f"--listen-addr=127.0.0.1:{port}",
             f"--http-addr=127.0.0.1:{http_port}"],
            stdout=log_handle, stderr=subprocess.STDOUT, env=env)
        for _ in range(30):
            if sql(port, "SELECT 1", expect_ok=False).returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("CockroachDB did not become ready")

        database = "p6quorum"
        sql(port, f"CREATE DATABASE {database}")
        apply_file(port, database, P3_MIGRATION)
        apply_file(port, database, P6_MIGRATION)

        declared = {"scope": "synthetic-p6", "state": "quorum"}
        state_hash = sha256_hex(declared)
        sql(port,
            "INSERT INTO tasks VALUES "
            "('task-p6-synthetic-001','p6-v1',decode(%s,'hex'),%s::JSONB,"
            "'2026-07-25 00:00:00+00')" %
            (quote(state_hash), quote(json.dumps(declared))), database)
        parent_receipt = sha256_hex({"candidate": "cand-p6-synthetic-001"})
        sql(port,
            "INSERT INTO candidates VALUES "
            "('cand-p6-synthetic-001','task-p6-synthetic-001','synthetic-parent',"
            "'[]'::JSONB,decode(%s,'hex'),decode(%s,'hex'),'policy-p6-v1',"
            "'REFUSE','QUORUM_MISSING','synthetic','2026-07-25 00:00:01+00')" %
            (quote(state_hash), quote(parent_receipt)), database)

        handoffs = [load_canonical(str(FIXTURES / "handoff-thinker-to-worker.json")),
                    load_canonical(str(FIXTURES / "handoff-worker-to-verifier.json"))]
        for offset, handoff in enumerate(handoffs, start=2):
            parent_handoff = ("NULL" if handoff["parent_handoff_hash"] is None
                              else "decode(%s,'hex')" % quote(handoff["parent_handoff_hash"]))
            parent_receipt_sql = ("NULL" if handoff["parent_receipt_hash"] is None
                                  else "decode(%s,'hex')" % quote(handoff["parent_receipt_hash"]))
            sql(port,
                "INSERT INTO p6_handoffs VALUES "
                "(%s,%s,%s,%s,%s::JSONB,decode(%s,'hex'),%s,%s,%s)" % (
                    quote(handoff["handoff_id"]), quote(handoff["task_id"]),
                    quote(handoff["stage"]), quote(handoff["candidate_id"]),
                    quote(json.dumps(handoff)), quote(sha256_hex(handoff)),
                    parent_handoff, parent_receipt_sql,
                    quote(f"2026-07-25 00:00:{offset:02d}+00")), database)

        votes = load_canonical(str(FIXTURES / "votes-ordinary-approval.json"))
        for offset, vote in enumerate(votes, start=10):
            sql(port,
                "INSERT INTO p6_votes VALUES "
                "(%s,%s,%s,%s,%s::JSONB,decode(%s,'hex'),%s)" % (
                    quote(vote["vote_id"]), quote(vote["task_id"]),
                    quote(vote["candidate_id"]), quote(vote["lane"]),
                    quote(json.dumps(vote)), quote(sha256_hex(vote)),
                    quote(f"2026-07-25 00:00:{offset:02d}+00")), database)

        intent = load_canonical(str(FIXTURES / "intent-ordinary-approval.json"))
        receipt = load_canonical(str(FIXTURES / "receipt-ordinary-approval.json"))

        interrupted = sql(port, transaction_sql(intent, receipt, bad_receipt_hash=True),
                          database, expect_ok=False)
        after_interrupt = sql(
            port,
            "SELECT (SELECT count(*) FROM p6_transitions),"
            "(SELECT count(*) FROM p6_transition_receipts)", database
        ).stdout.strip().splitlines()[-1].strip()

        rollback = sql(
            port,
            "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
            "INSERT INTO p6_transitions VALUES "
            "('task-p6-synthetic-001','intent-rollback','cand-p6-synthetic-001',"
            "'REFUSE','TEST_ROLLBACK',decode(%s,'hex'),'{}'::JSONB,"
            "'2026-07-25 00:02:00+00');ROLLBACK;" % quote(sha256_hex({"rollback": True})),
            database)
        after_rollback = sql(
            port, "SELECT count(*) FROM p6_transitions", database
        ).stdout.strip().splitlines()[-1].strip()

        first_commit = sql(port, transaction_sql(intent, receipt), database)
        retry_commit = sql(port, transaction_sql(intent, receipt), database)
        counts = sql(
            port,
            "SELECT (SELECT count(*) FROM p6_handoffs),"
            "(SELECT count(*) FROM p6_votes),"
            "(SELECT count(*) FROM p6_transitions),"
            "(SELECT count(*) FROM p6_transition_receipts)", database
        ).stdout.strip().splitlines()[-1].strip()
        linked = sql(
            port,
            "SELECT encode(t.decision_hash,'hex'),encode(r.receipt_hash,'hex') "
            "FROM p6_transitions t JOIN p6_transition_receipts r USING (intent_id)",
            database).stdout
        sql(port, f"DROP DATABASE {database} CASCADE")
        return {
            "label": label,
            "interrupted_rejected": interrupted.returncode != 0,
            "after_interrupt": after_interrupt,
            "rollback_exit": rollback.returncode,
            "after_rollback": after_rollback,
            "first_commit_exit": first_commit.returncode,
            "retry_commit_exit": retry_commit.returncode,
            "counts": counts,
            "decision_hash_present": intent["decision_hash"] in linked,
            "receipt_hash_present": receipt["receipt_hash"] in linked,
            "lanes": list(LANES),
        }
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if log_handle is not None:
            log_handle.close()
        shutil.rmtree(root)


if __name__ == "__main__":
    outputs = [trial("p6-db-a", 28267, 8291), trial("p6-db-b", 28268, 8292)]
    comparable = [{key: value for key, value in item.items() if key != "label"}
                  for item in outputs]
    assert comparable[0] == comparable[1], comparable
    assert all(item["interrupted_rejected"] and item["after_interrupt"] == "0\t0"
               and item["after_rollback"] == "0" and item["counts"] == "2\t5\t1\t1"
               and item["decision_hash_present"] and item["receipt_hash_present"]
               for item in outputs), outputs
    print(json.dumps(outputs, sort_keys=True, separators=(",", ":")))
