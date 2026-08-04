"""Canonical, read-only continuation brief projection.

This module deliberately has no database, network, model, filesystem, or
side-effect authority.  It turns one already-verified recovery result and its
explicitly supplied trajectory references into a hash-bound advisory record.
The existing deterministic verifier remains the only verdict authority.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable

BRIEF_VERSION = "ck-continuation-brief-v1"
AUTHORITY = "P4_DETERMINISTIC_VERIFIER"
PRIMARY_STATES = frozenset({
    "EXACT", "PARTIAL", "UNRECOVERABLE", "STALE", "TAMPERED", "UNSUPPORTED",
})
SUPPORT_CLASSES = frozenset({"VERIFIED", "DERIVED", "UNKNOWN"})
ALLOWED_NEXT = frozenset({
    "CONTINUE_FROM_VERIFIED_STATE",
    "REVIEW_OPEN_QUESTIONS",
    "RUN_ACCEPTANCE_CHECKS",
})
BLOCKED_NEXT = frozenset({
    "EXECUTE_SIDE_EFFECTS",
    "CLAIM_UNCAPTURED_RECOVERY",
    "CREATE_MISSING_BYTES",
})
_HASH = re.compile(r"^[0-9a-f]{64}$")


class BriefError(ValueError):
    """Fail-closed validation error for a brief or its inputs."""


def canonical_json(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise BriefError("BRIEF_MALFORMED") from exc


def digest(value: Any) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical_json(value)).hexdigest()


def _hash_without(record: dict[str, Any], field: str) -> str:
    body = {key: value for key, value in record.items() if key != field}
    return digest(body)


def _hash(value: Any, name: str) -> str:
    if not isinstance(value, str) or not _HASH.fullmatch(value):
        raise BriefError(f"{name}_HASH_INVALID")
    return value


def _source_hash(result: dict[str, Any]) -> str:
    supplied = result.get("result_hash")
    if supplied is not None:
        supplied = _hash(supplied, "RESULT")
        if supplied != _hash_without(result, "result_hash"):
            raise BriefError("RESULT_HASH_MISMATCH")
        return supplied
    raise BriefError("RESULT_HASH_MISSING")


def _trajectory_ref(item: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise BriefError("TRAJECTORY_MALFORMED")
    trajectory_id = item.get("trajectory_id") or item.get("receipt_id") or item.get("event_id")
    if not isinstance(trajectory_id, str) or not trajectory_id:
        raise BriefError("TRAJECTORY_ID_MISSING")
    content_hash = item.get("content_hash") or item.get("trajectory_hash") or item.get("event_hash")
    if content_hash is None:
        content_hash = _hash_without(item, "content_hash")
    _hash(content_hash, "TRAJECTORY")
    return {"trajectory_id": trajectory_id, "content_hash": content_hash}


def _primary_state(result: dict[str, Any]) -> str:
    explicit = result.get("recovery_state")
    if explicit is not None:
        if not isinstance(explicit, str) or explicit not in PRIMARY_STATES:
            raise BriefError("PRIMARY_STATE_INVALID")
        return explicit
    if result.get("tampered_verdict") in {"REFUSE", "INVALID"}:
        return "TAMPERED"
    verdict = result.get("local_verdict")
    if verdict == "PROMOTE":
        return "EXACT"
    if verdict in {"REFUSE", "INVALID"}:
        return "UNRECOVERABLE"
    raise BriefError("PRIMARY_STATE_MISSING")


def _fact(name: str, value: Any, support: str, provenance: Iterable[str]) -> dict[str, Any]:
    if support not in SUPPORT_CLASSES:
        raise BriefError("FACT_SUPPORT_INVALID")
    refs = sorted(set(provenance))
    for ref in refs:
        _hash(ref, "PROVENANCE")
    body: dict[str, Any] = {"name": name, "support": support, "provenance": refs}
    body["value"] = value if value is not None else "UNKNOWN"
    if body["value"] == "UNKNOWN" and support != "UNKNOWN":
        raise BriefError("UNKNOWN_SUPPORT_MISMATCH")
    return body


def build_brief(recovery_result: dict[str, Any], trajectories: Iterable[dict[str, Any]], *,
                generated_at: str | None = None) -> dict[str, Any]:
    """Build one deterministic advisory brief from explicit hash-bound inputs."""
    if not isinstance(recovery_result, dict):
        raise BriefError("RESULT_MALFORMED")
    result_hash = _source_hash(recovery_result)
    receipt_hash = _hash(recovery_result.get("receipt_hash"), "RECEIPT")
    refs = [_trajectory_ref(item) for item in trajectories]
    if not refs:
        raise BriefError("TRAJECTORIES_MISSING")
    state = _primary_state(recovery_result)
    input_body = {
        "result_hash": result_hash,
        "receipt_hash": receipt_hash,
        "trajectories": refs,
        "state": state,
        "version": BRIEF_VERSION,
    }
    facts = [
        _fact("recovery_state", state, "VERIFIED", [result_hash, receipt_hash]),
        _fact("trajectory_count", len(refs), "VERIFIED", [r["content_hash"] for r in refs]),
        _fact("fresh_context", recovery_result.get("fresh_context"),
              "VERIFIED" if isinstance(recovery_result.get("fresh_context"), bool) else "UNKNOWN",
              [result_hash]),
    ]
    body: dict[str, Any] = {
        "version": BRIEF_VERSION,
        "brief_id": digest(input_body),
        "authority": AUTHORITY,
        "bounds": {"feature_id": "C1", "no_side_effects": True,
                   "no_byte_creation": True, "read_only": True},
        "inputs_ref": {"recovery_result_hash": result_hash,
                        "receipt_hash": receipt_hash, "trajectories": refs},
        "recovery_state": {"primary": state, "qualifiers": []},
        "facts": facts,
        "continuation": {
            "allowed_next": ["CONTINUE_FROM_VERIFIED_STATE", "REVIEW_OPEN_QUESTIONS",
                              "RUN_ACCEPTANCE_CHECKS"],
            "blocked_next": sorted(BLOCKED_NEXT),
            "open_questions": ["Which declared acceptance check should run next?"],
        },
        "non_claims": {"no_execution": True, "no_byte_creation": True,
                       "verifier_sole_authority": True,
                       "surviving_representations_only": True},
    }
    if generated_at is not None:
        if not isinstance(generated_at, str) or not generated_at:
            raise BriefError("GENERATED_AT_INVALID")
        body["generated_at"] = generated_at
    validate_brief(body)
    return body


def validate_brief(brief: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(brief, dict) or brief.get("version") != BRIEF_VERSION:
        raise BriefError("BRIEF_VERSION_UNSUPPORTED")
    allowed_fields = {"version", "brief_id", "authority", "bounds", "inputs_ref",
                      "recovery_state", "facts", "continuation", "non_claims",
                      "generated_at"}
    if set(brief) - allowed_fields:
        raise BriefError("BRIEF_FIELDS_INVALID")
    if brief.get("authority") != AUTHORITY:
        raise BriefError("AUTHORITY_INVALID")
    if brief.get("bounds") != {"feature_id": "C1", "no_side_effects": True,
                                "no_byte_creation": True, "read_only": True}:
        raise BriefError("BOUNDS_INVALID")
    inputs = brief.get("inputs_ref")
    if not isinstance(inputs, dict) or set(inputs) != {"recovery_result_hash", "receipt_hash", "trajectories"}:
        raise BriefError("INPUT_REFS_INVALID")
    _hash(inputs["recovery_result_hash"], "RESULT")
    _hash(inputs["receipt_hash"], "RECEIPT")
    if not isinstance(inputs["trajectories"], list) or not inputs["trajectories"]:
        raise BriefError("TRAJECTORIES_MISSING")
    for ref in inputs["trajectories"]:
        if not isinstance(ref, dict) or set(ref) != {"trajectory_id", "content_hash"}:
            raise BriefError("TRAJECTORY_REF_INVALID")
        if not isinstance(ref["trajectory_id"], str) or not ref["trajectory_id"]:
            raise BriefError("TRAJECTORY_ID_MISSING")
        _hash(ref["content_hash"], "TRAJECTORY")
    state_block = brief.get("recovery_state")
    if (not isinstance(state_block, dict) or set(state_block) != {"primary", "qualifiers"}
            or state_block.get("primary") not in PRIMARY_STATES
            or state_block.get("qualifiers") != []):
        raise BriefError("PRIMARY_STATE_INVALID")
    if not isinstance(brief.get("facts"), list) or not brief["facts"]:
        raise BriefError("FACTS_MISSING")
    for fact in brief["facts"]:
        if (not isinstance(fact, dict)
                or set(fact) != {"name", "value", "support", "provenance"}
                or not isinstance(fact.get("name"), str)):
            raise BriefError("FACT_MALFORMED")
        support = fact.get("support")
        if support not in SUPPORT_CLASSES:
            raise BriefError("FACT_SUPPORT_INVALID")
        if "value" not in fact or not isinstance(fact.get("provenance"), list):
            raise BriefError("FACT_FIELDS_INVALID")
        for ref in fact["provenance"]:
            _hash(ref, "PROVENANCE")
        if fact["value"] == "UNKNOWN" and support != "UNKNOWN":
            raise BriefError("UNKNOWN_SUPPORT_MISMATCH")
    continuation = brief.get("continuation")
    if not isinstance(continuation, dict):
        raise BriefError("CONTINUATION_INVALID")
    if (not isinstance(continuation.get("allowed_next"), list)
            or any(item not in ALLOWED_NEXT for item in continuation["allowed_next"])):
        raise BriefError("ALLOWED_ACTION_INVALID")
    if (not isinstance(continuation.get("blocked_next"), list)
            or any(item not in BLOCKED_NEXT for item in continuation["blocked_next"])):
        raise BriefError("BLOCKED_ACTION_INVALID")
    if not isinstance(continuation.get("open_questions"), list) or any(
            not isinstance(item, str) for item in continuation["open_questions"]):
        raise BriefError("OPEN_QUESTIONS_INVALID")
    if brief.get("non_claims") != {"no_execution": True, "no_byte_creation": True,
                                    "verifier_sole_authority": True,
                                    "surviving_representations_only": True}:
        raise BriefError("NON_CLAIMS_INVALID")
    brief_id = brief.get("brief_id")
    if not isinstance(brief_id, str) or not _HASH.fullmatch(brief_id):
        raise BriefError("BRIEF_ID_INVALID")
    body = dict(brief)
    body.pop("generated_at", None)
    body.pop("brief_id", None)
    expected = digest({"result_hash": brief["inputs_ref"]["recovery_result_hash"],
                       "receipt_hash": brief["inputs_ref"]["receipt_hash"],
                       "trajectories": brief["inputs_ref"]["trajectories"],
                       "state": brief["recovery_state"]["primary"],
                       "version": BRIEF_VERSION})
    if brief_id != expected:
        raise BriefError("BRIEF_ID_MISMATCH")
    canonical_json(brief)
    return brief
