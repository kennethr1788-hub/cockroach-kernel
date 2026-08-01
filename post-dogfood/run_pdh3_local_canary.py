#!/usr/bin/env python3
"""No-cost local calibration for PDH-3 production-shaped scale.

This evidence controller does not change product behavior and does not claim
cloud or production validation. It runs the frozen verifier campaign in fresh
processes, starts one loopback-only disposable CockroachDB node, loads the real
P9 application schema with synthetic rows, exercises stepped query concurrency,
tests crash/restart durability, and tears down the generated root.
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
import subprocess
import sys
import tempfile
import time
from typing import Any


BASE = Path(__file__).resolve().parents[1]
CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
PLAN_SHA256 = "bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24"
PACKET_NAME = "PDH_3_LOCAL_CANARY_PACKET_R2.md"
CAMPAIGN_ID = "ck-g7r9-pdh3-local-r1"
TASK_ID_WIDTH = 4
TASKS = 500
EVENTS_PER_TASK = 10
RECEIPTS_PER_TASK = 2
VECTORS_PER_TASK = 10
QUERY_SAMPLES = 200
STAGES = (10, 50, 100, 250)
STAGE_DURATION_SECONDS = 2
MINIMUM_ACK_WRITE_OPERATIONS = 2_000
MINIMUM_CONTENDED_UPDATE_OPERATIONS = 1_000
MINIMUM_REPLAY_OPERATIONS = 1_000
MINIMUM_STAGE_OPERATIONS = 500
P99_LIMIT_MS = 5_000.0
PMAX_LIMIT_MS = 10_000.0
MAX_SERIALIZATION_RETRIES = 3
SERIALIZATION_RETRY_BACKOFF_MS = 250
ZERO_HASH = "0" * 64
SQLSTATE_40001_RE = re.compile(rb"SQLSTATE:\s*40001\b")
SUMMARY_RE = re.compile(
    r"^\s*(?P<elapsed>[0-9.]+)s\s+"
    r"(?P<errors>\d+)\s+"
    r"(?P<ops>\d+)\s+"
    r"(?P<ops_sec>[0-9.]+)\s+"
    r"(?P<avg>[0-9.]+)\s+"
    r"(?P<p50>[0-9.]+)\s+"
    r"(?P<p95>[0-9.]+)\s+"
    r"(?P<p99>[0-9.]+)\s+"
    r"(?P<pmax>[0-9.]+)"
)


class CanaryError(RuntimeError):
    pass


def bounded_timeout(
    deadline: float | None,
    cap_seconds: int,
    *,
    required_seconds: float = 1.0,
    reserve_seconds: float = 0.0,
) -> int:
    """Return a timeout that cannot cross a shared monotonic deadline."""
    if deadline is None:
        return cap_seconds
    available = deadline - time.monotonic() - reserve_seconds
    if available < required_seconds:
        raise CanaryError("EPOCH_DEADLINE_EXHAUSTED")
    return max(1, min(cap_seconds, int(available)))


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


def verifier_public_salt(campaign_id: str) -> bytes:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,127}", campaign_id):
        raise CanaryError("VERIFIER_CAMPAIGN_ID_INVALID")
    return hashlib.sha256(
        (
            CANDIDATE
            + ":"
            + campaign_id
            + ":verifier-public-salt-v1"
        ).encode("utf-8")
    ).digest()


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


def file_sha256(path: Path) -> str:
    return digest(path.read_bytes())


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CanaryError("MODULE_LOAD_FAILED:" + name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def find_cockroach() -> Path:
    matches = [
        path
        for path in BASE.glob("p2-cleanroom/vendor/**/cockroach")
        if "darwin" in str(path) and path.is_file() and os.access(path, os.X_OK)
    ]
    if len(matches) != 1:
        raise CanaryError("LOCAL_COCKROACH_BINARY_NOT_UNIQUE")
    return matches[0].resolve()


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
    stdin: bytes | None = None,
    stdout_path: Path | None = None,
    stderr_path: Path | None = None,
) -> subprocess.CompletedProcess[bytes]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(input=stdin, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate(timeout=5)
        captured_stdout = stdout if stdout else (exc.stdout or b"")
        captured_stderr = stderr if stderr else (exc.stderr or b"")
        if stdout_path is not None:
            atomic_write(stdout_path, captured_stdout)
        if stderr_path is not None:
            atomic_write(stderr_path, captured_stderr)
        partial = captured_stdout + captured_stderr
        raise CanaryError(
            "COMMAND_TIMEOUT:"
            + Path(command[0]).name
            + ":"
            + str(timeout)
            + ":"
            + digest(partial)
        ) from exc
    if stdout_path is not None:
        atomic_write(stdout_path, stdout)
    if stderr_path is not None:
        atomic_write(stderr_path, stderr)
    result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    if result.returncode != 0:
        raise CanaryError(
            "COMMAND_FAILED:"
            + command[1 if len(command) > 1 else 0]
            + ":"
            + digest(result.stdout + result.stderr)
            + ":stdout="
            + digest(result.stdout)
            + ":stderr="
            + digest(result.stderr)
        )
    return result


def sql(
    binary: Path,
    port: int,
    statement: str,
    *,
    env: dict[str, str],
    database: str | None = None,
    timeout: int = 120,
    deadline: float | None = None,
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
    return run(
        command,
        env=env,
        timeout=bounded_timeout(deadline, timeout),
    ).stdout


def apply_file(
    binary: Path,
    port: int,
    database: str,
    path: Path,
    *,
    env: dict[str, str],
) -> None:
    run(
        [
            str(binary),
            "sql",
            "--insecure",
            f"--host=127.0.0.1:{port}",
            f"--database={database}",
            f"--file={path.resolve()}",
        ],
        env=env,
        timeout=300,
    )


def start_database(
    binary: Path,
    root: Path,
    port: int,
    http_port: int,
    env: dict[str, str],
    *,
    append_log: bool,
) -> tuple[subprocess.Popen[bytes], Any]:
    log_mode = "ab" if append_log else "xb"
    log_handle = (root / "cockroach.log").open(log_mode, buffering=0)
    process = subprocess.Popen(
        [
            str(binary),
            "start-single-node",
            "--insecure",
            f"--store={root / 'store'}",
            f"--listen-addr=127.0.0.1:{port}",
            f"--http-addr=127.0.0.1:{http_port}",
            f"--temp-dir={root / 'temp'}",
            "--logtostderr=ERROR",
        ],
        cwd=root,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
    )
    for _ in range(120):
        if process.poll() is not None:
            log_handle.close()
            raise CanaryError("COCKROACH_EXITED_BEFORE_READY")
        try:
            sql(binary, port, "SELECT 1", env=env, timeout=5)
            return process, log_handle
        except (CanaryError, subprocess.TimeoutExpired):
            time.sleep(0.25)
    process.send_signal(signal.SIGTERM)
    process.wait(timeout=15)
    log_handle.close()
    raise CanaryError("COCKROACH_READINESS_TIMEOUT")


def stop_database(
    process: subprocess.Popen[bytes],
    log_handle: Any,
    *,
    crash: bool,
) -> int:
    if process.poll() is None:
        process.send_signal(signal.SIGKILL if crash else signal.SIGTERM)
    try:
        returncode = process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        process.kill()
        returncode = process.wait(timeout=10)
    log_handle.close()
    if process.poll() is None:
        raise CanaryError("COCKROACH_PROCESS_REMAINS")
    return returncode


def parse_last_integer(raw: bytes) -> int:
    lines = [line.strip() for line in raw.decode("utf-8").splitlines() if line.strip()]
    for line in reversed(lines):
        if line.isdigit():
            return int(line)
    raise CanaryError("INTEGER_OUTPUT_INVALID")


def parse_count_tuple(raw: bytes, expected: int) -> tuple[int, ...]:
    lines = [line.strip() for line in raw.decode("utf-8").splitlines() if line.strip()]
    for line in reversed(lines):
        fields = line.split("\t")
        if len(fields) == expected and all(field.isdigit() for field in fields):
            return tuple(int(field) for field in fields)
    raise CanaryError("COUNT_OUTPUT_INVALID")


def tree_bytes(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def build_dataset(generated: Path) -> dict[str, Any]:
    module = load_module(
        "pdh3_synthetic_dataset",
        BASE / "post-dogfood/pdh3_synthetic_dataset.py",
    )
    return module.build_sql(
        CAMPAIGN_ID,
        generated,
        tasks=TASKS,
        events_per_task=EVENTS_PER_TASK,
        receipts_per_task=RECEIPTS_PER_TASK,
        vectors_per_task=VECTORS_PER_TASK,
        query_samples=QUERY_SAMPLES,
        concurrency=STAGES[0],
        task_id_width=TASK_ID_WIDTH,
    )


def insert_dataset(
    binary: Path,
    port: int,
    generated: Path,
    manifest: dict[str, Any],
    env: dict[str, str],
) -> dict[str, Any]:
    stage_elapsed_ms: dict[str, int] = {}
    output_hashes: dict[str, list[str]] = {}
    retries_by_stage: dict[str, int] = {}
    for stage in ("tasks", "events", "receipts", "vectors"):
        started = time.monotonic_ns()
        hashes: list[str] = []
        retries = 0
        for batch in manifest["batches"][stage]:
            path = generated / batch["path"]
            if file_sha256(path) != batch["sha256"]:
                raise CanaryError("GENERATED_BATCH_HASH_MISMATCH")
            command = [
                str(binary),
                "sql",
                "--insecure",
                f"--host=127.0.0.1:{port}",
                "--database=cockroach_kernel",
                f"--file={path}",
            ]
            for attempt in range(MAX_SERIALIZATION_RETRIES + 1):
                completed = subprocess.run(
                    command,
                    env=env,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=300,
                    check=False,
                )
                if completed.returncode == 0:
                    break
                if (
                    SQLSTATE_40001_RE.search(completed.stdout)
                    and attempt < MAX_SERIALIZATION_RETRIES
                ):
                    retries += 1
                    time.sleep(SERIALIZATION_RETRY_BACKOFF_MS / 1_000)
                    continue
                raise CanaryError(
                    f"INSERT_BATCH_FAILED:{stage}:{batch['batch_index']}:"
                    + digest(completed.stdout)
                )
            hashes.append(digest(completed.stdout))
        stage_elapsed_ms[stage] = int((time.monotonic_ns() - started) / 1_000_000)
        output_hashes[stage] = hashes
        retries_by_stage[stage] = retries
    return {
        "stage_elapsed_ms": stage_elapsed_ms,
        "output_set_sha256": {
            stage: digest(hashes) for stage, hashes in output_hashes.items()
        },
        "serialization_retries_by_stage": retries_by_stage,
        "batch_count": sum(len(rows) for rows in manifest["batches"].values()),
        "serialization_retries": sum(retries_by_stage.values()),
    }


def build_query_files(root: Path) -> dict[str, dict[str, Any]]:
    rows: list[str] = []
    for index in range(20):
        task_id = f"{CAMPAIGN_ID}-task-{index:0{TASK_ID_WIDTH}d}"
        vector_id = f"{task_id}-vector-00"
        rows.append(
            f"vector-{index:02d}: SELECT count(*) FROM ck.context_vectors "
            f"WHERE task_id='{task_id}' AND namespace='{CAMPAIGN_ID}' "
            f"AND vector_id='{vector_id}'"
        )
    for index in range(5):
        task_id = f"{CAMPAIGN_ID}-task-{index:0{TASK_ID_WIDTH}d}"
        rows.append(
            f"receipt-{index:02d}: SELECT count(*) FROM ck.mcp_receipt_view "
            f"WHERE task_id='{task_id}'"
        )
    rows.extend(
        [
            "stale-projection-read: SELECT count(*) FROM ck.projection_events "
            "WHERE source_key LIKE 'missing-stale-%'",
            "trajectory-link-read: SELECT count(*) FROM ck.trajectory_events e "
            "JOIN ck.tasks t ON t.task_id=e.task_id "
            f"WHERE t.task_id='{CAMPAIGN_ID}-task-{0:0{TASK_ID_WIDTH}d}' "
            f"AND t.campaign_id='{CAMPAIGN_ID}'",
        ]
    )
    definitions = {
        "read_mix": rows,
        "ack_write": [
            "ack-write: INSERT INTO ck.pdh3_acknowledged_writes"
            "(ack_id,created_at) VALUES (gen_random_uuid()::STRING,now())"
        ],
        "contended_update": [
            "contended-update: UPDATE ck.pdh3_counter "
            "SET value=value+1 WHERE id='shared'"
        ],
        "replay": [
            "replay-idempotency: INSERT INTO ck.pdh3_replay_control"
            "(replay_id) VALUES ('fixed-replay') ON CONFLICT DO NOTHING"
        ],
    }
    result: dict[str, dict[str, Any]] = {}
    for kind, queries in definitions.items():
        path = root / f"querybench-{kind}.sql"
        atomic_write(path, ("\n".join(queries) + "\n").encode("utf-8"))
        result[kind] = {
            "path": path,
            "query_names": [row.split(":", 1)[0] for row in queries],
            "sha256": file_sha256(path),
        }
    return result


def parse_querybench_summary(raw: bytes) -> dict[str, Any]:
    matches = [
        SUMMARY_RE.match(line)
        for line in raw.decode("utf-8", "replace").splitlines()
    ]
    values = [match for match in matches if match is not None]
    if not values:
        raise CanaryError("QUERYBENCH_SUMMARY_MISSING")
    value = values[-1].groupdict()
    return {
        "elapsed_seconds": float(value["elapsed"]),
        "errors": int(value["errors"]),
        "operations": int(value["ops"]),
        "operations_per_second": float(value["ops_sec"]),
        "latency_ms": {
            "avg": float(value["avg"]),
            "p50": float(value["p50"]),
            "p95": float(value["p95"]),
            "p99": float(value["p99"]),
            "max": float(value["pmax"]),
        },
    }


def parse_histogram_count(path: Path) -> int:
    total = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        raw_counts = row.get("Hist", {}).get("Counts")
        if not isinstance(row.get("Name"), str) or not isinstance(raw_counts, list):
            raise CanaryError("QUERYBENCH_HISTOGRAM_SCHEMA_INVALID")
        total += sum(int(item) for item in raw_counts)
    return total


def run_querybench(
    binary: Path,
    port: int,
    query_file: Path,
    root: Path,
    concurrency: int,
    kind: str,
    env: dict[str, str],
    *,
    duration_seconds: int | None = None,
    minimum_operations: int | None = None,
    deadline: float | None = None,
) -> dict[str, Any]:
    if (duration_seconds is None) == (minimum_operations is None):
        raise CanaryError("QUERYBENCH_BOUNDARY_INVALID")
    prefix = f"querybench-c{concurrency}-{kind}"
    output_path = root / f"{prefix}.stdout.log"
    error_path = root / f"{prefix}.stderr.log"
    histogram_path = root / f"{prefix}.histograms.json"
    command = [
        str(binary),
        "workload",
        "run",
        "querybench",
        f"postgresql://root@127.0.0.1:{port}/cockroach_kernel?sslmode=disable",
        "--db=cockroach_kernel",
        f"--query-file={query_file}",
        f"--concurrency={concurrency}",
        "--display-format=simple",
        "--display-every=1s",
        "--verbose=false",
        f"--histograms={histogram_path}",
        "--histogram-export-format=json",
        "--isolation-level=serializable",
        "--warmup-conns=0",
    ]
    if duration_seconds is not None:
        command.append(f"--duration={duration_seconds}s")
        timeout_seconds = bounded_timeout(
            deadline,
            duration_seconds + 60,
            required_seconds=duration_seconds + 1,
        )
        execution_boundary = {
            "mode": "FIXED_DURATION",
            "duration_seconds": duration_seconds,
            "target_operations": None,
        }
    else:
        command.append(f"--max-ops={minimum_operations}")
        timeout_seconds = bounded_timeout(deadline, 120)
        execution_boundary = {
            "mode": "BOUNDED_FIXED_OPERATIONS",
            "duration_seconds": None,
            "minimum_operations": minimum_operations,
            "maximum_operations": minimum_operations + concurrency - 1,
            "querybench_soft_cap": minimum_operations,
        }
    completed = run(
        command,
        env=env,
        timeout=timeout_seconds,
        stdout_path=output_path,
        stderr_path=error_path,
    )
    if completed.returncode != 0:
        raise CanaryError(f"QUERYBENCH_FAILED_C{concurrency}_{kind}")
    summary = parse_querybench_summary(completed.stdout)
    histogram_count = parse_histogram_count(histogram_path)
    return {
        "kind": kind,
        "execution_boundary": execution_boundary,
        "summary": summary,
        "histogram_count": histogram_count,
        "histogram_accounts_for_operations": (
            histogram_count == summary["operations"]
        ),
        "stdout_sha256": file_sha256(output_path),
        "stderr_sha256": file_sha256(error_path),
        "histograms_sha256": file_sha256(histogram_path),
    }


def run_stage(
    binary: Path,
    port: int,
    query_files: dict[str, dict[str, Any]],
    root: Path,
    concurrency: int,
    env: dict[str, str],
    *,
    deadline: float | None = None,
) -> dict[str, Any]:
    ack_before = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT count(*) FROM ck.pdh3_acknowledged_writes",
            env=env,
            database="cockroach_kernel",
            deadline=deadline,
        )
    )
    counter_before = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT value FROM ck.pdh3_counter WHERE id='shared'",
            env=env,
            database="cockroach_kernel",
            deadline=deadline,
        )
    )
    workloads = {
        "read_mix": run_querybench(
            binary,
            port,
            query_files["read_mix"]["path"],
            root,
            concurrency,
            "read_mix",
            env,
            duration_seconds=STAGE_DURATION_SECONDS,
            deadline=deadline,
        ),
        "ack_write": run_querybench(
            binary,
            port,
            query_files["ack_write"]["path"],
            root,
            concurrency,
            "ack_write",
            env,
            minimum_operations=MINIMUM_ACK_WRITE_OPERATIONS,
            deadline=deadline,
        ),
        "contended_update": run_querybench(
            binary,
            port,
            query_files["contended_update"]["path"],
            root,
            concurrency,
            "contended_update",
            env,
            minimum_operations=MINIMUM_CONTENDED_UPDATE_OPERATIONS,
            deadline=deadline,
        ),
        "replay": run_querybench(
            binary,
            port,
            query_files["replay"]["path"],
            root,
            concurrency,
            "replay",
            env,
            minimum_operations=MINIMUM_REPLAY_OPERATIONS,
            deadline=deadline,
        ),
    }
    ack_after = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT count(*) FROM ck.pdh3_acknowledged_writes",
            env=env,
            database="cockroach_kernel",
            deadline=deadline,
        )
    )
    counter_after = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT value FROM ck.pdh3_counter WHERE id='shared'",
            env=env,
            database="cockroach_kernel",
            deadline=deadline,
        )
    )
    replay_rows = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT count(*) FROM ck.pdh3_replay_control",
            env=env,
            database="cockroach_kernel",
            deadline=deadline,
        )
    )
    total_operations = sum(
        workload["summary"]["operations"] for workload in workloads.values()
    )
    p99 = max(
        workload["summary"]["latency_ms"]["p99"]
        for workload in workloads.values()
    )
    pmax = max(
        workload["summary"]["latency_ms"]["max"]
        for workload in workloads.values()
    )
    checks = {
        "zero_errors": all(
            workload["summary"]["errors"] == 0
            for workload in workloads.values()
        ),
        "minimum_operations": total_operations >= MINIMUM_STAGE_OPERATIONS,
        "histograms_account_for_operations": all(
            workload["histogram_accounts_for_operations"]
            for workload in workloads.values()
        ),
        "bounded_operation_targets_respected": all(
            workload["execution_boundary"]["minimum_operations"]
            <= workload["summary"]["operations"]
            <= workload["execution_boundary"]["maximum_operations"]
            for workload in (
                workloads["ack_write"],
                workloads["contended_update"],
                workloads["replay"],
            )
        ),
        "acknowledged_writes_exact": (
            ack_after - ack_before
            == workloads["ack_write"]["summary"]["operations"]
        ),
        "contended_updates_exact": (
            counter_after - counter_before
            == workloads["contended_update"]["summary"]["operations"]
        ),
        "replay_idempotent": replay_rows == 1,
        "p99_within_limit": p99 <= P99_LIMIT_MS,
        "pmax_within_limit": pmax <= PMAX_LIMIT_MS,
    }
    return {
        "concurrency": concurrency,
        "workloads": workloads,
        "total_operations": total_operations,
        "maximum_latency_ms": {"p99": p99, "max": pmax},
        "acknowledged_write_delta": ack_after - ack_before,
        "contended_update_delta": counter_after - counter_before,
        "replay_rows": replay_rows,
        "checks": checks,
        "green": all(checks.values()),
    }


def run_verifier_campaign(
    root: Path,
    env: dict[str, str],
    *,
    deadline: float | None = None,
) -> dict[str, Any]:
    salt = root / "public-salt.bin"
    vector_set = root / "public-vectors.json"
    output = root / "verifier-campaign"
    atomic_write(salt, verifier_public_salt(CAMPAIGN_ID))
    run(
        [
            sys.executable,
            str(BASE / "hardening-gate7/make_vectors.py"),
            "--candidate-commit",
            CANDIDATE,
            "--salt-file",
            str(salt),
            "--output",
            str(vector_set),
        ],
        env=env,
        timeout=bounded_timeout(deadline, 60, reserve_seconds=1),
        cwd=BASE,
    )
    run(
        [
            sys.executable,
            str(BASE / "hardening-gate7/run_campaign.py"),
            "--vector-set",
            str(vector_set),
            "--candidate-commit",
            CANDIDATE,
            "--campaign-id",
            CAMPAIGN_ID + "-verifier",
            "--python-bin",
            sys.executable,
            "--output-root",
            str(output),
        ],
        env=env,
        timeout=bounded_timeout(deadline, 180),
        cwd=BASE,
    )
    aggregate_path = output / "aggregate.json"
    aggregate = json.loads(aggregate_path.read_bytes())
    if not aggregate.get("green"):
        raise CanaryError("VERIFIER_CAMPAIGN_NOT_GREEN")
    return {
        "aggregate_sha256": aggregate["aggregate_sha256"],
        "aggregate_file_sha256": file_sha256(aggregate_path),
        "measured_executions": aggregate["measured_executions"],
        "false_promotions": aggregate["false_promotions"],
        "mutation_after_refusal": aggregate["mutation_after_refusal"],
        "correct_stable_reason_count": aggregate["correct_stable_reason_count"],
        "valid_control_continuation_count": aggregate[
            "valid_control_continuation_count"
        ],
        "trial_teardown_count": aggregate["trial_teardown_count"],
        "residue_count": aggregate["residue_count"],
    }


def verify_query_targets(
    binary: Path,
    port: int,
    env: dict[str, str],
    *,
    campaign_id: str,
    id_width: int,
    deadline: float | None = None,
) -> dict[str, Any]:
    """Prove the generated scale read mix addresses real seeded rows."""
    if id_width < 1 or id_width > 12:
        raise CanaryError("TASK_ID_WIDTH_INVALID")
    vector_ids = [
        f"{campaign_id}-task-{index:0{id_width}d}" for index in range(20)
    ]
    receipt_ids = vector_ids[:5]
    vector_values = ",".join("'" + value.replace("'", "''") + "'" for value in vector_ids)
    receipt_values = ",".join("'" + value.replace("'", "''") + "'" for value in receipt_ids)
    vector_rows = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT count(*) FROM ck.context_vectors "
            f"WHERE namespace='{campaign_id}' AND task_id IN ({vector_values})",
            env=env,
            database="cockroach_kernel",
            deadline=deadline,
        )
    )
    receipt_rows = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT count(*) FROM ck.mcp_receipt_view "
            f"WHERE task_id IN ({receipt_values})",
            env=env,
            database="cockroach_kernel",
            deadline=deadline,
        )
    )
    expected_vectors = len(vector_ids)
    expected_receipts = len(receipt_ids) * RECEIPTS_PER_TASK
    body = {
        "id_width": id_width,
        "vector_rows": vector_rows,
        "expected_vector_rows": expected_vectors,
        "receipt_rows": receipt_rows,
        "expected_receipt_rows": expected_receipts,
        "green": vector_rows == expected_vectors and receipt_rows == expected_receipts,
    }
    if not body["green"]:
        raise CanaryError("QUERY_TARGET_CARDINALITY_MISMATCH")
    return body


def source_hashes(packet: Path) -> dict[str, str]:
    paths = [
        packet,
        Path(__file__).resolve(),
        BASE / "post-dogfood/pdh3_synthetic_dataset.py",
        BASE / "hardening-gate7/make_vectors.py",
        BASE / "hardening-gate7/run_campaign.py",
        BASE / "hardening-gate7/run_trial.py",
        BASE / "p9-cloud/context_vector.py",
        BASE / "p9-cloud/records.py",
        BASE / "p9-cloud/migrations/001_cloud.sql",
        BASE / "p9-cloud/migrations/003_collision_safe_vector_digest.sql",
    ]
    return {str(path.relative_to(BASE)): file_sha256(path) for path in paths}


def port_is_closed(port: int) -> bool:
    """Return true only when a new loopback connection is refused."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.2)
        return probe.connect_ex(("127.0.0.1", port)) != 0


