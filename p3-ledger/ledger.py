"""Deterministic P3 ledger primitives. Runtime uses only the Python standard library."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
VERDICTS = {"PROMOTE", "REFUSE", "INVALID"}
TRANSITIONS = {"DECLARE", "RECORD", "EVALUATE", "PROMOTE", "REFUSE", "INVALID"}


class LedgerError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    """Canonical UTF-8 JSON; no insignificant whitespace or nondeterminism."""
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise LedgerError(f"non-canonical value: {exc}") from exc
    if len(encoded) > 65536:
        raise LedgerError("record exceeds 64 KiB")
    return encoded


def sha256_hex(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value)
    return hashlib.sha256(raw).hexdigest()


def require_id(value: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise LedgerError("invalid stable ID")
    return value


def validate_object(record: dict[str, Any], required: set[str], allowed: set[str]) -> None:
    if not isinstance(record, dict):
        raise LedgerError("record must be an object")
    unknown = set(record) - allowed
    missing = required - set(record)
    if unknown:
        raise LedgerError(f"unknown fields: {sorted(unknown)}")
    if missing:
        raise LedgerError(f"missing fields: {sorted(missing)}")


def validate_task(task: dict[str, Any]) -> None:
    allowed = {"version", "task_id", "declared_state", "declared_state_hash"}
    validate_object(task, allowed, allowed)
    require_id(task["task_id"])
    if sha256_hex(task["declared_state"]) != task["declared_state_hash"]:
        raise LedgerError("declared state hash mismatch")


def validate_event(event: dict[str, Any]) -> None:
    allowed = {"version", "event_id", "task_id", "sequence", "parent_event_id", "state", "state_hash"}
    validate_object(event, allowed, allowed)
    for key in ("event_id", "task_id"):
        require_id(event[key])
    if event["parent_event_id"] is not None:
        require_id(event["parent_event_id"])
    if not isinstance(event["sequence"], int) or event["sequence"] < 0:
        raise LedgerError("invalid sequence")
    if sha256_hex(event["state"]) != event["state_hash"]:
        raise LedgerError("event state hash mismatch")


def validate_candidate(candidate: dict[str, Any]) -> None:
    allowed = {"version", "candidate_id", "task_id", "source_event_id", "prefix", "state_hash",
               "receipt_hash", "policy_version", "votes", "policy_veto", "tampered", "unsafe",
               "warrant_state", "retention_class"}
    validate_object(candidate, {"version", "candidate_id", "task_id", "source_event_id", "prefix",
                                "state_hash", "receipt_hash", "policy_version", "votes", "policy_veto",
                                "tampered", "unsafe", "warrant_state", "retention_class"}, allowed)
    for key in ("candidate_id", "task_id", "source_event_id"):
        require_id(candidate[key])
    if not isinstance(candidate["votes"], list):
        raise LedgerError("votes must be a list")
    if candidate["warrant_state"] not in {"ISSUED", "CONSUMED", "INVALID", None}:
        raise LedgerError("invalid warrant state")


def deterministic_verdict(candidate: dict[str, Any], quorum: int = 3) -> tuple[str, str]:
    """Pure verdict function. It uses no time, randomness, model, or network."""
    try:
        validate_candidate(candidate)
    except LedgerError:
        return "INVALID", "MALFORMED_RECORD"
    if candidate["tampered"]:
        return "REFUSE", "TAMPERED_EVIDENCE"
    if candidate["unsafe"]:
        return "REFUSE", "POLICY_UNSAFE"
    if candidate["policy_veto"]:
        return "REFUSE", "POLICY_VETO"
    if candidate["warrant_state"] == "CONSUMED":
        return "REFUSE", "WARRANT_REPLAY"
    approvals = sum(1 for vote in candidate["votes"] if vote == "APPROVE")
    if approvals < quorum:
        return "REFUSE", "QUORUM_MISSING"
    return "PROMOTE", "QUORUM_PASS"


def trajectory_hash(events: Iterable[dict[str, Any]]) -> str:
    ordered = sorted(events, key=lambda event: event["sequence"])
    previous = ""
    for event in ordered:
        validate_event(event)
        if event["sequence"] and event["parent_event_id"] is None:
            raise LedgerError("missing parent event")
        previous = sha256_hex({"previous": previous, "event": event})
    return previous


@dataclass(frozen=True)
class EvidenceBudget:
    workload_bytes: int
    telemetry_bytes: int
    receipt_bytes: int
    manifest_bytes: int
    database_bytes: int

    def as_record(self) -> dict[str, int]:
        values = self.__dict__.copy()
        if any(value < 0 for value in values.values()):
            raise LedgerError("negative evidence size")
        return values
