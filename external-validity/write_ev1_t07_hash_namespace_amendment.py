#!/usr/bin/env python3
"""Write an append-only clarification of the two EV1-T07 packet namespaces."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import time


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / ".ev1-runtime" / "EV1-T07" / "control"
OUTPUT = CONTROL / "HASH_NAMESPACE_AMENDMENT_R1.json"
GLOBAL_PACKET = ROOT / "EXTERNAL_VALIDITY_EV1_PREFLIGHT_PACKET_R3.md"
LOCAL_PACKET = CONTROL / "EV1_T07_CAPTURE_ONLY_PREFLIGHT_PACKET_R2.md"
LOCAL_PREFLIGHT = CONTROL / "CAPTURE_ONLY_PREFLIGHT_RECEIPT_R2.json"
LOCAL_JUDGES = CONTROL / "CAPTURE_ONLY_JUDGE_RECEIPT_R2.json"
RESULT = CONTROL / "CAPTURE_INVALID_RESULT_RECEIPT.json"
GLOBAL_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
LOCAL_SHA256 = "3ea307c17d9f80ede66600f91f8becee6c2a8b6d480e22919d36b70ec311555e"


def digest(raw: bytes | Path) -> str:
    value = raw.read_bytes() if isinstance(raw, Path) else raw
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def atomic(path: Path, raw: bytes) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError("T07_HASH_NAMESPACE_AMENDMENT_EXISTS")
    preflight = load(LOCAL_PREFLIGHT)
    judges = load(LOCAL_JUDGES)
    result = load(RESULT)
    if digest(GLOBAL_PACKET) != GLOBAL_SHA256:
        raise RuntimeError("GLOBAL_EV1_PACKET_DRIFT")
    if digest(LOCAL_PACKET) != LOCAL_SHA256:
        raise RuntimeError("LOCAL_CAPTURE_PACKET_DRIFT")
    if preflight.get("preflight_packet_sha256") != GLOBAL_SHA256:
        raise RuntimeError("GLOBAL_FIELD_BINDING_DRIFT")
    if judges.get("packet_sha256") != LOCAL_SHA256 or result.get("packet_sha256") != LOCAL_SHA256:
        raise RuntimeError("LOCAL_FIELD_BINDING_DRIFT")
    body = {
        "version": "ev1-t07-hash-namespace-amendment-v1",
        "status": "EV1_T07_HASH_NAMESPACE_CLARIFIED_APPEND_ONLY",
        "task_id": "EV1-T07",
        "original_receipts_modified": False,
        "original_blocked_judge_output_preserved": True,
        "ambiguous_original_field": "preflight_packet_sha256",
        "ambiguous_original_field_location": ".ev1-runtime/EV1-T07/control/CAPTURE_ONLY_PREFLIGHT_RECEIPT_R2.json",
        "ambiguous_original_field_semantics": "GLOBAL_EV1_R3_PREFLIGHT_PACKET_SHA256",
        "global_ev1_preflight_packet": {
            "path": "EXTERNAL_VALIDITY_EV1_PREFLIGHT_PACKET_R3.md",
            "sha256": GLOBAL_SHA256,
            "receipt_field_value": preflight["preflight_packet_sha256"],
        },
        "local_capture_only_preflight_packet": {
            "path": ".ev1-runtime/EV1-T07/control/EV1_T07_CAPTURE_ONLY_PREFLIGHT_PACKET_R2.md",
            "sha256": LOCAL_SHA256,
            "judge_receipt_field_value": judges["packet_sha256"],
            "result_receipt_field_value": result["packet_sha256"],
        },
        "classification": "LABEL_NAMESPACE_AMBIGUITY_NOT_HASH_VALUE_CONTRADICTION",
        "product_result_changed": False,
        "capture_rerun": False,
        "workspace_mutated": False,
        "deletion_or_recovery_performed": False,
        "utc_recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    receipt_hash = digest(canonical(body))
    atomic(OUTPUT, canonical(dict(body, receipt_sha256=receipt_hash)) + b"\n")
    print(canonical({"file_sha256": digest(OUTPUT), "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
