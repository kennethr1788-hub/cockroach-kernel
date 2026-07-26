#!/usr/bin/env python3
"""Prove the guard survives launcher exit and enforces exact-ID teardown."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    for executable in ("/usr/bin/screen", "/usr/bin/caffeinate"):
        if not Path(executable).is_file():
            raise RuntimeError(executable + " unavailable")
    root = Path(tempfile.mkdtemp(prefix="ck-s2-guard-proof."))
    state = root / "state.json"
    log = root / "guard.jsonl"
    fake = HERE / "fake_runpodctl.py"
    fake.chmod(0o700)
    state.write_text(json.dumps({"id": "pod-s2-proof", "name": "ck-s2-proof-a01",
                                 "desiredStatus": "RUNNING"}))
    environment = os.environ.copy()
    environment["FAKE_RUNPOD_STATE"] = str(state)
    now = int(time.time())
    session = "ck-s2-guard-proof-" + str(os.getpid())
    command = ["/usr/bin/screen", "-dmS", session, "/usr/bin/caffeinate", "-dimsu",
               sys.executable, str(HERE / "lifecycle_guard.py"),
               "--runpodctl", str(fake), "--runpodctl-sha256", digest(fake),
               "--pod-id", "pod-s2-proof", "--pod-name", "ck-s2-proof-a01",
               "--campaign-prefix", "ck-s2-proof-", "--stop-epoch", str(now + 2),
               "--delete-epoch", str(now + 4), "--heartbeat-seconds", "1",
               "--log", str(log)]
    subprocess.run(command, check=True, env=environment)
    # The launcher exits immediately; the screen-owned guard must continue.
    time.sleep(1)
    listing = subprocess.run(["/usr/bin/screen", "-ls"], text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if session not in listing.stdout or not log.exists():
        raise RuntimeError("detached guard did not survive launcher exit")
    deadline = time.time() + 15
    while time.time() < deadline:
        if log.exists() and "TEARDOWN_GREEN" in log.read_text():
            break
        time.sleep(0.5)
    else:
        raise RuntimeError("guard did not finish")
    if state.exists():
        raise RuntimeError("synthetic Pod residue")
    records = [json.loads(line) for line in log.read_text().splitlines()]
    previous = "0" * 64
    for sequence, record in enumerate(records, 1):
        if record["sequence"] != sequence or record["previous_hash"] != previous:
            raise RuntimeError("guard chain mismatch")
        core = dict(record)
        event_hash = core.pop("event_hash")
        calculated = hashlib.sha256(json.dumps(
            core, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False).encode()).hexdigest()
        if calculated != event_hash:
            raise RuntimeError("guard event hash mismatch")
        previous = event_hash
    summary = {"status": "GREEN", "detached_session": session,
               "events": len(records), "terminal_hash": previous,
               "bound": records[0]["event"] == "BOUND",
               "teardown": records[-1]["event"] == "TEARDOWN_GREEN",
               "state_absent": not state.exists()}
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    shutil.rmtree(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
