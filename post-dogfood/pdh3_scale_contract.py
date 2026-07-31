#!/usr/bin/env python3
"""Frozen constants and validation for the final PDH-3 scale campaign."""
from __future__ import annotations

import hashlib
import json
from typing import Any


VERSION = "ck-pdh3-production-scale-contract-v1"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
PLAN_SHA256 = "bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24"

MEASURED_SECONDS = 86_400
MAX_PAID_SECONDS = 100_800
CHECKPOINT_SECONDS = 300
REQUIRED_CHECKPOINTS = 288
QUERY_DURATION_SECONDS = 120
SEED_BATCH_TASKS = 5_000
SETUP_TIMEOUT_SECONDS = 5_400
FAULT_EVERY_CHECKPOINTS = 12
NODE_CACHE = "8GiB"
NODE_SQL_MEMORY = "8GiB"

TASKS = 500_000
EVENTS_PER_TASK = 10
RECEIPTS_PER_TASK = 2
VECTORS = 250_000
VERIFIER_EXECUTIONS = 9_976
VERIFIER_BATCH_SIZE = 43
VERIFIER_BATCHES = 232

CONCURRENCY_STAGES = (10, 50, 100, 250, 500)
MAX_CONCURRENCY = 500
P99_LIMIT_MS = 5_000.0
PMAX_LIMIT_MS = 10_000.0
DATABASE_BYTES_LIMIT = 100 * 1024**3
EVIDENCE_BYTES_LIMIT = 20 * 1024**3
DISK_USED_FRACTION_LIMIT = 0.70

RUNPOD = {
    "cloud": "SECURE",
    "gpu_id": "NVIDIA L40S",
    "gpu_count": 1,
    "image": "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
    "ports": ["22/tcp"],
    "global_networking": False,
    "vcpu": 16,
    "ram_gb": 94,
    "container_disk_gb": 250,
    "volume_gb": 0,
    "network_volume": None,
    "compute_rate_usd_hour_max": 0.99,
    "active_rate_usd_hour_max": 1.10,
    "aggregate_cost_usd_max": 35.00,
    "measured_seconds": MEASURED_SECONDS,
    "paid_seconds_max": MAX_PAID_SECONDS,
}

FORBIDDEN_RUNTIME_DEPENDENCIES = (
    "AWS credentials or login",
    "CockroachDB Cloud credentials or login",
    "GitHub credentials or login",
    "package-registry credentials",
    "persistent or network volume",
    "private, client, or production data",
)


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


def production_contract() -> dict[str, Any]:
    body = {
        "version": VERSION,
        "product_candidate": PRODUCT_CANDIDATE,
        "plan_sha256": PLAN_SHA256,
        "runpod": RUNPOD,
        "workload": {
            "tasks": TASKS,
            "trajectory_events": TASKS * EVENTS_PER_TASK,
            "receipts": TASKS * RECEIPTS_PER_TASK,
            "task_bound_vectors": VECTORS,
            "verifier_executions": VERIFIER_EXECUTIONS,
            "verifier_batches": VERIFIER_BATCHES,
            "concurrency_stages": list(CONCURRENCY_STAGES),
            "checkpoints": REQUIRED_CHECKPOINTS,
            "checkpoint_seconds": CHECKPOINT_SECONDS,
            "query_duration_seconds": QUERY_DURATION_SECONDS,
            "seed_batch_tasks": SEED_BATCH_TASKS,
            "setup_timeout_seconds": SETUP_TIMEOUT_SECONDS,
            "fault_every_checkpoints": FAULT_EVERY_CHECKPOINTS,
            "node_cache": NODE_CACHE,
            "node_sql_memory": NODE_SQL_MEMORY,
        },
        "thresholds": {
            "p99_ms": P99_LIMIT_MS,
            "pmax_ms": PMAX_LIMIT_MS,
            "database_bytes": DATABASE_BYTES_LIMIT,
            "evidence_bytes": EVIDENCE_BYTES_LIMIT,
            "disk_used_fraction": DISK_USED_FRACTION_LIMIT,
            "false_promotions": 0,
            "cross_task_vector_links": 0,
            "acknowledged_write_loss": 0,
            "accepted_replays": 0,
            "residual_paid_resources": 0,
        },
        "forbidden_runtime_dependencies": list(FORBIDDEN_RUNTIME_DEPENDENCIES),
    }
    return {**body, "contract_sha256": digest(body)}


def validate_production_arguments(arguments: dict[str, Any]) -> None:
    expected = {
        "duration_seconds": MEASURED_SECONDS,
        "checkpoint_seconds": CHECKPOINT_SECONDS,
        "tasks": TASKS,
        "events_per_task": EVENTS_PER_TASK,
        "receipts_per_task": RECEIPTS_PER_TASK,
        "vectors": VECTORS,
        "max_concurrency": MAX_CONCURRENCY,
        "disk_used_fraction_limit": DISK_USED_FRACTION_LIMIT,
        "query_duration_seconds": QUERY_DURATION_SECONDS,
        "seed_batch_tasks": SEED_BATCH_TASKS,
        "setup_timeout_seconds": SETUP_TIMEOUT_SECONDS,
        "fault_every_checkpoints": FAULT_EVERY_CHECKPOINTS,
        "cache": NODE_CACHE,
        "sql_memory": NODE_SQL_MEMORY,
    }
    mismatches = {
        key: {"expected": value, "actual": arguments.get(key)}
        for key, value in expected.items()
        if arguments.get(key) != value
    }
    if mismatches:
        raise ValueError("PRODUCTION_ARGUMENT_MISMATCH:" + digest(mismatches))


if __name__ == "__main__":
    print(canonical(production_contract()).decode("utf-8"))
