#!/usr/bin/env python3
"""Two fresh-root CockroachDB P8 promotion and rollback trials."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import golden as g
import make_fixtures as fx

BASE = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
BIN = next(path for path in BASE.glob("p2-cleanroom/vendor/**/cockroach")
           if "darwin" in str(path))
MIGRATION = HERE / "migrations/001_golden.sql"


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
    subprocess.run([str(BIN), "sql", "--insecure", f"--host=127.0.0.1:{port}",
                    f"--database={database}", f"--file={path}"], check=True,
                   text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def data_line(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def promotion_sql(result: dict, bad_receipt: bool = False) -> str:
    proposal = fx.PROPOSALS["proposal-safe"]
    receipt = result["receipt"]
    golden_pair = result["golden_pair"]
    receipt_hash = "00" if bad_receipt else receipt["receipt_hash"]
    return (
        "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
        "UPDATE p8_policies SET status='SUPERSEDED' WHERE policy_id=%s AND status='GOLDEN';"
        "INSERT INTO p8_policies VALUES (%s,%s::JSONB,decode(%s,'hex'),'GOLDEN') "
        "ON CONFLICT (policy_id) DO NOTHING;"
        "INSERT INTO p8_proposals VALUES (%s,%s::JSONB,decode(%s,'hex'),'PROMOTE',%s) "
        "ON CONFLICT (proposal_id) DO NOTHING;"
        "INSERT INTO p8_promotions VALUES (%s,%s,%s,decode(%s,'hex'),%s::JSONB,%s::JSONB,decode(%s,'hex')) "
        "ON CONFLICT (proposal_id) DO NOTHING;COMMIT;" % (
            quote(fx.BASE_POLICY["policy_id"]),
            quote(fx.SAFE_POLICY["policy_id"]), quote(json.dumps(fx.SAFE_POLICY)),
            quote(g.sha256_hex(fx.SAFE_POLICY)), quote(proposal["proposal_id"]),
            quote(json.dumps(proposal)), quote(g.sha256_hex(proposal)),
            quote(receipt["reason"]), quote(proposal["proposal_id"]),
            quote(fx.BASE_POLICY["policy_id"]), quote(fx.SAFE_POLICY["policy_id"]),
            quote(receipt["replay_hash"]), quote(json.dumps(golden_pair)),
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
            env=env, text=True, stdout=log_handle, stderr=subprocess.STDOUT)
        for _ in range(30):
            if sql(port, "SELECT 1", expect_ok=False).returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("CockroachDB did not become ready")

        database = "p8golden"
        sql(port, f"CREATE DATABASE {database}")
        apply_file(port, database, MIGRATION)
        set_hash = g.incident_set_hash(fx.INCIDENTS)
        sql(port, "INSERT INTO p8_policies VALUES (%s,%s::JSONB,decode(%s,'hex'),'GOLDEN')" % (
            quote(fx.BASE_POLICY["policy_id"]), quote(json.dumps(fx.BASE_POLICY)),
            quote(g.sha256_hex(fx.BASE_POLICY))), database)
        sql(port, "INSERT INTO p8_incident_sets VALUES (decode(%s,'hex'),%s::JSONB)" % (
            quote(set_hash), quote(json.dumps(fx.INCIDENTS))), database)

        results = {name: g.replay_proposal(proposal, fx.BASE_POLICY, fx.INCIDENTS)
                   for name, proposal in fx.PROPOSALS.items()}
        for name, result in sorted(results.items()):
            if name == "proposal-safe":
                continue
            receipt = result["receipt"] if "receipt" in result else result
            sql(port, "INSERT INTO p8_proposals VALUES (%s,%s::JSONB,decode(%s,'hex'),'REJECT',%s)" % (
                quote(fx.PROPOSALS[name]["proposal_id"]),
                quote(json.dumps(fx.PROPOSALS[name])),
                quote(g.sha256_hex(fx.PROPOSALS[name])), quote(receipt["reason"])), database)

        interrupted = sql(port, promotion_sql(results["proposal-safe"], bad_receipt=True),
                          database, expect_ok=False)
        after_interrupt = data_line(sql(
            port, "SELECT (SELECT count(*) FROM p8_policies WHERE policy_id='policy-p8-v2'),"
                  "(SELECT count(*) FROM p8_proposals WHERE proposal_id='proposal-safe'),"
                  "(SELECT count(*) FROM p8_promotions)", database).stdout)

        first = sql(port, promotion_sql(results["proposal-safe"]), database)
        duplicate = sql(port, promotion_sql(results["proposal-safe"]), database)
        after_promotion = data_line(sql(
            port, "SELECT (SELECT count(*) FROM p8_policies WHERE status='GOLDEN'),"
                  "(SELECT count(*) FROM p8_proposals),"
                  "(SELECT count(*) FROM p8_promotions)", database).stdout)

        rollback = g.build_rollback_receipt(results["proposal-safe"]["receipt"],
                                            fx.SAFE_POLICY, fx.BASE_POLICY)
        sql(port,
            "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
            "UPDATE p8_policies SET status='SUPERSEDED' WHERE policy_id=%s AND status='GOLDEN';"
            "UPDATE p8_policies SET status='GOLDEN' WHERE policy_id=%s AND status='SUPERSEDED';"
            "INSERT INTO p8_rollbacks VALUES ('rollback-p8-001',decode(%s,'hex'),%s,%s,%s::JSONB,decode(%s,'hex'));"
            "COMMIT;" % (
                quote(fx.SAFE_POLICY["policy_id"]), quote(fx.BASE_POLICY["policy_id"]),
                quote(results["proposal-safe"]["receipt"]["receipt_hash"]),
                quote(fx.SAFE_POLICY["policy_id"]), quote(fx.BASE_POLICY["policy_id"]),
                quote(json.dumps(rollback)), quote(rollback["receipt_hash"])), database)
        after_rollback = data_line(sql(
            port, "SELECT policy_id FROM p8_policies WHERE status='GOLDEN'", database).stdout)
        duplicate_rollback = sql(
            port,
            "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
            "UPDATE p8_policies SET status='SUPERSEDED' WHERE policy_id=%s AND status='GOLDEN';"
            "UPDATE p8_policies SET status='GOLDEN' WHERE policy_id=%s AND status='SUPERSEDED';"
            "INSERT INTO p8_rollbacks VALUES ('rollback-p8-001',decode(%s,'hex'),%s,%s,%s::JSONB,decode(%s,'hex'));"
            "COMMIT;" % (
                quote(fx.SAFE_POLICY["policy_id"]), quote(fx.BASE_POLICY["policy_id"]),
                quote(results["proposal-safe"]["receipt"]["receipt_hash"]),
                quote(fx.SAFE_POLICY["policy_id"]), quote(fx.BASE_POLICY["policy_id"]),
                quote(json.dumps(rollback)), quote(rollback["receipt_hash"])),
            database, expect_ok=False)
        after_duplicate_rollback = data_line(sql(
            port, "SELECT policy_id FROM p8_policies WHERE status='GOLDEN'", database).stdout)
        counts = data_line(sql(port,
            "SELECT (SELECT count(*) FROM p8_policies),"
            "(SELECT count(*) FROM p8_incident_sets),"
            "(SELECT count(*) FROM p8_proposals),"
            "(SELECT count(*) FROM p8_promotions),"
            "(SELECT count(*) FROM p8_rollbacks)", database).stdout)
        sql(port, f"DROP DATABASE {database} CASCADE")
        return {
            "label": label,
            "interrupted_rejected": interrupted.returncode != 0,
            "after_interrupt": after_interrupt,
            "first_commit_exit": first.returncode,
            "duplicate_commit_exit": duplicate.returncode,
            "after_promotion": after_promotion,
            "after_rollback": after_rollback,
            "duplicate_rollback_rejected": duplicate_rollback.returncode != 0,
            "after_duplicate_rollback": after_duplicate_rollback,
            "counts": counts,
            "proposal_outcomes": {
                name: ((value["receipt"] if "receipt" in value else value)["outcome"])
                for name, value in sorted(results.items())
            },
            "incident_set_hash": set_hash,
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
    outputs = [trial("p8-db-a", 28271, 8295), trial("p8-db-b", 28272, 8296)]
    comparable = [{key: value for key, value in item.items() if key != "label"}
                  for item in outputs]
    assert comparable[0] == comparable[1], outputs
    assert all(item["interrupted_rejected"] and item["after_interrupt"] == "0\t0\t0"
               and item["first_commit_exit"] == 0 and item["duplicate_commit_exit"] == 0
               and item["after_promotion"] == "1\t8\t1"
               and item["after_rollback"] == fx.BASE_POLICY["policy_id"]
               and item["duplicate_rollback_rejected"]
               and item["after_duplicate_rollback"] == fx.BASE_POLICY["policy_id"]
               and item["counts"] == "2\t1\t8\t1\t1"
               and item["proposal_outcomes"]["proposal-safe"] == "PROMOTE"
               and all(outcome == "REJECT" for name, outcome in item["proposal_outcomes"].items()
                       if name != "proposal-safe")
               for item in outputs), outputs
    print(json.dumps(outputs, sort_keys=True, separators=(",", ":")))
