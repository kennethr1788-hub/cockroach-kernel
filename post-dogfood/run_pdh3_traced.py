#!/usr/bin/env python3
"""Run one PDH-3 command under complete process-tree network syscall tracing.

This is evidence infrastructure, not a network namespace or firewall. It
follows every descendant with strace, permits only loopback, Unix, netlink, and
AF_UNSPEC destinations, terminates the process group when a non-loopback or
unparseable connect/sendto call is observed, and emits a canonical receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time
from typing import Any


VERSION = "ck-pdh3-process-tree-egress-observer-v1"
SYSCALL = re.compile(r"\b(connect|sendto)\(")
IPV4 = re.compile(r'inet_addr\("([^"]+)"\)')
IPV6 = re.compile(r'inet_pton\(AF_INET6,\s*"([^"]+)"')
PERMITTED_FAMILIES = ("AF_UNIX", "AF_NETLINK", "AF_UNSPEC")


class TraceFailure(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def atomic_write(path: Path, raw: bytes) -> None:
    if path.exists():
        raise TraceFailure("RECEIPT_EXISTS")
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


def classify_line(line: str) -> tuple[str, str] | None:
    match = SYSCALL.search(line)
    if match is None:
        return None
    syscall = match.group(1)
    if any(family in line for family in PERMITTED_FAMILIES):
        return ("PERMITTED_LOCAL_KERNEL", syscall)
    if "AF_INET6" in line:
        address = IPV6.search(line)
        if address is None:
            return ("BLOCK_UNPARSEABLE_INET6", syscall)
        try:
            permitted = ipaddress.ip_address(address.group(1)).is_loopback
        except ValueError:
            return ("BLOCK_UNPARSEABLE_INET6", syscall)
        return ("PERMITTED_LOOPBACK" if permitted else "BLOCK_EXTERNAL", syscall)
    if "AF_INET" in line:
        address = IPV4.search(line)
        if address is None:
            return ("BLOCK_UNPARSEABLE_INET", syscall)
        try:
            permitted = ipaddress.ip_address(address.group(1)).is_loopback
        except ValueError:
            return ("BLOCK_UNPARSEABLE_INET", syscall)
        return ("PERMITTED_LOOPBACK" if permitted else "BLOCK_EXTERNAL", syscall)
    return ("BLOCK_UNPARSEABLE_FAMILY", syscall)


def terminate_group(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=10)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=10)


def trace_files(prefix: Path) -> list[Path]:
    return sorted(
        path
        for path in prefix.parent.glob(prefix.name + ".*")
        if path.is_file() and not path.is_symlink()
    )


def scan_incremental(
    prefix: Path,
    offsets: dict[Path, int],
    maximum_bytes: int,
) -> tuple[dict[str, int], list[dict[str, str]], int]:
    counts = {
        "connect": 0,
        "sendto": 0,
        "permitted_loopback": 0,
        "permitted_local_kernel": 0,
    }
    violations: list[dict[str, str]] = []
    total = 0
    for path in trace_files(prefix):
        size = path.stat().st_size
        total += size
        if total > maximum_bytes:
            raise TraceFailure("TRACE_BYTES_LIMIT")
        offset = offsets.get(path, 0)
        if size < offset:
            raise TraceFailure("TRACE_FILE_SHRANK")
        with path.open("r", encoding="utf-8", errors="strict") as handle:
            handle.seek(offset)
            for raw_line in handle:
                line = raw_line.rstrip("\n")
                classified = classify_line(line)
                if classified is None:
                    continue
                classification, syscall = classified
                counts[syscall] += 1
                if classification == "PERMITTED_LOOPBACK":
                    counts["permitted_loopback"] += 1
                elif classification == "PERMITTED_LOCAL_KERNEL":
                    counts["permitted_local_kernel"] += 1
                else:
                    violations.append(
                        {
                            "classification": classification,
                            "line_sha256": digest(line.encode("utf-8")),
                            "source": path.name,
                            "syscall": syscall,
                        }
                    )
            offsets[path] = handle.tell()
    return counts, violations, total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-prefix", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--packet-sha256", required=True)
    parser.add_argument("--poll-seconds", type=float, default=0.5)
    parser.add_argument("--max-trace-bytes", type=int, default=2 * 1024**3)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise TraceFailure("COMMAND_REQUIRED")
    if not re.fullmatch(r"[0-9a-f]{64}", args.packet_sha256):
        raise TraceFailure("PACKET_SHA256_INVALID")
    if not 0.1 <= args.poll_seconds <= 5.0:
        raise TraceFailure("POLL_SECONDS_INVALID")
    if not 1 << 20 <= args.max_trace_bytes <= 4 * 1024**3:
        raise TraceFailure("TRACE_BYTES_LIMIT_INVALID")
    trace_prefix = args.trace_prefix.resolve()
    receipt = args.receipt.resolve()
    if trace_prefix.parent != receipt.parent:
        raise TraceFailure("OUTPUT_ROOT_MISMATCH")
    trace_prefix.parent.mkdir(parents=True, exist_ok=True)
    if trace_files(trace_prefix) or receipt.exists():
        raise TraceFailure("OUTPUT_EXISTS")
    strace_raw = shutil.which("strace")
    if strace_raw is None:
        raise TraceFailure("STRACE_UNAVAILABLE")
    strace = Path(strace_raw).resolve()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    invocation = [
        str(strace),
        "-ff",
        "-qq",
        "-s",
        "256",
        "-v",
        "-e",
        "trace=connect,sendto",
        "-o",
        str(trace_prefix),
        *command,
    ]
    process = subprocess.Popen(
        invocation,
        stdin=subprocess.DEVNULL,
        stdout=None,
        stderr=None,
        start_new_session=True,
    )
    offsets: dict[Path, int] = {}
    totals = {
        "connect": 0,
        "sendto": 0,
        "permitted_loopback": 0,
        "permitted_local_kernel": 0,
    }
    violations: list[dict[str, str]] = []
    trace_bytes = 0
    try:
        while process.poll() is None:
            counts, found, trace_bytes = scan_incremental(
                trace_prefix, offsets, args.max_trace_bytes
            )
            for key, value in counts.items():
                totals[key] += value
            if found:
                violations.extend(found)
                terminate_group(process)
                break
            time.sleep(args.poll_seconds)
        counts, found, trace_bytes = scan_incremental(
            trace_prefix, offsets, args.max_trace_bytes
        )
        for key, value in counts.items():
            totals[key] += value
        violations.extend(found)
    except Exception:
        terminate_group(process)
        raise
    child_exit = process.wait()
    files = [
        {
            "name": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in trace_files(trace_prefix)
    ]
    ended = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    body = {
        "version": VERSION,
        "packet_sha256": args.packet_sha256,
        "started_utc": started,
        "ended_utc": ended,
        "strace_path": str(strace),
        "strace_sha256": sha256_file(strace),
        "command_sha256": digest(canonical(command)),
        "child_exit": child_exit,
        "trace_files": files,
        "trace_bytes": trace_bytes,
        "syscalls": totals,
        "external_or_unparseable_count": len(violations),
        "violations": violations,
        "claim": "PROCESS_TREE_OBSERVED_ZERO_EXTERNAL_EGRESS",
        "limitations": [
            "OBSERVATION_NOT_NETWORK_NAMESPACE_OR_FIREWALL",
            "ONLY_CONNECT_AND_SENDTO_SYSCALLS_ARE_CLASSIFIED",
            "UNRELATED_HOST_OR_CONTAINER_PROCESSES_ARE_OUT_OF_SCOPE",
        ],
        "green": child_exit == 0 and not violations and bool(files),
    }
    record = {**body, "receipt_sha256": digest(canonical(body))}
    atomic_write(receipt, canonical(record))
    return 0 if record["green"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
