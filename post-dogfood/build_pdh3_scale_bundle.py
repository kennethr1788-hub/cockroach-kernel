#!/usr/bin/env python3
"""Build and mechanically verify the credential-free PDH-3 transfer bundle.

The transfer archive is a data-plane artifact.  Host control-plane programs
(the RunPod supervisor and lifecycle guard) are hash-bound in the receipt but
deliberately excluded from the worker archive.  Previous campaign evidence is
also represented only by a hash-only history manifest; raw lifecycle records,
provider responses, and retrieved evidence never enter the worker archive.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import Any, Iterable


BASE = Path(__file__).resolve().parents[1]
MANIFEST_MEMBER = "PDH3_BUNDLE_MANIFEST.json"
HISTORY_MEMBER = "PDH3_ATTEMPT_HISTORY_MANIFEST.json"

# Everything required by the remote campaign and by the bounded extracted-
# bundle smoke.  This is deliberately explicit: no directory recursion, glob,
# or generated file can silently enter the transfer boundary.
REMOTE_FILES = (
    "post-dogfood/pdh3_scale_contract.py",
    "post-dogfood/run_pdh3_scale_campaign.py",
    "post-dogfood/run_pdh3_traced.py",
    "post-dogfood/run_pdh3_local_canary.py",
    "post-dogfood/pdh3_synthetic_dataset.py",
    "post-dogfood/pdh3_r12_plan_ab.py",
    "post-dogfood/pdh3_r12_network_observer.py",
    "post-dogfood/pdh3_r12_checkpoint.py",
    "post-dogfood/pdh3_r12_cpu_affinity.py",
    "post-dogfood/pdh3_r12_remote_capability.py",
    "post-dogfood/pdh3_r12_remote_launcher.py",
    "post-dogfood/pdh3_r12_remote_preflight.py",
    "post-dogfood/build_pdh3_scale_bundle.py",
    "post-dogfood/test_pdh3_scale_contract.py",
    "post-dogfood/test_pdh3_scale_campaign.py",
    "post-dogfood/test_pdh3_local_canary.py",
    "post-dogfood/test_run_pdh3_traced.py",
    "post-dogfood/test_build_pdh3_scale_bundle.py",
    "post-dogfood/test_pdh3_r12_plan_ab.py",
    "post-dogfood/test_pdh3_r12_network_observer.py",
    "post-dogfood/test_pdh3_r12_checkpoint.py",
    "post-dogfood/test_pdh3_r12_cpu_affinity.py",
    "post-dogfood/test_pdh3_r12_remote_capability.py",
    "post-dogfood/test_pdh3_r12_remote_launcher.py",
    "post-dogfood/test_pdh3_r12_remote_preflight.py",
    "hardening-gate7/make_vectors.py",
    "hardening-gate7/run_campaign.py",
    "hardening-gate7/run_trial.py",
    "hardening-gate7/test_gate7.py",
    "hardening-gate5/heldout_contract.py",
    "p4-verifier/verifier.py",
    "p4-verifier/test_verifier.py",
    "p7-recovery/records.py",
    "p9-cloud/records.py",
    "p9-cloud/context_vector.py",
    "p9-cloud/migrations/001_cloud.sql",
    "p9-cloud/migrations/002_runtime_grants.sql",
    "p9-cloud/migrations/003_collision_safe_vector_digest.sql",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/cockroach",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/LICENSE",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/THIRD-PARTY-NOTICES.txt",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/lib/libgeos.so",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/lib/libgeos_c.so",
    "p2-cleanroom/vendor/ubuntu-noble-strace/"
    "strace_6.8-0ubuntu2_amd64.deb",
    "p2-cleanroom/vendor/ubuntu-noble-strace/"
    "libunwind8_1.6.2-3build1_amd64.deb",
    "p2-cleanroom/vendor/python-wheels/"
    "pg8000-1.31.5-py3-none-any.whl",
    "p2-cleanroom/vendor/python-wheels/"
    "scramp-1.4.15-py3-none-any.whl",
    "p2-cleanroom/vendor/python-wheels/"
    "asn1crypto-1.5.1-py2.py3-none-any.whl",
    "p2-cleanroom/vendor/python-wheels/"
    "python_dateutil-2.9.0.post0-py2.py3-none-any.whl",
    "p2-cleanroom/vendor/python-wheels/"
    "six-1.17.0-py2.py3-none-any.whl",
)

# Backwards-compatible name used by older packet tooling.  The tuple is kept
# immutable so tests can prove uniqueness before any bytes are read.
FILES = REMOTE_FILES

# These programs control a paid provider from the trusted host.  They are
# bound for the final packet, but transferring them to the worker would blur
# the control-plane/data-plane boundary and is unnecessary.
HOST_ONLY_FILES = (
    "post-dogfood/supervise_pdh3_scale_campaign.py",
    "post-dogfood/test_supervise_pdh3_scale_campaign.py",
    "s2-soak/lifecycle_guard.py",
    "s2-soak/test_lifecycle_guard.py",
    "post-dogfood/pdh3_r12_lifecycle_launch.py",
    "post-dogfood/test_pdh3_r12_lifecycle_launch.py",
    "post-dogfood/pdh3_r12_preflight.py",
    "post-dogfood/test_pdh3_r12_preflight.py",
    "post-dogfood/pdh3_r12_preflight_supervisor.py",
    "post-dogfood/test_pdh3_r12_preflight_supervisor.py",
    "post-dogfood/pdh3_r12_r6_config.py",
    "post-dogfood/test_pdh3_r12_r6_config.py",
    "post-dogfood/pdh3_r12_r6_launch_pf4.py",
    "post-dogfood/test_pdh3_r12_r6_launch_pf4.py",
    "post-dogfood/pdh3_r12_r6_run_pf4.py",
    "post-dogfood/pdh3_r12_r6_run_pf2r_pf7.py",
    "post-dogfood/pdh3_r12_r6_orchestrator.py",
)

# Hash-only historical custody.  Contents are never copied to the transfer
# archive, which prevents provider responses, SSH material, or logs from
# becoming remote workload inputs.
HISTORY_EVIDENCE = (
    (
        (1, 2, 3, 4, 5, 6, 7),
        "prior_attempt_cost_envelope",
        "PDH_3_PRIOR_ATTEMPT_COST_ENVELOPE_R8.md",
    ),
    ((1,), "summary_receipt", "PDH_3_SCALE_RUNPOD_ATTEMPT_01_RECEIPT.md"),
    ((1,), "create_response", ".pdh3-runtime/preflight-r3/attempt-01-create-response.json"),
    ((1,), "delete_response", ".pdh3-runtime/preflight-r3/attempt-01-delete-response.json"),
    ((1,), "post_delete_absence", ".pdh3-runtime/preflight-r3/attempt-01-post-delete-get.txt"),
    ((1,), "active_inventory", ".pdh3-runtime/preflight-r3/attempt-01-active-after-delete.json"),
    ((2,), "summary_receipt", "PDH_3_SCALE_RUNPOD_ATTEMPT_02_RECEIPT.md"),
    ((2,), "create_response", ".pdh3-runtime/preflight-r4/attempt-02-create-response.json"),
    ((2,), "delete_response", ".pdh3-runtime/preflight-r4/attempt-02-delete-response.json"),
    ((2,), "post_delete_absence", ".pdh3-runtime/preflight-r4/attempt-02-post-delete-get.txt"),
    ((2,), "active_inventory", ".pdh3-runtime/preflight-r4/attempt-02-active-after-delete.json"),
    ((2,), "lifecycle_log", ".pdh3-runtime/preflight-r4/attempt-02-lifecycle-guard.ndjson"),
    ((3,), "summary_receipt", "PDH_3_SCALE_RUNPOD_ATTEMPT_03_RECEIPT.md"),
    ((3,), "create_response", ".pdh3-runtime/preflight-r5/attempt-03-create-response.json"),
    ((3,), "delete_response", ".pdh3-runtime/preflight-r5/attempt-03-delete-response.json"),
    ((3,), "post_delete_absence", ".pdh3-runtime/preflight-r5/attempt-03-post-delete-get.txt"),
    ((3,), "active_inventory", ".pdh3-runtime/preflight-r5/attempt-03-active-after-delete.json"),
    ((3,), "lifecycle_log", ".pdh3-runtime/preflight-r5/attempt-03-lifecycle-guard.ndjson"),
    ((4,), "summary_receipt", "PDH_3_SCALE_RUNPOD_ATTEMPT_04_RECEIPT.md"),
    ((4,), "create_response", ".pdh3-runtime/preflight-r6/attempt-04-create-response.json"),
    ((4,), "delete_response", ".pdh3-runtime/preflight-r6/attempt-04-delete-response.json"),
    ((4,), "post_delete_absence", ".pdh3-runtime/preflight-r6/attempt-04-post-delete-get.txt"),
    ((4,), "active_inventory", ".pdh3-runtime/preflight-r6/attempt-04-active-after-delete.json"),
    ((4,), "lifecycle_log", ".pdh3-runtime/preflight-r6/attempt-04-lifecycle-guard.ndjson"),
    ((5, 6), "summary_receipt", "PDH_3_SCALE_RUNPOD_ATTEMPTS_05_06_RECEIPT.md"),
    ((5,), "create_response", ".pdh3-runtime/preflight-r7/attempt-05-create-response.json"),
    ((5,), "delete_response", ".pdh3-runtime/preflight-r7/attempt-05-delete-response.json"),
    ((5,), "post_delete_absence", ".pdh3-runtime/preflight-r7/attempt-05-post-delete-get.txt"),
    ((5,), "active_inventory", ".pdh3-runtime/preflight-r7/attempt-05-active-after-delete.json"),
    ((5,), "lifecycle_log", ".pdh3-runtime/preflight-r7/attempt-05-lifecycle-guard.ndjson"),
    ((6,), "create_response", ".pdh3-runtime/preflight-r7/attempt-06-create-response.json"),
    ((6,), "delete_response", ".pdh3-runtime/preflight-r7/attempt-06-delete-response.json"),
    ((6,), "post_delete_absence", ".pdh3-runtime/preflight-r7/attempt-06-post-delete-get.txt"),
    ((6,), "active_inventory", ".pdh3-runtime/preflight-r7/attempt-06-active-after-delete.json"),
    ((6,), "lifecycle_log", ".pdh3-runtime/preflight-r7/attempt-06-lifecycle-guard.ndjson"),
    ((7,), "running_receipt", "PDH_3_SCALE_CAMPAIGN_RUNNING_RECEIPT_R1.md"),
    ((7,), "create_response", ".pdh3-runtime/preflight-r7/attempt-07-create-response.json"),
    ((7,), "readiness", ".pdh3-runtime/preflight-r7/attempt-07-readiness.txt"),
    ((7,), "controller_canary", ".pdh3-runtime/preflight-r7/attempt-07-controller-canary.txt"),
    ((7,), "production_start", ".pdh3-runtime/preflight-r7/attempt-07-production-start.txt"),
    ((7,), "early_health", ".pdh3-runtime/preflight-r7/attempt-07-early-health.txt"),
    ((7,), "lifecycle_log", ".pdh3-runtime/preflight-r7/attempt-07-lifecycle-guard.ndjson"),
    ((7,), "supervisor_log", ".pdh3-runtime/preflight-r7/attempt-07-supervisor.ndjson"),
    ((7,), "final_state", ".pdh3-runtime/preflight-r7/attempt-07-final-retrieval/final-state.json"),
    ((7,), "final_evidence_archive", ".pdh3-runtime/preflight-r7/attempt-07-final-retrieval/final-evidence.tgz"),
    ((7,), "final_evidence_sidecar", ".pdh3-runtime/preflight-r7/attempt-07-final-retrieval/final-evidence.tgz.sha256"),
)

SMOKE_TESTS = (
    "post-dogfood/test_pdh3_scale_contract.py",
    "post-dogfood/test_pdh3_scale_campaign.py",
    "post-dogfood/test_pdh3_local_canary.py",
    "post-dogfood/test_run_pdh3_traced.py",
    "post-dogfood/test_pdh3_r12_plan_ab.py",
    "post-dogfood/test_pdh3_r12_network_observer.py",
    "post-dogfood/test_pdh3_r12_checkpoint.py",
    "post-dogfood/test_pdh3_r12_cpu_affinity.py",
    "post-dogfood/test_pdh3_r12_remote_capability.py",
    "post-dogfood/test_pdh3_r12_remote_launcher.py",
    "post-dogfood/test_pdh3_r12_remote_preflight.py",
    "hardening-gate7/test_gate7.py",
    "p4-verifier/test_verifier.py",
)

SMOKE_DIAGNOSTIC_TAIL_BYTES = 4096


class BundleError(RuntimeError):
    """Fail-closed bundle construction or verification error."""


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def bounded_diagnostic_tail(raw: bytes | str | None) -> str:
    """Return a deterministic, bounded UTF-8 tail for synthetic smoke output."""
    if raw is None:
        return ""
    encoded = raw.encode("utf-8", "replace") if isinstance(raw, str) else raw
    return encoded[-SMOKE_DIAGNOSTIC_TAIL_BYTES:].decode("utf-8", "replace")


def smoke_command_evidence(
    *,
    path: str,
    completed: subprocess.CompletedProcess[bytes] | None = None,
    timeout: subprocess.TimeoutExpired | None = None,
) -> dict[str, Any]:
    """Normalize one smoke command without losing bounded failure diagnostics."""
    if (completed is None) == (timeout is None):
        raise BundleError("SMOKE_COMMAND_RESULT_INVALID")

    def as_bytes(value: bytes | str | None) -> bytes:
        if value is None:
            return b""
        return value.encode("utf-8", "replace") if isinstance(value, str) else value
    if completed is not None:
        stdout = as_bytes(completed.stdout)
        stderr = as_bytes(completed.stderr)
        returncode: int | None = completed.returncode
        status = "PASS" if completed.returncode == 0 else "FAIL"
        timeout_seconds: int | None = None
    else:
        assert timeout is not None
        stdout = as_bytes(timeout.stdout)
        stderr = as_bytes(timeout.stderr)
        returncode = None
        status = "TIMEOUT"
        timeout_seconds = int(timeout.timeout) if timeout.timeout is not None else None
    return {
        "path": path,
        "status": status,
        "returncode": returncode,
        "timeout_seconds": timeout_seconds,
        "stdout_bytes": len(stdout),
        "stdout_sha256": digest(stdout),
        "stdout_tail": bounded_diagnostic_tail(stdout),
        "stderr_bytes": len(stderr),
        "stderr_sha256": digest(stderr),
        "stderr_tail": bounded_diagnostic_tail(stderr),
    }


def validate_relative(name: str) -> None:
    if not name or "\x00" in name or "\\" in name or name.startswith("/"):
        raise BundleError("BUNDLE_PATH_UNSAFE")
    path = PurePosixPath(name)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
        or str(path) != name
    ):
        raise BundleError("BUNDLE_PATH_UNSAFE")


def source_entry(relative: str) -> dict[str, Any]:
    validate_relative(relative)
    path = BASE / relative
    if not path.is_file() or path.is_symlink():
        raise BundleError("SOURCE_INVALID:" + relative)
    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": file_digest(path),
        "mode": 0o755 if os.access(path, os.X_OK) else 0o644,
    }


def load_contract() -> Any:
    path = BASE / "post-dogfood/pdh3_scale_contract.py"
    spec = importlib.util.spec_from_file_location("pdh3_bundle_contract", path)
    if spec is None or spec.loader is None:
        raise BundleError("CONTRACT_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def production_launch_contract() -> dict[str, Any]:
    """Bind the exact production arguments; store size is intentionally absent."""
    contract = load_contract()
    bindings = {
        "duration_seconds": contract.MEASURED_SECONDS,
        "checkpoint_seconds": contract.CHECKPOINT_SECONDS,
        "tasks": contract.TASKS,
        "events_per_task": contract.EVENTS_PER_TASK,
        "receipts_per_task": contract.RECEIPTS_PER_TASK,
        "vectors": contract.VECTORS,
        "max_concurrency": contract.MAX_CONCURRENCY,
        "query_duration_seconds": contract.QUERY_DURATION_SECONDS,
        "seed_batch_tasks": contract.SEED_BATCH_TASKS,
        "setup_timeout_seconds": contract.SETUP_TIMEOUT_SECONDS,
        "setup_success_margin_seconds": contract.SETUP_SUCCESS_MARGIN_SECONDS,
        "fault_every_checkpoints": contract.FAULT_EVERY_CHECKPOINTS,
        "disk_used_fraction_limit": contract.DISK_USED_FRACTION_LIMIT,
        "cache": contract.NODE_CACHE,
        "sql_memory": contract.NODE_SQL_MEMORY,
        "store_size": None,
    }
    contract.validate_production_arguments(bindings)
    binary = (
        "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
        "cockroach-v26.2.3.linux-amd64/cockroach"
    )
    strace_deb = (
        "p2-cleanroom/vendor/ubuntu-noble-strace/"
        "strace_6.8-0ubuntu2_amd64.deb"
    )
    libunwind_deb = (
        "p2-cleanroom/vendor/ubuntu-noble-strace/"
        "libunwind8_1.6.2-3build1_amd64.deb"
    )
    tracer_root = "__TRACER_ROOT__"
    tracer_binary = tracer_root + "/usr/bin/strace"
    tracer_library_path = (
        tracer_root + "/usr/lib/x86_64-linux-gnu:"
        + tracer_root
        + "/lib/x86_64-linux-gnu"
    )
    tracer_setup = [
        ["dpkg-deb", "--extract", libunwind_deb, tracer_root],
        ["dpkg-deb", "--extract", strace_deb, tracer_root],
    ]
    launch_environment = {
        "PDH3_PACKET_SHA256": "__FROZEN_PACKET_SHA256__",
        "LD_LIBRARY_PATH": tracer_library_path,
    }
    controller = [
        "python3",
        "post-dogfood/run_pdh3_scale_campaign.py",
        "--binary",
        binary,
        "--packet",
        "__FROZEN_PACKET__",
        "--output",
        "__REMOTE_EVIDENCE_ROOT__",
        "--campaign-id",
        "__IMMUTABLE_CAMPAIGN_ID__",
        "--production",
        "--duration-seconds",
        str(bindings["duration_seconds"]),
        "--checkpoint-seconds",
        str(bindings["checkpoint_seconds"]),
        "--tasks",
        str(bindings["tasks"]),
        "--events-per-task",
        str(bindings["events_per_task"]),
        "--receipts-per-task",
        str(bindings["receipts_per_task"]),
        "--vectors",
        str(bindings["vectors"]),
        "--max-concurrency",
        str(bindings["max_concurrency"]),
        "--query-duration-seconds",
        str(bindings["query_duration_seconds"]),
        "--seed-batch-tasks",
        str(bindings["seed_batch_tasks"]),
        "--setup-timeout-seconds",
        str(bindings["setup_timeout_seconds"]),
        "--fault-every-checkpoints",
        str(bindings["fault_every_checkpoints"]),
        "--disk-used-fraction-limit",
        str(bindings["disk_used_fraction_limit"]),
        "--cache",
        str(bindings["cache"]),
        "--sql-memory",
        str(bindings["sql_memory"]),
    ]
    if "--store-size" in controller:
        raise BundleError("PRODUCTION_STORE_SIZE_MUST_BE_ABSENT")
    traced = [
        "python3",
        "post-dogfood/pdh3_r12_network_observer.py",
        "run",
        "--output-dir",
        "__REMOTE_NETWORK_PROOF_ROOT__",
        "--packet-sha256",
        "__FROZEN_PACKET_SHA256__",
        "--tracer",
        tracer_binary,
        "--tracer-sha256",
        contract.STRACE_BINARY_SHA256,
        "--max-evidence-bytes",
        str(min(1024**3, contract.TRACE_BYTES_LIMIT // 2)),
        "--",
        *controller,
    ]
    body = {
        "version": "ck-pdh3-production-launch-binding-v3",
        "argument_bindings": bindings,
        "launch_environment_template": launch_environment,
        "tracer_artifact_bindings": [
            {"path": strace_deb, "sha256": contract.STRACE_DEB_SHA256},
            {"path": libunwind_deb, "sha256": contract.LIBUNWIND8_DEB_SHA256},
        ],
        "tracer_setup_argv_templates": tracer_setup,
        "tracer_binary_template": tracer_binary,
        "tracer_binary_sha256": contract.STRACE_BINARY_SHA256,
        "tracer_library_path_template": tracer_library_path,
        "controller_argv_template": controller,
        "controller_argv_template_sha256": digest(canonical(controller)),
        "traced_argv_template": traced,
        "traced_argv_template_sha256": digest(canonical(traced)),
        "launch_environment_template_sha256": digest(
            canonical(launch_environment)
        ),
        "tracer_setup_template_sha256": digest(canonical(tracer_setup)),
        "required_remote_setup_order": [
            "VERIFY_BUNDLED_DEB_HASHES",
            "EXTRACT_LIBUNWIND_WITH_DPKG_DEB",
            "EXTRACT_STRACE_WITH_DPKG_DEB",
            "VERIFY_EXTRACTED_STRACE_BINARY_HASH",
            "SET_EXACT_LAUNCH_ENVIRONMENT",
            "EXECUTE_STREAMING_NETWORK_PROOF_ARGV_WITHOUT_SHELL",
        ],
        "store_size_flag": "ABSENT",
        "shell_interpolation": False,
    }
    return {**body, "launch_sha256": digest(canonical(body))}


def host_only_bindings() -> dict[str, Any]:
    rows = [source_entry(relative) for relative in HOST_ONLY_FILES]
    body = {
        "version": "ck-pdh3-host-control-plane-bindings-v1",
        "archive_transfer": False,
        "reason": "HOST_CONTROL_PLANE_NOT_REQUIRED_BY_REMOTE_WORKLOAD",
        "files": rows,
        "file_count": len(rows),
        "source_set_sha256": digest(canonical(rows)),
    }
    return {**body, "bindings_sha256": digest(canonical(body))}


def history_manifest() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    covered: set[int] = set()
    for attempts, classification, relative in HISTORY_EVIDENCE:
        validate_relative(relative)
        if relative in seen:
            raise BundleError("HISTORY_PATH_DUPLICATE:" + relative)
        seen.add(relative)
        path = BASE / relative
        if not path.is_file() or path.is_symlink():
            raise BundleError("HISTORY_EVIDENCE_MISSING:" + relative)
        covered.update(attempts)
        rows.append(
            {
                "attempts": list(attempts),
                "classification": classification,
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": file_digest(path),
            }
        )
    rows.sort(key=lambda row: (row["attempts"], row["classification"], row["path"]))
    if covered != set(range(1, 8)):
        raise BundleError("HISTORY_ATTEMPT_COVERAGE_INVALID")
    lookup = {row["path"]: row for row in rows}
    final_state = lookup[
        ".pdh3-runtime/preflight-r7/attempt-07-final-retrieval/final-state.json"
    ]
    final_archive = lookup[
        ".pdh3-runtime/preflight-r7/attempt-07-final-retrieval/final-evidence.tgz"
    ]
    body = {
        "version": "ck-pdh3-attempt-history-manifest-v1",
        "attempts_covered": sorted(covered),
        "binding_only": True,
        "raw_evidence_embedded": False,
        "credential_material_copied": False,
        "entries": rows,
        "entry_count": len(rows),
        "history_set_sha256": digest(canonical(rows)),
        "attempt_07_final_state_sha256": final_state["sha256"],
        "attempt_07_final_evidence_archive_sha256": final_archive["sha256"],
    }
    return {**body, "history_manifest_sha256": digest(canonical(body))}


def validate_tar_members(
    members: Iterable[tarfile.TarInfo], expected_names: set[str]
) -> list[tarfile.TarInfo]:
    rows = list(members)
    names: list[str] = []
    for member in rows:
        validate_relative(member.name)
        if not member.isfile():
            raise BundleError("BUNDLE_MEMBER_TYPE_INVALID:" + member.name)
        names.append(member.name)
    if len(names) != len(set(names)):
        raise BundleError("BUNDLE_MEMBER_DUPLICATE")
    actual = set(names)
    if actual != expected_names:
        missing = sorted(expected_names - actual)
        extra = sorted(actual - expected_names)
        raise BundleError(
            "BUNDLE_MEMBER_SET_MISMATCH:"
            + digest(canonical({"missing": missing, "extra": extra}))
        )
    return rows


def validate_embedded_record(record: dict[str, Any], hash_field: str) -> None:
    if not isinstance(record, dict) or hash_field not in record:
        raise BundleError("EMBEDDED_RECORD_SCHEMA_INVALID")
    body = {key: value for key, value in record.items() if key != hash_field}
    if record[hash_field] != digest(canonical(body)):
        raise BundleError("EMBEDDED_RECORD_HASH_MISMATCH")


def verify_local_bindings_current(
    rows: Iterable[dict[str, Any]], *, classification: str
) -> None:
    """Detect host/history drift between initial hashing and receipt freeze."""
    for row in rows:
        relative = row.get("path")
        if not isinstance(relative, str):
            raise BundleError(classification + "_BINDING_SCHEMA_INVALID")
        validate_relative(relative)
        path = BASE / relative
        if (
            not path.is_file()
            or path.is_symlink()
            or path.stat().st_size != row.get("bytes")
            or file_digest(path) != row.get("sha256")
        ):
            raise BundleError(classification + "_BINDING_DRIFT:" + relative)


def verify_and_extract(
    archive_path: Path,
    destination: Path,
    manifest: dict[str, Any],
    history: dict[str, Any],
) -> dict[str, Any]:
    """Safely extract an exact archive and compare each source to current bytes."""
    if destination.exists():
        raise BundleError("EXTRACTION_ROOT_EXISTS")
    validate_embedded_record(manifest, "manifest_sha256")
    validate_embedded_record(history, "history_manifest_sha256")
    source_rows = manifest.get("files")
    if not isinstance(source_rows, list):
        raise BundleError("MANIFEST_FILES_INVALID")
    source_by_path: dict[str, dict[str, Any]] = {}
    for row in source_rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256", "mode"}:
            raise BundleError("MANIFEST_FILE_SCHEMA_INVALID")
        name = row["path"]
        validate_relative(name)
        if name in source_by_path:
            raise BundleError("MANIFEST_FILE_DUPLICATE")
        source_by_path[name] = row
    expected_raw = {
        MANIFEST_MEMBER: canonical(manifest),
        HISTORY_MEMBER: canonical(history),
    }
    expected_names = set(source_by_path) | set(expected_raw)
    destination.mkdir(parents=True)
    verified: list[dict[str, Any]] = []
    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            members = validate_tar_members(archive.getmembers(), expected_names)
            for member in members:
                expected_size = (
                    source_by_path[member.name]["bytes"]
                    if member.name in source_by_path
                    else len(expected_raw[member.name])
                )
                if member.size != expected_size:
                    raise BundleError("BUNDLE_MEMBER_SIZE_MISMATCH:" + member.name)
                if (
                    member.mtime != 0
                    or member.uid != 0
                    or member.gid != 0
                    or member.uname != ""
                    or member.gname != ""
                    or member.pax_headers
                ):
                    raise BundleError("BUNDLE_MEMBER_METADATA_INVALID:" + member.name)
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise BundleError("BUNDLE_MEMBER_UNREADABLE:" + member.name)
                target = destination.joinpath(*PurePosixPath(member.name).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                hasher = hashlib.sha256()
                size = 0
                with target.open("xb") as handle:
                    for block in iter(lambda: extracted.read(1 << 20), b""):
                        handle.write(block)
                        hasher.update(block)
                        size += len(block)
                    handle.flush()
                    os.fsync(handle.fileno())
                observed_hash = hasher.hexdigest()
                if member.name in source_by_path:
                    expected = source_by_path[member.name]
                    if size != expected["bytes"] or observed_hash != expected["sha256"]:
                        raise BundleError("BUNDLE_SOURCE_HASH_MISMATCH:" + member.name)
                    if member.mode & 0o777 != expected["mode"]:
                        raise BundleError("BUNDLE_SOURCE_MODE_MISMATCH:" + member.name)
                    current = BASE / member.name
                    if (
                        not current.is_file()
                        or current.is_symlink()
                        or file_digest(current) != observed_hash
                    ):
                        raise BundleError("CURRENT_SOURCE_MISMATCH:" + member.name)
                    os.chmod(target, expected["mode"])
                else:
                    raw = expected_raw[member.name]
                    if size != len(raw) or observed_hash != digest(raw):
                        raise BundleError("BUNDLE_METADATA_HASH_MISMATCH:" + member.name)
                    os.chmod(target, 0o644)
                verified.append(
                    {"path": member.name, "bytes": size, "sha256": observed_hash}
                )
        body = {
            "version": "ck-pdh3-extracted-bundle-verification-v2",
            "exact_member_set": True,
            "regular_files_only": True,
            "source_bytes_match_current": True,
            "source_count": len(source_by_path),
            "member_count": len(verified),
            "verified_members_sha256": digest(canonical(verified)),
        }
        return {**body, "verification_sha256": digest(canonical(body))}
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def write_new(path: Path, raw: bytes, mode: int = 0o600) -> None:
    if path.exists():
        raise BundleError("OUTPUT_EXISTS")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + ".part")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
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


def build(output: Path, manifest_path: Path) -> dict[str, Any]:
    if output.resolve() == manifest_path.resolve():
        raise BundleError("OUTPUT_PATH_COLLISION")
    if output.exists() or manifest_path.exists():
        raise BundleError("OUTPUT_EXISTS")
    if len(REMOTE_FILES) != len(set(REMOTE_FILES)):
        raise BundleError("REMOTE_FILE_DUPLICATE")
    if set(REMOTE_FILES) & set(HOST_ONLY_FILES):
        raise BundleError("HOST_REMOTE_BOUNDARY_OVERLAP")
    entries = [source_entry(relative) for relative in REMOTE_FILES]
    history = history_manifest()
    host_bindings = host_only_bindings()
    launch = production_launch_contract()
    manifest_body = {
        "version": "ck-pdh3-scale-bundle-manifest-v2",
        "credential_free": True,
        "synthetic_only": True,
        "files": entries,
        "file_count": len(entries),
        "source_set_sha256": digest(canonical(entries)),
        "history_member": HISTORY_MEMBER,
        "history_manifest_sha256": history["history_manifest_sha256"],
        "history_raw_evidence_embedded": False,
        "host_control_plane_transferred": False,
        "host_only_bindings_sha256": host_bindings["bindings_sha256"],
        "production_launch": launch,
    }
    manifest = {
        **manifest_body,
        "manifest_sha256": digest(canonical(manifest_body)),
    }
    manifest_raw = canonical(manifest)
    history_raw = canonical(history)
    stream = io.BytesIO()
    with gzip.GzipFile(fileobj=stream, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w") as archive:
            for row in entries:
                raw = (BASE / row["path"]).read_bytes()
                info = tarfile.TarInfo(row["path"])
                info.size = len(raw)
                info.mode = row["mode"]
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                archive.addfile(info, io.BytesIO(raw))
            for name, raw in (
                (MANIFEST_MEMBER, manifest_raw),
                (HISTORY_MEMBER, history_raw),
            ):
                info = tarfile.TarInfo(name)
                info.size = len(raw)
                info.mode = 0o644
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                archive.addfile(info, io.BytesIO(raw))
    archive_raw = stream.getvalue()
    write_new(output, archive_raw)
    try:
        with tempfile.TemporaryDirectory(prefix="pdh3-bundle-verify.") as temporary:
            extraction = Path(temporary) / "extracted"
            verification = verify_and_extract(output, extraction, manifest, history)
        verify_local_bindings_current(
            host_bindings["files"], classification="HOST_ONLY"
        )
        verify_local_bindings_current(
            history["entries"], classification="HISTORY"
        )
    except Exception:
        output.unlink(missing_ok=True)
        raise
    receipt_body = {
        "version": "ck-pdh3-scale-bundle-receipt-v2",
        "archive": output.name,
        "archive_bytes": len(archive_raw),
        "archive_sha256": digest(archive_raw),
        "manifest": manifest,
        "history_manifest": history,
        "host_only_bindings": host_bindings,
        "archive_verification": verification,
    }
    receipt = {
        **receipt_body,
        "receipt_sha256": digest(canonical(receipt_body)),
    }
    write_new(manifest_path, canonical(receipt))
    return receipt


def run_extracted_bundle_smoke(
    archive: Path,
    receipt: dict[str, Any],
    extraction_root: Path,
    smoke_receipt_path: Path,
) -> dict[str, Any]:
    """Compile/import and run reduced tests; never claim target-scale proof."""
    if smoke_receipt_path.exists():
        raise BundleError("OUTPUT_EXISTS")
    if file_digest(archive) != receipt.get("archive_sha256"):
        raise BundleError("ARCHIVE_RECEIPT_HASH_MISMATCH")
    manifest = receipt.get("manifest")
    history = receipt.get("history_manifest")
    if not isinstance(manifest, dict) or not isinstance(history, dict):
        raise BundleError("RECEIPT_METADATA_INVALID")
    verification = verify_and_extract(archive, extraction_root, manifest, history)
    python_files = [
        extraction_root / row["path"]
        for row in manifest["files"]
        if row["path"].endswith(".py")
    ]
    environment = {
        "HOME": str(extraction_root / ".smoke-home"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": os.pathsep.join(
            str(extraction_root / relative)
            for relative in (
                "post-dogfood",
                "hardening-gate7",
                "hardening-gate5",
                "p4-verifier",
                "p9-cloud",
                "p7-recovery",
            )
        ),
        "TMPDIR": str(extraction_root / ".smoke-tmp"),
        "TZ": "UTC",
    }
    Path(environment["HOME"]).mkdir()
    Path(environment["TMPDIR"]).mkdir()
    compile_result: subprocess.CompletedProcess[bytes] | None = None
    compile_timeout: subprocess.TimeoutExpired | None = None
    try:
        compile_result = subprocess.run(
            [sys.executable, "-m", "py_compile", *(str(path) for path in python_files)],
            cwd=extraction_root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        compile_timeout = exc
    compile_evidence = smoke_command_evidence(
        path="PY_COMPILE",
        completed=compile_result,
        timeout=compile_timeout,
    )
    executions: list[dict[str, Any]] = []
    if compile_evidence["status"] == "PASS":
        for relative in SMOKE_TESTS:
            if relative not in REMOTE_FILES:
                raise BundleError("SMOKE_TEST_NOT_BUNDLED:" + relative)
            completed = None
            timed_out = None
            try:
                completed = subprocess.run(
                    [sys.executable, relative],
                    cwd=extraction_root,
                    env=environment,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=300,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                timed_out = exc
            executions.append(
                smoke_command_evidence(
                    path=relative,
                    completed=completed,
                    timeout=timed_out,
                )
            )
    green = (
        compile_evidence["status"] == "PASS"
        and len(executions) == len(SMOKE_TESTS)
        and all(row["status"] == "PASS" for row in executions)
    )
    failed_checks = (
        [compile_evidence["path"]]
        if compile_evidence["status"] != "PASS"
        else []
    )
    failed_checks.extend(row["path"] for row in executions if row["status"] != "PASS")
    body = {
        "version": "ck-pdh3-extracted-bundle-smoke-v3",
        "evidence_class": "EXTRACTED_BUNDLE_INTEGRITY_SMOKE_ONLY",
        "archive_sha256": receipt["archive_sha256"],
        "archive_verification_sha256": verification["verification_sha256"],
        "compile": {**compile_evidence, "python_files": len(python_files)},
        "tests": executions,
        "failed_checks": failed_checks,
        "diagnostic_tail_bytes_max": SMOKE_DIAGNOSTIC_TAIL_BYTES,
        "target_scale_proof": False,
        "production_claim_allowed": False,
        "limitations": [
            "NO_FULL_CARDINALITY_SETUP",
            "NO_24_HOUR_MEASUREMENT",
            "NO_500_CONCURRENCY_REMOTE_WORKLOAD",
            "NO_RUNPOD_HARDWARE_PROOF",
            "NO_REMOTE_NETWORK_OBSERVATION",
        ],
        "green": green,
    }
    smoke = {**body, "smoke_sha256": digest(canonical(body))}
    write_new(smoke_receipt_path, canonical(smoke))
    if not green:
        raise BundleError("EXTRACTED_BUNDLE_SMOKE_BLOCKED")
    return smoke


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--smoke-root", type=Path)
    parser.add_argument("--smoke-receipt", type=Path)
    parser.add_argument("--verify-archive", type=Path)
    parser.add_argument("--verify-receipt", type=Path)
    parser.add_argument("--verify-root", type=Path)
    parser.add_argument("--verify-smoke-receipt", type=Path)
    arguments = parser.parse_args()
    verify_values = (
        arguments.verify_archive,
        arguments.verify_receipt,
        arguments.verify_root,
        arguments.verify_smoke_receipt,
    )
    if any(value is not None for value in verify_values):
        if not all(value is not None for value in verify_values):
            parser.error("all four --verify-* arguments are required")
        if any(value is not None for value in
               (arguments.output, arguments.receipt, arguments.smoke_root,
                arguments.smoke_receipt)):
            parser.error("build and verify modes are mutually exclusive")
        receipt = json.loads(arguments.verify_receipt.resolve().read_bytes())
        smoke = run_extracted_bundle_smoke(
            arguments.verify_archive.resolve(),
            receipt,
            arguments.verify_root.resolve(),
            arguments.verify_smoke_receipt.resolve(),
        )
        print(canonical({"extracted_bundle_smoke": smoke}).decode())
        return 0
    if arguments.output is None or arguments.receipt is None:
        parser.error("--output and --receipt are required in build mode")
    if (arguments.smoke_root is None) != (arguments.smoke_receipt is None):
        parser.error("--smoke-root and --smoke-receipt must be supplied together")
    receipt = build(arguments.output.resolve(), arguments.receipt.resolve())
    response: dict[str, Any] = {"bundle": receipt}
    if arguments.smoke_root is not None and arguments.smoke_receipt is not None:
        response["extracted_bundle_smoke"] = run_extracted_bundle_smoke(
            arguments.output.resolve(),
            receipt,
            arguments.smoke_root.resolve(),
            arguments.smoke_receipt.resolve(),
        )
    print(canonical(response).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
