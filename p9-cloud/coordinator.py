"""Fail-closed host coordinator core for the frozen P9 completion contract.

This module deliberately performs no network, SQL, shell, filesystem, model,
credential, random, or clock access.  It validates the sequence-bound commands
that a host adapter may execute and exposes only fixed operation plans.  Live
adapters remain separately bounded and must never execute data supplied by a
worker as code, SQL, paths, URLs, ARNs, or commands.
"""
from __future__ import annotations

from enum import Enum
from typing import Any

import records

VERSION = "p9-coordinator-v1"
CAMPAIGN_ID = "ck-p9-completion-r1"
PROMOTE_TRIAL_ID = "ck-p9-live-promote-r1"
REFUSE_TRIAL_ID = "ck-p9-live-refuse-r1"
TRIAL_IDS = (PROMOTE_TRIAL_ID, REFUSE_TRIAL_ID)
GENESIS_HASH = "0" * 64
MAX_MCP_ROWS = 2
MAX_VECTOR_ROWS = 8


class CoordinatorError(ValueError):
    """Stable coordinator refusal."""


class Operation(str, Enum):
    COMMIT_DECLARATION = "COMMIT_DECLARATION"
    STORE_CONTEXT_VECTOR = "STORE_CONTEXT_VECTOR"
    QUERY_CONTEXT_VECTOR = "QUERY_CONTEXT_VECTOR"
    INVOKE_LAMBDA = "INVOKE_LAMBDA"
    COMMIT_WORKER_RESULT = "COMMIT_WORKER_RESULT"
    STREAM_WORKER_RESULT = "STREAM_WORKER_RESULT"
    RESUME_STREAM = "RESUME_STREAM"
    VERIFY_CANDIDATE = "VERIFY_CANDIDATE"
    RECONSTRUCT_FRESH = "RECONSTRUCT_FRESH"
    REPLAY_LOCAL = "REPLAY_LOCAL"
    QUERY_MCP_LINKAGE = "QUERY_MCP_LINKAGE"
    CLEANUP_TRIAL = "CLEANUP_TRIAL"


ORDER = tuple(Operation)

COMMAND_FIELDS = {
    "version", "campaign_id", "trial_id", "sequence", "parent_hash",
    "operation", "payload", "command_hash",
}

PAYLOAD_FIELDS: dict[Operation, set[str]] = {
    Operation.COMMIT_DECLARATION: {
        "task_id", "event_id", "receipt_hash", "task_hash", "event_hash",
        "state_hash",
    },
    Operation.STORE_CONTEXT_VECTOR: {
        "vector_id", "task_id", "event_hash", "namespace", "vector_digest",
    },
    Operation.QUERY_CONTEXT_VECTOR: {
        "task_id", "namespace", "limit", "query_digest",
    },
    Operation.INVOKE_LAMBDA: {
        "request_id", "task_id", "candidate_id", "request_hash",
    },
    Operation.COMMIT_WORKER_RESULT: {
        "request_id", "task_id", "result_hash", "response_hash",
        "receipt_hash", "attempt",
    },
    Operation.STREAM_WORKER_RESULT: {
        "request_id", "projection_id", "receipt_hash", "cursor",
        "projection_hash",
    },
    Operation.RESUME_STREAM: {
        "projection_id", "cursor", "resume_hash",
    },
    Operation.VERIFY_CANDIDATE: {
        "candidate_id", "receipt_hash", "candidate_hash", "tampered", "unsafe",
    },
    Operation.RECONSTRUCT_FRESH: {
        "task_id", "receipt_hash", "capsule_hash",
    },
    Operation.REPLAY_LOCAL: {
        "task_id", "replay_hash", "expected_verdict",
    },
    Operation.QUERY_MCP_LINKAGE: {
        "task_id", "receipt_hash", "event_hash", "limit",
    },
    Operation.CLEANUP_TRIAL: {
        "task_id", "cleanup_hash",
    },
}

ID_FIELDS = {
    "task_id", "event_id", "vector_id", "request_id", "candidate_id",
    "projection_id", "namespace",
}
HASH_FIELDS = {
    "receipt_hash", "task_hash", "event_hash", "state_hash", "vector_digest",
    "query_digest", "request_hash", "result_hash", "response_hash",
    "projection_hash", "resume_hash", "candidate_hash", "capsule_hash",
    "replay_hash", "cleanup_hash",
}