def finalize_local_teardown(
    *,
    output: Path,
    root: Path,
    process: subprocess.Popen[bytes] | None,
    log_handle: Any | None,
    ports: tuple[int, int],
    packet_hash: str,
    workload_exception: BaseException | None,
) -> dict[str, Any]:
    """Attempt every teardown step and persist a fail-closed receipt.

    This function never turns a failed step into GREEN.  It records all
    teardown errors so a process-stop failure cannot prevent the guarded root
    removal and port checks from being attempted.
    """
    errors: list[str] = []
    database_process_stopped = False
    if process is None:
        database_process_stopped = True
    elif log_handle is None:
        errors.append("DATABASE_LOG_HANDLE_MISSING")
        try:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
            database_process_stopped = process.poll() is not None
        except Exception as exc:  # pragma: no cover - platform failure path
            errors.append("DATABASE_FORCE_STOP_FAILED:" + type(exc).__name__)
    else:
        try:
            stop_database(process, log_handle, crash=False)
            database_process_stopped = process.poll() is not None
        except Exception as exc:
            errors.append("DATABASE_STOP_FAILED:" + type(exc).__name__)
            database_process_stopped = process.poll() is not None
    if log_handle is not None and not getattr(log_handle, "closed", False):
        try:
            log_handle.close()
        except Exception as exc:  # pragma: no cover - filesystem failure path
            errors.append("DATABASE_LOG_CLOSE_FAILED:" + type(exc).__name__)

    open_ports: list[int] = []
    for checked_port in ports:
        closed = False
        for _ in range(20):
            try:
                if port_is_closed(checked_port):
                    closed = True
                    break
            except OSError as exc:
                errors.append(
                    f"PORT_PROBE_FAILED:{checked_port}:{type(exc).__name__}"
                )
                break
            time.sleep(0.05)
        if not closed:
            open_ports.append(checked_port)
    ports_closed = not open_ports
    if open_ports:
        errors.append("LOCAL_PORTS_REMAIN_OPEN:" + ",".join(map(str, open_ports)))

    generated_root_removed = False
    verified_root = root.resolve()
    if (
        verified_root.parent != Path("/private/tmp")
        or not verified_root.name.startswith("ck-pdh3-local-r1.")
    ):
        errors.append("GENERATED_ROOT_IDENTITY_INVALID")
    else:
        try:
            if verified_root.exists():
                shutil.rmtree(verified_root)
            generated_root_removed = not verified_root.exists()
        except Exception as exc:
            errors.append("GENERATED_ROOT_REMOVE_FAILED:" + type(exc).__name__)
        if not generated_root_removed:
            errors.append("GENERATED_ROOT_REMAINS")

    checks = {
        "database_process_stopped": database_process_stopped,
        "generated_root_removed": generated_root_removed,
        "ports_closed": ports_closed,
    }
    green = all(checks.values()) and not errors
    teardown_body = {
        "version": "pdh3-local-canary-teardown-v2",
        "status": "GREEN" if green else "BLOCKED",
        "candidate_commit": CANDIDATE,
        "packet_sha256": packet_hash,
        **checks,
        "open_ports": open_ports,
        "errors": errors,
        "workload_exception": (
            None
            if workload_exception is None
            else {
                "type": type(workload_exception).__name__,
                "message": str(workload_exception)[:500],
            }
        ),
    }
    teardown_receipt = dict(
        teardown_body, receipt_sha256=digest(teardown_body)
    )
    atomic_write(output / "teardown.json", canonical(teardown_receipt))
    return teardown_receipt


