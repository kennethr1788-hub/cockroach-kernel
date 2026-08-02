#!/usr/bin/env python3
"""Host-local detached RunPod lifecycle-guard launcher for PDH-3 R12.

The provider credential remains on the operator host. It is passed only to the
local exact-ID guard process, never written to receipts, argv, logs, or the Pod.
Startup is GREEN only after a hash-valid `BOUND` event is observed.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Callable


class LifecycleLaunchError(RuntimeError):
    """Stable host-side lifecycle-launch failure."""


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def guard_environment(empty_home: Path, source: dict[str, str] | None = None) -> dict[str, str]:
    inherited = os.environ if source is None else source
    api_key = inherited.get("RUNPOD_API_KEY", "")
    if not api_key:
        raise LifecycleLaunchError("RUNPOD_API_KEY_UNAVAILABLE")
    empty_home.mkdir(parents=True, exist_ok=True, mode=0o700)
    return {
        "HOME": str(empty_home.resolve()),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "RUNPOD_API_KEY": api_key,
        "TZ": "UTC",
    }


def read_chain(path: Path) -> list[dict[str, Any]]:
    if not path.is_file() or path.is_symlink():
        return []
    records: list[dict[str, Any]] = []
    previous = "0" * 64
    for expected_sequence, raw in enumerate(path.read_bytes().splitlines(), 1):
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LifecycleLaunchError("GUARD_CHAIN_JSON_INVALID") from exc
        if not isinstance(record, dict):
            raise LifecycleLaunchError("GUARD_CHAIN_RECORD_INVALID")
        core = {key: value for key, value in record.items() if key != "event_hash"}
        if record.get("sequence") != expected_sequence:
            raise LifecycleLaunchError("GUARD_CHAIN_SEQUENCE_INVALID")
        if record.get("previous_hash") != previous:
            raise LifecycleLaunchError("GUARD_CHAIN_PREVIOUS_HASH_INVALID")
        computed = hashlib.sha256(canonical(core)).hexdigest()
        if record.get("event_hash") != computed:
            raise LifecycleLaunchError("GUARD_CHAIN_EVENT_HASH_INVALID")
        previous = computed
        records.append(record)
    return records


def wait_for_bound(
    *,
    log: Path,
    pid: int,
    pod_id: str,
    pod_name: str,
    campaign_prefix: str,
    timeout_seconds: float,
    poll_seconds: float = 0.25,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    if timeout_seconds <= 0 or poll_seconds <= 0:
        raise LifecycleLaunchError("GUARD_WAIT_INVALID")
    deadline = monotonic() + timeout_seconds
    while monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError as exc:
            raise LifecycleLaunchError("GUARD_EXITED_BEFORE_BOUND") from exc
        records = read_chain(log)
        for record in records:
            event = record.get("event")
            if event == "GUARD_BLOCKED":
                raise LifecycleLaunchError("GUARD_REPORTED_BLOCKED")
            if event != "BOUND":
                continue
            details = record.get("details")
            if not isinstance(details, dict):
                raise LifecycleLaunchError("GUARD_BOUND_DETAILS_INVALID")
            if (
                details.get("pod_id") != pod_id
                or details.get("name") != pod_name
                or details.get("campaign_prefix") != campaign_prefix
            ):
                raise LifecycleLaunchError("GUARD_BOUND_IDENTITY_MISMATCH")
            return record
        sleep(min(poll_seconds, max(0.0, deadline - monotonic())))
    raise LifecycleLaunchError("GUARD_BOUND_TIMEOUT")


def launch_detached(
    *,
    argv: list[str],
    cwd: Path,
    process_log: Path,
    empty_home: Path,
    source_environment: dict[str, str] | None = None,
) -> int:
    if not argv or not Path(argv[0]).is_file():
        raise LifecycleLaunchError("GUARD_ARGV_INVALID")
    if process_log.exists() or process_log.is_symlink():
        raise LifecycleLaunchError("GUARD_PROCESS_LOG_EXISTS")
    environment = guard_environment(empty_home, source_environment)
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
            os.chdir(cwd.resolve())
            output_fd = os.open(
                process_log,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
            os.dup2(output_fd, 1)
            os.dup2(output_fd, 2)
            if output_fd > 2:
                os.close(output_fd)
            os.execve(argv[0], argv, environment)
        except BaseException:
            os._exit(127)
    os.close(write_fd)
    raw = os.read(read_fd, 64)
    os.close(read_fd)
    _, status = os.waitpid(first, 0)
    if status != 0 or not raw.strip().isdigit():
        raise LifecycleLaunchError("GUARD_DOUBLE_FORK_FAILED")
    pid = int(raw.strip())
    completed = subprocess.run(
        ["/bin/ps", "-o", "ppid=", "-p", str(pid)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
        check=False,
    )
    if completed.returncode != 0 or completed.stdout.strip() != b"1":
        raise LifecycleLaunchError("GUARD_NOT_DETACHED")
    return pid
