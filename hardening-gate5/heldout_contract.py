#!/usr/bin/env python3
"""Frozen post-candidate held-out vector generator contract for Gate 7.

The implementation is frozen at Gate 5. The 32-byte campaign salt is created
only after the candidate commit is immutable and is never exposed to a builder
before freeze. Public evidence records the salt hash, not the salt bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any


CLASSES = (
    "tampered-receipt", "replayed-warrant", "malformed-record",
    "unsupported-value", "quarantined-candidate", "incomplete-evidence",
    "interrupted-consumption",
)
HEX_COMMIT = re.compile(r"^[0-9a-f]{40,64}$")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def digest(value: bytes | Any) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def derive(candidate_commit: str, salt: bytes, vector_class: str,
           variant: int) -> dict[str, Any]:
    if not HEX_COMMIT.fullmatch(candidate_commit):
        raise ValueError("CANDIDATE_COMMIT_INVALID")
    if len(salt) != 32 or vector_class not in CLASSES or variant not in {1, 2, 3}:
        raise ValueError("HELDOUT_KEY_INVALID")
    seed_hash = digest(salt + candidate_commit.encode() +
                       vector_class.encode() + bytes([variant]))
    base = {
        "version": "p4-v1", "candidate_id": f"heldout-{seed_hash[:24]}",
        "source_receipt_hash": digest({"seed": seed_hash, "source": "heldout"}),
        "payload": {"op": "continue", "sequence": variant, "nonce": seed_hash[24:40]},
        "schema_version": "p4-v1", "provenance": {"source": "gate7-heldout"},
        "supported": True, "one_use_state": "ISSUED", "quarantined": False,
        "policy_veto": False, "requested_paths": ["app/state.json"],
        "declared_paths": ["app/state.json"],
    }
    base["payload_hash"] = digest(base["payload"])
    expected = ("REFUSE", "UNSPECIFIED")
    if vector_class == "tampered-receipt":
        base["payload_hash"] = "0" * 64
        expected = ("REFUSE", "HASH_MISMATCH")
    elif vector_class == "replayed-warrant":
        base["one_use_state"] = "CONSUMED"
        expected = ("REFUSE", "REPLAYED_TICKET")
    elif vector_class == "malformed-record":
        base["unexpected"] = seed_hash
        expected = ("INVALID", "UNKNOWN_FIELD")
    elif vector_class == "unsupported-value":
        base["schema_version"] = "p4-heldout-unsupported"
        expected = ("REFUSE", "UNSUPPORTED_SCHEMA")
    elif vector_class == "quarantined-candidate":
        base["quarantined"] = True
        expected = ("REFUSE", "QUARANTINED_INPUT")
    elif vector_class == "incomplete-evidence":
        del base["source_receipt_hash"]
        expected = ("INVALID", "MISSING_FIELD")
    elif vector_class == "interrupted-consumption":
        base["payload"]["fault"] = "interrupt-after-consume"
        base["payload_hash"] = digest(base["payload"])
        expected = ("REFUSE", "RECOVERY_INTERRUPTED_FAIL_CLOSED")
    vector = {
        "version": "gate7-heldout-vector-v1",
        "class": vector_class,
        "variant": variant,
        "seed_hash": seed_hash,
        "input": base,
        "expected_verdict": expected[0],
        "expected_reason": expected[1],
        "mutation_allowed": False,
    }
    vector["vector_hash"] = digest(vector)
    return vector


def known_preflight_vectors() -> list[dict[str, Any]]:
    salt = bytes.fromhex("42" * 32)
    commit = "1" * 40
    return [derive(commit, salt, "tampered-receipt", 1),
            derive(commit, salt, "replayed-warrant", 1)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-commit", required=True)
    parser.add_argument("--salt-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    salt = args.salt_file.read_bytes()
    vectors = [derive(args.candidate_commit, salt, name, variant)
               for name in CLASSES for variant in (1, 2, 3)]
    payload = {
        "version": "gate7-heldout-set-v1",
        "candidate_commit": args.candidate_commit,
        "salt_sha256": digest(salt),
        "vectors": vectors,
    }
    payload["set_hash"] = digest(payload)
    args.output.write_bytes(canonical(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
