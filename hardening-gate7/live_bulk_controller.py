#!/usr/bin/env python3
"""Bounded host-only CockroachDB bulk telemetry controller for Gate 7.

Credentials stay inside the already reviewed s3-soak cloud adapter. This file
is never transferred to the worker with configuration or secret material. It
creates only campaign-prefixed synthetic rows, measures them, and cleans them
in dependency order before returning.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import statistics
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "s3-soak"))
sys.path.insert(0, str(BASE / "p9-cloud"))
import cloud_adapter  # type: ignore  # noqa: E402
import context_vector  # type: ignore  # noqa: E402
import hardening  # type: ignore  # noqa: E402


TASKS = 2_000
EVENTS_PER_TASK = 10
RECEIPTS_PER_TASK = 2
VECTORS_PER_TASK = 10
QUERY_SAMPLES = 200
CONCURRENCY = 4
AWS_CALLS_SEPARATE_TRACK = 12
CAMPAIGN_RE = re.compile(r"^ck-g7r[0-9]+-[A-Za-z0-9-]+$")
BATCH_SIZE = 250
CLEANUP_TASK_BATCH_SIZE = 250
MAX_SERIALIZATION_RETRIES = 3
BATCH_TIMEOUT_SECONDS = 120
VECTOR_BATCH_TIMEOUT_SECONDS = 300
SERIALIZATION_RETRY_BACKOFF_MS = 250
DATABASE_GROWTH_LIMIT = 536_870_912
EVIDENCE_GROWTH_LIMIT = 67_108_864
QUERY_P99_LIMIT_MS = 10_000
INSERT_TOTAL_LIMIT_MS = 300_000


class LiveBulkError(RuntimeError):
    pass


class LiveBulkInterrupted(LiveBulkError):
    pass


class DurableJournal:
    """Hash-chained, fsynced stage and batch events for one controller run."""

    def __init__(self, path: Path, campaign_id: str) -> None:
        self.path = path.resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("xb", buffering=0)
        self.campaign_id = campaign_id
        self.started_ns = time.monotonic_ns()
        self.sequence = 0
        self.prior_hash = "0" * 64
        self.stage = "BOOT"
        self.batch_index: int | None = None

    def emit(self, event: str, stage: str, **details: Any) -> dict[str, Any]:
        self.sequence += 1
        self.stage = stage
        self.batch_index = details.get("batch_index")
        body = {
            "version": "hardening-gate7-live-bulk-journal-v2",
            "campaign_id": self.campaign_id,
            "sequence": self.sequence,
            "event": event,
            "stage": stage,
            "batch_index": self.batch_index,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "elapsed_ns": time.monotonic_ns() - self.started_ns,
            "prior_event_hash": self.prior_hash,
            "details": details,
        }
        record = dict(body, event_hash=digest(body))
        raw = canonical(record) + b"\n"
        self.handle.write(raw)
        os.fsync(self.handle.fileno())
        self.prior_hash = record["event_hash"]
        return record

    def close(self) -> None:
        if not self.handle.closed:
            self.handle.close()


class DurableTextLog:
    """Minimal text stream that fsyncs every write and never follows links."""

    def __init__(self, path: Path) -> None:
        path = path.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        self.handle = os.fdopen(descriptor, "w", encoding="utf-8", buffering=1)

    def write(self, value: str) -> int:
        written = self.handle.write(value)
        self.handle.flush()
        os.fsync(self.handle.fileno())
        return written

    def flush(self) -> None:
        self.handle.flush()
        os.fsync(self.handle.fileno())

    def close(self) -> None:
        if not self.handle.closed:
            self.handle.close()


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


def vector_text(task_index: int, sequence: int) -> str:
    """Bind an order-insensitive projection to one unique task/event pair."""
    return (
        f"continue synthetic task {task_index} trajectory segment {sequence} "
        f"eventkey t{task_index}s{sequence}"
    )


def campaign_prefix(campaign_id: str) -> str:
    if not CAMPAIGN_RE.fullmatch(campaign_id):
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
    vector_digests: set[str] = set()
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
            text = vector_text(task_index, sequence)
            vector = context_vector.context_vector(text, campaign_id)
            vector_digest = context_vector.vector_digest(vector)
            if vector_digest in vector_digests:
                raise LiveBulkError("VECTOR_DIGEST_COLLISION")
            vector_digests.add(vector_digest)
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
    batch_files: dict[str, list[dict[str, Any]]] = {}
    for name, (columns, rows) in tables.items():
        batch_files[name] = []
        for batch_index, group in enumerate(batched(rows, BATCH_SIZE), start=1):
            raw = (
                "BEGIN;\nINSERT INTO " + columns + " VALUES " +
                ",".join(group) + ";\nCOMMIT;\n"
            ).encode("utf-8")
            path = output / f"insert-{name}-batch-{batch_index:04d}.sql"
            atomic_write(path, raw)
            row = {
                "path": path.name,
                "sha256": digest(raw),
                "rows": len(group),
                "batch_index": batch_index,
            }
            batch_files[name].append(row)
            sql_hashes[path.name] = row["sha256"]
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
    cleanup_batches: list[dict[str, Any]] = []

    def add_cleanup(stage: str, statement: str, *, task_count: int) -> None:
        stage_index = 1 + sum(row["stage"] == stage for row in cleanup_batches)
        raw = ("BEGIN;\n" + statement + "\nCOMMIT;\n").encode("utf-8")
        path = output / f"cleanup-{stage}-batch-{stage_index:04d}.sql"
        atomic_write(path, raw)
        cleanup_batches.append({
            "path": path.name,
            "sha256": digest(raw),
            "stage": stage,
            "batch_index": stage_index,
            "task_count": task_count,
        })

    add_cleanup(
        "projection-events",
        f"DELETE FROM ck.projection_events WHERE source_key LIKE {sql_literal(prefix + '%')};",
        task_count=0,
    )
    add_cleanup(
        "worker-results",
        f"DELETE FROM ck.worker_results WHERE task_id LIKE {sql_literal(prefix + '%')};",
        task_count=0,
    )
    task_ids = [f"{prefix}task-{index:04d}" for index in range(TASKS)]
    for table, stage in (
        ("ck.context_vectors", "vectors"),
        ("ck.receipts", "receipts"),
        ("ck.trajectory_events", "events"),
        ("ck.tasks", "tasks"),
    ):
        for group in batched(task_ids, CLEANUP_TASK_BATCH_SIZE):
            identifiers = ",".join(sql_literal(item) for item in group)
            add_cleanup(
                stage,
                f"DELETE FROM {table} WHERE task_id IN ({identifiers});",
                task_count=len(group),
            )
    control_ids = [prefix + "rollback-control", prefix + "duplicate-control"]
    controls = ",".join(sql_literal(item) for item in control_ids)
    add_cleanup(
        "controls",
        "DELETE FROM ck.context_vectors WHERE task_id IN (" + controls + ");"
        "DELETE FROM ck.receipts WHERE task_id IN (" + controls + ");"
        "DELETE FROM ck.trajectory_events WHERE task_id IN (" + controls + ");"
        "DELETE FROM ck.tasks WHERE task_id IN (" + controls + ");",
        task_count=len(control_ids),
    )
    cleanup_plan = b"".join((output / row["path"]).read_bytes()
                            for row in cleanup_batches)
    atomic_write(output / "cleanup.sql", cleanup_plan)
    cleanup_manifest_body = {
        "version": "hardening-gate7-live-bulk-cleanup-manifest-v1",
        "campaign_id": campaign_id,
        "task_batch_size": CLEANUP_TASK_BATCH_SIZE,
        "batch_count": len(cleanup_batches),
        "batches": cleanup_batches,
        "composed_cleanup_sha256": digest(cleanup_plan),
    }
    cleanup_manifest = dict(
        cleanup_manifest_body,
        cleanup_manifest_sha256=digest(cleanup_manifest_body),
    )
    atomic_write(output / "cleanup-manifest.json", canonical(cleanup_manifest))
    manifest_body = {
        "version": "hardening-gate7-live-bulk-manifest-v2",
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
        "batch_size": BATCH_SIZE,
        "batches": batch_files,
        "unique_vector_digests": len(vector_digests),
        "sql_files": sql_hashes,
        "query_specs_sha256": digest(query_path.read_bytes()),
        "cleanup_manifest_sha256": cleanup_manifest["cleanup_manifest_sha256"],
        "cleanup_batch_count": len(cleanup_batches),
        "cleanup_sha256": digest(cleanup_plan),
        "execution_policy": {
            "batch_timeout_seconds": BATCH_TIMEOUT_SECONDS,
            "vector_batch_timeout_seconds": VECTOR_BATCH_TIMEOUT_SECONDS,
            "serialization_retries": MAX_SERIALIZATION_RETRIES,
            "serialization_retry_backoff_ms": SERIALIZATION_RETRY_BACKOFF_MS,
        },
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


def parse_count_row(raw: bytes, expected_fields: int = 4) -> tuple[int, ...]:
    rows = [line.strip() for line in raw.decode("utf-8").splitlines() if line.strip()]
    for row in reversed(rows):
        fields = row.split("\t")
        if len(fields) == expected_fields and all(field.isdigit() for field in fields):
            return tuple(int(field) for field in fields)
    raise LiveBulkError("COUNT_OUTPUT_INVALID")


def campaign_count_sql(prefix: str) -> str:
    return (
        "SELECT "
        f"(SELECT count(*) FROM ck.tasks WHERE task_id LIKE {sql_literal(prefix + '%')}),"
        f"(SELECT count(*) FROM ck.trajectory_events WHERE task_id LIKE {sql_literal(prefix + '%')}),"
        f"(SELECT count(*) FROM ck.receipts WHERE task_id LIKE {sql_literal(prefix + '%')}),"
        f"(SELECT count(*) FROM ck.context_vectors WHERE task_id LIKE {sql_literal(prefix + '%')});"
    )


def external_failure_fields(exc: BaseException) -> dict[str, Any]:
    if isinstance(exc, hardening.ExternalCommandFailure):
        return {
            "exception_type": type(exc).__name__,
            "failure_class": exc.failure_class,
            "operation_family": exc.command_family,
            "return_code": exc.return_code,
            "signal": -exc.return_code if exc.return_code < 0 else None,
            "sqlstate": exc.sqlstate,
            "sanitized_output_sha256": exc.output_hash,
        }
    reason = str(exc) if isinstance(exc, LiveBulkError) else "UNCLASSIFIED_INTERNAL"
    return {
        "exception_type": type(exc).__name__,
        "failure_class": reason,
        "operation_family": "internal",
        "return_code": -1,
        "signal": None,
        "sqlstate": None,
        "sanitized_output_sha256": digest(type(exc).__name__.encode("utf-8")),
    }


def write_receipt(path: Path, version: str, body: dict[str, Any]) -> dict[str, Any]:
    core = {"version": version, **body}
    receipt = dict(core, receipt_sha256=digest(core))
    atomic_write(path, canonical(receipt))
    return receipt


def execute_batches(config: dict[str, Any], sql_env: dict[str, str],
                    generated: Path, manifest: dict[str, Any], stage: str,
                    journal: DurableJournal) -> tuple[int, list[str], int]:
    total_ms = 0
    output_hashes: list[str] = []
    retries = 0
    rows_completed = 0
    for row in manifest["batches"][stage]:
        batch_index = row["batch_index"]
        path = generated / row["path"]
        if digest(path.read_bytes()) != row["sha256"]:
            raise LiveBulkError("BATCH_HASH_MISMATCH")
        attempt = 0
        while True:
            attempt += 1
            journal.emit("BATCH_START", stage.upper(), batch_index=batch_index,
                         attempt=attempt, rows=row["rows"], sql_sha256=row["sha256"])
            try:
                timeout_seconds = (VECTOR_BATCH_TIMEOUT_SECONDS
                                   if stage == "vectors"
                                   else BATCH_TIMEOUT_SECONDS)
                raw, elapsed = cloud_adapter._sql(
                    config, sql_env, file=path, timeout=timeout_seconds,
                )
                total_ms += elapsed
                output_hash = digest(raw)
                output_hashes.append(output_hash)
                rows_completed += row["rows"]
                journal.emit("BATCH_PASS", stage.upper(), batch_index=batch_index,
                             attempt=attempt, rows=row["rows"],
                             output_sha256=output_hash, elapsed_ms=elapsed)
                break
            except hardening.ExternalCommandFailure as exc:
                journal.emit("BATCH_FAIL", stage.upper(), batch_index=batch_index,
                             attempt=attempt, rows=row["rows"],
                             **external_failure_fields(exc))
                if exc.sqlstate == "40001" and attempt <= MAX_SERIALIZATION_RETRIES:
                    retries += 1
                    backoff_ms = SERIALIZATION_RETRY_BACKOFF_MS * attempt
                    journal.emit("BATCH_RETRY", stage.upper(), batch_index=batch_index,
                                 attempt=attempt, sqlstate=exc.sqlstate,
                                 backoff_ms=backoff_ms)
                    time.sleep(backoff_ms / 1000)
                    continue
                raise
    return total_ms, output_hashes, retries


def execute_cleanup_batches(config: dict[str, Any], sql_env: dict[str, str],
                            generated: Path, manifest: dict[str, Any],
                            journal: DurableJournal) -> tuple[int, list[str], int]:
    cleanup_path = generated / "cleanup-manifest.json"
    cleanup_manifest = json.loads(cleanup_path.read_bytes())
    body = {key: value for key, value in cleanup_manifest.items()
            if key != "cleanup_manifest_sha256"}
    if cleanup_manifest.get("cleanup_manifest_sha256") != digest(body):
        raise LiveBulkError("CLEANUP_MANIFEST_HASH_MISMATCH")
    if manifest.get("cleanup_manifest_sha256") != cleanup_manifest["cleanup_manifest_sha256"]:
        raise LiveBulkError("CLEANUP_MANIFEST_LINK_MISMATCH")
    batches = cleanup_manifest.get("batches")
    if not isinstance(batches, list) or len(batches) != manifest.get("cleanup_batch_count"):
        raise LiveBulkError("CLEANUP_BATCH_COUNT_MISMATCH")
    total_ms = 0
    output_hashes: list[str] = []
    retries = 0
    for row in batches:
        path = generated / row["path"]
        if path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != row["sha256"]:
            raise LiveBulkError("CLEANUP_BATCH_HASH_MISMATCH")
        attempt = 0
        while True:
            attempt += 1
            journal.emit(
                "CLEANUP_BATCH_START", "CLEANUP",
                cleanup_stage=row["stage"], batch_index=row["batch_index"],
                attempt=attempt, task_count=row["task_count"],
                sql_sha256=row["sha256"],
            )
            try:
                raw, elapsed = cloud_adapter._sql(
                    config, sql_env, file=path, timeout=120,
                )
                total_ms += elapsed
                output_hash = digest(raw)
                output_hashes.append(output_hash)
                journal.emit(
                    "CLEANUP_BATCH_PASS", "CLEANUP",
                    cleanup_stage=row["stage"], batch_index=row["batch_index"],
                    attempt=attempt, task_count=row["task_count"],
                    output_sha256=output_hash, elapsed_ms=elapsed,
                )
                break
            except hardening.ExternalCommandFailure as exc:
                journal.emit(
                    "CLEANUP_BATCH_FAIL", "CLEANUP",
                    cleanup_stage=row["stage"], batch_index=row["batch_index"],
                    attempt=attempt, task_count=row["task_count"],
                    **external_failure_fields(exc),
                )
                if exc.sqlstate == "40001" and attempt <= MAX_SERIALIZATION_RETRIES:
                    retries += 1
                    backoff_ms = SERIALIZATION_RETRY_BACKOFF_MS * attempt
                    journal.emit(
                        "CLEANUP_BATCH_RETRY", "CLEANUP",
                        cleanup_stage=row["stage"], batch_index=row["batch_index"],
                        attempt=attempt, sqlstate=exc.sqlstate,
                        backoff_ms=backoff_ms,
                    )
                    time.sleep(backoff_ms / 1000)
                    continue
                raise
    return total_ms, output_hashes, retries


def run_live(config_path: Path, generated: Path, evidence: Path,
             journal: DurableJournal) -> dict[str, Any]:
    config = cloud_adapter._read_config(config_path.resolve())
    manifest = json.loads((generated / "manifest.json").read_bytes())
    campaign_id = manifest["campaign_id"]
    prefix = campaign_prefix(campaign_id)
    secret = bytearray()
    sql_env = None
    if not evidence.is_dir():
        raise LiveBulkError("EVIDENCE_ROOT_MISSING")
    active = 0
    active_max = 0
    lock = threading.Lock()
    cleanup_receipt: dict[str, Any] | None = None
    actual_counts: tuple[int, ...] | None = None
    try:
        journal.emit("STAGE_START", "AUTH", credential_bytes_recorded=False)
        secret.extend(cloud_adapter._password(config))
        sql_env = cloud_adapter._sql_env(config, bytes(secret))
        journal.emit("STAGE_PASS", "AUTH", credential_bytes_recorded=False)
        journal.emit("STAGE_START", "PRECLEAN")
        count_sql = campaign_count_sql(prefix)
        before_raw, preclean_ms = cloud_adapter._sql(
            config, sql_env, execute=count_sql,
        )
        before_counts = parse_count_row(before_raw)
        if before_counts != (0, 0, 0, 0):
            raise LiveBulkError("PRECLEAN_RESIDUE")
        journal.emit("STAGE_PASS", "PRECLEAN", residue_counts=list(before_counts),
                     elapsed_ms=preclean_ms)
        insert_latencies: dict[str, int] = {}
        insert_hashes: dict[str, str] = {}
        insert_batch_output_hashes: dict[str, list[str]] = {}
        serialization_retries = 0
        for name in ("tasks", "events", "receipts", "vectors"):
            journal.emit("STAGE_START", name.upper(),
                         batches=len(manifest["batches"][name]))
            elapsed, hashes, retries = execute_batches(
                config, sql_env, generated, manifest, name, journal,
            )
            insert_latencies[name] = elapsed
            insert_batch_output_hashes[name] = hashes
            insert_hashes[name] = digest(hashes)
            serialization_retries += retries
            journal.emit("STAGE_PASS", name.upper(),
                         batches=len(hashes), elapsed_ms=elapsed,
                         output_set_sha256=insert_hashes[name], retries=retries)
        counts_raw, counts_ms = cloud_adapter._sql(config, sql_env, execute=count_sql)
        actual_counts = parse_count_row(counts_raw)
        expected_counts = (
            manifest["counts"]["tasks"], manifest["counts"]["events"],
            manifest["counts"]["receipts"], manifest["counts"]["vectors"],
        )
        if actual_counts != expected_counts:
            raise LiveBulkError("INSERT_COUNT_MISMATCH")
        journal.emit("STAGE_PASS", "COUNTS", actual_counts=list(actual_counts),
                     expected_counts=list(expected_counts), elapsed_ms=counts_ms)
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
        journal.emit("STAGE_START", "CLEANUP")
        cleanup_ms, cleanup_output_hashes, cleanup_retries = execute_cleanup_batches(
            config, sql_env, generated, manifest, journal,
        )
        residue_raw, residue_ms = cloud_adapter._sql(config, sql_env, execute=count_sql)
        residue_counts = parse_count_row(residue_raw)
        if residue_counts != (0, 0, 0, 0):
            raise LiveBulkError("CLEANUP_RESIDUE")
        cleanup_receipt = write_receipt(
            evidence / "cleanup.json", "hardening-gate7-live-bulk-cleanup-v2", {
                "campaign_id": campaign_id,
                "status": "PASS",
                "cleanup_output_set_sha256": digest(cleanup_output_hashes),
                "cleanup_batches": len(cleanup_output_hashes),
                "cleanup_retries": cleanup_retries,
                "cleanup_ms": cleanup_ms,
                "residue_output_sha256": digest(residue_raw),
                "residue_ms": residue_ms,
                "residue_counts": list(residue_counts),
            },
        )
        journal.emit("STAGE_PASS", "CLEANUP", cleanup_receipt_sha256=cleanup_receipt["receipt_sha256"])
        result_body = {
            "version": "hardening-gate7-live-bulk-result-v2",
            "campaign_id": campaign_id,
            "manifest_sha256": manifest["manifest_sha256"],
            "before_count_output_sha256": digest(before_raw),
            "count_output_sha256": digest(counts_raw),
            "expected_counts": manifest["counts"],
            "actual_counts": list(actual_counts),
            "insert_latency_ms": insert_latencies,
            "insert_output_hashes": insert_hashes,
            "insert_batch_output_hashes": insert_batch_output_hashes,
            "serialization_retries": serialization_retries,
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
            "cleanup_output_set_sha256": digest(cleanup_output_hashes),
            "cleanup_batches": len(cleanup_output_hashes),
            "cleanup_retries": cleanup_retries,
            "cleanup_ms": cleanup_ms,
            "residue_output_sha256": digest(residue_raw),
            "residue_ms": residue_ms,
            "residue_counts": list(residue_counts),
            "cleanup_receipt_sha256": cleanup_receipt["receipt_sha256"],
            "journal_terminal_prior_hash": journal.prior_hash,
            "credential_bytes_recorded": False,
            "worker_received_credentials": False,
            "synthetic_only": True,
        }
        result_body["green"] = (
            len(query_results) == QUERY_SAMPLES
            and actual_counts == expected_counts
            and residue_counts == (0, 0, 0, 0)
            and sum(len(rows) for rows in insert_batch_output_hashes.values()) == sum(
                len(rows) for rows in manifest["batches"].values()
            )
            and active_max >= 2
            and result_body["query_latency_ms"]["p99"] <= QUERY_P99_LIMIT_MS
            and result_body["insert_total_ms"] <= INSERT_TOTAL_LIMIT_MS
            and b"\n0\n" in rollback_raw
            and b"\n1\n" in duplicate_raw
        )
        result = dict(result_body, result_sha256=digest(result_body))
        atomic_write(evidence / "result.json", canonical(result))
        journal.emit("TERMINAL_PASS", "TERMINAL", process_exit_status=0,
                     signal=None, result_sha256=result["result_sha256"])
        write_receipt(
            evidence / "terminal.json", "hardening-gate7-live-bulk-terminal-v2", {
                "campaign_id": campaign_id,
                "status": "GREEN",
                "process_exit_status": 0,
                "signal": None,
                "result_sha256": result["result_sha256"],
                "journal_terminal_hash": journal.prior_hash,
            },
        )
        return result
    except BaseException as exc:
        failure_fields = external_failure_fields(exc)
        failure_receipt = write_receipt(
            evidence / "failure.json", "hardening-gate7-live-bulk-failure-v2", {
                "campaign_id": campaign_id,
                "stage": journal.stage,
                "batch_index": journal.batch_index,
                **failure_fields,
            },
        )
        journal.emit("TERMINAL_FAIL", "TERMINAL",
                     failure_receipt_sha256=failure_receipt["receipt_sha256"],
                     **failure_fields)
        if sql_env is not None and cleanup_receipt is None:
            try:
                cleanup_ms, cleanup_output_hashes, cleanup_retries = execute_cleanup_batches(
                    config, sql_env, generated, manifest, journal,
                )
                count_sql = campaign_count_sql(prefix)
                residue_raw, residue_ms = cloud_adapter._sql(
                    config, sql_env, execute=count_sql, timeout=120,
                )
                residue_counts = parse_count_row(residue_raw)
                cleanup_receipt = write_receipt(
                    evidence / "cleanup.json", "hardening-gate7-live-bulk-cleanup-v2", {
                        "campaign_id": campaign_id,
                        "status": "PASS" if residue_counts == (0, 0, 0, 0) else "BLOCKED",
                        "cleanup_output_set_sha256": digest(cleanup_output_hashes),
                        "cleanup_batches": len(cleanup_output_hashes),
                        "cleanup_retries": cleanup_retries,
                        "cleanup_ms": cleanup_ms,
                        "residue_output_sha256": digest(residue_raw),
                        "residue_ms": residue_ms,
                        "residue_counts": list(residue_counts),
                    },
                )
            except BaseException as cleanup_exc:
                cleanup_receipt = write_receipt(
                    evidence / "cleanup.json", "hardening-gate7-live-bulk-cleanup-v2", {
                        "campaign_id": campaign_id,
                        "status": "BLOCKED",
                        "failure": external_failure_fields(cleanup_exc),
                    },
                )
        write_receipt(
            evidence / "terminal.json", "hardening-gate7-live-bulk-terminal-v2", {
                "campaign_id": campaign_id,
                "status": "BLOCKED",
                "process_exit_status": 2,
                "signal": failure_fields["signal"],
                "failure_receipt_sha256": failure_receipt["receipt_sha256"],
                "cleanup_receipt_sha256": (
                    cleanup_receipt["receipt_sha256"] if cleanup_receipt else None
                ),
                "journal_terminal_hash": journal.prior_hash,
            },
        )
        raise
    finally:
        if sql_env is not None:
            sql_env.pop("PGPASSWORD", None)
        for index in range(len(secret)):
            secret[index] = 0


def validate_terminal_evidence(evidence: Path) -> dict[str, Any]:
    """Fail closed when terminal, cleanup, or result custody is incomplete."""
    terminal_path = evidence / "terminal.json"
    cleanup_path = evidence / "cleanup.json"
    if not terminal_path.is_file():
        raise LiveBulkError("TERMINAL_RECEIPT_MISSING")
    if not cleanup_path.is_file():
        raise LiveBulkError("CLEANUP_RECEIPT_MISSING")
    terminal = json.loads(terminal_path.read_bytes())
    cleanup = json.loads(cleanup_path.read_bytes())
    for value in (terminal, cleanup):
        body = {key: item for key, item in value.items() if key != "receipt_sha256"}
        if value.get("receipt_sha256") != digest(body):
            raise LiveBulkError("RECEIPT_HASH_INVALID")
    if cleanup.get("status") != "PASS" or cleanup.get("residue_counts") != [0, 0, 0, 0]:
        raise LiveBulkError("CLEANUP_RECEIPT_BLOCKED")
    if terminal.get("status") == "GREEN":
        result_path = evidence / "result.json"
        if not result_path.is_file():
            raise LiveBulkError("RESULT_RECEIPT_MISSING")
        result = json.loads(result_path.read_bytes())
        body = {key: item for key, item in result.items() if key != "result_sha256"}
        if result.get("result_sha256") != digest(body) or result.get("green") is not True:
            raise LiveBulkError("RESULT_RECEIPT_INVALID")
        if terminal.get("result_sha256") != result["result_sha256"]:
            raise LiveBulkError("TERMINAL_RESULT_LINK_INVALID")
    elif terminal.get("status") != "BLOCKED":
        raise LiveBulkError("TERMINAL_STATUS_INVALID")
    return {
        "status": terminal["status"],
        "terminal_receipt_sha256": terminal["receipt_sha256"],
        "cleanup_receipt_sha256": cleanup["receipt_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--generated-root", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()
    if args.generate_only:
        manifest = build_sql(args.campaign_id, args.generated_root.resolve())
        print(canonical({
            "status": "GENERATED", "manifest_sha256": manifest["manifest_sha256"]
        }).decode("utf-8"))
        return 0
    if args.config is None or args.evidence_root is None:
        raise LiveBulkError("LIVE_ARGUMENTS_REQUIRED")
    evidence = args.evidence_root.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    stdout_log = DurableTextLog(evidence / "controller.stdout.log")
    stderr_log = DurableTextLog(evidence / "controller.stderr.log")
    journal = DurableJournal(evidence / "journal.ndjson", args.campaign_id)
    prior_handlers: dict[int, Any] = {}

    def interrupted(signum: int, _frame: Any) -> None:
        raise LiveBulkInterrupted("SIGNAL_" + signal.Signals(signum).name)

    for signum in (signal.SIGINT, signal.SIGTERM):
        prior_handlers[signum] = signal.signal(signum, interrupted)
    try:
        with contextlib.redirect_stdout(stdout_log), contextlib.redirect_stderr(stderr_log):
            journal.emit("PROCESS_START", "BOOT", process_id=os.getpid(),
                         process_exit_status=None, signal=None)
            try:
                manifest = build_sql(args.campaign_id, args.generated_root.resolve())
                journal.emit("STAGE_PASS", "GENERATE",
                             manifest_sha256=manifest["manifest_sha256"],
                             unique_vector_digests=manifest["unique_vector_digests"])
                result = run_live(args.config, args.generated_root.resolve(), evidence, journal)
                print(canonical({"status": "GREEN", "result_sha256": result["result_sha256"]}).decode("utf-8"))
                return 0 if result["green"] else 2
            except BaseException as exc:
                if not (evidence / "failure.json").exists():
                    fields = external_failure_fields(exc)
                    failure = write_receipt(
                        evidence / "failure.json", "hardening-gate7-live-bulk-failure-v2", {
                            "campaign_id": args.campaign_id,
                            "stage": journal.stage,
                            "batch_index": journal.batch_index,
                            **fields,
                        },
                    )
                    journal.emit("TERMINAL_FAIL", "TERMINAL",
                                 failure_receipt_sha256=failure["receipt_sha256"],
                                 **fields)
                    write_receipt(
                        evidence / "terminal.json", "hardening-gate7-live-bulk-terminal-v2", {
                            "campaign_id": args.campaign_id,
                            "status": "BLOCKED",
                            "process_exit_status": 2,
                            "signal": fields["signal"],
                            "failure_receipt_sha256": failure["receipt_sha256"],
                            "cleanup_receipt_sha256": None,
                            "journal_terminal_hash": journal.prior_hash,
                        },
                    )
                print(type(exc).__name__ + ":" + external_failure_fields(exc)["failure_class"],
                      file=sys.stderr)
                return 2
    finally:
        for signum, handler in prior_handlers.items():
            signal.signal(signum, handler)
        journal.close()
        stdout_log.close()
        stderr_log.close()


if __name__ == "__main__":
    raise SystemExit(main())
