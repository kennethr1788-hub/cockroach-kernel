#!/usr/bin/env python3
"""Minimal isolated child used only by the EV1 fresh-process preflight canary."""
from __future__ import annotations

import hashlib
import json
import os
import sys


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def main() -> int:
    raw = sys.stdin.buffer.read()
    try:
        request = json.loads(raw)
    except json.JSONDecodeError:
        print(canonical({"status": "INVALID", "reason": "MALFORMED_INPUT"}).decode())
        return 17

    if sys.argv[1:] == ["--fail"]:
        print(canonical({"status": "EXPECTED_FAILURE", "reason": "CANARY"}).decode())
        return 17

    forbidden_environment = sorted(
        key
        for key in os.environ
        if any(token in key.upper() for token in ("CONVERSATION", "TRANSCRIPT", "PROMPT", "SESSION"))
    )
    response = {
        "argv_count": len(sys.argv) - 1,
        "forbidden_environment_keys": forbidden_environment,
        "home_environment_present": "HOME" in os.environ,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "invocation_id": request.get("invocation_id"),
        "status": "FRESH_PROCESS_READY",
    }
    print(canonical(response).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
