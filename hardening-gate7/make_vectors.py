#!/usr/bin/env python3
"""Generate the post-freeze Gate 7 held-out set and valid controls."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


BASE = Path(__file__).resolve().parents[1]
HELDOUT_PATH = BASE / "hardening-gate5" / "heldout_contract.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("MODULE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


heldout = load_module("gate7_heldout_contract", HELDOUT_PATH)


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: bytes | Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def base_record(seed_hash: str, source: str) -> dict[str, Any]:
    payload = {
        "op": "continue",
        "sequence": 1,
        "nonce": seed_hash[24:40],
    }
    return {
        "version": "p4-v1",
        "candidate_id": f"control-{seed_hash[:24]}",
        "source_receipt_hash": digest({"seed": seed_hash, "source": source}),
        "payload": payload,
        "payload_hash": digest(payload),
        "schema_version": "p4-v1",
        "provenance": {"source": source},
        "supported": True,
        "one_use_state": "ISSUED",
        "quarantined": False,
        "policy_veto": False,
        "requested_paths": ["app/state.json"],
        "declared_paths": ["app/state.json"],
    }


def make_control(candidate_commit: str, salt: bytes, source_class: str,
                 variant: int) -> dict[str, Any]:
    seed_hash = digest(
        salt + candidate_commit.encode("ascii") + b"valid-control" +
        source_class.encode("ascii") + bytes([variant])
    )
    vector = {
        "version": "gate7-heldout-control-v1",
        "class": f"valid-control-{source_class}",
        "variant": variant,
        "seed_hash": seed_hash,
        "input": base_record(seed_hash, "gate7-heldout-control"),
        "expected_verdict": "PROMOTE",
        "expected_reason": "VERIFIED",
        "mutation_allowed": False,
    }
    vector["vector_hash"] = digest(vector)
    return vector


def build(candidate_commit: str, salt: bytes) -> dict[str, Any]:
    if len(salt) != 32:
        raise ValueError("SALT_LENGTH_INVALID")
    failures = [
        heldout.derive(candidate_commit, salt, name, variant)
        for name in heldout.CLASSES
        for variant in (1, 2, 3)
    ]
    controls = [
        make_control(candidate_commit, salt, name, index)
        for index, name in enumerate(heldout.CLASSES, start=1)
    ]
    record = {
        "version": "hardening-gate7-vector-set-v1",
        "candidate_commit": candidate_commit,
        "salt_sha256": digest(salt),
        "failure_vectors": failures,
        "valid_controls": controls,
    }
    record["set_hash"] = digest(record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-commit", required=True)
    parser.add_argument("--salt-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record = build(args.candidate_commit, args.salt_file.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
