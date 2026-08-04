"""Read-only Cockroach memory inspection skill.

The caller supplies a bounded snapshot obtained through an approved read-only
CockroachDB surface. This module performs no network access and has no write or
recovery authority; it only checks receipt/vector linkage and emits an
advisory, hash-bound inspection report.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any

MAX_SNAPSHOT_BYTES = 65_536
MAX_ROWS = 64
VERSION = "ck-memory-snapshot-v1"
REPORT_VERSION = "ck-memory-inspection-v1"
HASH_KEYS = ("receipt_hash", "event_hash", "vector_digest")


class MemorySkillError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    try:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode()
    except (TypeError, ValueError) as exc:
        raise MemorySkillError("SNAPSHOT_NOT_CANONICAL") from exc
    if len(raw) > MAX_SNAPSHOT_BYTES:
        raise MemorySkillError("SNAPSHOT_TOO_LARGE")
    return raw


def _hash(value: Any) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise MemorySkillError("HASH_INVALID")
    try:
        int(value, 16)
    except ValueError as exc:
        raise MemorySkillError("HASH_INVALID") from exc
    return value


def _row(value: Any, fields: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise MemorySkillError("ROW_FIELDS_INVALID")
    return value


def inspect_snapshot(snapshot: Any) -> dict[str, Any]:
    if not isinstance(snapshot, dict) or set(snapshot) != {"version", "receipts", "vectors"}:
        raise MemorySkillError("SNAPSHOT_FIELDS_INVALID")
    if snapshot["version"] != VERSION:
        raise MemorySkillError("SNAPSHOT_VERSION_UNSUPPORTED")
    receipts = snapshot["receipts"]
    vectors = snapshot["vectors"]
    if not isinstance(receipts, list) or not isinstance(vectors, list):
        raise MemorySkillError("SNAPSHOT_ROWS_INVALID")
    if len(receipts) > MAX_ROWS or len(vectors) > MAX_ROWS:
        raise MemorySkillError("SNAPSHOT_ROW_LIMIT")

    receipt_rows: list[dict[str, Any]] = []
    by_hash: dict[str, tuple[str, str]] = {}
    by_link: set[tuple[str, str]] = set()
    warnings: list[str] = []
    for value in receipts:
        row = _row(value, {"task_id", "receipt_hash", "event_hash", "status"})
        if not isinstance(row["task_id"], str) or not row["task_id"]:
            raise MemorySkillError("TASK_ID_INVALID")
        if row["status"] not in {"DECLARED", "SEALED", "ADVISORY"}:
            raise MemorySkillError("STATUS_INVALID")
        receipt_hash = _hash(row["receipt_hash"])
        event_hash = _hash(row["event_hash"])
        link = (row["task_id"], event_hash)
        previous = by_hash.get(receipt_hash)
        if previous is not None and previous != link:
            warnings.append("RECEIPT_CONFLICT")
        by_hash[receipt_hash] = link
        by_link.add(link)
        receipt_rows.append({"task_id": row["task_id"], "receipt_hash": receipt_hash,
                             "event_hash": event_hash, "status": row["status"]})

    vector_rows: list[dict[str, Any]] = []
    orphan_count = 0
    for value in vectors:
        row = _row(value, {"task_id", "event_hash", "namespace", "vector_digest", "distance"})
        if not isinstance(row["task_id"], str) or not row["task_id"]:
            raise MemorySkillError("TASK_ID_INVALID")
        if not isinstance(row["namespace"], str) or not row["namespace"]:
            raise MemorySkillError("NAMESPACE_INVALID")
        if not isinstance(row["distance"], (int, float)) or isinstance(row["distance"], bool):
            raise MemorySkillError("DISTANCE_INVALID")
        if not math.isfinite(float(row["distance"])) or row["distance"] < 0:
            raise MemorySkillError("DISTANCE_INVALID")
        event_hash = _hash(row["event_hash"])
        if (row["task_id"], event_hash) not in by_link:
            orphan_count += 1
        vector_rows.append({"task_id": row["task_id"], "event_hash": event_hash,
                            "namespace": row["namespace"], "vector_digest": _hash(row["vector_digest"]),
                            "distance": float(row["distance"])})
    if orphan_count:
        warnings.append("ORPHAN_VECTOR")
    warnings = sorted(set(warnings))
    status = "CONFLICT" if "RECEIPT_CONFLICT" in warnings else ("INCOMPLETE" if warnings else "INSPECTED")
    body = {
        "version": REPORT_VERSION,
        "status": status,
        "receipt_count": len(receipt_rows),
        "vector_count": len(vector_rows),
        "linked_vector_count": len(vector_rows) - orphan_count,
        "task_ids": sorted({row["task_id"] for row in receipt_rows}),
        "warnings": warnings,
        "authority": "NONE_ADVISORY_ONLY",
        "network_used": False,
        "mutation_performed": False,
    }
    body["evidence_hash"] = hashlib.sha256(_canonical(body)).hexdigest()
    return body
