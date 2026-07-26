#!/usr/bin/env python3
"""Bounded local proof for coordinator-guard GREEN and fail-stop paths."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

import protocol

BASE = Path(__file__).resolve().parents[1]


def write_chain(path: Path, event: str, details: dict) -> None:
    core = {
        "version": "proof-log-v1", "campaign_id": "ck-s3-guard-proof",
        "sequence": 1, "previous_hash": protocol.GENESIS_HASH,
        "event": event, "details": details,
        "utc": "2026-07-26T00:00:00Z", "monotonic_ns": 1,
    }
    path.write_bytes(protocol.canonical({**core, "event_hash": protocol.sha256(core)}) + b"\n")


def write_state(path: Path, pod_id: str, name: str) -> None:
    path.write_text(json.dumps({"id": pod_id, "name": name,
                                "desiredStatus": "RUNNING"}), encoding="utf-8")


def run_case(root: Path, green: bool) -> dict:
    root.mkdir()
    protocol_copy = root / "protocol.py"
    allowlist = root / "allowlist.json"
    fake_cli = root / "runpodctl"
    shutil.copy2(Path(__file__).parent / "protocol.py", protocol_copy)
    shutil.copy2(BASE / "S3_RESOURCE_ALLOWLIST_R1.json", allowlist)
    shutil.copy2(BASE / "s2-soak/fake_runpodctl.py", fake_cli)
    fake_cli.chmod(0o700)
    coordinator_log = root / "coordinator.ndjson"
    bridge_log = root / "bridge.ndjson"
    runpod_log = root / "runpod.ndjson"
    completion = root / "complete"
    stop_marker = root / "stop.json"
    guard_log = root / "guard.ndjson"
    write_chain(coordinator_log, "COORDINATOR_GREEN" if green else "HEARTBEAT",
                {"lambda_calls": 0, "cockroach_operations": 0})
    write_chain(bridge_log, "BRIDGE_GREEN" if green else "HEARTBEAT", {})
    write_chain(runpod_log, "HEARTBEAT", {})
    if green:
        completion.write_text("GREEN", encoding="utf-8")
    pod_id = "proof-pod"
    name = "ck-s3-guard-proof-a1"
    state = root / "provider.json"
    write_state(state, pod_id, name)
    sleepers = [subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"]
    ) for _ in range(3)]
    env = os.environ.copy()
    env["FAKE_RUNPOD_STATE"] = str(state)
    command = [
        sys.executable, str(Path(__file__).parent / "coordinator_guard.py"),
        "--coordinator-pid", str(sleepers[0].pid),
        "--bridge-pid", str(sleepers[1].pid),
        "--runpod-guard-pid", str(sleepers[2].pid),
        "--coordinator-log", str(coordinator_log), "--bridge-log", str(bridge_log),
        "--runpod-guard-log", str(runpod_log), "--completion-marker", str(completion),
        "--protocol-file", str(protocol_copy), "--protocol-sha256", protocol.sha256(protocol_copy.read_bytes()),
        "--resource-allowlist", str(allowlist), "--resource-allowlist-sha256", protocol.sha256(allowlist.read_bytes()),
        "--lambda-call-ceiling", "12", "--cockroach-operation-ceiling", "108",
        "--runpodctl", str(fake_cli), "--runpodctl-sha256", protocol.sha256(fake_cli.read_bytes()),
        "--pod-id", pod_id, "--pod-name", name, "--campaign-prefix", "ck-s3-guard-proof-",
        "--deadline-epoch", str(int(time.time()) + 20), "--stale-seconds", "1",
        "--startup-grace-seconds", "1", "--log", str(guard_log),
        "--stop-marker", str(stop_marker),
    ]
    result = subprocess.run(command, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=15, check=False)
    for sleeper in sleepers:
        if sleeper.poll() is None:
            sleeper.terminate()
            sleeper.wait(timeout=5)
    return {
        "green_case": green,
        "exit": result.returncode,
        "state_exists": state.exists(),
        "stop_marker": stop_marker.exists(),
        "guard_log_hash": protocol.sha256(guard_log.read_bytes()),
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="s3-coordinator-guard-proof-") as temporary:
        root = Path(temporary)
        green = run_case(root / "green", True)
        blocked = run_case(root / "blocked", False)
        if green["exit"] != 0 or not green["state_exists"] or green["stop_marker"]:
            raise SystemExit("GREEN_CASE_FAILED")
        if blocked["exit"] == 0 or blocked["state_exists"] or not blocked["stop_marker"]:
            raise SystemExit("BLOCKED_CASE_FAILED")
        result = {"version": "s3-coordinator-guard-proof-v1",
                  "green": green, "blocked": blocked, "status": "GREEN"}
        result["proof_hash"] = protocol.sha256(result)
        print(protocol.canonical(result).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
