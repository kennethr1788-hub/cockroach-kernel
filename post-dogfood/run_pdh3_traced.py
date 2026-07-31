#!/usr/bin/env python3
"""Run one PDH-3 command under complete process-tree network syscall tracing.

This is evidence infrastructure, not a network namespace or firewall. It
follows every descendant with strace, permits only loopback, Unix, netlink,
AF_UNSPEC, and destinationless sends on already-connected sockets, terminates
the process group when a non-loopback or unparseable connect/sendto call is
observed, and emits a canonical receipt.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from typing import Any, Callable


VERSION = "ck-pdh3-process-tree-egress-observer-v2"
SYSCALL = re.compile(r"\b(connect|sendto)\(")
IPV4 = re.compile(r'inet_addr\("([^"]+)"\)')
IPV6 = re.compile(r'inet_pton\(AF_INET6,\s*"([^"]+)"')
SOCKADDR_FAMILY = re.compile(r"\bsa_family=(AF_[A-Z0-9_]+)\b")
PID_PREFIX = re.compile(r"^\s*(?:\[pid\s+)?(?P<pid>\d+)(?:\]\s+|\s+)")
PERMITTED_FAMILIES = ("AF_UNIX", "AF_NETLINK", "AF_UNSPEC")
READ_CHUNK_BYTES = 1 << 20
MAX_TRACE_LINE_BYTES = 1 << 20
PROJECTION_SECONDS = 24 * 60 * 60
PROGRESS_INTERVAL_SECONDS = 30.0


class TraceFailure(RuntimeError):
    pass


@dataclass
class TraceStreamState:
    offset: int = 0
    pending: bytes = b""
    poll_count: int = 0
    read_calls: int = 0
    bytes_read: int = 0
    last_observed_size: int = 0
    scan_wall_seconds: float = 0.0
    scan_cpu_seconds: float = 0.0
    last_progress_monotonic: float | None = None
    last_progress_bytes: int = 0
    trace_device: int | None = None
    trace_inode: int | None = None
    process_ids: set[int] = field(default_factory=set)
    hasher: Any = field(default_factory=hashlib.sha256, repr=False)


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


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def atomic_write(path: Path, raw: bytes) -> None:
    if path.exists() or path.is_symlink():
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


def atomic_replace(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(
        f".{path.name}.{os.getpid()}.{time.monotonic_ns()}.tmp"
    )
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


def syscall_arguments(line: str, match: re.Match[str]) -> list[str]:
    """Split one traced syscall at top-level commas only.

    Payload strings may contain family names, commas, braces, and parentheses.
    Those bytes are data, not the destination sockaddr, so classification must
    isolate the syscall argument that actually carries the address.
    """

    arguments: list[str] = []
    current: list[str] = []
    stack: list[str] = []
    closing = {"(": ")", "[": "]", "{": "}"}
    quote: str | None = None
    escaped = False
    for character in line[match.end() :]:
        if quote is not None:
            current.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
            current.append(character)
            continue
        if character in closing:
            stack.append(closing[character])
            current.append(character)
            continue
        if stack and character == stack[-1]:
            stack.pop()
            current.append(character)
            continue
        if character == ")" and not stack:
            arguments.append("".join(current).strip())
            return arguments
        if character == "," and not stack:
            arguments.append("".join(current).strip())
            current = []
            continue
        current.append(character)
    if current or arguments:
        arguments.append("".join(current).strip())
    return arguments


def sockaddr_argument(
    line: str,
    match: re.Match[str],
    syscall: str,
) -> str | None:
    arguments = syscall_arguments(line, match)
    destination_index = 1 if syscall == "connect" else 4
    if len(arguments) <= destination_index:
        return None
    return arguments[destination_index]


def classify_line(line: str) -> tuple[str, str] | None:
    match = SYSCALL.search(line)
    if match is None:
        return None
    syscall = match.group(1)
    destination = sockaddr_argument(line, match, syscall)
    if destination is None:
        return ("BLOCK_UNPARSEABLE_FAMILY", syscall)
    # A destinationless sendto delegates routing to a preceding connect().
    # strace begins before exec and traces every descendant, so any external
    # connection that could make this send egress is independently observed
    # and blocked by the connect classifier.
    if syscall == "sendto" and destination == "NULL":
        return ("PERMITTED_CONNECTED_NO_DESTINATION", syscall)
    families = set(SOCKADDR_FAMILY.findall(destination))
    if "AF_INET6" in families:
        address = IPV6.search(destination)
        if address is None:
            return ("BLOCK_UNPARSEABLE_INET6", syscall)
        try:
            permitted = ipaddress.ip_address(address.group(1)).is_loopback
        except ValueError:
            return ("BLOCK_UNPARSEABLE_INET6", syscall)
        return ("PERMITTED_LOOPBACK" if permitted else "BLOCK_EXTERNAL", syscall)
    if "AF_INET" in families:
        address = IPV4.search(destination)
        if address is None:
            return ("BLOCK_UNPARSEABLE_INET", syscall)
        try:
            permitted = ipaddress.ip_address(address.group(1)).is_loopback
        except ValueError:
            return ("BLOCK_UNPARSEABLE_INET", syscall)
        return ("PERMITTED_LOOPBACK" if permitted else "BLOCK_EXTERNAL", syscall)
    if families and families.issubset(PERMITTED_FAMILIES):
        return ("PERMITTED_LOCAL_KERNEL", syscall)
    return ("BLOCK_UNPARSEABLE_FAMILY", syscall)


def terminate_group(
    process: subprocess.Popen[bytes],
    *,
    signal_group: Callable[[int, int], None] = os.killpg,
) -> None:
    if process.poll() is not None:
        return
    try:
        signal_group(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=10)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        signal_group(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=10)


def trace_files(prefix: Path) -> list[Path]:
    try:
        if prefix.is_file() and not prefix.is_symlink():
            return [prefix]
    except OSError:
        pass
    return []


def trace_output_exists(prefix: Path) -> bool:
    if prefix.exists() or prefix.is_symlink():
        return True
    # Check legacy -ff output once at startup. Polling never scans this set.
    return any(prefix.parent.glob(prefix.name + ".*"))


def empty_counts() -> dict[str, int]:
    return {
        "connect": 0,
        "sendto": 0,
        "permitted_loopback": 0,
        "permitted_local_kernel": 0,
        "permitted_connected_no_destination": 0,
    }


def merge_counts(total: dict[str, int], values: dict[str, int]) -> None:
    for key, value in values.items():
        total[key] += value


def classify_complete_line(
    raw_line: bytes,
    state: TraceStreamState,
    counts: dict[str, int],
    violations: list[dict[str, str]],
) -> None:
    if len(raw_line) > MAX_TRACE_LINE_BYTES:
        raise TraceFailure("TRACE_LINE_TOO_LONG")
    line = raw_line.rstrip(b"\r").decode("utf-8", "strict")
    pid_match = PID_PREFIX.match(line)
    if pid_match is not None:
        state.process_ids.add(int(pid_match.group("pid")))
    classified = classify_line(line)
    if classified is None:
        return
    classification, syscall = classified
    counts[syscall] += 1
    if classification == "PERMITTED_LOOPBACK":
        counts["permitted_loopback"] += 1
    elif classification == "PERMITTED_LOCAL_KERNEL":
        counts["permitted_local_kernel"] += 1
    elif classification == "PERMITTED_CONNECTED_NO_DESTINATION":
        counts["permitted_connected_no_destination"] += 1
    else:
        violations.append(
            {
                "classification": classification,
                "line_sha256": digest(line.encode("utf-8")),
                "source": "single-stream",
                "syscall": syscall,
            }
        )


def scan_incremental(
    prefix: Path,
    state: TraceStreamState,
    maximum_bytes: int,
    *,
    final: bool = False,
) -> tuple[dict[str, int], list[dict[str, str]], int]:
    state.poll_count += 1
    counts = empty_counts()
    violations: list[dict[str, str]] = []
    if not prefix.exists():
        if final and state.pending:
            raise TraceFailure("TRACE_STREAM_DISAPPEARED")
        return counts, violations, 0
    if not prefix.is_file() or prefix.is_symlink():
        raise TraceFailure("TRACE_STREAM_INVALID")
    metadata = prefix.stat()
    if state.trace_device is None:
        state.trace_device = metadata.st_dev
        state.trace_inode = metadata.st_ino
    elif (metadata.st_dev, metadata.st_ino) != (
        state.trace_device,
        state.trace_inode,
    ):
        raise TraceFailure("TRACE_FILE_REPLACED")
    size = metadata.st_size
    state.last_observed_size = size
    if size > maximum_bytes:
        raise TraceFailure(f"TRACE_BYTES_LIMIT:{size}:{maximum_bytes}")
    if size < state.offset:
        raise TraceFailure("TRACE_FILE_SHRANK")
    remaining = size - state.offset
    if remaining:
        with prefix.open("rb") as handle:
            handle.seek(state.offset)
            while remaining:
                chunk = handle.read(min(READ_CHUNK_BYTES, remaining))
                if not chunk:
                    raise TraceFailure("TRACE_STREAM_SHORT_READ")
                state.read_calls += 1
                state.bytes_read += len(chunk)
                state.offset += len(chunk)
                state.hasher.update(chunk)
                remaining -= len(chunk)
                parts = (state.pending + chunk).split(b"\n")
                state.pending = parts.pop()
                for raw_line in parts:
                    classify_complete_line(raw_line, state, counts, violations)
                if len(state.pending) > MAX_TRACE_LINE_BYTES:
                    raise TraceFailure("TRACE_LINE_TOO_LONG")
    if final and state.pending:
        classify_complete_line(state.pending, state, counts, violations)
        state.pending = b""
    return counts, violations, size


def trace_file_records(prefix: Path, state: TraceStreamState) -> list[dict[str, Any]]:
    files = trace_files(prefix)
    result: list[dict[str, Any]] = []
    for path in files:
        metadata = path.stat()
        if state.trace_device is not None and (
            metadata.st_dev,
            metadata.st_ino,
        ) != (state.trace_device, state.trace_inode):
            raise TraceFailure("TRACE_FILE_REPLACED")
        size = metadata.st_size
        hash_complete = state.bytes_read == size
        result.append(
            {
                "name": path.name,
                "bytes": size,
                "sha256": state.hasher.hexdigest() if hash_complete else None,
                "hash_complete": hash_complete,
            }
        )
    return result


def bounded_error(exc: BaseException) -> dict[str, str]:
    raw = str(exc)
    return {
        "type": type(exc).__name__,
        "reason": raw[:500],
        "reason_sha256": digest(raw.encode("utf-8", "replace")),
    }


def build_progress_record(
    *,
    progress_receipt: Path,
    final_receipt: Path,
    state: TraceStreamState,
    maximum_bytes: int,
    started_utc: str,
    started_monotonic: float,
    observed_monotonic: float,
    observed_utc: str,
    terminal_snapshot: bool,
    trace_stream_count: int,
    packet_sha256: str,
    child_command_sha256: str,
    campaign_id: str,
) -> dict[str, Any]:
    elapsed = max(0.0, observed_monotonic - started_monotonic)
    trace_bytes = state.last_observed_size
    average_rate = trace_bytes / elapsed if elapsed > 0.0 else 0.0
    if state.last_progress_monotonic is None:
        current_rate = average_rate
    else:
        interval = max(0.0, observed_monotonic - state.last_progress_monotonic)
        delta = max(0, trace_bytes - state.last_progress_bytes)
        current_rate = delta / interval if interval > 0.0 else 0.0
    projection_rate = max(average_rate, current_rate)
    projected_bytes = trace_bytes + math.ceil(
        projection_rate * PROJECTION_SECONDS
    )
    body = {
        "version": VERSION,
        "status": (
            "TERMINAL_SNAPSHOT_NON_AUTHORITATIVE"
            if terminal_snapshot
            else "IN_PROGRESS"
        ),
        "authoritative": False,
        "progress_receipt_path": str(progress_receipt),
        "final_receipt_path": str(final_receipt),
        "started_utc": started_utc,
        "observed_utc": observed_utc,
        "elapsed_seconds": round(elapsed, 6),
        "trace_bytes": trace_bytes,
        "trace_stream_count": trace_stream_count,
        "packet_sha256": packet_sha256,
        "child_command_sha256": child_command_sha256,
        "campaign_id": campaign_id,
        "scan_count": state.poll_count,
        "scan_wall_seconds": round(state.scan_wall_seconds, 6),
        "scan_cpu_seconds": round(state.scan_cpu_seconds, 6),
        "current_trace_bytes_per_second": round(current_rate, 6),
        "average_trace_bytes_per_second": round(average_rate, 6),
        "projected_trace_bytes_24h_conservative": projected_bytes,
        "maximum_trace_bytes": maximum_bytes,
        "projected_cap_exceeded": projected_bytes > maximum_bytes,
    }
    return {**body, "progress_receipt_sha256": digest(canonical(body))}


def write_progress_receipt(
    *,
    progress_receipt: Path,
    final_receipt: Path,
    trace_prefix: Path,
    state: TraceStreamState,
    maximum_bytes: int,
    started_utc: str,
    started_monotonic: float,
    observed_monotonic: float,
    observed_utc: str,
    terminal_snapshot: bool,
    packet_sha256: str,
    child_command_sha256: str,
    campaign_id: str,
) -> dict[str, Any]:
    record = build_progress_record(
        progress_receipt=progress_receipt,
        final_receipt=final_receipt,
        state=state,
        maximum_bytes=maximum_bytes,
        started_utc=started_utc,
        started_monotonic=started_monotonic,
        observed_monotonic=observed_monotonic,
        observed_utc=observed_utc,
        terminal_snapshot=terminal_snapshot,
        trace_stream_count=len(trace_files(trace_prefix)),
        packet_sha256=packet_sha256,
        child_command_sha256=child_command_sha256,
        campaign_id=campaign_id,
    )
    atomic_replace(progress_receipt, canonical(record))
    state.last_progress_monotonic = observed_monotonic
    state.last_progress_bytes = state.last_observed_size
    return record


def build_child_environment(
    progress_receipt: Path,
    packet_sha256: str,
    child_command_sha256: str,
    base: dict[str, str] | None = None,
) -> dict[str, str]:
    environment = dict(os.environ if base is None else base)
    environment["PDH3_TRACE_PROGRESS_RECEIPT"] = str(progress_receipt)
    environment["PDH3_TRACE_PACKET_SHA256"] = packet_sha256
    environment["PDH3_TRACE_CHILD_COMMAND_SHA256"] = child_command_sha256
    return environment


def build_strace_invocation(
    strace: Path,
    trace_prefix: Path,
    command: list[str],
) -> list[str]:
    return [
        str(strace),
        "-f",
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


def observe_process(
    process: subprocess.Popen[bytes],
    *,
    trace_prefix: Path,
    receipt: Path,
    packet_sha256: str,
    strace: Path,
    strace_sha256: str,
    command: list[str],
    poll_seconds: float,
    maximum_bytes: int,
    started_utc: str,
    progress_receipt: Path | None = None,
    scan_function: Callable[
        ..., tuple[dict[str, int], list[dict[str, str]], int]
    ] = scan_incremental,
    terminate_function: Callable[[subprocess.Popen[bytes]], None] = terminate_group,
    sleep_function: Callable[[float], None] = time.sleep,
    monotonic_function: Callable[[], float] = time.monotonic,
    process_time_function: Callable[[], float] = time.process_time,
    utc_function: Callable[[], str] = utc_now,
) -> dict[str, Any]:
    if progress_receipt is None:
        progress_receipt = receipt.with_name(f"{receipt.stem}.progress.json")
    state = TraceStreamState()
    try:
        campaign_index = command.index("--campaign-id") + 1
        campaign_id = command[campaign_index]
    except (ValueError, IndexError) as exc:
        raise TraceFailure("CHILD_CAMPAIGN_ID_MISSING") from exc
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", campaign_id):
        raise TraceFailure("CHILD_CAMPAIGN_ID_INVALID")
    child_command_sha256 = digest(canonical(command))
    totals = empty_counts()
    violations: list[dict[str, str]] = []
    observer_error: dict[str, str] | None = None
    observer_phase = "scan"
    started_monotonic = monotonic_function()

    def timed_scan(*, final: bool = False) -> tuple[
        dict[str, int], list[dict[str, str]], int
    ]:
        wall_started = monotonic_function()
        cpu_started = process_time_function()
        try:
            return scan_function(
                trace_prefix,
                state,
                maximum_bytes,
                **({"final": True} if final else {}),
            )
        finally:
            state.scan_cpu_seconds += max(
                0.0, process_time_function() - cpu_started
            )
            state.scan_wall_seconds += max(
                0.0, monotonic_function() - wall_started
            )

    def update_progress(
        *, terminal_snapshot: bool
    ) -> dict[str, Any] | None:
        observed_monotonic = monotonic_function()
        if (
            not terminal_snapshot
            and state.last_progress_monotonic is not None
            and observed_monotonic - state.last_progress_monotonic
            < PROGRESS_INTERVAL_SECONDS
        ):
            return None
        return write_progress_receipt(
            progress_receipt=progress_receipt,
            final_receipt=receipt,
            trace_prefix=trace_prefix,
            state=state,
            maximum_bytes=maximum_bytes,
            started_utc=started_utc,
            started_monotonic=started_monotonic,
            observed_monotonic=observed_monotonic,
            observed_utc=utc_function(),
            terminal_snapshot=terminal_snapshot,
            packet_sha256=packet_sha256,
            child_command_sha256=child_command_sha256,
            campaign_id=campaign_id,
        )

    try:
        while process.poll() is None:
            observer_phase = "scan"
            counts, found, _ = timed_scan()
            merge_counts(totals, counts)
            if found:
                violations.extend(found)
                observer_phase = "termination"
                terminate_function(process)
                break
            observer_phase = "progress"
            update_progress(terminal_snapshot=False)
            sleep_function(poll_seconds)
        observer_phase = "final_scan"
        counts, found, _ = timed_scan(final=True)
        merge_counts(totals, counts)
        violations.extend(found)
        if found and process.poll() is None:
            observer_phase = "termination"
            terminate_function(process)
    except Exception as exc:
        observer_error = bounded_error(exc)
        observer_error["phase"] = observer_phase
        try:
            terminate_function(process)
        except Exception as terminate_exc:
            observer_error["termination_error_type"] = type(terminate_exc).__name__
            observer_error["termination_error_sha256"] = digest(
                str(terminate_exc).encode("utf-8", "replace")
            )
    child_exit = process.poll()
    if child_exit is None:
        try:
            terminate_function(process)
        except Exception as terminate_exc:
            if observer_error is None:
                observer_error = bounded_error(terminate_exc)
                observer_error["phase"] = "termination"
            else:
                observer_error["termination_retry_error_type"] = type(
                    terminate_exc
                ).__name__
                observer_error["termination_retry_error_sha256"] = digest(
                    str(terminate_exc).encode("utf-8", "replace")
                )
        child_exit = process.poll()
    if child_exit is None:
        if observer_error is None:
            observer_error = bounded_error(
                TraceFailure("CHILD_GROUP_TERMINATION_UNCONFIRMED")
            )
            observer_error["phase"] = "termination"
        else:
            observer_error["termination_unconfirmed"] = "true"
    try:
        files = trace_file_records(trace_prefix, state)
    except Exception as evidence_exc:
        files = []
        if observer_error is None:
            observer_error = bounded_error(evidence_exc)
            observer_error["phase"] = "evidence"
        else:
            observer_error["evidence_error_type"] = type(evidence_exc).__name__
            observer_error["evidence_error_sha256"] = digest(
                str(evidence_exc).encode("utf-8", "replace")
            )
    progress_record: dict[str, Any] | None = None
    try:
        progress_record = update_progress(terminal_snapshot=True)
    except Exception as progress_exc:
        if observer_error is None:
            observer_error = bounded_error(progress_exc)
            observer_error["phase"] = "progress"
        else:
            observer_error["progress_error_type"] = type(progress_exc).__name__
            observer_error["progress_error_sha256"] = digest(
                str(progress_exc).encode("utf-8", "replace")
            )
    trace_bytes = sum(int(row["bytes"]) for row in files)
    ended_utc = utc_function()
    green = (
        observer_error is None
        and child_exit == 0
        and not violations
        and len(files) == 1
        and all(bool(row["hash_complete"]) for row in files)
        and not state.pending
    )
    body = {
        "version": VERSION,
        "status": "GREEN" if green else "BLOCKED",
        "authoritative": True,
        "packet_sha256": packet_sha256,
        "tool_sha256": sha256_file(Path(__file__).resolve()),
        "started_utc": started_utc,
        "ended_utc": ended_utc,
        "strace_path": str(strace),
        "strace_sha256": strace_sha256,
        "command_sha256": digest(canonical(command)),
        "child_exit": child_exit,
        "trace_stream_mode": "SINGLE_FILE_PID_PREFIXED_STRACE_F",
        "trace_files": files,
        "trace_file_count": len(files),
        "trace_bytes": trace_bytes,
        "maximum_trace_bytes": maximum_bytes,
        "progress_receipt_path": str(progress_receipt),
        "progress_receipt_sha256": (
            progress_record["progress_receipt_sha256"]
            if progress_record is not None
            else None
        ),
        "trace_emitting_process_count": len(state.process_ids),
        "trace_emitting_process_set_sha256": digest(
            canonical(sorted(state.process_ids))
        ),
        "observer_metrics": {
            "poll_count": state.poll_count,
            "read_calls": state.read_calls,
            "bytes_read": state.bytes_read,
            "pending_bytes": len(state.pending),
        },
        "observer_error": observer_error,
        "syscalls": totals,
        "external_or_unparseable_count": len(violations),
        "violations": violations,
        "claim": (
            "PROCESS_TREE_OBSERVED_ZERO_EXTERNAL_EGRESS"
            if green
            else "PROCESS_TREE_OBSERVATION_BLOCKED"
        ),
        "limitations": [
            "OBSERVATION_NOT_NETWORK_NAMESPACE_OR_FIREWALL",
            "ONLY_CONNECT_AND_SENDTO_SYSCALLS_ARE_CLASSIFIED",
            "DESTINATIONLESS_SENDTO_RELIES_ON_COMPLETE_PRE_EXEC_CONNECT_TRACING",
            "UNRELATED_HOST_OR_CONTAINER_PROCESSES_ARE_OUT_OF_SCOPE",
        ],
        "green": green,
    }
    record = {**body, "receipt_sha256": digest(canonical(body))}
    atomic_write(receipt, canonical(record))
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-prefix", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--packet-sha256", required=True)
    parser.add_argument("--strace", type=Path, required=True)
    parser.add_argument("--strace-sha256", required=True)
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
    progress_receipt = receipt.with_name(f"{receipt.stem}.progress.json")
    if trace_prefix.parent != receipt.parent:
        raise TraceFailure("OUTPUT_ROOT_MISMATCH")
    if len({trace_prefix, receipt, progress_receipt}) != 3:
        raise TraceFailure("OUTPUT_PATH_COLLISION")
    trace_prefix.parent.mkdir(parents=True, exist_ok=True)
    if (
        trace_output_exists(trace_prefix)
        or receipt.exists()
        or receipt.is_symlink()
        or progress_receipt.exists()
        or progress_receipt.is_symlink()
    ):
        raise TraceFailure("OUTPUT_EXISTS")
    strace = args.strace.resolve()
    if not strace.is_file() or not os.access(strace, os.X_OK):
        raise TraceFailure("STRACE_UNAVAILABLE")
    if not re.fullmatch(r"[0-9a-f]{64}", args.strace_sha256):
        raise TraceFailure("STRACE_SHA256_INVALID")
    if sha256_file(strace) != args.strace_sha256:
        raise TraceFailure("STRACE_SHA256_MISMATCH")
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    invocation = build_strace_invocation(strace, trace_prefix, command)
    child_command_sha256 = digest(canonical(command))
    process = subprocess.Popen(
        invocation,
        stdin=subprocess.DEVNULL,
        stdout=None,
        stderr=None,
        start_new_session=True,
        env=build_child_environment(
            progress_receipt,
            args.packet_sha256,
            child_command_sha256,
        ),
    )
    record = observe_process(
        process,
        trace_prefix=trace_prefix,
        receipt=receipt,
        packet_sha256=args.packet_sha256,
        strace=strace,
        strace_sha256=args.strace_sha256,
        command=command,
        poll_seconds=args.poll_seconds,
        maximum_bytes=args.max_trace_bytes,
        started_utc=started,
        progress_receipt=progress_receipt,
    )
    return 0 if record["green"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
