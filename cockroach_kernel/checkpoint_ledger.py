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
