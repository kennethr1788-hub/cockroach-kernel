#!/usr/bin/env python3
"""Fail-closed PF-4 worker capability and disposable-disk benchmark.

This program runs before the main campaign bundle is uploaded.  It uses only
the selected worker's disposable container disk, removes its benchmark file,
and emits one canonical receipt.  The thresholds are prospective requirements;
the program never derives or relaxes them from observed worker performance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import time
from typing import Any, Iterable

import pdh3_r12_cpu_affinity as cpu_affinity


MIN_VCPUS = 16
MIN_RAM_BYTES = 64 * 1024**3
MIN_DISK_TOTAL_BYTES = 240_000_000_000
MIN_DISK_AVAILABLE_BYTES = 220_000_000_000
MAX_DISK_USED_FRACTION = 0.10
SEQUENTIAL_BYTES = 2 * 1024**3
SUSTAINED_BYTES = 8 * 1024**3
BLOCK_BYTES = 8 * 1024**2
MIN_SEQUENTIAL_MIB_S = 75.0
MIN_SUSTAINED_MIB_S = 75.0
FSYNC_SAMPLES = 200
MAX_FSYNC_P99_MS = 50.0
RANDOM_SYNC_SAMPLES = 256
MIN_RANDOM_SYNC_IOPS = 50.0
MAX_RECEIPT_BYTES = 64 * 1024
MAX_OBSERVER_STREAM_BYTES = 1024 * 1024


class CapabilityError(RuntimeError):
    """Stable PF-4 capability failure."""


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


def atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + ".part")
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


def memory_total_bytes() -> int:
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        if line.startswith("MemTotal:"):
            parts = line.split()
            if len(parts) == 3 and parts[2] == "kB":
                return int(parts[1]) * 1024
    raise CapabilityError("MEMTOTAL_UNAVAILABLE")


def parse_cpuset(raw: str) -> int:
    values: set[int] = set()
    for item in raw.strip().split(","):
        if not item:
            continue
        if "-" in item:
            first, last = item.split("-", 1)
            start, end = int(first), int(last)
            if start < 0 or end < start:
                raise CapabilityError("CPUSET_INVALID")
            values.update(range(start, end + 1))
        else:
            value = int(item)
            if value < 0:
                raise CapabilityError("CPUSET_INVALID")
            values.add(value)
    if not values:
        raise CapabilityError("CPUSET_EMPTY")
    return len(values)


def _first_file(root: Path, relatives: Iterable[str]) -> Path | None:
    for relative in relatives:
        candidate = root / relative
        if candidate.is_file() and not candidate.is_symlink():
            return candidate
    return None


def resource_accounting_backend(
    cgroup_root: Path = Path("/sys/fs/cgroup"),
    proc_root: Path = Path("/proc"),
) -> dict[str, Any]:
    """Select an observed accounting interface without assuming cgroup v2."""
    v2 = {
        name: cgroup_root / name
        for name in ("cpu.stat", "memory.current", "memory.events", "io.stat", "pids.current")
    }
    if all(path.is_file() and not path.is_symlink() for path in v2.values()):
        return {
            "available": True,
            "backend": "CGROUP_V2",
            "scope": "CONTAINER_CGROUP",
            "files": {name: str(path) for name, path in v2.items()},
            "cgroup_isolation_observed": True,
        }

    v1_candidates = {
        "cpu": (
            "cpuacct/cpuacct.usage", "cpu,cpuacct/cpuacct.usage",
            "cpu/cpu.stat", "cpu,cpuacct/cpu.stat",
        ),
        "memory_usage": (
            "memory/memory.usage_in_bytes", "memory.usage_in_bytes",
        ),
        "memory_limit": (
            "memory/memory.limit_in_bytes", "memory.limit_in_bytes",
        ),
        "io": (
            "blkio/blkio.throttle.io_service_bytes",
            "blkio/blkio.io_service_bytes",
            "blkio.throttle.io_service_bytes",
            "blkio.io_service_bytes",
        ),
        "pids": ("pids/pids.current", "pids.current"),
    }
    v1 = {
        name: _first_file(cgroup_root, relatives)
        for name, relatives in v1_candidates.items()
    }
    if all(path is not None for path in v1.values()):
        return {
            "available": True,
            "backend": "CGROUP_V1",
            "scope": "CONTAINER_CGROUP",
            "files": {name: str(path) for name, path in v1.items() if path is not None},
            "cgroup_isolation_observed": True,
        }

    proc = {
        "self_status": proc_root / "self/status",
        "self_io": proc_root / "self/io",
        "system_stat": proc_root / "stat",
        "meminfo": proc_root / "meminfo",
        "net_dev": proc_root / "net/dev",
    }
    proc_green = all(path.is_file() and not path.is_symlink() for path in proc.values())
    affinity_green = hasattr(os, "sched_getaffinity") and bool(os.sched_getaffinity(0))
    return {
        "available": proc_green and affinity_green,
        "backend": "PROCFS_PROCESS_TREE_PROVIDER_BOUND" if proc_green and affinity_green else "UNAVAILABLE",
        "scope": "PROCESS_TREE_PLUS_PROVIDER_ALLOCATION" if proc_green and affinity_green else "NONE",
        "files": {
            name: str(path)
            for name, path in proc.items()
            if path.is_file() and not path.is_symlink()
        },
        "cgroup_isolation_observed": False,
    }


def cgroup_cpu_limit(root: Path = Path("/sys/fs/cgroup")) -> dict[str, Any]:
    candidates: dict[str, int] = {}
    affinity = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else 0
    if affinity:
        candidates["sched_affinity"] = affinity
    cpuset = root / "cpuset.cpus.effective"
    if cpuset.is_file() and cpuset.read_text(encoding="utf-8").strip():
        candidates["cpuset"] = parse_cpuset(cpuset.read_text(encoding="utf-8"))
    cpu_max = root / "cpu.max"
    if cpu_max.is_file():
        fields = cpu_max.read_text(encoding="utf-8").split()
        if len(fields) != 2:
            raise CapabilityError("CPU_MAX_INVALID")
        if fields[0] != "max":
            quota, period = int(fields[0]), int(fields[1])
            if quota <= 0 or period <= 0:
                raise CapabilityError("CPU_MAX_INVALID")
            candidates["quota"] = max(1, quota // period)
    for base in (root / "cpu", root / "cpu,cpuacct", root):
        quota_path = base / "cpu.cfs_quota_us"
        period_path = base / "cpu.cfs_period_us"
        if quota_path.is_file() and period_path.is_file():
            quota = int(quota_path.read_text(encoding="utf-8").strip())
            period = int(period_path.read_text(encoding="utf-8").strip())
            if quota > 0 and period > 0:
                candidates["v1_quota"] = max(1, quota // period)
            break
    return {
        "host_logical": os.cpu_count() or 0,
        "constraints": candidates,
        "cgroup_effective": min(candidates.values()) if candidates else None,
    }


def cgroup_memory_limit(root: Path = Path("/sys/fs/cgroup")) -> dict[str, Any]:
    host = memory_total_bytes()
    finite: int | None = None
    memory_max = root / "memory.max"
    if memory_max.is_file():
        raw = memory_max.read_text(encoding="utf-8").strip()
        if raw != "max":
            finite = int(raw)
            if finite <= 0:
                raise CapabilityError("MEMORY_MAX_INVALID")
    if finite is None:
        for candidate in (root / "memory/memory.limit_in_bytes", root / "memory.limit_in_bytes"):
            if candidate.is_file():
                value = int(candidate.read_text(encoding="utf-8").strip())
                if 0 < value < (1 << 60):
                    finite = value
                break
    return {
        "host_bytes": host,
        "cgroup_max_bytes": finite,
        "cgroup_effective_bytes": min(host, finite) if finite is not None else None,
    }


def effective_resources(
    allocated_vcpus: int,
    allocated_memory_gib: int,
    root: Path = Path("/sys/fs/cgroup"),
) -> dict[str, Any]:
    if allocated_vcpus < 1 or allocated_memory_gib < 1:
        raise CapabilityError("PROVIDER_ALLOCATION_INVALID")
    cpu = cgroup_cpu_limit(root)
    memory = cgroup_memory_limit(root)
    cpu_candidates = [allocated_vcpus]
    if cpu["cgroup_effective"] is not None:
        cpu_candidates.append(int(cpu["cgroup_effective"]))
    memory_candidates = [allocated_memory_gib * 1024**3]
    if memory["cgroup_effective_bytes"] is not None:
        memory_candidates.append(int(memory["cgroup_effective_bytes"]))
    return {
        "provider_allocated_vcpus": allocated_vcpus,
        "provider_allocated_memory_gib": allocated_memory_gib,
        "cpu": cpu,
        "memory": memory,
        "effective_vcpus": min(cpu_candidates),
        "effective_memory_bytes": min(memory_candidates),
    }


def percentile(values: list[float], fraction: float) -> float:
    if not values or not 0 < fraction <= 1:
        raise CapabilityError("PERCENTILE_INPUT_INVALID")
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * fraction) - 1)]


def timed_write(path: Path, total_bytes: int, *, sync_interval: int) -> float:
    block = b"\x5a" * BLOCK_BYTES
    written = 0
    since_sync = 0
    started = time.monotonic()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        while written < total_bytes:
            amount = min(BLOCK_BYTES, total_bytes - written)
            view = memoryview(block)[:amount]
            while view:
                count = os.write(descriptor, view)
                if count <= 0:
                    raise CapabilityError("WRITE_MADE_NO_PROGRESS")
                view = view[count:]
                written += count
                since_sync += count
            if since_sync >= sync_interval:
                os.fdatasync(descriptor)
                since_sync = 0
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    elapsed = time.monotonic() - started
    if elapsed <= 0:
        raise CapabilityError("WRITE_TIMER_INVALID")
    return total_bytes / 1024**2 / elapsed


def fsync_latency(path: Path) -> dict[str, float]:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    values: list[float] = []
    try:
        for index in range(FSYNC_SAMPLES):
            os.pwrite(descriptor, index.to_bytes(8, "big") + b"x" * 4088, index * 4096)
            started = time.monotonic_ns()
            os.fsync(descriptor)
            values.append((time.monotonic_ns() - started) / 1_000_000)
    finally:
        os.close(descriptor)
    return {
        "samples": float(len(values)),
        "mean_ms": statistics.fmean(values),
        "p99_ms": percentile(values, 0.99),
        "max_ms": max(values),
    }


def random_sync_iops(path: Path) -> float:
    size = 64 * 1024**2
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.ftruncate(descriptor, size)
        os.fsync(descriptor)
        block = b"\xa5" * 4096
        slots = size // len(block)
        started = time.monotonic()
        for index in range(RANDOM_SYNC_SAMPLES):
            slot = (index * 104729) % slots
            os.pwrite(descriptor, block, slot * len(block))
            os.fdatasync(descriptor)
        elapsed = time.monotonic() - started
    finally:
        os.close(descriptor)
    if elapsed <= 0:
        raise CapabilityError("RANDOM_TIMER_INVALID")
    return RANDOM_SYNC_SAMPLES / elapsed


def command_receipt(
    command: list[str],
    timeout: int = 60,
    *,
    stdout_path: Path | None = None,
    stderr_path: Path | None = None,
) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    if len(completed.stdout) > MAX_OBSERVER_STREAM_BYTES or len(completed.stderr) > MAX_OBSERVER_STREAM_BYTES:
        raise CapabilityError("OBSERVER_STREAM_TOO_LARGE")
    if stdout_path is not None:
        atomic_write(stdout_path, completed.stdout)
    if stderr_path is not None:
        atomic_write(stderr_path, completed.stderr)
    return {
        "argv_sha256": digest(command),
        "returncode": completed.returncode,
        "stdout_sha256": digest(completed.stdout),
        "stderr_sha256": digest(completed.stderr),
        "stdout_bytes": len(completed.stdout),
        "stderr_bytes": len(completed.stderr),
        "green": completed.returncode == 0,
    }


def thresholds() -> dict[str, Any]:
    return {
        "min_vcpus": MIN_VCPUS,
        "min_ram_bytes": MIN_RAM_BYTES,
        "min_disk_total_bytes": MIN_DISK_TOTAL_BYTES,
        "min_disk_available_bytes": MIN_DISK_AVAILABLE_BYTES,
        "max_disk_used_fraction": MAX_DISK_USED_FRACTION,
        "sequential_bytes": SEQUENTIAL_BYTES,
        "sustained_bytes": SUSTAINED_BYTES,
        "min_sequential_mib_s": MIN_SEQUENTIAL_MIB_S,
        "min_sustained_mib_s": MIN_SUSTAINED_MIB_S,
        "fsync_samples": FSYNC_SAMPLES,
        "max_fsync_p99_ms": MAX_FSYNC_P99_MS,
        "random_sync_samples": RANDOM_SYNC_SAMPLES,
        "min_random_sync_iops": MIN_RANDOM_SYNC_IOPS,
    }


def execute(
    workdir: Path,
    output: Path,
    observer: Path,
    *,
    allocated_vcpus: int,
    allocated_memory_gib: int,
    effective_vcpu_limit: int,
    packet_sha256: str,
    tracer: Path,
    tracer_sha256: str,
) -> dict[str, Any]:
    if sys.platform != "linux" or platform.machine() not in {"x86_64", "amd64"}:
        raise CapabilityError("LINUX_AMD64_REQUIRED")
    if output.exists() or workdir.exists():
        raise CapabilityError("OUTPUT_OR_WORKDIR_EXISTS")
    try:
        affinity_plan = cpu_affinity.effective_vcpu_plan(
            allocated_vcpus, allocated_memory_gib
        )
        if effective_vcpu_limit != affinity_plan["effective_vcpu_limit"]:
            raise CapabilityError("EFFECTIVE_VCPU_PLAN_MISMATCH")
        affinity_apply = cpu_affinity.apply_effective_vcpu_limit(
            effective_vcpu_limit
        )
    except cpu_affinity.AffinityError as exc:
        raise CapabilityError("CPU_AFFINITY_BLOCKED:" + str(exc)) from exc
    workdir.mkdir(parents=True)
    usage_before = shutil.disk_usage(workdir)
    resources = effective_resources(allocated_vcpus, allocated_memory_gib)
    cpu_count = int(resources["effective_vcpus"])
    ram_bytes = int(resources["effective_memory_bytes"])
    used_fraction = (usage_before.used / usage_before.total) if usage_before.total else 1.0
    monotonic_before = time.monotonic_ns()
    time.sleep(0.05)
    monotonic_advanced = time.monotonic_ns() > monotonic_before
    observer_output = workdir / "network-probe.json"
    observer_receipt = workdir / "network-capability.json"
    observer_stdout = output.parent / "PF4_NETWORK_OBSERVER.stdout"
    observer_stderr = output.parent / "PF4_NETWORK_OBSERVER.stderr"
    observer_result = command_receipt(
        [
            sys.executable,
            str(observer.resolve()),
            "capability",
            "--output",
            str(observer_output),
            "--receipt",
            str(observer_receipt),
            "--packet-sha256",
            packet_sha256,
            "--tracer",
            str(tracer.resolve()),
            "--tracer-sha256",
            tracer_sha256,
        ],
        stdout_path=observer_stdout,
        stderr_path=observer_stderr,
    )
    accounting = resource_accounting_backend()
    cgroup_files = {
        name: (Path("/sys/fs/cgroup") / name).is_file()
        for name in ("cpu.stat", "memory.current", "memory.events", "io.stat", "pids.current")
    }
    process_tree_available = Path("/proc/self/status").is_file() and Path("/proc/self/task").is_dir()

    paths = {
        "sequential": workdir / "sequential.bin",
        "sustained": workdir / "sustained.bin",
        "fsync": workdir / "fsync.bin",
        "random": workdir / "random.bin",
    }
    try:
        sequential_mib_s = timed_write(
            paths["sequential"], SEQUENTIAL_BYTES, sync_interval=SEQUENTIAL_BYTES
        )
        paths["sequential"].unlink()
        sustained_mib_s = timed_write(
            paths["sustained"], SUSTAINED_BYTES, sync_interval=512 * 1024**2
        )
        paths["sustained"].unlink()
        fsync = fsync_latency(paths["fsync"])
        paths["fsync"].unlink()
        sync_iops = random_sync_iops(paths["random"])
        paths["random"].unlink()
    finally:
        for path in paths.values():
            path.unlink(missing_ok=True)
    usage_after = shutil.disk_usage(workdir)
    checks = {
        "cpu": cpu_count >= MIN_VCPUS,
        "ram": ram_bytes >= MIN_RAM_BYTES and ram_bytes >= cpu_count * 4 * 1024**3,
        "cpu_affinity": affinity_apply["exact"]
        and affinity_apply["after"]["count"] == effective_vcpu_limit,
        "disk_total": usage_before.total >= MIN_DISK_TOTAL_BYTES,
        "disk_available": usage_before.free >= MIN_DISK_AVAILABLE_BYTES,
        "disk_used_fraction": used_fraction <= MAX_DISK_USED_FRACTION,
        "sequential": sequential_mib_s >= MIN_SEQUENTIAL_MIB_S,
        "sustained": sustained_mib_s >= MIN_SUSTAINED_MIB_S,
        "fsync": fsync["p99_ms"] <= MAX_FSYNC_P99_MS,
        "random_sync": sync_iops >= MIN_RANDOM_SYNC_IOPS,
        "resource_accounting": accounting["available"],
        "process_tree": process_tree_available,
        "monotonic": monotonic_advanced,
        "streaming_network_observer": observer_result["green"]
        and observer_receipt.is_file(),
        "residue": not any(path.exists() for path in paths.values()),
    }
    body = {
        "version": "ck-pdh3-r12-pf4-capability-v3",
        "thresholds": thresholds(),
        "observed": {
            "cpu_count": cpu_count,
            "ram_bytes": ram_bytes,
            "cpu_affinity_plan": affinity_plan,
            "cpu_affinity_apply": affinity_apply,
            "resource_accounting": resources,
            "resource_accounting_backend": accounting,
            "disk_before": usage_before._asdict(),
            "disk_after": usage_after._asdict(),
            "disk_used_fraction_before": used_fraction,
            "sequential_mib_s": sequential_mib_s,
            "sustained_mib_s": sustained_mib_s,
            "fsync": fsync,
            "random_sync_iops": sync_iops,
            "cgroup_files": cgroup_files,
            "process_tree_available": process_tree_available,
            "monotonic_advanced": monotonic_advanced,
            "streaming_network_observer": observer_result,
            "network_probe_sha256": digest(observer_output.read_bytes())
            if observer_output.is_file()
            else None,
            "network_capability_sha256": digest(observer_receipt.read_bytes())
            if observer_receipt.is_file()
            else None,
        },
        "checks": checks,
        "benchmark_root_removed": False,
        "green": all(checks.values()),
    }
    shutil.rmtree(workdir)
    body["benchmark_root_removed"] = not workdir.exists()
    body["green"] = body["green"] and body["benchmark_root_removed"]
    record = {**body, "receipt_sha256": digest(body)}
    raw = canonical(record)
    if len(raw) > MAX_RECEIPT_BYTES:
        raise CapabilityError("RECEIPT_TOO_LARGE")
    atomic_write(output, raw)
    if not record["green"]:
        raise CapabilityError("PF4_CAPABILITY_GATE_FAILED")
    return record


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--workdir", type=Path, required=True)
    value.add_argument("--output", type=Path, required=True)
    value.add_argument("--observer", type=Path, required=True)
    value.add_argument("--allocated-vcpus", type=int, required=True)
    value.add_argument("--allocated-memory-gib", type=int, required=True)
    value.add_argument("--effective-vcpu-limit", type=int, required=True)
    value.add_argument("--packet-sha256", required=True)
    value.add_argument("--tracer", type=Path, required=True)
    value.add_argument("--tracer-sha256", required=True)
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    try:
        execute(
            args.workdir,
            args.output,
            args.observer,
            allocated_vcpus=args.allocated_vcpus,
            allocated_memory_gib=args.allocated_memory_gib,
            effective_vcpu_limit=args.effective_vcpu_limit,
            packet_sha256=args.packet_sha256,
            tracer=args.tracer,
            tracer_sha256=args.tracer_sha256,
        )
        return 0
    except (CapabilityError, OSError, subprocess.SubprocessError) as exc:
        print(f"PDH3_R12_PF4_BLOCKED:{type(exc).__name__}:{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