def verified_teardown_receipt(output: Path, packet_hash: str) -> dict[str, Any]:
    path = output / "teardown.json"
    try:
        receipt = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise CanaryError("TEARDOWN_RECEIPT_UNREADABLE") from exc
    if not isinstance(receipt, dict):
        raise CanaryError("TEARDOWN_RECEIPT_INVALID")
    claimed_hash = receipt.get("receipt_sha256")
    body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if (
        receipt.get("status") != "GREEN"
        or receipt.get("packet_sha256") != packet_hash
        or claimed_hash != digest(body)
        or not all(
            receipt.get(key) is True
            for key in (
                "database_process_stopped",
                "generated_root_removed",
                "ports_closed",
            )
        )
        or receipt.get("errors") != []
    ):
        raise CanaryError("TEARDOWN_RECEIPT_NOT_GREEN")
    return receipt


def publish_green_result(
    output: Path,
    packet_hash: str,
    pending_result: dict[str, Any],
) -> dict[str, Any]:
    """Publish terminal GREEN last, after teardown and manifest are durable."""
    if (output / "failure.json").exists():
        raise CanaryError("TERMINAL_FAILURE_ALREADY_EXISTS")
    if (output / "result.json").exists():
        raise CanaryError("TERMINAL_RESULT_ALREADY_EXISTS")
    teardown_receipt = verified_teardown_receipt(output, packet_hash)
    result_body = {
        **pending_result,
        "teardown_receipt_sha256": teardown_receipt["receipt_sha256"],
    }
    result = dict(result_body, result_sha256=digest(result_body))
    result_raw = canonical(result)
    manifest_body = {
        "version": "pdh3-local-canary-evidence-manifest-v3",
        "candidate_commit": CANDIDATE,
        "packet_sha256": packet_hash,
        "result_sha256": result["result_sha256"],
        "teardown_receipt_sha256": teardown_receipt["receipt_sha256"],
        "files": {
            "result.json": digest(result_raw),
            "teardown.json": file_sha256(output / "teardown.json"),
            **{
                path.name: file_sha256(path)
                for path in sorted(output.glob("stage-c*.json"))
            },
        },
    }
    evidence_manifest = dict(
        manifest_body, manifest_sha256=digest(manifest_body)
    )
    atomic_write(output / "manifest.json", canonical(evidence_manifest))
    # No filesystem operation follows this terminal commit in the success path.
    atomic_write(output / "result.json", result_raw)
    return result


