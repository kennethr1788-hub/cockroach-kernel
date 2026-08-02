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


def command_receipt(command: list[str], timeout: int = 60) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    return {
        "argv_sha256": digest(command),
        "returncode": completed.returncode,
        "stdout_sha256": digest(completed.stdout),
        "stderr_sha256": digest(completed.stderr),
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


def execute(workdir: Path, output: Path, observer: Path) -> dict[str, Any]:
    if sys.platform != "linux" or platform.machine() not in {"x86_64", "amd64"}:
        raise CapabilityError("LINUX_AMD64_REQUIRED")
    if output.exists() or workdir.exists():
        raise CapabilityError("OUTPUT_OR_WORKDIR_EXISTS")
    workdir.mkdir(parents=True)
    usage_before = shutil.disk_usage(workdir)
    cpu_count = os.cpu_count() or 0
    ram_bytes = memory_total_bytes()
    used_fraction = (usage_before.used / usage_before.total) if usage_before.total else 1.0
    monotonic_before = time.monotonic_ns()
    time.sleep(0.05)
    monotonic_advanced = time.monotonic_ns() > monotonic_before
    observer_output = workdir / "network-probe.json"
    observer_receipt = workdir / "network-capability.json"
    observer_result = command_receipt(
        [
            sys.executable,
            str(observer.resolve()),
            "capability",
            "--output",
            str(observer_output),
            "--receipt",
            str(observer_receipt),
        ]
    )
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
        "disk_total": usage_before.total >= MIN_DISK_TOTAL_BYTES,
        "disk_available": usage_before.free >= MIN_DISK_AVAILABLE_BYTES,
        "disk_used_fraction": used_fraction <= MAX_DISK_USED_FRACTION,
        "sequential": sequential_mib_s >= MIN_SEQUENTIAL_MIB_S,
        "sustained": sustained_mib_s >= MIN_SUSTAINED_MIB_S,
        "fsync": fsync["p99_ms"] <= MAX_FSYNC_P99_MS,
        "random_sync": sync_iops >= MIN_RANDOM_SYNC_IOPS,
        "cgroup": all(cgroup_files.values()),
        "process_tree": process_tree_available,
        "monotonic": monotonic_advanced,
        "network_namespace": observer_result["green"] and observer_receipt.is_file(),
        "residue": not any(path.exists() for path in paths.values()),
    }
    body = {
        "version": "ck-pdh3-r12-pf4-capability-v1",
        "thresholds": thresholds(),
        "observed": {
            "cpu_count": cpu_count,
            "ram_bytes": ram_bytes,
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
            "network_namespace": observer_result,
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
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    try:
        execute(args.workdir, args.output, args.observer)
        return 0
    except (CapabilityError, OSError, subprocess.SubprocessError) as exc:
        print(f"PDH3_R12_PF4_BLOCKED:{type(exc).__name__}:{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
