#!/usr/bin/env python3
"""Representative-cardinality CockroachDB plan A/B for PDH-3 R12 PF-2.

Each scale uses a fresh generated root and an isolated single-node CockroachDB
v26.2.3 process.  Current plans and read-only results are frozen before either
candidate index is created.  The script never edits the product migration.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable


BASE = Path(__file__).resolve().parents[1]
PLAN_SHA256 = "a1214b4779fe1495de219ed0033421ac810390641cd97742deb61cd3957df3d9"
SCALES = (10_000, 50_000, 100_000)
RECEIPT_INDEX_DDL = (
    "CREATE INDEX receipts_task_id_idx ON ck.receipts(task_id) "
    "STORING(status,event_hash)"
)
PROJECTION_INDEX_DDL = (
    "CREATE INDEX projection_events_source_key_idx "
    "ON ck.projection_events(source_key)"
)


class PlanABError(RuntimeError):
    """Stable PF-2 error."""


def load_canary() -> Any:
    path = BASE / "post-dogfood/run_pdh3_local_canary.py"
    spec = importlib.util.spec_from_file_location("pdh3_r12_pf2_canary", path)
    if spec is None or spec.loader is None:
        raise PlanABError("CANARY_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(raw: bytes | Any) -> str:
    return hashlib.sha256(raw if isinstance(raw, bytes) else canonical(raw)).hexdigest()


def atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


def write_record(path: Path, body: dict[str, Any], field: str) -> dict[str, Any]:
    value = {**body, field: digest(body)}
    atomic_write(path, canonical(value))
    return value


def full_scan(plan: str) -> bool:
    lowered = plan.lower()
    return "full scan" in lowered or bool(
        re.search(r"spans?\s*:\s*(?:all|full)", lowered)
    )


def query_definitions(campaign: str, width: int = 6) -> dict[str, str]:
    queries: dict[str, str] = {}
    for index in range(20):
        task = f"{campaign}-task-{index:0{width}d}"
        vector = task + "-vector-00"
        queries[f"vector-{index:02d}"] = (
            "SELECT count(*) FROM ck.context_vectors "
            f"WHERE task_id='{task}' AND namespace='{campaign}' "
            f"AND vector_id='{vector}'"
        )
    for index in range(5):
        task = f"{campaign}-task-{index:0{width}d}"
        queries[f"receipt-{index:02d}"] = (
            "SELECT count(*) FROM ck.mcp_receipt_view " f"WHERE task_id='{task}'"
        )
    queries["stale-projection-read"] = (
        "SELECT count(*) FROM ck.projection_events "
        "WHERE source_key LIKE 'missing-stale-%'"
    )
    task = f"{campaign}-task-{0:0{width}d}"
    queries["trajectory-link-read"] = (
        "SELECT count(*) FROM ck.trajectory_events e "
        "JOIN ck.tasks t ON t.task_id=e.task_id "
        f"WHERE t.task_id='{task}' AND t.campaign_id='{campaign}'"
    )
    return queries


def run_sql(
    canary: Any,
    binary: Path,
    port: int,
    env: dict[str, str],
    statement: str,
    *,
    timeout: int = 300,
) -> tuple[bytes, float]:
    started = time.monotonic()
    command = [
        str(binary),
        "sql",
        "--insecure",
        f"--host=127.0.0.1:{port}",
        "--format=tsv",
        "--database=cockroach_kernel",
        "--execute",
        statement,
    ]
    try:
        completed = subprocess.run(
            command,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise PlanABError("SQL_TIMEOUT:" + digest(statement.encode())) from exc
    if completed.returncode != 0:
        tail = completed.stderr.decode("utf-8", "replace")[-1000:].replace("\n", " ")
        raise PlanABError(
            "SQL_FAILED:"
            + digest(statement.encode())
            + ":stderr="
            + digest(completed.stderr)
            + ":tail="
            + tail
        )
    return completed.stdout, time.monotonic() - started


def seed_sql(campaign: str, tasks: int) -> str:
    prefix = "'" + campaign + "-task-'"
    campaign_literal = "'" + campaign + "'"
    task = f"{prefix} || lpad(i::STRING,6,'0')"
    event = f"{task} || '-event-00'"
    event_hash = (
        f"decode(sha256(({campaign_literal} || '-event-' || i::STRING)::BYTES),'hex')"
    )
    task_hash = (
        f"decode(sha256(({campaign_literal} || '-task-' || i::STRING)::BYTES),'hex')"
    )
    state_hash = (
        f"decode(sha256(({campaign_literal} || '-state-' || i::STRING)::BYTES),'hex')"
    )
    zero = "0" * 64
    vector = "'[' || mod(i,101)::STRING || ',0,0' || '" + ",0" * 61 + "]'"
    return ";".join(
        (
            "INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash) "
            f"SELECT {task},{campaign_literal},jsonb_build_object('synthetic',true),"
            f"{task_hash},{state_hash} FROM generate_series(0,{tasks - 1}) g(i)",
            "INSERT INTO ck.trajectory_events"
            "(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash) "
            f"SELECT {event},{task},0,decode('{zero}','hex'),{state_hash},"
            f"jsonb_build_object('synthetic',true),{event_hash} "
            f"FROM generate_series(0,{tasks - 1}) g(i)",
            "INSERT INTO ck.receipts(receipt_hash,task_id,event_hash,status,receipt_json) "
            f"SELECT decode(sha256(({campaign_literal} || '-receipt-' || i::STRING || '-' || s::STRING)::BYTES),'hex'),"
            f"{task},{event_hash},'SEALED',jsonb_build_object('synthetic',true) "
            f"FROM generate_series(0,{tasks - 1}) g(i),generate_series(0,1) x(s)",
            "INSERT INTO ck.context_vectors"
            "(vector_id,task_id,event_hash,namespace,vector,vector_digest) "
            f"SELECT {task} || '-vector-00',{task},{event_hash},{campaign_literal},"
            f"({vector})::VECTOR(64),decode(sha256(({vector})::BYTES),'hex') "
            f"FROM generate_series(0,{tasks - 1}) g(i)",
            "INSERT INTO ck.projection_events"
            "(projection_id,source_table,source_key,receipt_hash,sequence,projected_json,projection_hash) "
            f"SELECT {campaign_literal} || '-projection-' || i::STRING,'tasks',{task},"
            f"decode(sha256(({campaign_literal} || '-receipt-' || i::STRING || '-0')::BYTES),'hex'),"
            f"0,jsonb_build_object('synthetic',true),"
            f"decode(sha256(({campaign_literal} || '-projection-' || i::STRING)::BYTES),'hex') "
            f"FROM generate_series(0,{tasks - 1}) g(i)",
        )
    )


def capture_queries(
    canary: Any,
    binary: Path,
    port: int,
    env: dict[str, str],
    queries: dict[str, str],
    output: Path,
    label: str,
    *,
    deadline: float | None = None,
) -> dict[str, Any]:
    def remaining_timeout(cap: int = 300) -> int:
        if deadline is None:
            return cap
        available = deadline - time.monotonic() - 1
        if available < 1:
            raise PlanABError("QUERY_CAPTURE_DEADLINE_EXHAUSTED")
        return min(cap, max(1, int(available)))

    results: dict[str, Any] = {}
    for name, query in queries.items():
        plan_raw, plan_elapsed = run_sql(
            canary, binary, port, env, "EXPLAIN " + query,
            timeout=remaining_timeout(),
        )
        analyze_raw, analyze_elapsed = run_sql(
            canary, binary, port, env, "EXPLAIN ANALYZE (DISTSQL) " + query,
            timeout=remaining_timeout(),
        )
        result_raw, result_elapsed = run_sql(
            canary, binary, port, env, query, timeout=remaining_timeout()
        )
        plan_path = output / f"{label}-{name}.explain.txt"
        analyze_path = output / f"{label}-{name}.analyze.txt"
        atomic_write(plan_path, plan_raw)
        atomic_write(analyze_path, analyze_raw)
        results[name] = {
            "query_sha256": digest(query.encode()),
            "plan_sha256": digest(plan_raw),
            "analyze_sha256": digest(analyze_raw),
            "result_sha256": digest(result_raw),
            "full_scan": full_scan(plan_raw.decode("utf-8", "replace")),
            "analyze_full_scan": full_scan(analyze_raw.decode("utf-8", "replace")),
            "plan_elapsed_seconds": plan_elapsed,
            "analyze_elapsed_seconds": analyze_elapsed,
            "result_elapsed_seconds": result_elapsed,
        }
    return results


def table_evidence(
    canary: Any,
    binary: Path,
    port: int,
    env: dict[str, str],
    *,
    output: Path | None = None,
    label: str | None = None,
) -> dict[str, Any]:
    statements = {
        "receipts_indexes": "SHOW INDEXES FROM ck.receipts",
        "receipts_statistics": "SHOW STATISTICS FOR TABLE ck.receipts",
        "projection_indexes": "SHOW INDEXES FROM ck.projection_events",
        "projection_statistics": "SHOW STATISTICS FOR TABLE ck.projection_events",
    }
    result: dict[str, Any] = {}
    for name, statement in statements.items():
        raw, elapsed = run_sql(canary, binary, port, env, statement)
        entry: dict[str, Any] = {
            "sha256": digest(raw),
            "bytes": len(raw),
            "elapsed_seconds": elapsed,
        }
        if output is not None:
            if label is None:
                raise PlanABError("TABLE_EVIDENCE_LABEL_REQUIRED")
            path = output / f"{label}-{name}.tsv"
            atomic_write(path, raw)
            entry["path"] = path.name
        result[name] = entry
    return result


def scale_trial(
    canary: Any,
    output: Path,
    tasks: int,
    *,
    binary: Path | None = None,
    runtime_parent: Path | None = None,
) -> dict[str, Any]:
    binary = (binary or canary.find_cockroach()).resolve()
    if not binary.is_file() or binary.is_symlink() or not os.access(binary, os.X_OK):
        raise PlanABError("COCKROACH_BINARY_INVALID")
    runtime_parent = (runtime_parent or (output / "generated-roots")).resolve()
    runtime_parent.mkdir(parents=True, exist_ok=True)
    root = Path(
        tempfile.mkdtemp(prefix=f"pf2-{tasks}.", dir=runtime_parent.resolve())
    ).resolve()
    fake_home = root / "empty-home"
    (root / "temp").mkdir()
    fake_home.mkdir()
    env = canary.scrubbed_env(fake_home)
    port = canary.reserve_port()
    http_port = canary.reserve_port()
    while http_port == port:
        http_port = canary.reserve_port()
    process = None
    log = None
    trial_output = output / f"scale-{tasks}"
    trial_output.mkdir(parents=True)
    teardown: dict[str, Any] = {"process_stopped": False, "root_removed": False}
    try:
        process, log = canary.start_database(
            binary, root, port, http_port, env, append_log=False
        )
        canary.sql(binary, port, "CREATE DATABASE cockroach_kernel", env=env)
        canary.apply_file(
            binary,
            port,
            "cockroach_kernel",
            BASE / "p9-cloud/migrations/001_cloud.sql",
            env=env,
        )
        run_sql(canary, binary, port, env, seed_sql(f"pf2-{tasks}", tasks), timeout=1800)
        counts_raw, _ = run_sql(
            canary,
            binary,
            port,
            env,
            "SELECT (SELECT count(*) FROM ck.tasks),"
            "(SELECT count(*) FROM ck.trajectory_events),"
            "(SELECT count(*) FROM ck.receipts),"
            "(SELECT count(*) FROM ck.context_vectors),"
            "(SELECT count(*) FROM ck.projection_events)",
        )
        expected_counts = (tasks, tasks, tasks * 2, tasks, tasks)
        actual_counts = canary.parse_count_tuple(counts_raw, 5)
        if actual_counts != expected_counts:
            raise PlanABError("PF2_COUNT_MISMATCH")
        queries = query_definitions(f"pf2-{tasks}")
        before_metadata = table_evidence(
            canary, binary, port, env, output=trial_output, label="before"
        )
        before = capture_queries(
            canary, binary, port, env, queries, trial_output, "before"
        )
        receipt_scan = any(before[f"receipt-{i:02d}"]["full_scan"] for i in range(5))
        projection_scan = before["stale-projection-read"]["full_scan"]
        if not receipt_scan:
            raise PlanABError("PF2_EXPECTED_RECEIPT_FULL_SCAN_NOT_OBSERVED")
        run_sql(canary, binary, port, env, RECEIPT_INDEX_DDL, timeout=1800)
        selected_indexes = ["receipts_task_id_idx"]
        if projection_scan:
            run_sql(canary, binary, port, env, PROJECTION_INDEX_DDL, timeout=1800)
            selected_indexes.append("projection_events_source_key_idx")
        run_sql(
            canary,
            binary,
            port,
            env,
            "CREATE STATISTICS pf2_receipts_stats ON task_id FROM ck.receipts;"
            "CREATE STATISTICS pf2_projection_stats ON source_key FROM ck.projection_events",
            timeout=1800,
        )
        after_metadata = table_evidence(
            canary, binary, port, env, output=trial_output, label="after"
        )
        after = capture_queries(
            canary, binary, port, env, queries, trial_output, "after"
        )
        mismatched_results = sorted(
            name for name in queries if before[name]["result_sha256"] != after[name]["result_sha256"]
        )
        prohibited_scans = sorted(
            name
            for name in queries
            if name.startswith("receipt-") or name == "stale-projection-read"
            if after[name]["full_scan"] or after[name]["analyze_full_scan"]
        )
        body = {
            "version": "ck-pdh3-r12-pf2-scale-v1",
            "tasks": tasks,
            "expected_counts": list(expected_counts),
            "actual_counts": list(actual_counts),
            "query_count": len(queries),
            "before_metadata": before_metadata,
            "after_metadata": after_metadata,
            "before": before,
            "after": after,
            "receipt_full_scan_before": receipt_scan,
            "projection_full_scan_before": projection_scan,
            "selected_indexes": selected_indexes,
            "mismatched_results": mismatched_results,
            "prohibited_scans_after": prohibited_scans,
            "product_migration_modified": False,
            "green": not mismatched_results and not prohibited_scans,
        }
        if not body["green"]:
            raise PlanABError("PF2_PLAN_OR_RESULT_GATE_FAILED")
        return write_record(trial_output / "receipt.json", body, "receipt_sha256")
    finally:
        if process is not None and log is not None:
            canary.stop_database(process, log, crash=False)
            teardown["process_stopped"] = process.poll() is not None
        database_log = root / "cockroach.log"
        if database_log.is_file():
            copied_log = trial_output / "cockroach.log"
            shutil.copyfile(database_log, copied_log)
            teardown["database_log_sha256"] = file_sha256(copied_log)
        shutil.rmtree(root, ignore_errors=False)
        teardown["root_removed"] = not root.exists()
        write_record(
            trial_output / "teardown.json",
            {
                "version": "ck-pdh3-r12-pf2-teardown-v1",
                "tasks": tasks,
                **teardown,
                "green": all(teardown.values()),
            },
            "receipt_sha256",
        )


def execute(
    output: Path,
    packet_sha256: str,
    *,
    binary: Path | None = None,
    runtime_parent: Path | None = None,
) -> dict[str, Any]:
    if output.exists():
        raise PlanABError("OUTPUT_EXISTS")
    if packet_sha256 != PLAN_SHA256:
        raise PlanABError("PLAN_HASH_BINDING_INVALID")
    output.mkdir(parents=True)
    canary = load_canary()
    receipts = [
        scale_trial(
            canary,
            output,
            scale,
            binary=binary,
            runtime_parent=runtime_parent,
        )
        for scale in SCALES
    ]
    body = {
        "version": "ck-pdh3-r12-pf2-plan-ab-v1",
        "plan_sha256": PLAN_SHA256,
        "scales": list(SCALES),
        "scale_receipts": [row["receipt_sha256"] for row in receipts],
        "fresh_root_count": len(receipts),
        "result_equivalence": all(not row["mismatched_results"] for row in receipts),
        "no_prohibited_full_scan_after": all(not row["prohibited_scans_after"] for row in receipts),
        "product_migration_modified": False,
        "green": all(row["green"] for row in receipts),
    }
    return write_record(output / "PF2_RESULT.json", body, "receipt_sha256")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--output", type=Path, required=True)
    value.add_argument("--packet-sha256", required=True)
    value.add_argument("--binary", type=Path)
    value.add_argument("--runtime-parent", type=Path)
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    try:
        result = execute(
            args.output,
            args.packet_sha256,
            binary=args.binary,
            runtime_parent=args.runtime_parent,
        )
    except (PlanABError, OSError, subprocess.SubprocessError) as exc:
        print(f"PDH3_R12_PF2_BLOCKED:{type(exc).__name__}:{exc}", file=sys.stderr)
        return 2
    print(canonical(result).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
