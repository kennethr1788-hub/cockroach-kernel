#!/usr/bin/env python3
"""Build the append-only PDH-3 R8 relaunch preflight packet.

The builder is intentionally input-driven.  It does not know a launch date,
provider inventory, artifact hash, or RunPodCTL binary in advance.  Those facts
must be supplied as fresh, hash-verifiable inputs.  R7 files are never read as
authority and output files are created exclusively (never overwritten).

Local-test and prior-attempt manifests use canonical JSON and a top-level
``manifest_sha256`` computed over the document with that field removed.  File
bindings may be expressed either as ``{"path": ..., "sha256": ..., "bytes":
...}`` dictionaries or as a ``files`` mapping of relative path to SHA-256.
Every referenced file is rehashed before the packet is emitted.

The judge surface is deliberately compact.  It carries canonical full-file
hashes plus top-level symbol-range hashes instead of embedding entire source
bodies.  That keeps one identical packet inside the strictest judge transport
limit without weakening the archive, source-set, or executable bindings.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterable, Mapping


REVISION = "R8"
PACKET_VERSION = "ck-pdh3-scale-preflight-packet-r8-v3"
BINDINGS_VERSION = "ck-pdh3-scale-preflight-bindings-r8-v3"
PACKET_BYTES_MAX = 262_144
PREFLIGHT_EPOCH_SECONDS = 300
SETUP_CLOSEOUT_RESERVE_SECONDS = 900
FINAL_DELETE_RESERVE_SECONDS = 900
PROVIDER_RECEIPT_MAX_AGE_SECONDS = 900
PROVIDER_RECEIPT_FUTURE_SKEW_SECONDS = 5
RUNPOD_PRICING_URL = "https://www.runpod.io/pricing"

REMOTE_LOAD_BEARING_TEXT_SOURCES = (
    "post-dogfood/pdh3_scale_contract.py",
    "post-dogfood/run_pdh3_scale_campaign.py",
    "post-dogfood/run_pdh3_traced.py",
    "post-dogfood/run_pdh3_local_canary.py",
    "post-dogfood/pdh3_synthetic_dataset.py",
    "post-dogfood/build_pdh3_scale_bundle.py",
    "post-dogfood/test_build_pdh3_scale_bundle.py",
    "post-dogfood/test_pdh3_local_canary.py",
    "post-dogfood/test_pdh3_scale_campaign.py",
    "post-dogfood/test_pdh3_scale_contract.py",
    "post-dogfood/test_run_pdh3_traced.py",
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
)

PACKET_ONLY_SOURCES = (
    "PDH_3_R8_VALIDATION_BOUNDARY_DISCLOSURE.md",
    "post-dogfood/supervise_pdh3_scale_campaign.py",
    "post-dogfood/test_supervise_pdh3_scale_campaign.py",
    "s2-soak/lifecycle_guard.py",
    "s2-soak/test_lifecycle_guard.py",
    "post-dogfood/build_pdh3_scale_preflight_packet_r8.py",
    "post-dogfood/test_build_pdh3_scale_preflight_packet_r8.py",
)

MANDATORY_SOURCES = tuple(
    sorted(set(REMOTE_LOAD_BEARING_TEXT_SOURCES + PACKET_ONLY_SOURCES))
)

REMOTE_BUNDLE_REQUIRED = REMOTE_LOAD_BEARING_TEXT_SOURCES

TERMINAL_STATES = (
    "GREEN_PENDING_FINAL_GATE",
    "BLOCKED_COMPLETE",
    "ABSENT_RESULT",
    "PARTIAL_ARCHIVE",
    "TRANSPORT_FAILURE",
    "TEARDOWN_UNPROVEN",
)

RELAUNCH_CHECKLIST = (
    "Fresh R8 packet and bundle bind the exact repaired bytes; no R7 packet, "
    "expired timestamp, or stale hash is reused.",
    "Uncertain SQL outcomes resolve only to ZERO, EXACT, or MISMATCH; explicit "
    "primary-key conflict targets never conceal mismatched rows.",
    "One monotonic 5,400-second setup deadline includes a protected teardown "
    "tail; setup cannot become GREEN after deadline exhaustion.",
    "Vector-index drop, recreation, row cardinality, metadata, and forced-index "
    "queryability are directly evidenced; asynchronous builds additionally "
    "require exact succeeded-job ownership, while synchronous DDL records the "
    "explicit no-job completion mode.",
    "Full 500,000-task / 5,000,000-event / 1,000,000-receipt / 250,000-vector "
    "setup completes on the selected worker shape with recorded margin.",
    "Production query targets are proven to address real, nonzero seeded rows.",
    "Every measured epoch shares one 300-second monotonic deadline; no child "
    "operation receives a fresh epoch-sized timeout.",
    "Exactly 24 genuine SIGKILL/restart/reconciliation cycles preserve "
    "cumulative acknowledgements, counters, replay state, and three live nodes.",
    "Exactly 9,976 distinct verifier receipts plus manifests and batch evidence "
    "remain retrievable; hashes of deleted temporary files do not count.",
    "Database, evidence, disk, total RSS, per-node descriptors, process count, "
    "and all-three-node liveness are measured against contract thresholds.",
    "The O(new-data) syscall observer emits atomic progress receipts and blocks "
    "when the projected 24-hour trace exceeds 80 percent of the 2-GiB cap.",
    "The supervisor distinguishes all six terminal states and cannot interpret "
    "retrieval, a partial archive, or transport loss as campaign success.",
    "The exact-ID lifecycle guard uses bounded provider calls and proves stop, "
    "delete, exact-ID absence, and empty matching active inventory.",
    "Partial cluster startup is torn down and cannot vacuously report GREEN.",
    "Authoritative result.json and the GREEN marker are emitted only after "
    "database and local teardown; result and failure are mutually exclusive.",
    "Production store-size substitution is rejected.",
    "Reduced local tests are fault detectors only, never production-scale proof.",
)

# Each gate is bound to real implementation/test symbols.  The builder checks
# those names against the AST-derived source manifest before emitting a packet.
# Remote observations and process gates stay explicitly open.
CHECKLIST_EVIDENCE = (
    ("R8-01", "LOCAL_BOUND", (("post-dogfood/build_pdh3_scale_bundle.py", "build"), ("post-dogfood/build_pdh3_scale_preflight_packet_r8.py", "build")), (("post-dogfood/test_build_pdh3_scale_bundle.py", "test_deterministic_archive_and_exact_extracted_source_hashes"), ("post-dogfood/test_build_pdh3_scale_preflight_packet_r8.py", "test_successful_build_is_canonical_and_transport_safe")), ("bundle.archive_sha256", "source_set_sha256")),
    ("R8-02", "LOCAL_BOUND", (("post-dogfood/build_pdh3_scale_bundle.py", "history_manifest"),), (("post-dogfood/test_build_pdh3_scale_bundle.py", "test_history_manifest_binds_all_seven_attempts_without_raw_evidence"),), ("prior_attempt_history_manifest",)),
    ("R8-03", "LOCAL_BOUND", (("post-dogfood/pdh3_scale_contract.py", "validate_production_arguments"), ("post-dogfood/build_pdh3_scale_bundle.py", "production_launch_contract")), (("post-dogfood/test_pdh3_scale_campaign.py", "test_production_rejects_local_store_size_before_io"), ("post-dogfood/test_build_pdh3_scale_bundle.py", "test_production_launch_binds_contract_and_omits_store_size_flag")), ("commands.child_controller_argv",)),
    ("R8-04", "LOCAL_BOUND", (("post-dogfood/run_pdh3_scale_campaign.py", "sql"), ("post-dogfood/run_pdh3_scale_campaign.py", "reconcile_seed_batch")), (("post-dogfood/test_pdh3_scale_campaign.py", "test_timeout_after_commit_reconciles_exact_without_reinsert"), ("post-dogfood/test_pdh3_scale_campaign.py", "test_timeout_reconciliation_mismatch_fails_closed"), ("post-dogfood/test_pdh3_scale_campaign.py", "test_sqlstate_40001_is_retried_once")), ("local_test_manifest.tests",)),
    ("R8-05", "LOCAL_BOUND", (("post-dogfood/run_pdh3_scale_campaign.py", "seed_reconciliation_statement"), ("post-dogfood/run_pdh3_scale_campaign.py", "campaign_reconciliations")), (("post-dogfood/test_pdh3_scale_campaign.py", "test_reconciliation_detects_missing_and_corrupt_rows"),), ("local_test_manifest.tests",)),
    ("R8-06", "LOCAL_BOUND", (("post-dogfood/run_pdh3_scale_campaign.py", "defer_vector_index"), ("post-dogfood/run_pdh3_scale_campaign.py", "restore_vector_index"), ("post-dogfood/run_pdh3_scale_campaign.py", "vector_index_proof")), (("post-dogfood/test_pdh3_scale_campaign.py", "test_vector_index_defer_and_restore_are_explicit"), ("post-dogfood/test_pdh3_scale_campaign.py", "test_vector_index_full_coverage_is_exact_and_forced"), ("post-dogfood/test_pdh3_scale_campaign.py", "test_preexisting_successful_job_cannot_prove_async_completion")), ("local_test_manifest.tests",)),
    ("R8-07", "LOCAL_BOUND", (("post-dogfood/run_pdh3_scale_campaign.py", "setup_timeout"), ("post-dogfood/run_pdh3_scale_campaign.py", "setup_margin_gate")), (("post-dogfood/test_pdh3_scale_campaign.py", "test_expired_reserved_deadline_starts_no_sql"), ("post-dogfood/test_pdh3_scale_campaign.py", "test_setup_margin_gate_is_quantitative_and_fail_closed")), ("contract.workload.setup_timeout_seconds",)),
    ("R8-08", "REMOTE_GATE", (("post-dogfood/run_pdh3_scale_campaign.py", "seed_dataset"), ("post-dogfood/run_pdh3_scale_campaign.py", "campaign_counts")), (("post-dogfood/test_pdh3_scale_campaign.py", "test_seed_statement_counts_and_bounds"),), ("future_remote_setup_receipt",)),
    ("R8-09", "LOCAL_BOUND", (("post-dogfood/run_pdh3_scale_campaign.py", "create_query_files"),), (("post-dogfood/test_pdh3_scale_campaign.py", "test_query_files_use_six_digit_seed_ids"),), ("local_test_manifest.tests",)),
    ("R8-10", "REMOTE_GATE", (("post-dogfood/run_pdh3_scale_campaign.py", "run_remote_preflight"), ("post-dogfood/run_pdh3_scale_campaign.py", "reset_preflight_controls")), (("post-dogfood/test_pdh3_scale_campaign.py", "test_remote_preflight_is_three_500_worker_epochs_three_rotating_faults"), ("post-dogfood/test_pdh3_scale_campaign.py", "test_preflight_control_reset_is_atomic_and_exact")), ("future_remote_premeasurement_receipt",)),
    ("R8-11", "LOCAL_BOUND", (("post-dogfood/run_pdh3_scale_campaign.py", "run_campaign_epoch"), ("post-dogfood/run_pdh3_scale_campaign.py", "deadline_timeout")), (("post-dogfood/test_pdh3_scale_campaign.py", "test_epoch_snapshot_uses_shared_deadline_and_hits_boundary"), ("post-dogfood/test_pdh3_scale_campaign.py", "test_deadline_timeout_preserves_epoch_reserve")), ("contract.workload.checkpoint_seconds",)),
    ("R8-12", "LOCAL_BOUND", (("post-dogfood/pdh3_scale_contract.py", "expected_schedule"), ("post-dogfood/run_pdh3_scale_campaign.py", "production_schedule")), (("post-dogfood/test_pdh3_scale_campaign.py", "test_production_schedule_is_exact"),), ("schedule",)),
    ("R8-13", "LOCAL_BOUND", (("post-dogfood/run_pdh3_scale_campaign.py", "fault_cycle"),), (("post-dogfood/test_pdh3_scale_campaign.py", "test_fault_cycle_proves_sigkill_fresh_pid_and_control_durability"),), ("schedule.fault_count",)),
    ("R8-14", "LOCAL_BOUND", (("post-dogfood/run_pdh3_scale_campaign.py", "validate_verifier_evidence"), ("post-dogfood/supervise_pdh3_scale_campaign.py", "validate_verifier_summary")), (("post-dogfood/test_pdh3_scale_campaign.py", "test_reconstructs_exactly_9976_unique_verifier_receipts"), ("post-dogfood/test_supervise_pdh3_scale_campaign.py", "test_minimal_checkpoint_and_verifier_evidence_are_rejected")), ("schedule.verifier_executions", "future_remote_evidence_archive")),
    ("R8-15", "LOCAL_BOUND", (("post-dogfood/run_pdh3_scale_campaign.py", "process_metrics"), ("post-dogfood/run_pdh3_scale_campaign.py", "enforce_resource_thresholds")), (("post-dogfood/test_pdh3_scale_campaign.py", "test_production_resource_gate_requires_three_measured_nodes"), ("post-dogfood/test_pdh3_scale_campaign.py", "test_linux_process_tree_snapshot_is_complete_and_binds_nodes")), ("contract.thresholds",)),
    ("R8-16", "LOCAL_BOUND", (("post-dogfood/run_pdh3_traced.py", "scan_incremental"), ("post-dogfood/run_pdh3_traced.py", "observe_process")), (("post-dogfood/test_run_pdh3_traced.py", "test_ten_thousand_process_equivalent_has_constant_empty_poll_io"), ("post-dogfood/test_run_pdh3_traced.py", "test_progress_receipt_is_atomic_non_authoritative_and_projected"), ("post-dogfood/test_run_pdh3_traced.py", "test_blocks_external_addresses")), ("contract.thresholds.trace_bytes",)),
    ("R8-17", "LOCAL_BOUND", (("post-dogfood/run_pdh3_scale_campaign.py", "start_cluster"),), (("post-dogfood/test_pdh3_scale_campaign.py", "test_partial_cluster_start_failure_stops_started_nodes"),), ("local_test_manifest.tests",)),
    ("R8-18", "LOCAL_BOUND", (("post-dogfood/run_pdh3_scale_campaign.py", "close_local_campaign"), ("post-dogfood/run_pdh3_scale_campaign.py", "commit_success_evidence")), (("post-dogfood/test_pdh3_scale_campaign.py", "test_terminal_green_requires_hash_valid_green_teardown_and_no_failure"), ("post-dogfood/test_supervise_pdh3_scale_campaign.py", "test_actual_writer_order_manifest_result_marker_is_valid")), ("terminal_states",)),
    ("R8-19", "LOCAL_BOUND", (("post-dogfood/supervise_pdh3_scale_campaign.py", "supervise"), ("post-dogfood/supervise_pdh3_scale_campaign.py", "validate_archive")), (("post-dogfood/test_supervise_pdh3_scale_campaign.py", "test_mocked_supervise_state_matrix_and_exit_codes"), ("post-dogfood/test_supervise_pdh3_scale_campaign.py", "test_retrieve_file_is_atomic")), ("terminal_states",)),
    ("R8-20", "LOCAL_BOUND", (("s2-soak/lifecycle_guard.py", "guard_loop"), ("s2-soak/lifecycle_guard.py", "bounded_action"), ("post-dogfood/supervise_pdh3_scale_campaign.py", "delete_exact_worker")), (("s2-soak/test_lifecycle_guard.py", "test_transient_get_and_failed_stop_do_not_suppress_delete"), ("s2-soak/test_lifecycle_guard.py", "test_persistent_transient_failure_blocks_at_deadline"), ("post-dogfood/test_supervise_pdh3_scale_campaign.py", "test_teardown_requires_exact_404_and_all_inventory")), ("local_test_manifest.files",)),
    ("R8-21", "LOCAL_GREEN", (("post-dogfood/build_pdh3_scale_preflight_packet_r8.py", "build"),), (("post-dogfood/test_build_pdh3_scale_preflight_packet_r8.py", "test_successful_build_is_canonical_and_transport_safe"),), ("local_test_manifest.status", "local_test_manifest.files")),
    ("R8-22", "PROCESS_GATE", (("post-dogfood/build_pdh3_scale_preflight_packet_r8.py", "build"),), (), ("future_same_packet_glm_receipt", "future_same_packet_agy_receipt")),
    ("R8-23", "PRECREATE_RECHECK", (("post-dogfood/build_pdh3_scale_preflight_packet_r8.py", "_validate_active_inventory"), ("post-dogfood/build_pdh3_scale_preflight_packet_r8.py", "_validate_gpu_inventory"), ("post-dogfood/build_pdh3_scale_preflight_packet_r8.py", "_validate_times")), (("post-dogfood/test_build_pdh3_scale_preflight_packet_r8.py", "test_stale_provider_receipt_is_blocked"), ("post-dogfood/test_build_pdh3_scale_preflight_packet_r8.py", "test_nonempty_active_inventory_is_blocked")), ("provider.active_inventory_receipt", "provider.selected_offer", "lifecycle")),
)

CHECKLIST_REQUIREMENTS = {
    "R8-01": "Fresh packet/archive bind exact repaired bytes and no stale R7 authority.",
    "R8-02": "Attempts 01-07 remain immutable, hash-bound failed evidence.",
    "R8-03": "Production arguments reject reduced store-size or scale overrides.",
    "R8-04": "Retry/reconciliation permits only declared transient SQL outcomes.",
    "R8-05": "Conflict handling cannot conceal missing or mismatched rows.",
    "R8-06": "Vector-index recreation, ownership, coverage, and queryability are proved.",
    "R8-07": "One setup deadline includes receipt and teardown reserves.",
    "R8-08": "Selected worker completes target cardinality inside 5,400 seconds.",
    "R8-09": "Production reads directly hit nonzero seeded rows.",
    "R8-10": "Three full-shape premeasurement epochs pass and reset cleanly.",
    "R8-11": "Every epoch uses one shared 300-second monotonic deadline.",
    "R8-12": "The 288/232/9,976/24 execution schedule is exact.",
    "R8-13": "Every SIGKILL/restart cycle proves identity and state continuity.",
    "R8-14": "Raw logs and all unique verifier evidence remain reconstructable.",
    "R8-15": "Every checkpoint measures all declared resource thresholds.",
    "R8-16": "The syscall observer is incremental, atomic, bounded, and fail-closed.",
    "R8-17": "Partial cluster startup tears down every started node.",
    "R8-18": "Success cannot precede validated local teardown or coexist with failure.",
    "R8-19": "Supervisor terminal states, retrieval, and transport are unambiguous.",
    "R8-20": "Exact-ID lifecycle guard proves deletion and empty campaign inventory.",
    "R8-21": "All local tests, smoke, bundle, scan, compile, diff, and residue gates pass.",
    "R8-22": "GLM and AGY independently return GREEN on identical packet bytes.",
    "R8-23": "Provider shape, price, inventory, tool, and deadlines are fresh at creation.",
}

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_PRIVATE_PATH = re.compile(r"(?:^|[\s'\"`(])(?:/Users/[^/\s'\"`]+|/home/[^/\s'\"`]+)(?:/|\b)")
_SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bASIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)\baws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{20,}"),
    re.compile(r"(?i)\bauthorization\s*:\s*bearer\s+[A-Za-z0-9._~+/-]{16,}"),
)
_EXTERNAL_JUDGE_BLOCK_PATTERNS = (
    re.compile(
        r"(?i)(api[_-]?key|secret|password|passwd|access[_-]?token|bearer|auth[_-]?token)"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9_\-./+=]{12,}"
    ),
    re.compile(
        r"(?im)^\s*(?:export\s+)?[A-Z][A-Z0-9_]*"
        r"(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|PASSWD|AUTH)[A-Z0-9_]*\s*="
    ),
    re.compile(
        r"\b(?:session_meta\.payload|turn_context|response_item|tool_call_id|"
        r"transcript_path|history\.jsonl|requests\.jsonl|audit_input|raw_cli|"
        r"conversation_id)\b",
        re.I,
    ),
)


class PreflightBuildError(ValueError):
    """A stable fail-closed packet-build error."""


@dataclass(frozen=True)
class BuildConfig:
    root: Path
    runtime_dir: Path
    campaign_id: str
    pod_name: str
    launch_window_start: str
    launch_window_end: str
    stop_after: str
    terminate_after: str
    stop_epoch: int
    terminate_epoch: int
    active_inventory_json: Path
    gpu_inventory_json: Path
    bundle_archive: Path
    bundle_receipt_json: Path
    bundle_manifest_json: Path
    local_test_manifest_json: Path
    prior_attempt_history_manifest_json: Path
    attempt_08_manifest_json: Path
    authorization_receipt: Path
    runpodctl_path: Path
    runpodctl_version: str
    runpodctl_sha256: str
    sources: tuple[str, ...]
    output_packet: Path
    output_bindings: Path


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(raw: bytes | Any) -> str:
    value = raw if isinstance(raw, bytes) else canonical(raw)
    return hashlib.sha256(value).hexdigest()


def _require_hex64(value: str, code: str) -> None:
    if not _HEX64.fullmatch(value):
        raise PreflightBuildError(code)


def _parse_utc(value: str, code: str) -> datetime:
    if not value.endswith("Z"):
        raise PreflightBuildError(code)
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise PreflightBuildError(code) from exc
    if parsed.tzinfo != timezone.utc:
        raise PreflightBuildError(code)
    return parsed


def _safe_relative(value: str, code: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or ".." in path.parts
        or "\x00" in value
        or "\\" in value
    ):
        raise PreflightBuildError(code)
    return path


def _within(path: Path, parent: Path, code: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(parent.resolve())
    except ValueError as exc:
        raise PreflightBuildError(code) from exc
    return resolved


def _regular_file(path: Path, code: str) -> Path:
    if not path.is_file() or path.is_symlink():
        raise PreflightBuildError(code)
    return path.resolve()


def _read_json(path: Path, label: str) -> Any:
    raw = _regular_file(path, f"{label}_MISSING").read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreflightBuildError(f"{label}_INVALID_JSON") from exc
    _assert_sanitized(canonical(value).decode("utf-8"), f"{label}_UNSAFE")
    return value


def _assert_sanitized(text: str, code: str) -> None:
    if "\x00" in text or _PRIVATE_PATH.search(text):
        raise PreflightBuildError(code)
    for pattern in _SECRET_PATTERNS:
        if pattern.search(text):
            raise PreflightBuildError(code)


def _assert_external_judge_safe(text: str, code: str) -> None:
    """Mirror the installed judge gateway's content-shape blocks on output."""
    for pattern in _EXTERNAL_JUDGE_BLOCK_PATTERNS:
        if pattern.search(text):
            raise PreflightBuildError(code)


