#!/usr/bin/env python3
"""Low-volume process-tree network proof for PDH-3 R12.

The worker image used by RunPod does not expose unprivileged user/network
namespaces. This observer therefore uses the already hash-pinned strace
artifact to follow the complete launched process tree. Trace bytes are parsed
from a pipe and hashed but not retained in full. Any external or unparseable
destination terminates the traced process group. Canonical 30-second summaries,
bounded raw samples, container network counters, and the final receipt remain.

This proves observed process-tree destinations; it is not a firewall and does
not claim unrelated container processes are isolated.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import time
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
TRACE_SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_stream_trace", HERE / "run_pdh3_traced.py"
)
if TRACE_SPEC is None or TRACE_SPEC.loader is None:
    raise RuntimeError("TRACE_MODULE_IMPORT_FAILED")
trace = importlib.util.module_from_spec(TRACE_SPEC)
sys.modules[TRACE_SPEC.name] = trace
TRACE_SPEC.loader.exec_module(trace)


VERSION = "ck-pdh3-r12-streaming-network-proof-v2"
ZERO_HASH = "0" * 64
PR_SET_PDEATHSIG = 1
MAX_LINE_BYTES = 1 << 20
MAX_RAW_SAMPLES = 64
PROJECTION_SECONDS = 86_400


class ObserverError(RuntimeError):
    """Stable fail-closed observer error."""


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


def file_sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def atomic_write(path: Path, raw: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise ObserverError("OUTPUT_EXISTS")
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
        temporary.unlink(missing_ok=True)


def parse_net_dev(raw: str) -> dict[str, dict[str, int]]:
    rows: dict[str, dict[str, int]] = {}
    for line in raw.splitlines()[2:]:
        if ":" not in line:
            continue
        name, fields = line.split(":", 1)
        interface = name.strip()
        values = fields.split()
        if not interface or len(values) != 16:
            raise ObserverError("NET_DEV_PARSE_INVALID")
        parsed = [int(value) for value in values]
        rows[interface] = {
            "rx_bytes": parsed[0],
            "rx_packets": parsed[1],
            "rx_errors": parsed[2],
            "rx_drops": parsed[3],
            "tx_bytes": parsed[8],
            "tx_packets": parsed[9],
            "tx_errors": parsed[10],
            "tx_drops": parsed[11],
        }
    if not rows:
        raise ObserverError("NET_DEV_EMPTY")
    return rows


def network_snapshot() -> dict[str, dict[str, int]]:
    return parse_net_dev(Path("/proc/net/dev").read_text(encoding="utf-8"))


def counter_delta(
    first: dict[str, dict[str, int]], last: dict[str, dict[str, int]]
) -> tuple[dict[str, dict[str, int]], bool]:
    if set(first) != set(last):
        return {}, False
    result: dict[str, dict[str, int]] = {}
    continuous = True
    for interface in sorted(first):
        result[interface] = {}
        for name, before in first[interface].items():
            after = last[interface][name]
            if after < before:
                continuous = False
            result[interface][name] = max(0, after - before)
    return result, continuous


def persisted_bytes(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def parent_death_kill() -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(PR_SET_PDEATHSIG, signal.SIGKILL, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "prctl(PR_SET_PDEATHSIG) failed")
    if os.getppid() == 1:
        os.kill(os.getpid(), signal.SIGKILL)


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


class ChainWriter:
    def __init__(self, path: Path) -> None:
        if path.exists() or path.is_symlink():
            raise ObserverError("CHAIN_EXISTS")
        self.path = path
        self.sequence = 0
        self.previous = ZERO_HASH

    def emit(self, event: str, details: dict[str, Any]) -> dict[str, Any]:
        self.sequence += 1
        body = {
            "version": "ck-pdh3-r12-network-summary-v2",
            "sequence": self.sequence,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "monotonic_ns": time.monotonic_ns(),
            "previous_hash": self.previous,
            "event": event,
            "details": details,
        }
        record = {**body, "sample_sha256": digest(body)}
        with self.path.open("ab") as handle:
            handle.write(canonical(record) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous = record["sample_sha256"]
        return record


def validate_hash(value: str, label: str) -> None:
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise ObserverError(label + "_INVALID")


def append_raw_sample(path: Path, sequence: int, line: bytes, classification: str) -> None:
    body = {
        "version": "ck-pdh3-r12-bounded-network-raw-sample-v1",
        "sequence": sequence,
        "classification": classification,
        "line": line.decode("utf-8", "replace"),
        "line_sha256": digest(line),
    }
    record = {**body, "sample_sha256": digest(body)}
    with path.open("ab") as handle:
        handle.write(canonical(record) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())


def guarded_command(script: Path, command: list[str]) -> list[str]:
    return [sys.executable, str(script), "_guard_exec", "--", *command]


def tracer_invocation(
    tracer: Path, trace_fd: int, script: Path, command: list[str]
) -> list[str]:
    return [
        str(tracer),
        "-f",
        "-qq",
        "-s",
        "256",
        "-v",
        "-e",
        "trace=connect,sendto,sendmsg",
        "-o",
        f"/proc/self/fd/{trace_fd}",
        *guarded_command(script, command),
    ]


def observe(
    *,
    output: Path,
    packet_sha256: str,
    tracer: Path,
    tracer_sha256: str,
    command: list[str],
    interval_seconds: float,
    max_evidence_bytes: int,
    projection_required: bool = True,
) -> dict[str, Any]:
    validate_hash(packet_sha256, "PACKET_SHA256")
    validate_hash(tracer_sha256, "TRACER_SHA256")
    tracer = tracer.resolve()
    if not tracer.is_file() or not os.access(tracer, os.X_OK):
        raise ObserverError("TRACER_UNAVAILABLE")
    if file_sha256(tracer) != tracer_sha256:
        raise ObserverError("TRACER_SHA256_MISMATCH")
    if not command:
        raise ObserverError("COMMAND_REQUIRED")
    if not 1 <= interval_seconds <= 60:
        raise ObserverError("INTERVAL_INVALID")
    if not 1 << 20 <= max_evidence_bytes <= 2 * 1024**3:
        raise ObserverError("EVIDENCE_LIMIT_INVALID")
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    chain = ChainWriter(output / "network-summaries.ndjson")
    raw_samples = output / "bounded-raw-samples.ndjson"
    child_stdout = output / "child.stdout"
    child_stderr = output / "child.stderr"
    initial_counters = network_snapshot()
    counts = trace.empty_counts()
    trace_hash = hashlib.sha256()
    trace_bytes = 0
    trace_lines = 0
    process_ids: set[int] = set()
    violations: list[dict[str, str]] = []
    sample_count = 0
    pending = b""
    started = time.monotonic()
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    read_fd, write_fd = os.pipe()
    os.set_blocking(read_fd, False)
    process: subprocess.Popen[bytes] | None = None
    observer_error: dict[str, str] | None = None
    try:
        with child_stdout.open("wb") as stdout, child_stderr.open("wb") as stderr:
            invocation = tracer_invocation(
                tracer, write_fd, Path(__file__).resolve(), command
            )
            process = subprocess.Popen(
                invocation,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
                pass_fds=(write_fd,),
                preexec_fn=parent_death_kill,
            )
            os.close(write_fd)
            write_fd = -1
            chain.emit(
                "OBSERVER_STARTED",
                {
                    "packet_sha256": packet_sha256,
                    "tracer_sha256": tracer_sha256,
                    "command_sha256": digest(command),
                    "tracer_argv_sha256": digest(invocation),
                    "initial_network_counters": initial_counters,
                },
            )
            next_summary = time.monotonic() + interval_seconds
            pipe_eof = False
            while process.poll() is None or not pipe_eof:
                readable, _, _ = select.select([read_fd], [], [], 0.25)
                if readable:
                    chunk = os.read(read_fd, 1 << 20)
                    if not chunk:
                        pipe_eof = True
                    else:
                        trace_hash.update(chunk)
                        trace_bytes += len(chunk)
                        parts = (pending + chunk).split(b"\n")
                        pending = parts.pop()
                        if len(pending) > MAX_LINE_BYTES:
                            raise ObserverError("TRACE_LINE_TOO_LONG")
                        for raw_line in parts:
                            if len(raw_line) > MAX_LINE_BYTES:
                                raise ObserverError("TRACE_LINE_TOO_LONG")
                            trace_lines += 1
                            line = raw_line.decode("utf-8", "strict")
                            pid_match = trace.PID_PREFIX.match(line)
                            if pid_match is not None:
                                process_ids.add(int(pid_match.group("pid")))
                            classified = trace.classify_line(line)
                            if classified is None:
                                continue
                            classification, syscall = classified
                            counts[syscall] += 1
                            key = classification.lower()
                            if key in counts:
                                counts[key] += 1
                            if sample_count < MAX_RAW_SAMPLES:
                                sample_count += 1
                                append_raw_sample(
                                    raw_samples, sample_count, raw_line, classification
                                )
                            if classification.startswith("BLOCK_"):
                                violations.append(
                                    {
                                        "classification": classification,
                                        "syscall": syscall,
                                        "line_sha256": digest(raw_line),
                                    }
                                )
                                terminate_group(process)
                                break
                now = time.monotonic()
                if now >= next_summary or (process.poll() is not None and pipe_eof):
                    current = network_snapshot()
                    delta, continuous = counter_delta(initial_counters, current)
                    loss_delta = sum(
                        values["rx_errors"]
                        + values["rx_drops"]
                        + values["tx_errors"]
                        + values["tx_drops"]
                        for values in delta.values()
                    )
                    if not continuous:
                        violations.append(
                            {
                                "classification": "BLOCK_COUNTER_DISCONTINUITY",
                                "syscall": "observer",
                                "line_sha256": digest(canonical(current)),
                            }
                        )
                        terminate_group(process)
                    chain.emit(
                        "NETWORK_SUMMARY",
                        {
                            "child_alive": process.poll() is None,
                            "trace_bytes_observed": trace_bytes,
                            "trace_lines_observed": trace_lines,
                            "trace_stream_sha256": trace_hash.copy().hexdigest(),
                            "syscalls": counts,
                            "violation_count": len(violations),
                            "counter_delta": delta,
                            "counter_continuous": continuous,
                            "network_error_drop_delta": loss_delta,
                            "persisted_evidence_bytes": persisted_bytes(output),
                        },
                    )
                    if persisted_bytes(output) > max_evidence_bytes:
                        violations.append(
                            {
                                "classification": "BLOCK_EVIDENCE_LIMIT",
                                "syscall": "observer",
                                "line_sha256": digest(str(persisted_bytes(output)).encode()),
                            }
                        )
                        terminate_group(process)
                    next_summary = now + interval_seconds
                if violations and process.poll() is not None and pipe_eof:
                    break
            if pending:
                if len(pending) > MAX_LINE_BYTES:
                    raise ObserverError("TRACE_LINE_TOO_LONG")
                trace_hash.update(b"")
                trace_lines += 1
                classified = trace.classify_line(pending.decode("utf-8", "strict"))
                if classified is not None and classified[0].startswith("BLOCK_"):
                    violations.append(
                        {
                            "classification": classified[0],
                            "syscall": classified[1],
                            "line_sha256": digest(pending),
                        }
                    )
            child_exit = process.wait(timeout=10)
    except Exception as exc:
        observer_error = {
            "type": type(exc).__name__,
            "reason": str(exc)[:500],
            "reason_sha256": digest(str(exc).encode("utf-8", "replace")),
        }
        if process is not None:
            try:
                terminate_group(process)
            except Exception:
                pass
        child_exit = process.poll() if process is not None else None
    finally:
        if write_fd >= 0:
            os.close(write_fd)
        os.close(read_fd)
    ended = time.monotonic()
    final_counters = network_snapshot()
    delta, continuous = counter_delta(initial_counters, final_counters)
    elapsed = max(0.001, ended - started)
    chain.emit(
        "OBSERVER_STOPPING",
        {
            "child_exit": child_exit,
            "observer_error": observer_error,
            "violation_count": len(violations),
        },
    )
    evidence_bytes = persisted_bytes(output)
    projected = evidence_bytes + int(evidence_bytes / elapsed * PROJECTION_SECONDS)
    projection_green = projected <= max_evidence_bytes if projection_required else True
    green = (
        observer_error is None
        and child_exit == 0
        and not violations
        and continuous
        and trace_lines > 0
        and projection_green
    )
    body = {
        "version": VERSION,
        "packet_sha256": packet_sha256,
        "started_utc": started_utc,
        "ended_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": elapsed,
        "tracer_path": str(tracer),
        "tracer_sha256": tracer_sha256,
        "command_sha256": digest(command),
        "child_exit": child_exit,
        "trace_stream_bytes_observed_not_retained": trace_bytes,
        "trace_stream_lines_observed": trace_lines,
        "trace_stream_sha256": trace_hash.hexdigest(),
        "trace_emitting_process_count": len(process_ids),
        "trace_emitting_process_set_sha256": digest(sorted(process_ids)),
        "syscalls": counts,
        "external_or_unparseable_count": len(violations),
        "violations": violations,
        "initial_network_counters": initial_counters,
        "final_network_counters": final_counters,
        "network_counter_delta": delta,
        "network_counter_continuous": continuous,
        "summary_count": chain.sequence,
        "last_summary_sha256": chain.previous,
        "bounded_raw_sample_count": sample_count,
        "persisted_evidence_bytes": evidence_bytes,
        "projected_24h_evidence_bytes": projected,
        "projection_gate_applied": projection_required,
        "evidence_limit_bytes": max_evidence_bytes,
        "stdout_sha256": file_sha256(child_stdout),
        "stderr_sha256": file_sha256(child_stderr),
        "observer_error": observer_error,
        "claim": (
            "PROCESS_TREE_OBSERVED_ZERO_EXTERNAL_EGRESS"
            if green
            else "PROCESS_TREE_OBSERVATION_BLOCKED"
        ),
        "limitations": [
            "OBSERVATION_AND_FAIL_CLOSED_TERMINATION_NOT_PREVENTIVE_FIREWALL",
            "CONTAINER_COUNTERS_INCLUDE_UNRELATED_CONTROL_PLANE_TRAFFIC",
            "UNRELATED_CONTAINER_PROCESSES_ARE_OUT_OF_SCOPE",
            "ONLY_CONNECT_SENDTO_AND_SENDMSG_DESTINATIONS_ARE_CLASSIFIED",
        ],
        "green": green,
    }
    record = {**body, "receipt_sha256": digest(body)}
    atomic_write(output / "network-receipt.json", canonical(record))
    return record


def capability(args: argparse.Namespace) -> int:
    validate_hash(args.packet_sha256, "PACKET_SHA256")
    output = args.output.resolve()
    receipt = args.receipt.resolve()
    trace_root = output.with_name(output.stem + "-trace")
    script = (
        "import socket,threading;"
        "s=socket.socket();s.bind(('127.0.0.1',0));s.listen(1);"
        "t=threading.Thread(target=lambda:s.accept()[0].close());t.start();"
        "c=socket.create_connection(s.getsockname());c.close();t.join();s.close()"
    )
    command = [
        sys.executable,
        "-c",
        script,
        "--campaign-id",
        "ck-pdh3-r12-preflight-capability",
    ]
    result = observe(
        output=trace_root,
        packet_sha256=args.packet_sha256,
        tracer=args.tracer,
        tracer_sha256=args.tracer_sha256,
        command=command,
        interval_seconds=1,
        max_evidence_bytes=64 * 1024**2,
        projection_required=False,
    )
    atomic_write(output, canonical(result))
    body = {
        "version": "ck-pdh3-r12-streaming-network-capability-v2",
        "packet_sha256": args.packet_sha256,
        "probe_sha256": file_sha256(output),
        "trace_receipt_sha256": file_sha256(trace_root / "network-receipt.json"),
        "green": result["green"],
    }
    atomic_write(receipt, canonical({**body, "receipt_sha256": digest(body)}))
    return 0 if body["green"] else 2


def guard_exec(command: list[str]) -> int:
    if not command:
        raise ObserverError("COMMAND_REQUIRED")
    parent_death_kill()
    os.execvpe(command[0], command, os.environ.copy())
    return 127


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    subparsers = value.add_subparsers(dest="mode", required=True)
    cap = subparsers.add_parser("capability")
    cap.add_argument("--output", type=Path, required=True)
    cap.add_argument("--receipt", type=Path, required=True)
    cap.add_argument("--packet-sha256", required=True)
    cap.add_argument("--tracer", type=Path, required=True)
    cap.add_argument("--tracer-sha256", required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--output-dir", type=Path, required=True)
    run.add_argument("--packet-sha256", required=True)
    run.add_argument("--tracer", type=Path, required=True)
    run.add_argument("--tracer-sha256", required=True)
    run.add_argument("--interval-seconds", type=float, default=30)
    run.add_argument("--max-evidence-bytes", type=int, default=1024**3)
    run.add_argument("command", nargs=argparse.REMAINDER)
    guard = subparsers.add_parser("_guard_exec")
    guard.add_argument("command", nargs=argparse.REMAINDER)
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    if getattr(args, "command", None) and args.command[0] == "--":
        args.command = args.command[1:]
    try:
        if args.mode == "capability":
            return capability(args)
        if args.mode == "_guard_exec":
            return guard_exec(args.command)
        result = observe(
            output=args.output_dir,
            packet_sha256=args.packet_sha256,
            tracer=args.tracer,
            tracer_sha256=args.tracer_sha256,
            command=args.command,
            interval_seconds=args.interval_seconds,
            max_evidence_bytes=args.max_evidence_bytes,
        )
        return 0 if result["green"] else 2
    except (ObserverError, OSError, subprocess.SubprocessError) as exc:
        print(
            f"PDH3_R12_NETWORK_OBSERVER_BLOCKED:{type(exc).__name__}:{exc}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