# Fixed SQL text is code-owned.  Values are always supplied through the adapter
# parameter channel; object names can never come from an input payload.
SQL_OPERATION_PLANS = {
    Operation.COMMIT_DECLARATION: "P9_SQL_COMMIT_DECLARATION_V1",
    Operation.STORE_CONTEXT_VECTOR: "P9_SQL_STORE_CONTEXT_VECTOR_V1",
    Operation.QUERY_CONTEXT_VECTOR: "P9_SQL_QUERY_CONTEXT_VECTOR_V1",
    Operation.COMMIT_WORKER_RESULT: "P9_SQL_COMMIT_WORKER_RESULT_V1",
    Operation.STREAM_WORKER_RESULT: "P9_CHANGEFEED_WORKER_RESULTS_V1",
    Operation.RESUME_STREAM: "P9_CHANGEFEED_RESUME_WORKER_RESULTS_V1",
    Operation.QUERY_MCP_LINKAGE: "P9_MCP_RECEIPT_SELECT_V1",
    Operation.CLEANUP_TRIAL: "P9_SQL_CLEANUP_CAMPAIGN_V1",
}


def _validate_exact(record: Any, fields: set[str], code: str) -> None:
    if not isinstance(record, dict):
        raise CoordinatorError(code)
    if set(record) != fields:
        raise CoordinatorError(code)


