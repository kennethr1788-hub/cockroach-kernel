#!/usr/bin/env python3
"""Offline sizing profile for the bounded Gate 7 CockroachDB workload."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import time
from typing import Any


BASE = Path(__file__).resolve().parents[1]
VECTOR_PATH = BASE / "p9-cloud" / "context_vector.py"
sys.path.insert(0, str(BASE / "p9-cloud"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("MODULE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


vectors = load_module("gate7_context_vector", VECTOR_PATH)


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: bytes | Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def profile(tasks: int, events_per_task: int, receipts_per_task: int,
            vectors_per_task: int, query_samples: int,
            end_to_end_calls: int, concurrency: int) -> dict[str, Any]:
    started = time.monotonic_ns()
    byte_counts = {"tasks": 0, "events": 0, "receipts": 0, "vectors": 0}
    row_hash = hashlib.sha256()
    for task_index in range(tasks):
        task_id = f"g7-load-task-{task_index:06d}"
        task = {"task_id": task_id, "campaign_id": "ck-gate7-load-r1",
                "state": "ACTIVE", "sequence": task_index}
        raw = canonical(task)
        byte_counts["tasks"] += len(raw)
        row_hash.update(raw)
        for sequence in range(events_per_task):
            event = {"task_id": task_id, "sequence": sequence,
                     "state_hash": digest({"task": task_id, "sequence": sequence})}
            raw = canonical(event)
            byte_counts["events"] += len(raw)
            row_hash.update(raw)
        for sequence in range(receipts_per_task):
            receipt = {"task_id": task_id, "sequence": sequence,
                       "receipt_hash": digest({"receipt": task_id, "sequence": sequence})}
            raw = canonical(receipt)
            byte_counts["receipts"] += len(raw)
            row_hash.update(raw)
        for sequence in range(vectors_per_task):
            text = f"continue task {task_index} trajectory segment {sequence}"
            vector = vectors.context_vector(text, "ck-gate7-load-r1")
            row = {"task_id": task_id, "sequence": sequence,
                   "vector": vector, "vector_digest": vectors.vector_digest(vector)}
            raw = canonical(row)
            byte_counts["vectors"] += len(raw)
            row_hash.update(raw)
    elapsed_ms = int((time.monotonic_ns() - started) / 1_000_000)
    counts = {
        "tasks": tasks,
        "events": tasks * events_per_task,
        "receipts": tasks * receipts_per_task,
        "vectors": tasks * vectors_per_task,
        "vector_queries": query_samples,
        "end_to_end_aws_calls": end_to_end_calls,
    }
    body = {
        "version": "hardening-gate7-memory-profile-v1",
        "platform": platform.system(),
        "python": platform.python_version(),
        "concurrency": concurrency,
        "counts": counts,
        "canonical_input_bytes": byte_counts,
        "canonical_input_bytes_total": sum(byte_counts.values()),
        "generation_elapsed_ms": elapsed_ms,
        "row_stream_sha256": row_hash.hexdigest(),
        "scope": "OFFLINE_INPUT_SIZING_NOT_DATABASE_PERFORMANCE",
    }
    body["profile_sha256"] = digest(body)
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", type=int, default=2000)
    parser.add_argument("--events-per-task", type=int, default=10)
    parser.add_argument("--receipts-per-task", type=int, default=2)
    parser.add_argument("--vectors-per-task", type=int, default=10)
    parser.add_argument("--query-samples", type=int, default=200)
    parser.add_argument("--end-to-end-calls", type=int, default=12)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    values = (
        args.tasks, args.events_per_task, args.receipts_per_task,
        args.vectors_per_task, args.query_samples, args.end_to_end_calls,
        args.concurrency,
    )
    if any(value < 1 for value in values):
        raise ValueError("PROFILE_VALUE_INVALID")
    result = profile(*values)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
