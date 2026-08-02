#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pdh3_r12_r6_config as r6_config


CONFIG = r6_config.load()
ROOT = Path(CONFIG["root"])
RUNTIME = Path(CONFIG["runtime"])
LAUNCH_START = datetime.fromisoformat(CONFIG["launch_start_utc"].replace("Z", "+00:00"))
STAGES = (
    ("PF4_CREATE", ROOT / "post-dogfood/pdh3_r12_r6_launch_pf4.py"),
    ("PF4_CAPABILITY", ROOT / "post-dogfood/pdh3_r12_r6_run_pf4.py"),
    ("PF2R_PF7_AND_PF8", ROOT / "post-dogfood/pdh3_r12_r6_run_pf2r_pf7.py"),
)


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()


def atomic_write(path: Path, raw: bytes) -> None:
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


def main() -> int:
    last = 0.0
    while datetime.now(timezone.utc) < LAUNCH_START:
        now = time.monotonic()
        if now - last >= 30:
            remaining = max(0, int((LAUNCH_START - datetime.now(timezone.utc)).total_seconds()))
            print(canonical({"stage": "WAITING_FOR_FROZEN_WINDOW", "seconds_remaining": remaining}).decode(), flush=True)
            last = now
        time.sleep(5)
    for stage, script in STAGES:
        print(canonical({"stage": stage, "status": "STARTING",
                         "utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}).decode(), flush=True)
        completed = subprocess.run(
            [sys.executable, str(script)], cwd=ROOT, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=None,
            check=False, shell=False,
        )
        atomic_write(RUNTIME / (stage.lower() + ".stdout"), completed.stdout)
        atomic_write(RUNTIME / (stage.lower() + ".stderr"), completed.stderr)
        print(canonical({"stage": stage, "returncode": completed.returncode,
                         "stdout_bytes": len(completed.stdout), "stderr_bytes": len(completed.stderr),
                         "status": "GREEN" if completed.returncode == 0 else "BLOCKED"}).decode(), flush=True)
        if completed.returncode != 0:
            atomic_write(RUNTIME / "ORCHESTRATOR_BLOCKED.json", canonical({
                "stage": stage, "returncode": completed.returncode,
                "status": "PDH3_R12_PREFLIGHT_BLOCKED",
                "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }))
            return completed.returncode
    atomic_write(RUNTIME / "ORCHESTRATOR_COMPLETE.json", canonical({
        "status": "GREEN_PENDING_FINAL_GLM",
        "measured_24h_started": False,
        "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
