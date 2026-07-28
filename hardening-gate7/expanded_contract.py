#!/usr/bin/env python3
"""Frozen Gate 7 R2 case-slot and oracle contract.

This module is generator/scorer authority. The measured runner must never import it.
It defines outcomes from the frozen product contract before any hidden seed exists.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


VERSION = "hardening-gate7-expanded-contract-v1"
CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
ORIGINAL_CANDIDATE = "8718fbecc2b145ff36ce8c3ed655e92b5906aeab"
MAX_FILE_BYTES = 65_536
MAX_AGGREGATE_BYTES = 1_048_576

FAILURE_CLASSES = (
    "tampered-receipt",
    "replayed-warrant",
    "malformed-record",
    "unsupported-value",
    "quarantined-candidate",
    "incomplete-evidence",
    "interrupted-consumption",
)
TOPOLOGIES = (
    "T1_SMALL_SINGLE_PACKAGE",
    "T2_MEDIUM_SERVICE",
    "T3_MONOREPO",
    "T4_MIXED_LANGUAGE",
)
WORKFLOWS = (
    "W1_CONFLICTING_EDITS",
    "W2_PARTIAL_DELETION",
    "W3_STALE_EVIDENCE",
    "W4_MISSING_HISTORY",
    "W5_OVERSIZED_STATE",
)

PRECEDENCE = (
    "RECORD_TOO_LARGE",
    "REQUEST_NOT_CANONICAL",
    "MALFORMED_RECORD",
    "UNSUPPORTED_SCHEMA",
    "UNSAFE_PATH",
    "WARRANT_REPLAY",
    "WARRANT_BINDING_MISMATCH",
    "AGGREGATE_LIMIT_EXCEEDED",
    "REPRESENTATION_HASH_MISMATCH",
    "WORKSPACE_PATH_CONFLICT",
    "EXECUTABLE_TEST_FAILED",
    "NO_SURVIVING_CANDIDATE",
    "MAX_PROVEN_PREFIX",
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


def _slot(
    slot_id: str,
    block: str,
    operation: str,
    verdict: str,
    reason: str,
    *,
    topology: str = "NONE",
    workflow: str = "NONE",
    factors: list[str] | None = None,
    boundary: str = "NONE",
    temporal: str = "NONE",
) -> dict[str, Any]:
    return {
        "slot_id": slot_id,
        "block": block,
        "operation": operation,
        "expected_verdict": verdict,
        "expected_reason": reason,
        "topology": topology,
        "workflow": workflow,
        "factors": sorted(factors or []),
        "boundary": boundary,
        "temporal": temporal,
    }


def slots() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    # Block A keeps the original 21 + 7 + 15 semantics. Expected legacy
    # verdicts/reasons are populated from the preserved generator at generation time.
    for failure in FAILURE_CLASSES:
        for variant in (1, 2, 3):
            rows.append(_slot(
                f"A-F-{failure}-{variant}", "A_ORIGINAL_FAILURE",
                f"legacy-failure:{failure}:{variant}", "LEGACY", "LEGACY",
                factors=[failure],
            ))
    for variant, failure in enumerate(FAILURE_CLASSES, start=1):
        rows.append(_slot(
            f"A-C-{failure}", "A_ORIGINAL_CONTROL",
            f"legacy-control:{failure}:{variant}", "LEGACY", "LEGACY",
            factors=[failure, "valid-control"],
        ))
    for verdict in ("PROMOTE", "REFUSE", "INVALID"):
        for repetition in range(1, 6):
            rows.append(_slot(
                f"A-D-{verdict.lower()}-{repetition}",
                "A_ORIGINAL_DETERMINISM",
                f"legacy-determinism:{verdict}:{repetition}",
                "LEGACY", "LEGACY", factors=["determinism", verdict],
            ))

    matrix_operations = {
        "W1_CONFLICTING_EDITS": (
            "conflict-safe", "conflict-safe", "conflict-no-safe", "conflict-no-safe"
        ),
        "W2_PARTIAL_DELETION": (
            "partial-promote", "partial-promote", "missing-test", "missing-test"
        ),
        "W3_STALE_EVIDENCE": ("stale",) * 4,
        "W4_MISSING_HISTORY": ("missing-history",) * 4,
        "W5_OVERSIZED_STATE": ("oversized-aggregate",) * 4,
    }
    expected = {
        "conflict-safe": ("PROMOTE", "MAX_PROVEN_PREFIX"),
        "conflict-no-safe": ("REFUSE", "NO_SURVIVING_CANDIDATE"),
        "partial-promote": ("PROMOTE", "MAX_PROVEN_PREFIX"),
        "missing-test": ("REFUSE", "EXECUTABLE_TEST_FAILED"),
        "stale": ("REFUSE", "NO_SURVIVING_CANDIDATE"),
        "missing-history": ("REFUSE", "NO_SURVIVING_CANDIDATE"),
        "oversized-aggregate": ("INVALID", "AGGREGATE_LIMIT_EXCEEDED"),
    }
    for workflow in WORKFLOWS:
        for index, topology in enumerate(TOPOLOGIES):
            operation = matrix_operations[workflow][index]
            verdict, reason = expected[operation]
            rows.append(_slot(
                f"B-{topology[1]}-{workflow[1]}", "B_TOPOLOGY_WORKFLOW",
                operation, verdict, reason, topology=topology, workflow=workflow,
                factors=[topology, workflow],
            ))

    compound = (
        ("C1_TAMPERED_AND_STALE", "tampered-stale", "REFUSE", "NO_SURVIVING_CANDIDATE"),
        ("C2_REPLAY_AFTER_PARTIAL_LOSS", "replay-partial", "REFUSE", "WARRANT_REPLAY"),
        ("C3_QUARANTINED_CONFLICT_WINNER", "veto-strong-valid-weak", "PROMOTE", "MAX_PROVEN_PREFIX"),
        ("C4_MALFORMED_OVERSIZED_RECORD", "raw-oversized-malformed", "INVALID", "RECORD_TOO_LARGE"),
        ("C5_UNSUPPORTED_SCHEMA_WITH_MISSING_HISTORY", "unsupported-missing", "INVALID", "UNSUPPORTED_SCHEMA"),
        ("C6_DUPLICATE_DURING_CONSUME_MUTATE_INTERRUPTION", "interrupt-duplicate", "REFUSE", "WARRANT_REPLAY"),
        ("C7_MONOREPO_PARTIAL_LOSS_WITH_STALE_DEPENDENCY", "missing-test", "REFUSE", "EXECUTABLE_TEST_FAILED"),
        ("C8_MIXED_LANGUAGE_EXECUTABLE_FAILURE", "missing-test", "REFUSE", "EXECUTABLE_TEST_FAILED"),
        ("C9_VALID_NEAR_BOUNDARY_WITH_STALE_DECOY", "near-boundary-stale-decoy", "PROMOTE", "MAX_PROVEN_PREFIX"),
    )
    compound_topology = {
        "C7_MONOREPO_PARTIAL_LOSS_WITH_STALE_DEPENDENCY": "T3_MONOREPO",
        "C8_MIXED_LANGUAGE_EXECUTABLE_FAILURE": "T4_MIXED_LANGUAGE",
        "C9_VALID_NEAR_BOUNDARY_WITH_STALE_DECOY": "T2_MEDIUM_SERVICE",
    }
    for case_id, operation, verdict, reason in compound:
        rows.append(_slot(
            f"C-{case_id.split('_', 1)[0]}", "C_COMPOUND", operation, verdict, reason,
            topology=compound_topology.get(case_id, "T2_MEDIUM_SERVICE"),
            factors=case_id.split("_"),
        ))

    boundaries = (
        ("D-FILE-LM1", "file-boundary", MAX_FILE_BYTES - 1, "PROMOTE", "MAX_PROVEN_PREFIX"),
        ("D-FILE-L", "file-boundary", MAX_FILE_BYTES, "PROMOTE", "MAX_PROVEN_PREFIX"),
        ("D-FILE-LP1", "file-boundary", MAX_FILE_BYTES + 1, "INVALID", "AGGREGATE_LIMIT_EXCEEDED"),
        ("D-AGG-LM1", "aggregate-boundary", MAX_AGGREGATE_BYTES - 1, "PROMOTE", "MAX_PROVEN_PREFIX"),
        ("D-AGG-L", "aggregate-boundary", MAX_AGGREGATE_BYTES, "PROMOTE", "MAX_PROVEN_PREFIX"),
        ("D-AGG-LP1", "aggregate-boundary", MAX_AGGREGATE_BYTES + 1, "INVALID", "AGGREGATE_LIMIT_EXCEEDED"),
    )
    for case_id, operation, size, verdict, reason in boundaries:
        rows.append(_slot(
            case_id, "D_EXACT_BOUNDARY", f"{operation}:{size}", verdict,
            reason, topology="T1_SMALL_SINGLE_PACKAGE",
            factors=[operation], boundary=str(size),
        ))

    temporal = (
        ("R1_CONSUMED_BEFORE_MUTATION_INTERRUPT", "fault-after-consume", "REFUSE", "WARRANT_REPLAY"),
        ("R2_RECEIPT_DURABILITY_RESTART", "receipt-restart", "REFUSE", "WARRANT_REPLAY"),
        ("R3_DUPLICATE_EVENT_DELIVERY", "duplicate-delivery", "REFUSE", "WARRANT_REPLAY"),
        ("R4_CONCURRENT_WARRANT_CLAIM", "concurrent-claim", "REFUSE", "WARRANT_REPLAY"),
        ("R5_DELAYED_STALE_EVENT_AFTER_NEWER_SAFE_STATE", "delayed-stale", "PROMOTE", "MAX_PROVEN_PREFIX"),
        ("R6_OUT_OF_ORDER_METADATA", "out-of-order", "INVALID", "MALFORMED_RECORD"),
    )
    for index, (case_id, operation, verdict, reason) in enumerate(temporal, start=1):
        rows.append(_slot(
            f"E-R{index}", "E_TEMPORAL_CUSTODY", operation, verdict, reason,
            topology="T2_MEDIUM_SERVICE", factors=[case_id], temporal=case_id,
        ))
    return rows


def validate_slots(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) != 84:
        raise ValueError("SLOT_COUNT_INVALID")
    identifiers = [row["slot_id"] for row in rows]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("DUPLICATE_SLOT")
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["block"]] = counts.get(row["block"], 0) + 1
    required = {
        "A_ORIGINAL_FAILURE": 21,
        "A_ORIGINAL_CONTROL": 7,
        "A_ORIGINAL_DETERMINISM": 15,
        "B_TOPOLOGY_WORKFLOW": 20,
        "C_COMPOUND": 9,
        "D_EXACT_BOUNDARY": 6,
        "E_TEMPORAL_CUSTODY": 6,
    }
    if counts != required:
        raise ValueError("BLOCK_COUNTS_INVALID")
    pairs = {
        (row["topology"], row["workflow"])
        for row in rows if row["block"] == "B_TOPOLOGY_WORKFLOW"
    }
    if pairs != {(topology, workflow) for topology in TOPOLOGIES for workflow in WORKFLOWS}:
        raise ValueError("MATRIX_COVERAGE_INVALID")
    matrix = [row for row in rows if row["block"] == "B_TOPOLOGY_WORKFLOW"]
    balance = {
        verdict: sum(row["expected_verdict"] == verdict for row in matrix)
        for verdict in ("PROMOTE", "REFUSE", "INVALID")
    }
    if balance["PROMOTE"] < 4 or balance["REFUSE"] < 8 or balance["INVALID"] < 4:
        raise ValueError("MATRIX_BALANCE_INVALID")
    return {"block_counts": counts, "matrix_balance": balance}


def contract_record() -> dict[str, Any]:
    rows = slots()
    coverage = validate_slots(rows)
    body = {
        "version": VERSION,
        "candidate_commit": CANDIDATE,
        "original_candidate_commit": ORIGINAL_CANDIDATE,
        "limits": {
            "max_file_bytes": MAX_FILE_BYTES,
            "max_aggregate_bytes": MAX_AGGREGATE_BYTES,
        },
        "reason_precedence": list(PRECEDENCE),
        "slots": rows,
        "coverage": coverage,
    }
    return dict(body, contract_sha256=digest(body))


if __name__ == "__main__":
    print(canonical(contract_record()).decode("utf-8"))
