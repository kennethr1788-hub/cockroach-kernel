#!/usr/bin/env python3
"""Low-volume, fail-closed network proof for the PDH-3 R12 preflight.

The observed command is launched in a new unprivileged user, network, PID, and
mount namespace.  The namespace contains only loopback.  The observer records
the interface and route state plus byte/packet counters in a hash chain.  A
child receives ``SIGKILL`` if the observer dies, so observer loss cannot leave
an unobserved workload running.

This module deliberately has no privileged fallback.  If the provider image or
container policy does not permit the exact namespace construction, the remote
capability gate is BLOCKED.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
from typing import Any, Iterable


ZERO_HASH = "0" * 64
PR_SET_PDEATHSIG = 1
ALLOWED_INTERFACES = {"lo"}


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


def digest(raw: bytes | Any) -> str:
    return hashlib.sha256(raw if isinstance(raw, bytes) else canonical(raw)).hexdigest()


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def atomic_write(path: Path, raw: bytes) -> None:
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


def write_record(path: Path, body: dict[str, Any], hash_field: str) -> dict[str, Any]:
    record = {**body, hash_field: digest(body)}
    atomic_write(path, canonical(record))
    return record


def parse_net_dev(raw: str) -> dict[str, dict[str, int]]:
    rows: dict[str, dict[str, int]] = {}
    for line in raw.splitlines()[2:]:
        if ":" not in line:
            continue
        name, counters = line.split(":", 1)
        interface = name.strip()
        values = counters.split()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", interface) or len(values) != 16:
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


def route_interfaces(raw: str) -> list[str]:
    rows = raw.splitlines()
    if not rows:
        return []
    interfaces: list[str] = []
    for line in rows[1:]:
        fields = line.split()
        if fields:
            interfaces.append(fields[0])
    return sorted(set(interfaces))


def ipv6_route_interfaces(raw: str) -> list[str]:
    interfaces: list[str] = []
    for line in raw.splitlines():
        fields = line.split()
        if fields:
            interfaces.append(fields[-1])
    return sorted(set(interfaces))


def namespace_snapshot() -> dict[str, Any]:
    namespace = os.readlink("/proc/self/ns/net")
    interfaces = parse_net_dev(Path("/proc/net/dev").read_text(encoding="utf-8"))
    ipv4 = route_interfaces(Path("/proc/net/route").read_text(encoding="utf-8"))
    ipv6_path = Path("/proc/net/ipv6_route")
    ipv6 = (
        ipv6_route_interfaces(ipv6_path.read_text(encoding="utf-8"))
        if ipv6_path.is_file()
        else []
    )
    visible = set(interfaces) | set(ipv4) | set(ipv6)
    unexpected = sorted(visible - ALLOWED_INTERFACES)
    return {
        "network_namespace": namespace,
        "interfaces": interfaces,
        "ipv4_route_interfaces": ipv4,
        "ipv6_route_interfaces": ipv6,
        "unexpected_interfaces": unexpected,
        "loopback_only": not unexpected and set(interfaces) == ALLOWED_INTERFACES,
    }


def bring_loopback_up(ip_binary: Path) -> None:
    completed = subprocess.run(
        [str(ip_binary), "link", "set", "dev", "lo", "up"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=10,
    )
    if completed.returncode != 0:
        raise ObserverError("LOOPBACK_ENABLE_FAILED:" + digest(completed.stderr))


def parent_death_kill() -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(PR_SET_PDEATHSIG, signal.SIGKILL, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "prctl(PR_SET_PDEATHSIG) failed")
    if os.getppid() == 1:
        os.kill(os.getpid(), signal.SIGKILL)


def terminate_group(process: subprocess.Popen[bytes], grace_seconds: float = 10.0) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=5)


class ChainWriter:
    def __init__(self, path: Path) -> None:
        if path.exists():
            raise ObserverError("CHAIN_ALREADY_EXISTS")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.sequence = 0
        self.previous_hash = ZERO_HASH

    def emit(self, event: str, details: dict[str, Any]) -> dict[str, Any]:
        self.sequence += 1
        body = {
            "version": "ck-pdh3-r12-network-sample-v1",
            "sequence": self.sequence,
            "monotonic_ns": time.monotonic_ns(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "previous_hash": self.previous_hash,
            "event": event,
            "details": details,
        }
        record = {**body, "sample_sha256": digest(body)}
        with self.path.open("ab") as handle:
            handle.write(canonical(record) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous_hash = record["sample_sha256"]
        return record


def validate_packet_sha256(value: str) -> None:
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ObserverError("PACKET_SHA256_INVALID")


def inside_run(args: argparse.Namespace) -> int:
    validate_packet_sha256(args.packet_sha256)
    if sys.platform != "linux":
        raise ObserverError("LINUX_REQUIRED")
    ip = Path(args.ip_binary).resolve()
    if not ip.is_file() or not os.access(ip, os.X_OK):
        raise ObserverError("IP_BINARY_INVALID")
    if args.interval_seconds < 1 or args.interval_seconds > 60:
        raise ObserverError("INTERVAL_INVALID")
    if args.max_evidence_bytes < 4096:
        raise ObserverError("EVIDENCE_LIMIT_INVALID")
    if not args.command:
        raise ObserverError("COMMAND_REQUIRED")

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    bring_loopback_up(ip)
    initial = namespace_snapshot()
    if not initial["loopback_only"]:
        raise ObserverError("NETWORK_NAMESPACE_NOT_LOOPBACK_ONLY")

    chain = ChainWriter(output / "network-samples.ndjson")
    stdout_path = output / "child.stdout"
    stderr_path = output / "child.stderr"
    started = time.monotonic()
    child: subprocess.Popen[bytes] | None = None
    violation: str | None = None
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            child = subprocess.Popen(
                args.command,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
                preexec_fn=parent_death_kill,
            )
            chain.emit(
                "OBSERVER_STARTED",
                {
                    "packet_sha256": args.packet_sha256,
                    "child_pid": child.pid,
                    "snapshot": initial,
                },
            )
            next_sample = time.monotonic()
            while child.poll() is None:
                now = time.monotonic()
                if now >= next_sample:
                    snapshot = namespace_snapshot()
                    if not snapshot["loopback_only"]:
                        violation = "UNEXPECTED_NETWORK_INTERFACE"
                    chain.emit(
                        "NETWORK_SAMPLE",
                        {
                            "child_pid": child.pid,
                            "child_alive": True,
                            "snapshot": snapshot,
                        },
                    )
                    if chain.path.stat().st_size > args.max_evidence_bytes:
                        violation = "NETWORK_EVIDENCE_LIMIT_EXCEEDED"
                    if violation is not None:
                        terminate_group(child)
                        break
                    next_sample = now + args.interval_seconds
                time.sleep(min(0.25, max(0.01, next_sample - time.monotonic())))
            returncode = child.wait()
            final_snapshot = namespace_snapshot()
            chain.emit(
                "OBSERVER_TERMINAL",
                {
                    "child_pid": child.pid,
                    "child_returncode": returncode,
                    "violation": violation,
                    "snapshot": final_snapshot,
                },
            )
    finally:
        if child is not None:
            terminate_group(child)

    elapsed = time.monotonic() - started
    chain_bytes = chain.path.stat().st_size
    projected = int(chain_bytes * max(1.0, 86_400 / max(elapsed, 1.0)))
    body = {
        "version": "ck-pdh3-r12-loopback-network-proof-v1",
        "packet_sha256": args.packet_sha256,
        "network_namespace": initial["network_namespace"],
        "allowed_destination_classes": ["LOOPBACK_ONLY"],
        "external_interfaces": [],
        "undeclared_destination_count": 0 if violation is None else 1,
        "observer_loss": False,
        "sample_count": chain.sequence,
        "last_sample_sha256": chain.previous_hash,
        "chain_bytes": chain_bytes,
        "elapsed_seconds": elapsed,
        "projected_24h_bytes": projected,
        "evidence_limit_bytes": args.max_evidence_bytes,
        "child_returncode": returncode,
        "violation": violation,
        "stdout_sha256": file_sha256(stdout_path),
        "stderr_sha256": file_sha256(stderr_path),
        "green": violation is None and returncode == 0,
    }
    write_record(output / "network-receipt.json", body, "receipt_sha256")
    return 0 if body["green"] else 2


def inside_probe(args: argparse.Namespace) -> int:
    ip = Path(args.ip_binary).resolve()
    bring_loopback_up(ip)
    snapshot = namespace_snapshot()
    body = {
        "version": "ck-pdh3-r12-network-capability-probe-v1",
        "linux": sys.platform == "linux",
        "effective_uid": os.geteuid(),
        "network_namespace": snapshot["network_namespace"],
        "loopback_only": snapshot["loopback_only"],
        "snapshot": snapshot,
        "green": sys.platform == "linux" and snapshot["loopback_only"],
    }
    write_record(args.output, body, "receipt_sha256")
    return 0 if body["green"] else 2


def exact_unshare_command(
    *, script: Path, mode: str, forwarded: list[str], unshare: Path
) -> list[str]:
    return [
        str(unshare),
        "--user",
        "--map-root-user",
        "--net",
        "--pid",
        "--fork",
        "--mount-proc",
        sys.executable,
        str(script),
        mode,
        *forwarded,
    ]


def launch(args: argparse.Namespace) -> int:
    if sys.platform != "linux":
        raise ObserverError("LINUX_REQUIRED")
    unshare_name = shutil.which("unshare")
    ip_name = shutil.which("ip")
    if unshare_name is None or ip_name is None:
        raise ObserverError("NETWORK_NAMESPACE_TOOL_MISSING")
    unshare = Path(unshare_name).resolve()
    ip = Path(ip_name).resolve()
    forwarded = [
        "--output-dir",
        str(args.output_dir),
        "--packet-sha256",
        args.packet_sha256,
        "--interval-seconds",
        str(args.interval_seconds),
        "--max-evidence-bytes",
        str(args.max_evidence_bytes),
        "--ip-binary",
        str(ip),
        "--",
        *args.command,
    ]
    command = exact_unshare_command(
        script=Path(__file__).resolve(), mode="_inside", forwarded=forwarded, unshare=unshare
    )
    completed = subprocess.run(command, stdin=subprocess.DEVNULL, check=False)
    return completed.returncode


def capability(args: argparse.Namespace) -> int:
    if sys.platform != "linux":
        raise ObserverError("LINUX_REQUIRED")
    unshare_name = shutil.which("unshare")
    ip_name = shutil.which("ip")
    if unshare_name is None or ip_name is None:
        raise ObserverError("NETWORK_NAMESPACE_TOOL_MISSING")
    unshare = Path(unshare_name).resolve()
    ip = Path(ip_name).resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)
    command = exact_unshare_command(
        script=Path(__file__).resolve(),
        mode="_probe",
        forwarded=["--output", str(output), "--ip-binary", str(ip)],
        unshare=unshare,
    )
    completed = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=args.timeout_seconds,
        check=False,
    )
    body = {
        "version": "ck-pdh3-r12-network-capability-v1",
        "unshare_path": str(unshare),
        "unshare_sha256": file_sha256(unshare),
        "ip_path": str(ip),
        "ip_sha256": file_sha256(ip),
        "command_sha256": digest(command),
        "returncode": completed.returncode,
        "stdout_sha256": digest(completed.stdout),
        "stderr_sha256": digest(completed.stderr),
        "probe_receipt_sha256": file_sha256(output) if output.is_file() else None,
        "green": completed.returncode == 0 and output.is_file(),
    }
    write_record(args.receipt, body, "receipt_sha256")
    return 0 if body["green"] else 2


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    subparsers = value.add_subparsers(dest="mode", required=True)

    cap = subparsers.add_parser("capability")
    cap.add_argument("--output", type=Path, required=True)
    cap.add_argument("--receipt", type=Path, required=True)
    cap.add_argument("--timeout-seconds", type=int, default=30)

    run = subparsers.add_parser("run")
    run.add_argument("--output-dir", type=Path, required=True)
    run.add_argument("--packet-sha256", required=True)
    run.add_argument("--interval-seconds", type=float, default=30)
    run.add_argument("--max-evidence-bytes", type=int, default=1024**3)
    run.add_argument("command", nargs=argparse.REMAINDER)

    inside = subparsers.add_parser("_inside")
    inside.add_argument("--output-dir", type=Path, required=True)
    inside.add_argument("--packet-sha256", required=True)
    inside.add_argument("--interval-seconds", type=float, required=True)
    inside.add_argument("--max-evidence-bytes", type=int, required=True)
    inside.add_argument("--ip-binary", required=True)
    inside.add_argument("command", nargs=argparse.REMAINDER)

    probe = subparsers.add_parser("_probe")
    probe.add_argument("--output", type=Path, required=True)
    probe.add_argument("--ip-binary", required=True)
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    if getattr(args, "command", None) and args.command[0] == "--":
        args.command = args.command[1:]
    try:
        if args.mode == "capability":
            return capability(args)
        if args.mode == "run":
            return launch(args)
        if args.mode == "_inside":
            return inside_run(args)
        return inside_probe(args)
    except (ObserverError, OSError, subprocess.SubprocessError) as exc:
        print(f"PDH3_R12_NETWORK_OBSERVER_BLOCKED:{type(exc).__name__}:{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
