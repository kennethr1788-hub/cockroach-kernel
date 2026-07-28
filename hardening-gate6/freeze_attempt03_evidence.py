#!/usr/bin/env python3
"""Validate and freeze the bounded Gate 6 R3 attempt-03 evidence set."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ATTEMPT = ROOT / ".hardening-runtime/gate6-r3-agy/attempt-03"
RETRIEVED = ATTEMPT / "retrieved-evidence"
CAMPAIGN = RETRIEVED / "measured-parent/campaign"
CANDIDATE = "8718fbecc2b145ff36ce8c3ed655e92b5906aeab"
CAMPAIGN_ID = "ck-gate6-20260727-run1-r3"
ARCHIVE_SHA256 = "1ed09238a554b6ddb333d8adfafd554a55205f9c45fa5b2487a03645367814e5"
PAYLOAD_SHA256 = "c3958a5847f1cd8d35bb66c89700d0412eda72c5c28bbda41e67cf6cef44403a"
PAYLOAD_TREE_SHA256 = "6bb049a13904dc2d7b447d9193cf1574f83dd2d3ed622f347d8fd6e3913a95a3"

COPIES = {
    "HARDENING_GATE6_R3_AGGREGATE.json": CAMPAIGN / "aggregate.json",
    "HARDENING_GATE6_R3_CHECKPOINTS.ndjson": CAMPAIGN / "checkpoints.ndjson",
    "HARDENING_GATE6_R3_REMOTE_EVIDENCE_MANIFEST.json": CAMPAIGN / "evidence-manifest.json",
    "HARDENING_GATE6_R3_ISOLATION.json": RETRIEVED / "isolation.json",
    "HARDENING_GATE6_R3_SMOKE_RECEIPT.json": RETRIEVED / "smoke-r3/receipt.json",
    "HARDENING_GATE6_R3_SMOKE_ISOLATION.json": RETRIEVED / "smoke-r3/isolation.json",
    "HARDENING_GATE6_R3_LIFECYCLE.ndjson": ATTEMPT / "lifecycle.ndjson",
}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def atomic_write(path: Path, raw: bytes) -> None:
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


def load_canonical(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or canonical(value) != raw:
        raise SystemExit(f"non-canonical JSON: {path}")
    return value


def verify_embedded_hash(record: dict[str, object], field: str) -> None:
    claimed = record.get(field)
    body = {key: value for key, value in record.items() if key != field}
    if claimed != sha256(canonical(body)):
        raise SystemExit(f"{field} mismatch")


def main() -> int:
    aggregate = load_canonical(CAMPAIGN / "aggregate.json")
    manifest = load_canonical(CAMPAIGN / "evidence-manifest.json")
    isolation = load_canonical(RETRIEVED / "isolation.json")
    smoke = load_canonical(RETRIEVED / "smoke-r3/receipt.json")
    smoke_isolation = load_canonical(RETRIEVED / "smoke-r3/isolation.json")
    checkpoints = [json.loads(line) for line in (CAMPAIGN / "checkpoints.ndjson").read_text().splitlines()]
    lifecycle = [json.loads(line) for line in (ATTEMPT / "lifecycle.ndjson").read_text().splitlines()]

    verify_embedded_hash(aggregate, "aggregate_sha256")
    verify_embedded_hash(manifest, "manifest_sha256")
    verify_embedded_hash(isolation, "attestation_sha256")
    verify_embedded_hash(smoke, "receipt_sha256")
    verify_embedded_hash(smoke_isolation, "attestation_sha256")

    if aggregate.get("status") != "GREEN":
        raise SystemExit("aggregate not GREEN")
    if aggregate.get("campaign_id") != CAMPAIGN_ID or aggregate.get("candidate_commit") != CANDIDATE:
        raise SystemExit("aggregate identity mismatch")
    if aggregate.get("measured_executions") != 54 or aggregate.get("unique_combinations") != 54:
        raise SystemExit("aggregate count mismatch")
    if len(checkpoints) != 54:
        raise SystemExit("checkpoint count mismatch")
    if isolation != smoke_isolation:
        raise SystemExit("isolation attestation changed between canary/smoke/measurement")
    if isolation.get("network_socket_probe_result") != "DENIED_EPERM":
        raise SystemExit("network denial not proved")
    if lifecycle[-1].get("event") != "TEARDOWN_GREEN":
        raise SystemExit("lifecycle did not close GREEN")
    if lifecycle[-1].get("details") != {"campaign_active": [], "exact_id_absent": True}:
        raise SystemExit("teardown details mismatch")
    if (RETRIEVED / "measured.exit").read_text().strip() != "0":
        raise SystemExit("measured process exit mismatch")
    if (RETRIEVED / "measured.stderr").read_bytes() != b"":
        raise SystemExit("measured stderr not empty")
    if sha256((ATTEMPT / "gate6-evidence-r3-a03.tar.gz").read_bytes()) != ARCHIVE_SHA256:
        raise SystemExit("retrieved archive hash mismatch")

    manifest_by_path = {entry["path"]: entry for entry in manifest["files"]}
    rows: list[dict[str, object]] = []
    previous = "0" * 64
    for sequence, checkpoint in enumerate(checkpoints, start=1):
        if checkpoint.get("sequence") != sequence:
            raise SystemExit(f"checkpoint sequence mismatch: {sequence}")
        if checkpoint.get("previous_event_sha256") != previous:
            raise SystemExit(f"checkpoint chain mismatch: {sequence}")
        event_body = {key: value for key, value in checkpoint.items() if key != "event_sha256"}
        if checkpoint.get("event_sha256") != sha256(canonical(event_body)):
            raise SystemExit(f"checkpoint hash mismatch: {sequence}")
        previous = str(checkpoint["event_sha256"])

        candidates = sorted((CAMPAIGN / "receipts").glob(f"{sequence:03d}--*.json"))
        if len(candidates) != 1:
            raise SystemExit(f"receipt selection mismatch: {sequence}")
        receipt_path = candidates[0]
        relative = receipt_path.relative_to(CAMPAIGN).as_posix()
        raw = receipt_path.read_bytes()
        receipt = load_canonical(receipt_path)
        verify_embedded_hash(receipt, "receipt_sha256")
        entry = manifest_by_path.get(relative)
        if entry is None or entry.get("sha256") != sha256(raw) or entry.get("bytes") != len(raw):
            raise SystemExit(f"manifest binding mismatch: {relative}")
        if checkpoint.get("receipt_sha256") != receipt.get("receipt_sha256"):
            raise SystemExit(f"checkpoint receipt mismatch: {sequence}")
        if receipt.get("execution_order") not in {1, 2, 3}:
            raise SystemExit(f"receipt within-pair execution order mismatch: {sequence}")
        rows.append({
            "sequence": sequence,
            "within_pair_execution_order": receipt["execution_order"],
            "receipt_path": relative,
            "file_sha256": sha256(raw),
            "receipt_sha256": receipt["receipt_sha256"],
            "checkpoint_event_sha256": checkpoint["event_sha256"],
            "row_sha256": checkpoint["row_sha256"],
            "scenario_class": receipt["scenario_class"],
            "repetition": receipt["repetition"],
            "method": receipt["method"],
            "operation_status": receipt["operation_status"],
            "retained_units": receipt["declared_work_units_retained"],
            "total_units": receipt["declared_work_units_total"],
            "manifest_exact_match": receipt["manifest_exact_match"],
            "executable_continuation_pass": receipt["executable_continuation_pass"],
            "unsafe_acceptance": receipt["unsafe_acceptance"],
            "original_workspace_mutated_after_loss": receipt["original_workspace_mutated_after_loss"],
            "cleanup_pass": receipt["cleanup_pass"],
            "residue_bytes_after_teardown": receipt["residue_bytes_after_teardown"],
            "capture_overhead_ms": receipt["capture_overhead_ms"],
            "wall_clock_recovery_ms": receipt["wall_clock_recovery_ms"],
            "storage_bytes_pre_loss": receipt["storage_bytes_pre_loss"],
            "canonical_receipt_bytes": len(raw),
        })

    if previous != aggregate.get("final_checkpoint_sha256"):
        raise SystemExit("final checkpoint/aggregate mismatch")
    if len(manifest_by_path) != 56:
        raise SystemExit("evidence manifest file count mismatch")

    for output_name, source in COPIES.items():
        atomic_write(ROOT / output_name, source.read_bytes())

    index = {
        "version": "hardening-gate6-r3-evidence-index-v1",
        "status": "GREEN_CANDIDATE_PENDING_INDEPENDENT_FINAL_REVIEW",
        "candidate_commit": CANDIDATE,
        "campaign_id": CAMPAIGN_ID,
        "pod_id": "18hf13p5qu4pov",
        "pod_deleted": True,
        "campaign_active_inventory": [],
        "measured_exit_status": 0,
        "measured_stderr_bytes": 0,
        "measured_executions": 54,
        "unique_combinations": 54,
        "pair_count": aggregate["pair_count"],
        "cleanup_pass": aggregate["cleanup_pass"],
        "residue_bytes": aggregate["residue_bytes"],
        "unsafe_acceptance_count": aggregate["unsafe_acceptance_count"],
        "original_workspace_mutation_count": aggregate["original_workspace_mutation_count"],
        "payload_archive_sha256": PAYLOAD_SHA256,
        "payload_tree_sha256": PAYLOAD_TREE_SHA256,
        "remote_evidence_archive_sha256": ARCHIVE_SHA256,
        "aggregate_file_sha256": sha256((CAMPAIGN / "aggregate.json").read_bytes()),
        "aggregate_sha256": aggregate["aggregate_sha256"],
        "evidence_manifest_file_sha256": sha256((CAMPAIGN / "evidence-manifest.json").read_bytes()),
        "evidence_manifest_sha256": manifest["manifest_sha256"],
        "checkpoints_file_sha256": sha256((CAMPAIGN / "checkpoints.ndjson").read_bytes()),
        "final_checkpoint_sha256": aggregate["final_checkpoint_sha256"],
        "isolation_file_sha256": sha256((RETRIEVED / "isolation.json").read_bytes()),
        "isolation_attestation_sha256": isolation["attestation_sha256"],
        "smoke_receipt_file_sha256": sha256((RETRIEVED / "smoke-r3/receipt.json").read_bytes()),
        "smoke_receipt_sha256": smoke["receipt_sha256"],
        "lifecycle_file_sha256": sha256((ATTEMPT / "lifecycle.ndjson").read_bytes()),
        "lifecycle_final_event_sha256": lifecycle[-1]["event_hash"],
        "limitations": aggregate["limitations"],
        "billing": {
            "exact_provider_charge": None,
            "provider_billing_query_result": [],
            "rate_usd_per_hour": 0.06,
            "known_lifetime_seconds_max": 709.044,
            "bounded_compute_cost_usd_max": 0.0118174,
            "bounded_cost_at_active_rate_ceiling_usd_max": 0.0196956667,
            "classification": "PENDING_NOT_A_COMPLETION_BLOCKER_UNDER_CURRENT_OPERATOR_AUTHORIZATION",
        },
        "rows": rows,
    }
    atomic_write(ROOT / "HARDENING_GATE6_R3_MEASURED_EVIDENCE_INDEX.json", canonical(index))

    copies = {
        output: {"bytes": (ROOT / output).stat().st_size, "sha256": sha256((ROOT / output).read_bytes())}
        for output in COPIES
    }
    index_hash = sha256((ROOT / "HARDENING_GATE6_R3_MEASURED_EVIDENCE_INDEX.json").read_bytes())
    receipt = f"""# Hardening Gate 6 R3 — Attempt 03 Evidence Validation Receipt

