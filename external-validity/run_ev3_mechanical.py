#!/usr/bin/env python3
"""Run EV3 mechanical tests and write hash-bound preflight evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ROOT / "external-validity" / "ev3_actor_routes.py",
    ROOT / "external-validity" / "ev3_campaign.py",
    ROOT / "external-validity" / "test_ev3_campaign.py",
    Path(__file__).resolve(),
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_atomic(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def run(name: str, command: list[str], output_root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, timeout=600, check=False
    )
    raw = (completed.stdout + completed.stderr).encode()
    write_atomic(output_root / f"{name}.log", raw)
    match = re.findall(r"Ran (\d+) tests?", raw.decode(errors="replace"))
    return {
        "name": name,
        "command": command,
        "exit": completed.returncode,
        "log_sha256": digest(raw),
        "tests": sum(int(value) for value in match),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    if args.output_root.exists():
        raise SystemExit("OUTPUT_ROOT_EXISTS")
    args.output_root.mkdir(parents=True, mode=0o700)
    commands = (
        ("compile", ["python3.12", "-m", "py_compile", *[str(path.relative_to(ROOT)) for path in SOURCES]]),
        ("ev3", ["python3.12", "external-validity/test_ev3_campaign.py"]),
        ("kernel_public", ["python3.12", "-m", "unittest", "-v", "cockroach_kernel.test_cli", "cockroach_kernel.test_http_api"]),
        ("p4", ["python3.12", "-m", "unittest", "discover", "-s", "p4-verifier", "-p", "test*.py", "-v"]),
        ("p7", ["python3.12", "-m", "unittest", "discover", "-s", "p7-recovery", "-p", "test*.py", "-v"]),
        ("r3_hidden", ["python3.12", "fresh-context-black-box/test_r3_hidden_campaign.py"]),
        ("r3_preflight", ["python3.12", "fresh-context-black-box/test_r3_preflight.py"]),
        ("r4_hidden", ["python3.12", "fresh-context-black-box/test_r4_hidden_campaign.py"]),
        ("r4_public", ["python3.12", "fresh-context-black-box/test_r4_public_canary_r2.py"]),
    )
    results = [run(name, command, args.output_root) for name, command in commands]
    staged = Path(tempfile.mkdtemp(prefix="ck-ev3-scan-", dir="/private/tmp"))
    try:
        for source in SOURCES:
            shutil.copy2(source, staged / source.name)
        gitleaks_path = args.output_root / "gitleaks.json"
        gitleaks = subprocess.run(
            [
                "gitleaks", "detect", "--no-git", "--source", str(staged),
                "--report-format", "json", "--report-path", str(gitleaks_path),
            ],
            cwd=ROOT, text=True, capture_output=True, timeout=120, check=False,
        )
        if not gitleaks_path.exists():
            write_atomic(gitleaks_path, b"[]\n")
        detect = subprocess.run(
            ["detect-secrets", "scan", *[str(path) for path in SOURCES]],
            cwd=ROOT, text=True, capture_output=True, timeout=120, check=False,
        )
        write_atomic(args.output_root / "detect-secrets.json", detect.stdout.encode())
    finally:
        shutil.rmtree(staged, ignore_errors=False)
    private_pattern = re.compile(rb"/Users/|\$HOME|~/|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{16,}")
    private_hits = {
        path.relative_to(ROOT).as_posix(): len(private_pattern.findall(path.read_bytes()))
        for path in SOURCES[:2]
    }
    body = {
        "version": "ck-ev3-mechanical-receipt-v1",
        "commands": results,
        "tests": sum(item["tests"] for item in results),
        "command_failures": sum(item["exit"] != 0 for item in results),
        "gitleaks_exit": gitleaks.returncode,
        "gitleaks_sha256": digest(gitleaks_path.read_bytes()),
        "detect_secrets_exit": detect.returncode,
        "detect_secrets_sha256": digest((args.output_root / "detect-secrets.json").read_bytes()),
        "private_path_or_credential_marker_hits": private_hits,
        "source_sha256": {
            path.relative_to(ROOT).as_posix(): digest(path.read_bytes()) for path in SOURCES
        },
        "scan_runtime_teardown_verified": not staged.exists(),
    }
    body["status"] = "GREEN" if (
        body["command_failures"] == 0
        and gitleaks.returncode == 0
        and detect.returncode == 0
        and not any(private_hits.values())
        and body["scan_runtime_teardown_verified"]
    ) else "NOT_GREEN"
    body["receipt_sha256"] = digest(canonical(body))
    write_atomic(args.output_root / "FINAL_RECEIPT.json", canonical(body) + b"\n")
    print(canonical(body).decode())
    return 0 if body["status"] == "GREEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
