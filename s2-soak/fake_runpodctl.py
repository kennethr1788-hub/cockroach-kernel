#!/usr/bin/env python3
"""Synthetic provider surface for local lifecycle-guard proof only."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> int:
    state_path = Path(os.environ["FAKE_RUNPOD_STATE"])
    args = [arg for arg in sys.argv[1:] if arg not in ("--output", "json")]
    state = json.loads(state_path.read_text()) if state_path.exists() else None
    if args[:2] == ["pod", "get"]:
        if state is None or state.get("id") != args[2]:
            print(json.dumps({"statusCode": 404, "message": "Pod not found"}))
            return 1
        print(json.dumps(state))
        return 0
    if args[:3] == ["pod", "list", "--all"]:
        print(json.dumps([state] if state is not None else []))
        return 0
    if args[:2] == ["pod", "stop"]:
        if state is None or state.get("id") != args[2]:
            print(json.dumps({"statusCode": 404, "message": "Pod not found"}))
            return 1
        state["desiredStatus"] = "EXITED"
        state_path.write_text(json.dumps(state))
        print(json.dumps(state))
        return 0
    if args[:2] == ["pod", "delete"]:
        if state is None or state.get("id") != args[2]:
            print(json.dumps({"statusCode": 404, "message": "Pod not found"}))
            return 1
        state_path.unlink()
        print(json.dumps({"deleted": args[2]}))
        return 0
    print("unsupported", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
