#!/usr/bin/env python3
"""Launch the R12 observer/workload as a detached, receipt-bound process."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import sys
import time
from typing import Any, Iterable


class LaunchError(RuntimeError):
    """Stable remote-launch failure."""


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: bytes | Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def atomic_new(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb", closefd=True) as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def launch_argv(args: argparse.Namespace) -> list[str]:
    return [
        sys.executable,
        str(args.observer.resolve()),
        "run",
        "--output-dir",
        str(args.network_output.resolve()),
        "--packet-sha256",
        args.packet_sha256,
        "--tracer",
        str(args.tracer.resolve()),
        "--tracer-sha256",
        args.tracer_sha256,
        "--interval-seconds",
        "30",
        "--max-evidence-bytes",
        str(1024**3),
        "--",
        sys.executable,
        str(args.runner.resolve()),
        "--binary",
        str(args.binary.resolve()),
        "--packet",
        str(args.packet.resolve()),
        "--packet-sha256",
        args.packet_sha256,
        "--campaign-id",
        args.campaign_id,
        "--output",
        str(args.output.resolve()),
        "--export-root",
        str(args.export_root.resolve()),
        "--remote-ack-root",
        str(args.remote_ack_root.resolve()),
        "--network-observer-dir",
        str(args.network_output.resolve()),
        "--runtime-root-parent",
        str(args.runtime_parent.resolve()),
        "--pf2-runtime-parent",
        str(args.pf2_runtime_parent.resolve()),
        "--setup-timeout-seconds",
        str(args.setup_timeout_seconds),
        "--host-ack-timeout-seconds",
        str(args.host_ack_timeout_seconds),
    ]


def runtime_environment(args: argparse.Namespace) -> dict[str, str]:
    """Return the complete allowlisted environment for the remote process.

    Keep both system sbin locations explicit for the bounded remote harness
    while discarding every inherited environment variable.  The streaming
    observer and its hash-pinned tracer are passed by explicit absolute paths.
    """
    return {
        "HOME": str(args.empty_home.resolve()),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "PDH3_PACKET_SHA256": args.packet_sha256,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "TZ": "UTC",
    }


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if re.fullmatch(r"[0-9a-f]{64}", args.packet_sha256) is None:
        raise LaunchError("PACKET_SHA256_INVALID")
    if not args.campaign_id.startswith("ck-pdh3-r12-preflight-"):
        raise LaunchError("CAMPAIGN_ID_INVALID")
    for path in (args.observer, args.runner, args.binary, args.packet, args.tracer):
        if not path.resolve().is_file():
            raise LaunchError("LAUNCH_INPUT_MISSING:" + path.name)
    if hashlib.sha256(args.tracer.resolve().read_bytes()).hexdigest() != args.tracer_sha256:
        raise LaunchError("TRACER_SHA256_MISMATCH")
    if args.receipt.exists() or args.log.exists():
        raise LaunchError("LAUNCH_OUTPUT_EXISTS")
    argv = launch_argv(args)
    read_fd, write_fd = os.pipe()
    first = os.fork()
    if first == 0:
        try:
            os.close(read_fd)
            os.setsid()
            second = os.fork()
            if second > 0:
                os.write(write_fd, (str(second) + "\n").encode("ascii"))
                os._exit(0)
            os.close(write_fd)
            args.log.parent.mkdir(parents=True, exist_ok=True)
            log_fd = os.open(args.log, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.dup2(log_fd, 1)
            os.dup2(log_fd, 2)
            if log_fd > 2:
                os.close(log_fd)
            os.chdir(args.workdir.resolve())
            environment = runtime_environment(args)
            os.execve(argv[0], argv, environment)
        except BaseException:
            os._exit(127)
    os.close(write_fd)
    raw_pid = os.read(read_fd, 64)
    os.close(read_fd)
    _, status = os.waitpid(first, 0)
    if status != 0 or not raw_pid.strip().isdigit():
        raise LaunchError("DOUBLE_FORK_FAILED")
    pid = int(raw_pid.strip())
    time.sleep(1)
    try:
        os.kill(pid, 0)
    except OSError as exc:
        raise LaunchError("DETACHED_PROCESS_NOT_ALIVE") from exc
    body = {
        "version": "ck-pdh3-r12-remote-launch-v1",
        "campaign_id": args.campaign_id,
        "packet_sha256": args.packet_sha256,
        "pid": pid,
        "ppid_expected": 1,
        "argv_sha256": digest(argv),
        "log": args.log.name,
        "measured_24h_branch_present": False,
        "running": True,
    }
    record = {**body, "receipt_sha256": digest(body)}
    atomic_new(args.receipt, canonical(record))
    return record


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--observer", type=Path, required=True)
    value.add_argument("--runner", type=Path, required=True)
    value.add_argument("--binary", type=Path, required=True)
    value.add_argument("--packet", type=Path, required=True)
    value.add_argument("--packet-sha256", required=True)
    value.add_argument("--tracer", type=Path, required=True)
    value.add_argument("--tracer-sha256", required=True)
    value.add_argument("--campaign-id", required=True)
    value.add_argument("--workdir", type=Path, required=True)
    value.add_argument("--empty-home", type=Path, required=True)
    value.add_argument("--output", type=Path, required=True)
    value.add_argument("--export-root", type=Path, required=True)
    value.add_argument("--remote-ack-root", type=Path, required=True)
    value.add_argument("--network-output", type=Path, required=True)
    value.add_argument("--runtime-parent", type=Path, required=True)
    value.add_argument("--pf2-runtime-parent", type=Path, required=True)
    value.add_argument("--setup-timeout-seconds", type=int, default=10_800)
    value.add_argument("--host-ack-timeout-seconds", type=int, default=900)
    value.add_argument("--receipt", type=Path, required=True)
    value.add_argument("--log", type=Path, required=True)
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    try:
        record = execute(args)
    except (LaunchError, OSError) as exc:
        print(f"PDH3_R12_REMOTE_LAUNCH_BLOCKED:{type(exc).__name__}:{exc}", file=sys.stderr)
        return 2
    print(canonical(record).decode("utf-8"), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
