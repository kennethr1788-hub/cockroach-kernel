"""P4 deterministic verifier and quarantine authority."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
ALLOWED = {
    "version", "candidate_id", "source_receipt_hash", "payload", "payload_hash",
    "schema_version", "provenance", "supported", "one_use_state", "quarantined",
    "policy_veto", "requested_paths", "declared_paths",
}


class VerifyError(ValueError):
    pass


def canonical(value: Any) -> bytes:
    try:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise VerifyError("MALFORMED_RECORD") from exc
    if len(raw) > 65536:
        raise VerifyError("RECORD_TOO_LARGE")
    return raw


def digest(value: Any) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def _paths_safe(paths: Any, declared: Any) -> bool:
    if not isinstance(paths, list) or not isinstance(declared, list):
        return False
    declared_set = set(declared)
    for path in paths:
        if not isinstance(path, str) or "\x00" in path or path.startswith("/"):
            return False
        parts = path.split("/")
        if ".." in parts or path not in declared_set:
            return False
    return True


@dataclass
class Quarantine:
    _records: dict[str, dict[str, Any]] = field(default_factory=dict)

    def insert(self, record: dict[str, Any]) -> None:
        candidate_id = record.get("candidate_id")
        if not isinstance(candidate_id, str) or not ID_RE.fullmatch(candidate_id):
            raise VerifyError("INVALID_ID")
        self._records[candidate_id] = json.loads(canonical(record))

    def contains(self, candidate_id: str) -> bool:
        return candidate_id in self._records

    def active(self) -> list[dict[str, Any]]:
        # Quarantined records have no active retrieval path by construction.
        return []

    def retrieve(self, candidate_id: str) -> None:
        return None


def verify(record: Any, quarantine: Quarantine | None = None) -> tuple[str, str]:
    """Return only deterministic (verdict, stable_reason_code)."""
    if not isinstance(record, dict):
        return "INVALID", "MALFORMED_RECORD"
    if set(record) - ALLOWED:
        return "INVALID", "UNKNOWN_FIELD"
    required = ALLOWED
    if not required.issubset(record):
        return "INVALID", "MISSING_FIELD"
    if not isinstance(record["candidate_id"], str) or not ID_RE.fullmatch(record["candidate_id"]):
        return "INVALID", "INVALID_ID"
    if record["schema_version"] != "p4-v1":
        return "REFUSE", "UNSUPPORTED_SCHEMA"
    if not isinstance(record["source_receipt_hash"], str) or not HEX64_RE.fullmatch(record["source_receipt_hash"]):
        return "INVALID", "INVALID_RECEIPT_HASH"
    if record["payload_hash"] != digest(record["payload"]):
        return "REFUSE", "HASH_MISMATCH"
    if not isinstance(record["provenance"], dict) or not record["provenance"].get("source"):
        return "INVALID", "MISSING_PROVENANCE"
    if record["one_use_state"] == "CONSUMED":
        return "REFUSE", "REPLAYED_TICKET"
    if record["quarantined"] or (quarantine and quarantine.contains(record["candidate_id"])):
        return "REFUSE", "QUARANTINED_INPUT"
    if not record["supported"]:
        return "REFUSE", "UNSUPPORTED_INPUT"
    if record["policy_veto"]:
        return "REFUSE", "POLICY_VETO"
    if not _paths_safe(record["requested_paths"], record["declared_paths"]):
        return "REFUSE", "UNSAFE_PATH"
    return "PROMOTE", "VERIFIED"
