"""Hash-bound recovery checkpoint records and parameterized Cockroach insert."""
from __future__ import annotations

from typing import Any
import re

from .continuation_brief import canonical_json, digest

HASH = re.compile(r"^[0-9a-f]{64}$")
CHECKPOINT_VERSION = "ck-recovery-checkpoint-v1"

# A deployment adapter may execute this with positional parameters. The core
# recovery path never opens a connection or executes this statement.
CHECKPOINT_INSERT_SQL = (
    "INSERT INTO ck.recovery_checkpoints "
    "(checkpoint_id, task_id, parent_hash, request_hash, decision_hash, "
    "receipt_hash, preservation_hash, verdict, recovered_paths, record_json, "
    "record_hash) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11) "
    "ON CONFLICT (checkpoint_id) DO NOTHING"
)

CHECKPOINT_READBACK_SQL = (
    "SELECT record_json, record_hash FROM ck.recovery_checkpoints "
    "WHERE checkpoint_id = $1"
)


class CheckpointError(ValueError):
    pass


def _hash(value: Any, name: str) -> str:
    if not isinstance(value, str) or not HASH.fullmatch(value):
        raise CheckpointError(f"{name}_HASH_INVALID")
    return value


def build_checkpoint(*, request_id: str, task_id: str, parent_hash: str,
                     request_hash: str, decision_hash: str, receipt_hash: str,
                     preservation_hash: str, verdict: str,
                     recovered_paths: list[str], record_hash: str | None = None) -> dict[str, Any]:
    if not isinstance(request_id, str) or not request_id:
        raise CheckpointError("CHECKPOINT_ID_INVALID")
    if not isinstance(task_id, str) or not task_id:
        raise CheckpointError("TASK_ID_INVALID")
    for value, name in ((parent_hash, "PARENT"), (request_hash, "REQUEST"),
                        (decision_hash, "DECISION"), (receipt_hash, "RECEIPT"),
                        (preservation_hash, "PRESERVATION")):
        _hash(value, name)
    if verdict not in {"PROMOTE", "REFUSE", "INVALID", "NO_ACTION"}:
        raise CheckpointError("VERDICT_INVALID")
    if (not isinstance(recovered_paths, list)
            or any(not isinstance(path, str) or not path or path.startswith("/")
                   or ".." in path.split("/") for path in recovered_paths)):
        raise CheckpointError("RECOVERED_PATHS_INVALID")
    body = {
        "version": CHECKPOINT_VERSION,
        "checkpoint_id": request_id,
        "task_id": task_id,
        "parent_hash": parent_hash,
        "request_hash": request_hash,
        "decision_hash": decision_hash,
        "receipt_hash": receipt_hash,
        "preservation_hash": preservation_hash,
        "verdict": verdict,
        "recovered_paths": sorted(set(recovered_paths)),
        "append_only": True,
        "no_side_effects_in_builder": True,
    }
    expected = digest(body)
    if record_hash is not None and record_hash != expected:
        raise CheckpointError("CHECKPOINT_HASH_MISMATCH")
    return dict(body, record_hash=expected)


def validate_checkpoint(record: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict) or record.get("version") != CHECKPOINT_VERSION:
        raise CheckpointError("CHECKPOINT_VERSION_UNSUPPORTED")
    supplied = record.get("record_hash")
    if not isinstance(supplied, str) or not HASH.fullmatch(supplied):
        raise CheckpointError("CHECKPOINT_HASH_INVALID")
    body = dict(record)
    body.pop("record_hash")
    if supplied != digest(body):
        raise CheckpointError("CHECKPOINT_HASH_MISMATCH")
    return record


def persist_checkpoint(connection: Any, record: dict[str, Any]) -> dict[str, Any]:
    """Write and hash-verify one checkpoint through an injected DB adapter.

    The function owns no connection lifecycle and performs no network access;
    callers must supply a bounded, read/write transaction and close it. A
    duplicate checkpoint is accepted only when the read-back bytes match.
    """
    validate_checkpoint(record)
    params = (
        record["checkpoint_id"], record["task_id"], record["parent_hash"],
        record["request_hash"], record["decision_hash"], record["receipt_hash"],
        record["preservation_hash"], record["verdict"],
        canonical_json(record["recovered_paths"]).decode("utf-8"),
        canonical_json(record).decode("utf-8"), record["record_hash"],
    )
    connection.run(CHECKPOINT_INSERT_SQL, *params)
    rows = connection.run(CHECKPOINT_READBACK_SQL, record["checkpoint_id"])
    if len(rows) != 1:
        raise CheckpointError("CHECKPOINT_READBACK_MISSING")
    raw_json, stored_hash = rows[0]
    if stored_hash != record["record_hash"]:
        raise CheckpointError("CHECKPOINT_READBACK_HASH_MISMATCH")
    if isinstance(raw_json, str):
        import json
        raw_json = json.loads(raw_json)
    if raw_json != record:
        raise CheckpointError("CHECKPOINT_READBACK_RECORD_MISMATCH")
    return record
