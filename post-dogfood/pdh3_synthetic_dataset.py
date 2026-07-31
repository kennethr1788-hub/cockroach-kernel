#!/usr/bin/env python3
"""Credential-free deterministic SQL dataset builder for PDH-3 evidence runs.

This module deliberately contains no cloud adapter, AWS, credential, provider,
or lifecycle imports.  It is safe to include in the remote evidence bundle and
is the only source used by the local canary to prepare synthetic application
rows.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any


BASE = Path(__file__).resolve().parents[1]
P9_CLOUD = BASE / "p9-cloud"
if str(P9_CLOUD) not in sys.path:
    sys.path.insert(0, str(P9_CLOUD))

import context_vector  # type: ignore  # noqa: E402


CAMPAIGN_RE = re.compile(r"^ck-[A-Za-z0-9-]+$")


class SyntheticDatasetError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
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
        raise SyntheticDatasetError("SQL_VALUE_INVALID")
    return "'" + value.replace("'", "''") + "'"


def byte_literal(value: str) -> str:
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise SyntheticDatasetError("HASH_INVALID")
    return "decode('" + value + "','hex')"


def vector_literal(value: list[float]) -> str:
    if len(value) != 64:
        raise SyntheticDatasetError("VECTOR_INVALID")
    return "'[" + ",".join(format(item, ".6f") for item in value) + "]'::VECTOR(64)"


def vector_text(task_index: int, sequence: int) -> str:
    return (
        f"continue synthetic task {task_index} trajectory segment {sequence} "
        f"eventkey t{task_index}s{sequence}"
    )


def hash_for(*parts: object) -> str:
    return digest({"parts": list(parts)})


def batched(values: list[str], size: int) -> list[list[str]]:
    return [values[index:index + size] for index in range(0, len(values), size)]


def build_sql(
    campaign_id: str,
    output: Path,
    *,
    tasks: int,
    events_per_task: int,
    receipts_per_task: int,
    vectors_per_task: int,
    query_samples: int,
    concurrency: int,
    task_id_width: int,
    batch_size: int = 250,
    cleanup_task_batch_size: int = 250,
    cleanup_vector_row_batch_size: int = 250,
) -> dict[str, Any]:
    """Write one deterministic, synthetic-only SQL dataset and manifest."""
    if not CAMPAIGN_RE.fullmatch(campaign_id):
        raise SyntheticDatasetError("CAMPAIGN_ID_INVALID")
    numeric = (
        tasks,
        events_per_task,
        receipts_per_task,
        vectors_per_task,
        query_samples,
        concurrency,
        task_id_width,
        batch_size,
        cleanup_task_batch_size,
        cleanup_vector_row_batch_size,
    )
    if any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in numeric):
        raise SyntheticDatasetError("DATASET_PARAMETER_INVALID")
    if receipts_per_task > events_per_task or vectors_per_task > events_per_task:
        raise SyntheticDatasetError("DATASET_CARDINALITY_INVALID")
    if query_samples > tasks:
        raise SyntheticDatasetError("QUERY_SAMPLE_CARDINALITY_INVALID")

    prefix = campaign_id + "-"
    output.mkdir(parents=True, exist_ok=False)
    task_rows: list[str] = []
    event_rows: list[str] = []
    receipt_rows: list[str] = []
    vector_rows: list[str] = []
    vector_digest_counts: dict[str, int] = {}
    vector_ids: set[str] = set()
    vector_linkages: set[tuple[str, str, str]] = set()
    query_vectors: list[tuple[str, list[float]]] = []

    for task_index in range(tasks):
        task_id = f"{prefix}task-{task_index:0{task_id_width}d}"
        task_hash = hash_for(campaign_id, "task", task_index)
        state_hash = hash_for(campaign_id, "state", task_index)
        task_json = canonical({"synthetic": True, "task": task_index}).decode("utf-8")
        task_rows.append(
            f"({sql_literal(task_id)},{sql_literal(campaign_id)},"
            f"{sql_literal(task_json)}::JSONB,{byte_literal(task_hash)},"
            f"{byte_literal(state_hash)})"
        )
        parent = "0" * 64
        for sequence in range(events_per_task):
            event_id = f"{task_id}-event-{sequence:02d}"
            event_hash = hash_for(campaign_id, "event", task_index, sequence)
            event_json = canonical({"synthetic": True, "sequence": sequence}).decode("utf-8")
            event_rows.append(
                f"({sql_literal(event_id)},{sql_literal(task_id)},{sequence},"
                f"{byte_literal(parent)},{byte_literal(state_hash)},"
                f"{sql_literal(event_json)}::JSONB,{byte_literal(event_hash)})"
            )
            if sequence < receipts_per_task:
                receipt_hash = hash_for(campaign_id, "receipt", task_index, sequence)
                receipt_json = canonical({"synthetic": True, "receipt": sequence}).decode("utf-8")
                receipt_rows.append(
                    f"({byte_literal(receipt_hash)},{sql_literal(task_id)},"
                    f"{byte_literal(event_hash)},'SEALED',"
                    f"{sql_literal(receipt_json)}::JSONB)"
                )
            if sequence < vectors_per_task:
                text = vector_text(task_index, sequence)
                vector = context_vector.context_vector(text, campaign_id)
                vector_digest = context_vector.vector_digest(vector)
                vector_id = f"{task_id}-vector-{sequence:02d}"
                linkage = (task_id, event_hash, campaign_id)
                if vector_id in vector_ids:
                    raise SyntheticDatasetError("VECTOR_ID_COLLISION")
                if linkage in vector_linkages:
                    raise SyntheticDatasetError("VECTOR_LINKAGE_COLLISION")
                vector_ids.add(vector_id)
                vector_linkages.add(linkage)
                vector_digest_counts[vector_digest] = vector_digest_counts.get(vector_digest, 0) + 1
                vector_rows.append(
                    f"({sql_literal(vector_id)},{sql_literal(task_id)},"
                    f"{byte_literal(event_hash)},{sql_literal(campaign_id)},"
                    f"{vector_literal(vector)},{byte_literal(vector_digest)})"
                )
                if task_index < query_samples and sequence == 0:
                    query_vectors.append((task_id, vector))
            parent = event_hash

    tables = {
        "tasks": ("ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash)", task_rows),
        "events": (
            "ck.trajectory_events(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash)",
            event_rows,
        ),
        "receipts": (
            "ck.receipts(receipt_hash,task_id,event_hash,status,receipt_json)",
            receipt_rows,
        ),
        "vectors": (
            "ck.context_vectors(vector_id,task_id,event_hash,namespace,vector,vector_digest)",
            vector_rows,
        ),
    }
    sql_hashes: dict[str, str] = {}
    batch_files: dict[str, list[dict[str, Any]]] = {}
    for name, (columns, rows) in tables.items():
        batch_files[name] = []
        for batch_index, group in enumerate(batched(rows, batch_size), start=1):
            raw = (
                "BEGIN;\nINSERT INTO " + columns + " VALUES "
                + ",".join(group) + ";\nCOMMIT;\n"
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

    query_specs: list[dict[str, Any]] = []
    for index, (task_id, vector) in enumerate(query_vectors, start=1):
        statement = (
            "SELECT vector_id FROM ck.context_vectors "
            f"WHERE task_id={sql_literal(task_id)} AND namespace={sql_literal(campaign_id)} "
            f"ORDER BY vector <-> {vector_literal(vector)} LIMIT 1;"
        )
        query_specs.append(
            {
                "index": index,
                "task_id": task_id,
                "sql": statement,
                "expected_vector_id": task_id + "-vector-00",
                "sql_sha256": digest(statement.encode("utf-8")),
            }
        )
    query_path = output / "query-specs.json"
    atomic_write(query_path, canonical(query_specs))

    cleanup_batches: list[dict[str, Any]] = []

    def add_cleanup(
        stage: str,
        statement: str,
        *,
        task_count: int,
        row_limit: int | None = None,
    ) -> None:
        stage_index = 1 + sum(row["stage"] == stage for row in cleanup_batches)
        raw = (
            "BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;\n"
            + statement + "\nCOMMIT;\n"
        ).encode("utf-8")
        path = output / f"cleanup-{stage}-batch-{stage_index:04d}.sql"
        atomic_write(path, raw)
        cleanup_batches.append(
            {
                "path": path.name,
                "sha256": digest(raw),
                "stage": stage,
                "batch_index": stage_index,
                "task_count": task_count,
                "row_limit": row_limit,
            }
        )

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
    task_ids = [f"{prefix}task-{index:0{task_id_width}d}" for index in range(tasks)]
    vector_batches = (
        tasks * vectors_per_task + cleanup_vector_row_batch_size - 1
    ) // cleanup_vector_row_batch_size
    for _ in range(vector_batches):
        add_cleanup(
            "vectors",
            "DELETE FROM ck.context_vectors "
            f"WHERE vector_id LIKE {sql_literal(prefix + '%')} "
            f"ORDER BY vector_id LIMIT {cleanup_vector_row_batch_size};",
            task_count=0,
            row_limit=cleanup_vector_row_batch_size,
        )
    for table, stage in (
        ("ck.receipts", "receipts"),
        ("ck.trajectory_events", "events"),
        ("ck.tasks", "tasks"),
    ):
        for group in batched(task_ids, cleanup_task_batch_size):
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

    cleanup_plan = b"".join((output / row["path"]).read_bytes() for row in cleanup_batches)
    atomic_write(output / "cleanup.sql", cleanup_plan)
    cleanup_manifest_body = {
        "version": "ck-pdh3-synthetic-cleanup-manifest-v1",
        "campaign_id": campaign_id,
        "default_task_batch_size": cleanup_task_batch_size,
        "vector_row_batch_size": cleanup_vector_row_batch_size,
        "vector_batch_count": vector_batches,
        "batch_count": len(cleanup_batches),
        "batches": cleanup_batches,
        "composed_cleanup_sha256": digest(cleanup_plan),
    }
    cleanup_manifest = {
        **cleanup_manifest_body,
        "cleanup_manifest_sha256": digest(cleanup_manifest_body),
    }
    atomic_write(output / "cleanup-manifest.json", canonical(cleanup_manifest))

    manifest_body = {
        "version": "ck-pdh3-synthetic-manifest-v1",
        "campaign_id": campaign_id,
        "synthetic_only": True,
        "credential_material": False,
        "counts": {
            "tasks": tasks,
            "events": tasks * events_per_task,
            "receipts": tasks * receipts_per_task,
            "vectors": tasks * vectors_per_task,
            "vector_queries": query_samples,
        },
        "concurrency": concurrency,
        "task_id_width": task_id_width,
        "batch_size": batch_size,
        "batches": batch_files,
        "vector_digest_policy": "NON_UNIQUE_CONTENT_DIGEST_EXACT_ROW_LINKAGE",
        "unique_vector_digests": len(vector_digest_counts),
        "vector_digest_collisions": sum(
            count - 1 for count in vector_digest_counts.values() if count > 1
        ),
        "max_vector_digest_multiplicity": max(vector_digest_counts.values()),
        "unique_vector_ids": len(vector_ids),
        "unique_vector_linkages": len(vector_linkages),
        "sql_files": sql_hashes,
        "query_specs_sha256": digest(query_path.read_bytes()),
        "cleanup_manifest_sha256": cleanup_manifest["cleanup_manifest_sha256"],
        "cleanup_batch_count": len(cleanup_batches),
        "cleanup_sha256": digest(cleanup_plan),
        "credential_location": "NONE_SYNTHETIC_GENERATOR",
    }
    manifest = {**manifest_body, "manifest_sha256": digest(manifest_body)}
    atomic_write(output / "manifest.json", canonical(manifest))
    return manifest
