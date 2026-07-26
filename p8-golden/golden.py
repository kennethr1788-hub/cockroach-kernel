"""Deterministic P8 reflection replay and golden-policy validation.

Reflection proposals are untrusted data. This module is the sole local authority
for replay semantics; it performs no model call, network access, filesystem
mutation, deployment, or foundation-model training.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

VERSION = "p8-v1"
MAX_RECORD_BYTES = 65536
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

POLICY_FIELDS = {
    "version", "policy_id", "ordinary_quorum", "critical_quorum",
    "correlation_limit",
}
INCIDENT_FIELDS = {
    "version", "incident_id", "task_id", "critical", "approvals", "refusals",
    "correlated_votes", "policy_veto", "tampered", "unsafe", "warrant_state",
    "expected_decision", "expected_reason", "input_hash",
}
PROPOSAL_FIELDS = {
    "version", "proposal_id", "base_policy_hash", "candidate_policy",
    "reflection_hash",
}

DECISIONS = ("PROMOTE", "REFUSE", "INVALID")
WARRANT_STATES = ("ISSUED", "CONSUMED", "INVALID", None)


class GoldenError(ValueError):
    """Fail-closed canonical validation error."""


def canonical_json(value: Any) -> bytes:
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise GoldenError("MALFORMED_RECORD") from exc
    if len(encoded) > MAX_RECORD_BYTES:
        raise GoldenError("RECORD_TOO_LARGE")
    return encoded


def sha256_hex(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value)
    return hashlib.sha256(raw).hexdigest()


def validate_object(value: Any, fields: set[str]) -> None:
    if not isinstance(value, dict):
        raise GoldenError("MALFORMED_RECORD")
    if set(value) - fields:
        raise GoldenError("UNKNOWN_FIELD")
    if fields - set(value):
        raise GoldenError("MISSING_FIELD")


def require_id(value: Any) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise GoldenError("INVALID_ID")
    return value


def require_hash(value: Any) -> str:
    if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
        raise GoldenError("INVALID_HASH")
    return value


def require_count(value: Any, minimum: int = 0, maximum: int = 5) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise GoldenError("MALFORMED_RECORD")
    if value < minimum or value > maximum:
        raise GoldenError("INVALID_THRESHOLD")
    return value


def validate_policy(policy: Any) -> None:
    validate_object(policy, POLICY_FIELDS)
    if policy["version"] != VERSION:
        raise GoldenError("UNSUPPORTED_SCHEMA")
    require_id(policy["policy_id"])
    ordinary = require_count(policy["ordinary_quorum"], 1)
    critical = require_count(policy["critical_quorum"], 1)
    correlation = require_count(policy["correlation_limit"], 1)
    if ordinary < 3 or critical < 4 or critical < ordinary:
        raise GoldenError("SAFETY_INVARIANT_FAILED")
    if correlation < 2 or correlation > 4:
        raise GoldenError("SAFETY_INVARIANT_FAILED")


def incident_input(incident: dict[str, Any]) -> dict[str, Any]:
    return {key: incident[key] for key in (
        "task_id", "critical", "approvals", "refusals", "correlated_votes",
        "policy_veto", "tampered", "unsafe", "warrant_state",
    )}


def validate_incident(incident: Any) -> None:
    validate_object(incident, INCIDENT_FIELDS)
    if incident["version"] != VERSION:
        raise GoldenError("UNSUPPORTED_SCHEMA")
    require_id(incident["incident_id"])
    require_id(incident["task_id"])
    for field in ("critical", "policy_veto", "tampered", "unsafe"):
        if not isinstance(incident[field], bool):
            raise GoldenError("MALFORMED_RECORD")
    require_count(incident["approvals"])
    require_count(incident["refusals"])
    require_count(incident["correlated_votes"])
    if incident["approvals"] + incident["refusals"] > 5:
        raise GoldenError("MALFORMED_RECORD")
    if incident["warrant_state"] not in WARRANT_STATES:
        raise GoldenError("MALFORMED_RECORD")
    if incident["expected_decision"] not in DECISIONS:
        raise GoldenError("MALFORMED_RECORD")
    if not isinstance(incident["expected_reason"], str) or not incident["expected_reason"]:
        raise GoldenError("MALFORMED_RECORD")
    require_hash(incident["input_hash"])
    if incident["input_hash"] != sha256_hex(incident_input(incident)):
        raise GoldenError("STALE_HASH")


def validate_incident_set(incidents: Any) -> None:
    if not isinstance(incidents, list) or not incidents:
        raise GoldenError("MALFORMED_RECORD")
    seen: set[str] = set()
    has_success = has_failure = False
    for incident in incidents:
        validate_incident(incident)
        identifier = incident["incident_id"]
        if identifier in seen:
            raise GoldenError("DUPLICATE_INCIDENT")
        seen.add(identifier)
        has_success |= incident["expected_decision"] == "PROMOTE"
        has_failure |= incident["expected_decision"] != "PROMOTE"
    if not has_success or not has_failure:
        raise GoldenError("INCIDENT_COVERAGE_MISSING")


def incident_set_hash(incidents: list[dict[str, Any]]) -> str:
    validate_incident_set(incidents)
    return sha256_hex(sorted((sha256_hex(item) for item in incidents)))


def validate_proposal(proposal: Any, base_policy: dict[str, Any]) -> None:
    validate_object(proposal, PROPOSAL_FIELDS)
    if proposal["version"] != VERSION:
        raise GoldenError("UNSUPPORTED_SCHEMA")
    require_id(proposal["proposal_id"])
    require_hash(proposal["base_policy_hash"])
    require_hash(proposal["reflection_hash"])
    validate_policy(base_policy)
    if proposal["base_policy_hash"] != sha256_hex(base_policy):
        raise GoldenError("STALE_BASE_POLICY")
    validate_policy(proposal["candidate_policy"])
    if proposal["candidate_policy"] == base_policy:
        raise GoldenError("NO_POLICY_CHANGE")
    if proposal["candidate_policy"]["policy_id"] == base_policy["policy_id"]:
        raise GoldenError("POLICY_VERSION_NOT_ADVANCED")


def evaluate(policy: dict[str, Any], incident: dict[str, Any]) -> tuple[str, str]:
    """Pure authority function. Free text and reflection hashes are never read."""
    validate_policy(policy)
    validate_incident(incident)
    if incident["tampered"]:
        return "REFUSE", "TAMPERED_EVIDENCE"
    if incident["unsafe"]:
        return "REFUSE", "POLICY_UNSAFE"
    if incident["policy_veto"]:
        return "REFUSE", "POLICY_VETO"
    if incident["warrant_state"] == "CONSUMED":
        return "REFUSE", "WARRANT_REPLAY"
    if incident["correlated_votes"] >= policy["correlation_limit"]:
        return "REFUSE", "CORRELATED_OUTPUTS"
    threshold = (policy["critical_quorum"] if incident["critical"]
                 else policy["ordinary_quorum"])
    if incident["approvals"] < threshold:
        return "REFUSE", "QUORUM_MISSING"
    return "PROMOTE", "QUORUM_PASS"


def _rejection(proposal: Any, base_policy: Any, incidents: Any,
               reason: str) -> dict[str, Any]:
    proposal_hash = sha256_hex(proposal) if isinstance(proposal, dict) else sha256_hex({"invalid": True})
    base_hash = sha256_hex(base_policy) if isinstance(base_policy, dict) else "0" * 64
    try:
        set_hash = incident_set_hash(incidents)
    except GoldenError:
        set_hash = "0" * 64
    body = {
        "version": VERSION,
        "outcome": "REJECT",
        "proposal_hash": proposal_hash,
        "base_policy_hash": base_hash,
        "candidate_policy_hash": sha256_hex(proposal.get("candidate_policy", {})) if isinstance(proposal, dict) else "0" * 64,
        "incident_set_hash": set_hash,
        "replay_hash": None,
        "reason": reason,
    }
    body["receipt_hash"] = sha256_hex(body)
    return body


def replay_proposal(proposal: Any, base_policy: Any,
                    incidents: Any) -> dict[str, Any]:
    """Return a canonical PROMOTE or REJECT outcome for every proposal."""
    try:
        validate_incident_set(incidents)
        validate_proposal(proposal, base_policy)
    except GoldenError as exc:
        return _rejection(proposal, base_policy, incidents, str(exc))

    candidate = proposal["candidate_policy"]
    results = []
    for incident in sorted(incidents, key=lambda item: item["incident_id"]):
        decision, reason = evaluate(candidate, incident)
        matched = (decision == incident["expected_decision"]
                   and reason == incident["expected_reason"])
        results.append({
            "incident_id": incident["incident_id"],
            "incident_hash": sha256_hex(incident),
            "decision": decision,
            "reason": reason,
            "matched": matched,
        })
    replay = {
        "version": VERSION,
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": sha256_hex(proposal),
        "base_policy_hash": sha256_hex(base_policy),
        "candidate_policy_hash": sha256_hex(candidate),
        "incident_set_hash": incident_set_hash(incidents),
        "results": results,
        "passed": all(item["matched"] for item in results),
    }
    replay_hash = sha256_hex(replay)
    if not replay["passed"]:
        receipt = _rejection(proposal, base_policy, incidents, "REGRESSION_DETECTED")
        receipt["replay_hash"] = replay_hash
        receipt["receipt_hash"] = sha256_hex({k: v for k, v in receipt.items()
                                               if k != "receipt_hash"})
        return {"replay": replay, "receipt": receipt}

    receipt_body = {
        "version": VERSION,
        "outcome": "PROMOTE",
        "proposal_hash": sha256_hex(proposal),
        "base_policy_hash": sha256_hex(base_policy),
        "candidate_policy_hash": sha256_hex(candidate),
        "incident_set_hash": replay["incident_set_hash"],
        "replay_hash": replay_hash,
        "reason": "ALL_INCIDENTS_MATCH",
    }
    receipt = dict(receipt_body, receipt_hash=sha256_hex(receipt_body))
    golden_pair = {
        "version": VERSION,
        "proposal_hash": receipt["proposal_hash"],
        "base_policy_hash": receipt["base_policy_hash"],
        "candidate_policy_hash": receipt["candidate_policy_hash"],
        "incident_set_hash": receipt["incident_set_hash"],
        "replay_hash": replay_hash,
        "promotion_receipt_hash": receipt["receipt_hash"],
    }
    return {"replay": replay, "receipt": receipt, "golden_pair": golden_pair}


def build_rollback_receipt(promotion_receipt: dict[str, Any],
                           current_policy: dict[str, Any],
                           previous_policy: dict[str, Any]) -> dict[str, Any]:
    validate_policy(current_policy)
    validate_policy(previous_policy)
    if promotion_receipt.get("outcome") != "PROMOTE":
        raise GoldenError("INVALID_PROMOTION_RECEIPT")
    if promotion_receipt.get("candidate_policy_hash") != sha256_hex(current_policy):
        raise GoldenError("ROLLBACK_CURRENT_MISMATCH")
    if promotion_receipt.get("base_policy_hash") != sha256_hex(previous_policy):
        raise GoldenError("ROLLBACK_TARGET_MISMATCH")
    body = {
        "version": VERSION,
        "promotion_receipt_hash": promotion_receipt["receipt_hash"],
        "from_policy_hash": sha256_hex(current_policy),
        "to_policy_hash": sha256_hex(previous_policy),
        "reason": "EXPLICIT_ROLLBACK",
    }
    return dict(body, receipt_hash=sha256_hex(body))
