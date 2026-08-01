#!/usr/bin/env python3
"""Credential-free three-node PDH-3 production-shaped scale campaign.

The production mode is hash-bound to the frozen packet and exact 24-hour
contract. A reduced smoke mode exercises the same cluster, query, verifier,
fault, evidence, cleanup, and teardown paths without making scale claims.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import stat as stat_module
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable

import pdh3_scale_contract as contract


BASE = Path(__file__).resolve().parents[1]
ZERO_HASH = "0" * 64
SQLSTATE_RE = re.compile(r"SQLSTATE(?:\s*[:=]\s*|\s+)([0-9A-Z]{5})", re.IGNORECASE)
SERIALIZATION_SQLSTATE = "40001"
SEED_STATEMENT_TIMEOUT_SECONDS = 900
SETUP_SQL_TIMEOUT_SECONDS = 60
FULL_RECONCILIATION_TIMEOUT_SECONDS = 300
VECTOR_SEED_BATCH_TASKS = 250
PRODUCTION_SETUP_TAIL_RESERVE_SECONDS = 2_400
SETUP_RECEIPT_FINALIZATION_RESERVE_SECONDS = 5
MAX_SEED_ATTEMPTS = 4
MAX_CLUSTER_RECOVERY_RESTARTS_PER_NODE = 3
CLUSTER_RECOVERY_STABLE_POLLS = 2
PRODUCTION_TASK_ID_WIDTH = 6
EPOCH_FINAL_RESERVE_SECONDS = 15
CHECKPOINT_DRIFT_SECONDS = 2
TRACE_PROGRESS_MAX_AGE_SECONDS = 90
PREFLIGHT_CONTROL_RESET_VERSION = "ck-pdh3-preflight-control-reset-v1"
FAULT_TRANSITION_SQLSTATES = {"08003", "08006", "57P01"}
FAULT_TRANSITION_MARKERS = (
    "client connection is closing",
    "connection refused",
    "connection reset by peer",
    "node is unavailable",
)


class CampaignError(RuntimeError):
    pass


class CommandError(CampaignError):
    """Bounded, machine-classifiable failure from an external command."""

    def __init__(
        self,
        kind: str,
        executable: str,
        output_sha256: str,
        *,
        timeout_seconds: int | None = None,
        returncode: int | None = None,
        sqlstate: str | None = None,
        output_tail: str = "",
    ) -> None:
        self.kind = kind
        self.executable = executable
        self.output_sha256 = output_sha256
        self.timeout_seconds = timeout_seconds
        self.returncode = returncode
        self.sqlstate = sqlstate
        self.output_tail = output_tail
        fields = ["COMMAND", kind, executable, output_sha256]
        if timeout_seconds is not None:
            fields.append(f"timeout={timeout_seconds}")
        if returncode is not None:
            fields.append(f"returncode={returncode}")
        if sqlstate is not None:
            fields.append(f"sqlstate={sqlstate}")
        if output_tail:
            fields.append(f"tail={output_tail}")
        super().__init__(":".join(fields))

    @property
    def retryable(self) -> bool:
        return self.kind == "TIMEOUT" or self.sqlstate == SERIALIZATION_SQLSTATE

    @property
    def server_effect_uncertain(self) -> bool:
        """True only when a schema-change job may outlive the SQL client."""
        if self.kind == "TIMEOUT":
            return True
        tail = self.output_tail.lower()
        return all(
            marker in tail
            for marker in (
                "waiting for job(s) to complete",
                "jobs will continue in the background",
                "error: connection lost",
            )
        )


class SqlOperationError(CampaignError):
    """SQL failure bound to the deterministic operation that produced it."""

    def __init__(
        self,
        cause: CommandError,
        *,
        stage: str,
        start: int | None,
        stop: int | None,
        statement_sha256: str,
    ) -> None:
        self.cause = cause
        self.stage = stage
        self.start = start
        self.stop = stop
        self.statement_sha256 = statement_sha256
        self.sqlstate = cause.sqlstate
        start_text = "-" if start is None else str(start)
        stop_text = "-" if stop is None else str(stop)
        super().__init__(
            "SQL_OPERATION_FAILED:"
            f"stage={stage}:range={start_text}-{stop_text}:"
            f"statement_sha256={statement_sha256}:{cause}"
        )

    @property
    def retryable(self) -> bool:
        return self.cause.retryable

    @property
    def server_effect_uncertain(self) -> bool:
        return self.cause.server_effect_uncertain

    @property
    def connection_transition(self) -> bool:
        tail = self.cause.output_tail.lower()
        return self.sqlstate in FAULT_TRANSITION_SQLSTATES or any(
            marker in tail for marker in FAULT_TRANSITION_MARKERS
        )


class SetupDeadlineError(CampaignError):
    pass


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
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
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
        if temporary.exists():
            temporary.unlink()


class ChainLog:
    def __init__(self, path: Path, campaign_id: str) -> None:
        if path.exists():
            raise CampaignError("JOURNAL_ALREADY_EXISTS")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.campaign_id = campaign_id
        self.sequence = 0
        self.previous = ZERO_HASH
        self.started_ns = time.monotonic_ns()

    def emit(self, event: str, details: dict[str, Any]) -> dict[str, Any]:
        self.sequence += 1
        body = {
            "version": "ck-pdh3-scale-journal-v1",
            "campaign_id": self.campaign_id,
            "sequence": self.sequence,
            "event": event,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "elapsed_ns": time.monotonic_ns() - self.started_ns,
            "previous_hash": self.previous,
            "details": details,
        }
        record = {**body, "event_hash": digest(body)}
        with self.path.open("ab") as handle:
            handle.write(canonical(record) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous = record["event_hash"]
        return record


def load_canary_module() -> Any:
    path = BASE / "post-dogfood/run_pdh3_local_canary.py"
    spec = importlib.util.spec_from_file_location("pdh3_local_canary_reuse", path)
    if spec is None or spec.loader is None:
        raise CampaignError("CANARY_MODULE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def configure_canary_module(canary: Any, args: argparse.Namespace) -> None:
    """Bind reusable canary helpers to this exact declared campaign shape."""
    canary.CANDIDATE = contract.PRODUCT_CANDIDATE
    canary.P99_LIMIT_MS = contract.P99_LIMIT_MS
    canary.PMAX_LIMIT_MS = contract.PMAX_LIMIT_MS
    canary.STAGE_DURATION_SECONDS = args.query_duration_seconds
    canary.TASK_ID_WIDTH = PRODUCTION_TASK_ID_WIDTH
    canary.TASKS = args.tasks
    canary.EVENTS_PER_TASK = args.events_per_task
    canary.RECEIPTS_PER_TASK = args.receipts_per_task
    canary.VECTORS_PER_TASK = 1
    canary.QUERY_SAMPLES = min(200, args.vectors)


def fault_transition_retryable(exc: CommandError) -> bool:
    tail = exc.output_tail.lower()
    return (
        exc.kind == "TIMEOUT"
        or exc.sqlstate in FAULT_TRANSITION_SQLSTATES
        or any(marker in tail for marker in FAULT_TRANSITION_MARKERS)
    )


def fault_transition_read(operation: Any, *, deadline: float) -> Any:
    """Retry only bounded transport transitions induced by the declared fault."""
    attempts = 0
    while time.monotonic() < deadline - 1:
        attempts += 1
        try:
            return operation()
        except CommandError as exc:
            if not fault_transition_retryable(exc):
                raise
            remaining = deadline - time.monotonic()
            if remaining <= 1:
                break
            time.sleep(min(0.25 * attempts, 1.0, remaining - 1))
    raise CampaignError("FAULT_TRANSITION_READ_EXHAUSTED")


def reserve_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", 0))
        return int(handle.getsockname()[1])


def scrubbed_env(fake_home: Path) -> dict[str, str]:
    return {
        "HOME": str(fake_home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "TZ": "UTC",
        "COCKROACH_SKIP_ENABLING_DIAGNOSTIC_REPORTING": "true",
    }


def run(
    command: list[str],
    *,
    env: dict[str, str],
    timeout: int,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[bytes]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        partial_value = exc.stdout or b""
        partial = (
            partial_value.encode("utf-8", "replace")
            if isinstance(partial_value, str)
            else partial_value
        )
        raise CommandError(
            "TIMEOUT",
            Path(command[0]).name,
            digest(partial),
            timeout_seconds=timeout,
            sqlstate=extract_sqlstate(partial),
        ) from exc
    if completed.returncode != 0:
        bounded_tail = completed.stdout[-2_000:].decode("utf-8", "replace")
        raise CommandError(
            "FAILED",
            Path(command[0]).name,
            digest(completed.stdout),
            returncode=completed.returncode,
            sqlstate=extract_sqlstate(completed.stdout),
            output_tail=bounded_tail.replace("\n", "\\n"),
        )
    return completed


def extract_sqlstate(raw: bytes) -> str | None:
    match = SQLSTATE_RE.search(raw.decode("utf-8", "replace"))
    return match.group(1).upper() if match else None


def deadline_timeout(
    deadline: float | None,
    cap_seconds: int,
    *,
    reserve_seconds: int = 1,
    required_seconds: int = 1,
    label: str = "OPERATION",
) -> int:
    """Bound one operation so it cannot consume a shared monotonic deadline."""
    if cap_seconds < 1 or required_seconds < 1 or reserve_seconds < 0:
        raise CampaignError(f"{label}_DEADLINE_ARGUMENT_INVALID")
    if deadline is None:
        return cap_seconds
    available = deadline - time.monotonic() - reserve_seconds
    if available < required_seconds:
        raise CampaignError(
            f"{label}_DEADLINE_RESERVE_EXHAUSTED:"
            f"required_seconds={required_seconds}:reserve_seconds={reserve_seconds}"
        )
    return min(cap_seconds, max(1, int(available)))


def sql(
    binary: Path,
    port: int,
    statement: str,
    *,
    env: dict[str, str],
    database: str | None = "cockroach_kernel",
    timeout: int = 300,
    stage: str | None = None,
    start: int | None = None,
    stop: int | None = None,
    deadline: float | None = None,
    reserve_seconds: int = 1,
) -> bytes:
    command = [
        str(binary),
        "sql",
        "--insecure",
        f"--host=127.0.0.1:{port}",
        "--format=tsv",
    ]
    if database is not None:
        command.append(f"--database={database}")
    command.extend(["--execute", statement])
    try:
        return run(
            command,
            env=env,
            timeout=deadline_timeout(
                deadline,
                timeout,
                reserve_seconds=reserve_seconds,
                label=stage or "SQL",
            ),
        ).stdout
    except CommandError as exc:
        if stage is None:
            raise
        raise SqlOperationError(
            exc,
            stage=stage,
            start=start,
            stop=stop,
            statement_sha256=digest(statement.encode("utf-8")),
        ) from exc


def setup_timeout(
    setup_deadline: float,
    cap_seconds: int,
    *,
    reserve_seconds: int = 0,
) -> int:
    effective_reserve = max(1, reserve_seconds)
    available = setup_deadline - time.monotonic() - effective_reserve
    if available < 1:
        raise SetupDeadlineError(
            "SETUP_DEADLINE_RESERVE_EXHAUSTED:"
            f"reserve_seconds={effective_reserve}"
        )
    return min(cap_seconds, int(available))


def ensure_setup_deadline(setup_deadline: float) -> None:
    if time.monotonic() > setup_deadline:
        raise SetupDeadlineError("SETUP_DEADLINE_EXCEEDED")


def setup_tail_reserve(setup_timeout_seconds: int) -> int:
    return min(
        PRODUCTION_SETUP_TAIL_RESERVE_SECONDS,
        max(1, setup_timeout_seconds // 2),
    )


def setup_margin_gate(
    setup_timeout_seconds: int,
    setup_elapsed_seconds: float,
    *,
    production: bool,
) -> dict[str, Any]:
    required = (
        contract.SETUP_SUCCESS_MARGIN_SECONDS
        if production
        else min(
            contract.SETUP_SUCCESS_MARGIN_SECONDS,
            max(1, setup_timeout_seconds // 2),
        )
    )
    remaining = max(0.0, setup_timeout_seconds - setup_elapsed_seconds)
    return {
        "required_setup_margin_seconds": required,
        "setup_margin_seconds": remaining,
        "setup_margin_met": remaining >= required,
    }


def result_mode_metadata(production: bool) -> dict[str, Any]:
    if production:
        return {
            "version": "ck-pdh3-production-scale-result-v1",
            "cluster_topology": "THREE_NODES_ONE_SECURE_RUNPOD_HOST",
            "limitations": [
                "SYNTHETIC_ONLY",
                "SINGLE_RUNPOD_HOST",
                "NOT_MULTI_REGION",
                "NOT_PRODUCTION_TRAFFIC",
                "LAMBDA_FAILURES_ARE_FROZEN_LOCAL_ADVICE_STATES",
                "GPU_NOT_USED_BY_CPU_BOUND_PROTOCOL",
            ],
        }
    return {
        "version": "ck-pdh3-reduced-local-smoke-result-v1",
        "cluster_topology": "THREE_LOCAL_LOOPBACK_NODES_DISPOSABLE_ROOT",
        "limitations": [
            "SYNTHETIC_ONLY",
            "REDUCED_SCALE_LOCAL_SMOKE",
            "NOT_RUNPOD_EVIDENCE",
            "NOT_TARGET_SCALE",
            "NOT_MULTI_REGION",
            "NOT_PRODUCTION_TRAFFIC",
            "LAMBDA_FAILURES_ARE_FROZEN_LOCAL_ADVICE_STATES",
        ],
    }


def parse_last_integer(raw: bytes) -> int:
    for line in reversed(raw.decode("utf-8", "replace").splitlines()):
        value = line.strip()
        if value.isdigit():
            return int(value)
    raise CampaignError("INTEGER_OUTPUT_MISSING")


def parse_count_tuple(raw: bytes, fields: int) -> tuple[int, ...]:
    for line in reversed(raw.decode("utf-8", "replace").splitlines()):
        values = line.strip().split("\t")
        if len(values) == fields and all(value.isdigit() for value in values):
            return tuple(int(value) for value in values)
    raise CampaignError("COUNT_OUTPUT_INVALID")


def tree_bytes(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


class Node:
    def __init__(
        self,
        index: int,
        sql_port: int,
        http_port: int,
        store: Path,
        log: Path,
        store_size: str | None = None,
    ) -> None:
        self.index = index
        self.sql_port = sql_port
        self.http_port = http_port
        self.store = store
        self.log = log
        self.store_size = store_size
        self.process: subprocess.Popen[bytes] | None = None
        self.log_handle: Any | None = None


def node_command(
    binary: Path,
    node: Node,
    join: str,
    cache: str,
    sql_memory: str,
) -> list[str]:
    store = f"path={node.store}"
    if node.store_size:
        store += f",size={node.store_size}"
    return [
        str(binary),
        "start",
        "--insecure",
        f"--store={store}",
        f"--listen-addr=127.0.0.1:{node.sql_port}",
        f"--advertise-addr=127.0.0.1:{node.sql_port}",
        f"--http-addr=127.0.0.1:{node.http_port}",
        f"--join={join}",
        f"--cache={cache}",
        f"--max-sql-memory={sql_memory}",
        "--logtostderr=ERROR",
    ]


def start_node(
    binary: Path,
    node: Node,
    join: str,
    cache: str,
    sql_memory: str,
    env: dict[str, str],
    *,
    append: bool,
) -> None:
    node.store.mkdir(parents=True, exist_ok=True)
    node.log_handle = node.log.open("ab" if append else "xb", buffering=0)
    try:
        node.process = subprocess.Popen(
            node_command(binary, node, join, cache, sql_memory),
            env=env,
            cwd=node.store.parent,
            stdin=subprocess.DEVNULL,
            stdout=node.log_handle,
            stderr=subprocess.STDOUT,
        )
    except BaseException:
        node.log_handle.close()
        node.log_handle = None
        node.process = None
        raise


def stop_node(node: Node, *, crash: bool) -> int:
    if node.process is None:
        return 0
    process = node.process
    if process.poll() is None:
        process.send_signal(signal.SIGKILL if crash else signal.SIGTERM)
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=15)
    code = int(process.returncode or 0)
    if node.log_handle is not None:
        node.log_handle.close()
    node.process = None
    node.log_handle = None
    return code


def start_cluster(
    binary: Path,
    root: Path,
    env: dict[str, str],
    cache: str,
    sql_memory: str,
    store_size: str | None = None,
    startup_evidence: dict[str, Any] | None = None,
) -> tuple[list[Node], str]:
    ports: set[int] = set()
    while len(ports) < 6:
        ports.add(reserve_port())
    values = list(ports)
    nodes = [
        Node(
            index=index,
            sql_port=values[index * 2],
            http_port=values[index * 2 + 1],
            store=root / f"node-{index + 1}/store",
            log=root / f"node-{index + 1}/cockroach.log",
            store_size=store_size,
        )
        for index in range(3)
    ]
    join = ",".join(f"127.0.0.1:{node.sql_port}" for node in nodes)
    started: list[Node] = []
    evidence = startup_evidence if startup_evidence is not None else {}
    evidence.update(
        {
            "version": "ck-pdh3-cluster-startup-v1",
            "attempted_nodes": len(nodes),
            "candidate_ports": sorted(
                port for node in nodes for port in (node.sql_port, node.http_port)
            ),
            "started_nodes": 0,
            "started_pids": [],
            "cluster_ready": False,
            "partial_teardown_required": False,
            "partial_teardown_proved": False,
            "stop_returncodes": [],
            "open_ports_after_failure": [],
            "log_sha256": {},
        }
    )
    try:
        for node in nodes:
            node.store.parent.mkdir(parents=True)
            start_node(binary, node, join, cache, sql_memory, env, append=False)
            started.append(node)
            evidence["started_nodes"] = len(started)
            evidence["started_pids"].append(
                int(node.process.pid) if node.process is not None else None
            )
        run(
            [
                str(binary),
                "init",
                "--insecure",
                f"--host=127.0.0.1:{nodes[0].sql_port}",
            ],
            env=env,
            timeout=120,
        )
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            try:
                status = cluster_status(
                    binary,
                    nodes,
                    env,
                    deadline=deadline,
                    database=None,
                )
                if status["green"]:
                    evidence["cluster_ready"] = True
                    evidence["partial_teardown_proved"] = True
                    return nodes, join
            except (CampaignError, subprocess.TimeoutExpired):
                time.sleep(1)
        raise CampaignError("THREE_NODE_CLUSTER_READINESS_TIMEOUT")
    except BaseException as exc:
        evidence["failure_type"] = type(exc).__name__
        evidence["failure_sha256"] = digest(
            {"type": type(exc).__name__, "reason": str(exc)}
        )
        evidence["partial_teardown_required"] = bool(started)
        stop_codes: list[int] = []
        for node in started:
            stop_codes.append(stop_node(node, crash=False))
        evidence["stop_returncodes"] = stop_codes
        evidence["log_sha256"] = {
            f"node-{node.index + 1}": file_sha256(node.log)
            for node in started
            if node.log.is_file()
        }
        open_ports: list[int] = []
        for node in started:
            for port in (node.sql_port, node.http_port):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                    probe.settimeout(0.2)
                    if probe.connect_ex(("127.0.0.1", port)) == 0:
                        open_ports.append(port)
        evidence["open_ports_after_failure"] = open_ports
        evidence["partial_teardown_proved"] = (
            bool(started)
            and all(node.process is None for node in started)
            and not open_ports
            and len(stop_codes) == len(started)
        )
        if any(node.process is not None for node in started) or open_ports:
            raise CampaignError("PARTIAL_CLUSTER_TEARDOWN_FAILED")
        raise


def cluster_status(
    binary: Path,
    nodes: list[Node],
    env: dict[str, str],
    *,
    deadline: float | None,
    database: str | None = "cockroach_kernel",
) -> dict[str, Any]:
    """Prove exactly three live processes and SQL-ready endpoints."""
    if len(nodes) != 3:
        raise CampaignError(f"CLUSTER_NODE_COUNT_INVALID:{len(nodes)}")
    rows: list[dict[str, Any]] = []
    for node in nodes:
        process = node.process
        alive = process is not None and process.poll() is None
        pid = process.pid if process is not None else None
        sql_ready = False
        if alive:
            try:
                sql_ready = parse_last_integer(
                    sql(
                        binary,
                        node.sql_port,
                        "SELECT 1",
                        env=env,
                        database=database,
                        timeout=10,
                        deadline=deadline,
                        reserve_seconds=1,
                        stage=f"node_{node.index + 1}_readiness",
                    )
                ) == 1
            except CampaignError:
                sql_ready = False
        rows.append(
            {
                "node": node.index + 1,
                "pid": pid,
                "alive": alive,
                "sql_ready": sql_ready,
            }
        )
    green = len(rows) == 3 and all(
        row["alive"] and row["sql_ready"] for row in rows
    )
    if not green:
        raise CampaignError("THREE_NODE_CLUSTER_NOT_READY:" + digest(rows))
    return {"nodes": rows, "green": True}


def recover_cluster_gateway(
    binary: Path,
    nodes: list[Node],
    join: str,
    cache: str,
    sql_memory: str,
    env: dict[str, str],
    setup_deadline: float,
    *,
    failed_port: int,
    reserve_seconds: int,
    database: str = "cockroach_kernel",
) -> tuple[int, dict[str, Any]]:
    """Continuously restore all three nodes and select a stable SQL gateway."""
    before: list[dict[str, Any]] = []
    restarted: list[dict[str, Any]] = []
    restart_counts = {node.index: 0 for node in nodes}
    for node in nodes:
        process = node.process
        returncode = process.poll() if process is not None else None
        before.append(
            {
                "node": node.index + 1,
                "pid": process.pid if process is not None else None,
                "returncode": returncode,
                "alive": process is not None and returncode is None,
            }
        )
    recovery_deadline = min(
        setup_deadline - max(1, reserve_seconds), time.monotonic() + 180
    )
    if recovery_deadline <= time.monotonic():
        raise SetupDeadlineError("CLUSTER_RECOVERY_DEADLINE_EXHAUSTED")
    stable_polls = 0
    last_status: dict[str, Any] | None = None
    while time.monotonic() < recovery_deadline:
        for node in nodes:
            process = node.process
            returncode = process.poll() if process is not None else None
            if process is not None and returncode is None:
                continue
            if restart_counts[node.index] >= MAX_CLUSTER_RECOVERY_RESTARTS_PER_NODE:
                raise CampaignError(
                    f"CLUSTER_RECOVERY_RESTART_LIMIT:node={node.index + 1}"
                )
            old_pid = process.pid if process is not None else None
            old_returncode = stop_node(node, crash=False)
            start_node(
                binary,
                node,
                join,
                cache,
                sql_memory,
                env,
                append=True,
            )
            restart_counts[node.index] += 1
            restarted.append(
                {
                    "node": node.index + 1,
                    "attempt": restart_counts[node.index],
                    "old_pid": old_pid,
                    "old_returncode": old_returncode,
                    "new_pid": node.process.pid if node.process is not None else None,
                }
            )
        try:
            status = cluster_status(
                binary,
                nodes,
                env,
                deadline=recovery_deadline,
                database=database,
            )
            last_status = status
            stable_polls += 1
            if stable_polls >= CLUSTER_RECOVERY_STABLE_POLLS:
                ordered = sorted(nodes, key=lambda item: item.sql_port == failed_port)
                gateway_port = ordered[0].sql_port
                return gateway_port, {
                    "before": before,
                    "restarted": restarted,
                    "restart_counts": {
                        str(index + 1): count
                        for index, count in sorted(restart_counts.items())
                    },
                    "stable_polls": stable_polls,
                    "after": status,
                    "failed_gateway_port": failed_port,
                    "gateway_port": gateway_port,
                    "green": True,
                }
        except CampaignError:
            stable_polls = 0
        time.sleep(1)
    raise CampaignError(
        "THREE_NODE_CLUSTER_RECOVERY_TIMEOUT:"
        + digest({"restarted": restarted, "last_status": last_status})
    )


def apply_migrations(binary: Path, port: int, env: dict[str, str]) -> None:
    sql(binary, port, "CREATE DATABASE cockroach_kernel", env=env, database=None)
    for relative in (
        "p9-cloud/migrations/001_cloud.sql",
        "p9-cloud/migrations/003_collision_safe_vector_digest.sql",
    ):
        run(
            [
                str(binary),
                "sql",
                "--insecure",
                f"--host=127.0.0.1:{port}",
                "--database=cockroach_kernel",
                f"--file={BASE / relative}",
            ],
            env=env,
            timeout=600,
        )
    sql(
        binary,
        port,
        "CREATE TABLE ck.pdh3_acknowledged_writes "
        "(ack_id STRING PRIMARY KEY,created_at TIMESTAMPTZ NOT NULL);"
        "CREATE TABLE ck.pdh3_counter "
        "(id STRING PRIMARY KEY,value INT8 NOT NULL);"
        "INSERT INTO ck.pdh3_counter VALUES ('shared',0);"
        "CREATE TABLE ck.pdh3_replay_control "
        "(replay_id STRING PRIMARY KEY);",
        env=env,
    )


def q(value: str) -> str:
    if "\x00" in value:
        raise CampaignError("SQL_LITERAL_INVALID")
    return "'" + value.replace("'", "''") + "'"


def vector_literal() -> str:
    values = ",".join(f"{((index % 17) - 8) / 17:.6f}" for index in range(64))
    return q("[" + values + "]") + "::VECTOR(64)"


def seed_batch_statements(
    campaign_id: str,
    start: int,
    stop: int,
    events_per_task: int,
    receipts_per_task: int,
    vector_stop: int,
) -> list[tuple[str, str]]:
    campaign = q(campaign_id)
    prefix = q(campaign_id + "-task-")
    task_expression = f"{prefix} || lpad(i::STRING,6,'0')"
    event_expression = (
        f"{task_expression} || '-event-' || lpad(s::STRING,2,'0')"
    )
    event_hash = (
        f"decode(sha256(({campaign} || '-event-' || i::STRING || '-' || "
        "s::STRING)::BYTES),'hex')"
    )
    parent_hash = (
        "CASE WHEN s=0 THEN decode('" + ZERO_HASH + "','hex') "
        f"ELSE decode(sha256(({campaign} || '-event-' || i::STRING || '-' || "
        "(s-1)::STRING)::BYTES),'hex') END"
    )
    statements = [
        (
            "tasks",
            "INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash) "
            f"SELECT {task_expression},{campaign},"
            "jsonb_build_object('synthetic',true,'task',i),"
            f"decode(sha256(({campaign} || '-task-hash-' || i::STRING)::BYTES),'hex'),"
            f"decode(sha256(({campaign} || '-state-hash-' || i::STRING)::BYTES),'hex') "
            f"FROM generate_series({start},{stop - 1}) AS g(i) "
            "ON CONFLICT (task_id) DO NOTHING",
        ),
        (
            "events",
            "INSERT INTO ck.trajectory_events"
            "(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash) "
            f"SELECT {event_expression},{task_expression},s,{parent_hash},"
            f"decode(sha256(({campaign} || '-state-hash-' || i::STRING)::BYTES),'hex'),"
            "jsonb_build_object('synthetic',true,'sequence',s),"
            f"{event_hash} FROM generate_series({start},{stop - 1}) AS g(i),"
            f"generate_series(0,{events_per_task - 1}) AS e(s) "
            "ON CONFLICT (event_id) DO NOTHING",
        ),
        (
            "receipts",
            "INSERT INTO ck.receipts"
            "(receipt_hash,task_id,event_hash,status,receipt_json) "
            f"SELECT decode(sha256(({campaign} || '-receipt-' || i::STRING || '-' || "
            f"s::STRING)::BYTES),'hex'),{task_expression},{event_hash},'SEALED',"
            "jsonb_build_object('synthetic',true,'receipt',s) "
            f"FROM generate_series({start},{stop - 1}) AS g(i),"
            f"generate_series(0,{receipts_per_task - 1}) AS e(s) "
            "ON CONFLICT (receipt_hash) DO NOTHING",
        ),
    ]
    limited_stop = min(stop, vector_stop)
    if start < limited_stop:
        statements.append(
            (
                "vectors",
                "INSERT INTO ck.context_vectors"
                "(vector_id,task_id,event_hash,namespace,vector,vector_digest) "
                f"SELECT {task_expression} || '-vector-00',{task_expression},"
                f"decode(sha256(({campaign} || '-event-' || i::STRING || '-0')::BYTES),'hex'),"
                f"{campaign},{vector_literal()},"
                f"decode(sha256(({campaign} || '-vector-constant')::BYTES),'hex') "
                f"FROM generate_series({start},{limited_stop - 1}) AS g(i) "
                "ON CONFLICT (vector_id) DO NOTHING",
            )
        )
    return statements


def vector_seed_statement(
    campaign_id: str,
    start: int,
    stop: int,
) -> str:
    """Build one bounded vector insert; vector batches stay independent."""
    if start < 0 or stop <= start or stop - start > VECTOR_SEED_BATCH_TASKS:
        raise CampaignError("VECTOR_SEED_BATCH_RANGE_INVALID")
    campaign = q(campaign_id)
    prefix = q(campaign_id + "-task-")
    task_expression = f"{prefix} || lpad(i::STRING,6,'0')"
    return (
        "INSERT INTO ck.context_vectors"
        "(vector_id,task_id,event_hash,namespace,vector,vector_digest) "
        f"SELECT {task_expression} || '-vector-00',{task_expression},"
        f"decode(sha256(({campaign} || '-event-' || i::STRING || '-0')::BYTES),'hex'),"
        f"{campaign},{vector_literal()},"
        f"decode(sha256(({campaign} || '-vector-constant')::BYTES),'hex') "
        f"FROM generate_series({start},{stop - 1}) AS g(i) "
        "ON CONFLICT (vector_id) DO NOTHING"
    )


def seed_reconciliation_statement(
    stage: str,
    campaign_id: str,
    start: int,
    stop: int,
    events_per_task: int,
    receipts_per_task: int,
    vector_stop: int,
) -> tuple[str, int]:
    campaign = q(campaign_id)
    prefix = q(campaign_id + "-task-")
    task_expression = f"{prefix} || lpad(i::STRING,6,'0')"
    event_expression = f"{task_expression} || '-event-' || lpad(s::STRING,2,'0')"
    event_hash = (
        f"decode(sha256(({campaign} || '-event-' || i::STRING || '-' || "
        "s::STRING)::BYTES),'hex')"
    )
    parent_hash = (
        "CASE WHEN s=0 THEN decode('" + ZERO_HASH + "','hex') "
        f"ELSE decode(sha256(({campaign} || '-event-' || i::STRING || '-' || "
        "(s-1)::STRING)::BYTES),'hex') END"
    )
    if stage == "tasks":
        expected_count = stop - start
        expected = (
            f"SELECT {task_expression} AS task_id,{campaign} AS campaign_id,"
            "jsonb_build_object('synthetic',true,'task',i) AS task_json,"
            f"decode(sha256(({campaign} || '-task-hash-' || i::STRING)::BYTES),'hex') "
            "AS task_hash,"
            f"decode(sha256(({campaign} || '-state-hash-' || i::STRING)::BYTES),'hex') "
            f"AS state_hash FROM generate_series({start},{stop - 1}) AS g(i)"
        )
        table = "ck.tasks"
        alias = "a"
        key = "task_id"
        mismatch = (
            "a.campaign_id IS DISTINCT FROM e.campaign_id OR "
            "a.task_json IS DISTINCT FROM e.task_json OR "
            "a.task_hash IS DISTINCT FROM e.task_hash OR "
            "a.state_hash IS DISTINCT FROM e.state_hash"
        )
    elif stage == "events":
        expected_count = (stop - start) * events_per_task
        expected = (
            f"SELECT {event_expression} AS event_id,{task_expression} AS task_id,"
            f"s AS sequence,{parent_hash} AS parent_event_hash,"
            f"decode(sha256(({campaign} || '-state-hash-' || i::STRING)::BYTES),'hex') "
            "AS state_hash,jsonb_build_object('synthetic',true,'sequence',s) "
            f"AS event_json,{event_hash} AS event_hash "
            f"FROM generate_series({start},{stop - 1}) AS g(i),"
            f"generate_series(0,{events_per_task - 1}) AS x(s)"
        )
        table = "ck.trajectory_events"
        alias = "a"
        key = "event_id"
        mismatch = (
            "a.task_id IS DISTINCT FROM e.task_id OR "
            "a.sequence IS DISTINCT FROM e.sequence OR "
            "a.parent_event_hash IS DISTINCT FROM e.parent_event_hash OR "
            "a.state_hash IS DISTINCT FROM e.state_hash OR "
            "a.event_json IS DISTINCT FROM e.event_json OR "
            "a.event_hash IS DISTINCT FROM e.event_hash"
        )
    elif stage == "receipts":
        expected_count = (stop - start) * receipts_per_task
        receipt_hash = (
            f"decode(sha256(({campaign} || '-receipt-' || i::STRING || '-' || "
            "s::STRING)::BYTES),'hex')"
        )
        expected = (
            f"SELECT {receipt_hash} AS receipt_hash,{task_expression} AS task_id,"
            f"{event_hash} AS event_hash,'SEALED' AS status,"
            "jsonb_build_object('synthetic',true,'receipt',s) AS receipt_json "
            f"FROM generate_series({start},{stop - 1}) AS g(i),"
            f"generate_series(0,{receipts_per_task - 1}) AS x(s)"
        )
        table = "ck.receipts"
        alias = "a"
        key = "receipt_hash"
        mismatch = (
            "a.task_id IS DISTINCT FROM e.task_id OR "
            "a.event_hash IS DISTINCT FROM e.event_hash OR "
            "a.status IS DISTINCT FROM e.status OR "
            "a.receipt_json IS DISTINCT FROM e.receipt_json"
        )
    elif stage == "vectors":
        limited_stop = min(stop, vector_stop)
        expected_count = max(0, limited_stop - start)
        expected = (
            f"SELECT {task_expression} || '-vector-00' AS vector_id,"
            f"{task_expression} AS task_id,"
            f"decode(sha256(({campaign} || '-event-' || i::STRING || '-0')::BYTES),'hex') "
            f"AS event_hash,{campaign} AS namespace,{vector_literal()} AS vector,"
            f"decode(sha256(({campaign} || '-vector-constant')::BYTES),'hex') "
            f"AS vector_digest FROM generate_series({start},{limited_stop - 1}) AS g(i)"
        )
        table = "ck.context_vectors"
        alias = "a"
        key = "vector_id"
        mismatch = (
            "a.task_id IS DISTINCT FROM e.task_id OR "
            "a.event_hash IS DISTINCT FROM e.event_hash OR "
            "a.namespace IS DISTINCT FROM e.namespace OR "
            "(a.vector <-> e.vector) != 0 OR "
            "a.vector_digest IS DISTINCT FROM e.vector_digest"
        )
    else:
        raise CampaignError(f"SEED_STAGE_INVALID:{stage}")
    statement = (
        f"WITH expected AS ({expected}) SELECT count({alias}.{key}),"
        f"count(*) FILTER (WHERE {alias}.{key} IS NOT NULL AND ({mismatch})) "
        f"FROM expected e LEFT JOIN {table} {alias} ON {alias}.{key}=e.{key}"
    )
    return statement, expected_count


def reconcile_seed_batch(
    binary: Path,
    port: int,
    env: dict[str, str],
    *,
    stage: str,
    campaign_id: str,
    start: int,
    stop: int,
    events_per_task: int,
    receipts_per_task: int,
    vector_stop: int,
    setup_deadline: float,
    reserve_seconds: int,
    timeout_cap: int = SETUP_SQL_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    statement, expected_rows = seed_reconciliation_statement(
        stage,
        campaign_id,
        start,
        stop,
        events_per_task,
        receipts_per_task,
        vector_stop,
    )
    actual_rows, content_mismatches = parse_count_tuple(
        sql(
            binary,
            port,
            statement,
            env=env,
            timeout=setup_timeout(
                setup_deadline,
                timeout_cap,
                reserve_seconds=reserve_seconds,
            ),
            stage=f"reconcile_{stage}",
            start=start,
            stop=stop,
        ),
        2,
    )
    missing_rows = max(0, expected_rows - actual_rows)
    mismatch_rows = missing_rows + content_mismatches
    if actual_rows == 0 and content_mismatches == 0:
        state = "ZERO"
    elif actual_rows == expected_rows and content_mismatches == 0:
        state = "EXACT"
    else:
        state = "MISMATCH"
    return {
        "stage": stage,
        "start": start,
        "stop": stop,
        "state": state,
        "expected_rows": expected_rows,
        "actual_rows": actual_rows,
        "missing_rows": missing_rows,
        "content_mismatches": content_mismatches,
        "mismatch_rows": mismatch_rows,
        "statement_sha256": digest(statement.encode("utf-8")),
    }


def vector_index_metadata(
    binary: Path,
    port: int,
    env: dict[str, str],
    setup_deadline: float,
    reserve_seconds: int = 0,
) -> dict[str, Any]:
    statement = (
        "SELECT count(*),"
        "count(*) FILTER (WHERE NOT storing AND NOT implicit),"
        "count(*) FILTER (WHERE column_name='vector' AND NOT storing AND NOT implicit),"
        "count(*) FILTER (WHERE NOT visible) "
        "FROM [SHOW INDEXES FROM ck.context_vectors] "
        "WHERE index_name='context_vectors_vector_idx'"
    )
    rows, key_rows, vector_key_rows, invisible_rows = parse_count_tuple(
        sql(
            binary,
            port,
            statement,
            env=env,
            timeout=setup_timeout(
                setup_deadline,
                SETUP_SQL_TIMEOUT_SECONDS,
                reserve_seconds=reserve_seconds,
            ),
            stage="vector_index_metadata",
        ),
        4,
    )
    return {
        "rows": rows,
        "key_rows": key_rows,
        "vector_key_rows": vector_key_rows,
        "invisible_rows": invisible_rows,
        "green": (
            rows >= 1
            and key_rows == 1
            and vector_key_rows == 1
            and invisible_rows == 0
        ),
    }


def vector_index_coverage(
    binary: Path,
    port: int,
    env: dict[str, str],
    setup_deadline: float,
    vector_count: int,
    reserve_seconds: int = 0,
) -> dict[str, Any]:
    if vector_count < 1:
        raise CampaignError("VECTOR_INDEX_EXPECTED_CARDINALITY_INVALID")
    statement = (
        "SELECT count(*),count(DISTINCT vector_id) FROM ("
        "SELECT vector_id FROM "
        "ck.context_vectors@context_vectors_vector_idx "
        f"ORDER BY vector <-> {vector_literal()} LIMIT {vector_count})"
    )
    returned_rows, distinct_vector_ids = parse_count_tuple(
        sql(
            binary,
            port,
            statement,
            env=env,
            timeout=setup_timeout(
                setup_deadline,
                FULL_RECONCILIATION_TIMEOUT_SECONDS,
                reserve_seconds=reserve_seconds,
            ),
            stage="vector_index_full_coverage",
        ),
        2,
    )
    return {
        "expected_vectors": vector_count,
        "returned_rows": returned_rows,
        "distinct_vector_ids": distinct_vector_ids,
        "statement_sha256": digest(statement.encode("utf-8")),
        "forced_index": "context_vectors_vector_idx",
        "green": (
            returned_rows == vector_count
            and distinct_vector_ids == vector_count
        ),
    }


def prove_preseed_vector_index(
    binary: Path,
    port: int,
    env: dict[str, str],
    setup_deadline: float,
    reserve_seconds: int = 0,
) -> dict[str, Any]:
    """Prove migration created the visible index before any vector is inserted."""
    metadata = vector_index_metadata(
        binary,
        port,
        env,
        setup_deadline,
        reserve_seconds=reserve_seconds,
    )
    vector_rows = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT count(*) FROM ck.context_vectors",
            env=env,
            timeout=setup_timeout(
                setup_deadline,
                SETUP_SQL_TIMEOUT_SECONDS,
                reserve_seconds=reserve_seconds,
            ),
            stage="vector_index_preseed_cardinality",
        )
    )
    return {
        "mode": "PRECREATED_ON_EMPTY_TABLE",
        "metadata": metadata,
        "vector_rows": vector_rows,
        "green": metadata["green"] and vector_rows == 0,
    }


def prove_seeded_vector_index(
    binary: Path,
    port: int,
    env: dict[str, str],
    setup_deadline: float,
    vector_count: int,
    reserve_seconds: int = 0,
) -> dict[str, Any]:
    """Prove the precreated index retained full forced-index coverage after seed."""
    metadata = vector_index_metadata(
        binary,
        port,
        env,
        setup_deadline,
        reserve_seconds=reserve_seconds,
    )
    coverage = vector_index_coverage(
        binary,
        port,
        env,
        setup_deadline,
        vector_count,
        reserve_seconds=reserve_seconds,
    )
    return {
        "mode": "INCREMENTALLY_MAINTAINED_DURING_SEED",
        "metadata": metadata,
        "coverage": coverage,
        "queryable": coverage["green"],
        "green": metadata["green"] and coverage["green"],
    }


def seed_dataset(
    binary: Path,
    port: int,
    env: dict[str, str],
    journal: ChainLog,
    *,
    campaign_id: str,
    tasks: int,
    events_per_task: int,
    receipts_per_task: int,
    vectors: int,
    batch_tasks: int,
    setup_deadline: float,
    tail_reserve_seconds: int = 0,
) -> dict[str, Any]:
    counts = {"tasks": 0, "events": 0, "receipts": 0, "vectors": 0}
    retries = 0
    uncertain_timeouts = 0
    statement_hashes: list[str] = []
    timeout_reconciliations: list[dict[str, Any]] = []

    def execute_seed_statement(
        stage: str,
        statement: str,
        start: int,
        stop: int,
    ) -> None:
        nonlocal retries, uncertain_timeouts
        raw_hash = digest(statement.encode("utf-8"))
        completed = False
        for attempt in range(MAX_SEED_ATTEMPTS):
            try:
                sql(
                    binary,
                    port,
                    statement,
                    env=env,
                    timeout=setup_timeout(
                        setup_deadline,
                        SEED_STATEMENT_TIMEOUT_SECONDS,
                        reserve_seconds=tail_reserve_seconds,
                    ),
                    stage=f"seed_{stage}",
                    start=start,
                    stop=stop,
                )
                completed = True
                break
            except SqlOperationError as exc:
                if not exc.retryable:
                    raise
                if exc.cause.kind == "TIMEOUT":
                    uncertain_timeouts += 1
                    reconciliation = reconcile_seed_batch(
                        binary,
                        port,
                        env,
                        stage=stage,
                        campaign_id=campaign_id,
                        start=start,
                        stop=stop,
                        events_per_task=events_per_task,
                        receipts_per_task=receipts_per_task,
                        vector_stop=vectors,
                        setup_deadline=setup_deadline,
                        reserve_seconds=tail_reserve_seconds,
                    )
                    timeout_reconciliations.append(reconciliation)
                    if reconciliation["state"] == "EXACT":
                        completed = True
                        break
                    if reconciliation["state"] == "MISMATCH":
                        raise CampaignError(
                            "SEED_RECONCILIATION_MISMATCH:"
                            f"stage={stage}:range={start}-{stop}:"
                            f"statement_sha256={raw_hash}:"
                            f"mismatch_rows={reconciliation['mismatch_rows']}"
                        ) from exc
                if attempt == MAX_SEED_ATTEMPTS - 1:
                    raise
                retries += 1
                time.sleep(0.25 * (attempt + 1))
        if not completed:
            raise CampaignError(
                "SEED_BATCH_INCOMPLETE:"
                f"stage={stage}:range={start}-{stop}:"
                f"statement_sha256={raw_hash}"
            )
        rows = stop - start
        if stage == "events":
            rows *= events_per_task
        elif stage == "receipts":
            rows *= receipts_per_task
        counts[stage] += rows
        statement_hashes.append(raw_hash)

    for start in range(0, tasks, batch_tasks):
        setup_timeout(
            setup_deadline,
            1,
            reserve_seconds=tail_reserve_seconds,
        )
        stop = min(tasks, start + batch_tasks)
        for stage, statement in seed_batch_statements(
            campaign_id,
            start,
            stop,
            events_per_task,
            receipts_per_task,
            0,
        ):
            execute_seed_statement(stage, statement, start, stop)
        journal.emit(
            "SEED_BATCH",
            {
                "start": start,
                "stop": stop,
                "counts": dict(counts),
                "statement_set_sha256": digest(statement_hashes),
            },
        )
    for start in range(0, vectors, VECTOR_SEED_BATCH_TASKS):
        setup_timeout(
            setup_deadline,
            1,
            reserve_seconds=tail_reserve_seconds,
        )
        stop = min(vectors, start + VECTOR_SEED_BATCH_TASKS)
        execute_seed_statement(
            "vectors",
            vector_seed_statement(campaign_id, start, stop),
            start,
            stop,
        )
        journal.emit(
            "VECTOR_SEED_BATCH",
            {
                "start": start,
                "stop": stop,
                "maximum_batch_rows": VECTOR_SEED_BATCH_TASKS,
                "counts": dict(counts),
                "statement_set_sha256": digest(statement_hashes),
            },
        )
    return {
        "counts": counts,
        "vector_seed_batch_rows": VECTOR_SEED_BATCH_TASKS,
        "statement_set_sha256": digest(statement_hashes),
        "retries": retries,
        "uncertain_timeouts": uncertain_timeouts,
        "timeout_reconciliations": timeout_reconciliations,
    }


def campaign_counts(
    binary: Path,
    port: int,
    env: dict[str, str],
    campaign: str,
    setup_deadline: float | None = None,
    deadline: float | None = None,
    reserve_seconds: int = 0,
) -> tuple[int, ...]:
    prefix = campaign + "-task-%"
    timeout = (
        setup_timeout(
            setup_deadline,
            SETUP_SQL_TIMEOUT_SECONDS,
            reserve_seconds=reserve_seconds,
        )
        if setup_deadline is not None
        else 300
    )
    return parse_count_tuple(
        sql(
            binary,
            port,
            "SELECT "
            f"(SELECT count(*) FROM ck.tasks WHERE campaign_id={q(campaign)}),"
            f"(SELECT count(*) FROM ck.trajectory_events WHERE task_id LIKE {q(prefix)}),"
            f"(SELECT count(*) FROM ck.receipts WHERE task_id LIKE {q(prefix)}),"
            f"(SELECT count(*) FROM ck.context_vectors WHERE namespace={q(campaign)})",
            env=env,
            timeout=timeout,
            stage="campaign_counts" if setup_deadline is not None else None,
            deadline=deadline,
        ),
        4,
    )


def campaign_reconciliations(
    binary: Path,
    port: int,
    env: dict[str, str],
    *,
    campaign_id: str,
    tasks: int,
    events_per_task: int,
    receipts_per_task: int,
    vectors: int,
    setup_deadline: float,
    reserve_seconds: int = 0,
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for stage in ("tasks", "events", "receipts", "vectors"):
        results[stage] = reconcile_seed_batch(
            binary,
            port,
            env,
            stage=stage,
            campaign_id=campaign_id,
            start=0,
            stop=tasks,
            events_per_task=events_per_task,
            receipts_per_task=receipts_per_task,
            vector_stop=vectors,
            setup_deadline=setup_deadline,
            reserve_seconds=reserve_seconds,
            timeout_cap=FULL_RECONCILIATION_TIMEOUT_SECONDS,
        )
    return results


def dependency_matrix(
    binary: Path,
    port: int,
    env: dict[str, str],
    campaign: str,
    epoch: int,
    *,
    deadline: float | None = None,
) -> dict[str, Any]:
    task_id = f"{campaign}-task-000000"
    statuses = ("ADVISORY", "TIMEOUT", "THROTTLED", "MALFORMED", "STALE")
    for index, status in enumerate(statuses):
        request_id = f"{campaign}-advice-{epoch:04d}-{index}"
        seed = f"{campaign}:{epoch}:{index}"
        sql(
            binary,
            port,
            "INSERT INTO ck.worker_results"
            "(request_id,task_id,candidate_id,request_hash,response_hash,attempt,"
            "supersedes,status,result_json,result_hash) VALUES ("
            f"{q(request_id)},{q(task_id)},{q('candidate-' + str(index))},"
            f"decode(sha256({q(seed + ':request')}::BYTES),'hex'),"
            f"decode(sha256({q(seed + ':response')}::BYTES),'hex'),1,NULL,{q(status)},"
            f"jsonb_build_object('synthetic',true,'status',{q(status)}),"
            f"decode(sha256({q(seed + ':result')}::BYTES),'hex')) ON CONFLICT DO NOTHING",
            env=env,
            deadline=deadline,
            stage="dependency_matrix_insert",
        )
    count = parse_last_integer(
        sql(
            binary,
            port,
            f"SELECT count(*) FROM ck.worker_results WHERE request_id LIKE "
            f"{q(campaign + '-advice-' + format(epoch, '04d') + '-%')}",
            env=env,
            deadline=deadline,
            stage="dependency_matrix_count",
        )
    )
    if count != len(statuses):
        raise CampaignError("DEPENDENCY_MATRIX_COUNT_MISMATCH")
    return {"statuses": list(statuses), "rows": count}


def cleanup_probe(
    binary: Path,
    port: int,
    env: dict[str, str],
    campaign: str,
    epoch: int,
    *,
    deadline: float | None = None,
) -> dict[str, Any]:
    task_id = f"{campaign}-cleanup-{epoch:04d}"
    task_seed = task_id + ":task"
    event_seed = task_id + ":event"
    sql(
        binary,
        port,
        "BEGIN;"
        "INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash)"
        f" VALUES ({q(task_id)},{q(campaign)},'{{\"synthetic\":true}}',"
        f"decode(sha256({q(task_seed)}::BYTES),'hex'),"
        f"decode(sha256({q(task_id + ':state')}::BYTES),'hex'));"
        "INSERT INTO ck.trajectory_events"
        "(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash)"
        f" VALUES ({q(task_id + '-event')},{q(task_id)},0,"
        f"decode('{ZERO_HASH}','hex'),"
        f"decode(sha256({q(task_id + ':state')}::BYTES),'hex'),"
        f"'{{\"synthetic\":true}}',"
        f"decode(sha256({q(event_seed)}::BYTES),'hex'));"
        "COMMIT;"
        f"DELETE FROM ck.trajectory_events WHERE task_id={q(task_id)};"
        f"DELETE FROM ck.tasks WHERE task_id={q(task_id)};",
        env=env,
        deadline=deadline,
        stage="cleanup_probe_transaction",
    )
    residue = parse_last_integer(
        sql(
            binary,
            port,
            f"SELECT count(*) FROM ck.tasks WHERE task_id={q(task_id)}",
            env=env,
            deadline=deadline,
            stage="cleanup_probe_residue",
        )
    )
    if residue != 0:
        raise CampaignError("CLEANUP_PROBE_RESIDUE")
    return {"task_id_hash": digest(task_id.encode()), "residue": residue}


def linux_process_tree_snapshot(
    root_pid: int,
    required_pids: list[int],
    *,
    proc_root: Path = Path("/proc"),
) -> dict[str, Any]:
    """Return a fail-closed Linux procfs process-tree snapshot."""
    unavailable = {
        "available": False,
        "complete": False,
        "root_pid": root_pid,
        "required_pids": sorted(required_pids),
        "required_pids_present": False,
        "missing_required_pids": sorted(required_pids),
        "member_count": None,
        "member_pid_set_sha256": None,
        "unreadable_status_count": None,
    }
    if not proc_root.is_dir():
        return unavailable
    try:
        entries = list(proc_root.iterdir())
    except OSError:
        return unavailable
    parents: dict[int, int] = {}
    unreadable = 0
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            lines = (entry / "status").read_text().splitlines()
        except (FileNotFoundError, ProcessLookupError):
            # A process may exit between readdir and open. It is not part of
            # the point-in-time tree being measured.
            continue
        except (PermissionError, OSError):
            unreadable += 1
            continue
        ppid = None
        for line in lines:
            if line.startswith("PPid:"):
                fields = line.split()
                if len(fields) == 2 and fields[1].isdigit():
                    ppid = int(fields[1])
                break
        if ppid is None:
            unreadable += 1
            continue
        parents[int(entry.name)] = ppid
    members: set[int] = set()
    if root_pid in parents:
        members.add(root_pid)
        changed = True
        while changed:
            changed = False
            for pid, parent in parents.items():
                if pid not in members and parent in members:
                    members.add(pid)
                    changed = True
    missing = sorted(set(required_pids) - members)
    complete = unreadable == 0 and root_pid in parents and not missing
    member_rows = sorted(members)
    return {
        "available": True,
        "complete": complete,
        "root_pid": root_pid,
        "required_pids": sorted(required_pids),
        "required_pids_present": not missing,
        "missing_required_pids": missing,
        "member_count": len(member_rows),
        "member_pid_set_sha256": digest(member_rows),
        "unreadable_status_count": unreadable,
    }


def process_metrics(nodes: list[Node], root: Path, output: Path) -> dict[str, Any]:
    values = []
    for node in nodes:
        pid = node.process.pid if node.process is not None else None
        rss_kb = None
        descriptors = None
        if pid is not None and Path(f"/proc/{pid}/status").is_file():
            for line in Path(f"/proc/{pid}/status").read_text().splitlines():
                if line.startswith("VmRSS:"):
                    rss_kb = int(line.split()[1])
            descriptors = len(list(Path(f"/proc/{pid}/fd").iterdir()))
        values.append(
            {
                "node": node.index + 1,
                "pid": pid,
                "alive": node.process is not None and node.process.poll() is None,
                "rss_kb": rss_kb,
                "descriptors": descriptors,
            }
        )
    usage = shutil.disk_usage(root)
    required_pids = [
        int(row["pid"])
        for row in values
        if row["alive"] is True and row["pid"] is not None
    ]
    return {
        "nodes": values,
        "process_tree": linux_process_tree_snapshot(
            os.getpid(), required_pids
        ),
        "database_bytes": sum(tree_bytes(node.store) for node in nodes),
        "evidence_bytes": tree_bytes(output),
        "disk_total_bytes": usage.total,
        "disk_used_bytes": usage.used,
        "disk_used_fraction": usage.used / usage.total,
    }


def control_counts(
    binary: Path,
    port: int,
    env: dict[str, str],
    *,
    deadline: float | None,
) -> tuple[int, int, int]:
    return parse_count_tuple(
        sql(
            binary,
            port,
            "SELECT "
            "(SELECT count(*) FROM ck.pdh3_acknowledged_writes),"
            "(SELECT value FROM ck.pdh3_counter WHERE id='shared'),"
            "(SELECT count(*) FROM ck.pdh3_replay_control)",
            env=env,
            deadline=deadline,
            stage="control_counts",
        ),
        3,
    )


def reset_preflight_controls(
    binary: Path,
    port: int,
    env: dict[str, str],
    campaign: str,
    *,
    deadline: float,
) -> dict[str, Any]:
    before = control_counts(binary, port, env, deadline=deadline)
    sql(
        binary,
        port,
        "BEGIN;"
        "DELETE FROM ck.pdh3_acknowledged_writes;"
        "UPDATE ck.pdh3_counter SET value=0 WHERE id='shared';"
        "DELETE FROM ck.pdh3_replay_control;"
        f"DELETE FROM ck.worker_results WHERE request_id LIKE {q(campaign + '-advice-%')};"
        "COMMIT;",
        env=env,
        deadline=deadline,
        stage="preflight_control_reset",
    )
    after = control_counts(binary, port, env, deadline=deadline)
    advice_rows = parse_last_integer(
        sql(
            binary,
            port,
            f"SELECT count(*) FROM ck.worker_results WHERE request_id LIKE "
            f"{q(campaign + '-advice-%')}",
            env=env,
            deadline=deadline,
            stage="preflight_advice_reset_count",
        )
    )
    green = after == (0, 0, 0) and advice_rows == 0
    body = {
        "version": PREFLIGHT_CONTROL_RESET_VERSION,
        "before": list(before),
        "after": list(after),
        "preflight_advice_rows": advice_rows,
        "green": green,
    }
    if not green:
        raise CampaignError("PREFLIGHT_CONTROL_RESET_FAILED:" + digest(body))
    return {**body, "reset_sha256": digest(body)}


def fault_cycle(
    binary: Path,
    nodes: list[Node],
    node_index: int,
    join: str,
    cache: str,
    sql_memory: str,
    env: dict[str, str],
    campaign: str,
    *,
    deadline: float,
) -> dict[str, Any]:
    target = nodes[node_index]
    surviving = nodes[(node_index + 1) % len(nodes)]
    if target.process is None or target.process.poll() is not None:
        raise CampaignError("FAULT_TARGET_NOT_ALIVE")
    old_pid = target.process.pid
    before = campaign_counts(
        binary, surviving.sql_port, env, campaign, deadline=deadline
    )
    controls_before = control_counts(
        binary, surviving.sql_port, env, deadline=deadline
    )
    returncode = stop_node(target, crash=True)
    if returncode != -signal.SIGKILL:
        raise CampaignError(f"FAULT_SIGNAL_RETURN_CODE_INVALID:{returncode}")
    during = fault_transition_read(
        lambda: campaign_counts(
            binary, surviving.sql_port, env, campaign, deadline=deadline
        ),
        deadline=deadline,
    )
    controls_during = fault_transition_read(
        lambda: control_counts(
            binary, surviving.sql_port, env, deadline=deadline
        ),
        deadline=deadline,
    )
    start_node(binary, target, join, cache, sql_memory, env, append=True)
    new_pid = target.process.pid if target.process is not None else None
    if new_pid is None or new_pid == old_pid:
        raise CampaignError("FAULT_RESTART_PID_NOT_FRESH")
    while time.monotonic() < deadline - 1:
        try:
            readiness = cluster_status(
                binary, nodes, env, deadline=deadline
            )
            after = campaign_counts(
                binary, target.sql_port, env, campaign, deadline=deadline
            )
            controls_after = control_counts(
                binary, target.sql_port, env, deadline=deadline
            )
            green = (
                readiness["green"]
                and during == before
                and after == before
                and controls_during == controls_before
                and controls_after == controls_before
            )
            if green:
                return {
                    "node": node_index + 1,
                    "signal": "SIGKILL",
                    "returncode": returncode,
                    "old_pid": old_pid,
                    "new_pid": new_pid,
                    "before": list(before),
                    "during": list(during),
                    "after": list(after),
                    "controls_before": list(controls_before),
                    "controls_during": list(controls_during),
                    "controls_after": list(controls_after),
                    "cluster_readiness": readiness,
                    "green": True,
                }
        except CampaignError:
            remaining = deadline - time.monotonic()
            if remaining <= 1:
                break
            time.sleep(min(0.25, remaining - 1))
    raise CampaignError("FAULT_RESTART_RECONCILIATION_FAILED")


def create_query_files(canary: Any, root: Path, campaign_id: str) -> dict[str, dict[str, Any]]:
    canary.CAMPAIGN_ID = campaign_id
    canary.TASK_ID_WIDTH = PRODUCTION_TASK_ID_WIDTH
    return canary.build_query_files(root)


def verifier_batch(
    canary: Any,
    root: Path,
    env: dict[str, str],
    campaign_id: str,
    *,
    deadline: float,
) -> dict[str, Any]:
    canary.CAMPAIGN_ID = campaign_id
    result = canary.run_verifier_campaign(root, env, deadline=deadline)
    if result["measured_executions"] != contract.VERIFIER_BATCH_SIZE:
        raise CampaignError("VERIFIER_BATCH_COUNT_INVALID")
    return result


def preserve_epoch_evidence(
    epoch_root: Path,
    output: Path,
    *,
    lane: str,
    epoch: int,
    deadline: float,
) -> dict[str, Any]:
    """Atomically retain all querybench and verifier evidence before root deletion."""
    deadline_timeout(
        deadline,
        60,
        reserve_seconds=1,
        label="EPOCH_EVIDENCE_COPY",
    )
    raw_root = output / "raw" / lane
    raw_root.mkdir(parents=True, exist_ok=True)
    destination = raw_root / f"epoch-{epoch:04d}"
    temporary = raw_root / f".epoch-{epoch:04d}.{os.getpid()}.tmp"
    if destination.exists() or temporary.exists():
        raise CampaignError("RAW_EPOCH_EVIDENCE_ALREADY_EXISTS")
    shutil.copytree(epoch_root, temporary, symlinks=False)
    files = {
        str(path.relative_to(temporary)): file_sha256(path)
        for path in sorted(temporary.rglob("*"))
        if path.is_file()
    }
    body = {
        "version": "ck-pdh3-raw-epoch-manifest-v1",
        "lane": lane,
        "epoch": epoch,
        "files": files,
        "file_count": len(files),
        "file_set_sha256": digest(files),
    }
    atomic_write(
        temporary / "raw-epoch-manifest.json",
        canonical({**body, "manifest_sha256": digest(body)}),
    )
    os.replace(temporary, destination)
    directory = os.open(raw_root, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return {
        "path": str(destination.relative_to(output)),
        "manifest_sha256": digest(body),
        "file_count": len(files),
    }


def validate_verifier_evidence(
    output: Path,
    *,
    lane: str,
    expected_batches: int,
    expected_receipts: int,
) -> dict[str, Any]:
    roots = sorted((output / "raw" / lane).glob(
        "epoch-*/verifier/verifier-campaign"
    ))
    if len(roots) != expected_batches:
        raise CampaignError(
            f"VERIFIER_EVIDENCE_BATCH_COUNT_INVALID:{len(roots)}:{expected_batches}"
        )
    receipt_hashes: set[str] = set()
    receipt_file_hashes: set[str] = set()
    manifests: list[str] = []
    receipt_count = 0
    for root in roots:
        manifest_path = root / "manifest.json"
        aggregate_path = root / "aggregate.json"
        if not manifest_path.is_file() or not aggregate_path.is_file():
            raise CampaignError("VERIFIER_MANIFEST_OR_AGGREGATE_MISSING")
        manifest = json.loads(manifest_path.read_bytes())
        manifest_hash = manifest.get("manifest_sha256")
        body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
        if manifest_hash != digest(body):
            raise CampaignError("VERIFIER_MANIFEST_HASH_INVALID")
        files = manifest.get("files")
        if not isinstance(files, dict):
            raise CampaignError("VERIFIER_MANIFEST_FILES_INVALID")
        for relative, expected_hash in files.items():
            path = root / relative
            if not path.is_file() or file_sha256(path) != expected_hash:
                raise CampaignError("VERIFIER_MANIFEST_FILE_HASH_INVALID")
        receipt_paths = sorted((root / "receipts").glob("*.json"))
        if len(receipt_paths) != contract.VERIFIER_BATCH_SIZE:
            raise CampaignError("VERIFIER_BATCH_RECEIPT_COUNT_INVALID")
        for path in receipt_paths:
            receipt = json.loads(path.read_bytes())
            receipt_hash = receipt.get("receipt_hash")
            body = {key: value for key, value in receipt.items() if key != "receipt_hash"}
            if not isinstance(receipt_hash, str) or receipt_hash != digest(body):
                raise CampaignError("VERIFIER_RECEIPT_HASH_INVALID")
            file_hash = file_sha256(path)
            if receipt_hash in receipt_hashes or file_hash in receipt_file_hashes:
                raise CampaignError("VERIFIER_RECEIPT_NOT_UNIQUE")
            receipt_hashes.add(receipt_hash)
            receipt_file_hashes.add(file_hash)
            receipt_count += 1
        manifests.append(str(manifest_hash))
    if receipt_count != expected_receipts:
        raise CampaignError(
            f"VERIFIER_RECEIPT_TOTAL_INVALID:{receipt_count}:{expected_receipts}"
        )
    return {
        "lane": lane,
        "batch_count": len(roots),
        "receipt_count": receipt_count,
        "unique_receipt_hashes": len(receipt_hashes),
        "manifest_set_sha256": digest(manifests),
        "green": True,
    }


def validate_trace_progress_receipt(
    output: Path,
    *,
    campaign_id: str,
    now: float | None = None,
    destination_name: str = "preflight-trace-progress.json",
) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", destination_name):
        raise CampaignError("TRACE_PROGRESS_DESTINATION_INVALID")
    raw_path = os.environ.get("PDH3_TRACE_PROGRESS_RECEIPT")
    if not raw_path:
        raise CampaignError("TRACE_PROGRESS_RECEIPT_MISSING")
    source = Path(raw_path)
    if not source.is_absolute() or source.is_symlink():
        raise CampaignError("TRACE_PROGRESS_RECEIPT_INVALID_PATH")
    try:
        path = source.resolve(strict=True)
    except (FileNotFoundError, OSError) as exc:
        raise CampaignError("TRACE_PROGRESS_RECEIPT_INVALID_PATH") from exc
    if path != source or not path.is_file():
        raise CampaignError("TRACE_PROGRESS_RECEIPT_INVALID_PATH")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise CampaignError("TRACE_PROGRESS_RECEIPT_OPEN_FAILED") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat_module.S_ISREG(metadata.st_mode):
            raise CampaignError("TRACE_PROGRESS_RECEIPT_NOT_REGULAR")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, 65_536)
            if not chunk:
                break
            total += len(chunk)
            if total > 1 << 20:
                raise CampaignError("TRACE_PROGRESS_RECEIPT_TOO_LARGE")
            chunks.append(chunk)
        raw = b"".join(chunks)
    finally:
        os.close(descriptor)
    observed_now = time.time() if now is None else now
    age = observed_now - metadata.st_mtime
    if age < -2 or age > TRACE_PROGRESS_MAX_AGE_SECONDS:
        raise CampaignError(f"TRACE_PROGRESS_RECEIPT_STALE:{age:.3f}")
    record = json.loads(raw)
    receipt_hash = record.get("progress_receipt_sha256")
    body = {
        key: value for key, value in record.items()
        if key != "progress_receipt_sha256"
    }
    checks = {
        "version": record.get("version")
        == "ck-pdh3-process-tree-egress-observer-v2",
        "hash": isinstance(receipt_hash, str) and receipt_hash == digest(body),
        "non_authoritative": record.get("authoritative") is False,
        "in_progress": record.get("status") == "IN_PROGRESS",
        "one_trace_stream": record.get("trace_stream_count") == 1,
        "maximum_bytes": record.get("maximum_trace_bytes") == contract.TRACE_BYTES_LIMIT,
        "current_bytes": isinstance(record.get("trace_bytes"), int)
        and 0 <= record["trace_bytes"] <= contract.TRACE_BYTES_LIMIT,
        "projection": isinstance(
            record.get("projected_trace_bytes_24h_conservative"), int
        )
        and record["projected_trace_bytes_24h_conservative"]
        <= contract.TRACE_PREFLIGHT_PROJECTION_LIMIT,
        "cap_not_exceeded": record.get("projected_cap_exceeded") is False,
        "scan_progress": isinstance(record.get("scan_count"), int)
        and record["scan_count"] > 0,
        "packet_binding": (
            isinstance(os.environ.get("PDH3_PACKET_SHA256"), str)
            and record.get("packet_sha256")
            == os.environ.get("PDH3_PACKET_SHA256")
            == os.environ.get("PDH3_TRACE_PACKET_SHA256")
        ),
        "child_command_binding": (
            isinstance(os.environ.get("PDH3_TRACE_CHILD_COMMAND_SHA256"), str)
            and record.get("child_command_sha256")
            == os.environ.get("PDH3_TRACE_CHILD_COMMAND_SHA256")
        ),
        "campaign_binding": record.get("campaign_id") == campaign_id,
        "path_binding": record.get("progress_receipt_path") == str(path),
    }
    if not all(checks.values()):
        raise CampaignError("TRACE_PROGRESS_RECEIPT_NOT_GREEN:" + digest(checks))
    destination = output / destination_name
    atomic_write(destination, raw)
    return {
        "receipt_sha256": receipt_hash,
        "file_sha256": file_sha256(destination),
        "source_file_sha256": digest(raw),
        "destination": destination.name,
        "trace_bytes": record["trace_bytes"],
        "projected_trace_bytes_24h_conservative": (
            record["projected_trace_bytes_24h_conservative"]
        ),
        "age_seconds": round(age, 6),
        "checks": checks,
        "green": True,
    }


def production_schedule(args: argparse.Namespace) -> dict[str, Any]:
    expected = contract.expected_schedule()
    required_checkpoints = args.duration_seconds // args.checkpoint_seconds
    actual = {
        "checkpoints": required_checkpoints,
        "verifier_batches": min(contract.VERIFIER_BATCHES, required_checkpoints),
        "verifier_executions": min(
            contract.VERIFIER_BATCHES, required_checkpoints
        ) * contract.VERIFIER_BATCH_SIZE,
        "fault_epochs": [
            epoch + 1 for epoch in range(required_checkpoints)
            if (epoch + 1) % args.fault_every_checkpoints == 0
        ],
    }
    actual["fault_count"] = len(actual["fault_epochs"])
    if args.production and any(
        actual[key] != expected[key]
        for key in (
            "checkpoints", "verifier_batches", "verifier_executions",
            "fault_epochs", "fault_count",
        )
    ):
        raise CampaignError("PRODUCTION_SCHEDULE_MISMATCH:" + digest(actual))
    return actual


def enforce_resource_thresholds(
    resources: dict[str, Any],
    *,
    production: bool,
) -> None:
    nodes = resources["nodes"]
    live = sum(1 for row in nodes if row["alive"])
    if live != contract.REQUIRED_LIVE_NODE_PROCESSES:
        raise CampaignError(f"LIVE_NODE_PROCESS_COUNT_INVALID:{live}")
    if resources["database_bytes"] > contract.DATABASE_BYTES_LIMIT:
        raise CampaignError("DATABASE_GROWTH_LIMIT")
    if resources["evidence_bytes"] > contract.EVIDENCE_BYTES_LIMIT:
        raise CampaignError("EVIDENCE_GROWTH_LIMIT")
    if production:
        process_tree = resources.get("process_tree")
        if (
            not isinstance(process_tree, dict)
            or process_tree.get("available") is not True
            or process_tree.get("complete") is not True
            or process_tree.get("required_pids_present") is not True
            or not isinstance(process_tree.get("member_count"), int)
            or not isinstance(process_tree.get("member_pid_set_sha256"), str)
        ):
            raise CampaignError("PRODUCTION_PROCESS_TREE_SNAPSHOT_INCOMPLETE")
        if process_tree["member_count"] > contract.PROCESS_TREE_COUNT_LIMIT:
            raise CampaignError("PROCESS_TREE_COUNT_LIMIT")
        rss_values = [row["rss_kb"] for row in nodes]
        descriptor_values = [row["descriptors"] for row in nodes]
        if any(value is None for value in rss_values):
            raise CampaignError("PRODUCTION_RSS_METRICS_UNAVAILABLE")
        if any(value is None for value in descriptor_values):
            raise CampaignError("PRODUCTION_FD_METRICS_UNAVAILABLE")
        if sum(int(value) for value in rss_values) > contract.RSS_KB_LIMIT:
            raise CampaignError("RSS_GROWTH_LIMIT")
        if any(
            int(value) > contract.FILE_DESCRIPTORS_PER_NODE_LIMIT
            for value in descriptor_values
        ):
            raise CampaignError("FILE_DESCRIPTOR_LIMIT")


def run_campaign_epoch(
    *,
    canary: Any,
    binary: Path,
    nodes: list[Node],
    join: str,
    env: dict[str, str],
    root: Path,
    output: Path,
    query_files: dict[str, dict[str, Any]],
    campaign_id: str,
    expected_counts: tuple[int, ...],
    cache: str,
    sql_memory: str,
    lane: str,
    epoch: int,
    concurrency: int,
    boundary_ns: int,
    verifier_required: bool,
    fault_target: int | None,
    disk_used_fraction_limit: float,
    production: bool,
) -> dict[str, Any]:
    epoch_deadline = boundary_ns / 1_000_000_000
    work_deadline = epoch_deadline - EPOCH_FINAL_RESERVE_SECONDS
    if time.monotonic() >= work_deadline:
        raise CampaignError("EPOCH_WORK_DEADLINE_EXHAUSTED")
    gateway = nodes[0].sql_port
    epoch_root = root / f"{lane}-epoch-{epoch:04d}"
    epoch_root.mkdir()
    canary.MINIMUM_ACK_WRITE_OPERATIONS = max(2_000, concurrency * 10)
    canary.MINIMUM_CONTENDED_UPDATE_OPERATIONS = max(1_000, concurrency * 5)
    canary.MINIMUM_REPLAY_OPERATIONS = max(1_000, concurrency * 5)
    stage = canary.run_stage(
        binary,
        gateway,
        query_files,
        epoch_root,
        concurrency,
        env,
        deadline=work_deadline,
    )
    if not stage["green"]:
        raise CampaignError("CONCURRENCY_STAGE_BLOCKED:" + str(concurrency))
    cleanup = cleanup_probe(
        binary,
        gateway,
        env,
        campaign_id,
        epoch,
        deadline=work_deadline,
    )
    dependency = dependency_matrix(
        binary,
        gateway,
        env,
        campaign_id,
        epoch,
        deadline=work_deadline,
    )
    verifier = None
    if verifier_required:
        verifier = verifier_batch(
            canary,
            epoch_root / "verifier",
            env,
            f"{campaign_id}-{lane}-v{epoch:04d}",
            deadline=work_deadline,
        )
    fault = None
    if fault_target is not None:
        fault = fault_cycle(
            binary,
            nodes,
            fault_target,
            join,
            cache,
            sql_memory,
            env,
            campaign_id,
            deadline=work_deadline,
        )
        gateway = nodes[0].sql_port
        if not fault["green"]:
            raise CampaignError("FAULT_CYCLE_NOT_GREEN")
    counts = campaign_counts(
        binary, gateway, env, campaign_id, deadline=work_deadline
    )
    if counts != expected_counts:
        raise CampaignError("ACKNOWLEDGED_DATASET_DRIFT")
    controls = control_counts(binary, gateway, env, deadline=work_deadline)
    wrong_links = parse_last_integer(
        sql(
            binary,
            gateway,
            "SELECT count(*) FROM ck.context_vectors v "
            "JOIN ck.trajectory_events e ON e.event_hash=v.event_hash "
            "WHERE v.task_id != e.task_id",
            env=env,
            deadline=work_deadline,
            stage="epoch_vector_link_verification",
        )
    )
    if wrong_links:
        raise CampaignError("VECTOR_CROSS_TASK_CONTAMINATION")
    readiness = cluster_status(
        binary, nodes, env, deadline=work_deadline
    )
    raw_evidence = preserve_epoch_evidence(
        epoch_root,
        output,
        lane=lane,
        epoch=epoch,
        deadline=epoch_deadline,
    )
    remaining_ns = boundary_ns - time.monotonic_ns()
    if remaining_ns < 0:
        raise CampaignError("CHECKPOINT_INTERVAL_OVERRUN")
    time.sleep(remaining_ns / 1_000_000_000)
    snapshot_ns = time.monotonic_ns()
    drift_ns = abs(snapshot_ns - boundary_ns)
    if drift_ns > CHECKPOINT_DRIFT_SECONDS * 1_000_000_000:
        raise CampaignError(f"CHECKPOINT_SCHEDULE_DRIFT:{drift_ns}")
    resources = process_metrics(nodes, root, output)
    enforce_resource_thresholds(resources, production=production)
    trace_progress = (
        validate_trace_progress_receipt(
            output,
            campaign_id=campaign_id,
            destination_name=f"{lane}-trace-progress-{epoch:04d}.json",
        )
        if production
        else {"required": False, "green": True}
    )
    if resources["disk_used_fraction"] > disk_used_fraction_limit:
        raise CampaignError("DISK_USED_FRACTION_LIMIT")
    if (
        sum(1 for row in resources["nodes"] if row["alive"])
        != contract.REQUIRED_LIVE_NODE_PROCESSES
    ):
        raise CampaignError("CHECKPOINT_LIVE_NODE_COUNT_INVALID")
    body = {
        "version": "ck-pdh3-scale-checkpoint-v2",
        "lane": lane,
        "epoch": epoch,
        "concurrency": concurrency,
        "stage": stage,
        "cleanup_probe": cleanup,
        "dependency_matrix": dependency,
        "verifier": verifier,
        "fault": fault,
        "counts": list(counts),
        "control_counts": list(controls),
        "wrong_task_vector_links": wrong_links,
        "cluster_readiness_before_boundary": readiness,
        "resources_at_boundary": resources,
        "trace_progress_at_boundary": trace_progress,
        "boundary_monotonic_ns": boundary_ns,
        "snapshot_monotonic_ns": snapshot_ns,
        "boundary_drift_ns": drift_ns,
        "raw_evidence": raw_evidence,
    }
    return {**body, "checkpoint_sha256": digest(body)}


def run_remote_preflight(
    *,
    args: argparse.Namespace,
    canary: Any,
    binary: Path,
    nodes: list[Node],
    join: str,
    env: dict[str, str],
    root: Path,
    output: Path,
    query_files: dict[str, dict[str, Any]],
    expected_counts: tuple[int, ...],
) -> dict[str, Any]:
    if not args.production:
        return {"required": False, "green": True}
    started_ns = time.monotonic_ns()
    checkpoints: list[dict[str, Any]] = []
    for index in range(contract.REMOTE_PREFLIGHT_EPOCHS):
        boundary_ns = started_ns + (index + 1) * contract.CHECKPOINT_SECONDS * 1_000_000_000
        checkpoint = run_campaign_epoch(
            canary=canary,
            binary=binary,
            nodes=nodes,
            join=join,
            env=env,
            root=root,
            output=output,
            query_files=query_files,
            campaign_id=args.campaign_id,
            expected_counts=expected_counts,
            cache=args.cache,
            sql_memory=args.sql_memory,
            lane="preflight",
            epoch=index + 1,
            concurrency=contract.REMOTE_PREFLIGHT_CONCURRENCY,
            boundary_ns=boundary_ns,
            verifier_required=True,
            fault_target=index % 3,
            disk_used_fraction_limit=args.disk_used_fraction_limit,
            production=True,
        )
        atomic_write(
            output / f"preflight-checkpoint-{index + 1:04d}.json",
            canonical(checkpoint),
        )
        checkpoints.append(
            {
                "epoch": index + 1,
                "checkpoint_sha256": checkpoint["checkpoint_sha256"],
            }
        )
    verifier_evidence = validate_verifier_evidence(
        output,
        lane="preflight",
        expected_batches=contract.REMOTE_PREFLIGHT_EPOCHS,
        expected_receipts=(
            contract.REMOTE_PREFLIGHT_EPOCHS * contract.VERIFIER_BATCH_SIZE
        ),
    )
    trace = validate_trace_progress_receipt(
        output,
        campaign_id=args.campaign_id,
        destination_name="preflight-trace-progress-final.json",
    )
    reset_deadline = time.monotonic() + 120
    reset = reset_preflight_controls(
        binary,
        nodes[0].sql_port,
        env,
        args.campaign_id,
        deadline=reset_deadline,
    )
    counts_after_reset = campaign_counts(
        binary,
        nodes[0].sql_port,
        env,
        args.campaign_id,
        deadline=reset_deadline,
    )
    if counts_after_reset != expected_counts:
        raise CampaignError("PREFLIGHT_RESET_STATIC_DATASET_DRIFT")
    query_targets = canary.verify_query_targets(
        binary,
        nodes[0].sql_port,
        env,
        campaign_id=args.campaign_id,
        id_width=PRODUCTION_TASK_ID_WIDTH,
        deadline=reset_deadline,
    )
    body = {
        "version": "ck-pdh3-remote-preflight-v1",
        "epoch_count": len(checkpoints),
        "concurrency": contract.REMOTE_PREFLIGHT_CONCURRENCY,
        "fault_count": sum(
            1
            for index in range(1, contract.REMOTE_PREFLIGHT_EPOCHS + 1)
            if json.loads(
                (output / f"preflight-checkpoint-{index:04d}.json").read_bytes()
            )["fault"] is not None
        ),
        "checkpoints": checkpoints,
        "verifier_evidence": verifier_evidence,
        "trace_progress": trace,
        "control_reset": reset,
        "static_counts_after_reset": list(counts_after_reset),
        "query_targets_after_reset": query_targets,
        "green": True,
    }
    receipt = {**body, "preflight_sha256": digest(body)}
    atomic_write(output / "remote-preflight.json", canonical(receipt))
    return receipt


def result_manifest(output: Path) -> dict[str, Any]:
    files = {
        str(path.relative_to(output)): file_sha256(path)
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    }
    body = {
        "version": "ck-pdh3-scale-evidence-manifest-v1",
        "files": files,
        "file_count": len(files),
        "file_set_sha256": digest(files),
    }
    value = {**body, "manifest_sha256": digest(body)}
    atomic_write(output / "manifest.json", canonical(value))
    return value


def capture_node_diagnostics(
    nodes: list[Node], output: Path, *, tail_bytes: int = 65_536
) -> dict[str, Any]:
    """Preserve bounded node failure evidence before disposable stores are removed."""
    records: list[dict[str, Any]] = []
    for node in nodes:
        if node.log_handle is not None:
            try:
                node.log_handle.flush()
                os.fsync(node.log_handle.fileno())
            except (OSError, ValueError):
                pass
        process = node.process
        log_size = node.log.stat().st_size if node.log.is_file() else 0
        tail = b""
        if log_size:
            with node.log.open("rb") as handle:
                handle.seek(max(0, log_size - tail_bytes))
                tail = handle.read(tail_bytes)
        records.append(
            {
                "node": node.index + 1,
                "pid": process.pid if process is not None else None,
                "returncode": process.poll() if process is not None else None,
                "log_bytes": log_size,
                "log_sha256": file_sha256(node.log) if log_size else None,
                "log_tail_sha256": digest(tail) if tail else None,
                "log_tail": tail.decode("utf-8", "replace"),
            }
        )
    body = {
        "version": "ck-pdh3-node-diagnostics-v1",
        "nodes": records,
        "tail_byte_limit": tail_bytes,
    }
    receipt = {**body, "diagnostics_sha256": digest(body)}
    atomic_write(output / "node-diagnostics.json", canonical(receipt))
    return receipt


def close_local_campaign(
    nodes: list[Node],
    root: Path,
    campaign_id: str,
    teardown: dict[str, Any],
    *,
    require_database_drop: bool,
) -> dict[str, Any]:
    stop_codes = [stop_node(node, crash=False) for node in nodes]
    teardown["nodes_stopped"] = all(node.process is None for node in nodes)
    partial_start = teardown.get("partial_start")
    if not nodes and isinstance(partial_start, dict) and partial_start.get(
        "partial_teardown_required"
    ):
        teardown["nodes_stopped"] = bool(
            partial_start.get("partial_teardown_proved")
        )
        stop_codes = list(partial_start.get("stop_returncodes", []))
    if require_database_drop and len(nodes) != 3:
        teardown["nodes_stopped"] = False
    open_ports: list[int] = []
    for node in nodes:
        for port in (node.sql_port, node.http_port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                probe.settimeout(0.2)
                if probe.connect_ex(("127.0.0.1", port)) == 0:
                    open_ports.append(port)
    if not nodes and isinstance(partial_start, dict):
        open_ports.extend(partial_start.get("open_ports_after_failure", []))
    teardown["ports_closed"] = not open_ports
    verified = root.resolve()
    if verified.parent not in (Path("/tmp"), Path("/private/tmp")):
        raise CampaignError("GENERATED_ROOT_PARENT_INVALID")
    if not verified.name.startswith(campaign_id + "."):
        raise CampaignError("GENERATED_ROOT_IDENTITY_INVALID")
    if verified.exists():
        shutil.rmtree(verified)
    teardown["generated_root_removed"] = not verified.exists()
    body = {
        "version": "ck-pdh3-scale-teardown-v2",
        "campaign_id": campaign_id,
        **teardown,
        "node_stop_returncodes": stop_codes,
        "open_ports": open_ports,
    }
    required_keys = ["nodes_stopped", "ports_closed", "generated_root_removed"]
    if require_database_drop:
        required_keys.append("database_dropped")
    body["green"] = all(bool(body[key]) for key in required_keys)
    if not body["green"]:
        raise CampaignError("LOCAL_TEARDOWN_NOT_GREEN:" + digest(body))
    return {**body, "receipt_sha256": digest(body)}


def commit_success_evidence(
    output: Path,
    result_body: dict[str, Any],
    teardown_receipt: dict[str, Any],
) -> dict[str, Any]:
    """Commit terminal GREEN only after a hash-valid, fully green teardown."""
    if not teardown_receipt.get("green"):
        raise CampaignError("PREMATURE_GREEN_TEARDOWN_NOT_GREEN")
    receipt_hash = teardown_receipt.get("receipt_sha256")
    teardown_body = {
        key: value for key, value in teardown_receipt.items()
        if key != "receipt_sha256"
    }
    if not isinstance(receipt_hash, str) or receipt_hash != digest(teardown_body):
        raise CampaignError("PREMATURE_GREEN_TEARDOWN_HASH_INVALID")
    if (output / "failure.json").exists():
        raise CampaignError("FAILURE_RESULT_MUTUAL_EXCLUSION_BREACH")
    if (output / "result.json").exists() or (
        output / "MEASURED_CAMPAIGN_GREEN"
    ).exists():
        raise CampaignError("SUCCESS_EVIDENCE_ALREADY_EXISTS")
    result = {**result_body, "result_sha256": digest(result_body)}
    atomic_write(output / "result.json", canonical(result))
    marker_body = {
        "version": "ck-pdh3-measured-campaign-green-v1",
        "campaign_id": result_body["campaign_id"],
        "result_sha256": result["result_sha256"],
        "teardown_receipt_sha256": receipt_hash,
    }
    atomic_write(
        output / "MEASURED_CAMPAIGN_GREEN",
        canonical({**marker_body, "marker_sha256": digest(marker_body)}),
    )
    return result


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if not args.campaign_id.startswith("ck-pdh3-scale-"):
        raise CampaignError("CAMPAIGN_ID_INVALID")
    if args.production and args.store_size is not None:
        raise CampaignError("PRODUCTION_STORE_SIZE_FORBIDDEN")
    binary = args.binary.resolve()
    packet = args.packet.resolve()
    output = args.output.resolve()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise CampaignError("COCKROACH_BINARY_INVALID")
    if not packet.is_file():
        raise CampaignError("PACKET_MISSING")
    if output.exists():
        raise CampaignError("OUTPUT_ALREADY_EXISTS")
    output.mkdir(parents=True)
    packet_hash = file_sha256(packet)
    if os.environ.get("PDH3_PACKET_SHA256") != packet_hash:
        raise CampaignError("PACKET_HASH_BINDING_INVALID")
    if args.production:
        contract.validate_production_arguments(vars(args))
    schedule = production_schedule(args)
    root_parent = Path("/tmp" if sys.platform.startswith("linux") else "/private/tmp")
    root = Path(tempfile.mkdtemp(prefix=args.campaign_id + ".", dir=root_parent))
    fake_home = root / "empty-home"
    fake_home.mkdir()
    env = scrubbed_env(fake_home)
    journal = ChainLog(output / "journal.ndjson", args.campaign_id)
    canary = load_canary_module()
    configure_canary_module(canary, args)
    nodes: list[Node] = []
    join = ""
    result: dict[str, Any] | None = None
    success_committed = False
    teardown_written = False
    teardown: dict[str, Any] = {
        "nodes_stopped": False,
        "ports_closed": False,
        "generated_root_removed": False,
        "database_dropped": False,
    }
    startup_evidence: dict[str, Any] = {}
    try:
        journal.emit(
            "CAMPAIGN_START",
            {
                "production": args.production,
                "packet_sha256": packet_hash,
                "contract_sha256": contract.production_contract()["contract_sha256"],
                "binary_sha256": file_sha256(binary),
                "network": "LOOPBACK_CLUSTER_ONLY",
                "credential_material": False,
            },
        )
        nodes, join = start_cluster(
            binary,
            root,
            env,
            args.cache,
            args.sql_memory,
            args.store_size,
            startup_evidence=startup_evidence,
        )
        startup_body = {
            **startup_evidence,
            "green": bool(startup_evidence.get("cluster_ready")),
        }
        atomic_write(
            output / "startup.json",
            canonical({**startup_body, "startup_sha256": digest(startup_body)}),
        )
        gateway = nodes[0].sql_port
        apply_migrations(binary, gateway, env)
        setup_deadline = time.monotonic() + args.setup_timeout_seconds
        setup_started_ns = time.monotonic_ns()
        tail_reserve_seconds = setup_tail_reserve(args.setup_timeout_seconds)
        required_setup_margin_seconds = setup_margin_gate(
            args.setup_timeout_seconds,
            0.0,
            production=args.production,
        )["required_setup_margin_seconds"]
        finalization_reserve_seconds = (
            required_setup_margin_seconds
            + SETUP_RECEIPT_FINALIZATION_RESERVE_SECONDS
        )
        index_verification_reserve_seconds = max(
            finalization_reserve_seconds,
            tail_reserve_seconds // 4,
        )
        preseed_index = prove_preseed_vector_index(
            binary,
            gateway,
            env,
            setup_deadline,
            tail_reserve_seconds,
        )
        if not preseed_index["green"]:
            raise CampaignError("PRESEED_VECTOR_INDEX_NOT_GREEN")
        journal.emit(
            "VECTOR_INDEX_PRESEED_PROVED",
            {
                "index": "context_vectors_vector_idx",
                "proof": preseed_index,
            },
        )
        seed = seed_dataset(
            binary,
            gateway,
            env,
            journal,
            campaign_id=args.campaign_id,
            tasks=args.tasks,
            events_per_task=args.events_per_task,
            receipts_per_task=args.receipts_per_task,
            vectors=args.vectors,
            batch_tasks=args.seed_batch_tasks,
            setup_deadline=setup_deadline,
            tail_reserve_seconds=tail_reserve_seconds,
        )
        seeded_index = prove_seeded_vector_index(
            binary,
            gateway,
            env,
            setup_deadline,
            args.vectors,
            index_verification_reserve_seconds,
        )
        journal.emit(
            "VECTOR_INDEX_POSTSEED_PROVED",
            {
                "index": "context_vectors_vector_idx",
                "proof": seeded_index,
            },
        )
        recovered_cluster = cluster_status(
            binary,
            nodes,
            env,
            deadline=setup_deadline,
        )
        journal.emit(
            "POST_INDEX_CLUSTER_READY",
            {
                "gateway_port": gateway,
                "cluster": recovered_cluster,
            },
        )
        expected_counts = (
            args.tasks,
            args.tasks * args.events_per_task,
            args.tasks * args.receipts_per_task,
            args.vectors,
        )
        actual_counts = campaign_counts(
            binary,
            gateway,
            env,
            args.campaign_id,
            setup_deadline,
            reserve_seconds=finalization_reserve_seconds,
        )
        reconciliations = campaign_reconciliations(
            binary,
            gateway,
            env,
            campaign_id=args.campaign_id,
            tasks=args.tasks,
            events_per_task=args.events_per_task,
            receipts_per_task=args.receipts_per_task,
            vectors=args.vectors,
            setup_deadline=setup_deadline,
            reserve_seconds=finalization_reserve_seconds,
        )
        mismatch_counts = {
            stage: result["mismatch_rows"]
            for stage, result in reconciliations.items()
        }
        wrong_links = parse_last_integer(
            sql(
                binary,
                gateway,
                "SELECT count(*) FROM ck.context_vectors v "
                "JOIN ck.trajectory_events e ON e.event_hash=v.event_hash "
                f"WHERE v.namespace={q(args.campaign_id)} "
                "AND v.task_id != e.task_id",
                env=env,
                timeout=setup_timeout(
                    setup_deadline,
                    SETUP_SQL_TIMEOUT_SECONDS,
                    reserve_seconds=finalization_reserve_seconds,
                ),
                stage="vector_link_verification",
            )
        )
        query_files = create_query_files(canary, root, args.campaign_id)
        query_targets = canary.verify_query_targets(
            binary,
            gateway,
            env,
            campaign_id=args.campaign_id,
            id_width=PRODUCTION_TASK_ID_WIDTH,
            deadline=setup_deadline - finalization_reserve_seconds,
        )
        ensure_setup_deadline(setup_deadline)
        setup_elapsed_seconds = (
            time.monotonic_ns() - setup_started_ns
        ) / 1_000_000_000
        deadline_met = time.monotonic() <= setup_deadline
        setup_margin = setup_margin_gate(
            args.setup_timeout_seconds,
            setup_elapsed_seconds,
            production=args.production,
        )
        pre_fsync_required_margin_seconds = (
            required_setup_margin_seconds
            + SETUP_RECEIPT_FINALIZATION_RESERVE_SECONDS
        )
        pre_fsync_margin_met = (
            setup_margin["setup_margin_seconds"]
            >= pre_fsync_required_margin_seconds
        )
        setup_green = (
            actual_counts == expected_counts
            and all(value == 0 for value in mismatch_counts.values())
            and all(
                result["state"] == "EXACT"
                for result in reconciliations.values()
            )
            and wrong_links == 0
            and preseed_index["green"]
            and seeded_index["green"]
            and query_targets["green"]
            and deadline_met
            and setup_margin["setup_margin_met"]
            and pre_fsync_margin_met
        )
        setup_body = {
            "version": "ck-pdh3-scale-setup-v4",
            "campaign_id": args.campaign_id,
            "seed": seed,
            "expected_counts": list(expected_counts),
            "actual_counts": list(actual_counts),
            "dataset_counts": list(actual_counts),
            "reconciliations": reconciliations,
            "mismatch_counts": mismatch_counts,
            "wrong_task_vector_links": wrong_links,
            "vector_index_preseed": preseed_index,
            "vector_index_postseed": seeded_index,
            "query_targets": query_targets,
            "setup_elapsed_seconds": setup_elapsed_seconds,
            "setup_deadline_seconds": args.setup_timeout_seconds,
            **setup_margin,
            "setup_receipt_finalization_reserve_seconds": (
                SETUP_RECEIPT_FINALIZATION_RESERVE_SECONDS
            ),
            "pre_fsync_required_margin_seconds": (
                pre_fsync_required_margin_seconds
            ),
            "pre_fsync_margin_met": pre_fsync_margin_met,
            "setup_tail_reserve_seconds": tail_reserve_seconds,
            "deadline_met": deadline_met,
            "green": setup_green,
        }
        setup_receipt = {
            **setup_body,
            "setup_sha256": digest(setup_body),
        }
        atomic_write(output / "setup.json", canonical(setup_receipt))
        if not setup_green:
            journal.emit(
                "FULL_CARDINALITY_SETUP_BLOCKED",
                {"setup_sha256": setup_receipt["setup_sha256"]},
            )
            raise CampaignError("FULL_CARDINALITY_SETUP_NOT_GREEN")
        post_setup_fsync_elapsed_seconds = (
            time.monotonic_ns() - setup_started_ns
        ) / 1_000_000_000
        post_setup_fsync_margin = setup_margin_gate(
            args.setup_timeout_seconds,
            post_setup_fsync_elapsed_seconds,
            production=args.production,
        )
        finalization_body = {
            "version": "ck-pdh3-setup-finalization-v1",
            "campaign_id": args.campaign_id,
            "setup_sha256": setup_receipt["setup_sha256"],
            "post_setup_fsync_elapsed_seconds": (
                post_setup_fsync_elapsed_seconds
            ),
            **post_setup_fsync_margin,
            "green": post_setup_fsync_margin["setup_margin_met"],
        }
        finalization_receipt = {
            **finalization_body,
            "finalization_sha256": digest(finalization_body),
        }
        atomic_write(
            output / "setup-finalization.json",
            canonical(finalization_receipt),
        )
        post_finalization_elapsed_seconds = (
            time.monotonic_ns() - setup_started_ns
        ) / 1_000_000_000
        post_finalization_margin = setup_margin_gate(
            args.setup_timeout_seconds,
            post_finalization_elapsed_seconds,
            production=args.production,
        )
        if not (
            post_setup_fsync_margin["setup_margin_met"]
            and post_finalization_margin["setup_margin_met"]
        ):
            blocked_body = {
                **setup_body,
                "setup_elapsed_seconds": post_finalization_elapsed_seconds,
                "setup_margin_seconds": post_finalization_margin[
                    "setup_margin_seconds"
                ],
                "setup_margin_met": False,
                "deadline_met": time.monotonic() <= setup_deadline,
                "green": False,
                "post_receipt_margin_breach": True,
            }
            blocked_receipt = {
                **blocked_body,
                "setup_sha256": digest(blocked_body),
            }
            atomic_write(output / "setup.json", canonical(blocked_receipt))
            journal.emit(
                "FULL_CARDINALITY_SETUP_BLOCKED",
                {
                    "setup_sha256": blocked_receipt["setup_sha256"],
                    "reason": "SETUP_SUCCESS_MARGIN_EXHAUSTED",
                },
            )
            raise CampaignError("SETUP_SUCCESS_MARGIN_EXHAUSTED")
        journal.emit(
            "FULL_CARDINALITY_SETUP_GREEN",
            {
                "setup_sha256": setup_receipt["setup_sha256"],
                "finalization_sha256": finalization_receipt[
                    "finalization_sha256"
                ],
                "post_finalization_margin_seconds": (
                    post_finalization_margin["setup_margin_seconds"]
                ),
            },
        )
        remote_preflight = run_remote_preflight(
            args=args,
            canary=canary,
            binary=binary,
            nodes=nodes,
            join=join,
            env=env,
            root=root,
            output=output,
            query_files=query_files,
            expected_counts=expected_counts,
        )
        journal.emit(
            "REMOTE_PREFLIGHT_GREEN",
            {
                "required": remote_preflight.get("required", True),
                "preflight_sha256": remote_preflight.get("preflight_sha256"),
            },
        )
        measured_start_ns = time.monotonic_ns()
        measured_start_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        checkpoints: list[dict[str, Any]] = []
        total_verifier = 0
        total_operations = 0
        max_p99 = 0.0
        max_pmax = 0.0
        fault_count = 0
        expected_acknowledged_writes = 0
        expected_counter_value = 0
        required_checkpoints = int(schedule["checkpoints"])
        for epoch in range(required_checkpoints):
            concurrency = min(
                args.max_concurrency,
                contract.CONCURRENCY_STAGES[
                    min(epoch, len(contract.CONCURRENCY_STAGES) - 1)
                ],
            )
            boundary_ns = (
                measured_start_ns
                + (epoch + 1) * args.checkpoint_seconds * 1_000_000_000
            )
            verifier_required = epoch < int(schedule["verifier_batches"])
            fault_target = (
                fault_count % 3
                if (epoch + 1) in schedule["fault_epochs"]
                else None
            )
            checkpoint = run_campaign_epoch(
                canary=canary,
                binary=binary,
                nodes=nodes,
                join=join,
                env=env,
                root=root,
                output=output,
                query_files=query_files,
                campaign_id=args.campaign_id,
                expected_counts=expected_counts,
                cache=args.cache,
                sql_memory=args.sql_memory,
                lane="measured",
                epoch=epoch + 1,
                concurrency=concurrency,
                boundary_ns=boundary_ns,
                verifier_required=verifier_required,
                fault_target=fault_target,
                disk_used_fraction_limit=args.disk_used_fraction_limit,
                production=args.production,
            )
            stage = checkpoint["stage"]
            verifier = checkpoint["verifier"]
            fault = checkpoint["fault"]
            if verifier is not None:
                total_verifier += verifier["measured_executions"]
            if fault is not None:
                fault_count += 1
            expected_acknowledged_writes += stage["acknowledged_write_delta"]
            expected_counter_value += stage["contended_update_delta"]
            total_operations += stage["total_operations"]
            max_p99 = max(max_p99, stage["maximum_latency_ms"]["p99"])
            max_pmax = max(max_pmax, stage["maximum_latency_ms"]["max"])
            atomic_write(
                output / f"checkpoint-{epoch + 1:04d}.json",
                canonical(checkpoint),
            )
            checkpoints.append(
                {
                    "epoch": epoch + 1,
                    "checkpoint_sha256": checkpoint["checkpoint_sha256"],
                }
            )
            journal.emit(
                "CHECKPOINT",
                {
                    "epoch": epoch + 1,
                    "checkpoint_sha256": checkpoint["checkpoint_sha256"],
                    "concurrency": concurrency,
                    "total_operations": total_operations,
                    "total_verifier": total_verifier,
                },
            )
        measured_end_ns = (
            int(checkpoint["snapshot_monotonic_ns"])
            if required_checkpoints > 0
            else time.monotonic_ns()
        )
        measured_seconds = (measured_end_ns - measured_start_ns) / 1_000_000_000
        if args.production and not (args.duration_seconds <= measured_seconds <= args.duration_seconds + 2):
            raise CampaignError("MEASURED_DURATION_INVALID")
        if args.production and total_verifier != contract.VERIFIER_EXECUTIONS:
            raise CampaignError("VERIFIER_EXECUTION_TOTAL_INVALID")
        verifier_evidence = validate_verifier_evidence(
            output,
            lane="measured",
            expected_batches=int(schedule["verifier_batches"]),
            expected_receipts=total_verifier,
        )
        if max_p99 > contract.P99_LIMIT_MS or max_pmax > contract.PMAX_LIMIT_MS:
            raise CampaignError("LATENCY_THRESHOLD_BREACH")
        final_counts = campaign_counts(binary, gateway, env, args.campaign_id)
        final_controls = control_counts(
            binary,
            gateway,
            env,
            deadline=time.monotonic() + 120,
        )
        expected_final_controls = (
            expected_acknowledged_writes,
            expected_counter_value,
            1 if required_checkpoints else 0,
        )
        if final_controls != expected_final_controls:
            raise CampaignError(
                "FINAL_CONTROL_COUNT_MISMATCH:"
                + digest(
                    {
                        "actual": final_controls,
                        "expected": expected_final_controls,
                    }
                )
            )
        final_wrong_links = parse_last_integer(
            sql(
                binary,
                gateway,
                "SELECT count(*) FROM ck.context_vectors v "
                "JOIN ck.trajectory_events e ON e.event_hash=v.event_hash "
                "WHERE v.task_id != e.task_id",
                env=env,
                deadline=time.monotonic() + 120,
                stage="final_vector_link_verification",
            )
        )
        mode_metadata = result_mode_metadata(args.production)
        result_body = {
            "version": mode_metadata["version"],
            "status": "GREEN",
            "production_mode": args.production,
            "product_candidate": contract.PRODUCT_CANDIDATE,
            "plan_sha256": contract.PLAN_SHA256,
            "packet_sha256": packet_hash,
            "contract_sha256": contract.production_contract()["contract_sha256"],
            "campaign_id": args.campaign_id,
            "synthetic_only": True,
            "credentials_used": False,
            "external_cloud_calls": 0,
            "cluster_topology": mode_metadata["cluster_topology"],
            "measured_start_utc": measured_start_utc,
            "measured_end_utc": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            ),
            "measured_seconds": measured_seconds,
            "seed": seed,
            "remote_preflight": {
                "required": remote_preflight.get("required", True),
                "preflight_sha256": remote_preflight.get("preflight_sha256"),
            },
            "dataset_counts": list(final_counts),
            "control_counts": list(final_controls),
            "expected_control_counts": list(expected_final_controls),
            "wrong_task_vector_links": final_wrong_links,
            "checkpoints": checkpoints,
            "checkpoint_count": len(checkpoints),
            "total_measured_operations": total_operations,
            "verifier_executions": total_verifier,
            "verifier_evidence": verifier_evidence,
            "fault_cycles": fault_count,
            "maximum_p99_ms": max_p99,
            "maximum_latency_ms": max_pmax,
            "journal_terminal_hash_before_result": journal.previous,
            "limitations": mode_metadata["limitations"],
        }
        required = {
            "checkpoint_count": (
                contract.REQUIRED_CHECKPOINTS if args.production else required_checkpoints
            ),
            "verifier_executions": (
                contract.VERIFIER_EXECUTIONS if args.production else total_verifier
            ),
        }
        result_body["green_checks"] = {
            "checkpoint_count": len(checkpoints) == required["checkpoint_count"],
            "verifier_execution_count": total_verifier == required["verifier_executions"],
            "dataset_counts": final_counts == expected_counts,
            "control_counts": final_controls == expected_final_controls,
            "cross_task_vector_links": final_wrong_links == 0,
            "false_promotions": all(
                (
                    json.loads(
                        (output / f"checkpoint-{index:04d}.json").read_bytes()
                    ).get("verifier") or {}
                ).get("false_promotions", 0)
                == 0
                for index in range(1, len(checkpoints) + 1)
            ),
            "latency": (
                max_p99 <= contract.P99_LIMIT_MS
                and max_pmax <= contract.PMAX_LIMIT_MS
            ),
            "fault_cycles": fault_count == int(schedule["fault_count"]),
        }
        if not all(result_body["green_checks"].values()):
            raise CampaignError("FINAL_GREEN_CHECK_FAILED")
        sql(
            binary,
            gateway,
            "DROP DATABASE cockroach_kernel CASCADE",
            env=env,
            database=None,
            timeout=1800,
        )
        remaining = parse_last_integer(
            sql(
                binary,
                gateway,
                "SELECT count(*) FROM [SHOW DATABASES] "
                "WHERE database_name='cockroach_kernel'",
                env=env,
                database=None,
            )
        )
        if remaining != 0:
            raise CampaignError("DATABASE_DROP_RESIDUE")
        teardown["database_dropped"] = True
        teardown_receipt = close_local_campaign(
            nodes,
            root,
            args.campaign_id,
            teardown,
            require_database_drop=True,
        )
        atomic_write(output / "teardown.json", canonical(teardown_receipt))
        teardown_written = True
        journal.emit(
            "LOCAL_TEARDOWN_GREEN",
            {"receipt_sha256": teardown_receipt["receipt_sha256"]},
        )
        result_body["local_teardown"] = {
            "receipt_sha256": teardown_receipt["receipt_sha256"],
            "green": teardown_receipt["green"],
        }
        precommit_manifest = result_manifest(output)
        result_body["precommit_manifest_sha256"] = precommit_manifest[
            "manifest_sha256"
        ]
        result = commit_success_evidence(output, result_body, teardown_receipt)
        success_committed = True
        return result
    except BaseException as exc:
        for path in (output / "result.json", output / "MEASURED_CAMPAIGN_GREEN"):
            if path.exists():
                path.unlink()
        node_diagnostics = capture_node_diagnostics(nodes, output)
        failure_body = {
            "version": "ck-pdh3-scale-failure-v1",
            "campaign_id": args.campaign_id,
            "exception_type": type(exc).__name__,
            "reason": str(exc),
            "journal_prior_hash": journal.previous,
            "startup_evidence": startup_evidence,
            "node_diagnostics_sha256": node_diagnostics["diagnostics_sha256"],
        }
        if startup_evidence.get("partial_teardown_required"):
            teardown["partial_start"] = startup_evidence
        if startup_evidence and not (output / "startup.json").exists():
            startup_body = {
                **startup_evidence,
                "green": bool(startup_evidence.get("cluster_ready")),
            }
            atomic_write(
                output / "startup.json",
                canonical(
                    {**startup_body, "startup_sha256": digest(startup_body)}
                ),
            )
        atomic_write(
            output / "failure.json",
            canonical({**failure_body, "failure_sha256": digest(failure_body)}),
        )
        journal.emit(
            "CAMPAIGN_BLOCKED",
            {"type": type(exc).__name__, "reason": str(exc)},
        )
        raise
    finally:
        if not success_committed:
            teardown_receipt = close_local_campaign(
                nodes,
                root,
                args.campaign_id,
                teardown,
                require_database_drop=False,
            )
            if not teardown_written:
                atomic_write(output / "teardown.json", canonical(teardown_receipt))
            journal.emit("LOCAL_TEARDOWN", teardown)
            if (output / "result.json").exists() or (
                output / "MEASURED_CAMPAIGN_GREEN"
            ).exists():
                raise CampaignError("FAILURE_RESULT_MUTUAL_EXCLUSION_BREACH")
            result_manifest(output)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--binary", type=Path, required=True)
    value.add_argument("--packet", type=Path, required=True)
    value.add_argument("--output", type=Path, required=True)
    value.add_argument("--campaign-id", required=True)
    value.add_argument("--production", action="store_true")
    value.add_argument("--duration-seconds", type=int, default=60)
    value.add_argument("--checkpoint-seconds", type=int, default=60)
    value.add_argument("--tasks", type=int, default=100)
    value.add_argument("--events-per-task", type=int, default=3)
    value.add_argument("--receipts-per-task", type=int, default=1)
    value.add_argument("--vectors", type=int, default=50)
    value.add_argument("--max-concurrency", type=int, default=10)
    value.add_argument("--query-duration-seconds", type=int, default=2)
    value.add_argument("--seed-batch-tasks", type=int, default=100)
    value.add_argument("--setup-timeout-seconds", type=int, default=600)
    value.add_argument("--fault-every-checkpoints", type=int, default=1)
    value.add_argument("--disk-used-fraction-limit", type=float, default=0.999)
    value.add_argument("--cache", default="128MiB")
    value.add_argument("--sql-memory", default="128MiB")
    value.add_argument("--store-size")
    return value


def main() -> int:
    args = parser().parse_args()
    if args.duration_seconds < 1 or args.checkpoint_seconds < 1:
        raise CampaignError("DURATION_INVALID")
    if args.duration_seconds % args.checkpoint_seconds:
        raise CampaignError("CHECKPOINT_DIVISIBILITY_INVALID")
    if not 0.1 <= args.disk_used_fraction_limit <= 0.999:
        raise CampaignError("DISK_FRACTION_LIMIT_INVALID")
    if not 1 <= args.receipts_per_task <= args.events_per_task:
        raise CampaignError("RECEIPT_COUNT_INVALID")
    execute(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
