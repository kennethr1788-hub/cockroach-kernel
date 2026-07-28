#!/usr/bin/env python3
"""Reveal the sealed oracle only after all 84 observations are immutable."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


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


def load_canonical(path: Path) -> Any:
    raw = path.read_bytes()
    value = json.loads(raw)
    if canonical(value) != raw:
        raise ValueError("NON_CANONICAL_FILE")
    return value


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


def validate_oracle(path: Path, input_manifest_sha256: str) -> dict[str, Any]:
    oracle = load_canonical(path)
    required = {
        "version", "campaign_id", "candidate_commit", "input_manifest_sha256",
        "entries", "oracle_manifest_sha256",
    }
    if not isinstance(oracle, dict) or set(oracle) != required:
        raise ValueError("ORACLE_SCHEMA_INVALID")
    body = {key: value for key, value in oracle.items() if key != "oracle_manifest_sha256"}
    if oracle["oracle_manifest_sha256"] != digest(body):
        raise ValueError("ORACLE_HASH_INVALID")
    if oracle["input_manifest_sha256"] != input_manifest_sha256:
        raise ValueError("ORACLE_INPUT_BINDING_INVALID")
    if len(oracle["entries"]) != 84:
        raise ValueError("ORACLE_COUNT_INVALID")
    for entry in oracle["entries"]:
        entry_body = {key: value for key, value in entry.items() if key != "oracle_sha256"}
        if entry.get("oracle_sha256") != digest(entry_body):
            raise ValueError("ORACLE_ENTRY_HASH_INVALID")
    return oracle


def percentile(values: list[int], percentile_value: int) -> int:
    ordered = sorted(values)
    index = max(0, (len(ordered) * percentile_value + 99) // 100 - 1)
    return ordered[index]


def score_one(
    observation: dict[str, Any],
    oracle: dict[str, Any],
    cleanup: dict[str, Any],
    *,
    require_isolation: bool,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    observed = observation["observation"]
    if observed["observed_verdict"] != oracle["expected_verdict"]:
        reasons.append("VERDICT_MISMATCH")
    if observed["observed_reason"] != oracle["expected_reason"]:
        reasons.append("REASON_MISMATCH")
    if oracle["expected_verdict"] in {"REFUSE", "INVALID"} and observed["terminal_invocation_mutated"]:
        reasons.append("MUTATION_AFTER_REFUSAL_OR_INVALID")
    if observed["representations_unchanged"] is not True:
        reasons.append("SOURCE_REPRESENTATION_MUTATED")
    if oracle["expected_verdict"] == "PROMOTE":
        if observed["manifest_exact_match"] is not True:
            reasons.append("PROMOTED_MANIFEST_MISMATCH")
        if observed["acceptance_passed"] is not True:
            reasons.append("PROMOTED_ACCEPTANCE_FAILED")
    if cleanup.get("cleanup") != "GREEN" or cleanup.get("residue") is not False:
        reasons.append("TRIAL_CLEANUP_FAILED")
    if observation.get("oracle_loaded") is not False:
        reasons.append("ORACLE_RUNNER_BOUNDARY_VIOLATED")
    if observation.get("model_invoked") is not False:
        reasons.append("MODEL_INVOKED")
    if observation.get("non_loopback_connection_observed") is not False:
        reasons.append("UNDECLARED_EGRESS")
    if require_isolation and observation.get("network_denial_attestation_bound") is not True:
        reasons.append("NETWORK_DENIAL_ATTESTATION_MISSING")
    safety = {
        "MUTATION_AFTER_REFUSAL_OR_INVALID",
        "SOURCE_REPRESENTATION_MUTATED",
        "TRIAL_CLEANUP_FAILED",
        "ORACLE_RUNNER_BOUNDARY_VIOLATED",
        "UNDECLARED_EGRESS",
        "NETWORK_DENIAL_ATTESTATION_MISSING",
    }
    if any(reason in safety for reason in reasons):
        return "FAIL_SAFETY", reasons
    if reasons:
        return "FAIL_BEHAVIOR", reasons
    return "PASS", []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-root", required=True, type=Path)
    parser.add_argument("--oracle", required=True, type=Path)
    parser.add_argument("--input-manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--require-isolation", action="store_true")
    args = parser.parse_args()
    campaign_root = args.campaign_root.resolve()
    raw_manifest = load_canonical(campaign_root / "raw-campaign-manifest.json")
    raw_body = {key: value for key, value in raw_manifest.items() if key != "raw_manifest_sha256"}
    if raw_manifest.get("raw_manifest_sha256") != digest(raw_body):
        raise ValueError("RAW_MANIFEST_HASH_INVALID")
    if raw_manifest.get("raw_observation_count") != 84 or raw_manifest.get("scoring_performed") is not False:
        raise ValueError("RAW_CAMPAIGN_STATE_INVALID")
    input_manifest = load_canonical(args.input_manifest.resolve())
    input_body = {key: value for key, value in input_manifest.items() if key != "manifest_sha256"}
    if input_manifest.get("manifest_sha256") != digest(input_body):
        raise ValueError("INPUT_MANIFEST_HASH_INVALID")
    oracle = validate_oracle(args.oracle.resolve(), input_manifest["manifest_sha256"])
    oracle_by_id = {entry["slot_id"]: entry for entry in oracle["entries"]}
    if len(oracle_by_id) != 84:
        raise ValueError("DUPLICATE_ORACLE_SLOT")
    output = args.output_root.resolve()
    if output.exists():
        raise ValueError("SCORE_OUTPUT_EXISTS")
    receipts = output / "scored-receipts"
    receipts.mkdir(parents=True)
    observation_files = sorted((campaign_root / "raw-observations").glob("*.json"))
    cleanup_files = sorted((campaign_root / "unscored-receipts").glob("*.json"))
    if len(observation_files) != 84 or len(cleanup_files) != 84:
        raise ValueError("RAW_FILE_COUNT_INVALID")
    cleanup_by_id = {load_canonical(path)["slot_id"]: load_canonical(path) for path in cleanup_files}
    rows: list[dict[str, Any]] = []
    for path in observation_files:
        observation = load_canonical(path)
        slot_id = observation["slot_id"]
        expected = oracle_by_id.get(slot_id)
        cleanup = cleanup_by_id.get(slot_id)
        if expected is None or cleanup is None:
            raise ValueError("SLOT_BINDING_MISSING")
        if expected["input_sha256"] != observation["input_sha256"]:
            raise ValueError("ORACLE_OBSERVATION_BINDING_INVALID")
        classification, failures = score_one(
            observation, expected, cleanup, require_isolation=args.require_isolation
        )
        body = {
            "version": "hardening-gate7-scored-receipt-v1",
            "campaign_id": raw_manifest["campaign_id"],
            "candidate_commit": raw_manifest["candidate_commit"],
            "slot_id": slot_id,
            "execution_order": observation["execution_order"],
            "block": observation["block"],
            "topology": observation["topology"],
            "workflow": observation["workflow"],
            "boundary": observation["boundary"],
            "temporal": observation["temporal"],
            "input_sha256": observation["input_sha256"],
            "observation_sha256": digest(path.read_bytes()),
            "oracle_sha256": expected["oracle_sha256"],
            "expected_verdict": expected["expected_verdict"],
            "expected_reason": expected["expected_reason"],
            "observed_verdict": observation["observation"]["observed_verdict"],
            "observed_reason": observation["observation"]["observed_reason"],
            "terminal_classification": classification,
            "failures": failures,
            "elapsed_monotonic_ns": observation["elapsed_monotonic_ns"],
            "peak_rss_raw": observation["peak_rss_raw"],
            "cleanup": cleanup["cleanup"],
            "residue": cleanup["residue"],
            "manifest_exact_match": observation["observation"]["manifest_exact_match"],
            "acceptance_passed": observation["observation"]["acceptance_passed"],
            "terminal_invocation_mutated": observation["observation"]["terminal_invocation_mutated"],
            "authorized_prior_mutation": observation["observation"]["authorized_prior_mutation"],
        }
        receipt = dict(body, scored_receipt_sha256=digest(body))
        atomic_write(receipts / path.name, canonical(receipt))
        rows.append(receipt)
    rows.sort(key=lambda row: row["execution_order"])
    determinism: dict[str, set[tuple[str, str, str]]] = {}
    for row in rows:
        if row["block"] == "A_ORIGINAL_DETERMINISM":
            determinism.setdefault(row["expected_verdict"], set()).add((
                row["observed_verdict"], row["observed_reason"],
                load_canonical(observation_files[row["execution_order"] - 1])["observation"]["summary_sha256"],
            ))
    by_block: dict[str, dict[str, int]] = {}
    by_topology: dict[str, dict[str, int]] = {}
    by_workflow: dict[str, dict[str, int]] = {}
    for row in rows:
        for table, key in (
            (by_block, row["block"]),
            (by_topology, row["topology"]),
            (by_workflow, row["workflow"]),
        ):
            bucket = table.setdefault(key, {"PASS": 0, "FAIL_BEHAVIOR": 0, "FAIL_SAFETY": 0})
            bucket[row["terminal_classification"]] += 1
    latencies = [row["elapsed_monotonic_ns"] for row in rows]
    false_promotions = sum(
        row["expected_verdict"] != "PROMOTE" and row["observed_verdict"] == "PROMOTE"
        for row in rows
    )
    aggregate_body = {
        "version": "hardening-gate7-expanded-aggregate-v1",
        "campaign_id": raw_manifest["campaign_id"],
        "candidate_commit": raw_manifest["candidate_commit"],
        "packet_sha256": raw_manifest["packet_sha256"],
        "input_manifest_sha256": input_manifest["manifest_sha256"],
        "oracle_manifest_sha256": oracle["oracle_manifest_sha256"],
        "raw_manifest_sha256": raw_manifest["raw_manifest_sha256"],
        "scored_execution_count": len(rows),
        "pass_count": sum(row["terminal_classification"] == "PASS" for row in rows),
        "behavior_failure_count": sum(row["terminal_classification"] == "FAIL_BEHAVIOR" for row in rows),
        "safety_failure_count": sum(row["terminal_classification"] == "FAIL_SAFETY" for row in rows),
        "original_43_semantics_preserved": all(
            row["terminal_classification"] == "PASS" for row in rows
            if row["block"].startswith("A_")
        ),
        "all_case_slots_unique": len({row["slot_id"] for row in rows}) == 84,
        "false_promotions": false_promotions,
        "mutation_after_refusal_or_invalid": sum(
            row["expected_verdict"] in {"REFUSE", "INVALID"}
            and row["terminal_invocation_mutated"] for row in rows
        ),
        "correct_stable_reason_count": sum(
            row["expected_verdict"] == row["observed_verdict"]
            and row["expected_reason"] == row["observed_reason"] for row in rows
        ),
        "promoted_manifest_exact_match_count": sum(
            row["expected_verdict"] == "PROMOTE" and row["manifest_exact_match"] for row in rows
        ),
        "promoted_acceptance_count": sum(
            row["expected_verdict"] == "PROMOTE" and row["acceptance_passed"] for row in rows
        ),
        "expected_promotion_count": sum(row["expected_verdict"] == "PROMOTE" for row in rows),
        "representative_determinism": {
            verdict: len(values) == 1 for verdict, values in determinism.items()
        },
        "post_reveal_tuning_events": raw_manifest["post_reveal_tuning_events"],
        "cleanup_green_count": sum(row["cleanup"] == "GREEN" for row in rows),
        "residue_count": sum(bool(row["residue"]) for row in rows),
        "require_isolation": args.require_isolation,
        "by_block": by_block,
        "by_topology": by_topology,
        "by_workflow": by_workflow,
        "latency_ns": {
            "p50": percentile(latencies, 50),
            "p95": percentile(latencies, 95),
            "p99": percentile(latencies, 99),
            "max": max(latencies),
        },
        "limitations": [
            "COMMON_SYNTHETIC_GENERATOR",
            "COMMON_PRODUCT_IMPLEMENTATION",
            "NOT_STATISTICALLY_INDEPENDENT",
            "NOT_ARBITRARY_UNDELETE",
            "NOT_PUBLIC_USER_EVIDENCE",
        ],
    }
    aggregate_body["green"] = (
        aggregate_body["scored_execution_count"] == 84
        and aggregate_body["pass_count"] == 84
        and aggregate_body["behavior_failure_count"] == 0
        and aggregate_body["safety_failure_count"] == 0
        and aggregate_body["original_43_semantics_preserved"]
        and aggregate_body["all_case_slots_unique"]
        and aggregate_body["false_promotions"] == 0
        and aggregate_body["mutation_after_refusal_or_invalid"] == 0
        and aggregate_body["correct_stable_reason_count"] == 84
        and all(aggregate_body["representative_determinism"].get(verdict) for verdict in ("PROMOTE", "REFUSE", "INVALID"))
        and aggregate_body["cleanup_green_count"] == 84
        and aggregate_body["residue_count"] == 0
        and aggregate_body["post_reveal_tuning_events"] == 0
    )
    aggregate = dict(aggregate_body, aggregate_sha256=digest(aggregate_body))
    atomic_write(output / "aggregate.json", canonical(aggregate))
    manifest_body = {
        "version": "hardening-gate7-scored-evidence-manifest-v1",
        "campaign_id": raw_manifest["campaign_id"],
        "aggregate_sha256": aggregate["aggregate_sha256"],
        "files": {
            str(path.relative_to(output)): digest(path.read_bytes())
            for path in sorted(output.rglob("*.json"))
        },
    }
    manifest = dict(manifest_body, manifest_sha256=digest(manifest_body))
    atomic_write(output / "manifest.json", canonical(manifest))
    return 0 if aggregate["green"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
