"""P7 declared-loss recovery records and non-authoritative in-memory harness.

Synthetic, deterministic, standard library only. This layer implements strict
canonical JSON records (declared manifest, trajectory/loss receipts, surviving
candidates, one-use warrant, recovery decision, promotion/refusal receipt,
unrecovered ledger), normalized relative POSIX path validation, deterministic
candidate eligibility and maximum-proven-prefix selection, and a one-use
in-memory warrant harness in which consumption precedes promotion.

This module has NO deletion, promotion, policy, or gate authority. It performs
no filesystem undelete, no process control, no CockroachDB SQL, no network,
and no credential or HOME access. It reconstructs nothing; it only validates
hash-bound synthetic representations and records deterministic verdicts.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

VERSION = "p7-v1"
MAX_RECORD_BYTES = 65536  # 64 KiB cap on every canonical record

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

WARRANT_STATES = ("ISSUED", "CONSUMED", "INVALID")
DECISIONS = ("PROMOTE", "REFUSE")

# Stable refusal / decision reason codes.
POLICY_VETO = "POLICY_VETO"
TAMPERED_EVIDENCE = "TAMPERED_EVIDENCE"
WARRANT_REPLAY = "WARRANT_REPLAY"
MALFORMED_RECORD = "MALFORMED_RECORD"
UNSAFE_PATH = "UNSAFE_PATH"
UNSUPPORTED_SCHEMA = "UNSUPPORTED_SCHEMA"
STALE_POLICY = "STALE_POLICY"
MISSING_QUORUM = "MISSING_QUORUM"
EXECUTABLE_TEST_FAILED = "EXECUTABLE_TEST_FAILED"
NO_SURVIVING_CANDIDATE = "NO_SURVIVING_CANDIDATE"
MAX_PROVEN_PREFIX = "MAX_PROVEN_PREFIX"

FILE_ENTRY_FIELDS = {"path", "content_hash", "executable", "is_symlink"}
MANIFEST_FIELDS = {"version", "manifest_id", "task_id", "files"}
TRAJECTORY_RECEIPT_FIELDS = {"version", "receipt_id", "task_id", "manifest_hash",
                             "events", "trajectory_hash"}
LOSS_RECEIPT_FIELDS = {"version", "receipt_id", "task_id", "manifest_hash",
                       "lost_paths", "absence_hash"}
CANDIDATE_FIELDS = {"version", "candidate_id", "task_id", "provenance",
                    "source_receipt_hash", "policy_version", "policy_veto",
                    "tampered", "quorum_decision", "prefix_length",
                    "integrity_hash", "declared_paths", "file_hashes",
                    "executable_test"}
EXECUTABLE_TEST_FIELDS = {"test_id", "path", "feature_hash", "passed"}
WARRANT_FIELDS = {"version", "warrant_id", "task_id", "candidate_id",
                  "decision_hash", "state"}
DECISION_FIELDS = {"version", "task_id", "decision", "reason", "candidate_id",
                   "candidates_hash"}
PROMOTION_RECEIPT_FIELDS = {"version", "receipt_id", "task_id", "candidate_id",
                            "warrant_id", "decision_hash", "promoted_paths",
                            "receipt_hash"}
REFUSAL_RECEIPT_FIELDS = {"version", "receipt_id", "task_id", "decision_hash",
                          "reason", "receipt_hash"}
UNRECOVERED_ITEM_FIELDS = {"path", "reason"}
LEDGER_FIELDS = {"version", "ledger_id", "task_id", "manifest_hash",
                 "recovered_paths", "unrecovered_items"}

_MALFORMED_STRUCTURAL = {"UNKNOWN_FIELD", "MISSING_FIELD", "MALFORMED_RECORD",
                         "INVALID_ID", "INVALID_HASH", "RECORD_TOO_LARGE",
                         "NON_CANONICAL_ENCODING"}


class RecoveryError(ValueError):
    """Raised on any closed-failure validation or harness fault."""


class RecoveryInterrupted(RecoveryError):
    """Simulated crash after warrant consumption, before promotion records."""


# ---------------------------------------------------------------------------
# Canonical primitives
# ---------------------------------------------------------------------------

def canonical_json(value: Any) -> bytes:
    """Canonical UTF-8 JSON: sorted keys, no whitespace, 64 KiB cap."""
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise RecoveryError("MALFORMED_RECORD") from exc
    if len(encoded) > MAX_RECORD_BYTES:
        raise RecoveryError("RECORD_TOO_LARGE")
    return encoded


def sha256_hex(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value)
    return hashlib.sha256(raw).hexdigest()


def require_id(value: Any) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise RecoveryError("INVALID_ID")
    return value


def require_hash(value: Any) -> str:
    if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
        raise RecoveryError("INVALID_HASH")
    return value


def validate_object(record: Any, fields: set[str]) -> None:
    if not isinstance(record, dict):
        raise RecoveryError("MALFORMED_RECORD")
    if set(record) - fields:
        raise RecoveryError("UNKNOWN_FIELD")
    if fields - set(record):
        raise RecoveryError("MISSING_FIELD")


def _require_bool(value: Any) -> bool:
    if not isinstance(value, bool):
        raise RecoveryError("MALFORMED_RECORD")
    return value


def load_canonical(path: str) -> Any:
    """Load a JSON record that must be stored in exact canonical form."""
    with open(path, "rb") as handle:
        raw = handle.read()
    if len(raw) > MAX_RECORD_BYTES:
        raise RecoveryError("RECORD_TOO_LARGE")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RecoveryError("MALFORMED_RECORD") from exc
    if canonical_json(value) != raw:
        raise RecoveryError("NON_CANONICAL_ENCODING")
    return value


# ---------------------------------------------------------------------------
# Normalized relative POSIX path validation
# ---------------------------------------------------------------------------

def validate_relative_path(path: Any) -> str:
    """Accept only normalized relative POSIX paths.

    Rejects absolute paths, empty segments, dot segments, ``..``, NUL bytes,
    and backslashes. This is a pure lexical check; it touches no filesystem.
    """
    if not isinstance(path, str) or not path:
        raise RecoveryError(UNSAFE_PATH)
    if "\x00" in path or "\\" in path:
        raise RecoveryError(UNSAFE_PATH)
    if path.startswith("/"):
        raise RecoveryError(UNSAFE_PATH)
    for segment in path.split("/"):
        if segment in ("", ".", ".."):
            raise RecoveryError(UNSAFE_PATH)
    return path


def validate_file_entry(entry: Any) -> None:
    validate_object(entry, FILE_ENTRY_FIELDS)
    validate_relative_path(entry["path"])
    require_hash(entry["content_hash"])
    # Symlinks and executable content are represented by explicit record
    # flags; either flag set fails closed before any write could be imagined.
    if _require_bool(entry["is_symlink"]) is not False:
        raise RecoveryError(UNSAFE_PATH)
    if _require_bool(entry["executable"]) is not False:
        raise RecoveryError(UNSAFE_PATH)


def declared_paths(manifest: dict[str, Any]) -> list[str]:
    """Sorted declared path set of a validated manifest."""
    validate_manifest(manifest)
    return sorted(entry["path"] for entry in manifest["files"])


# ---------------------------------------------------------------------------
# Record validators
# ---------------------------------------------------------------------------

def validate_manifest(manifest: Any) -> None:
    validate_object(manifest, MANIFEST_FIELDS)
    if manifest["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(manifest["manifest_id"])
    require_id(manifest["task_id"])
    if not isinstance(manifest["files"], list):
        raise RecoveryError("MALFORMED_RECORD")
    seen: set[str] = set()
    for entry in manifest["files"]:
        validate_file_entry(entry)
        if entry["path"] in seen:
            raise RecoveryError("MALFORMED_RECORD")
        seen.add(entry["path"])


def validate_trajectory_receipt(receipt: Any) -> None:
    validate_object(receipt, TRAJECTORY_RECEIPT_FIELDS)
    if receipt["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(receipt["receipt_id"])
    require_id(receipt["task_id"])
    require_hash(receipt["manifest_hash"])
    require_hash(receipt["trajectory_hash"])
    if not isinstance(receipt["events"], list):
        raise RecoveryError("MALFORMED_RECORD")
    previous = ""
    for index, event in enumerate(receipt["events"]):
        validate_object(event, {"sequence", "event", "event_hash"})
        if (isinstance(event["sequence"], bool)
                or not isinstance(event["sequence"], int)
                or event["sequence"] != index):
            raise RecoveryError("NON_CONTIGUOUS_TRAJECTORY")
        if not isinstance(event["event"], str) or not event["event"]:
            raise RecoveryError("MALFORMED_RECORD")
        require_hash(event["event_hash"])
        previous = sha256_hex({"previous": previous, "event": event})
    if previous != receipt["trajectory_hash"]:
        raise RecoveryError("STALE_HASH")


def trajectory_integrity_hash(events: list[dict[str, Any]], prefix_length: int) -> str:
    """Hash binding exactly the contiguous proven prefix of trajectory events."""
    return sha256_hex(events[:prefix_length])


def validate_loss_receipt(receipt: Any, manifest: dict[str, Any] | None = None) -> None:
    validate_object(receipt, LOSS_RECEIPT_FIELDS)
    if receipt["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(receipt["receipt_id"])
    require_id(receipt["task_id"])
    require_hash(receipt["manifest_hash"])
    require_hash(receipt["absence_hash"])
    if not isinstance(receipt["lost_paths"], list):
        raise RecoveryError("MALFORMED_RECORD")
    for path in receipt["lost_paths"]:
        validate_relative_path(path)
    if receipt["absence_hash"] != sha256_hex({"lost_paths": sorted(receipt["lost_paths"]),
                                              "observed": "absent"}):
        raise RecoveryError("STALE_HASH")
    if manifest is not None:
        validate_manifest(manifest)
        if receipt["task_id"] != manifest["task_id"]:
            raise RecoveryError("LOSS_MANIFEST_MISMATCH")
        if receipt["manifest_hash"] != sha256_hex(manifest):
            raise RecoveryError("LOSS_MANIFEST_MISMATCH")
        if sorted(receipt["lost_paths"]) != declared_paths(manifest):
            raise RecoveryError("LOSS_MANIFEST_MISMATCH")


def validate_candidate(candidate: Any) -> None:
    validate_object(candidate, CANDIDATE_FIELDS)
    if candidate["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(candidate["candidate_id"])
    require_id(candidate["task_id"])
    provenance = candidate["provenance"]
    if not isinstance(provenance, dict) or not provenance.get("source"):
        raise RecoveryError("MALFORMED_RECORD")
    if not isinstance(provenance["source"], str):
        raise RecoveryError("MALFORMED_RECORD")
    require_hash(candidate["source_receipt_hash"])
    if not isinstance(candidate["policy_version"], str) or not candidate["policy_version"]:
        raise RecoveryError("MALFORMED_RECORD")
    _require_bool(candidate["policy_veto"])
    _require_bool(candidate["tampered"])
    quorum = candidate["quorum_decision"]
    if not isinstance(quorum, dict):
        raise RecoveryError("MALFORMED_RECORD")
    if quorum.get("decision") not in DECISIONS:
        raise RecoveryError("MALFORMED_RECORD")
    if (isinstance(candidate["prefix_length"], bool)
            or not isinstance(candidate["prefix_length"], int)
            or candidate["prefix_length"] < 0):
        raise RecoveryError("MALFORMED_RECORD")
    require_hash(candidate["integrity_hash"])
    if not isinstance(candidate["declared_paths"], list):
        raise RecoveryError("MALFORMED_RECORD")
    for path in candidate["declared_paths"]:
        validate_relative_path(path)
    if not isinstance(candidate["file_hashes"], dict):
        raise RecoveryError("MALFORMED_RECORD")
    for path, content_hash in candidate["file_hashes"].items():
        validate_relative_path(path)
        require_hash(content_hash)
    if set(candidate["file_hashes"]) != set(candidate["declared_paths"]):
        raise RecoveryError("MALFORMED_RECORD")
    test = candidate["executable_test"]
    validate_object(test, EXECUTABLE_TEST_FIELDS)
    require_id(test["test_id"])
    validate_relative_path(test["path"])
    require_hash(test["feature_hash"])
    _require_bool(test["passed"])


def validate_warrant(warrant: Any) -> None:
    validate_object(warrant, WARRANT_FIELDS)
    if warrant["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(warrant["warrant_id"])
    require_id(warrant["task_id"])
    require_id(warrant["candidate_id"])
    require_hash(warrant["decision_hash"])
    if warrant["state"] not in WARRANT_STATES:
        raise RecoveryError("MALFORMED_RECORD")


def validate_recovery_decision(decision: Any) -> None:
    validate_object(decision, DECISION_FIELDS)
    if decision["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(decision["task_id"])
    if decision["decision"] not in DECISIONS:
        raise RecoveryError("MALFORMED_RECORD")
    if not isinstance(decision["reason"], str) or not decision["reason"]:
        raise RecoveryError("MALFORMED_RECORD")
    if decision["candidate_id"] is not None:
        require_id(decision["candidate_id"])
    if decision["decision"] == "PROMOTE" and decision["candidate_id"] is None:
        raise RecoveryError("MALFORMED_RECORD")
    require_hash(decision["candidates_hash"])


def validate_promotion_receipt(receipt: Any) -> None:
    validate_object(receipt, PROMOTION_RECEIPT_FIELDS)
    if receipt["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(receipt["receipt_id"])
    require_id(receipt["task_id"])
    require_id(receipt["candidate_id"])
    require_id(receipt["warrant_id"])
    require_hash(receipt["decision_hash"])
    require_hash(receipt["receipt_hash"])
    if not isinstance(receipt["promoted_paths"], list):
        raise RecoveryError("MALFORMED_RECORD")
    for path in receipt["promoted_paths"]:
        validate_relative_path(path)


def validate_refusal_receipt(receipt: Any) -> None:
    validate_object(receipt, REFUSAL_RECEIPT_FIELDS)
    if receipt["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(receipt["receipt_id"])
    require_id(receipt["task_id"])
    require_hash(receipt["decision_hash"])
    require_hash(receipt["receipt_hash"])
    if not isinstance(receipt["reason"], str) or not receipt["reason"]:
        raise RecoveryError("MALFORMED_RECORD")


def validate_unrecovered_ledger(ledger: Any) -> None:
    validate_object(ledger, LEDGER_FIELDS)
    if ledger["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(ledger["ledger_id"])
    require_id(ledger["task_id"])
    require_hash(ledger["manifest_hash"])
    if not isinstance(ledger["recovered_paths"], list):
        raise RecoveryError("MALFORMED_RECORD")
    for path in ledger["recovered_paths"]:
        validate_relative_path(path)
    if not isinstance(ledger["unrecovered_items"], list):
        raise RecoveryError("MALFORMED_RECORD")
    for item in ledger["unrecovered_items"]:
        validate_object(item, UNRECOVERED_ITEM_FIELDS)
        validate_relative_path(item["path"])
        if not isinstance(item["reason"], str) or not item["reason"]:
            raise RecoveryError("MALFORMED_RECORD")


# ---------------------------------------------------------------------------
# Deterministic eligibility and selection
# ---------------------------------------------------------------------------

def _structural_code(exc: RecoveryError) -> str:
    code = str(exc)
    if code == UNSUPPORTED_SCHEMA:
        return UNSUPPORTED_SCHEMA
    if code == UNSAFE_PATH:
        return UNSAFE_PATH
    return MALFORMED_RECORD


def validate_context(context: Any) -> None:
    try:
        validate_object(context, {"manifest", "trajectory_receipt",
                                  "policy_version", "quorum_decision_hash"})
        validate_manifest(context["manifest"])
        validate_trajectory_receipt(context["trajectory_receipt"])
        if (not isinstance(context["policy_version"], str)
                or not context["policy_version"]):
            raise RecoveryError(MALFORMED_RECORD)
        require_hash(context["quorum_decision_hash"])
    except (RecoveryError, KeyError, TypeError) as exc:
        raise RecoveryError(MALFORMED_RECORD) from exc


def check_eligibility(candidate: Any, context: dict[str, Any]) -> str | None:
    """Return None if the candidate is admissible, else a stable reason code.

    Checks, in fixed order: exact schema/structure, provenance, source receipt
    binding, explicit policy veto, policy version, tamper flag, P6 quorum
    decision binding, contiguous-prefix integrity binding, declared-path set
    binding, and the executable-test declaration. Pure and deterministic.
    """
    try:
        validate_context(context)
        validate_candidate(candidate)
        canonical_json(candidate)  # enforce the 64 KiB record cap
    except RecoveryError as exc:
        return _structural_code(exc)

    manifest = context["manifest"]
    trajectory = context["trajectory_receipt"]

    if candidate["task_id"] != manifest["task_id"]:
        return TAMPERED_EVIDENCE
    if candidate["source_receipt_hash"] != sha256_hex(trajectory):
        return TAMPERED_EVIDENCE
    if candidate["policy_veto"]:
        return POLICY_VETO
    if candidate["policy_version"] != context["policy_version"]:
        return STALE_POLICY
    if candidate["tampered"]:
        return TAMPERED_EVIDENCE
    quorum = candidate["quorum_decision"]
    if quorum["decision"] != "PROMOTE":
        return MISSING_QUORUM
    if sha256_hex(quorum) != context["quorum_decision_hash"]:
        return MISSING_QUORUM
    events = trajectory["events"]
    if candidate["prefix_length"] > len(events):
        return TAMPERED_EVIDENCE
    if candidate["integrity_hash"] != trajectory_integrity_hash(events,
                                                                candidate["prefix_length"]):
        return TAMPERED_EVIDENCE
    declared = set(declared_paths(manifest))
    if any(path not in declared for path in candidate["declared_paths"]):
        return UNSAFE_PATH
    manifest_hashes = {entry["path"]: entry["content_hash"]
                       for entry in manifest["files"]}
    if any(candidate["file_hashes"][path] != manifest_hashes[path]
           for path in candidate["declared_paths"]):
        return TAMPERED_EVIDENCE
    test_path = candidate["executable_test"]["path"]
    if (test_path not in candidate["file_hashes"]
            or candidate["executable_test"]["feature_hash"]
            != candidate["file_hashes"][test_path]):
        return EXECUTABLE_TEST_FAILED
    if candidate["executable_test"]["passed"] is not True:
        return EXECUTABLE_TEST_FAILED
    return None


def _candidates_hash(candidates: list[Any]) -> str:
    """Order-independent hash over every canonically serializable candidate."""
    hashes = []
    for candidate in candidates:
        try:
            hashes.append(sha256_hex(candidate))
        except RecoveryError:
            continue
    return sha256_hex(sorted(hashes))


def make_decision(task_id: str, decision: str, reason: str,
                  candidate_id: str | None, candidates: list[Any]) -> dict[str, Any]:
    record = {
        "version": VERSION,
        "task_id": task_id,
        "decision": decision,
        "reason": reason,
        "candidate_id": candidate_id,
        "candidates_hash": _candidates_hash(candidates),
    }
    validate_recovery_decision(record)
    canonical_json(record)
    return record


def select_candidate(candidates: list[Any], context: dict[str, Any]) -> dict[str, Any]:
    """Deterministically select the longest contiguous proven prefix.

    Only candidates passing every eligibility binding are admitted. Among
    admitted candidates the longest ``prefix_length`` wins; ties break by
    canonical candidate ID (lexicographic minimum). The selector never
    invents or merges bytes. Returns a recovery decision record.
    """
    if not isinstance(candidates, list):
        raise RecoveryError("MALFORMED_RECORD")
    validate_context(context)
    task_id = context["manifest"]["task_id"]
    admitted = [candidate for candidate in candidates
                if check_eligibility(candidate, context) is None]
    if not admitted:
        return make_decision(task_id, "REFUSE", NO_SURVIVING_CANDIDATE, None, candidates)
    chosen = sorted(admitted,
                    key=lambda c: (-c["prefix_length"], c["candidate_id"]))[0]
    return make_decision(task_id, "PROMOTE", MAX_PROVEN_PREFIX,
                         chosen["candidate_id"], candidates)


# ---------------------------------------------------------------------------
# One-use warrant + non-authoritative in-memory harness
# ---------------------------------------------------------------------------

def make_warrant(warrant_id: str, task_id: str, candidate_id: str,
                 decision: dict[str, Any]) -> dict[str, Any]:
    """Issue a one-use warrant bound to an exact recovery decision."""
    validate_recovery_decision(decision)
    warrant = {
        "version": VERSION,
        "warrant_id": warrant_id,
        "task_id": task_id,
        "candidate_id": candidate_id,
        "decision_hash": sha256_hex(decision),
        "state": "ISSUED",
    }
    validate_warrant(warrant)
    canonical_json(warrant)
    return warrant


def _seal_receipt(body: dict[str, Any], fields: set[str]) -> dict[str, Any]:
    receipt_hash = sha256_hex(body)
    receipt = dict(body)
    receipt["receipt_id"] = "rcpt-" + receipt_hash[:32]
    receipt["receipt_hash"] = receipt_hash
    validate_object(receipt, fields)
    canonical_json(receipt)
    return receipt


def build_promotion_receipt(decision: dict[str, Any], warrant: dict[str, Any],
                            promoted_paths: list[str]) -> dict[str, Any]:
    validate_recovery_decision(decision)
    validate_warrant(warrant)
    body = {
        "version": VERSION,
        "task_id": decision["task_id"],
        "candidate_id": warrant["candidate_id"],
        "warrant_id": warrant["warrant_id"],
        "decision_hash": sha256_hex(decision),
        "promoted_paths": sorted(promoted_paths),
    }
    receipt = _seal_receipt(body, PROMOTION_RECEIPT_FIELDS)
    validate_promotion_receipt(receipt)
    return receipt


def build_refusal_receipt(decision: dict[str, Any]) -> dict[str, Any]:
    validate_recovery_decision(decision)
    body = {
        "version": VERSION,
        "task_id": decision["task_id"],
        "decision_hash": sha256_hex(decision),
        "reason": decision["reason"],
    }
    receipt = _seal_receipt(body, REFUSAL_RECEIPT_FIELDS)
    validate_refusal_receipt(receipt)
    return receipt


def make_unrecovered_ledger(ledger_id: str, manifest: dict[str, Any],
                            recovered_paths: list[str]) -> dict[str, Any]:
    """Ledger of declared paths no surviving authorized representation covers."""
    validate_manifest(manifest)
    declared = set(declared_paths(manifest))
    recovered = sorted(recovered_paths)
    for path in recovered:
        validate_relative_path(path)
        if path not in declared:
            raise RecoveryError(UNSAFE_PATH)
    ledger = {
        "version": VERSION,
        "ledger_id": ledger_id,
        "task_id": manifest["task_id"],
        "manifest_hash": sha256_hex(manifest),
        "recovered_paths": recovered,
        "unrecovered_items": [
            {"path": path, "reason": "NO_PROVEN_REPRESENTATION"}
            for path in sorted(declared - set(recovered))
        ],
    }
    validate_unrecovered_ledger(ledger)
    canonical_json(ledger)
    return ledger


class RecoveryHarness:
    """Non-authoritative in-memory one-use warrant harness.

    Consumption precedes promotion: an ISSUED warrant is marked CONSUMED
    before the promotion receipt is recorded. An interruption after
    consumption leaves the warrant CONSUMED (never replayable) and records
    no promotion. A second use refuses with WARRANT_REPLAY. This models the
    serializable consume-then-promote contract without any database, process,
    or filesystem authority.
    """

    def __init__(self) -> None:
        self._warrants: dict[str, dict[str, Any]] = {}
        self._promotions: dict[str, dict[str, Any]] = {}
        self._refusals: list[dict[str, Any]] = []

    def register_warrant(self, warrant: dict[str, Any]) -> None:
        validate_warrant(warrant)
        canonical_json(warrant)
        if warrant["warrant_id"] in self._warrants:
            raise RecoveryError(WARRANT_REPLAY)
        self._warrants[warrant["warrant_id"]] = json.loads(canonical_json(warrant))

    def warrant_state(self, warrant_id: str) -> str | None:
        warrant = self._warrants.get(warrant_id)
        return warrant["state"] if warrant else None

    def promotion(self, task_id: str) -> dict[str, Any] | None:
        return self._promotions.get(task_id)

    def refusals(self) -> list[dict[str, Any]]:
        return list(self._refusals)

    def recover(self, decision: dict[str, Any], warrant_id: str,
                promoted_paths: list[str] | None = None,
                fault: str | None = None) -> dict[str, Any]:
        """Apply a recovery decision against a one-use warrant.

        REFUSE decisions never touch the warrant. PROMOTE decisions consume
        the warrant first; fault="interrupt" raises RecoveryInterrupted after
        consumption with no promotion recorded. Returns the promotion or
        refusal receipt.
        """
        validate_recovery_decision(decision)
        canonical_json(decision)
        if decision["decision"] == "REFUSE":
            receipt = build_refusal_receipt(decision)
            self._refusals.append(receipt)
            return receipt

        warrant = self._warrants.get(warrant_id)
        if warrant is None:
            raise RecoveryError("UNKNOWN_WARRANT")
        if warrant["state"] != "ISSUED":
            receipt = build_refusal_receipt(make_decision(
                decision["task_id"], "REFUSE", WARRANT_REPLAY, None, []))
            self._refusals.append(receipt)
            return receipt
        if (warrant["task_id"] != decision["task_id"]
                or warrant["candidate_id"] != decision["candidate_id"]
                or warrant["decision_hash"] != sha256_hex(decision)):
            receipt = build_refusal_receipt(make_decision(
                decision["task_id"], "REFUSE", TAMPERED_EVIDENCE, None, []))
            self._refusals.append(receipt)
            return receipt

        # Consumption strictly precedes promotion.
        warrant["state"] = "CONSUMED"
        if fault == "interrupt":
            raise RecoveryInterrupted("RECOVERY_INTERRUPTED")
        if fault is not None:
            raise RecoveryError("UNKNOWN_FAULT")

        receipt = build_promotion_receipt(decision, warrant,
                                          promoted_paths or [])
        self._promotions[decision["task_id"]] = receipt
        return receipt
