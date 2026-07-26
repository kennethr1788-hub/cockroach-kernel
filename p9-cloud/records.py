"""P9 offline cloud integration records: strict canonical request/response schemas.

Synthetic, deterministic, standard library only. This module defines the exact
canonical JSON contract for the bounded P9 Lambda evaluator and the strict
client-side response validation used by the vertical slice. Every cloud message
is capped at 16 KiB, uses sorted keys and compact separators, forbids NaN, and
binds a self-referential SHA-256 hash computed over the body without that hash.

The Lambda response is ALWAYS advisory. It carries no promotion/refusal/invalid
decision, no policy mutation, no destination or tool choice. Strict known-field
validation plus an authority-vocabulary scan fail closed on any attempt to emit
authority. This module performs no network, filesystem, credential, model,
random, or time access.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

VERSION = "p9-v1"
MAX_MESSAGE_BYTES = 16384  # 16 KiB cap on every cloud request/response
MAX_OBSERVATIONS = 16
MAX_OBSERVATION_TEXT_BYTES = 256

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

REQUEST_FIELDS = {
    "version", "request_id", "task_id", "candidate_id",
    "trajectory_hash", "candidate_hash", "policy_hash",
    "features", "request_hash",
}
RESPONSE_FIELDS = {
    "version", "request_id", "candidate_id",
    "trajectory_hash", "candidate_hash", "policy_hash",
    "status", "observations", "response_hash",
}
OBSERVATION_FIELDS = {"code", "severity", "message"}

# The only status a Lambda response may ever carry.
ADVISORY_STATUS = "ADVISORY"

SEVERITIES = ("INFO", "LOW", "MEDIUM", "HIGH")

# Stable, closed set of advisory observation codes. The evaluator only emits
# codes from this set; anything else fails closed.
OBSERVATION_CODES = (
    "EVALUATION_COMPLETE",
    "POLICY_VETO_SIGNAL",
    "TAMPER_SIGNAL",
    "UNSAFE_SIGNAL",
    "WARRANT_CONSUMED_SIGNAL",
    "QUORUM_SHORTFALL_SIGNAL",
    "CONTEXT_LOW_SIGNAL",
)

# Declared numeric/boolean feature evidence. The features object is bounded and
# strict: exactly these keys, each with the declared kind and bounds.
FEATURE_SPECS = {
    "event_count": ("int", 0, 100000),
    "approvals": ("int", 0, 1000),
    "refusals": ("int", 0, 1000),
    "context_relevance": ("float", 0.0, 1.0),
    "quorum_met": ("bool", None, None),
    "policy_veto": ("bool", None, None),
    "tampered": ("bool", None, None),
    "unsafe": ("bool", None, None),
    "warrant_consumed": ("bool", None, None),
}

# Authority vocabulary that must never appear in an advisory response. Any
# observation code or message containing one of these markers fails closed.
AUTHORITY_MARKERS = (
    "promote", "promotion", "refuse", "refusal", "invalid",
    "policy_change", "destination", "tool_call", "tool_request",
    "execute", "escalate", "delegate", "call_agent",
)


class CloudError(ValueError):
    """Fail-closed canonical validation or evaluation fault. Carries a stable code."""


# ---------------------------------------------------------------------------
# Canonical primitives
# ---------------------------------------------------------------------------

def canonical_json(value: Any) -> bytes:
    """Canonical UTF-8 JSON: sorted keys, compact separators, no NaN, 16 KiB cap."""
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise CloudError("MALFORMED_RECORD") from exc
    if len(encoded) > MAX_MESSAGE_BYTES:
        raise CloudError("RECORD_TOO_LARGE")
    return encoded


def sha256_hex(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value)
    return hashlib.sha256(raw).hexdigest()


def require_id(value: Any) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise CloudError("INVALID_ID")
    return value


def require_hash(value: Any) -> str:
    if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
        raise CloudError("INVALID_HASH")
    return value


def validate_object(record: Any, fields: set[str]) -> None:
    if not isinstance(record, dict):
        raise CloudError("MALFORMED_RECORD")
    if set(record) - fields:
        raise CloudError("UNKNOWN_FIELD")
    if fields - set(record):
        raise CloudError("MISSING_FIELD")


def contains_authority_marker(value: Any) -> bool:
    """Detect authority/decision vocabulary in untrusted response content."""
    if isinstance(value, dict):
        return any(contains_authority_marker(k) or contains_authority_marker(v)
                   for k, v in value.items())
    if isinstance(value, list):
        return any(contains_authority_marker(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return any(marker in lowered for marker in AUTHORITY_MARKERS)
    return False


# ---------------------------------------------------------------------------
# Feature validation
# ---------------------------------------------------------------------------

def validate_features(features: Any) -> None:
    """Strict bounded features: exactly the declared numeric/boolean evidence."""
    validate_object(features, set(FEATURE_SPECS))
    for name, (kind, low, high) in FEATURE_SPECS.items():
        value = features[name]
        if kind == "bool":
            if not isinstance(value, bool):
                raise CloudError("WRONG_TYPE")
        elif kind == "int":
            if isinstance(value, bool) or not isinstance(value, int):
                raise CloudError("WRONG_TYPE")
            if value < low or value > high:
                raise CloudError("OUT_OF_RANGE")
        else:  # float
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise CloudError("WRONG_TYPE")
            if value != value or value in (float("inf"), float("-inf")):
                raise CloudError("WRONG_TYPE")
            if value < low or value > high:
                raise CloudError("OUT_OF_RANGE")


# ---------------------------------------------------------------------------
# Request records
# ---------------------------------------------------------------------------

def request_body(request: dict[str, Any]) -> dict[str, Any]:
    """The exact request body over which request_hash is computed."""
    return {key: request[key] for key in REQUEST_FIELDS if key != "request_hash"}


def make_request(request_id: str, task_id: str, candidate_id: str,
                 trajectory_hash: str, candidate_hash: str, policy_hash: str,
                 features: dict[str, Any]) -> dict[str, Any]:
    body = {
        "version": VERSION,
        "request_id": request_id,
        "task_id": task_id,
        "candidate_id": candidate_id,
        "trajectory_hash": trajectory_hash,
        "candidate_hash": candidate_hash,
        "policy_hash": policy_hash,
        "features": features,
    }
    validate_features(features)
    request = dict(body)
    request["request_hash"] = sha256_hex(body)
    validate_request(request)
    canonical_json(request)
    return request


def validate_request(request: Any) -> None:
    """Strict request validation; any deviation fails closed with a stable code."""
    validate_object(request, REQUEST_FIELDS)
    if request["version"] != VERSION:
        raise CloudError("UNSUPPORTED_SCHEMA")
    for key in ("request_id", "task_id", "candidate_id"):
        require_id(request[key])
    for key in ("trajectory_hash", "candidate_hash", "policy_hash"):
        require_hash(request[key])
    validate_features(request["features"])
    require_hash(request["request_hash"])
    if request["request_hash"] != sha256_hex(request_body(request)):
        raise CloudError("STALE_HASH")
    canonical_json(request)  # enforce the 16 KiB message cap


# ---------------------------------------------------------------------------
# Response records
# ---------------------------------------------------------------------------

def response_body(response: dict[str, Any]) -> dict[str, Any]:
    """The exact response body over which response_hash is computed."""
    return {key: response[key] for key in RESPONSE_FIELDS if key != "response_hash"}


def validate_observation(observation: Any) -> None:
    validate_object(observation, OBSERVATION_FIELDS)
    if observation["code"] not in OBSERVATION_CODES:
        raise CloudError("UNKNOWN_OBSERVATION_CODE")
    if observation["severity"] not in SEVERITIES:
        raise CloudError("MALFORMED_RECORD")
    message = observation["message"]
    if not isinstance(message, str):
        raise CloudError("WRONG_TYPE")
    if len(message.encode("utf-8")) > MAX_OBSERVATION_TEXT_BYTES:
        raise CloudError("RECORD_TOO_LARGE")
    if contains_authority_marker(observation):
        raise CloudError("AUTHORITY_REQUEST")


def make_response(request: dict[str, Any],
                  observations: list[dict[str, Any]]) -> dict[str, Any]:
    """Build an ADVISORY-only response bound to a validated request.

    The response echoes the request's identity and input hashes, always carries
    status ADVISORY, and never carries any decision, policy, destination, or
    tool field.
    """
    validate_request(request)
    body = {
        "version": VERSION,
        "request_id": request["request_id"],
        "candidate_id": request["candidate_id"],
        "trajectory_hash": request["trajectory_hash"],
        "candidate_hash": request["candidate_hash"],
        "policy_hash": request["policy_hash"],
        "status": ADVISORY_STATUS,
        "observations": observations,
    }
    response = dict(body)
    response["response_hash"] = sha256_hex(body)
    validate_response(response)
    canonical_json(response)
    return response


def validate_response(response: Any) -> None:
    """Strict client-side response validation; fail closed on any deviation."""
    validate_object(response, RESPONSE_FIELDS)
    if response["version"] != VERSION:
        raise CloudError("UNSUPPORTED_SCHEMA")
    require_id(response["request_id"])
    require_id(response["candidate_id"])
    for key in ("trajectory_hash", "candidate_hash", "policy_hash"):
        require_hash(response[key])
    # Advisory-only: the status is fixed and no authority vocabulary may appear.
    if response["status"] != ADVISORY_STATUS:
        raise CloudError("AUTHORITY_REQUEST")
    observations = response["observations"]
    if not isinstance(observations, list):
        raise CloudError("WRONG_TYPE")
    if len(observations) > MAX_OBSERVATIONS:
        raise CloudError("OBSERVATION_LIMIT_VIOLATION")
    for observation in observations:
        validate_observation(observation)
    require_hash(response["response_hash"])
    if response["response_hash"] != sha256_hex(response_body(response)):
        raise CloudError("STALE_HASH")
    canonical_json(response)  # enforce the 16 KiB message cap


def response_matches_request(request: dict[str, Any], response: dict[str, Any]) -> bool:
    """True only if the response echoes exactly this request's identity + hashes.

    Detects stale or misattributed responses that are internally well-formed but
    bound to a different (superseded) request.
    """
    validate_request(request)
    validate_response(response)
    for key in ("request_id", "candidate_id",
                "trajectory_hash", "candidate_hash", "policy_hash"):
        if response[key] != request[key]:
            return False
    return True