def _read_source(root: Path, relative: str) -> tuple[dict[str, Any], str]:
    _safe_relative(relative, "SOURCE_PATH_UNSAFE")
    path = _within(root / relative, root, "SOURCE_PATH_OUTSIDE_ROOT")
    raw = _regular_file(path, "SOURCE_MISSING").read_bytes()
    if len(raw) > 512 * 1024 or b"\x00" in raw:
        raise PreflightBuildError("SOURCE_NOT_BOUNDED_UTF8_TEXT")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PreflightBuildError("SOURCE_NOT_BOUNDED_UTF8_TEXT") from exc
    _assert_sanitized(text, "SOURCE_UNSAFE")
    return {
        "path": relative,
        "bytes": len(raw),
        "sha256": digest(raw),
    }, text


def _resolve_artifact(root: Path, manifest: Path, relative: str) -> Path:
    _safe_relative(relative, "EVIDENCE_PATH_UNSAFE")
    candidates = []
    for candidate in (root / relative, manifest.parent / relative):
        resolved = candidate.resolve()
        if resolved in candidates:
            continue
        if resolved.is_file() and not resolved.is_symlink():
            candidates.append(resolved)
    if len(candidates) > 1:
        # A manifest extracted beside an immutable bundle can legitimately
        # resolve both to the current source tree and to the verified extracted
        # copy.  Accept that duplicate only when the bytes are identical; any
        # disagreement remains an ambiguity and fails closed.
        candidate_hashes = {digest(candidate.read_bytes()) for candidate in candidates}
        if len(candidate_hashes) == 1:
            return candidates[0]
    if len(candidates) != 1:
        raise PreflightBuildError(
            "EVIDENCE_PATH_MISSING_OR_AMBIGUOUS:" + relative
        )
    return candidates[0]


def _verify_bound_file(
    root: Path,
    manifest: Path,
    relative: str,
    expected_sha256: str,
    expected_bytes: Any = None,
) -> dict[str, Any]:
    _require_hex64(expected_sha256, "EVIDENCE_SHA256_INVALID")
    path = _resolve_artifact(root, manifest, relative)
    raw = path.read_bytes()
    if digest(raw) != expected_sha256:
        raise PreflightBuildError("EVIDENCE_HASH_MISMATCH")
    if expected_bytes is not None and (
        not isinstance(expected_bytes, int)
        or isinstance(expected_bytes, bool)
        or expected_bytes != len(raw)
    ):
        raise PreflightBuildError("EVIDENCE_SIZE_MISMATCH")
    if path.suffix.lower() in {".json", ".jsonl", ".ndjson", ".md", ".txt", ".log"} and len(raw) <= 4 * 1024 * 1024:
        try:
            _assert_sanitized(raw.decode("utf-8"), "EVIDENCE_ARTIFACT_UNSAFE")
        except UnicodeDecodeError as exc:
            raise PreflightBuildError("EVIDENCE_ARTIFACT_NOT_UTF8") from exc
    return {"path": relative, "bytes": len(raw), "sha256": expected_sha256}


def _manifest_body(
    document: Mapping[str, Any], label: str, hash_field: str
) -> dict[str, Any]:
    expected = document.get(hash_field)
    if not isinstance(expected, str):
        raise PreflightBuildError(f"{label}_MANIFEST_HASH_MISSING")
    _require_hex64(expected, f"{label}_MANIFEST_HASH_INVALID")
    body = {key: value for key, value in document.items() if key != hash_field}
    if digest(body) != expected:
        raise PreflightBuildError(f"{label}_MANIFEST_HASH_MISMATCH")
    return body


def _walk_bindings(
    value: Any,
    root: Path,
    manifest: Path,
    *,
    key: str | None = None,
) -> list[dict[str, Any]]:
    verified: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
            verified.append(
                _verify_bound_file(
                    root,
                    manifest,
                    value["path"],
                    value["sha256"],
                    value.get("bytes"),
                )
            )
            return verified
        if key == "files" and value and all(
            isinstance(name, str) and isinstance(sha256, str)
            for name, sha256 in value.items()
        ):
            for name, sha256 in sorted(value.items()):
                verified.append(_verify_bound_file(root, manifest, name, sha256))
            return verified
        for child_key, child in value.items():
            verified.extend(_walk_bindings(child, root, manifest, key=child_key))
    elif isinstance(value, list):
        for child in value:
            verified.extend(_walk_bindings(child, root, manifest, key=key))
    return verified