def publish_blocked_failure(
    output: Path,
    packet: Path,
    exc: BaseException,
) -> None:
    """Ensure a current invocation exposes exactly one terminal outcome."""
    output.mkdir(parents=True, exist_ok=True)
    for stale_success in (output / "result.json", output / "manifest.json"):
        if stale_success.is_file():
            stale_success.unlink()
    if (output / "result.json").exists():
        raise CanaryError("TERMINAL_RESULT_COULD_NOT_BE_WITHHELD")
    teardown_path = output / "teardown.json"
    teardown_value = (
        json.loads(teardown_path.read_bytes()) if teardown_path.is_file() else None
    )
    reason = str(exc) if isinstance(exc, CanaryError) else type(exc).__name__
    failure_body = {
        "version": "pdh3-local-canary-failure-v2",
        "status": "BLOCKED",
        "candidate_commit": CANDIDATE,
        "plan_sha256": PLAN_SHA256,
        "packet_sha256": file_sha256(packet) if packet.is_file() else None,
        "failure_class": reason,
        "exception_type": type(exc).__name__,
        "teardown_receipt_sha256": (
            teardown_value.get("receipt_sha256")
            if isinstance(teardown_value, dict)
            else None
        ),
        "teardown_file_sha256": (
            file_sha256(teardown_path) if teardown_path.is_file() else None
        ),
        "stage_receipts": {
            path.name: file_sha256(path)
            for path in sorted(output.glob("stage-c*.json"))
        },
    }
    atomic_write(
        output / "failure.json",
        canonical(dict(failure_body, receipt_sha256=digest(failure_body))),
    )


