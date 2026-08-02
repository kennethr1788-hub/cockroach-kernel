#!/usr/bin/env python3
"""Preflight-only PDH-3 R12 remote campaign.

This entry point has no measured-24-hour branch.  It executes amended PF-2R,
PF-5, PF-6, and PF-7 on one disposable Linux worker, publishes immutable
checkpoints for independent off-worker retrieval, and tears down its local
CockroachDB roots before returning.  Provider creation/deletion remains a
host-control-plane responsibility.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import pdh3_r12_checkpoint as checkpoint
import pdh3_r12_plan_ab as plan_ab
import pdh3_scale_contract as contract
import run_pdh3_scale_campaign as scale


PLAN_SHA256 = "a1214b4779fe1495de219ed0033421ac810390641cd97742deb61cd3957df3d9"
PF2_AMENDMENT_SHA256 = "0068c17d1c2e515181f209848bd383da08c33893b1e0fb738acefab49070a41e"
ZERO_HASH = "0" * 64
NAMED_CONCURRENCY = (10, 50, 100, 250, 500)
GATEWAY_ALLOCATION = (167, 167, 166)
NAMED_FAMILIES = {
    "vector_exact": tuple(f"vector-{index:02d}" for index in range(20)),
    "receipt_view": tuple(f"receipt-{index:02d}" for index in range(5)),
    "stale_projection": ("stale-projection-read",),
    "trajectory_join": ("trajectory-link-read",),
}
GROWTH_SECONDS = 900
NETWORK_PROJECTION_LIMIT = 1024**3
OTHER_EVIDENCE_LIMIT = int(contract.EVIDENCE_BYTES_LIMIT * 0.80)
DATABASE_PROJECTION_LIMIT = int(contract.DATABASE_BYTES_LIMIT * 0.80)


class R12RemoteError(RuntimeError):
    """Stable preflight-only terminal failure."""


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


def write_record(path: Path, body: dict[str, Any], field: str) -> dict[str, Any]:
    record = {**body, field: digest(body)}
    atomic_write(path, canonical(record))
    return record


def tree_bytes(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def files_under(root: Path, relatives: Iterable[Path]) -> list[str]:
    values: list[str] = []
    for relative in relatives:
        path = root / relative
        if path.is_file() and not path.is_symlink():
            values.append(relative.as_posix())
        elif path.is_dir() and not path.is_symlink():
            values.extend(
                child.relative_to(root).as_posix()
                for child in sorted(path.rglob("*"))
                if child.is_file() and not child.is_symlink()
            )
        else:
            raise R12RemoteError("CHECKPOINT_SOURCE_INVALID:" + relative.as_posix())
    result = sorted(set(values))
    if not result:
        raise R12RemoteError("CHECKPOINT_SOURCE_EMPTY")
    return result


class Publisher:
    def __init__(self, source: Path, export: Path, packet_sha256: str) -> None:
        self.source = source
        self.export = export
        self.packet_sha256 = packet_sha256
        self.sequence = 0
        self.previous = ZERO_HASH

    def publish(self, *relatives: Path) -> dict[str, Any]:
        self.sequence += 1
        manifest = checkpoint.publish(
            source_root=self.source,
            export_root=self.export,
            sequence=self.sequence,
            previous_manifest_sha256=self.previous,
            packet_sha256=self.packet_sha256,
            files=files_under(self.source, relatives),
        )
        self.previous = manifest["manifest_sha256"]
        return manifest


def read_small(path: Path, maximum: int = 1 << 20) -> bytes:
    raw = path.read_bytes()
    if len(raw) > maximum:
        raise R12RemoteError("FILE_TOO_LARGE:" + path.name)
    return raw


def cgroup_snapshot() -> dict[str, Any]:
    base = Path("/sys/fs/cgroup")
    names = ("cpu.stat", "memory.current", "memory.events", "io.stat", "pids.current")
    values: dict[str, Any] = {}
    for name in names:
        path = base / name
        values[name] = (
            {
                "bytes": path.stat().st_size,
                "sha256": digest(read_small(path)),
                "text": read_small(path).decode("utf-8", "replace")[:16_384],
            }
            if path.is_file()
            else None
        )
    return values


def bounded_metrics(port: int) -> dict[str, Any]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        connection.request("GET", "/_status/vars")
        response = connection.getresponse()
        raw = response.read(16 * 1024 * 1024)
    finally:
        connection.close()
    selected = []
    prefixes = (
        "sql_conns",
        "sql_service_latency",
        "admission_",
        "sys_cpu",
        "sys_rss",
        "storage_l0",
        "storage_write_stall",
    )
    for line in raw.decode("utf-8", "replace").splitlines():
        if line.startswith(prefixes):
            selected.append(line)
    return {
        "http_status": response.status,
        "raw_sha256": digest(raw),
        "selected": selected,
        "selected_sha256": digest(selected),
    }


class Sampler:
    def __init__(
        self,
        path: Path,
        nodes: list[scale.Node],
        root: Path,
        output: Path,
        interval: float = 1.0,
    ) -> None:
        self.path = path
        self.nodes = nodes
        self.root = root
        self.output = output
        self.interval = interval
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.error: str | None = None
        self.samples = 0
        self.previous = ZERO_HASH

    def _run(self) -> None:
        try:
            while not self.stop_event.wait(0 if self.samples == 0 else self.interval):
                body = {
                    "version": "ck-pdh3-r12-resource-sample-v1",
                    "sequence": self.samples + 1,
                    "monotonic_ns": time.monotonic_ns(),
                    "previous_hash": self.previous,
                    "metrics": [bounded_metrics(node.http_port) for node in self.nodes],
                    "process": scale.process_metrics(self.nodes, self.root, self.output),
                    "cgroup": cgroup_snapshot(),
                }
                record = {**body, "sample_sha256": digest(body)}
                with self.path.open("ab") as handle:
                    handle.write(canonical(record) + b"\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                self.previous = record["sample_sha256"]
                self.samples += 1
        except BaseException as exc:  # evidence collector failure is fatal
            self.error = f"{type(exc).__name__}:{exc}"
            self.stop_event.set()

    def start(self) -> None:
        if self.thread is not None:
            raise R12RemoteError("SAMPLER_ALREADY_STARTED")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.thread = threading.Thread(target=self._run, name="pdh3-r12-sampler", daemon=False)
        self.thread.start()

    def stop(self) -> dict[str, Any]:
        self.stop_event.set()
        if self.thread is None:
            raise R12RemoteError("SAMPLER_NOT_STARTED")
        self.thread.join(timeout=max(5.0, self.interval + 4.0))
        if self.thread.is_alive():
            raise R12RemoteError("SAMPLER_THREAD_LEAK")
        if self.error is not None:
            raise R12RemoteError("SAMPLER_FAILED:" + digest(self.error.encode()))
        if self.samples < 1 or not self.path.is_file():
            raise R12RemoteError("SAMPLER_EVIDENCE_MISSING")
        return {
            "samples": self.samples,
            "last_sample_sha256": self.previous,
            "file_sha256": file_sha256(self.path),
            "bytes": self.path.stat().st_size,
            "green": True,
        }


def make_query_files(canary: Any, root: Path, campaign_id: str) -> dict[str, dict[str, Any]]:
    definitions = plan_ab.query_definitions(campaign_id)
    result: dict[str, dict[str, Any]] = {}
    root.mkdir(parents=True, exist_ok=True)
    for family, names in NAMED_FAMILIES.items():
        rows = [f"{name}: {definitions[name]}" for name in names]
        path = root / f"querybench-{family}.sql"
        atomic_write(path, ("\n".join(rows) + "\n").encode())
        result[family] = {"path": path, "query_names": list(names), "sha256": file_sha256(path)}
    mixed = scale.create_query_files(canary, root, campaign_id)["read_mix"]
    result["read_mix"] = mixed
    return result


def run_bench(
    canary: Any,
    binary: Path,
    port: int,
    query_file: Path,
    root: Path,
    concurrency: int,
    kind: str,
    env: dict[str, str],
    duration: int,
) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=False)
    value = canary.run_querybench(
        binary,
        port,
        query_file,
        root,
        concurrency,
        kind,
        env,
        duration_seconds=duration,
        deadline=time.monotonic() + duration + 120,
    )
    latency = value["summary"]["latency_ms"]
    value["diagnostic_binding"] = {
        "query_file_sha256": file_sha256(query_file),
        "gateway_port": port,
        "sql_fingerprint_set": kind,
        # querybench exposes p95 rather than p90 in its stable summary.  The
        # p95 is recorded as a conservative upper bound for the requested p90.
        "p90_upper_bound_ms": latency["p95"],
    }
    value["green"] = (
        value["summary"]["errors"] == 0
        and value["histogram_accounts_for_operations"]
        and latency["p99"] <= contract.P99_LIMIT_MS
        and latency["max"] <= contract.PMAX_LIMIT_MS
    )
    if not value["green"]:
        raise R12RemoteError("QUERYBENCH_GATE_FAILED:" + kind)
    return value


def aggregate_gateway(values: list[dict[str, Any]]) -> dict[str, Any]:
    operations = sum(row["summary"]["operations"] for row in values)
    errors = sum(row["summary"]["errors"] for row in values)
    p99 = max(row["summary"]["latency_ms"]["p99"] for row in values)
    maximum = max(row["summary"]["latency_ms"]["max"] for row in values)
    body = {
        "logical_workers": sum(row["concurrency"] for row in values),
        "operations": operations,
        "errors": errors,
        "p99_ms_conservative_max": p99,
        "max_ms": maximum,
        "members": values,
    }
    return {
        **body,
        "green": (
            body["logical_workers"] == 500
            and errors == 0
            and p99 <= contract.P99_LIMIT_MS
            and maximum <= contract.PMAX_LIMIT_MS
        ),
    }


def run_three_gateway(
    canary: Any,
    binary: Path,
    nodes: list[scale.Node],
    query_file: Path,
    root: Path,
    env: dict[str, str],
    duration: int,
) -> dict[str, Any]:
    def member(index: int) -> dict[str, Any]:
        concurrency = GATEWAY_ALLOCATION[index]
        value = run_bench(
            canary,
            binary,
            nodes[index].sql_port,
            query_file,
            root / f"gateway-{index + 1}",
            concurrency,
            f"three-gateway-{index + 1}",
            env,
            duration,
        )
        return {**value, "gateway": index + 1, "concurrency": concurrency}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(member, index) for index in range(3)]
        values = [future.result(timeout=duration + 180) for future in futures]
    result = aggregate_gateway(values)
    if not result["green"]:
        raise R12RemoteError("THREE_GATEWAY_GATE_FAILED")
    return result


def ensure_plans(
    binary: Path,
    port: int,
    env: dict[str, str],
    campaign_id: str,
    output: Path,
    deadline: float,
) -> dict[str, Any]:
    def remaining(cap: int) -> int:
        available = deadline - time.monotonic() - 300
        if available < 1:
            raise R12RemoteError("TARGET_PLAN_DEADLINE_EXHAUSTED")
        return min(cap, max(1, int(available)))

    queries = plan_ab.query_definitions(campaign_id)
    before_metadata = plan_ab.table_evidence(
        None, binary, port, env, output=output, label="before"
    )
    before = plan_ab.capture_queries(
        None, binary, port, env, queries, output, "before", deadline=deadline - 300
    )
    receipt_scan = any(before[f"receipt-{index:02d}"]["full_scan"] for index in range(5))
    projection_scan = before["stale-projection-read"]["full_scan"]
    if not receipt_scan:
        raise R12RemoteError("TARGET_RECEIPT_FULL_SCAN_NOT_OBSERVED")
    plan_ab.run_sql(
        None, binary, port, env, plan_ab.RECEIPT_INDEX_DDL, timeout=remaining(1800)
    )
    indexes = ["receipts_task_id_idx"]
    if projection_scan:
        plan_ab.run_sql(
            None, binary, port, env, plan_ab.PROJECTION_INDEX_DDL, timeout=remaining(1800)
        )
        indexes.append("projection_events_source_key_idx")
    plan_ab.run_sql(
        None,
        binary,
        port,
        env,
        "CREATE STATISTICS r12_receipts_stats ON task_id FROM ck.receipts;"
        "CREATE STATISTICS r12_projection_stats ON source_key FROM ck.projection_events",
        timeout=remaining(1800),
    )
    after_metadata = plan_ab.table_evidence(
        None, binary, port, env, output=output, label="after"
    )
    after = plan_ab.capture_queries(
        None, binary, port, env, queries, output, "after", deadline=deadline - 300
    )
    mismatches = sorted(name for name in queries if before[name]["result_sha256"] != after[name]["result_sha256"])
    scans = sorted(
        name
        for name in queries
        if (name.startswith("receipt-") or name == "stale-projection-read")
        and (after[name]["full_scan"] or after[name]["analyze_full_scan"])
    )
    body = {
        "version": "ck-pdh3-r12-target-plan-ab-v1",
        "query_count": len(queries),
        "before_metadata": before_metadata,
        "after_metadata": after_metadata,
        "before": before,
        "after": after,
        "receipt_full_scan_before": receipt_scan,
        "projection_full_scan_before": projection_scan,
        "selected_indexes": indexes,
        "mismatched_results": mismatches,
        "prohibited_scans_after": scans,
        "green": not mismatches and not scans,
    }
    if not body["green"]:
        raise R12RemoteError("TARGET_PLAN_AB_FAILED")
    return write_record(output / "receipt.json", body, "receipt_sha256")


def verify_full_setup(
    binary: Path,
    nodes: list[scale.Node],
    env: dict[str, str],
    journal: scale.ChainLog,
    args: argparse.Namespace,
    output: Path,
) -> tuple[tuple[int, ...], dict[str, Any]]:
    gateway = nodes[0].sql_port
    deadline = time.monotonic() + args.setup_timeout_seconds
    reserve = scale.setup_tail_reserve(args.setup_timeout_seconds)
    preseed = scale.prove_preseed_vector_index(binary, gateway, env, deadline, reserve)
    seeded = scale.seed_dataset(
        binary,
        gateway,
        env,
        journal,
        campaign_id=args.campaign_id,
        tasks=contract.TASKS,
        events_per_task=contract.EVENTS_PER_TASK,
        receipts_per_task=contract.RECEIPTS_PER_TASK,
        vectors=contract.VECTORS,
        batch_tasks=contract.SEED_BATCH_TASKS,
        setup_deadline=deadline,
        tail_reserve_seconds=reserve,
    )
    seeded_index = scale.prove_seeded_vector_index(
        binary, gateway, env, deadline, args.campaign_id, contract.VECTORS, 600
    )
    expected = (
        contract.TASKS,
        contract.TASKS * contract.EVENTS_PER_TASK,
        contract.TASKS * contract.RECEIPTS_PER_TASK,
        contract.VECTORS,
    )
    actual = scale.campaign_counts(binary, gateway, env, args.campaign_id, deadline, reserve_seconds=600)
    reconciliations = scale.campaign_reconciliations(
        binary,
        gateway,
        env,
        campaign_id=args.campaign_id,
        tasks=contract.TASKS,
        events_per_task=contract.EVENTS_PER_TASK,
        receipts_per_task=contract.RECEIPTS_PER_TASK,
        vectors=contract.VECTORS,
        setup_deadline=deadline,
        reserve_seconds=600,
    )
    plan = ensure_plans(
        binary, gateway, env, args.campaign_id, output / "plans", deadline
    )
    resources = scale.process_metrics(nodes, args.runtime_root, args.output)
    scale.enforce_resource_thresholds(resources, production=True)
    elapsed = args.setup_timeout_seconds - max(0.0, deadline - time.monotonic())
    body = {
        "version": "ck-pdh3-r12-pf5-full-setup-v1",
        "campaign_id": args.campaign_id,
        "expected_counts": list(expected),
        "actual_counts": list(actual),
        "seed": seeded,
        "vector_index_preseed": preseed,
        "vector_index_postseed": seeded_index,
        "reconciliations": reconciliations,
        "target_plan_receipt_sha256": plan["receipt_sha256"],
        "resources": resources,
        "setup_elapsed_seconds": elapsed,
        "setup_deadline_seconds": args.setup_timeout_seconds,
        "green": (
            actual == expected
            and preseed["green"]
            and seeded_index["green"]
            and all(row["state"] == "EXACT" and row["mismatch_rows"] == 0 for row in reconciliations.values())
            and plan["green"]
            and time.monotonic() <= deadline
        ),
    }
    if not body["green"]:
        raise R12RemoteError("PF5_FULL_SETUP_FAILED")
    return expected, write_record(output / "PF5_RESULT.json", body, "receipt_sha256")


def query_matrix(
    binary: Path,
    nodes: list[scale.Node],
    env: dict[str, str],
    args: argparse.Namespace,
    output: Path,
) -> dict[str, Any]:
    canary = scale.load_canary_module()
    fake = argparse.Namespace(
        query_duration_seconds=contract.QUERY_DURATION_SECONDS,
        tasks=contract.TASKS,
        events_per_task=contract.EVENTS_PER_TASK,
        receipts_per_task=contract.RECEIPTS_PER_TASK,
        vectors=contract.VECTORS,
    )
    scale.configure_canary_module(canary, fake)
    query_files = make_query_files(canary, output / "queries", args.campaign_id)
    named: dict[str, Any] = {}
    for family in NAMED_FAMILIES:
        named[family] = {}
        for concurrency in NAMED_CONCURRENCY:
            named[family][str(concurrency)] = run_bench(
                canary,
                binary,
                nodes[0].sql_port,
                query_files[family]["path"],
                output / "named" / family / f"c{concurrency}",
                concurrency,
                f"{family}-c{concurrency}",
                env,
                contract.QUERY_DURATION_SECONDS,
            )
    one_gateway = run_bench(
        canary,
        binary,
        nodes[0].sql_port,
        query_files["read_mix"]["path"],
        output / "gateway" / "one",
        500,
        "one-gateway-c500",
        env,
        contract.QUERY_DURATION_SECONDS,
    )
    three_gateway = run_three_gateway(
        canary,
        binary,
        nodes,
        query_files["read_mix"]["path"],
        output / "gateway" / "three",
        env,
        contract.QUERY_DURATION_SECONDS,
    )

    order = ["observer_on", "observer_off"] if int(args.packet_sha256[-1], 16) % 2 else ["observer_off", "observer_on"]
    ab: dict[str, Any] = {}
    for label in order:
        sampler = None
        if label == "observer_on":
            sampler = Sampler(output / "observer-ab.ndjson", nodes, args.runtime_root, args.output)
            sampler.start()
        try:
            ab[label] = run_bench(
                canary,
                binary,
                nodes[0].sql_port,
                query_files["read_mix"]["path"],
                output / "observer-ab" / label,
                500,
                label,
                env,
                contract.QUERY_DURATION_SECONDS,
            )
        finally:
            if sampler is not None:
                ab[label]["sampler"] = sampler.stop()
    baseline = max(ab["observer_off"]["summary"]["latency_ms"]["p99"], 0.001)
    overhead = max(0.0, (ab["observer_on"]["summary"]["latency_ms"]["p99"] - baseline) / baseline)
    if overhead > 0.10:
        raise R12RemoteError("OBSERVER_OVERHEAD_LIMIT")

    sampler = Sampler(output / "mixed-epochs-observer.ndjson", nodes, args.runtime_root, args.output)
    sampler.start()
    mixed_epochs: list[dict[str, Any]] = []
    try:
        for index in range(3):
            mixed_epochs.append(
                run_bench(
                    canary,
                    binary,
                    nodes[0].sql_port,
                    query_files["read_mix"]["path"],
                    output / "mixed" / f"epoch-{index + 1}",
                    500,
                    f"mixed-c500-{index + 1}",
                    env,
                    contract.QUERY_DURATION_SECONDS,
                )
            )
    finally:
        mixed_sampler = sampler.stop()
    body = {
        "version": "ck-pdh3-r12-pf6-query-matrix-v1",
        "literal_c500": True,
        "named": named,
        "one_gateway": one_gateway,
        "three_gateway": three_gateway,
        "observer_ab_order": order,
        "observer_ab": ab,
        "observer_p99_overhead_fraction": overhead,
        "mixed_epochs": mixed_epochs,
        "mixed_sampler": mixed_sampler,
        "green": all(
            row["green"]
            for family in named.values()
            for row in family.values()
        ) and one_gateway["green"] and three_gateway["green"] and all(row["green"] for row in mixed_epochs) and overhead <= 0.10,
    }
    if not body["green"]:
        raise R12RemoteError("PF6_QUERY_MATRIX_FAILED")
    return write_record(output / "PF6_RESULT.json", body, "receipt_sha256")


def growth_projection(samples: list[dict[str, int]], elapsed: float) -> dict[str, Any]:
    if len(samples) < 2 or elapsed <= 0:
        raise R12RemoteError("GROWTH_SAMPLES_INSUFFICIENT")
    first, last = samples[0], samples[-1]
    projections: dict[str, int] = {}
    for key in first:
        delta = max(0, last[key] - first[key])
        projections[key] = int(last[key] + delta * max(0.0, (86_400 - elapsed) / elapsed))
    return {"first": first, "last": last, "elapsed_seconds": elapsed, "projected_24h": projections}


def run_growth(
    binary: Path,
    nodes: list[scale.Node],
    join: str,
    env: dict[str, str],
    expected: tuple[int, ...],
    args: argparse.Namespace,
    output: Path,
    publisher: Publisher,
) -> dict[str, Any]:
    canary = scale.load_canary_module()
    fake = argparse.Namespace(
        query_duration_seconds=contract.QUERY_DURATION_SECONDS,
        tasks=contract.TASKS,
        events_per_task=contract.EVENTS_PER_TASK,
        receipts_per_task=contract.RECEIPTS_PER_TASK,
        vectors=contract.VECTORS,
    )
    scale.configure_canary_module(canary, fake)
    query_file = make_query_files(canary, output / "queries", args.campaign_id)["read_mix"]["path"]
    sampler = Sampler(output / "growth-observer.ndjson", nodes, args.runtime_root, args.output)
    sampler.start()
    samples: list[dict[str, int]] = [
        {
            "database": sum(scale.tree_bytes(node.store) for node in nodes),
            "evidence": tree_bytes(args.output),
            "network": tree_bytes(args.network_observer_dir),
        }
    ]
    started = time.monotonic()
    index = 0
    try:
        while time.monotonic() - started < GROWTH_SECONDS:
            remaining = GROWTH_SECONDS - (time.monotonic() - started)
            duration = max(1, min(contract.QUERY_DURATION_SECONDS, int(remaining)))
            run_bench(
                canary,
                binary,
                nodes[0].sql_port,
                query_file,
                output / "growth" / f"segment-{index + 1}",
                500,
                f"growth-c500-{index + 1}",
                env,
                duration,
            )
            index += 1
            samples.append(
                {
                    "database": sum(scale.tree_bytes(node.store) for node in nodes),
                    "evidence": tree_bytes(args.output),
                    "network": tree_bytes(args.network_observer_dir),
                }
            )
    finally:
        sampler_receipt = sampler.stop()
    elapsed = time.monotonic() - started
    projection = growth_projection(samples, elapsed)
    projected = projection["projected_24h"]
    if projected["network"] > NETWORK_PROJECTION_LIMIT:
        raise R12RemoteError("NETWORK_PROJECTION_LIMIT")
    if projected["evidence"] > OTHER_EVIDENCE_LIMIT:
        raise R12RemoteError("EVIDENCE_PROJECTION_LIMIT")
    if projected["database"] > DATABASE_PROJECTION_LIMIT:
        raise R12RemoteError("DATABASE_PROJECTION_LIMIT")

    fault = scale.fault_cycle(
        binary,
        nodes,
        0,
        join,
        contract.NODE_CACHE,
        contract.NODE_SQL_MEMORY,
        env,
        args.campaign_id,
        deadline=time.monotonic() + 300,
    )
    if not fault["green"] or scale.campaign_counts(binary, nodes[0].sql_port, env, args.campaign_id) != expected:
        raise R12RemoteError("SAME_HOST_FAULT_RECONCILIATION_FAILED")

    pre_interrupt = write_record(
        output / "pre-interruption.json",
        {
            "version": "ck-pdh3-r12-pre-interruption-v1",
            "projection": projection,
            "sampler": sampler_receipt,
            "fault": fault,
            "green": True,
        },
        "receipt_sha256",
    )
    manifest = publisher.publish(Path("pf7/pre-interruption.json"), Path("pf7/growth-observer.ndjson"))
    ack_path = args.remote_ack_root / f"host-ack-{manifest['sequence']:04d}.json"
    ack_deadline = time.monotonic() + args.host_ack_timeout_seconds
    while time.monotonic() < ack_deadline and not ack_path.is_file():
        time.sleep(1)
    if not ack_path.is_file():
        raise R12RemoteError("OFFPOD_ACK_MISSING")
    ack = json.loads(read_small(ack_path))
    if (
        ack.get("manifest_sha256") != manifest["manifest_sha256"]
        or ack.get("packet_sha256") != args.packet_sha256
        or ack.get("verified") is not True
    ):
        raise R12RemoteError("OFFPOD_ACK_INVALID")

    target = subprocess.Popen(["sleep", "600"], stdin=subprocess.DEVNULL, start_new_session=True)
    partial = publisher.export / f"checkpoint-{manifest['sequence'] + 1:04d}.tgz.part"
    atomic_write(partial, b"intentionally incomplete successor")
    latest_before = read_small(publisher.export / "latest.json")
    os.killpg(target.pid, signal.SIGKILL)
    target.wait(timeout=10)
    if target.returncode != -signal.SIGKILL or read_small(publisher.export / "latest.json") != latest_before:
        raise R12RemoteError("INTERRUPTION_CANARY_FAILED")
    body = {
        "version": "ck-pdh3-r12-pf7-growth-interruption-v1",
        "growth_seconds": elapsed,
        "growth_segments": index,
        "projection": projection,
        "network_projection_limit": NETWORK_PROJECTION_LIMIT,
        "evidence_projection_limit": OTHER_EVIDENCE_LIMIT,
        "database_projection_limit": DATABASE_PROJECTION_LIMIT,
        "sampler": sampler_receipt,
        "same_host_fault": fault,
        "offpod_manifest_sha256": manifest["manifest_sha256"],
        "offpod_ack_sha256": digest(ack),
        "killed_process_returncode": target.returncode,
        "partial_successor_rejected": True,
        "pre_interruption_receipt_sha256": pre_interrupt["receipt_sha256"],
        "green": True,
    }
    return write_record(output / "PF7_RESULT.json", body, "receipt_sha256")


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if re.fullmatch(r"[0-9a-f]{64}", args.packet_sha256) is None:
        raise R12RemoteError("PACKET_SHA256_INVALID")
    if os.environ.get("PDH3_PACKET_SHA256") != args.packet_sha256:
        raise R12RemoteError("PACKET_ENV_BINDING_INVALID")
    binary = args.binary.resolve()
    packet = args.packet.resolve()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise R12RemoteError("COCKROACH_BINARY_INVALID")
    if not packet.is_file() or file_sha256(packet) != args.packet_sha256:
        raise R12RemoteError("PACKET_FILE_BINDING_INVALID")
    if args.output.exists() or args.export_root.exists() or args.remote_ack_root.exists():
        raise R12RemoteError("OUTPUT_OR_EXPORT_ALREADY_EXISTS")
    args.output.mkdir(parents=True)
    args.export_root.mkdir(parents=True)
    args.remote_ack_root.mkdir(parents=True)
    publisher = Publisher(args.output, args.export_root, args.packet_sha256)

    pf2 = plan_ab.execute(
        args.output / "pf2r",
        PLAN_SHA256,
        binary=binary,
        runtime_parent=args.pf2_runtime_parent,
    )
    if not pf2["green"]:
        raise R12RemoteError("PF2R_NOT_GREEN")
    publisher.publish(Path("pf2r"))

    runtime_parent = args.runtime_root_parent.resolve()
    runtime_parent.mkdir(parents=True, exist_ok=True)
    args.runtime_root = Path(tempfile.mkdtemp(prefix=args.campaign_id + ".", dir=runtime_parent))
    fake_home = args.runtime_root / "empty-home"
    fake_home.mkdir()
    env = scale.scrubbed_env(fake_home)
    journal = scale.ChainLog(args.output / "journal.ndjson", args.campaign_id)
    nodes: list[scale.Node] = []
    join = ""
    teardown = {"nodes_stopped": False, "ports_closed": False, "generated_root_removed": False, "database_dropped": False}
    success = False
    try:
        nodes, join = scale.start_cluster(
            binary,
            args.runtime_root,
            env,
            contract.NODE_CACHE,
            contract.NODE_SQL_MEMORY,
        )
        scale.apply_migrations(binary, nodes[0].sql_port, env)
        expected, pf5 = verify_full_setup(binary, nodes, env, journal, args, args.output / "pf5")
        publisher.publish(Path("pf5"), Path("journal.ndjson"))
        pf6 = query_matrix(binary, nodes, env, args, args.output / "pf6")
        publisher.publish(Path("pf6"))
        pf7 = run_growth(binary, nodes, join, env, expected, args, args.output / "pf7", publisher)
        publisher.publish(Path("pf7/PF7_RESULT.json"))
        scale.sql(
            binary,
            nodes[0].sql_port,
            "DROP DATABASE cockroach_kernel CASCADE",
            env=env,
            database=None,
            timeout=1800,
        )
        teardown["database_dropped"] = True
        teardown_receipt = scale.close_local_campaign(
            nodes,
            args.runtime_root,
            args.campaign_id,
            teardown,
            require_database_drop=True,
        )
        atomic_write(args.output / "local-teardown.json", canonical(teardown_receipt))
        nodes = []
        success = True
        body = {
            "version": "ck-pdh3-r12-remote-preflight-result-v1",
            "status": "GREEN_PENDING_PF8",
            "campaign_id": args.campaign_id,
            "packet_sha256": args.packet_sha256,
            "plan_sha256": PLAN_SHA256,
            "pf2_amendment_sha256": PF2_AMENDMENT_SHA256,
            "pf2r_receipt_sha256": pf2["receipt_sha256"],
            "pf5_receipt_sha256": pf5["receipt_sha256"],
            "pf6_receipt_sha256": pf6["receipt_sha256"],
            "pf7_receipt_sha256": pf7["receipt_sha256"],
            "teardown_receipt_sha256": teardown_receipt["receipt_sha256"],
            "measured_24h_started": False,
            "green_pending_pf8": True,
        }
        result = write_record(args.output / "result.json", body, "result_sha256")
        publisher.publish(Path("result.json"), Path("local-teardown.json"), Path("journal.ndjson"))
        return result
    except BaseException as exc:
        failure = {
            "version": "ck-pdh3-r12-remote-preflight-failure-v1",
            "campaign_id": args.campaign_id,
            "packet_sha256": args.packet_sha256,
            "exception_type": type(exc).__name__,
            "reason": str(exc),
            "measured_24h_started": False,
        }
        write_record(args.output / "failure.json", failure, "failure_sha256")
        raise
    finally:
        if not success and args.runtime_root.exists():
            try:
                receipt = scale.close_local_campaign(
                    nodes,
                    args.runtime_root,
                    args.campaign_id,
                    teardown,
                    require_database_drop=False,
                )
                atomic_write(args.output / "local-teardown.json", canonical(receipt))
            except BaseException as exc:
                write_record(
                    args.output / "local-teardown-blocked.json",
                    {"version": "ck-pdh3-r12-local-teardown-blocked-v1", "reason": str(exc), "green": False},
                    "receipt_sha256",
                )


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--binary", type=Path, required=True)
    value.add_argument("--packet", type=Path, required=True)
    value.add_argument("--packet-sha256", required=True)
    value.add_argument("--campaign-id", required=True)
    value.add_argument("--output", type=Path, required=True)
    value.add_argument("--export-root", type=Path, required=True)
    value.add_argument("--remote-ack-root", type=Path, required=True)
    value.add_argument("--network-observer-dir", type=Path, required=True)
    value.add_argument("--runtime-root-parent", type=Path, default=Path("/tmp"))
    value.add_argument("--pf2-runtime-parent", type=Path, default=Path("/tmp"))
    value.add_argument("--setup-timeout-seconds", type=int, default=contract.SETUP_TIMEOUT_SECONDS)
    value.add_argument("--host-ack-timeout-seconds", type=int, default=600)
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    if not args.campaign_id.startswith("ck-pdh3-r12-preflight-"):
        raise R12RemoteError("CAMPAIGN_ID_INVALID")
    if not 3600 <= args.setup_timeout_seconds <= 10_800:
        raise R12RemoteError("SETUP_TIMEOUT_INVALID")
    if not 60 <= args.host_ack_timeout_seconds <= 1800:
        raise R12RemoteError("HOST_ACK_TIMEOUT_INVALID")
    execute(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