- `STATUS`: `GREEN_CANDIDATE_PENDING_INDEPENDENT_FINAL_REVIEW`
- `CANDIDATE_COMMIT`: `{CANDIDATE}`
- `CAMPAIGN_ID`: `{CAMPAIGN_ID}`
- `MEASURED_EXECUTIONS`: `54`
- `UNIQUE_COMBINATIONS`: `54`
- `PAIR_COUNT`: `{aggregate['pair_count']}`
- `CANONICAL_RECEIPTS_VALID`: `{aggregate['canonical_receipts_valid']}`
- `CHECKPOINT_CHAIN_VALID`: `54_OF_54`
- `MANIFEST_FILE_BINDINGS_VALID`: `56_OF_56`
- `MEASURED_EXIT_STATUS`: `0`
- `MEASURED_STDERR_BYTES`: `0`
- `CLEANUP_PASS`: `{aggregate['cleanup_pass']}_OF_54`
- `RESIDUE_BYTES`: `{aggregate['residue_bytes']}`
- `UNSAFE_ACCEPTANCE_COUNT`: `{aggregate['unsafe_acceptance_count']}`
- `ORIGINAL_WORKSPACE_MUTATION_COUNT`: `{aggregate['original_workspace_mutation_count']}`
- `REMOTE_EVIDENCE_ARCHIVE_SHA256`: `{ARCHIVE_SHA256}`
- `AGGREGATE_SHA256`: `{aggregate['aggregate_sha256']}`
- `FINAL_CHECKPOINT_SHA256`: `{aggregate['final_checkpoint_sha256']}`
- `EVIDENCE_MANIFEST_SHA256`: `{manifest['manifest_sha256']}`
- `ISOLATION_ATTESTATION_SHA256`: `{isolation['attestation_sha256']}`
- `SMOKE_RECEIPT_SHA256`: `{smoke['receipt_sha256']}`
- `LIFECYCLE_FINAL_EVENT_SHA256`: `{lifecycle[-1]['event_hash']}`
- `MEASURED_EVIDENCE_INDEX_FILE_SHA256`: `{index_hash}`
- `TRACKED_EVIDENCE_COPIES`: `{json.dumps(copies, sort_keys=True, separators=(',', ':'))}`
- `FINAL_REVIEW`: `GLM 5.2 AND AGY REQUIRED ON ONE EXACT PACKET HASH`

The local validator recomputed every embedded receipt hash, every receipt file
hash, all 54 checkpoint event links, the aggregate hash, the evidence-manifest
hash, the isolation attestation hash, and the smoke receipt hash. It also bound
each receipt to both the remote evidence manifest and its corresponding
checkpoint. The final lifecycle event proves exact-ID absence and empty active
campaign inventory. These results remain synthetic paired comparative evidence,
not live AWS or population-scale evidence.
"""
    atomic_write(ROOT / "HARDENING_GATE6_R3_EVIDENCE_VALIDATION_RECEIPT.md", receipt.encode())
    print(f"index_sha256={index_hash}")
    print(f"aggregate_sha256={aggregate['aggregate_sha256']}")
    print(f"final_checkpoint_sha256={aggregate['final_checkpoint_sha256']}")
    print("status=GREEN_CANDIDATE_PENDING_INDEPENDENT_FINAL_REVIEW")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