def execute(output: Path, packet: Path) -> dict[str, Any]:
    if output.exists():
        raise CanaryError("OUTPUT_ROOT_EXISTS")
    output.mkdir(parents=True)
    binary = find_cockroach()
    binary_hash = file_sha256(binary)
    packet_hash = file_sha256(packet)
    expected_packet_hash = os.environ.get("PDH3_PACKET_SHA256")
    if expected_packet_hash is None or packet_hash != expected_packet_hash:
        raise CanaryError("PACKET_HASH_BINDING_INVALID")
    root = Path(tempfile.mkdtemp(prefix="ck-pdh3-local-r1.", dir="/private/tmp"))
    fake_home = root / "empty-home"
    temp = root / "temp"
    store = root / "store"
    generated = root / "generated"
    for path in (fake_home, temp):
        path.mkdir()
    env = scrubbed_env(fake_home)
    port = reserve_port()
    http_port = reserve_port()
    while http_port == port:
        http_port = reserve_port()
    process: subprocess.Popen[bytes] | None = None
    log_handle: Any | None = None
    pending_result: dict[str, Any] | None = None
    teardown_receipt: dict[str, Any] | None = None
    try:
        verifier = run_verifier_campaign(root, env)
        process, log_handle = start_database(
            binary, root, port, http_port, env, append_log=False
        )
        sql(binary, port, "CREATE DATABASE cockroach_kernel", env=env)
        apply_file(
            binary,
            port,
            "cockroach_kernel",
            BASE / "p9-cloud/migrations/001_cloud.sql",
            env=env,
        )
        apply_file(
            binary,
            port,
            "cockroach_kernel",
            BASE / "p9-cloud/migrations/003_collision_safe_vector_digest.sql",
            env=env,
        )
        sql(
            binary,
            port,
            "CREATE TABLE ck.pdh3_acknowledged_writes "
            "(ack_id STRING PRIMARY KEY, created_at TIMESTAMPTZ NOT NULL);"
            "CREATE TABLE ck.pdh3_counter "
            "(id STRING PRIMARY KEY, value INT8 NOT NULL);"
            "INSERT INTO ck.pdh3_counter VALUES ('shared',0);"
            "CREATE TABLE ck.pdh3_replay_control (replay_id STRING PRIMARY KEY);",
            env=env,
            database="cockroach_kernel",
        )
        manifest = build_dataset(generated)
        insert_metrics = insert_dataset(binary, port, generated, manifest, env)
        expected_counts = (
            manifest["counts"]["tasks"],
            manifest["counts"]["events"],
            manifest["counts"]["receipts"],
            manifest["counts"]["vectors"],
        )
        count_sql = (
            "SELECT "
            f"(SELECT count(*) FROM ck.tasks WHERE campaign_id='{CAMPAIGN_ID}'),"
            f"(SELECT count(*) FROM ck.trajectory_events WHERE task_id LIKE '{CAMPAIGN_ID}-%'),"
            f"(SELECT count(*) FROM ck.receipts WHERE task_id LIKE '{CAMPAIGN_ID}-%'),"
            f"(SELECT count(*) FROM ck.context_vectors WHERE task_id LIKE '{CAMPAIGN_ID}-%')"
        )
        initial_counts = parse_count_tuple(
            sql(
                binary,
                port,
                count_sql,
                env=env,
                database="cockroach_kernel",
            ),
            4,
        )
        if initial_counts != expected_counts:
            raise CanaryError("INITIAL_COUNTS_MISMATCH")
        wrong_link_count = parse_last_integer(
            sql(
                binary,
                port,
                "SELECT count(*) FROM ck.context_vectors v "
                "JOIN ck.trajectory_events e ON e.event_hash=v.event_hash "
                "WHERE v.task_id != e.task_id",
                env=env,
                database="cockroach_kernel",
            )
        )
        if wrong_link_count != 0:
            raise CanaryError("VECTOR_TASK_CROSS_CONTAMINATION")
        query_files = build_query_files(root)
        stages: list[dict[str, Any]] = []
        restart_receipt: dict[str, Any] | None = None
        for concurrency in STAGES:
            stage = run_stage(
                binary, port, query_files, root, concurrency, env
            )
            stage_body = {
                "version": "pdh3-local-canary-stage-v2",
                "candidate_commit": CANDIDATE,
                "packet_sha256": packet_hash,
                **stage,
            }
            stage_receipt = dict(
                stage_body, receipt_sha256=digest(stage_body)
            )
            atomic_write(
                output / f"stage-c{concurrency}.json",
                canonical(stage_receipt),
            )
            stages.append(stage)
            if not stage["green"]:
                failed_checks = sorted(
                    name for name, passed in stage["checks"].items() if not passed
                )
                raise CanaryError(
                    f"CONCURRENCY_STAGE_NOT_GREEN:{concurrency}:"
                    + ",".join(failed_checks)
                )
            if concurrency == 50:
                counts_before_crash = parse_count_tuple(
                    sql(
                        binary,
                        port,
                        count_sql,
                        env=env,
                        database="cockroach_kernel",
                    ),
                    4,
                )
                crash_returncode = stop_database(process, log_handle, crash=True)
                process = None
                log_handle = None
                process, log_handle = start_database(
                    binary, root, port, http_port, env, append_log=True
                )
                counts_after_restart = parse_count_tuple(
                    sql(
                        binary,
                        port,
                        count_sql,
                        env=env,
                        database="cockroach_kernel",
                    ),
                    4,
                )
                restart_receipt = {
                    "crash_signal": "SIGKILL",
                    "crash_returncode": crash_returncode,
                    "counts_before_crash": list(counts_before_crash),
                    "counts_after_restart": list(counts_after_restart),
                    "acknowledged_rows_after_restart": parse_last_integer(
                        sql(
                            binary,
                            port,
                            "SELECT count(*) FROM ck.pdh3_acknowledged_writes",
                            env=env,
                            database="cockroach_kernel",
                        )
                    ),
                    "green": counts_after_restart == counts_before_crash,
                }
                if not restart_receipt["green"]:
                    raise CanaryError("CRASH_RESTART_ACKNOWLEDGED_WRITE_LOSS")
        final_counts = parse_count_tuple(
            sql(
                binary,
                port,
                count_sql,
                env=env,
                database="cockroach_kernel",
            ),
            4,
        )
        if final_counts != expected_counts:
            raise CanaryError("FINAL_COUNTS_MISMATCH")
        rollback_id = CAMPAIGN_ID + "-rollback-control"
        rollback_raw = sql(
            binary,
            port,
            "BEGIN;"
            "INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash)"
            f" VALUES ('{rollback_id}','{CAMPAIGN_ID}','{{}}',"
            f"decode('{digest(b'rollback-task')}','hex'),"
            f"decode('{digest(b'rollback-state')}','hex'));"
            "ROLLBACK;"
            f"SELECT count(*) FROM ck.tasks WHERE task_id='{rollback_id}'",
            env=env,
            database="cockroach_kernel",
        )
        rollback_count = parse_last_integer(rollback_raw)
        if rollback_count != 0:
            raise CanaryError("ROLLBACK_CONTROL_FAILED")
        database_bytes_before_cleanup = tree_bytes(store)
        for row in json.loads((generated / "cleanup-manifest.json").read_bytes())[
            "batches"
        ]:
            apply_file(
                binary,
                port,
                "cockroach_kernel",
                generated / row["path"],
                env=env,
            )
        residue_counts = parse_count_tuple(
            sql(
                binary,
                port,
                count_sql,
                env=env,
                database="cockroach_kernel",
            ),
            4,
        )
        if residue_counts != (0, 0, 0, 0):
            raise CanaryError("CAMPAIGN_CLEANUP_RESIDUE")
        evidence_bytes = tree_bytes(root / "verifier-campaign") + sum(
            path.stat().st_size
            for path in root.glob("querybench-*")
            if path.is_file()
        )
        total_ops = sum(stage["total_operations"] for stage in stages)
        total_duration = sum(
            workload["summary"]["elapsed_seconds"]
            for stage in stages
            for workload in stage["workloads"].values()
        )
        trajectories = manifest["counts"]["tasks"]
        result_body = {
            "version": "pdh3-local-canary-result-v2",
            "status": "GREEN",
            "candidate_commit": CANDIDATE,
            "plan_sha256": PLAN_SHA256,
            "packet_sha256": packet_hash,
            "campaign_id": CAMPAIGN_ID,
            "synthetic_only": True,
            "network_scope": "LOOPBACK_ONLY",
            "paid_resources": False,
            "cloud_execution": False,
            "diagnostic_reporting_disabled": True,
            "cockroach_binary_sha256": binary_hash,
            "source_hashes": source_hashes(packet),
            "manifest_sha256": manifest["manifest_sha256"],
            "dataset_counts": manifest["counts"],
            "initial_counts": list(initial_counts),
            "final_counts": list(final_counts),
            "wrong_task_vector_links": wrong_link_count,
            "insert_metrics": insert_metrics,
            "verifier_campaign": verifier,
            "query_files": {
                kind: {
                    "query_names": value["query_names"],
                    "sha256": value["sha256"],
                }
                for kind, value in query_files.items()
            },
            "concurrency_stages": stages,
            "crash_restart": restart_receipt,
            "rollback_count": rollback_count,
            "residue_counts": list(residue_counts),
            "database_bytes_before_cleanup": database_bytes_before_cleanup,
            "evidence_bytes": evidence_bytes,
            "calibration": {
                "measured_operations": total_ops,
                "measured_stage_seconds": total_duration,
                "aggregate_operations_per_second": (
                    total_ops / total_duration if total_duration else 0
                ),
                "database_bytes_per_seeded_trajectory": (
                    database_bytes_before_cleanup / trajectories
                ),
                "evidence_bytes_per_measured_operation": (
                    evidence_bytes / total_ops if total_ops else 0
                ),
                "provider_hourly_price": None,
                "provider_total_cost_estimate": None,
                "cost_gate": "SEPARATE_EXACT_OPERATOR_AUTHORIZATION_REQUIRED",
            },
            "coverage": {
                "captured_and_valid_semantics": "43_FRESH_PROCESS_EXECUTIONS",
                "stale_replay_unsupported_unsafe": "43_FRESH_PROCESS_EXECUTIONS",
                "transaction_contention": "QUERYBENCH_CONTENDED_UPDATE",
                "crash_restart": "ONE_LOCAL_SIGKILL_AND_RESTART",
                "queue_backpressure": "FOUR_STEPPED_CONCURRENCY_STAGES",
                "cleanup": "CAMPAIGN_PREFIXED_ZERO_RESIDUE",
                "lambda_variations": "DEFERRED_TO_PAID_MEASURED_CAMPAIGN",
                "custody_interruption": "43_FRESH_PROCESS_EXECUTIONS",
            },
            "limitations": [
                "LOCAL_SINGLE_NODE_ONLY",
                "SYNTHETIC_ONLY",
                "NOT_PRODUCTION",
                "NOT_CLOUD_SCALE",
                "NO_EXTERNAL_TESTER",
                "NO_PAID_EXECUTION_AUTHORIZED",
                "NO_PROVIDER_COST_ESTIMATE_WITHOUT_LIVE_PRICING",
            ],
            "next_gate": "EXACT_PAID_COST_AND_LIFECYCLE_AUTHORIZATION",
        }
        pending_result = result_body
    finally:
        teardown_receipt = finalize_local_teardown(
            output=output,
            root=root,
            process=process,
            log_handle=log_handle,
            ports=(port, http_port),
            packet_hash=packet_hash,
            workload_exception=sys.exc_info()[1],
        )
        if teardown_receipt["status"] != "GREEN":
            raise CanaryError(
                "LOCAL_TEARDOWN_BLOCKED:"
                + ",".join(teardown_receipt["errors"])
            )
    if pending_result is None:
        raise CanaryError("RESULT_NOT_WRITTEN")
    return publish_green_result(output, packet_hash, pending_result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--packet", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_root.resolve()
    packet = args.packet.resolve()
    output_preexisted = output.exists()
    try:
        result = execute(output, packet)
    except Exception as exc:
        reason = str(exc) if isinstance(exc, CanaryError) else type(exc).__name__
        if not output_preexisted:
            publish_blocked_failure(output, packet, exc)
        print(canonical({"status": "BLOCKED", "failure_class": reason}).decode())
        return 2
    print(
        canonical(
            {
                "status": result["status"],
                "result_sha256": result["result_sha256"],
            }
        ).decode("utf-8")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
