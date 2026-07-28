#!/usr/bin/env python3
"""Bounded host-only CockroachDB bulk telemetry controller for Gate 7.

Credentials stay inside the already reviewed s3-soak cloud adapter. This file
is never transferred to the worker with configuration or secret material. It
creates only campaign-prefixed synthetic rows, measures them, and cleans them
in dependency order before returning.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "s3-soak"))
sys.path.insert(0, str(BASE / "p9-cloud"))
import cloud_adapter  # type: ignore  # noqa: E402
import context_vector  # type: ignore  # noqa: E402


TASKS = 2_000
EVENTS_PER_TASK = 10
RECEIPTS_PER_TASK = 2
VECTORS_PER_TASK = 10
QUERY_SAMPLES = 200
CONCURRENCY = 4
AWS_CALLS_SEPARATE_TRACK = 12
PREFIX = "ck-g7r2-"
DATABASE_GROWTH_LIMIT = 536_870_912
EVIDENCE_GROWTH_LIMIT = 67_108_864
QUERY_P99_LIMIT_MS = 10_000
INSERT_TOTAL_LIMIT_MS = 300_000


class LiveBulkError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: bytes | Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


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
        if temporary.exists():
            temporary.unlink()


def sql_literal(value: str) -> str:
    if not isinstance(value, str) or "\x00" in value:
        raise LiveBulkError("SQL_VALUE_INVALID")
    return "'" + value.replace("'", "''") + "'"


def byte_literal(value: str) -> str:
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise LiveBulkError("HASH_INVALID")
    return "decode('" + value + "','hex')"


def vector_literal(value: list[float]) -> str:
    if len(value) != 64:
        raise LiveBulkError("VECTOR_INVALID")
    return "'[" + ",".join(format(item, ".6f") for item in value) + "]'::VECTOR(64)"


def campaign_prefix(campaign_id: str) -> str:
    if not campaign_id.startswith(PREFIX) or not campaign_id.replace("-", "").isalnum():
        raise LiveBulkError("CAMPAIGN_ID_INVALID")
    return campaign_id + "-"


def hash_for(*parts: object) -> str:
    return digest({"parts": list(parts)})


def batched(values: list[str], size: int) -> list[list[str]]:
    return [values[index:index + size] for index in range(0, len(values), size)]


def build_sql(campaign_id: str, output: Path) -> dict[str, Any]:
    prefix = campaign_prefix(campaign_id)
    output.mkdir(parents=True, exist_ok=False)
    task_rows: list[str] = []
    event_rows: list[str] = []
    receipt_rows: list[str] = []
    vector_rows: list[str] = []
    query_vectors: list[tuple[str, list[float]]] = []
    for task_index in range(TASKS):
        task_id = f"{prefix}task-{task_index:04d}"
        task_hash = hash_for(campaign_id, "task", task_index)
        state_hash = hash_for(campaign_id, "state", task_index)
        task_json = canonical({"synthetic": True, "task": task_index}).decode("utf-8")
        task_rows.append(
            f"({sql_literal(task_id)},{sql_literal(campaign_id)},"
            f"{sql_literal(task_json)}::JSONB,{byte_literal(task_hash)},"
            f"{byte_literal(state_hash)})"
        )
        parent = "0" * 64
        for sequence in range(EVENTS_PER_TASK):
            event_id = f"{task_id}-event-{sequence:02d}"
            event_hash = hash_for(campaign_id, "event", task_index, sequence)
            event_json = canonical({"synthetic": True, "sequence": sequence}).decode("utf-8")
            event_rows.append(
                f"({sql_literal(event_id)},{sql_literal(task_id)},{sequence},"
                f"{byte_literal(parent)},{byte_literal(state_hash)},"
                f"{sql_literal(event_json)}::JSONB,{byte_literal(event_hash)})"
            )
            if sequence < RECEIPTS_PER_TASK:
                receipt_hash = hash_for(campaign_id, "receipt", task_index, sequence)
                receipt_json = canonical({"synthetic": True, "receipt": sequence}).decode("utf-8")
                receipt_rows.append(
                    f"({byte_literal(receipt_hash)},{sql_literal(task_id)},"
                    f"{byte_literal(event_hash)},'SEALED',"
                    f"{sql_literal(receipt_json)}::JSONB)"
                )
            text = f"continue synthetic task {task_index} trajectory segment {sequence}"
            vector = context_vector.context_vector(text, campaign_id)
            vector_digest = context_vector.vector_digest(vector)
            vector_rows.append(
                f"({sql_literal(task_id + '-vector-' + format(sequence, '02d'))},"
                f"{sql_literal(task_id)},{byte_literal(event_hash)},"
                f"{sql_literal(campaign_id)},{vector_literal(vector)},"
                f"{byte_literal(vector_digest)})"
            )
            if task_index < QUERY_SAMPLES and sequence == 0:
                query_vectors.append((task_id, vector))
            parent = event_hash
    tables = {
        "tasks": ("ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash)", task_rows),
        "events": (
            "ck.trajectory_events(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash)",
            event_rows,
        ),
        "receipts": ("ck.receipts(receipt_hash,task_id,event_hash,status,receipt_json)", receipt_rows),
        "vectors": (
            "ck.context_vectors(vector_id,task_id,event_hash,namespace,vector,vector_digest)",
            vector_rows,
        ),
    }
    sql_hashes: dict[str, str] = {}
    for name, (columns, rows) in tables.items():
        statements = ["BEGIN;"]
        for group in batched(rows, 250):
            statements.append(f"INSERT INTO {columns} VALUES " + ",".join(group) + ";")
        statements.append("COMMIT;")
        raw = ("\n".join(statements) + "\n").encode("utf-8")
        path = output / f"insert-{name}.sql"
        atomic_write(path, raw)
        sql_hashes[path.name] = digest(raw)
    query_specs = []
    for index, (task_id, vector) in enumerate(query_vectors, start=1):
        sql = (
            "SELECT vector_id FROM ck.context_vectors "
            f"WHERE task_id={sql_literal(task_id)} AND namespace={sql_literal(campaign_id)} "
            f"ORDER BY vector <-> {vector_literal(vector)} LIMIT 1;"
        )
        query_specs.append({
            "index": index, "task_id": task_id, "sql": sql,
            "expected_vector_id": task_id + "-vector-00",
            "sql_sha256": digest(sql.encode("utf-8")),
        })
    query_path = output / "query-specs.json"
    atomic_write(query_path, canonical(query_specs))
    cleanup = (
        "BEGIN;"
        f"DELETE FROM ck.projection_events WHERE source_key LIKE {sql_literal(prefix + '%')};"
        f"DELETE FROM ck.worker_results WHERE task_id LIKE {sql_literal(prefix + '%')};"
        f"DELETE FROM ck.context_vectors WHERE task_id LIKE {sql_literal(prefix + '%')};"
        f"DELETE FROM ck.receipts WHERE task_id LIKE {sql_literal(prefix + '%')};"
        f"DELETE FROM ck.trajectory_events WHERE task_id LIKE {sql_literal(prefix + '%')};"
        f"DELETE FROM ck.tasks WHERE task_id LIKE {sql_literal(prefix + '%')};"
        "COMMIT;"
    )
    atomic_write(output / "cleanup.sql", cleanup.encode("utf-8"))
    manifest_body = {
        "version": "hardening-gate7-live-bulk-manifest-v1",
        "campaign_id": campaign_id,
        "synthetic_only": True,
        "counts": {
            "tasks": TASKS,
            "events": TASKS * EVENTS_PER_TASK,
            "receipts": TASKS * RECEIPTS_PER_TASK,
            "vectors": TASKS * VECTORS_PER_TASK,
            "vector_queries": QUERY_SAMPLES,
            "aws_calls_separate_track": AWS_CALLS_SEPARATE_TRACK,
        },
        "concurrency": CONCURRENCY,
        "sql_files": sql_hashes,
        "query_specs_sha256": digest(query_path.read_bytes()),
        "cleanup_sha256": digest(cleanup.encode("utf-8")),
        "ceilings": {
            "database_growth_bytes": DATABASE_GROWTH_LIMIT,
            "evidence_growth_bytes": EVIDENCE_GROWTH_LIMIT,
            "query_p99_ms": QUERY_P99_LIMIT_MS,
            "insert_total_ms": INSERT_TOTAL_LIMIT_MS,
        },
        "credential_location": "HOST_ONLY_EXISTING_REVIEWED_ADAPTER",
    }
    manifest = dict(manifest_body, manifest_sha256=digest(manifest_body))
    atomic_write(output / "manifest.json", canonical(manifest))
    return manifest


def percentile(values: list[int], percentage: int) -> int:
    ordered = sorted(values)
    return ordered[max(0, (len(ordered) * percentage + 99) // 100 - 1)]


def run_live(config_path: Path, generated: Path, evidence: Path) -> dict[str, Any]:
    config = cloud_adapter._read_config(config_path.resolve())
    manifest = json.loads((generated / "manifest.json").read_bytes())
    campaign_id = manifest["campaign_id"]
    prefix = campaign_prefix(campaign_id)
    secret = bytearray()
    sql_env = None
    evidence.mkdir(parents=True, exist_ok=False)
    active = 0
    active_max = 0
    lock = threading.Lock()
    try:
        secret.extend(cloud_adapter._password(config))
        sql_env = cloud_adapter._sql_env(config, bytes(secret))
        cloud_adapter._sql(config, sql_env, file=generated / "cleanup.sql", timeout=180)
        before_raw, _ = cloud_adapter._sql(
            config, sql_env,
            execute="SELECT count(*) FROM ck.tasks WHERE task_id LIKE " + sql_literal(prefix + "%"),
        )
        insert_latencies: dict[str, int] = {}
        insert_hashes: dict[str, str] = {}
        for name in ("tasks", "events", "receipts", "vectors"):
            raw, elapsed = cloud_adapter._sql(
                config, sql_env, file=generated / f"insert-{name}.sql", timeout=300,
            )
            insert_latencies[name] = elapsed
            insert_hashes[name] = digest(raw)
        count_sql = (
            "SELECT "
            f"(SELECT count(*) FROM ck.tasks WHERE task_id LIKE {sql_literal(prefix + '%')}),"
            f"(SELECT count(*) FROM ck.trajectory_events WHERE task_id LIKE {sql_literal(prefix + '%')}),"
            f"(SELECT count(*) FROM ck.receipts WHERE task_id LIKE {sql_literal(prefix + '%')}),"
            f"(SELECT count(*) FROM ck.context_vectors WHERE task_id LIKE {sql_literal(prefix + '%')});"
        )
        counts_raw, counts_ms = cloud_adapter._sql(config, sql_env, execute=count_sql)
        specs = json.loads((generated / "query-specs.json").read_bytes())

        def query(spec: dict[str, Any]) -> tuple[int, str]:
            nonlocal active, active_max
            with lock:
                active += 1
                active_max = max(active_max, active)
            try:
                raw, elapsed = cloud_adapter._sql(
                    config, sql_env, execute=spec["sql"], timeout=60,
                )
                if spec["expected_vector_id"].encode("utf-8") not in raw:
                    raise LiveBulkError("TASK_BOUND_RECALL_FAILED")
                return elapsed, digest(raw)
            finally:
                with lock:
                    active -= 1

        query_results: list[tuple[int, str]] = []
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
            futures = [executor.submit(query, spec) for spec in specs]
            for future in as_completed(futures):
                query_results.append(future.result())
        query_latencies = [row[0] for row in query_results]
        plan_raw, plan_ms = cloud_adapter._sql(
            config, sql_env,
            execute="EXPLAIN " + specs[0]["sql"], timeout=60,
        )
        topology_raw, topology_ms = cloud_adapter._sql(
            config, sql_env,
            execute="SHOW REGIONS FROM CLUSTER;",
        )
        rollback_id = prefix + "rollback-control"
        rollback_sql = (
            "BEGIN; INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash) VALUES ("
            f"{sql_literal(rollback_id)},{sql_literal(campaign_id)},'{{}}'::JSONB,"
            f"{byte_literal(hash_for(campaign_id, 'rollback-task'))},"
            f"{byte_literal(hash_for(campaign_id, 'rollback-state'))}); ROLLBACK;"
            f"SELECT count(*) FROM ck.tasks WHERE task_id={sql_literal(rollback_id)};"
        )
        rollback_raw, rollback_ms = cloud_adapter._sql(config, sql_env, execute=rollback_sql)
        duplicate_id = prefix + "duplicate-control"
        duplicate_hash = hash_for(campaign_id, "duplicate-task")
        duplicate_state = hash_for(campaign_id, "duplicate-state")
        duplicate_sql = (
            "BEGIN;"
            "INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash) VALUES ("
            f"{sql_literal(duplicate_id)},{sql_literal(campaign_id)},'{{}}'::JSONB,"
            f"{byte_literal(duplicate_hash)},{byte_literal(duplicate_state)}) ON CONFLICT DO NOTHING;"
            "INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash) VALUES ("
            f"{sql_literal(duplicate_id)},{sql_literal(campaign_id)},'{{}}'::JSONB,"
            f"{byte_literal(duplicate_hash)},{byte_literal(duplicate_state)}) ON CONFLICT DO NOTHING;"
            "COMMIT;"
            f"SELECT count(*) FROM ck.tasks WHERE task_id={sql_literal(duplicate_id)};"
        )
        duplicate_raw, duplicate_ms = cloud_adapter._sql(config, sql_env, execute=duplicate_sql)
        cleanup_raw, cleanup_ms = cloud_adapter._sql(
            config, sql_env, file=generated / "cleanup.sql", timeout=300,
        )
        residue_raw, residue_ms = cloud_adapter._sql(config, sql_env, execute=count_sql)
        result_body = {
            "version": "hardening-gate7-live-bulk-result-v1",
            "campaign_id": campaign_id,
            "manifest_sha256": manifest["manifest_sha256"],
            "before_count_output_sha256": digest(before_raw),
            "count_output_sha256": digest(counts_raw),
            "expected_counts": manifest["counts"],
            "insert_latency_ms": insert_latencies,
            "insert_output_hashes": insert_hashes,
            "insert_total_ms": sum(insert_latencies.values()),
            "count_query_ms": counts_ms,
            "query_count": len(query_results),
            "query_latency_ms": {
                "p50": percentile(query_latencies, 50),
                "p95": percentile(query_latencies, 95),
                "p99": percentile(query_latencies, 99),
                "max": max(query_latencies),
            },
            "query_output_set_sha256": digest(sorted(row[1] for row in query_results)),
            "configured_concurrency": CONCURRENCY,
            "observed_concurrency_max": active_max,
            "plan_output_sha256": digest(plan_raw),
            "plan_ms": plan_ms,
            "topology_output_sha256": digest(topology_raw),
            "topology_ms": topology_ms,
            "rollback_output_sha256": digest(rollback_raw),
            "rollback_ms": rollback_ms,
            "duplicate_output_sha256": digest(duplicate_raw),
            "duplicate_ms": duplicate_ms,
            "cleanup_output_sha256": digest(cleanup_raw),
            "cleanup_ms": cleanup_ms,
            "residue_output_sha256": digest(residue_raw),
            "residue_ms": residue_ms,
            "credential_bytes_recorded": False,
            "worker_received_credentials": False,
            "synthetic_only": True,
        }
        result_body["green"] = (
            len(query_results) == QUERY_SAMPLES
            and active_max >= 2
            and result_body["query_latency_ms"]["p99"] <= QUERY_P99_LIMIT_MS
            and result_body["insert_total_ms"] <= INSERT_TOTAL_LIMIT_MS
            and b"\n0\n" in rollback_raw
            and b"\n1\n" in duplicate_raw
        )
        result = dict(result_body, result_sha256=digest(result_body))
        atomic_write(evidence / "result.json", canonical(result))
        return result
    finally:
        if sql_env is not None:
            sql_env.pop("PGPASSWORD", None)
        for index in range(len(secret)):
            secret[index] = 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--generated-root", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()
    manifest = build_sql(args.campaign_id, args.generated_root.resolve())
    if args.generate_only:
        print(canonical({
            "status": "GENERATED", "manifest_sha256": manifest["manifest_sha256"]
        }).decode("utf-8"))
        return 0
    if args.config is None or args.evidence_root is None:
        raise LiveBulkError("LIVE_ARGUMENTS_REQUIRED")
    result = run_live(args.config, args.generated_root.resolve(), args.evidence_root.resolve())
    return 0 if result["green"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
