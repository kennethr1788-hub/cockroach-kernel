"""Canonical primitives for the append-only external-validity campaign."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


VERSION = "ck-external-validity-v1"


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def write_atomic(path: Path, value: Any) -> str:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical(value) + b"\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return hashlib.sha256(payload).hexdigest()


def chained_receipt(
    *, campaign_id: str, sequence: int, kind: str, result: str,
    details: dict[str, Any], previous_hash: str,
) -> dict[str, Any]:
    core = {
        "version": VERSION,
        "campaign_id": campaign_id,
        "sequence": sequence,
        "kind": kind,
        "result": result,
        "details": details,
        "previous_hash": previous_hash,
    }
    return {**core, "receipt_hash": sha256(core)}
