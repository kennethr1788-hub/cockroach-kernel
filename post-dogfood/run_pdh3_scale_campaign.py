#!/usr/bin/env python3
"""Credential-free three-node PDH-3 production-shaped scale campaign.

The production mode is hash-bound to the frozen packet and exact 24-hour
contract. A reduced smoke mode exercises the same cluster, query, verifier,
fault, evidence, cleanup, and teardown paths without making scale claims.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from typing import Any

import pdh3_scale_contract as contract


BASE = Path(__file__).resolve().parents[1]
ZERO_HASH = "0" * 64


class CampaignError(RuntimeError):
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
    if completed.returncode != 0:
        bounded_tail = completed.stdout[-2_000:].decode("utf-8", "replace")
        raise CampaignError(
            "COMMAND_FAILED:"
            + Path(command[0]).name
            + ":"
            + digest(completed.stdout)
            + ":"
            + bounded_tail
        )
    return completed


def sql(
    binary: Path,
    port: int,
    statement: str,
    *,
    env: dict[str, str],
    database: str | None = "cockroach_kernel",
    timeout: int = 300,
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
    return run(command, env=env, timeout=timeout).stdout


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
    ) -> None:
        self.index = index
        self.sql_port = sql_port
        self.http_port = http_port
        self.store = store
        self.log = log
        self.process: subprocess.Popen[bytes] | None = None
        self.log_handle: Any | None = None


def node_command(
    binary: Path,
    node: Node,
    join: str,
    cache: str,
    sql_memory: str,
) -> list[str]:
    return [
        str(binary),
        "start",
        "--insecure",
        f"--store={node.store}",
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
    node.process = subprocess.Popen(
        node_command(binary, node, join, cache, sql_memory),
        env=env,
        cwd=node.store.parent,
        stdin=subprocess.DEVNULL,
        stdout=node.log_handle,
        stderr=subprocess.STDOUT,
    )


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
        )
        for index in range(3)
    ]
    join = ",".join(f"127.0.0.1:{node.sql_port}" for node in nodes)
    for node in nodes:
        node.store.parent.mkdir(parents=True)
        start_node(binary, node, join, cache, sql_memory, env, append=False)
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
            if parse_last_integer(
                sql(
                    binary,
                    nodes[0].sql_port,
                    "SELECT 1",
                    env=env,
                    database=None,
                    timeout=10,
                )
            ) == 1:
                return nodes, join
        except (CampaignError, subprocess.TimeoutExpired):
            time.sleep(1)
    raise CampaignError("THREE_NODE_CLUSTER_READINESS_TIMEOUT")


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
            f"FROM generate_series({start},{stop - 1}) AS g(i)",
        ),
        (
            "events",
            "INSERT INTO ck.trajectory_events"
            "(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash) "
            f"SELECT {event_expression},{task_expression},s,{parent_hash},"
            f"decode(sha256(({campaign} || '-state-hash-' || i::STRING)::BYTES),'hex'),"
            "jsonb_build_object('synthetic',true,'sequence',s),"
            f"{event_hash} FROM generate_series({start},{stop - 1}) AS g(i),"
            f"generate_series(0,{events_per_task - 1}) AS e(s)",
        ),
        (
            "receipts",
            "INSERT INTO ck.receipts"
            "(receipt_hash,task_id,event_hash,status,receipt_json) "
            f"SELECT decode(sha256(({campaign} || '-receipt-' || i::STRING || '-' || "
            f"s::STRING)::BYTES),'hex'),{task_expression},{event_hash},'SEALED',"
            "jsonb_build_object('synthetic',true,'receipt',s) "
            f"FROM generate_series({start},{stop - 1}) AS g(i),"
            f"generate_series(0,{receipts_per_task - 1}) AS e(s)",
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
                f"FROM generate_series({start},{limited_stop - 1}) AS g(i)",
            )
        )
    return statements


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
) -> dict[str, Any]:
    counts = {"tasks": 0, "events": 0, "receipts": 0, "vectors": 0}
    retries = 0
    statement_hashes: list[str] = []
    for start in range(0, tasks, batch_tasks):
        if time.monotonic() >= setup_deadline:
            raise CampaignError("SETUP_DEADLINE_EXCEEDED")
        stop = min(tasks, start + batch_tasks)
        for stage, statement in seed_batch_statements(
            campaign_id,
            start,
            stop,
            events_per_task,
            receipts_per_task,
            vectors,
        ):
            raw_hash = digest(statement.encode("utf-8"))
            for attempt in range(4):
                try:
                    sql(binary, port, statement, env=env, timeout=900)
                    break
                except CampaignError:
                    if attempt == 3:
                        raise
                    retries += 1
                    time.sleep(0.25 * (attempt + 1))
            rows = stop - start
            if stage == "events":
                rows *= events_per_task
            elif stage == "receipts":
                rows *= receipts_per_task
            elif stage == "vectors":
                rows = max(0, min(stop, vectors) - start)
            counts[stage] += rows
            statement_hashes.append(raw_hash)
        journal.emit(
            "SEED_BATCH",
            {
                "start": start,
                "stop": stop,
                "counts": dict(counts),
                "statement_set_sha256": digest(statement_hashes),
            },
        )
    return {
        "counts": counts,
        "statement_set_sha256": digest(statement_hashes),
        "retries": retries,
    }


def campaign_counts(binary: Path, port: int, env: dict[str, str], campaign: str) -> tuple[int, ...]:
    prefix = campaign + "-task-%"
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
        ),
        4,
    )


def dependency_matrix(
    binary: Path,
    port: int,
    env: dict[str, str],
    campaign: str,
    epoch: int,
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
        )
    count = parse_last_integer(
        sql(
            binary,
            port,
            f"SELECT count(*) FROM ck.worker_results WHERE request_id LIKE "
            f"{q(campaign + '-advice-' + format(epoch, '04d') + '-%')}",
            env=env,
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
    )
    residue = parse_last_integer(
        sql(
            binary,
            port,
            f"SELECT count(*) FROM ck.tasks WHERE task_id={q(task_id)}",
            env=env,
        )
    )
    if residue != 0:
        raise CampaignError("CLEANUP_PROBE_RESIDUE")
    return {"task_id_hash": digest(task_id.encode()), "residue": residue}


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
    return {
        "nodes": values,
        "database_bytes": sum(tree_bytes(node.store) for node in nodes),
        "evidence_bytes": tree_bytes(output),
        "disk_total_bytes": usage.total,
        "disk_used_bytes": usage.used,
        "disk_used_fraction": usage.used / usage.total,
    }


def fault_cycle(
    binary: Path,
    nodes: list[Node],
    node_index: int,
    join: str,
    cache: str,
    sql_memory: str,
    env: dict[str, str],
    campaign: str,
) -> dict[str, Any]:
    target = nodes[node_index]
    surviving = nodes[(node_index + 1) % len(nodes)]
    before = campaign_counts(binary, surviving.sql_port, env, campaign)
    returncode = stop_node(target, crash=True)
    during = campaign_counts(binary, surviving.sql_port, env, campaign)
    start_node(binary, target, join, cache, sql_memory, env, append=True)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        try:
            after = campaign_counts(binary, target.sql_port, env, campaign)
            if after == before:
                return {
                    "node": node_index + 1,
                    "signal": "SIGKILL",
                    "returncode": returncode,
                    "before": list(before),
                    "during": list(during),
                    "after": list(after),
                    "green": during == before and after == before,
                }
        except (CampaignError, subprocess.TimeoutExpired):
            time.sleep(1)
    raise CampaignError("FAULT_RESTART_RECONCILIATION_FAILED")


def create_query_files(canary: Any, root: Path, campaign_id: str) -> dict[str, dict[str, Any]]:
    canary.CAMPAIGN_ID = campaign_id
    return canary.build_query_files(root)


def verifier_batch(
    canary: Any,
    root: Path,
    env: dict[str, str],
    campaign_id: str,
) -> dict[str, Any]:
    canary.CAMPAIGN_ID = campaign_id
    result = canary.run_verifier_campaign(root, env)
    if result["measured_executions"] != contract.VERIFIER_BATCH_SIZE:
        raise CampaignError("VERIFIER_BATCH_COUNT_INVALID")
    return result


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


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if not args.campaign_id.startswith("ck-pdh3-scale-"):
        raise CampaignError("CAMPAIGN_ID_INVALID")
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
    root_parent = Path("/tmp" if sys.platform.startswith("linux") else "/private/tmp")
    root = Path(tempfile.mkdtemp(prefix=args.campaign_id + ".", dir=root_parent))
    fake_home = root / "empty-home"
    fake_home.mkdir()
    env = scrubbed_env(fake_home)
    journal = ChainLog(output / "journal.ndjson", args.campaign_id)
    canary = load_canary_module()
    canary.CANDIDATE = contract.PRODUCT_CANDIDATE
    canary.P99_LIMIT_MS = contract.P99_LIMIT_MS
    canary.PMAX_LIMIT_MS = contract.PMAX_LIMIT_MS
    canary.STAGE_DURATION_SECONDS = args.query_duration_seconds
    nodes: list[Node] = []
    join = ""
    result: dict[str, Any] | None = None
    teardown: dict[str, Any] = {
        "nodes_stopped": False,
        "ports_closed": False,
        "generated_root_removed": False,
        "database_dropped": False,
    }
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
        )
        gateway = nodes[0].sql_port
        apply_migrations(binary, gateway, env)
        setup_deadline = time.monotonic() + args.setup_timeout_seconds
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
        )
        expected_counts = (
            args.tasks,
            args.tasks * args.events_per_task,
            args.tasks * args.receipts_per_task,
            args.vectors,
        )
        if campaign_counts(binary, gateway, env, args.campaign_id) != expected_counts:
            raise CampaignError("SEEDED_COUNTS_MISMATCH")
        wrong_links = parse_last_integer(
            sql(
                binary,
                gateway,
                "SELECT count(*) FROM ck.context_vectors v "
                "JOIN ck.trajectory_events e ON e.event_hash=v.event_hash "
                "WHERE v.task_id != e.task_id",
                env=env,
            )
        )
        if wrong_links:
            raise CampaignError("VECTOR_CROSS_TASK_CONTAMINATION")
        query_files = create_query_files(canary, root, args.campaign_id)
        measured_start_ns = time.monotonic_ns()
        measured_start_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        checkpoints: list[dict[str, Any]] = []
        total_verifier = 0
        total_operations = 0
        max_p99 = 0.0
        max_pmax = 0.0
        fault_count = 0
        required_checkpoints = args.duration_seconds // args.checkpoint_seconds
        for epoch in range(required_checkpoints):
            epoch_start_ns = time.monotonic_ns()
            epoch_root = root / f"epoch-{epoch:04d}"
            epoch_root.mkdir()
            concurrency = min(
                args.max_concurrency,
                contract.CONCURRENCY_STAGES[
                    min(epoch, len(contract.CONCURRENCY_STAGES) - 1)
                ],
            )
            canary.MINIMUM_ACK_WRITE_OPERATIONS = max(2_000, concurrency * 10)
            canary.MINIMUM_CONTENDED_UPDATE_OPERATIONS = max(1_000, concurrency * 5)
            canary.MINIMUM_REPLAY_OPERATIONS = max(1_000, concurrency * 5)
            with ThreadPoolExecutor(max_workers=1) as executor:
                cleanup_future = executor.submit(
                    cleanup_probe,
                    binary,
                    gateway,
                    env,
                    args.campaign_id,
                    epoch,
                )
                stage = canary.run_stage(
                    binary,
                    gateway,
                    query_files,
                    epoch_root,
                    concurrency,
                    env,
                )
                cleanup = cleanup_future.result(timeout=120)
            if not stage["green"]:
                raise CampaignError("CONCURRENCY_STAGE_BLOCKED:" + str(concurrency))
            dependency = dependency_matrix(
                binary, gateway, env, args.campaign_id, epoch
            )
            verifier = None
            if epoch < min(contract.VERIFIER_BATCHES, required_checkpoints):
                verifier = verifier_batch(
                    canary,
                    epoch_root / "verifier",
                    env,
                    f"{args.campaign_id}-v{epoch:04d}",
                )
                total_verifier += verifier["measured_executions"]
            fault = None
            if (epoch + 1) % args.fault_every_checkpoints == 0:
                target = fault_count % 3
                fault = fault_cycle(
                    binary,
                    nodes,
                    target,
                    join,
                    args.cache,
                    args.sql_memory,
                    env,
                    args.campaign_id,
                )
                fault_count += 1
                gateway = nodes[0].sql_port
                if not fault["green"]:
                    raise CampaignError("FAULT_CYCLE_NOT_GREEN")
            counts = campaign_counts(binary, gateway, env, args.campaign_id)
            if counts != expected_counts:
                raise CampaignError("ACKNOWLEDGED_DATASET_DRIFT")
            wrong_links = parse_last_integer(
                sql(
                    binary,
                    gateway,
                    "SELECT count(*) FROM ck.context_vectors v "
                    "JOIN ck.trajectory_events e ON e.event_hash=v.event_hash "
                    "WHERE v.task_id != e.task_id",
                    env=env,
                )
            )
            if wrong_links:
                raise CampaignError("VECTOR_CROSS_TASK_CONTAMINATION")
            resources = process_metrics(nodes, root, output)
            if resources["database_bytes"] > contract.DATABASE_BYTES_LIMIT:
                raise CampaignError("DATABASE_GROWTH_LIMIT")
            if resources["evidence_bytes"] > contract.EVIDENCE_BYTES_LIMIT:
                raise CampaignError("EVIDENCE_GROWTH_LIMIT")
            if resources["disk_used_fraction"] > args.disk_used_fraction_limit:
                raise CampaignError("DISK_USED_FRACTION_LIMIT")
            total_operations += stage["total_operations"]
            max_p99 = max(max_p99, stage["maximum_latency_ms"]["p99"])
            max_pmax = max(max_pmax, stage["maximum_latency_ms"]["max"])
            checkpoint_body = {
                "version": "ck-pdh3-scale-checkpoint-v1",
                "epoch": epoch + 1,
                "concurrency": concurrency,
                "stage": stage,
                "cleanup_probe": cleanup,
                "dependency_matrix": dependency,
                "verifier": verifier,
                "fault": fault,
                "counts": list(counts),
                "wrong_task_vector_links": wrong_links,
                "resources": resources,
                "elapsed_ns": time.monotonic_ns() - measured_start_ns,
            }
            checkpoint = {
                **checkpoint_body,
                "checkpoint_sha256": digest(checkpoint_body),
            }
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
            next_boundary_ns = (
                measured_start_ns + (epoch + 1) * args.checkpoint_seconds * 1_000_000_000
            )
            remaining_ns = next_boundary_ns - time.monotonic_ns()
            if remaining_ns < 0:
                raise CampaignError("CHECKPOINT_INTERVAL_OVERRUN")
            time.sleep(remaining_ns / 1_000_000_000)
            if time.monotonic_ns() - epoch_start_ns > (
                args.checkpoint_seconds * 1_000_000_000 + 2_000_000_000
            ):
                raise CampaignError("CHECKPOINT_SCHEDULE_DRIFT")
        measured_end_ns = time.monotonic_ns()
        measured_seconds = (measured_end_ns - measured_start_ns) / 1_000_000_000
        if args.production and not (args.duration_seconds <= measured_seconds <= args.duration_seconds + 2):
            raise CampaignError("MEASURED_DURATION_INVALID")
        if args.production and total_verifier != contract.VERIFIER_EXECUTIONS:
            raise CampaignError("VERIFIER_EXECUTION_TOTAL_INVALID")
        if max_p99 > contract.P99_LIMIT_MS or max_pmax > contract.PMAX_LIMIT_MS:
            raise CampaignError("LATENCY_THRESHOLD_BREACH")
        final_counts = campaign_counts(binary, gateway, env, args.campaign_id)
        final_wrong_links = parse_last_integer(
            sql(
                binary,
                gateway,
                "SELECT count(*) FROM ck.context_vectors v "
                "JOIN ck.trajectory_events e ON e.event_hash=v.event_hash "
                "WHERE v.task_id != e.task_id",
                env=env,
            )
        )
        result_body = {
            "version": "ck-pdh3-production-scale-result-v1",
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
            "cluster_topology": "THREE_NODES_ONE_SECURE_RUNPOD_HOST",
            "measured_start_utc": measured_start_utc,
            "measured_end_utc": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            ),
            "measured_seconds": measured_seconds,
            "seed": seed,
            "dataset_counts": list(final_counts),
            "wrong_task_vector_links": final_wrong_links,
            "checkpoints": checkpoints,
            "checkpoint_count": len(checkpoints),
            "total_measured_operations": total_operations,
            "verifier_executions": total_verifier,
            "fault_cycles": fault_count,
            "maximum_p99_ms": max_p99,
            "maximum_latency_ms": max_pmax,
            "journal_terminal_hash_before_result": journal.previous,
            "limitations": [
                "SYNTHETIC_ONLY",
                "SINGLE_RUNPOD_HOST",
                "NOT_MULTI_REGION",
                "NOT_PRODUCTION_TRAFFIC",
                "LAMBDA_FAILURES_ARE_FROZEN_LOCAL_ADVICE_STATES",
                "GPU_NOT_USED_BY_CPU_BOUND_PROTOCOL",
            ],
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
            "fault_cycles": fault_count >= (required_checkpoints // args.fault_every_checkpoints),
        }
        if not all(result_body["green_checks"].values()):
            raise CampaignError("FINAL_GREEN_CHECK_FAILED")
        result = {**result_body, "result_sha256": digest(result_body)}
        atomic_write(output / "result.json", canonical(result))
        journal.emit("MEASURED_CAMPAIGN_GREEN", {"result_sha256": result["result_sha256"]})
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
        return result
    except BaseException as exc:
        failure_body = {
            "version": "ck-pdh3-scale-failure-v1",
            "campaign_id": args.campaign_id,
            "exception_type": type(exc).__name__,
            "reason": str(exc),
            "journal_prior_hash": journal.previous,
        }
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
        for node in nodes:
            stop_node(node, crash=False)
        teardown["nodes_stopped"] = all(
            node.process is None for node in nodes
        )
        open_ports = []
        for node in nodes:
            for port in (node.sql_port, node.http_port):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                    probe.settimeout(0.2)
                    if probe.connect_ex(("127.0.0.1", port)) == 0:
                        open_ports.append(port)
        teardown["ports_closed"] = not open_ports
        verified = root.resolve()
        if verified.parent not in (Path("/tmp"), Path("/private/tmp")):
            raise CampaignError("GENERATED_ROOT_PARENT_INVALID")
        if not verified.name.startswith(args.campaign_id + "."):
            raise CampaignError("GENERATED_ROOT_IDENTITY_INVALID")
        shutil.rmtree(verified)
        teardown["generated_root_removed"] = not verified.exists()
        teardown_body = {
            "version": "ck-pdh3-scale-teardown-v1",
            "campaign_id": args.campaign_id,
            **teardown,
            "open_ports": open_ports,
        }
        atomic_write(
            output / "teardown.json",
            canonical({**teardown_body, "receipt_sha256": digest(teardown_body)}),
        )
        journal.emit("LOCAL_TEARDOWN", teardown)
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
