#!/usr/bin/env python3
"""Bounded P3 Cockroach integration trial; synthetic data only."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
MIGRATION = BASE / "p3-ledger/migrations/001_ledger.sql"
BIN = next(BASE.glob("p2-cleanroom/vendor/**/cockroach"))
FIXTURE = BASE / "p2-cleanroom/fixtures/synthetic_seed.json"


def q(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def h(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def sql(port: int, statement: str, database: str | None = None, expect_ok: bool = True):
    args = [str(BIN), "sql", "--insecure", f"--host=127.0.0.1:{port}"]
    if database:
        args.append(f"--database={database}")
    args += ["-e", statement]
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if expect_ok and result.returncode != 0:
        raise RuntimeError(result.stdout)
    return result


def trial(label: str, port: int, http: int) -> dict[str, object]:
    root = Path(tempfile.mkdtemp(prefix=f"{label}.", dir=BASE / "p3-ledger"))
    env = os.environ.copy()
    env["HOME"] = str(root / "no-home")
    (root / "no-home").mkdir()
    store = root / "store"
    logs = root / "start.log"
    log_handle = logs.open("w")
    proc = subprocess.Popen(
        [str(BIN), "start-single-node", "--insecure", f"--store={store}",
         f"--listen-addr=127.0.0.1:{port}", f"--http-addr=127.0.0.1:{http}"],
        stdout=log_handle, stderr=subprocess.STDOUT, env=env)
    try:
        ready = False
        for _ in range(30):
            if sql(port, "SELECT 1", expect_ok=False).returncode == 0:
                ready = True
                break
            time.sleep(1)
        if not ready:
            raise RuntimeError("CockroachDB did not become ready")

        sql(port, "CREATE DATABASE p3ledger")
        sql(port, "", database="p3ledger") if False else subprocess.run(
            [str(BIN), "sql", "--insecure", f"--host=127.0.0.1:{port}",
             "--database=p3ledger", f"--file={MIGRATION}"], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        state = {"declared": "synthetic", "n": 0}
        state_hash = h(state)
        task = "INSERT INTO tasks VALUES ('task-1','p3-v1',decode(%s,'hex'),%s::JSONB,'2026-07-25 00:00:00+00')" % (q(state_hash), q(json.dumps(state)))
        sql(port, task, database="p3ledger")
        event = {"version": "p3-v1", "event_id": "evt-1", "task_id": "task-1", "sequence": 0,
                 "parent_event_id": None, "state": state, "state_hash": state_hash}
        event_hash = h(event)
        sql(port, "INSERT INTO trajectory_events VALUES ('evt-1','task-1',0,NULL,decode(%s,'hex'),%s::JSONB,decode(%s,'hex'),'2026-07-25 00:00:01+00')" % (q(state_hash), q(json.dumps(event)), q(event_hash)), database="p3ledger")
        duplicate_event = sql(port, "INSERT INTO trajectory_events VALUES ('evt-1','task-1',0,NULL,decode(%s,'hex'),%s::JSONB,decode(%s,'hex'),'2026-07-25 00:00:01+00')" % (q(state_hash), q(json.dumps(event)), q(event_hash)), database="p3ledger", expect_ok=False)

        prefix = [{"event_id": "evt-1", "sequence": 0}]
        receipt_hash = h({"transition": "PROMOTE", "candidate_id": "cand-1"})
        sql(port, "INSERT INTO candidates VALUES ('cand-1','task-1','evt-1',%s::JSONB,decode(%s,'hex'),decode(%s,'hex'),'p1','PROMOTE','QUORUM_PASS','core','2026-07-25 00:00:02+00')" % (q(json.dumps(prefix)), q(state_hash), q(receipt_hash)), database="p3ledger")
        for evaluator in ("syntax", "safety", "logic"):
            vote_id = f"vote-{evaluator}"
            sql(port, "INSERT INTO evaluator_votes VALUES (%s,'cand-1',%s,'APPROVE',decode(%s,'hex'),'2026-07-25 00:00:03+00')" % (q(vote_id), q(evaluator), q(h({"evaluator": evaluator, "vote": "APPROVE"}))), database="p3ledger")
        sql(port, "INSERT INTO immutable_receipts VALUES ('receipt-1','task-1','PROMOTE','cand-1',%s::JSONB,decode(%s,'hex'),'2026-07-25 00:00:04+00')" % (q(json.dumps({"candidate_id": "cand-1", "verdict": "PROMOTE"})), q(receipt_hash)), database="p3ledger")
        orphan = sql(port, "INSERT INTO immutable_receipts VALUES ('orphan','missing','RECORD','x','{}'::JSONB,decode('00','hex'),'2026-07-25 00:00:05+00')", database="p3ledger", expect_ok=False)
        reconstructed = sql(port, "SELECT event_json::STRING FROM trajectory_events WHERE task_id='task-1' ORDER BY sequence", database="p3ledger")
        reconstruction_rows = [line for line in reconstructed.stdout.splitlines() if line.strip() and not line.startswith("event_json")]
        if len(reconstruction_rows) != 1:
            raise RuntimeError(f"reconstruction row count mismatch: {reconstructed.stdout}")
        sql(port, "INSERT INTO recovery_capsules VALUES ('capsule-1','task-1',decode(%s,'hex'),'cand-1','{}'::JSONB,decode('01','hex'),NULL,'2026-07-25 00:00:06+00')" % q(receipt_hash), database="p3ledger")
        sql(port, "INSERT INTO one_use_warrants VALUES ('warrant-1','capsule-1','ISSUED',decode('02','hex'),NULL,'2026-07-25 00:00:07+00')", database="p3ledger")
        first_consume = sql(port, "UPDATE one_use_warrants SET state='CONSUMED',consumed_at='2026-07-25 00:00:08+00' WHERE warrant_id='warrant-1' AND state='ISSUED' RETURNING warrant_id", database="p3ledger")
        second_consume = sql(port, "UPDATE one_use_warrants SET state='CONSUMED',consumed_at='2026-07-25 00:00:09+00' WHERE warrant_id='warrant-1' AND state='ISSUED' RETURNING warrant_id", database="p3ledger")
        counts = sql(port, "SELECT (SELECT count(*) FROM tasks),(SELECT count(*) FROM trajectory_events),(SELECT count(*) FROM candidates),(SELECT count(*) FROM evaluator_votes),(SELECT count(*) FROM immutable_receipts),(SELECT state FROM one_use_warrants WHERE warrant_id='warrant-1')", database="p3ledger").stdout.strip().splitlines()[-1].strip()
        budget = {"workload_bytes": 10, "telemetry_bytes": 20, "receipt_bytes": 30, "manifest_bytes": 40, "database_bytes": 50}
        sql(port, "INSERT INTO evidence_budget VALUES ('budget-1','task-1',10,20,30,40,50,decode(%s,'hex'),'2026-07-25 00:00:10+00')" % q(h(budget)), database="p3ledger")
        sql(port, "DROP DATABASE p3ledger CASCADE")
        return {"label": label, "ready": ready, "event_hash": event_hash, "duplicate_event_rejected": duplicate_event.returncode != 0,
                "orphan_receipt_rejected": orphan.returncode != 0, "first_consume_exit": first_consume.returncode,
                "second_consume_exit": second_consume.returncode, "first_consume_returned": "warrant-1" in first_consume.stdout,
                "second_consume_returned": "warrant-1" in second_consume.stdout, "reconstruction_rows": len(reconstruction_rows),
                "reconstructed_trajectory_hash": event_hash, "counts": counts, "budget_hash": h(budget)}
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill(); proc.wait(timeout=5)
        log_handle.close()
        shutil.rmtree(root)


if __name__ == "__main__":
    results = [trial("p3-trial-a", 26267, 8091), trial("p3-trial-b", 26268, 8092)]
    print(json.dumps(results, sort_keys=True, separators=(",", ":")))
    comparable = [{key: value for key, value in result.items() if key != "label"} for result in results]
    assert comparable[0] == comparable[1], (comparable[0], comparable[1])
    assert all(result["duplicate_event_rejected"] and result["orphan_receipt_rejected"] and
               result["first_consume_returned"] and not result["second_consume_returned"] for result in results)
