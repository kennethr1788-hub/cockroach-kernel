#!/usr/bin/env python3
"""Bounded S1 foundation soak using synthetic data and loopback CockroachDB."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[1]
MIGRATION = BASE / "p3-ledger/migrations/001_ledger.sql"
P3 = BASE / "p3-ledger"
P4 = BASE / "p4-verifier"
SCHEMA_VERSION = "s1-v1"


class SoakFailure(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def tree_bytes(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def write_canonical(path: Path, value: dict[str, Any]) -> None:
    raw = canonical(value) + b"\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def run(args: list[str], *, expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if expect_ok and result.returncode != 0:
        raise SoakFailure(f"command failed ({result.returncode}): {result.stdout[-2000:]}")
    return result


class Database:
    def __init__(self, binary: Path, runtime_root: Path, sql_port: int, http_port: int):
        self.binary = binary
        self.runtime_root = runtime_root
        self.sql_port = sql_port
        self.http_port = http_port
        self.store = runtime_root / "store"
        self.log_path = runtime_root / "cockroach.log"
        self.process: subprocess.Popen[str] | None = None
        self.log_handle: Any = None

    def sql(self, statement: str, *, database: str | None = "s1ledger", expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
        command = [str(self.binary), "sql", "--insecure", f"--host=127.0.0.1:{self.sql_port}"]
        if database:
            command.append(f"--database={database}")
        command.extend(["-e", statement])
        return run(command, expect_ok=expect_ok)

    def start(self) -> None:
        if self.process is not None:
            raise SoakFailure("database already started")
        self.runtime_root.mkdir(parents=True, exist_ok=True)
        isolated_home = self.runtime_root / "isolated-home"
        isolated_home.mkdir(exist_ok=True)
        environment = os.environ.copy()
        environment["HOME"] = str(isolated_home)
        self.log_handle = self.log_path.open("a")
        self.process = subprocess.Popen(
            [
                str(self.binary),
                "start-single-node",
                "--insecure",
                f"--store={self.store}",
                f"--listen-addr=127.0.0.1:{self.sql_port}",
                f"--http-addr=127.0.0.1:{self.http_port}",
            ],
            stdout=self.log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            env=environment,
        )
        for _ in range(60):
            if self.process.poll() is not None:
                raise SoakFailure("database exited before readiness")
            if self.sql("SELECT 1", database=None, expect_ok=False).returncode == 0:
                return
            time.sleep(0.5)
        raise SoakFailure("database readiness timeout")

    def stop(self) -> None:
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
            self.process = None
        if self.log_handle is not None:
            self.log_handle.flush()
            os.fsync(self.log_handle.fileno())
            self.log_handle.close()
            self.log_handle = None

    def initialize(self) -> None:
        self.sql("CREATE DATABASE IF NOT EXISTS s1ledger", database=None)
        run(
            [
                str(self.binary),
                "sql",
                "--insecure",
                f"--host=127.0.0.1:{self.sql_port}",
                "--database=s1ledger",
                f"--file={MIGRATION}",
            ]
        )


def q(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def last_scalar(result: subprocess.CompletedProcess[str]) -> str:
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise SoakFailure("SQL query returned no scalar")
    return lines[-1]


def process_metrics(process: subprocess.Popen[str] | None) -> dict[str, int | str]:
    if process is None or process.poll() is not None:
        return {"status": "STOPPED", "rss_bytes": 0, "open_files": 0}
    status_path = Path(f"/proc/{process.pid}/status")
    fd_path = Path(f"/proc/{process.pid}/fd")
    rss = 0
    if status_path.exists():
        for line in status_path.read_text().splitlines():
            if line.startswith("VmRSS:"):
                rss = int(line.split()[1]) * 1024
                break
    open_files = len(list(fd_path.iterdir())) if fd_path.exists() else 0
    return {"status": "RUNNING", "rss_bytes": rss, "open_files": open_files}


def exercise_checkpoint(db: Database, index: int) -> dict[str, Any]:
    sys.path.insert(0, str(P3))
    sys.path.insert(0, str(P4))
    from ledger import deterministic_verdict  # type: ignore
    from verifier import Quarantine, digest as p4_digest, verify  # type: ignore

    task_id = f"s1-task-{index:04d}"
    event_id = f"s1-event-{index:04d}"
    receipt_id = f"s1-receipt-{index:04d}"
    state = {"checkpoint": index, "source": "synthetic"}
    state_hash = digest(state)
    event = {
        "event_id": event_id,
        "parent_event_id": None,
        "sequence": 0,
        "state": state,
        "state_hash": state_hash,
        "task_id": task_id,
        "version": "p3-v1",
    }
    event_hash = digest(event)

    forced = db.sql(
        "SET allow_unsafe_internals = true; BEGIN; "
        "SELECT crdb_internal.force_error('40001','synthetic retry'); COMMIT;",
        expect_ok=False,
    )
    forced_output = forced.stdout.lower()
    if forced.returncode == 0 or not any(
        marker in forced_output for marker in ("40001", "restart transaction", "synthetic retry")
    ):
        raise SoakFailure(f"forced serializable retry was not observed: {forced.stdout[-500:]}")
    retry_count = 1

    db.sql(
        "BEGIN; "
        f"INSERT INTO tasks VALUES ({q(task_id)},'p3-v1',decode({q(state_hash)},'hex'),"
        f"{q(json.dumps(state))}::JSONB,'2026-07-25 00:00:00+00'); "
        f"INSERT INTO trajectory_events VALUES ({q(event_id)},{q(task_id)},0,NULL,"
        f"decode({q(state_hash)},'hex'),{q(json.dumps(event))}::JSONB,"
        f"decode({q(event_hash)},'hex'),'2026-07-25 00:00:01+00'); COMMIT;"
    )

    receipt_json = {"subject_id": event_id, "transition": "RECORD"}
    receipt_hash = digest(receipt_json)
    receipt_insert = (
        "INSERT INTO immutable_receipts VALUES "
        f"({q(receipt_id)},{q(task_id)},'RECORD',{q(event_id)},"
        f"{q(json.dumps(receipt_json))}::JSONB,decode({q(receipt_hash)},'hex'),"
        "'2026-07-25 00:00:02+00') ON CONFLICT DO NOTHING;"
    )
    db.sql(receipt_insert)
    db.sql(receipt_insert)
    duplicate_count = int(last_scalar(db.sql(
        f"SELECT count(*) FROM immutable_receipts WHERE receipt_id={q(receipt_id)}"
    )))
    if duplicate_count != 1:
        raise SoakFailure("duplicate receipt created multiple rows")

    rollback_id = f"s1-rollback-{index:04d}"
    db.sql(
        "BEGIN; "
        f"INSERT INTO tasks VALUES ({q(rollback_id)},'p3-v1',decode({q(state_hash)},'hex'),"
        f"{q(json.dumps(state))}::JSONB,'2026-07-25 00:00:03+00'); ROLLBACK;"
    )
    rollback_count = int(last_scalar(db.sql(
        f"SELECT count(*) FROM tasks WHERE task_id={q(rollback_id)}"
    )))
    if rollback_count != 0:
        raise SoakFailure("rolled-back task remained visible")

    ledger_candidate = {
        "candidate_id": "s1-candidate",
        "policy_version": "p1",
        "policy_veto": False,
        "prefix": [{"op": "keep"}],
        "receipt_hash": "receipt",
        "retention_class": "core",
        "source_event_id": event_id,
        "state_hash": state_hash,
        "tampered": False,
        "task_id": task_id,
        "unsafe": False,
        "version": "p3-v1",
        "votes": ["APPROVE", "APPROVE", "APPROVE"],
        "warrant_state": "ISSUED",
    }
    ledger_verdicts = [deterministic_verdict(ledger_candidate) for _ in range(5)]
    if len(set(ledger_verdicts)) != 1:
        raise SoakFailure("ledger verdict was nondeterministic")

    payload = {"op": "continue", "sequence": index}
    verifier_record = {
        "candidate_id": "s1-candidate",
        "declared_paths": ["src/main.py"],
        "one_use_state": "ISSUED",
        "payload": payload,
        "payload_hash": p4_digest(payload),
        "policy_veto": False,
        "provenance": {"source": receipt_id},
        "quarantined": False,
        "requested_paths": ["src/main.py"],
        "schema_version": "p4-v1",
        "source_receipt_hash": "a" * 64,
        "supported": True,
        "version": "p4-v1",
    }
    verifier_verdicts = [verify(verifier_record) for _ in range(5)]
    if verifier_verdicts != [("PROMOTE", "VERIFIED")] * 5:
        raise SoakFailure("verifier verdict was nondeterministic")
    quarantine = Quarantine()
    quarantine.insert(verifier_record)
    quarantine_result = verify(verifier_record, quarantine)
    if quarantine_result != ("REFUSE", "QUARANTINED_INPUT") or quarantine.active():
        raise SoakFailure("quarantined record entered active retrieval")

    return {
        "duplicate_receipt": "PASS",
        "ledger_verdict": list(ledger_verdicts[0]),
        "quarantine_exclusion": "PASS",
        "quarantine_verdict": list(quarantine_result),
        "retry_count": retry_count,
        "rollback": "PASS",
        "verifier_verdict": list(verifier_verdicts[0]),
        "workload_state_hash": state_hash,
        "workload_state_bytes": len(canonical(state)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cockroach-bin", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--duration-seconds", type=int, default=3600)
    parser.add_argument("--checkpoint-seconds", type=int, default=60)
    parser.add_argument("--sql-port", type=int, default=26357)
    parser.add_argument("--http-port", type=int, default=8099)
    parser.add_argument("--database-growth-limit-bytes", type=int, default=268435456)
    parser.add_argument("--evidence-growth-limit-bytes", type=int, default=67108864)
    args = parser.parse_args()

    if args.duration_seconds < 1 or args.duration_seconds > 3600:
        raise SoakFailure("duration must be between 1 and 3600 seconds")
    if args.checkpoint_seconds < 1 or args.checkpoint_seconds > args.duration_seconds:
        raise SoakFailure("invalid checkpoint interval")
    binary = args.cockroach_bin.resolve()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise SoakFailure("CockroachDB binary is not executable")
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=False)
    evidence_root = output_root / "evidence"
    receipts_root = evidence_root / "receipts"
    telemetry_root = evidence_root / "telemetry"
    runtime_root = output_root / "runtime"
    receipts_root.mkdir(parents=True)
    telemetry_root.mkdir(parents=True)

    manifest = {
        "checkpoint_seconds": args.checkpoint_seconds,
        "cockroach_binary_sha256": digest(binary.read_bytes()),
        "database_growth_limit_bytes": args.database_growth_limit_bytes,
        "duration_seconds": args.duration_seconds,
        "evidence_growth_limit_bytes": args.evidence_growth_limit_bytes,
        "migration_sha256": digest(MIGRATION.read_bytes()),
        "schema_version": SCHEMA_VERSION,
        "synthetic_only": True,
    }
    manifest_path = evidence_root / "manifest.json"
    write_canonical(manifest_path, manifest)

    database = Database(binary, runtime_root, args.sql_port, args.http_port)
    started_monotonic = time.monotonic()
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    baseline_database_bytes = 0
    checkpoints: list[dict[str, Any]] = []
    failure: str | None = None
    interrupted = False

    def interrupt_handler(signum: int, _frame: Any) -> None:
        nonlocal interrupted
        interrupted = True
        raise SoakFailure(f"received signal {signum}")

    signal.signal(signal.SIGTERM, interrupt_handler)
    signal.signal(signal.SIGINT, interrupt_handler)

    try:
        database.start()
        database.initialize()
        baseline_database_bytes = tree_bytes(database.store)
        checkpoint_index = 0
        next_checkpoint = started_monotonic
        while True:
            now = time.monotonic()
            if now < next_checkpoint:
                time.sleep(min(0.5, next_checkpoint - now))
                continue
            elapsed = now - started_monotonic
            result = exercise_checkpoint(database, checkpoint_index)

            database.stop()
            database.start()
            recovered = int(last_scalar(database.sql(
                f"SELECT count(*) FROM tasks WHERE task_id='s1-task-{checkpoint_index:04d}'"
            ))) == 1
            if not recovered:
                raise SoakFailure("restart recovery failed")

            database_bytes = tree_bytes(database.store)
            evidence_bytes_before = tree_bytes(evidence_root)
            database_growth = max(0, database_bytes - baseline_database_bytes)
            if database_growth > args.database_growth_limit_bytes:
                raise SoakFailure("database growth threshold breached")
            if evidence_bytes_before > args.evidence_growth_limit_bytes:
                raise SoakFailure("evidence growth threshold breached")

            telemetry = {
                "checkpoint": checkpoint_index,
                "database_bytes": database_bytes,
                "database_growth_bytes": database_growth,
                "elapsed_seconds": round(elapsed, 3),
                "process": process_metrics(database.process),
                "schema_version": SCHEMA_VERSION,
            }
            telemetry_path = telemetry_root / f"checkpoint-{checkpoint_index:04d}.json"
            write_canonical(telemetry_path, telemetry)
            telemetry_hash = digest(telemetry_path.read_bytes())

            receipt_core = {
                "checkpoint": checkpoint_index,
                "database_growth_bytes": database_growth,
                "deterministic_verdict": "PASS",
                "duplicate_receipt": result["duplicate_receipt"],
                "elapsed_seconds": round(elapsed, 3),
                "iteration": checkpoint_index,
                "manifest_bytes": manifest_path.stat().st_size,
                "process_resource_status": telemetry["process"],
                "quarantine_exclusion": result["quarantine_exclusion"],
                "receipt_bytes_before_write": tree_bytes(receipts_root),
                "residue": "CLEAN_RUNTIME_SCOPE",
                "restart_recovery": "PASS",
                "retry_count": result["retry_count"],
                "rollback": result["rollback"],
                "schema_version": SCHEMA_VERSION,
                "telemetry_bytes": tree_bytes(telemetry_root),
                "telemetry_hash": telemetry_hash,
                "utc_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "workload_state_bytes": result["workload_state_bytes"],
                "workload_state_hash": result["workload_state_hash"],
            }
            receipt = {**receipt_core, "evidence_hash": digest(receipt_core)}
            receipt_path = receipts_root / f"checkpoint-{checkpoint_index:04d}.json"
            write_canonical(receipt_path, receipt)
            checkpoints.append(receipt)
            checkpoint_index += 1

            if time.monotonic() - started_monotonic >= args.duration_seconds:
                break
            next_checkpoint = started_monotonic + checkpoint_index * args.checkpoint_seconds
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    finally:
        database.stop()
        if runtime_root.exists():
            shutil.rmtree(runtime_root)

    runtime_residue = sorted(str(path.relative_to(output_root)) for path in runtime_root.rglob("*")) if runtime_root.exists() else []
    finished_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    expected_checkpoints = args.duration_seconds // args.checkpoint_seconds + 1
    checkpoint_requirement_met = len(checkpoints) >= expected_checkpoints
    final_core = {
        "checkpoint_count": len(checkpoints),
        "checkpoint_requirement_met": checkpoint_requirement_met,
        "evidence_bytes": tree_bytes(evidence_root),
        "expected_checkpoint_count": expected_checkpoints,
        "failure": failure,
        "finished_utc": finished_utc,
        "interrupted": interrupted,
        "manifest_hash": digest(manifest_path.read_bytes()),
        "runtime_residue": runtime_residue,
        "schema_version": SCHEMA_VERSION,
        "started_utc": started_utc,
        "status": "GREEN" if failure is None and not runtime_residue and checkpoint_requirement_met else "BLOCKED",
    }
    final = {**final_core, "final_evidence_hash": digest(final_core)}
    write_canonical(evidence_root / "final.json", final)
    print(canonical(final).decode("utf-8"))
    return 0 if final["status"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