def _require_uint(value: Any, low: int, high: int, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise CoordinatorError(code)
    return value


def _validate_payload(operation: Operation, payload: Any) -> None:
    _validate_exact(payload, PAYLOAD_FIELDS[operation], "PAYLOAD_FIELDS_INVALID")
    for name, value in payload.items():
        if name in ID_FIELDS:
            try:
                records.require_id(value)
            except records.CloudError as exc:
                raise CoordinatorError("PAYLOAD_ID_INVALID") from exc
        elif name in HASH_FIELDS:
            try:
                records.require_hash(value)
            except records.CloudError as exc:
                raise CoordinatorError("PAYLOAD_HASH_INVALID") from exc
    if operation is Operation.QUERY_CONTEXT_VECTOR:
        _require_uint(payload["limit"], 1, MAX_VECTOR_ROWS, "VECTOR_LIMIT_INVALID")
    if operation is Operation.QUERY_MCP_LINKAGE:
        _require_uint(payload["limit"], 1, MAX_MCP_ROWS, "MCP_LIMIT_INVALID")
    if operation is Operation.COMMIT_WORKER_RESULT:
        _require_uint(payload["attempt"], 1, 8, "ATTEMPT_INVALID")
    if operation in (Operation.STREAM_WORKER_RESULT, Operation.RESUME_STREAM):
        _require_uint(payload["cursor"], 1, 2**63 - 1, "CURSOR_INVALID")
    if operation is Operation.VERIFY_CANDIDATE:
        if not isinstance(payload["tampered"], bool) or not isinstance(payload["unsafe"], bool):
            raise CoordinatorError("CANDIDATE_FLAGS_INVALID")
    if operation is Operation.REPLAY_LOCAL and payload["expected_verdict"] not in {
        "PROMOTE", "REFUSE",
    }:
        raise CoordinatorError("EXPECTED_VERDICT_INVALID")


def command_body(command: dict[str, Any]) -> dict[str, Any]:
    return {key: command[key] for key in COMMAND_FIELDS if key != "command_hash"}


def make_command(
    trial_id: str,
    sequence: int,
    parent_hash: str,
    operation: Operation,
    payload: dict[str, Any],
) -> dict[str, Any]:
    body = {
        "version": VERSION,
        "campaign_id": CAMPAIGN_ID,
        "trial_id": trial_id,
        "sequence": sequence,
        "parent_hash": parent_hash,
        "operation": operation.value,
        "payload": payload,
    }
    command = dict(body, command_hash=records.sha256_hex(body))
    validate_command(command)
    records.canonical_json(command)
    return command


def validate_command(command: Any) -> None:
    _validate_exact(command, COMMAND_FIELDS, "COMMAND_FIELDS_INVALID")
    if command["version"] != VERSION or command["campaign_id"] != CAMPAIGN_ID:
        raise CoordinatorError("COMMAND_VERSION_OR_CAMPAIGN_INVALID")
    if command["trial_id"] not in TRIAL_IDS:
        raise CoordinatorError("TRIAL_ID_INVALID")
    sequence = _require_uint(command["sequence"], 0, len(ORDER) - 1, "SEQUENCE_INVALID")
    try:
        records.require_hash(command["parent_hash"])
        records.require_hash(command["command_hash"])
    except records.CloudError as exc:
        raise CoordinatorError("COMMAND_HASH_INVALID") from exc
    try:
        operation = Operation(command["operation"])
    except (TypeError, ValueError) as exc:
        raise CoordinatorError("OPERATION_INVALID") from exc
    if operation is not ORDER[sequence]:
        raise CoordinatorError("OPERATION_SEQUENCE_INVALID")
    _validate_payload(operation, command["payload"])
    if command["command_hash"] != records.sha256_hex(command_body(command)):
        raise CoordinatorError("COMMAND_HASH_MISMATCH")
    records.canonical_json(command)


def validate_command_bytes(raw: bytes) -> dict[str, Any]:
    if not isinstance(raw, bytes) or len(raw) > records.MAX_MESSAGE_BYTES:
        raise CoordinatorError("COMMAND_BYTES_INVALID")
    try:
        import json
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise CoordinatorError("COMMAND_JSON_INVALID") from exc
    if records.canonical_json(value) != raw:
        raise CoordinatorError("COMMAND_NON_CANONICAL")
    validate_command(value)
    return value


class Coordinator:
    """Sequence and replay authority for one fixed trial."""

    SNAPSHOT_FIELDS = {
        "version", "campaign_id", "trial_id", "next_sequence", "last_hash",
        "accepted_hashes", "state_hash", "snapshot_hash",
    }

    def __init__(self, trial_id: str) -> None:
        if trial_id not in TRIAL_IDS:
            raise CoordinatorError("TRIAL_ID_INVALID")
        self.trial_id = trial_id
        self.next_sequence = 0
        self.last_hash = GENESIS_HASH
        self.accepted_hashes: list[str] = []
        self.state_hash = GENESIS_HASH

    def accept(self, command: dict[str, Any] | bytes) -> dict[str, Any]:
        if isinstance(command, bytes):
            command = validate_command_bytes(command)
        else:
            validate_command(command)
        if command["trial_id"] != self.trial_id:
            raise CoordinatorError("TRIAL_MISMATCH")
        if command["sequence"] != self.next_sequence:
            raise CoordinatorError("SEQUENCE_MISMATCH")
        if command["parent_hash"] != self.last_hash:
            raise CoordinatorError("PARENT_HASH_MISMATCH")
        if command["command_hash"] in self.accepted_hashes:
            raise CoordinatorError("COMMAND_REPLAY")
        next_state = records.sha256_hex({
            "prior_state": self.state_hash,
            "command_hash": command["command_hash"],
            "sequence": self.next_sequence,
        })
        self.accepted_hashes.append(command["command_hash"])
        self.last_hash = command["command_hash"]
        self.state_hash = next_state
        self.next_sequence += 1
        return {
            "version": VERSION,
            "trial_id": self.trial_id,
            "sequence": command["sequence"],
            "operation": command["operation"],
            "command_hash": command["command_hash"],
            "state_hash": next_state,
            "result": "ACCEPTED",
        }

    def snapshot(self) -> bytes:
        body = {
            "version": VERSION,
            "campaign_id": CAMPAIGN_ID,
            "trial_id": self.trial_id,
            "next_sequence": self.next_sequence,
            "last_hash": self.last_hash,
            "accepted_hashes": list(self.accepted_hashes),
            "state_hash": self.state_hash,
        }
        return records.canonical_json(dict(body, snapshot_hash=records.sha256_hex(body)))

    @classmethod
    def restore(cls, raw: bytes) -> "Coordinator":
        if not isinstance(raw, bytes) or len(raw) > records.MAX_MESSAGE_BYTES:
            raise CoordinatorError("SNAPSHOT_BYTES_INVALID")
        try:
            import json
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise CoordinatorError("SNAPSHOT_JSON_INVALID") from exc
        if records.canonical_json(value) != raw:
            raise CoordinatorError("SNAPSHOT_NON_CANONICAL")
        _validate_exact(value, cls.SNAPSHOT_FIELDS, "SNAPSHOT_FIELDS_INVALID")
        body = {key: value[key] for key in cls.SNAPSHOT_FIELDS if key != "snapshot_hash"}
        if value["snapshot_hash"] != records.sha256_hex(body):
            raise CoordinatorError("SNAPSHOT_HASH_MISMATCH")
        if value["version"] != VERSION or value["campaign_id"] != CAMPAIGN_ID:
            raise CoordinatorError("SNAPSHOT_VERSION_OR_CAMPAIGN_INVALID")
        instance = cls(value["trial_id"])
        next_sequence = _require_uint(
            value["next_sequence"], 0, len(ORDER), "SNAPSHOT_SEQUENCE_INVALID"
        )
        accepted = value["accepted_hashes"]
        if not isinstance(accepted, list) or len(accepted) != next_sequence:
            raise CoordinatorError("SNAPSHOT_ACCEPTED_INVALID")
        for item in accepted:
            try:
                records.require_hash(item)
            except records.CloudError as exc:
                raise CoordinatorError("SNAPSHOT_ACCEPTED_INVALID") from exc
        if len(set(accepted)) != len(accepted):
            raise CoordinatorError("SNAPSHOT_REPLAY_INVALID")
        for field in ("last_hash", "state_hash"):
            try:
                records.require_hash(value[field])
            except records.CloudError as exc:
                raise CoordinatorError("SNAPSHOT_HASH_INVALID") from exc
        expected_last = GENESIS_HASH if not accepted else accepted[-1]
        if value["last_hash"] != expected_last:
            raise CoordinatorError("SNAPSHOT_LAST_HASH_INVALID")
        instance.next_sequence = next_sequence
        instance.last_hash = value["last_hash"]
        instance.accepted_hashes = list(accepted)
        instance.state_hash = value["state_hash"]
        return instance


def trial_fixture(trial_id: str) -> dict[str, Any]:
    if trial_id not in TRIAL_IDS:
        raise CoordinatorError("TRIAL_ID_INVALID")
    branch = "promote" if trial_id == PROMOTE_TRIAL_ID else "refuse"
    task_id = trial_id
    request_id = f"ck-p9-live-{branch}-request-r1"
    candidate_id = f"ck-p9-live-{branch}-candidate-r1"
    event_id = f"{trial_id}-event-r1"
    receipt_hash = records.sha256_hex({"trial": trial_id, "kind": "receipt"})
    event_hash = records.sha256_hex({"trial": trial_id, "kind": "event"})
    task_hash = records.sha256_hex({"trial": trial_id, "kind": "task"})
    state_hash = records.sha256_hex({"trial": trial_id, "kind": "state"})
    candidate_hash = records.sha256_hex({"trial": trial_id, "kind": "candidate"})
    request_hash = records.sha256_hex({"trial": trial_id, "kind": "request"})
    response_hash = records.sha256_hex({"trial": trial_id, "kind": "response"})
    result_hash = records.sha256_hex({"trial": trial_id, "kind": "result"})
    projection_hash = records.sha256_hex({"trial": trial_id, "kind": "projection"})
    hashes = {
        "receipt": receipt_hash,
        "event": event_hash,
        "task": task_hash,
        "state": state_hash,
        "candidate": candidate_hash,
        "request": request_hash,
        "response": response_hash,
        "result": result_hash,
        "projection": projection_hash,
    }
    payloads = (
        {"task_id": task_id, "event_id": event_id, "receipt_hash": receipt_hash,
         "task_hash": task_hash, "event_hash": event_hash, "state_hash": state_hash},
        {"vector_id": f"{trial_id}-vector-r1", "task_id": task_id,
         "event_hash": event_hash, "namespace": "ck-p9-completion",
         "vector_digest": records.sha256_hex({"trial": trial_id, "kind": "vector"})},
        {"task_id": task_id, "namespace": "ck-p9-completion", "limit": 8,
         "query_digest": records.sha256_hex({"trial": trial_id, "kind": "query"})},
        {"request_id": request_id, "task_id": task_id, "candidate_id": candidate_id,
         "request_hash": request_hash},
        {"request_id": request_id, "task_id": task_id, "result_hash": result_hash,
         "response_hash": response_hash, "receipt_hash": receipt_hash, "attempt": 1},
        {"request_id": request_id, "projection_id": f"{trial_id}-projection-r1",
         "receipt_hash": receipt_hash, "cursor": 1, "projection_hash": projection_hash},
        {"projection_id": f"{trial_id}-projection-r1", "cursor": 1,
         "resume_hash": records.sha256_hex({"trial": trial_id, "kind": "resume"})},
        {"candidate_id": candidate_id, "receipt_hash": receipt_hash,
         "candidate_hash": candidate_hash, "tampered": branch == "refuse",
         "unsafe": branch == "refuse"},
        {"task_id": task_id, "receipt_hash": receipt_hash,
         "capsule_hash": records.sha256_hex({"trial": trial_id, "kind": "capsule"})},
        {"task_id": task_id,
         "replay_hash": records.sha256_hex({"trial": trial_id, "kind": "replay"}),
         "expected_verdict": "PROMOTE" if branch == "promote" else "REFUSE"},
        {"task_id": task_id, "receipt_hash": receipt_hash, "event_hash": event_hash,
         "limit": 2},
        {"task_id": task_id,
         "cleanup_hash": records.sha256_hex({"trial": trial_id, "kind": "cleanup"})},
    )
    commands: list[dict[str, Any]] = []
    parent = GENESIS_HASH
    for sequence, (operation, payload) in enumerate(zip(ORDER, payloads)):
        command = make_command(trial_id, sequence, parent, operation, payload)
        commands.append(command)
        parent = command["command_hash"]
    return {
        "version": VERSION,
        "campaign_id": CAMPAIGN_ID,
        "trial_id": trial_id,
        "branch": branch,
        "expected_verdict": "PROMOTE" if branch == "promote" else "REFUSE",
        "hashes": hashes,
        "commands": commands,
        "fixture_hash": records.sha256_hex({
            "trial_id": trial_id,
            "expected_verdict": "PROMOTE" if branch == "promote" else "REFUSE",
            "command_hashes": [item["command_hash"] for item in commands],
        }),
    }
