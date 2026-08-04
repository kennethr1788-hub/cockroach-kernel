"""Deterministic safety decision for competing surviving representations.

This is deliberately a pure projection.  It never chooses a winner, writes
files, calls a model, opens a connection, or executes a recovery action.
"""
from __future__ import annotations

from typing import Any, Iterable
import re

from .continuation_brief import BriefError, canonical_json, digest

DECISION_VERSION = "ck-recovery-decision-v1"
OUTCOMES = frozenset({"CONTINUE", "QUARANTINE", "HUMAN_REVIEW_REQUIRED"})
STATUSES = frozenset({"VERIFIED", "STALE", "TAMPERED", "UNSUPPORTED"})
_HASH = re.compile(r"^[0-9a-f]{64}$")
_MAX_REPRESENTATIONS = 32
_MAX_FACTS = 128


class DecisionError(BriefError):
    """Fail-closed validation error for decision inputs."""


def _hash(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _HASH.fullmatch(value):
        raise DecisionError(f"{field}_HASH_INVALID")
    return value


def _bounded_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 256:
        raise DecisionError(f"{field}_INVALID")
    return value


def _representation(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict) or set(item) != {
            "representation_id", "content_hash", "lineage_hash", "status", "facts"}:
        raise DecisionError("REPRESENTATION_FIELDS_INVALID")
    representation_id = _bounded_text(item["representation_id"], "REPRESENTATION_ID")
    content_hash = _hash(item["content_hash"], "CONTENT")
    lineage_hash = item["lineage_hash"]
    if lineage_hash is not None:
        lineage_hash = _hash(lineage_hash, "LINEAGE")
    status = item["status"]
    if status not in STATUSES:
        raise DecisionError("REPRESENTATION_STATUS_INVALID")
    facts = item["facts"]
    if not isinstance(facts, dict) or len(facts) > _MAX_FACTS:
        raise DecisionError("REPRESENTATION_FACTS_INVALID")
    normalized: dict[str, Any] = {}
    for key, value in facts.items():
        _bounded_text(key, "FACT_NAME")
        if value is None:
            raise DecisionError("FACT_VALUE_INVALID")
        try:
            encoded = canonical_json(value)
        except BriefError as exc:
            raise DecisionError("FACT_VALUE_INVALID") from exc
        if len(encoded) > 4096:
            raise DecisionError("FACT_VALUE_TOO_LARGE")
        normalized[key] = value
    return {
        "representation_id": representation_id,
        "content_hash": content_hash,
        "lineage_hash": lineage_hash,
        "status": status,
        "facts": normalized,
    }


def _fact_groups(representations: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    names = sorted({name for item in representations for name in item["facts"]})
    common: list[dict[str, Any]] = []
    subset: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    for name in names:
        present = [(item["representation_id"], item["facts"][name])
                   for item in representations if name in item["facts"]]
        values = {canonical_json(value) for _, value in present}
        provenance = sorted(item["content_hash"] for item in representations if name in item["facts"])
        entry = {"name": name, "provenance": provenance}
        if len(values) == 1 and len(present) == len(representations):
            common.append(dict(entry, value=present[0][1]))
        elif len(values) == 1:
            subset.append(dict(entry, value=present[0][1], representation_ids=sorted(i for i, _ in present)))
        else:
            conflicts.append(dict(entry, values=[value for _, value in sorted(present)]))
    return common, subset, conflicts


def evaluate_recovery(representations: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Return one hash-bound, fail-closed recovery decision."""
    items = [_representation(item) for item in representations]
    if not items:
        raise DecisionError("REPRESENTATIONS_MISSING")
    if len(items) > _MAX_REPRESENTATIONS:
        raise DecisionError("REPRESENTATIONS_TOO_MANY")

    by_id: dict[str, dict[str, Any]] = {}
    duplicate_ids: list[str] = []
    for item in items:
        prior = by_id.get(item["representation_id"])
        if prior is not None:
            # The identifier is not an authority boundary: a replay with the
            # same content hash but different lineage, status, or facts is
            # still a conflicting duplicate and must be quarantined.
            if canonical_json(prior) != canonical_json(item):
                duplicate_ids.append(item["representation_id"])
            continue
        by_id[item["representation_id"]] = item
    unique = [by_id[key] for key in sorted(by_id)]
    common, subset, conflicts = _fact_groups(unique)
    statuses = {item["status"] for item in unique}
    missing_lineage = sorted(item["representation_id"] for item in unique if item["lineage_hash"] is None)
    reasons: list[str] = []
    if duplicate_ids:
        reasons.append("DUPLICATE_ID_CONFLICT")
    if "TAMPERED" in statuses:
        reasons.append("TAMPERED_REPRESENTATION")
    if conflicts:
        reasons.append("FACT_CONFLICT")
    if missing_lineage:
        reasons.append("LINEAGE_MISSING")
    if statuses - {"VERIFIED"}:
        reasons.append("NON_VERIFIED_STATUS")
    if duplicate_ids or "TAMPERED" in statuses:
        outcome = "QUARANTINE"
    elif reasons:
        outcome = "HUMAN_REVIEW_REQUIRED"
    else:
        outcome = "CONTINUE"

    source_hashes = sorted(item["content_hash"] for item in unique)
    body = {
        "version": DECISION_VERSION,
        "outcome": outcome,
        "reason_codes": sorted(set(reasons)) or ["ALL_REPRESENTATIONS_VERIFIED"],
        "source_hashes": source_hashes,
        "common_facts": common,
        "subset_facts": subset,
        "conflicts": conflicts,
        "missing_lineage": missing_lineage,
        "duplicate_ids": sorted(set(duplicate_ids)),
        "non_claims": {"no_winner_selected": True, "no_byte_creation": True,
                       "no_side_effects": True, "verifier_sole_authority": True},
    }
    return dict(body, decision_id=digest(body))


def evaluate_lineage_rows(rows: Iterable[Any]) -> dict[str, Any]:
    """Evaluate already-fetched, strictly parsed lineage rows.

    The adapter intentionally accepts rows only after ``parse_lineage_row``;
    it performs no SQL, connection, or network operation itself.
    """
    from .continuation_lineage import parse_lineage_row

    representations = []
    for raw in rows:
        row = parse_lineage_row(raw)
        representations.append({
            "representation_id": f"{row['task_id']}:{row['event_id']}",
            "content_hash": row["event_hash"],
            "lineage_hash": row["parent_event_hash"],
            "status": "VERIFIED",
            "facts": {
                "task_hash": row["task_hash"],
                "state_hash": row["state_hash"],
                "sequence": row["sequence"],
                "receipt_hash": row["receipt_hash"],
                "request_hash": row["request_hash"],
                "response_hash": row["response_hash"],
                "result_hash": row["result_hash"],
                "projection_hash": row["projection_hash"] or "UNKNOWN",
            },
        })
    return evaluate_recovery(representations)


def validate_decision(decision: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(decision, dict) or decision.get("version") != DECISION_VERSION:
        raise DecisionError("DECISION_VERSION_UNSUPPORTED")
    if decision.get("outcome") not in OUTCOMES:
        raise DecisionError("OUTCOME_INVALID")
    body = dict(decision)
    decision_id = body.pop("decision_id", None)
    if not isinstance(decision_id, str) or not _HASH.fullmatch(decision_id):
        raise DecisionError("DECISION_ID_INVALID")
    if decision_id != digest(body):
        raise DecisionError("DECISION_ID_MISMATCH")
    if body.get("non_claims") != {"no_winner_selected": True, "no_byte_creation": True,
                                   "no_side_effects": True, "verifier_sole_authority": True}:
        raise DecisionError("NON_CLAIMS_INVALID")
    canonical_json(decision)
    return decision
