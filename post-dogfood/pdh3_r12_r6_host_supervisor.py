#!/usr/bin/env python3
"""Durable host supervisor for the R6 remote preflight stage.

The remote worker already has its own lifecycle guard. This wrapper protects
the host-side ACK/retrieval process from a terminal or Codex session ending:
the actual stage runs inside a detached screen+caffeinate session, while the
foreground command only observes its terminal receipt. A later terminal can
use ``status`` without launching a second worker or workload.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
STAGE = ROOT / "post-dogfood/pdh3_r12_r6_run_pf2r_pf7.py"


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_config() -> dict[str, object]:
    import pdh3_r12_r6_config as config
    return config.load()


def session_name(campaign: str) -> str:
    suffix = re.sub(r"[^A-Za-z0-9_.-]", "-", campaign)
    return "ck-r6-host-" + suffix[-70:]


def terminal_path(runtime: Path) -> Path:
    return runtime / "PF8_HOST_TERMINAL.json"


def launch_receipt_path(runtime: Path) -> Path:
    return runtime / "HOST_SUPERVISOR_LAUNCH.json"


def screen_alive(name: str) -> bool:
    listing = subprocess.run(
        ["/usr/bin/screen", "-ls"], stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, check=False,
    )
    return listing.returncode == 0 and name in listing.stdout


def command(config: dict[str, object], name: str) -> list[str]:
    return [
        "/usr/bin/screen", "-dmS", name,
        "/usr/bin/caffeinate", "-dimsu",
        "/usr/bin/env", "PYTHONPATH=" + str(ROOT / "post-dogfood"),
        "PDH3_R12_R6_CONFIG=" + str(config["_config_path"]),
        PYTHON, str(STAGE),
    ]


def atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_name("." + path.name + ".part")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def start(config: dict[str, object]) -> int:
    runtime = Path(str(config["runtime"]))
    name = session_name(str(config["campaign_id"]))
    if not Path("/usr/bin/screen").is_file() or not Path("/usr/bin/caffeinate").is_file():
        raise RuntimeError("DURABLE_HOST_RUNTIME_UNAVAILABLE")
    if terminal_path(runtime).exists():
        raise RuntimeError("HOST_STAGE_ALREADY_TERMINAL")
    receipt = launch_receipt_path(runtime)
    if receipt.exists():
        prior = json.loads(receipt.read_bytes())
        if prior.get("session") != name:
            raise RuntimeError("HOST_SUPERVISOR_SESSION_MISMATCH")
        if screen_alive(name):
            return 0
        raise RuntimeError("HOST_SUPERVISOR_LAUNCH_STALE")
    argv = command(config, name)
    completed = subprocess.run(argv, cwd=ROOT, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               check=False)
    if completed.returncode != 0 or not screen_alive(name):
        raise RuntimeError("HOST_SUPERVISOR_DETACH_FAILED")
    body = {
        "version": "ck-pdh3-r12-host-supervisor-launch-v1",
        "campaign_id": config["campaign_id"],
        "packet_sha256": config["packet_sha256"],
        "session": name,
        "command_sha256": sha256_bytes(canonical(argv)),
        "screen": "/usr/bin/screen",
        "caffeinate": "/usr/bin/caffeinate",
        "stage": str(STAGE),
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    atomic_write(receipt, canonical(body))
    return 0


def status(config: dict[str, object]) -> int:
    runtime = Path(str(config["runtime"]))
    terminal = terminal_path(runtime)
    if terminal.is_file():
        value = json.loads(terminal.read_bytes())
        print(json.dumps({"status": "TERMINAL", "terminal": value},
                         sort_keys=True, separators=(",", ":")))
        return 0 if value.get("status") == "GREEN_PENDING_FINAL_GLM" else 1
    name = session_name(str(config["campaign_id"]))
    print(json.dumps({"status": "RUNNING" if screen_alive(name) else "ABSENT",
                      "session": name}, sort_keys=True, separators=(",", ":")))
    return 2 if screen_alive(name) else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "start", "status"))
    args = parser.parse_args()
    config = load_config()
    if args.command == "status":
        return status(config)
    start(config)
    if args.command == "start":
        return 0
    runtime = Path(str(config["runtime"]))
    terminal = terminal_path(runtime)
    deadline = datetime.fromisoformat(
        str(config["terminate_utc"]).replace("Z", "+00:00")
    ).replace(tzinfo=timezone.utc).timestamp()
    while time.time() < deadline:
        if terminal.is_file():
            value = json.loads(terminal.read_bytes())
            print(json.dumps(value, sort_keys=True, separators=(",", ":")), flush=True)
            return 0 if value.get("status") == "GREEN_PENDING_FINAL_GLM" else 1
        time.sleep(5)
    raise RuntimeError("HOST_SUPERVISOR_WAIT_TIMEOUT")


if __name__ == "__main__":
    raise SystemExit(main())