def _verify_manifest(
    path: Path,
    root: Path,
    label: str,
    *,
    hash_field: str = "manifest_sha256",
    nested_key: str | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    document = _read_json(path, label)
    if (
        nested_key is not None
        and isinstance(document, dict)
        and hash_field not in document
        and isinstance(document.get(nested_key), dict)
    ):
        document = document[nested_key]
    if not isinstance(document, dict):
        raise PreflightBuildError(f"{label}_MANIFEST_NOT_OBJECT")
    _manifest_body(document, label, hash_field)
    files = _walk_bindings(document, root, path)
    if not files:
        raise PreflightBuildError(f"{label}_NO_HASHED_ARTIFACTS")
    raw = canonical(document)
    binding = {
        "bytes": len(raw),
        "sha256": digest(raw),
        "manifest_hash_field": hash_field,
        "manifest_hash": document[hash_field],
        "verified_artifacts": len(files),
    }
    return document, files, binding


def _load_contract(root: Path) -> Any:
    path = root / "post-dogfood" / "pdh3_scale_contract.py"
    spec = importlib.util.spec_from_file_location("pdh3_scale_contract_r8", path)
    if spec is None or spec.loader is None:
        raise PreflightBuildError("CONTRACT_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # pragma: no cover - exact import cause is retained
        raise PreflightBuildError("CONTRACT_IMPORT_FAILED") from exc
    for name in ("production_contract", "expected_schedule"):
        if not callable(getattr(module, name, None)):
            raise PreflightBuildError("CONTRACT_INTERFACE_MISSING")
    return module


def _validate_times(
    config: BuildConfig,
    contract: Mapping[str, Any],
    now: datetime,
) -> dict[str, Any]:
    start = _parse_utc(config.launch_window_start, "LAUNCH_START_INVALID")
    end = _parse_utc(config.launch_window_end, "LAUNCH_END_INVALID")
    stop = _parse_utc(config.stop_after, "STOP_AFTER_INVALID")
    terminate = _parse_utc(config.terminate_after, "TERMINATE_AFTER_INVALID")
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)
    if start <= now:
        raise PreflightBuildError("LAUNCH_WINDOW_EXPIRED")
    if not start < end < stop < terminate:
        raise PreflightBuildError("LIFECYCLE_TIME_ORDER_INVALID")
    if int(stop.timestamp()) != config.stop_epoch or int(terminate.timestamp()) != config.terminate_epoch:
        raise PreflightBuildError("LIFECYCLE_EPOCH_MISMATCH")

    workload = contract["workload"]
    provider = contract["runpod"]
    paid_seconds = int((terminate - start).total_seconds())
    required_before_stop = (
        int(workload["setup_timeout_seconds"])
        + int(workload["remote_preflight_epochs"]) * PREFLIGHT_EPOCH_SECONDS
        + int(provider["measured_seconds"])
        + SETUP_CLOSEOUT_RESERVE_SECONDS
    )
    if paid_seconds > int(provider["paid_seconds_max"]):
        raise PreflightBuildError("PAID_LIFETIME_OVERFLOW")
    if (stop - end).total_seconds() < required_before_stop:
        raise PreflightBuildError("MEASURED_WINDOW_INSUFFICIENT")
    if (terminate - stop).total_seconds() < FINAL_DELETE_RESERVE_SECONDS:
        raise PreflightBuildError("DELETE_RESERVE_INSUFFICIENT")
    return {
        "start": config.launch_window_start,
        "end": config.launch_window_end,
        "stop_after": config.stop_after,
        "terminate_after": config.terminate_after,
        "stop_epoch": config.stop_epoch,
        "terminate_epoch": config.terminate_epoch,
        "maximum_paid_seconds": paid_seconds,
        "minimum_pre_stop_seconds_from_latest_launch": required_before_stop,
    }


def _validate_identity(campaign_id: str, pod_name: str) -> dict[str, str]:
    pattern = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
    if (
        not pattern.fullmatch(campaign_id)
        or not pattern.fullmatch(pod_name)
        or len(campaign_id) > 48
        or len(pod_name) > 63
        or not pod_name.startswith(campaign_id + "-")
    ):
        raise PreflightBuildError("CAMPAIGN_IDENTITY_INVALID")
    return {"campaign_id": campaign_id, "pod_name": pod_name}


def _validate_fresh_observation(
    observed_utc: Any,
    max_age_seconds: Any,
    now: datetime,
    label: str,
) -> str:
    if (
        not isinstance(observed_utc, str)
        or isinstance(max_age_seconds, bool)
        or not isinstance(max_age_seconds, int)
        or not 1 <= max_age_seconds <= PROVIDER_RECEIPT_MAX_AGE_SECONDS
    ):
        raise PreflightBuildError(label + "_FRESHNESS_INVALID")
    observed = _parse_utc(observed_utc, label + "_OBSERVED_UTC_INVALID")
    normalized_now = now if now.tzinfo is not None else now.replace(tzinfo=timezone.utc)
    age = (normalized_now.astimezone(timezone.utc) - observed).total_seconds()
    if age < -PROVIDER_RECEIPT_FUTURE_SKEW_SECONDS or age > max_age_seconds:
        raise PreflightBuildError(label + "_STALE")
    return observed_utc


def _validate_argv(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or any(
            not isinstance(item, str)
            or not item
            or "\x00" in item
            or "\n" in item
            or "\r" in item
            for item in value
        )
    ):
        raise PreflightBuildError(label + "_ARGV_INVALID")
    _assert_sanitized(canonical(value).decode("utf-8"), label + "_ARGV_UNSAFE")
    if value[:2] in (["sh", "-c"], ["bash", "-c"], ["zsh", "-c"]):
        raise PreflightBuildError(label + "_SHELL_INTERPOLATION_FORBIDDEN")
    return value


def _provider_raw_binding(
    root: Path,
    receipt_path: Path,
    value: Any,
    label: str,
) -> tuple[dict[str, Any], bytes]:
    if not isinstance(value, dict):
        raise PreflightBuildError(label + "_RAW_BINDING_INVALID")
    relative = value.get("path")
    expected_hash = value.get("sha256")
    expected_bytes = value.get("bytes")
    if not isinstance(relative, str) or not isinstance(expected_hash, str):
        raise PreflightBuildError(label + "_RAW_BINDING_INVALID")
    binding = _verify_bound_file(
        root,
        receipt_path,
        relative,
        expected_hash,
        expected_bytes,
    )
    raw_path = _resolve_artifact(root, receipt_path, relative)
    raw = raw_path.read_bytes()
    if len(raw) > 8 * 1024 * 1024 or b"\x00" in raw:
        raise PreflightBuildError(label + "_RAW_NOT_BOUNDED_TEXT")
    try:
        _assert_sanitized(raw.decode("utf-8"), label + "_RAW_UNSAFE")
    except UnicodeDecodeError as exc:
        raise PreflightBuildError(label + "_RAW_NOT_UTF8") from exc
    return binding, raw


def _validate_receipt_hash(value: Any, version: str, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("version") != version:
        raise PreflightBuildError(label + "_VERSION_INVALID")
    expected = value.get("receipt_sha256")
    if not isinstance(expected, str):
        raise PreflightBuildError(label + "_HASH_MISSING")
    _require_hex64(expected, label + "_HASH_INVALID")
    body = {key: item for key, item in value.items() if key != "receipt_sha256"}
    if digest(body) != expected:
        raise PreflightBuildError(label + "_HASH_MISMATCH")
    return body


def _validate_active_inventory(
    value: Any,
    *,
    root: Path,
    receipt_path: Path,
    now: datetime,
    runpodctl_display: str,
    runpodctl_version: str,
    runpodctl_sha256: str,
    campaign_id: str,
) -> dict[str, Any]:
    body = _validate_receipt_hash(
        value,
        "ck-pdh3-runpod-active-inventory-receipt-r8-v1",
        "ACTIVE_INVENTORY_RECEIPT",
    )
    _validate_fresh_observation(
        body.get("observed_utc"), body.get("max_age_seconds"), now, "ACTIVE_INVENTORY"
    )
    command = _validate_argv(body.get("command"), "ACTIVE_INVENTORY")
    # The relaunch gate is absence of paid/running resources.  ``--all`` also
    # returns historical EXITED pods, so requiring that response to equal []
    # is impossible for an account with preserved lifecycle history.  The
    # default list is provider-defined running-only inventory.
    expected_command = [runpodctl_display, "pod", "list", "--output", "json"]
    if (
        command != expected_command
        or body.get("command_sha256") != digest(command)
        or body.get("source") != "AUTHENTICATED_RUNPODCTL_JSON"
        or body.get("runpodctl_version") != runpodctl_version
        or body.get("runpodctl_sha256") != runpodctl_sha256
        or body.get("exit_status") != 0
        or body.get("shell_interpolation") is not False
        or body.get("campaign_id") != campaign_id
    ):
        raise PreflightBuildError("ACTIVE_INVENTORY_PROVENANCE_INVALID")
    raw_binding, raw = _provider_raw_binding(
        root, receipt_path, body.get("raw_response"), "ACTIVE_INVENTORY"
    )
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PreflightBuildError("ACTIVE_INVENTORY_RAW_INVALID_JSON") from exc
    if (
        parsed != body.get("inventory")
        or body.get("parsed_response_sha256") != digest(parsed)
        or parsed != []
    ):
        raise PreflightBuildError("ACTIVE_INVENTORY_NOT_EMPTY")
    return {
        "observed_utc": body["observed_utc"],
        "max_age_seconds": body["max_age_seconds"],
        "command": command,
        "command_sha256": body["command_sha256"],
        "raw_response": raw_binding,
        "parsed_response_sha256": body["parsed_response_sha256"],
        "inventory": [],
        "receipt_sha256": value["receipt_sha256"],
    }


def _number(value: Any, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise PreflightBuildError(code)
    return float(value)


def _find_l40s_inventory_rows(value: Any, expected_gpu_id: str) -> list[Mapping[str, Any]]:
    found: list[Mapping[str, Any]] = []
    if isinstance(value, dict):
        gpu_id = value.get("gpuId", value.get("gpu_id"))
        if gpu_id == expected_gpu_id:
            found.append(value)
        for child in value.values():
            found.extend(_find_l40s_inventory_rows(child, expected_gpu_id))
    elif isinstance(value, list):
        for child in value:
            found.extend(_find_l40s_inventory_rows(child, expected_gpu_id))
    return found


def _validate_inventory_component(
    value: Any,
    *,
    root: Path,
    receipt_path: Path,
    now: datetime,
    expected_command: list[str],
    label: str,
) -> tuple[dict[str, Any], Any]:
    if not isinstance(value, dict):
        raise PreflightBuildError(label + "_COMPONENT_INVALID")
    _validate_fresh_observation(
        value.get("observed_utc"), value.get("max_age_seconds"), now, label
    )
    command = _validate_argv(value.get("command"), label)
    if (
        command != expected_command
        or value.get("command_sha256") != digest(command)
        or value.get("exit_status") != 0
        or value.get("shell_interpolation") is not False
    ):
        raise PreflightBuildError(label + "_PROVENANCE_INVALID")
    raw_binding, raw = _provider_raw_binding(
        root, receipt_path, value.get("raw_response"), label
    )
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PreflightBuildError(label + "_RAW_INVALID_JSON") from exc
    if value.get("parsed_response_sha256") != digest(parsed):
        raise PreflightBuildError(label + "_PARSED_HASH_MISMATCH")
    return {
        "observed_utc": value["observed_utc"],
        "max_age_seconds": value["max_age_seconds"],
        "command": command,
        "command_sha256": value["command_sha256"],
        "raw_response": raw_binding,
        "parsed_response_sha256": value["parsed_response_sha256"],
    }, parsed


def _validate_gpu_inventory(
    value: Any,
    *,
    root: Path,
    receipt_path: Path,
    now: datetime,
    runpodctl_display: str,
    runpodctl_version: str,
    runpodctl_sha256: str,
    contract: Mapping[str, Any],
    maximum_paid_seconds: int,
    prior_cost: float,
) -> dict[str, Any]:
    body = _validate_receipt_hash(
        value,
        "ck-pdh3-runpod-gpu-pricing-receipt-r8-v1",
        "GPU_PRICING_RECEIPT",
    )
    _validate_fresh_observation(
        body.get("observed_utc"), body.get("max_age_seconds"), now, "GPU_PRICING"
    )
    if (
        body.get("source") != "RUNPOD_AUTHENTICATED_INVENTORY_AND_OFFICIAL_PRICING"
        or body.get("runpodctl_version") != runpodctl_version
        or body.get("runpodctl_sha256") != runpodctl_sha256
    ):
        raise PreflightBuildError("GPU_PRICING_PROVENANCE_INVALID")
    gpu_component, gpu_inventory = _validate_inventory_component(
        body.get("gpu_inventory"),
        root=root,
        receipt_path=receipt_path,
        now=now,
        expected_command=[
            runpodctl_display,
            "gpu",
            "list",
            "--include-unavailable",
            "--output",
            "json",
        ],
        label="GPU_INVENTORY",
    )
    datacenter_component, datacenter_inventory = _validate_inventory_component(
        body.get("datacenter_inventory"),
        root=root,
        receipt_path=receipt_path,
        now=now,
        expected_command=[
            runpodctl_display,
            "datacenter",
            "list",
            "--output",
            "json",
        ],
        label="DATACENTER_INVENTORY",
    )
    provider = contract["runpod"]
    inventory_rows = _find_l40s_inventory_rows(gpu_inventory, provider["gpu_id"])
    if not any(
        row.get("available") is True
        and row.get("secureCloud", row.get("cloud") == "SECURE") is True
        and _number(row.get("memoryInGb", row.get("vram_gb")), "GPU_INVENTORY_VALUE_INVALID")
        == 48
        for row in inventory_rows
    ):
        raise PreflightBuildError("SECURE_L40S_NOT_CURRENTLY_AVAILABLE")
    if provider["gpu_id"] not in canonical(datacenter_inventory).decode("utf-8"):
        raise PreflightBuildError("DATACENTER_L40S_PROVENANCE_MISSING")

    pricing = body.get("official_pricing")
    if not isinstance(pricing, dict):
        raise PreflightBuildError("OFFICIAL_PRICING_COMPONENT_INVALID")
    _validate_fresh_observation(
        pricing.get("observed_utc"),
        pricing.get("max_age_seconds"),
        now,
        "OFFICIAL_PRICING",
    )
    if (
        pricing.get("url") != RUNPOD_PRICING_URL
        or pricing.get("capture_method") != "READ_ONLY_OFFICIAL_PRICING_PAGE"
    ):
        raise PreflightBuildError("OFFICIAL_PRICING_PROVENANCE_INVALID")
    pricing_binding, pricing_raw = _provider_raw_binding(
        root, receipt_path, pricing.get("raw_response"), "OFFICIAL_PRICING"
    )
    source_page_binding, source_page_raw = _provider_raw_binding(
        root, receipt_path, pricing.get("source_page"), "OFFICIAL_PRICING_PAGE"
    )
    extracted = pricing.get("extracted_fields")
    expected_extracted = {
        "gpu_id": "NVIDIA L40S",
        "cloud": "SECURE",
        "gpu_count": 1,
        "vram_gb": 48,
        "ram_gb": 94,
        "vcpu": 16,
        "compute_rate_usd_hour": 0.99,
        "container_disk_rate_usd_gb_30_day_month": 0.10,
    }
    pricing_text = pricing_raw.decode("utf-8")
    if (
        extracted != expected_extracted
        or pricing.get("derived_fields_sha256") != digest(extracted)
        or pricing.get("source_page_sha256") != digest(source_page_raw)
        or digest(source_page_raw).encode("ascii") not in pricing_raw
        or any(
            token not in pricing_text
            for token in ("L40S", "48 GB", "94 GB", "16 vCPU", "$0.99", "$0.10")
        )
    ):
        raise PreflightBuildError("OFFICIAL_PRICING_FIELDS_INVALID")

    derivation = body.get("active_rate_derivation")
    if not isinstance(derivation, dict):
        raise PreflightBuildError("ACTIVE_RATE_DERIVATION_INVALID")
    expected_storage_rate = 250 * 0.10 / 720
    expected_active_rate = 0.99 + expected_storage_rate
    derivation_body = {
        key: item for key, item in derivation.items() if key != "derived_fields_sha256"
    }
    if (
        derivation.get("derived_fields_sha256") != digest(derivation_body)
        or derivation_body.get("formula")
        != "compute_rate + container_disk_gb * disk_rate_usd_gb_30_day_month / 720"
        or derivation_body.get("compute_rate_usd_hour") != 0.99
        or derivation_body.get("container_disk_gb") != 250
        or derivation_body.get("disk_rate_usd_gb_30_day_month") != 0.10
        or derivation_body.get("month_hours") != 720
        or not math.isclose(
            _number(
                derivation_body.get("container_disk_rate_usd_hour"),
                "ACTIVE_RATE_DERIVATION_INVALID",
            ),
            expected_storage_rate,
            rel_tol=0,
            abs_tol=1e-12,
        )
        or not math.isclose(
            _number(
                derivation_body.get("active_rate_usd_hour"),
                "ACTIVE_RATE_DERIVATION_INVALID",
            ),
            expected_active_rate,
            rel_tol=0,
            abs_tol=1e-12,
        )
        or derivation_body.get("active_rate_ceiling_usd_hour")
        != provider["active_rate_usd_hour_max"]
    ):
        raise PreflightBuildError("ACTIVE_RATE_DERIVATION_INVALID")

    selected = body.get("derived_offer")
    expected_selected = {
        "gpu_id": provider["gpu_id"],
        "available": True,
        "cloud": provider["cloud"],
        "gpu_count": provider["gpu_count"],
        "vram_gb": 48,
        "vcpu": 16,
        "ram_gb": 94,
        "compute_rate_usd_hour": 0.99,
        "active_rate_usd_hour": expected_active_rate,
        "offer_id": None,
        "region": None,
    }
    if (
        selected != expected_selected
        or body.get("derived_offer_sha256") != digest(selected)
    ):
        raise PreflightBuildError("DERIVED_L40S_OFFER_INVALID")
    projected = selected["active_rate_usd_hour"] * maximum_paid_seconds / 3600
    aggregate = prior_cost + projected
    if aggregate > provider["aggregate_cost_usd_max"]:
        raise PreflightBuildError("AGGREGATE_COST_OVERFLOW")
    if selected["compute_rate_usd_hour"] > provider["compute_rate_usd_hour_max"]:
        raise PreflightBuildError("COMPUTE_RATE_OVERFLOW")
    if selected["active_rate_usd_hour"] > provider["active_rate_usd_hour_max"]:
        raise PreflightBuildError("ACTIVE_RATE_OVERFLOW")
    return {
        **selected,
        "gpu_inventory_provenance": gpu_component,
        "datacenter_inventory_provenance": datacenter_component,
        "official_pricing_provenance": {
            "url": pricing["url"],
            "observed_utc": pricing["observed_utc"],
            "max_age_seconds": pricing["max_age_seconds"],
            "capture_method": pricing["capture_method"],
            "raw_response": pricing_binding,
            "source_page": source_page_binding,
            "source_page_sha256": pricing["source_page_sha256"],
            "derived_fields_sha256": pricing["derived_fields_sha256"],
        },
        "active_rate_derivation": derivation,
        "derived_offer_sha256": body["derived_offer_sha256"],
        "receipt_sha256": value["receipt_sha256"],
        "projected_relaunch_cost_usd": round(projected, 6),
        "prior_cost_ceiling_usd": round(prior_cost, 6),
        "aggregate_cost_ceiling_usd": round(aggregate, 6),
    }


def _authorization_binding(path: Path, root: Path, contract: Mapping[str, Any]) -> dict[str, Any]:
    path = _within(path, root, "AUTHORIZATION_OUTSIDE_ROOT")
    raw = _regular_file(path, "AUTHORIZATION_MISSING").read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PreflightBuildError("AUTHORIZATION_NOT_UTF8") from exc
    _assert_sanitized(text, "AUTHORIZATION_UNSAFE")
    required = (
        "NVIDIA L40S",
        "86,400",
        "100,800",
        "$35.00",
        "$0.99",
        "$1.10",
        "250 GB",
    )
    if any(token not in text for token in required):
        raise PreflightBuildError("AUTHORIZATION_SCOPE_MISMATCH")
    return {
        "path": path.relative_to(root.resolve()).as_posix(),
        "bytes": len(raw),
        "sha256": digest(raw),
    }


def _validate_template_hash(value: Any, expected: Any, label: str) -> None:
    if not isinstance(expected, str):
        raise PreflightBuildError(label + "_HASH_MISSING")
    _require_hex64(expected, label + "_HASH_INVALID")
    if digest(value) != expected:
        raise PreflightBuildError(label + "_HASH_MISMATCH")


def _validate_launch_v3(
    launch: Mapping[str, Any],
    contract_module: Any,
    bundle_by_path: Mapping[str, dict[str, Any]],
) -> dict[str, Any]:
    if launch.get("version") != "ck-pdh3-production-launch-binding-v3":
        raise PreflightBuildError("BUNDLE_PRODUCTION_LAUNCH_VERSION_INVALID")
    arguments = launch.get("argument_bindings")
    if not isinstance(arguments, dict):
        raise PreflightBuildError("BUNDLE_PRODUCTION_ARGUMENTS_MISSING")
    try:
        contract_module.validate_production_arguments(arguments)
    except Exception as exc:
        raise PreflightBuildError("BUNDLE_PRODUCTION_ARGUMENT_MISMATCH") from exc

    controller = _validate_argv(
        launch.get("controller_argv_template"), "BUNDLE_CONTROLLER_TEMPLATE"
    )
    traced = _validate_argv(
        launch.get("traced_argv_template"), "BUNDLE_TRACED_TEMPLATE"
    )
    environment = launch.get("launch_environment_template")
    setup = launch.get("tracer_setup_argv_templates")
    if (
        not isinstance(environment, dict)
        or set(environment) != {"PDH3_PACKET_SHA256", "LD_LIBRARY_PATH"}
        or environment.get("PDH3_PACKET_SHA256") != "__FROZEN_PACKET_SHA256__"
        or not isinstance(environment.get("LD_LIBRARY_PATH"), str)
        or environment.get("LD_LIBRARY_PATH")
        != launch.get("tracer_library_path_template")
        or not isinstance(setup, list)
        or len(setup) != 2
        or any(not isinstance(item, list) for item in setup)
    ):
        raise PreflightBuildError("BUNDLE_PRODUCTION_ENVIRONMENT_INVALID")
    _validate_template_hash(
        controller,
        launch.get("controller_argv_template_sha256"),
        "BUNDLE_CONTROLLER_TEMPLATE",
    )
    _validate_template_hash(
        traced,
        launch.get("traced_argv_template_sha256"),
        "BUNDLE_TRACED_TEMPLATE",
    )
    _validate_template_hash(
        environment,
        launch.get("launch_environment_template_sha256"),
        "BUNDLE_LAUNCH_ENVIRONMENT_TEMPLATE",
    )
    _validate_template_hash(
        setup,
        launch.get("tracer_setup_template_sha256"),
        "BUNDLE_TRACER_SETUP_TEMPLATE",
    )

    tracer_root = "__TRACER_ROOT__"
    artifact_bindings = launch.get("tracer_artifact_bindings")
    expected_artifacts = {
        (
            "p2-cleanroom/vendor/ubuntu-noble-strace/"
            "strace_6.8-0ubuntu2_amd64.deb"
        ): contract_module.STRACE_DEB_SHA256,
        (
            "p2-cleanroom/vendor/ubuntu-noble-strace/"
            "libunwind8_1.6.2-3build1_amd64.deb"
        ): contract_module.LIBUNWIND8_DEB_SHA256,
    }
    if (
        not isinstance(artifact_bindings, list)
        or len(artifact_bindings) != len(expected_artifacts)
        or {
            row.get("path"): row.get("sha256")
            for row in artifact_bindings
            if isinstance(row, dict)
        }
        != expected_artifacts
    ):
        raise PreflightBuildError("BUNDLE_TRACER_ARTIFACT_BINDINGS_INVALID")
    for relative, expected_hash in expected_artifacts.items():
        bundled = bundle_by_path.get(relative)
        if bundled is None or bundled.get("sha256") != expected_hash:
            raise PreflightBuildError("BUNDLE_TRACER_ARTIFACT_HASH_MISMATCH")
    expected_setup = [
        [
            "dpkg-deb",
            "--extract",
            (
                "p2-cleanroom/vendor/ubuntu-noble-strace/"
                "libunwind8_1.6.2-3build1_amd64.deb"
            ),
            tracer_root,
        ],
        [
            "dpkg-deb",
            "--extract",
            (
                "p2-cleanroom/vendor/ubuntu-noble-strace/"
                "strace_6.8-0ubuntu2_amd64.deb"
            ),
            tracer_root,
        ],
    ]
    if setup != expected_setup:
        raise PreflightBuildError("BUNDLE_TRACER_SETUP_COMMAND_INVALID")
    tracer_binary = launch.get("tracer_binary_template")
    if (
        tracer_binary != "__TRACER_ROOT__/usr/bin/strace"
        or launch.get("tracer_binary_sha256")
        != contract_module.STRACE_BINARY_SHA256
        or environment["LD_LIBRARY_PATH"]
        != (
            "__TRACER_ROOT__/usr/lib/x86_64-linux-gnu:"
            "__TRACER_ROOT__/lib/x86_64-linux-gnu"
        )
    ):
        raise PreflightBuildError("BUNDLE_EXTRACTED_TRACER_BINDING_INVALID")

    expected_order = [
        "VERIFY_BUNDLED_DEB_HASHES",
        "EXTRACT_LIBUNWIND_WITH_DPKG_DEB",
        "EXTRACT_STRACE_WITH_DPKG_DEB",
        "VERIFY_EXTRACTED_STRACE_BINARY_HASH",
        "SET_EXACT_LAUNCH_ENVIRONMENT",
        "EXECUTE_TRACED_ARGV_WITHOUT_SHELL",
    ]
    try:
        delimiter = traced.index("--")
        binary_index = controller.index("--binary") + 1
    except (ValueError, IndexError) as exc:
        raise PreflightBuildError("BUNDLE_PRODUCTION_COMMAND_INVALID") from exc
    binary = controller[binary_index]
    if (
        traced[delimiter + 1 :] != controller
        or traced[:2] != ["python3", "post-dogfood/run_pdh3_traced.py"]
        or "__FROZEN_PACKET_SHA256__" not in traced
        or "__IMMUTABLE_CAMPAIGN_ID__" not in controller
        or "__FROZEN_PACKET__" not in controller
        or "__REMOTE_EVIDENCE_ROOT__" not in controller
        or bundle_by_path.get(binary) is None
        or launch.get("required_remote_setup_order") != expected_order
        or arguments.get("store_size", "NOT_PRESENT") is not None
        or launch.get("store_size_flag") != "ABSENT"
        or "--store-size" in controller
        or launch.get("shell_interpolation") is not False
    ):
        raise PreflightBuildError("BUNDLE_PRODUCTION_COMMAND_INVALID")
    return dict(launch)


def _bundle_bindings(
    config: BuildConfig,
    root: Path,
    source_bindings: Mapping[str, dict[str, Any]],
    prior_history: Mapping[str, Any],
    contract_module: Any,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest, files, manifest_binding = _verify_manifest(
        config.bundle_manifest_json, root, "BUNDLE", nested_key="manifest"
    )
    receipt = _read_json(config.bundle_receipt_json, "BUNDLE_RECEIPT")
    if not isinstance(receipt, dict) or not isinstance(receipt.get("receipt_sha256"), str):
        raise PreflightBuildError("BUNDLE_RECEIPT_HASH_MISSING")
    if (
        receipt.get("version") != "ck-pdh3-scale-bundle-receipt-v2"
        or manifest.get("version") != "ck-pdh3-scale-bundle-manifest-v2"
        or manifest.get("credential_free") is not True
        or manifest.get("synthetic_only") is not True
    ):
        raise PreflightBuildError("BUNDLE_V2_BOUNDARY_INVALID")
    receipt_body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if digest(receipt_body) != receipt["receipt_sha256"]:
        raise PreflightBuildError("BUNDLE_RECEIPT_HASH_MISMATCH")
    if receipt.get("manifest") != manifest:
        raise PreflightBuildError("BUNDLE_RECEIPT_MANIFEST_MISMATCH")
    if receipt.get("history_manifest") != prior_history:
        raise PreflightBuildError("BUNDLE_RECEIPT_HISTORY_MISMATCH")
    if (
        manifest.get("history_manifest_sha256")
        != prior_history.get("history_manifest_sha256")
        or manifest.get("history_raw_evidence_embedded") is not False
        or manifest.get("host_control_plane_transferred") is not False
    ):
        raise PreflightBuildError("BUNDLE_HISTORY_BOUNDARY_MISMATCH")
    host_only = receipt.get("host_only_bindings")
    if not isinstance(host_only, dict) or not isinstance(
        host_only.get("bindings_sha256"), str
    ):
        raise PreflightBuildError("BUNDLE_HOST_BINDINGS_MISSING")
    host_body = {
        key: value for key, value in host_only.items() if key != "bindings_sha256"
    }
    if digest(host_body) != host_only["bindings_sha256"]:
        raise PreflightBuildError("BUNDLE_HOST_BINDINGS_HASH_MISMATCH")
    if (
        host_only.get("version") != "ck-pdh3-host-control-plane-bindings-v1"
        or
        host_only.get("archive_transfer") is not False
        or manifest.get("host_only_bindings_sha256") != host_only["bindings_sha256"]
    ):
        raise PreflightBuildError("BUNDLE_HOST_BOUNDARY_MISMATCH")
    remote_paths = {
        row.get("path") for row in manifest.get("files", []) if isinstance(row, dict)
    }
    for row in host_only.get("files", []):
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise PreflightBuildError("BUNDLE_HOST_BINDINGS_SCHEMA_INVALID")
        relative = row["path"]
        source = source_bindings.get(relative)
        if (
            relative in remote_paths
            or source is None
            or source["sha256"] != row.get("sha256")
            or source["bytes"] != row.get("bytes")
        ):
            raise PreflightBuildError("BUNDLE_HOST_SOURCE_DRIFT")
    verification = receipt.get("archive_verification")
    if not isinstance(verification, dict) or not isinstance(
        verification.get("verification_sha256"), str
    ):
        raise PreflightBuildError("BUNDLE_VERIFICATION_MISSING")
    verification_body = {
        key: value
        for key, value in verification.items()
        if key != "verification_sha256"
    }
    if digest(verification_body) != verification["verification_sha256"] or any(
        verification.get(key) is not True
        for key in ("exact_member_set", "regular_files_only", "source_bytes_match_current")
    ):
        raise PreflightBuildError("BUNDLE_VERIFICATION_INVALID")
    if verification.get("version") != "ck-pdh3-extracted-bundle-verification-v2":
        raise PreflightBuildError("BUNDLE_VERIFICATION_VERSION_INVALID")
    bundle_by_path = {row["path"]: row for row in files}
    launch = manifest.get("production_launch")
    if not isinstance(launch, dict) or not isinstance(launch.get("launch_sha256"), str):
        raise PreflightBuildError("BUNDLE_PRODUCTION_LAUNCH_MISSING")
    launch_body = {key: value for key, value in launch.items() if key != "launch_sha256"}
    if digest(launch_body) != launch["launch_sha256"]:
        raise PreflightBuildError("BUNDLE_PRODUCTION_LAUNCH_HASH_MISMATCH")
    launch = _validate_launch_v3(launch, contract_module, bundle_by_path)
    archive = _regular_file(config.bundle_archive, "BUNDLE_ARCHIVE_MISSING")
    archive_raw_hash = hashlib.sha256()
    archive_bytes = 0
    with archive.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            archive_raw_hash.update(block)
            archive_bytes += len(block)
    if archive_bytes != receipt.get("archive_bytes") or archive_raw_hash.hexdigest() != receipt.get("archive_sha256"):
        raise PreflightBuildError("BUNDLE_ARCHIVE_MISMATCH")
    if Path(str(receipt.get("archive", ""))).name != archive.name:
        raise PreflightBuildError("BUNDLE_ARCHIVE_NAME_MISMATCH")
    for relative in REMOTE_BUNDLE_REQUIRED:
        source = source_bindings.get(relative)
        bundled = bundle_by_path.get(relative)
        if source is None or bundled is None or source["sha256"] != bundled["sha256"] or source["bytes"] != bundled["bytes"]:
            raise PreflightBuildError("BUNDLE_SOURCE_DRIFT")
    binding = {
        "archive": archive.name,
        "archive_bytes": archive_bytes,
        "archive_sha256": archive_raw_hash.hexdigest(),
        "receipt_sha256": receipt["receipt_sha256"],
        "manifest": manifest_binding,
        "history_manifest_sha256": prior_history["history_manifest_sha256"],
        "host_only_bindings_sha256": host_only["bindings_sha256"],
        "archive_verification_sha256": verification["verification_sha256"],
        "production_launch_sha256": launch["launch_sha256"],
    }
    return binding, manifest, launch


def _substitute_argv(
    template: list[str], substitutions: Mapping[str, str], label: str
) -> list[str]:
    result = []
    for item in template:
        resolved = item
        for placeholder, replacement in substitutions.items():
            resolved = resolved.replace(placeholder, replacement)
        result.append(resolved)
    return _validate_argv(result, label)


def _command_bindings(
    config: BuildConfig,
    contract: Mapping[str, Any],
    launch: Mapping[str, Any],
    source_bindings: Mapping[str, dict[str, Any]],
    runpodctl_display: str,
) -> dict[str, Any]:
    identity = _validate_identity(config.campaign_id, config.pod_name)
    provider = contract["runpod"]
    remote_root = "/workspace/" + config.campaign_id
    remote_packet = remote_root + "/PDH_3_SCALE_RUNPOD_PREFLIGHT_PACKET_R8.md"
    remote_evidence = remote_root + "/evidence"
    tracer_root = remote_root + "/tracer-root"
    substitutions = {
        "__TRACER_ROOT__": tracer_root,
        "__FROZEN_PACKET__": remote_packet,
        "__REMOTE_EVIDENCE_ROOT__": remote_evidence,
        "__IMMUTABLE_CAMPAIGN_ID__": config.campaign_id,
        "__REMOTE_TRACE_PREFIX__": remote_root + "/network-trace",
        # The tracer owns this terminal receipt.  Keep it outside the
        # controller-owned evidence root: the production controller correctly
        # refuses to start when its output directory already exists.
        "__REMOTE_NETWORK_RECEIPT__": remote_root + "/network-receipt.json",
    }
    controller = _substitute_argv(
        list(launch["controller_argv_template"]),
        substitutions,
        "CONCRETE_CONTROLLER",
    )
    if any("__" in item for item in controller):
        raise PreflightBuildError("CONCRETE_CONTROLLER_PLACEHOLDER_REMAINS")
    traced_runtime_template = _substitute_argv(
        list(launch["traced_argv_template"]),
        substitutions,
        "TRACED_RUNTIME_TEMPLATE",
    )
    unresolved_traced = sorted(
        {
            placeholder
            for item in traced_runtime_template
            for placeholder in re.findall(r"__[A-Z0-9_]+__", item)
        }
    )
    if unresolved_traced != ["__FROZEN_PACKET_SHA256__"]:
        raise PreflightBuildError("TRACED_RUNTIME_PLACEHOLDER_SET_INVALID")
    setup = [
        _substitute_argv(list(argv), substitutions, "TRACER_SETUP")
        for argv in launch["tracer_setup_argv_templates"]
    ]
    if any("__" in item for argv in setup for item in argv):
        raise PreflightBuildError("TRACER_SETUP_PLACEHOLDER_REMAINS")
    environment = {
        key: value.replace("__TRACER_ROOT__", tracer_root)
        for key, value in launch["launch_environment_template"].items()
    }
    if environment.get("PDH3_PACKET_SHA256") != "__FROZEN_PACKET_SHA256__":
        raise PreflightBuildError("LAUNCH_PACKET_ENVIRONMENT_INVALID")

    create_argv = [
        runpodctl_display,
        "pod",
        "create",
        "--cloud-type",
        provider["cloud"],
        "--compute-type",
        "GPU",
        "--gpu-id",
        provider["gpu_id"],
        "--gpu-count",
        str(provider["gpu_count"]),
        "--image",
        provider["image"],
        "--name",
        config.pod_name,
        "--container-disk-in-gb",
        str(provider["container_disk_gb"]),
        "--volume-in-gb",
        str(provider["volume_gb"]),
        "--ports",
        ",".join(provider["ports"]),
        "--stop-after",
        config.stop_after,
        "--terminate-after",
        config.terminate_after,
        "--output",
        "json",
    ]
    create_argv = _validate_argv(create_argv, "RUNPOD_CREATE")
    lifecycle_argv_template = _validate_argv(
        [
            "python3",
            "s2-soak/lifecycle_guard.py",
            "--runpodctl",
            runpodctl_display,
            "--runpodctl-sha256",
            config.runpodctl_sha256,
            "--pod-id",
            "__PROVIDER_POD_ID__",
            "--pod-name",
            config.pod_name,
            "--campaign-prefix",
            config.campaign_id,
            "--stop-epoch",
            str(config.stop_epoch),
            "--delete-epoch",
            str(config.terminate_epoch),
            "--heartbeat-seconds",
            "30",
            "--command-timeout-seconds",
            "30",
            "--bind-timeout-seconds",
            "120",
            "--delete-grace-seconds",
            "900",
            "--log",
            ".pdh3-runtime/r8/lifecycle-guard.ndjson",
        ],
        "LIFECYCLE_GUARD_TEMPLATE",
    )
    trace_tool = source_bindings.get("post-dogfood/run_pdh3_traced.py")
    if trace_tool is None:
        raise PreflightBuildError("TRACE_TOOL_SOURCE_BINDING_MISSING")
    child_command_sha256 = digest(controller)
    supervisor_argv_template = _validate_argv(
        [
            "python3",
            "post-dogfood/supervise_pdh3_scale_campaign.py",
            "--runpodctl",
            runpodctl_display,
            "--runpodctl-sha256",
            config.runpodctl_sha256,
            "--pod-id",
            "__PROVIDER_POD_ID__",
            "--pod-name",
            config.pod_name,
            "--campaign-prefix",
            config.campaign_id,
            "--ssh-config",
            ".pdh3-runtime/r8/ssh-config",
            "--ssh-alias",
            config.pod_name,
            "--remote-root",
            remote_root,
            "--retrieval",
            ".pdh3-runtime/r8/retrieval",
            "--log",
            ".pdh3-runtime/r8/supervisor.ndjson",
            "--packet-sha256",
            "__FROZEN_PACKET_SHA256__",
            "--trace-tool-sha256",
            trace_tool["sha256"],
            "--trace-command-sha256",
            child_command_sha256,
            "--closeout-deadline-epoch",
            str(config.terminate_epoch),
            "--poll-seconds",
            "300",
            "--command-timeout-seconds",
            "60",
            "--transfer-timeout-seconds",
            "1800",
            "--teardown-reserve-seconds",
            "300",
        ],
        "SUPERVISOR_TEMPLATE",
    )
    return {
        "version": "ck-pdh3-r8-command-bindings-v1",
        "identity": identity,
        "remote_root": remote_root,
        "remote_packet": remote_packet,
        "remote_evidence_root": remote_evidence,
        "runpod_create_argv": create_argv,
        "runpod_create_argv_sha256": digest(create_argv),
        "lifecycle_guard_argv_template": lifecycle_argv_template,
        "lifecycle_guard_argv_template_sha256": digest(lifecycle_argv_template),
        "supervisor_argv_template": supervisor_argv_template,
        "supervisor_argv_template_sha256": digest(supervisor_argv_template),
        "tracer_setup_argv": setup,
        "tracer_setup_argv_sha256": digest(setup),
        "tracer_binary": tracer_root + "/usr/bin/strace",
        "tracer_binary_sha256": launch["tracer_binary_sha256"],
        "launch_environment_runtime_template": environment,
        "launch_environment_runtime_template_sha256": digest(environment),
        "traced_argv_runtime_template": traced_runtime_template,
        "traced_argv_runtime_template_sha256": digest(traced_runtime_template),
        "child_controller_argv": controller,
        "child_controller_argv_sha256": child_command_sha256,
        "packet_sha256_runtime_placeholder": "__FROZEN_PACKET_SHA256__",
        "provider_pod_id_runtime_placeholder": "__PROVIDER_POD_ID__",
        "runtime_substitution_law": {
            "allowed_placeholders": [
                "__FROZEN_PACKET_SHA256__",
                "__PROVIDER_POD_ID__",
            ],
            "recompute_concrete_argv_hash_after_substitution": True,
            "child_controller_hash_is_already_concrete": True,
        },
        "shell_interpolation": False,
    }


def instantiate_runtime_commands(
    command_bindings: Mapping[str, Any],
    *,
    packet_sha256: str,
    provider_pod_id: str,
) -> dict[str, Any]:
    """Instantiate the two declared runtime placeholders without a shell.

    This function is the only packet-defined runtime completion path.  It
    accepts the final packet digest and provider-returned Pod ID, substitutes
    those two values in argv/environment structures, rejects every residual
    placeholder, and returns canonical hashes for direct ``subprocess`` use.
    """
    _require_hex64(packet_sha256, "RUNTIME_PACKET_SHA256_INVALID")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", provider_pod_id):
        raise PreflightBuildError("RUNTIME_PROVIDER_POD_ID_INVALID")
    if (
        command_bindings.get("version") != "ck-pdh3-r8-command-bindings-v1"
        or command_bindings.get("shell_interpolation") is not False
        or command_bindings.get("runtime_substitution_law", {}).get(
            "allowed_placeholders"
        )
        != ["__FROZEN_PACKET_SHA256__", "__PROVIDER_POD_ID__"]
    ):
        raise PreflightBuildError("RUNTIME_COMMAND_BINDINGS_INVALID")
    template_hash_checks = (
        ("runpod_create_argv", "runpod_create_argv_sha256"),
        ("tracer_setup_argv", "tracer_setup_argv_sha256"),
        (
            "launch_environment_runtime_template",
            "launch_environment_runtime_template_sha256",
        ),
        ("child_controller_argv", "child_controller_argv_sha256"),
        ("traced_argv_runtime_template", "traced_argv_runtime_template_sha256"),
        (
            "lifecycle_guard_argv_template",
            "lifecycle_guard_argv_template_sha256",
        ),
        ("supervisor_argv_template", "supervisor_argv_template_sha256"),
    )
    for value_field, hash_field in template_hash_checks:
        expected = command_bindings.get(hash_field)
        if not isinstance(expected, str):
            raise PreflightBuildError("RUNTIME_TEMPLATE_HASH_MISSING")
        _require_hex64(expected, "RUNTIME_TEMPLATE_HASH_INVALID")
        if digest(command_bindings.get(value_field)) != expected:
            raise PreflightBuildError("RUNTIME_TEMPLATE_HASH_MISMATCH")
    replacements = {
        "__FROZEN_PACKET_SHA256__": packet_sha256,
        "__PROVIDER_POD_ID__": provider_pod_id,
    }

    def substitute(value: str) -> str:
        result = value
        for placeholder, replacement in replacements.items():
            result = result.replace(placeholder, replacement)
        return result

    traced = _validate_argv(
        [substitute(item) for item in command_bindings["traced_argv_runtime_template"]],
        "RUNTIME_TRACED_COMMAND",
    )
    guard = _validate_argv(
        [
            substitute(item)
            for item in command_bindings["lifecycle_guard_argv_template"]
        ],
        "RUNTIME_LIFECYCLE_GUARD_COMMAND",
    )
    supervisor = _validate_argv(
        [substitute(item) for item in command_bindings["supervisor_argv_template"]],
        "RUNTIME_SUPERVISOR_COMMAND",
    )
    environment = {
        key: substitute(value)
        for key, value in command_bindings[
            "launch_environment_runtime_template"
        ].items()
    }
    controller = _validate_argv(
        list(command_bindings["child_controller_argv"]), "RUNTIME_CONTROLLER_COMMAND"
    )
    create = _validate_argv(
        list(command_bindings["runpod_create_argv"]), "RUNTIME_CREATE_COMMAND"
    )
    setup = [
        _validate_argv(list(argv), "RUNTIME_TRACER_SETUP_COMMAND")
        for argv in command_bindings["tracer_setup_argv"]
    ]
    concrete = {
        "version": "ck-pdh3-r8-concrete-runtime-commands-v1",
        "runpod_create_argv": create,
        "tracer_setup_argv": setup,
        "launch_environment": environment,
        "child_controller_argv": controller,
        "traced_argv": traced,
        "lifecycle_guard_argv": guard,
        "supervisor_argv": supervisor,
        "shell_interpolation": False,
    }
    if re.search(r"__[A-Z0-9_]+__", canonical(concrete).decode("utf-8")):
        raise PreflightBuildError("RUNTIME_PLACEHOLDER_REMAINS")
    try:
        delimiter = traced.index("--")
        trace_hash_index = supervisor.index("--trace-command-sha256") + 1
        packet_hash_index = supervisor.index("--packet-sha256") + 1
        guard_pod_index = guard.index("--pod-id") + 1
        supervisor_pod_index = supervisor.index("--pod-id") + 1
    except (ValueError, IndexError) as exc:
        raise PreflightBuildError("RUNTIME_COMMAND_INTERFACE_INVALID") from exc
    if (
        traced[delimiter + 1 :] != controller
        or digest(controller) != command_bindings["child_controller_argv_sha256"]
        or supervisor[trace_hash_index] != digest(controller)
        or supervisor[packet_hash_index] != packet_sha256
        or environment.get("PDH3_PACKET_SHA256") != packet_sha256
        or guard[guard_pod_index] != provider_pod_id
        or supervisor[supervisor_pod_index] != provider_pod_id
    ):
        raise PreflightBuildError("RUNTIME_COMMAND_BINDING_MISMATCH")
    hashes = {
        "runpod_create_argv_sha256": digest(create),
        "tracer_setup_argv_sha256": digest(setup),
        "launch_environment_sha256": digest(environment),
        "child_controller_argv_sha256": digest(controller),
        "traced_argv_sha256": digest(traced),
        "lifecycle_guard_argv_sha256": digest(guard),
        "supervisor_argv_sha256": digest(supervisor),
    }
    body = {**concrete, "hashes": hashes}
    return {**body, "commands_sha256": digest(body)}


def _history_cost_and_validate(
    history: Mapping[str, Any],
    contract: Mapping[str, Any],
    root: Path,
    manifest_path: Path,
) -> float:
    if history.get("version") != "ck-pdh3-attempt-history-manifest-v1":
        raise PreflightBuildError("PRIOR_HISTORY_VERSION_INVALID")
    if history.get("attempts_covered") != list(range(1, 8)):
        raise PreflightBuildError("PRIOR_ATTEMPT_SET_INVALID")
    if (
        history.get("binding_only") is not True
        or history.get("raw_evidence_embedded") is not False
        or history.get("credential_material_copied") is not False
    ):
        raise PreflightBuildError("PRIOR_HISTORY_BOUNDARY_INVALID")
    entries = history.get("entries")
    if (
        not isinstance(entries, list)
        or history.get("entry_count") != len(entries)
        or digest(entries) != history.get("history_set_sha256")
    ):
        raise PreflightBuildError("PRIOR_HISTORY_ENTRY_SET_INVALID")
    covered: set[int] = set()
    by_classification: dict[str, list[Mapping[str, Any]]] = {}
    for row in entries:
        if not isinstance(row, dict) or not isinstance(row.get("attempts"), list):
            raise PreflightBuildError("PRIOR_ATTEMPT_INVALID")
        attempts = row["attempts"]
        if any(
            isinstance(attempt, bool)
            or not isinstance(attempt, int)
            or attempt not in range(1, 8)
            for attempt in attempts
        ):
            raise PreflightBuildError("PRIOR_ATTEMPT_SET_INVALID")
        covered.update(attempts)
        classification = row.get("classification")
        if not isinstance(classification, str):
            raise PreflightBuildError("PRIOR_ATTEMPT_INVALID")
        by_classification.setdefault(classification, []).append(row)
    if covered != set(range(1, 8)):
        raise PreflightBuildError("PRIOR_ATTEMPT_SET_INVALID")
    final_states = by_classification.get("final_state", [])
    final_archives = by_classification.get("final_evidence_archive", [])
    if (
        len(final_states) != 1
        or len(final_archives) != 1
        or final_states[0].get("sha256")
        != history.get("attempt_07_final_state_sha256")
        or final_archives[0].get("sha256")
        != history.get("attempt_07_final_evidence_archive_sha256")
    ):
        raise PreflightBuildError("PRIOR_ATTEMPT_07_BINDING_INVALID")
    envelopes = by_classification.get("prior_attempt_cost_envelope", [])
    if len(envelopes) != 1:
        raise PreflightBuildError("PRIOR_COST_ENVELOPE_MISSING")
    envelope_path = _resolve_artifact(root, manifest_path, str(envelopes[0]["path"]))
    try:
        envelope_text = envelope_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise PreflightBuildError("PRIOR_COST_ENVELOPE_NOT_UTF8") from exc
    _assert_sanitized(envelope_text, "PRIOR_COST_ENVELOPE_UNSAFE")

    def field(name: str) -> float:
        match = re.search(rf"^- `{re.escape(name)}`: `([^`]+)`$", envelope_text, re.MULTILINE)
        if match is None:
            raise PreflightBuildError("PRIOR_COST_FIELD_MISSING")
        try:
            parsed = float(match.group(1))
        except ValueError as exc:
            raise PreflightBuildError("PRIOR_COST_INVALID") from exc
        return _number(parsed, "PRIOR_COST_INVALID")

    status = re.search(r"^- `STATUS`: `([^`]+)`$", envelope_text, re.MULTILINE)
    if status is None or status.group(1) != "CONSERVATIVE_UPPER_BOUND_NOT_PROVIDER_INVOICE":
        raise PreflightBuildError("PRIOR_COST_BASIS_INVALID")
    paid_seconds = field("PRIOR_ACTIVE_SECONDS_UPPER")
    disk_rate = field("DISK_RATE_USD_GB_30_DAY_MONTH")
    active_rate = field("TOTAL_ACTIVE_RATE_UPPER_USD_HOUR")
    prior_cost = field("PRIOR_COST_UPPER_USD")
    replacement_cost = field("REPLACEMENT_28_HOUR_COST_UPPER_USD")
    aggregate = field("AGGREGATE_COST_UPPER_USD")
    authorized = field("AUTHORIZED_AGGREGATE_CEILING_USD")
    headroom = field("MINIMUM_REMAINING_HEADROOM_USD")
    if paid_seconds != 5_684:
        raise PreflightBuildError("PRIOR_COST_INTERVAL_MISMATCH")
    compute = float(contract["runpod"]["compute_rate_usd_hour_max"])
    calculated_rate = compute + (
        float(contract["runpod"]["container_disk_gb"]) * disk_rate / (30 * 24)
    )
    calculated_prior = float(paid_seconds) / 3600 * calculated_rate
    calculated_replacement = 28 * calculated_rate
    calculated_aggregate = calculated_prior + calculated_replacement
    calculated_headroom = authorized - calculated_aggregate
    expected_values = (
        (active_rate, calculated_rate),
        (prior_cost, calculated_prior),
        (replacement_cost, calculated_replacement),
        (aggregate, calculated_aggregate),
        (headroom, calculated_headroom),
        (authorized, float(contract["runpod"]["aggregate_cost_usd_max"])),
    )
    if disk_rate < 0 or any(not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-9) for actual, expected in expected_values):
        raise PreflightBuildError("PRIOR_COST_ARITHMETIC_MISMATCH")
    if prior_cost < 0 or aggregate > authorized or headroom <= 0:
        raise PreflightBuildError("PRIOR_COST_INVALID")
    return prior_cost


def _runpodctl_v272_not_found(raw: str) -> bool:
    """Accept only the exact command-scoped v2.7.2 Pod-not-found wrapper."""
    first, separator, remainder = raw.partition("\n")
    expected_remainder = (
        "Usage:\n"
        "  runpodctl pod get <pod-id> [flags]\n\n"
        "Flags:\n"
        "  -h, --help                     help for get\n"
        "      --include-machine          include machine info\n"
        "      --include-network-volume   include network volume info\n\n"
        "Global Flags:\n"
        "  -o, --output string   output format (json, yaml) (default \"json\")\n\n"
        '{"error":"failed to get pod: api error: {"error":"pod not found",'
        '"status":404}\n (status 404)"}\n'
    )
    if not separator or remainder != expected_remainder:
        return False
    try:
        envelope = json.loads(first)
    except json.JSONDecodeError:
        return False
    if not isinstance(envelope, dict) or set(envelope) != {"error"}:
        return False
    message = envelope.get("error")
    if not isinstance(message, str):
        return False
    match = re.fullmatch(r"api error: (\{.*\})\n \(status 404\)", message)
    if match is None:
        return False
    try:
        nested = json.loads(match.group(1))
    except json.JSONDecodeError:
        return False
    return (
        isinstance(nested, dict)
        and nested.get("status") == 404
        and nested.get("error") == "pod not found"
    )


def _attempt_08_cost_and_validate(
    attempt: Mapping[str, Any],
    contract: Mapping[str, Any],
    root: Path,
    manifest_path: Path,
) -> float:
    if (
        attempt.get("version") != "ck-pdh3-attempt-08-manifest-v1"
        or attempt.get("attempt") != 8
        or attempt.get("status") != "BLOCKED_PREMEASUREMENT"
        or attempt.get("campaign_id") != "ck-pdh3-scale-r8-relaunch"
        or attempt.get("pod_name") != "ck-pdh3-scale-r8-relaunch-01"
        or attempt.get("pod_id") != "eo9deg7xgys6a8"
        or attempt.get("measured_clock_started") is not False
        or attempt.get("workload_executed") is not False
        or attempt.get("blocker") != "OUTPUT_ALREADY_EXISTS"
        or attempt.get("provider_resource_status") != "DELETED"
        or attempt.get("frozen_teardown_proof_status")
        != "BLOCKED_PROVIDER_RENDERING_UNSUPPORTED"
    ):
        raise PreflightBuildError("ATTEMPT_08_STATE_INVALID")
    _require_hex64(str(attempt.get("packet_sha256", "")), "ATTEMPT_08_PACKET_HASH_INVALID")
    if (
        attempt.get("binding_only") is not True
        or attempt.get("raw_evidence_embedded") is not False
        or attempt.get("credential_material_copied") is not False
        or attempt.get("exact_provider_charge_available") is not False
    ):
        raise PreflightBuildError("ATTEMPT_08_BOUNDARY_INVALID")
    entries = attempt.get("entries")
    if (
        not isinstance(entries, list)
        or attempt.get("entry_count") != len(entries)
        or digest(entries) != attempt.get("evidence_set_sha256")
    ):
        raise PreflightBuildError("ATTEMPT_08_EVIDENCE_SET_INVALID")
    by_classification: dict[str, Mapping[str, Any]] = {}
    for row in entries:
        if not isinstance(row, dict) or not isinstance(row.get("classification"), str):
            raise PreflightBuildError("ATTEMPT_08_EVIDENCE_INVALID")
        classification = row["classification"]
        if classification in by_classification:
            raise PreflightBuildError("ATTEMPT_08_EVIDENCE_DUPLICATE")
        by_classification[classification] = row
    required = {
        "summary_receipt",
        "preflight_packet",
        "preflight_bindings",
        "runtime_commands",
        "final_state",
        "final_evidence_archive",
        "final_evidence_sidecar",
        "supervisor_log",
        "lifecycle_log",
        "provider_exact_absence",
        "provider_campaign_absence",
    }
    if set(by_classification) != required:
        raise PreflightBuildError("ATTEMPT_08_EVIDENCE_CLASSIFICATION_INVALID")

    def artifact(classification: str) -> Path:
        return _resolve_artifact(
            root, manifest_path, str(by_classification[classification]["path"])
        )

    final_state = _read_json(artifact("final_state"), "ATTEMPT_08_FINAL_STATE")
    if not isinstance(final_state, dict) or any(
        value is not None for key, value in final_state.items() if key != "version"
    ):
        raise PreflightBuildError("ATTEMPT_08_FINAL_STATE_INVALID")
    exact_absence = _read_json(
        artifact("provider_exact_absence"), "ATTEMPT_08_PROVIDER_GET"
    )
    if (
        not isinstance(exact_absence, dict)
        or exact_absence.get("returncode") != 1
        or exact_absence.get("stdout") != ""
        or not isinstance(exact_absence.get("stderr"), str)
        or not _runpodctl_v272_not_found(exact_absence["stderr"])
    ):
        raise PreflightBuildError("ATTEMPT_08_EXACT_ABSENCE_INVALID")
    campaign_absence = _read_json(
        artifact("provider_campaign_absence"), "ATTEMPT_08_PROVIDER_LIST"
    )
    try:
        inventory = json.loads(campaign_absence.get("stdout", ""))
    except (AttributeError, json.JSONDecodeError) as exc:
        raise PreflightBuildError("ATTEMPT_08_CAMPAIGN_ABSENCE_INVALID") from exc
    if (
        campaign_absence.get("returncode") != 0
        or campaign_absence.get("stderr") != ""
        or not isinstance(inventory, list)
        or any(
            row.get("id") == attempt["pod_id"]
            or row.get("name") == attempt["pod_name"]
            or str(row.get("name", "")).startswith(attempt["campaign_id"])
            for row in inventory
            if isinstance(row, dict)
        )
    ):
        raise PreflightBuildError("ATTEMPT_08_CAMPAIGN_ABSENCE_INVALID")
    seconds = attempt.get("active_seconds_upper")
    rate = attempt.get("active_rate_usd_hour_upper")
    cost = attempt.get("attempt_cost_usd_upper")
    if (
        isinstance(seconds, bool)
        or not isinstance(seconds, int)
        or seconds <= 0
        or seconds > 3_600
        or not isinstance(rate, (int, float))
        or isinstance(rate, bool)
        or not isinstance(cost, (int, float))
        or isinstance(cost, bool)
        or float(rate) > float(contract["runpod"]["active_rate_usd_hour_max"])
        or abs(float(cost) - seconds / 3_600 * float(rate)) > 1e-12
    ):
        raise PreflightBuildError("ATTEMPT_08_COST_INVALID")
    return float(cost)


def _symbol_bindings(relative: str, text: str) -> dict[str, Any]:
    """Bind review-relevant top-level Python spans without exporting bodies."""
    if not relative.endswith(".py"):
        return {"symbols": [], "symbol_set_sha256": digest([])}
    try:
        tree = ast.parse(text, filename=relative)
    except SyntaxError as exc:
        raise PreflightBuildError("SOURCE_PARSE_FAILED:" + relative) from exc
    lines = text.splitlines(keepends=True)
    rows: list[dict[str, Any]] = []
    for node in sorted(
        (
            candidate
            for candidate in ast.walk(tree)
            if isinstance(
                candidate, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            )
        ),
        key=lambda candidate: (candidate.lineno, candidate.col_offset, candidate.name),
    ):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        end_line = getattr(node, "end_lineno", None)
        if not isinstance(end_line, int) or node.lineno < 1 or end_line < node.lineno:
            raise PreflightBuildError("SOURCE_SYMBOL_RANGE_INVALID:" + relative)
        raw = "".join(lines[node.lineno - 1 : end_line]).encode("utf-8")
        rows.append(
            {
                "end_line": end_line,
                "kind": "class" if isinstance(node, ast.ClassDef) else "function",
                "name": node.name,
                "sha256": digest(raw),
                "start_line": node.lineno,
            }
        )
    return {"symbols": rows, "symbol_set_sha256": digest(rows)}


def _checklist_bindings(
    sources_by_path: Mapping[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    expected_ids = [f"R8-{index:02d}" for index in range(1, 24)]
    observed_ids = [row[0] for row in CHECKLIST_EVIDENCE]
    if observed_ids != expected_ids or set(CHECKLIST_REQUIREMENTS) != set(expected_ids):
        raise PreflightBuildError("CHECKLIST_ID_COVERAGE_INVALID")

    def bind_reference(path: str, symbol: str) -> dict[str, Any]:
        source = sources_by_path.get(path)
        if source is None:
            raise PreflightBuildError("CHECKLIST_SOURCE_MISSING:" + path)
        matches = [row for row in source["symbols"] if row["name"] == symbol]
        if len(matches) != 1:
            raise PreflightBuildError(
                "CHECKLIST_SYMBOL_AMBIGUOUS_OR_MISSING:" + path + ":" + symbol
            )
        match = matches[0]
        return {
            "path": path,
            "symbol": symbol,
            "start_line": match["start_line"],
            "end_line": match["end_line"],
            "sha256": match["sha256"],
        }

    result: list[dict[str, Any]] = []
    for gate_id, state, implementation, tests, pointers in CHECKLIST_EVIDENCE:
        if state not in {
            "LOCAL_BOUND",
            "LOCAL_GREEN",
            "REMOTE_GATE",
            "PROCESS_GATE",
            "PRECREATE_RECHECK",
        }:
            raise PreflightBuildError("CHECKLIST_GATE_STATE_INVALID:" + gate_id)
        result.append(
            {
                "id": gate_id,
                "requirement": CHECKLIST_REQUIREMENTS[gate_id],
                "gate_state": state,
                "implementation_symbols": [
                    bind_reference(path, symbol) for path, symbol in implementation
                ],
                "mechanical_tests": [
                    bind_reference(path, symbol) for path, symbol in tests
                ],
                "binding_pointers": list(pointers),
            }
        )
    return result


def _write_exclusive(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except Exception:
        path.unlink(missing_ok=True)
        raise


def build(config: BuildConfig, *, now: datetime | None = None) -> dict[str, Any]:
    root = config.root.resolve()
    if config.runtime_dir.is_symlink():
        raise PreflightBuildError("RUNTIME_INVALID")
    runtime = _within(config.runtime_dir, root, "RUNTIME_OUTSIDE_ROOT")
    if not runtime.is_dir() or runtime.is_symlink():
        raise PreflightBuildError("RUNTIME_INVALID")
    for path in (
        config.active_inventory_json,
        config.gpu_inventory_json,
        config.bundle_archive,
        config.bundle_receipt_json,
        config.bundle_manifest_json,
        config.local_test_manifest_json,
        config.prior_attempt_history_manifest_json,
        config.attempt_08_manifest_json,
    ):
        _within(path, runtime, "RUNTIME_INPUT_OUTSIDE_RUNTIME")
    for path in (config.output_packet, config.output_bindings):
        _within(path, root, "OUTPUT_OUTSIDE_ROOT")
        if path.exists():
            raise PreflightBuildError("OUTPUT_EXISTS")
    if config.output_packet.name != "PDH_3_SCALE_RUNPOD_PREFLIGHT_PACKET_R8.md" or config.output_bindings.name != "PDH_3_SCALE_RUNPOD_PREFLIGHT_BINDINGS_R8.json":
        raise PreflightBuildError("R8_OUTPUT_NAME_REQUIRED")

    if tuple(config.sources) != tuple(sorted(set(config.sources))):
        raise PreflightBuildError("SOURCE_LIST_NOT_CANONICAL")
    if tuple(config.sources) != MANDATORY_SOURCES:
        raise PreflightBuildError("MANDATORY_SOURCE_SET_MISMATCH")
    sources: list[dict[str, Any]] = []
    for relative in config.sources:
        binding, text = _read_source(root, relative)
        sources.append({**binding, **_symbol_bindings(relative, text)})
    sources_by_path = {row["path"]: row for row in sources}
    disclosure = sources_by_path["PDH_3_R8_VALIDATION_BOUNDARY_DISCLOSURE.md"]
    source_set_sha256 = digest(sources)
    checklist_bindings = _checklist_bindings(sources_by_path)

    module = _load_contract(root)
    contract = module.production_contract()
    schedule = module.expected_schedule()
    if schedule.get("checkpoints") != contract["workload"]["checkpoints"] or schedule.get("verifier_executions") != 9_976 or schedule.get("fault_count") != 24:
        raise PreflightBuildError("CONTRACT_SCHEDULE_INVALID")
    observed_now = now or datetime.now(timezone.utc)
    lifecycle = _validate_times(config, contract, observed_now)

    authorization = _authorization_binding(config.authorization_receipt, root, contract)
    _require_hex64(config.runpodctl_sha256, "RUNPODCTL_SHA256_INVALID")
    runpodctl = _regular_file(config.runpodctl_path, "RUNPODCTL_MISSING")
    if digest(runpodctl.read_bytes()) != config.runpodctl_sha256:
        raise PreflightBuildError("RUNPODCTL_HASH_MISMATCH")
    if not config.runpodctl_version.strip() or len(config.runpodctl_version) > 128:
        raise PreflightBuildError("RUNPODCTL_VERSION_INVALID")
    runpodctl_display = runpodctl.as_posix()
    _assert_sanitized(runpodctl_display, "RUNPODCTL_PATH_UNSAFE")
    identity = _validate_identity(config.campaign_id, config.pod_name)
    active = _validate_active_inventory(
        _read_json(config.active_inventory_json, "ACTIVE_INVENTORY"),
        root=root,
        receipt_path=config.active_inventory_json,
        now=observed_now,
        runpodctl_display=runpodctl_display,
        runpodctl_version=config.runpodctl_version,
        runpodctl_sha256=config.runpodctl_sha256,
        campaign_id=config.campaign_id,
    )
    local_manifest, local_files, local_binding = _verify_manifest(
        config.local_test_manifest_json, root, "LOCAL_TEST"
    )
    if local_manifest.get("status") != "GREEN" or local_manifest.get("reduced_scale") is not True:
        raise PreflightBuildError("LOCAL_TEST_MANIFEST_NOT_GREEN_REDUCED")
    isolated_contract = local_manifest.get("isolated_smoke_contract")
    isolated_result = local_manifest.get("isolated_smoke_observed_result")
    if (
        not isinstance(isolated_contract, dict)
        or not isinstance(isolated_result, dict)
        or isolated_contract.get("fresh_generated_root_required") is not True
        or isolated_contract.get("isolated_home_required") is not True
        or isolated_contract.get("diagnostic_reporting_disabled_required") is not True
        or isolated_result.get("status") != "GREEN"
        or isolated_result.get("synthetic_only") is not True
        or isolated_result.get("credentials_used") is not False
        or isolated_result.get("external_cloud_calls") != 0
        or isolated_result.get("generated_root_removed") is not True
        or isolated_result.get("nodes_stopped") is not True
        or isolated_result.get("ports_closed") is not True
        or isolated_result.get("open_ports") != []
    ):
        raise PreflightBuildError("ISOLATED_LOCAL_SMOKE_EVIDENCE_INVALID")
    history, history_files, history_binding = _verify_manifest(
        config.prior_attempt_history_manifest_json,
        root,
        "PRIOR_HISTORY",
        hash_field="history_manifest_sha256",
        nested_key="history_manifest",
    )
    prior_cost = _history_cost_and_validate(
        history,
        contract,
        root,
        config.prior_attempt_history_manifest_json,
    )
    attempt_08, attempt_08_files, attempt_08_binding = _verify_manifest(
        config.attempt_08_manifest_json,
        root,
        "ATTEMPT_08",
    )
    prior_cost += _attempt_08_cost_and_validate(
        attempt_08,
        contract,
        root,
        config.attempt_08_manifest_json,
    )
    offer = _validate_gpu_inventory(
        _read_json(config.gpu_inventory_json, "GPU_INVENTORY"),
        root=root,
        receipt_path=config.gpu_inventory_json,
        now=observed_now,
        runpodctl_display=runpodctl_display,
        runpodctl_version=config.runpodctl_version,
        runpodctl_sha256=config.runpodctl_sha256,
        contract=contract,
        maximum_paid_seconds=lifecycle["maximum_paid_seconds"],
        prior_cost=prior_cost,
    )

    bundle, bundle_manifest, launch = _bundle_bindings(
        config, root, sources_by_path, history, module
    )
    commands = _command_bindings(
        config, contract, launch, sources_by_path, runpodctl_display
    )
    preflight = {
        "epochs": contract["workload"]["remote_preflight_epochs"],
        "seconds_per_epoch": PREFLIGHT_EPOCH_SECONDS,
        "concurrency": contract["workload"]["remote_preflight_concurrency"],
        "faults": contract["workload"]["remote_preflight_faults"],
        "trace_projection_limit_bytes": contract["thresholds"][
            "trace_preflight_projected_bytes"
        ],
        "trace_projection_fraction_of_cap": 0.80,
        "official_clock_starts_only_after_green_and_control_reset": True,
    }
    if (
        preflight["epochs"] != 3
        or preflight["seconds_per_epoch"] != 300
        or preflight["concurrency"] != 500
        or preflight["faults"] != 3
        or preflight["trace_projection_limit_bytes"]
        != int(contract["thresholds"]["trace_bytes"] * 0.80)
    ):
        raise PreflightBuildError("PREMEASUREMENT_CONTRACT_INVALID")

    bindings_body: dict[str, Any] = {
        "version": BINDINGS_VERSION,
        "revision": REVISION,
        "contract": contract,
        "schedule": schedule,
        "source_files": sources,
        "source_set_sha256": source_set_sha256,
        "validation_boundary_disclosure": disclosure,
        "authorization": authorization,
        "bundle": bundle,
        "identity": identity,
        "commands": commands,
        "local_test_manifest": local_binding,
        "prior_attempt_history_manifest": history_binding,
        "prior_attempt_artifacts_verified": len(history_files),
        "attempt_08_manifest": attempt_08_binding,
        "attempt_08_artifacts_verified": len(attempt_08_files),
        "local_test_artifacts_verified": len(local_files),
        "provider": {
            "active_inventory_receipt": active,
            "selected_offer": offer,
            "image": contract["runpod"]["image"],
            "ports": contract["runpod"]["ports"],
            "container_disk_gb": contract["runpod"]["container_disk_gb"],
            "volume_gb": contract["runpod"]["volume_gb"],
            "network_volume": contract["runpod"]["network_volume"],
        },
        "runpodctl": {
            "path": runpodctl_display,
            "version": config.runpodctl_version,
            "sha256": config.runpodctl_sha256,
        },
        "lifecycle": lifecycle,
        "premeasurement": preflight,
        "terminal_states": list(TERMINAL_STATES),
        "checklist": checklist_bindings,
        "limitations": [
            "REDUCED_TESTS_ARE_NOT_TARGET_SCALE_PROOF",
            "AUDIT_SESSION_ZERO_HOME_MUTATION_NOT_CLAIMED",
            "AUDIT_SESSION_ZERO_EGRESS_NOT_CLAIMED",
            "CLEAN_EVIDENCE_REQUIRES_FRESH_ISOLATED_SMOKE",
            "PAID_WORKER_RESULT_AND_TEARDOWN_DO_NOT_YET_EXIST",
            "PREFLIGHT_GREEN_AUTHORIZES_CREATION_ONLY",
        ],
    }
    bindings = {
        **bindings_body,
        "bindings_sha256": digest(bindings_body),
    }
    bindings_raw = canonical(bindings)

    checklist_text = "\n".join(
        f"{row['id']}. **{row['gate_state']}** — {row['requirement']}"
        for row in checklist_bindings
    )
    packet = f"""# PDH-3 Production-Shaped Scale Relaunch Preflight Packet R8

## Independent judge task

Review this one sanitized, byte-exact packet as a non-authoring preflight
judge. Do not write code, invoke tools, request credentials, launch a worker,
or infer future evidence. GLM and AGY must receive these identical packet bytes.

This is a **pre-creation readiness review**, not the post-campaign result gate.
Do not return NOT_GREEN solely because R8-08, R8-10, the 24-hour result, and
provider teardown evidence do not yet exist: those observations are impossible
before worker creation and are deliberately fail-closed worker-local gates.
Judge whether the bound implementation, local evidence, provider envelope, and
kill lines are sufficient to authorize creation. A GREEN here means
`RELAUNCH_READY`; it does not mean the remote campaign passed.

Return one JSON object:

```json
{{"verdict":"GREEN|NOT_GREEN|BLOCKED","freshness_and_hashes":"GREEN|NOT_GREEN","setup_and_premeasurement":"GREEN|NOT_GREEN","measured_schedule_and_evidence":"GREEN|NOT_GREEN","provider_cost_and_lifecycle":"GREEN|NOT_GREEN","credential_and_private_data_boundary":"GREEN|NOT_GREEN","blockers":[],"limitations":[]}}
```

GREEN is valid only when every named dimension is GREEN and blockers is empty.
This preflight can authorize one creation envelope; it cannot prove the future
24-hour result, provider teardown, or final evidence review.

## Frozen authority

- packet version: `{PACKET_VERSION}`
- bindings SHA-256: `{bindings['bindings_sha256']}`
- product candidate: `{contract['product_candidate']}`
- plan SHA-256: `{contract['plan_sha256']}`
- contract SHA-256: `{contract['contract_sha256']}`
- authorization SHA-256: `{authorization['sha256']}`
- transfer archive SHA-256: `{bundle['archive_sha256']}`
- immutable campaign ID: `{identity['campaign_id']}`
- exact provider Pod name: `{identity['pod_name']}`
- active inventory receipt SHA-256: `{active['receipt_sha256']}`
- active matching RunPod inventory: `[]`

R7 and Attempts 01–07 remain immutable historical evidence. This packet does
not revise their outcomes or reuse their expired lifecycle timestamps.

## Stated goal and kill line

Goal: make one honest 24-hour production-shaped campaign succeed on the frozen
candidate after a target-cardinality setup and exact-shape premeasurement gate.

Kill line: stop and delete on any stale or mixed hash, ambiguous SQL outcome,
setup/epoch deadline overrun, cardinality/index/query-target mismatch, lost
acknowledgement or replay state, missing raw verifier evidence, trace projection
overflow, process/resource leak, external destination, provider mismatch,
credential/private-data exposure, archive/transport ambiguity, or unproven
exact-ID teardown. No failure may be relabeled GREEN.

## Exact provider, cost, and lifecycle binding

```json
{canonical(bindings['provider']).decode('utf-8')}
```

- launch window: `{lifecycle['start']}` through `{lifecycle['end']}`
- provider stop-after: `{lifecycle['stop_after']}` / epoch `{lifecycle['stop_epoch']}`
- provider terminate-after: `{lifecycle['terminate_after']}` / epoch `{lifecycle['terminate_epoch']}`
- maximum paid lifetime: `{lifecycle['maximum_paid_seconds']}` seconds
- prior known plus conservatively unreconciled ceiling: `${offer['prior_cost_ceiling_usd']:.6f}`
- maximum relaunch projection: `${offer['projected_relaunch_cost_usd']:.6f}`
- aggregate bounded projection: `${offer['aggregate_cost_ceiling_usd']:.6f}`
- RunPodCTL: `{runpodctl_display}` · `{config.runpodctl_version}` · `{config.runpodctl_sha256}`

The returned worker must match the selected Secure Cloud L40S offer and the
contract mechanically: one 48-GiB L40S, 16–32 vCPU inclusive, 94–188 GiB RAM
inclusive, the exact image, 250-GiB disposable disk, SSH-only port exposure,
zero persistent/network volume, and both rate ceilings. Failed pre-workload
attempts are sequential; every extant worker is deleted and proven absent
before another creation. Once upload or measured execution makes replacement
unsafe under the frozen law, the campaign fails closed.

## Exact no-shell launch and control-plane wiring

```json
{canonical(commands).decode('utf-8')}
```

`instantiate_runtime_commands()` in the hash-bound packet-builder source is
the only declared runtime completion path. It accepts exactly the final packet
SHA-256 and provider-returned Pod ID, substitutes only those two declared
placeholders, rejects every residual placeholder, verifies the traced child,
packet environment, guard identity, and supervisor hashes, and returns concrete
argv/environment structures plus canonical hashes. All commands are executed as
argv; shell interpolation is forbidden. The controller child command is already
fully concrete and its SHA-256 is the exact `--trace-command-sha256` supplied to
the supervisor after instantiation.

## Exact setup and premeasurement gate

The selected worker first performs the complete target setup inside one shared
5,400-second monotonic deadline: 500,000 tasks, 5,000,000 events, 1,000,000
receipts, and 250,000 task-bound vectors. Seed operations resolve uncertain
client timeouts to ZERO, EXACT, or MISMATCH and block MISMATCH. Index recreation
must verify cardinality, visible metadata, and forced-index queryability. An
asynchronous build additionally binds the exact succeeded 100-percent job; a
synchronous build records `SYNCHRONOUS_DDL_NO_JOB` rather than inventing a job.
Both modes leave teardown time reserved.

Before the official 24-hour clock, the same worker must run exactly three
300-second epochs at concurrency 500 with three rotating genuine node faults.
It preserves those receipts; verifies query targets, control-state durability,
three live nodes, RSS, descriptors, processes, disk, database, evidence, and
trace slope; and projects the trace across 24 hours. The projection must be no
greater than `{preflight['trace_projection_limit_bytes']}` bytes—80 percent of
the `{contract['thresholds']['trace_bytes']}`-byte cap. The controller then
resets and proves all premeasurement control tables empty. Only that GREEN
receipt and clean reset may start the official measured clock.

## Exact 24-hour schedule and retained evidence

```json
{canonical(schedule).decode('utf-8')}
```

There are exactly 288 shared-deadline five-minute epochs, 232 verifier batches,
9,976 verifier executions, and 24 rotating SIGKILL/restart/reconciliation
cycles. All 9,976 distinct raw verifier receipts, their batch manifests,
aggregate files, querybench outputs, histograms, checkpoint receipts, fault
receipts, control-state proofs, and hash links remain in retrieved evidence.
A hash that points to a deleted temporary file is not evidence.

The authoritative GREEN result is written only after the database and local
cluster are torn down. The host-side supervisor can emit only one of:
`{', '.join(TERMINAL_STATES)}`. Retrieval alone is not success; partial archive,
absent result, transport failure, or unproven deletion is BLOCKED. A completed
remote command remains `GREEN_PENDING_FINAL_GATE` until exact-ID deletion,
empty matching active inventory, local hash verification, and final independent
same-hash review pass.

The host supervisor invocation must receive the exact final packet SHA-256,
the SHA-256 of `post-dogfood/run_pdh3_traced.py`, and the canonical SHA-256 of
the concrete child command substituted from the bundle launch template. Any
missing or mismatched `--packet-sha256`, `--trace-tool-sha256`, or
`--trace-command-sha256` value is terminally blocked.

## Relaunch checklist

{checklist_text}

`LOCAL_BOUND` and `LOCAL_GREEN` refer only to evidence already present in this
packet. `REMOTE_GATE`, `PROCESS_GATE`, and `PRECREATE_RECHECK` remain open and
cannot be converted into evidence by preflight prose. Target-scale setup, the
three remote premeasurement epochs, the 24-hour result, and provider teardown
remain OPEN until the selected worker produces and returns those receipts.

## Evidence summaries and prior failures

### Validation-boundary disclosure

The hash-bound disclosure
`PDH_3_R8_VALIDATION_BOUNDARY_DISCLOSURE.md` is bound at SHA-256
`{disclosure['sha256']}`. An excluded exploratory `cockroach demo` invocation
may have refreshed metadata under `~/.cockroach-demo` and may have attempted
diagnostic telemetry. Therefore this packet does **not** claim the entire audit
session had zero HOME mutation or zero egress.

The required clean candidate smoke was subsequently completed and is directly
bound in the local-test manifest below. Its frozen contract SHA-256 is
`{isolated_contract['packet']['sha256']}` and requires an isolated HOME,
disabled diagnostic reporting, and a fresh generated root. The observed result
is GREEN, synthetic and credential-free, recorded zero external cloud calls,
ran `{isolated_result['measured_seconds']}` measured seconds on
`{isolated_result['cluster_topology']}`, stopped all nodes, removed the generated
root, and proved zero open ports. This reduced smoke is local defect evidence,
not target-scale or RunPod evidence.

### Local-test manifest

```json
{canonical(local_manifest).decode('utf-8')}
```

### Attempts 01–07 history manifest

```json
{canonical(history).decode('utf-8')}
```

### Failed Attempt 08 manifest

Attempt 08 is preserved as a premeasurement failure. Its bundle was uploaded,
the measured clock never began, and its frozen teardown proof remained blocked
even though the provider resource was deleted. The replacement cost projection
includes its conservative upper-bound interval.

```json
{canonical(attempt_08).decode('utf-8')}
```

### Transfer-bundle receipt and manifest

```json
{canonical(bundle).decode('utf-8')}
```

```json
{canonical(bundle_manifest).decode('utf-8')}
```

Reduced and mocked tests are necessary defect detectors. They do **not** prove
target-cardinality setup, exact-shape performance, 24-hour trace growth, or
production-scale reliability. Those claims remain deliberately OPEN until the
remote premeasurement and measured campaign produce direct evidence.

## Canonical bindings

```json
{bindings_raw.decode('utf-8')}
```

## Hash-bound load-bearing source manifest

The packet does not copy full source bodies into an external judge prompt.
Every source is instead bound once, inside `source_files` in the canonical
bindings, by complete-file SHA-256 and byte count; each Python function/class
is additionally bound by exact line range and segment SHA-256. The remote
subset is independently bound inside the transfer archive, while the host-only
subset remains outside that archive. This avoids credential-shaped test
literals and keeps the identical GLM/AGY packet below the strict 262,144-byte
transport ceiling without changing executable bytes.

- source count: `{len(sources)}`
- canonical source-set SHA-256: `{source_set_sha256}`
- exact manifest location: `Canonical bindings -> source_files`
"""
    packet_raw = packet.encode("utf-8")
    _assert_sanitized(packet, "PACKET_UNSAFE")
    _assert_sanitized(bindings_raw.decode("utf-8"), "BINDINGS_UNSAFE")
    _assert_external_judge_safe(packet, "PACKET_EXTERNAL_JUDGE_UNSAFE")
    if len(packet_raw) > PACKET_BYTES_MAX:
        raise PreflightBuildError("PACKET_SIZE_OVERFLOW")

    _write_exclusive(config.output_bindings, bindings_raw)
    try:
        _write_exclusive(config.output_packet, packet_raw)
    except Exception:
        config.output_bindings.unlink(missing_ok=True)
        raise
    return {
        "revision": REVISION,
        "packet": config.output_packet.name,
        "packet_bytes": len(packet_raw),
        "packet_sha256": digest(packet_raw),
        "bindings": config.output_bindings.name,
        "bindings_bytes": len(bindings_raw),
        "bindings_sha256": bindings["bindings_sha256"],
        "sources": len(sources),
        "local_artifacts_verified": len(local_files),
        "prior_attempt_artifacts_verified": len(history_files),
        "attempt_08_artifacts_verified": len(attempt_08_files),
    }


def parse_arguments(argv: Iterable[str] | None = None) -> BuildConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--pod-name", required=True)
    parser.add_argument("--launch-window-start", required=True)
    parser.add_argument("--launch-window-end", required=True)
    parser.add_argument("--stop-after", required=True)
    parser.add_argument("--terminate-after", required=True)
    parser.add_argument("--stop-epoch", type=int, required=True)
    parser.add_argument("--terminate-epoch", type=int, required=True)
    parser.add_argument("--active-inventory-json", type=Path, required=True)
    parser.add_argument("--gpu-inventory-json", type=Path, required=True)
    parser.add_argument("--bundle-archive", type=Path, required=True)
    parser.add_argument("--bundle-receipt-json", type=Path, required=True)
    parser.add_argument("--bundle-manifest-json", type=Path, required=True)
    parser.add_argument("--local-test-manifest-json", type=Path, required=True)
    parser.add_argument("--prior-attempt-history-manifest-json", type=Path, required=True)
    parser.add_argument("--attempt-08-manifest-json", type=Path, required=True)
    parser.add_argument("--authorization-receipt", type=Path, required=True)
    parser.add_argument("--runpodctl-path", type=Path, required=True)
    parser.add_argument("--runpodctl-version", required=True)
    parser.add_argument("--runpodctl-sha256", required=True)
    parser.add_argument("--source", action="append", dest="sources", required=True)
    parser.add_argument("--output-packet", type=Path, required=True)
    parser.add_argument("--output-bindings", type=Path, required=True)
    values = parser.parse_args(argv)
    parsed = vars(values)
    parsed["sources"] = tuple(parsed["sources"])
    return BuildConfig(**parsed)


def main(argv: Iterable[str] | None = None) -> int:
    try:
        result = build(parse_arguments(argv))
    except PreflightBuildError as exc:
        print(canonical({"status": "BLOCKED", "blocker": str(exc)}).decode("utf-8"))
        return 2
    print(canonical({"status": "GREEN", **result}).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
