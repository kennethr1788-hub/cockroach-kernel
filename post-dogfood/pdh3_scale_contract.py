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
SETUP_TIMEOUT_SECONDS = 10_800
SETUP_SUCCESS_MARGIN_SECONDS = 300
FAULT_EVERY_CHECKPOINTS = 12
REMOTE_PREFLIGHT_EPOCHS = 3
REMOTE_PREFLIGHT_CONCURRENCY = 500
REMOTE_PREFLIGHT_FAULTS = 3
TRACE_BYTES_LIMIT = 2 * 1024**3
TRACE_PREFLIGHT_PROJECTION_LIMIT = int(TRACE_BYTES_LIMIT * 0.80)
NODE_CACHE = "8GiB"
NODE_SQL_MEMORY = "8GiB"
EGRESS_OBSERVATION = "strace-process-tree-connect-sendto-v2"
EXTERNAL_EGRESS_ALLOWED = 0
STRACE_DEB_SHA256 = "d588810ae26b06fee6678dc81e5b54f6efcde8e718e4589adb4d11d254b9820b"
LIBUNWIND8_DEB_SHA256 = "658977d18976149b75391850ba0ccacaf7bde3201f0284189da50cd634334d17"
STRACE_BINARY_SHA256 = "28f957c227012de0b18d1bd7fff2d396cb693ea60ed8013be68de071e84b5001"

TASKS = 500_000
EVENTS_PER_TASK = 10
RECEIPTS_PER_TASK = 2
VECTORS = 250_000
VERIFIER_EXECUTIONS = 9_976
VERIFIER_BATCH_SIZE = 43
VERIFIER_BATCHES = 232

CONCURRENCY_STAGES = (10, 50, 100, 250, 500)
CONTENDED_COUNTER_SHARDS = 16
MAX_CONCURRENCY = 500
P99_LIMIT_MS = 5_000.0
PMAX_LIMIT_MS = 10_000.0
DATABASE_BYTES_LIMIT = 100 * 1024**3
EVIDENCE_BYTES_LIMIT = 20 * 1024**3
DISK_USED_FRACTION_LIMIT = 0.70
RSS_KB_LIMIT = 80 * 1024**2
FILE_DESCRIPTORS_PER_NODE_LIMIT = 65_536
REQUIRED_LIVE_NODE_PROCESSES = 3
PROCESS_TREE_COUNT_LIMIT = 64

RUNPOD = {
    "cloud": "SECURE",
    "gpu_id": "NVIDIA L40S",
    "gpu_count": 1,
    "image": "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
    "ports": ["22/tcp"],
    "global_networking": False,
    "vcpu_min": 16,
    "vcpu_max": 32,
    "ram_gb_min": 94,
    "ram_gb_max": 188,
    "container_disk_gb": 250,
    "volume_gb": 0,
    "network_volume": None,
    "compute_rate_usd_hour_max": 0.99,
    "active_rate_usd_hour_max": 1.10,
    # The original campaign envelope was USD 35.00. The operator explicitly
    # authorized replacement lifecycles after failed premeasurement attempts.
    # Preserve USD 35.00 for the newly authorized lifecycle while retaining
    # every prior attempt, including R10, inside a minimally raised cumulative
    # ceiling mechanically sufficient for one full 100,800-second lifecycle.
    "replacement_cost_usd_max": 35.00,
    "aggregate_cost_usd_max": 39.00,
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
            "contended_counter_shards": CONTENDED_COUNTER_SHARDS,
            "checkpoints": REQUIRED_CHECKPOINTS,
            "checkpoint_seconds": CHECKPOINT_SECONDS,
            "query_duration_seconds": QUERY_DURATION_SECONDS,
            "seed_batch_tasks": SEED_BATCH_TASKS,
            "setup_timeout_seconds": SETUP_TIMEOUT_SECONDS,
            "setup_success_margin_seconds": SETUP_SUCCESS_MARGIN_SECONDS,
            "fault_every_checkpoints": FAULT_EVERY_CHECKPOINTS,
            "remote_preflight_epochs": REMOTE_PREFLIGHT_EPOCHS,
            "remote_preflight_concurrency": REMOTE_PREFLIGHT_CONCURRENCY,
            "remote_preflight_faults": REMOTE_PREFLIGHT_FAULTS,
            "node_cache": NODE_CACHE,
            "node_sql_memory": NODE_SQL_MEMORY,
        },
        "thresholds": {
            "p99_ms": P99_LIMIT_MS,
            "pmax_ms": PMAX_LIMIT_MS,
            "database_bytes": DATABASE_BYTES_LIMIT,
            "evidence_bytes": EVIDENCE_BYTES_LIMIT,
            "disk_used_fraction": DISK_USED_FRACTION_LIMIT,
            "rss_kb_total": RSS_KB_LIMIT,
            "file_descriptors_per_node": FILE_DESCRIPTORS_PER_NODE_LIMIT,
            "live_node_processes": REQUIRED_LIVE_NODE_PROCESSES,
            "process_tree_count": PROCESS_TREE_COUNT_LIMIT,
            "false_promotions": 0,
            "cross_task_vector_links": 0,
            "acknowledged_write_loss": 0,
            "accepted_replays": 0,
            "residual_paid_resources": 0,
            "external_egress_destinations": EXTERNAL_EGRESS_ALLOWED,
            "trace_bytes": TRACE_BYTES_LIMIT,
            "trace_preflight_projected_bytes": TRACE_PREFLIGHT_PROJECTION_LIMIT,
        },
        "egress_evidence": {
            "mechanism": EGRESS_OBSERVATION,
            "claim": "PROCESS_TREE_OBSERVED_ZERO_EXTERNAL_EGRESS",
            "network_namespace": False,
            "firewall": False,
            "strace_deb_sha256": STRACE_DEB_SHA256,
            "libunwind8_deb_sha256": LIBUNWIND8_DEB_SHA256,
            "strace_binary_sha256": STRACE_BINARY_SHA256,
        },
        "forbidden_runtime_dependencies": list(FORBIDDEN_RUNTIME_DEPENDENCIES),
    }
    return {**body, "contract_sha256": digest(body)}


def expected_schedule() -> dict[str, Any]:
    """Return the exact mechanically checkable 24-hour execution schedule."""
    checkpoints = MEASURED_SECONDS // CHECKPOINT_SECONDS
    concurrency = [
        min(MAX_CONCURRENCY, CONCURRENCY_STAGES[min(epoch, len(CONCURRENCY_STAGES) - 1)])
        for epoch in range(checkpoints)
    ]
    verifier_batches = min(VERIFIER_BATCHES, checkpoints)
    fault_epochs = [
        epoch + 1
        for epoch in range(checkpoints)
        if (epoch + 1) % FAULT_EVERY_CHECKPOINTS == 0
    ]
    return {
        "checkpoints": checkpoints,
        "concurrency": concurrency,
        "concurrency_counts": {
            str(value): concurrency.count(value) for value in CONCURRENCY_STAGES
        },
        "verifier_batches": verifier_batches,
        "verifier_executions": verifier_batches * VERIFIER_BATCH_SIZE,
        "fault_epochs": fault_epochs,
        "fault_count": len(fault_epochs),
        "fault_targets": [index % 3 for index in range(len(fault_epochs))],
    }


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
        "store_size": None,
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
