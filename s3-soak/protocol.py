#!/usr/bin/env python3
"""Canonical, fail-closed S3 worker/coordinator exchange protocol."""
from __future__ import annotations

from enum import Enum
import hashlib
import json
import re
from typing import Any

VERSION = "s3-bridge-v1"
MAX_BYTES = 16_384
MAX_SEQUENCE = 12
GENESIS_HASH = "0" * 64
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class ProtocolError(ValueError):
    pass


class Operation(str, Enum):
    RUN_PROMOTE = "RUN_PROMOTE"
    RUN_REFUSE = "RUN_REFUSE"


REQUEST_FIELDS = {
    "version", "campaign_id", "sequence", "parent_hash", "operation",
    "payload", "request_hash",
}
PAYLOAD_FIELDS = {"hour", "scenario", "synthetic_hash"}
RESULT_FIELDS = {
    "version", "campaign_id", "sequence", "request_hash", "operation",
    "status", "stable_reason_code", "cloud_metrics", "evidence_hashes",
    "result_hash",
}
CLOUD_METRIC_FIELDS = {
    "cockroach_ms", "vector_ms", "lambda_ms", "changefeed_ms",
    "coordinator_ms", "lambda_invocations", "cockroach_operations",
    "changefeed_rows", "coordinator_backlog",
}
EVIDENCE_HASH_FIELDS = {
    "transaction", "vector", "lambda", "changefeed", "mcp_audit",
    "verifier", "cleanup",
}


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ProtocolError("NON_CANONICAL_VALUE") from exc


def sha256(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def _exact(value: Any, fields: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ProtocolError(code)
    return value


def _identifier(value: Any, code: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise ProtocolError(code)
    return value


def _hash(value: Any, code: str) -> str:
    if not isinstance(value, str) or not HASH_RE.fullmatch(value):
        raise ProtocolError(code)
    return value


def _uint(value: Any, low: int, high: int, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ProtocolError(code)
    return value


def request_body(value: dict[str, Any]) -> dict[str, Any]:
    return {key: value[key] for key in REQUEST_FIELDS if key != "request_hash"}


def make_request(campaign_id: str, sequence: int, parent_hash: str,
                 operation: Operation, scenario: str) -> dict[str, Any]:
    body = {
        "version": VERSION,
        "campaign_id": campaign_id,
        "sequence": sequence,
        "parent_hash": parent_hash,
        "operation": operation.value,
        "payload": {
            "hour": sequence,
            "scenario": scenario,
            "synthetic_hash": sha256({"campaign": campaign_id,
                                       "sequence": sequence,
                                       "scenario": scenario}),
        },
    }
    value = {**body, "request_hash": sha256(body)}
    validate_request(value)
    return value


def validate_request(value: Any) -> dict[str, Any]:
    value = _exact(value, REQUEST_FIELDS, "REQUEST_FIELDS_INVALID")
    if value["version"] != VERSION:
        raise ProtocolError("REQUEST_VERSION_INVALID")
    _identifier(value["campaign_id"], "CAMPAIGN_ID_INVALID")
    sequence = _uint(value["sequence"], 1, MAX_SEQUENCE, "SEQUENCE_INVALID")
    _hash(value["parent_hash"], "PARENT_HASH_INVALID")
    try:
        operation = Operation(value["operation"])
    except (TypeError, ValueError) as exc:
        raise ProtocolError("OPERATION_INVALID") from exc
    expected = Operation.RUN_PROMOTE if sequence % 2 else Operation.RUN_REFUSE
    if operation is not expected:
        raise ProtocolError("OPERATION_SEQUENCE_INVALID")
    payload = _exact(value["payload"], PAYLOAD_FIELDS, "PAYLOAD_FIELDS_INVALID")
    if payload["hour"] != sequence:
        raise ProtocolError("PAYLOAD_HOUR_INVALID")
    _identifier(payload["scenario"], "SCENARIO_INVALID")
    _hash(payload["synthetic_hash"], "SYNTHETIC_HASH_INVALID")
    _hash(value["request_hash"], "REQUEST_HASH_INVALID")
    if value["request_hash"] != sha256(request_body(value)):
        raise ProtocolError("REQUEST_HASH_MISMATCH")
    if len(canonical(value)) > MAX_BYTES:
        raise ProtocolError("REQUEST_OVERSIZED")
    return value


def result_body(value: dict[str, Any]) -> dict[str, Any]:
    return {key: value[key] for key in RESULT_FIELDS if key != "result_hash"}


def make_result(request: dict[str, Any], cloud_metrics: dict[str, Any],
                evidence_hashes: dict[str, str]) -> dict[str, Any]:
    validate_request(request)
    body = {
        "version": VERSION,
        "campaign_id": request["campaign_id"],
        "sequence": request["sequence"],
        "request_hash": request["request_hash"],
        "operation": request["operation"],
        "status": "PASS",
        "stable_reason_code": "LIVE_PATH_VERIFIED",
        "cloud_metrics": cloud_metrics,
        "evidence_hashes": evidence_hashes,
    }
    value = {**body, "result_hash": sha256(body)}
    validate_result(value, request)
    return value


def validate_result(value: Any, request: dict[str, Any]) -> dict[str, Any]:
    validate_request(request)
    value = _exact(value, RESULT_FIELDS, "RESULT_FIELDS_INVALID")
    if value["version"] != VERSION:
        raise ProtocolError("RESULT_VERSION_INVALID")
    for name in ("campaign_id", "sequence", "request_hash", "operation"):
        if value[name] != request[name]:
            raise ProtocolError("RESULT_LINKAGE_INVALID")
    if value["status"] != "PASS" or value["stable_reason_code"] != "LIVE_PATH_VERIFIED":
        raise ProtocolError("RESULT_STATUS_INVALID")
    metrics = _exact(value["cloud_metrics"], CLOUD_METRIC_FIELDS,
                     "CLOUD_METRICS_INVALID")
    for name, metric in metrics.items():
        if name.endswith("_ms"):
            _uint(metric, 0, 120_000, "LATENCY_INVALID")
        else:
            _uint(metric, 0, 10_000, "COUNTER_INVALID")
    hashes = _exact(value["evidence_hashes"], EVIDENCE_HASH_FIELDS,
                    "EVIDENCE_HASHES_INVALID")
    for item in hashes.values():
        _hash(item, "EVIDENCE_HASH_INVALID")
    _hash(value["result_hash"], "RESULT_HASH_INVALID")
    if value["result_hash"] != sha256(result_body(value)):
        raise ProtocolError("RESULT_HASH_MISMATCH")
    if len(canonical(value)) > MAX_BYTES:
        raise ProtocolError("RESULT_OVERSIZED")
    return value


def decode_request(raw: bytes) -> dict[str, Any]:
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BYTES:
        raise ProtocolError("REQUEST_BYTES_INVALID")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("REQUEST_JSON_INVALID") from exc
    if canonical(value) != raw:
        raise ProtocolError("REQUEST_NON_CANONICAL")
    return validate_request(value)


def decode_result(raw: bytes, request: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BYTES:
        raise ProtocolError("RESULT_BYTES_INVALID")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("RESULT_JSON_INVALID") from exc
    if canonical(value) != raw:
        raise ProtocolError("RESULT_NON_CANONICAL")
    return validate_result(value, request)
