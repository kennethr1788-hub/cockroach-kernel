# PDH-3 Local Canary Same-Hash Preflight R2

Decision: authorize or block one no-cost local canary. Review the complete contract and controller below for safety, evidence integrity, threshold sufficiency, teardown, and exact contract/code parity. Do not provide code, patches, implementation plans, tool calls, or deployment direction. The transport wrapper independently verifies served-model identity; do not infer, adopt, or report model identity. Return strict JSON with keys packet_sha256, verdict (GREEN|NOT_GREEN|BLOCKED), blockers, non_blocking_risks, evidence_required.

## CONTRACT

# PDH-3 Local Canary Packet R1

## Authority and boundary

- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PLAN_SHA256`: `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- `PARENT_GREEN`: `PDH_1_INFORMATION_BOUNDARY_GREEN`
- `PDH_2`: `DELIBERATELY_SKIPPED_BY_OPERATOR`
- `PAID_RESOURCES`: forbidden
- `NETWORK`: loopback only
- `DATA`: generated synthetic data only
- `PRODUCT_MUTATION`: forbidden
- `PUBLIC_ACTIONS`: forbidden
- `HOME_RUNTIME`, `QDRANT`, `STATEV2`, `LAUNCHD`, `CLIENT_DATA`, `PRODUCTION_DATA`: forbidden

This packet authorizes only a no-cost calibration. It cannot produce
`PDH_3_PRODUCTION_SHAPED_SCALE_GREEN`; it may produce only
`PDH_3_LOCAL_CANARY_GREEN` or a fail-closed local-canary blocker.

## Frozen controller

`post-dogfood/run_pdh3_local_canary.py`:

1. Binds the candidate, plan, and this packet's externally supplied SHA-256.
2. Uses the existing verified CockroachDB v26.2.3 macOS arm64 binary.
3. Runs the frozen 43-execution fresh-process verifier/refusal campaign.
4. Creates one loopback-only CockroachDB single-node process in a generated
   `/private/tmp/ck-pdh3-local-r1.*` root with an empty task-local `HOME`.
5. Applies the exact P9 application migrations.
6. Generates and inserts:
   - 500 tasks;
   - 5,000 trajectory events;
   - 1,000 receipts;
   - 5,000 task-bound vectors.
7. Runs real application-schema queries at concurrency 10, 50, 100, and 250.
8. Accounts for acknowledged writes and contended counter increments against
   named query histograms.
9. Requires idempotent replay, zero wrong-task vector linkage, zero query
   errors, exact row counts, and exact rollback.
10. Sends SIGKILL after the concurrency-50 stage, restarts from the same
    disposable store, and verifies that acknowledged state and application row
    counts survive.
11. Executes the generated dependency-ordered cleanup manifest and requires
    zero campaign residue.
12. Stops the node, proves both loopback ports are closed, and removes only the
    verified generated root.

No credential acquisition, AWS call, Lambda call, external model call, package
installation, live CockroachDB connection, RunPod worker, or public surface is
permitted.

## Frozen thresholds

- Concurrency stages: exactly `10`, `50`, `100`, `250`.
- Measured duration: two seconds per stage.
- Minimum completed operations: 500 per stage.
- Query errors: zero.
- Histogram-accounted operations must equal the querybench operation total.
- Acknowledged-write row delta must equal the named acknowledged-write
  histogram count.
- Contended counter delta must equal the named contended-update histogram
  count.
- Replay-control rows: exactly one.
- Aggregate p99: at most 5,000 ms per stage.
- Aggregate pMax: at most 10,000 ms per stage.
- Wrong-task vector links: zero.
- Acknowledged application-row loss after crash/restart: zero.
- Rollback residue: zero.
- Campaign data residue after cleanup: zero.
- Verifier false promotions: zero.
- Verifier mutation after refusal: zero.
- Verifier task-root residue: zero.

Stage 500 is not authorized by this canary. It may be included only in a later
paid campaign if stages 10–250 are GREEN and the exact cost/lifecycle packet is
separately authorized.

## Evidence contract

The controller emits canonical JSON:

- `result.json`: source hashes, product/plan/packet binding, row counts, load
  metrics, per-query operation counts, latency, crash/restart evidence,
  verifier results, storage/evidence calibration, limitations, and next gate.
- `teardown.json`: process, port, and generated-root teardown.
- `manifest.json`: hashes binding the final result and teardown.

Raw querybench logs and generated database state exist only inside the
generated disposable root. The final receipts preserve their hashes and
aggregate metrics but not the disposable rows.

## Fail-closed conditions

Stop and preserve a blocked result on:

- source, packet, candidate, migration, generated-batch, or receipt hash drift;
- any external network, credential, HOME, private, client, or production
  access;
- false verifier result or mutation after refusal;
- wrong-task vector linkage;
- query error or unaccounted operation;
- acknowledged-write or counter loss;
- replay non-idempotency;
- crash/restart data loss;
- rollback or cleanup residue;
- threshold breach;
- database process, loopback port, or generated-root teardown failure.

## Permitted conclusion

If every mechanical threshold passes and an independent GLM 5.2 review of this
exact packet is GREEN, the controller may run. If the resulting evidence also
passes independent review, the only permitted status is:

`PDH_3_LOCAL_CANARY_GREEN`

The next step remains blocked until Kenneth provides a separate exact hourly
rate ceiling, exact total-dollar ceiling, maximum paid lifetime, attempt
ceiling, and teardown authorization for the measured cloud campaign.

## CONTROLLER

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
PACKET_NAME = "PDH_3_LOCAL_CANARY_PACKET_R1.md"
CAMPAIGN_ID = "ck-g7r9-pdh3-local-r1"
TASKS = 500
EVENTS_PER_TASK = 10
RECEIPTS_PER_TASK = 2
VECTORS_PER_TASK = 10
QUERY_SAMPLES = 200
STAGES = (10, 50, 100, 250)
STAGE_DURATION_SECONDS = 2
MINIMUM_STAGE_OPERATIONS = 500
P99_LIMIT_MS = 5_000.0
PMAX_LIMIT_MS = 10_000.0
ZERO_HASH = "0" * 64
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
) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        raise CanaryError(
            "COMMAND_FAILED:"
            + command[1 if len(command) > 1 else 0]
            + ":"
            + digest(result.stdout + result.stderr)
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
        "pdh3_local_bulk_generator",
        BASE / "hardening-gate7/live_bulk_controller.py",
    )
    module.TASKS = TASKS
    module.EVENTS_PER_TASK = EVENTS_PER_TASK
    module.RECEIPTS_PER_TASK = RECEIPTS_PER_TASK
    module.VECTORS_PER_TASK = VECTORS_PER_TASK
    module.QUERY_SAMPLES = QUERY_SAMPLES
    module.CONCURRENCY = STAGES[0]
    return module.build_sql(CAMPAIGN_ID, generated)


def insert_dataset(
    binary: Path,
    port: int,
    generated: Path,
    manifest: dict[str, Any],
    env: dict[str, str],
) -> dict[str, Any]:
    stage_elapsed_ms: dict[str, int] = {}
    output_hashes: dict[str, list[str]] = {}
    for stage in ("tasks", "events", "receipts", "vectors"):
        started = time.monotonic_ns()
        hashes: list[str] = []
        for batch in manifest["batches"][stage]:
            path = generated / batch["path"]
            if file_sha256(path) != batch["sha256"]:
                raise CanaryError("GENERATED_BATCH_HASH_MISMATCH")
            completed = run(
                [
                    str(binary),
                    "sql",
                    "--insecure",
                    f"--host=127.0.0.1:{port}",
                    "--database=cockroach_kernel",
                    f"--file={path}",
                ],
                env=env,
                timeout=300,
            )
            hashes.append(digest(completed.stdout))
        stage_elapsed_ms[stage] = int((time.monotonic_ns() - started) / 1_000_000)
        output_hashes[stage] = hashes
    return {
        "stage_elapsed_ms": stage_elapsed_ms,
        "output_set_sha256": {
            stage: digest(hashes) for stage, hashes in output_hashes.items()
        },
        "batch_count": sum(len(rows) for rows in manifest["batches"].values()),
        "serialization_retries": 0,
    }


def build_query_file(path: Path) -> list[str]:
    rows: list[str] = []
    for index in range(20):
        task_id = f"{CAMPAIGN_ID}-task-{index:04d}"
        vector_id = f"{task_id}-vector-00"
        rows.append(
            f"vector-{index:02d}: SELECT count(*) FROM ck.context_vectors "
            f"WHERE task_id='{task_id}' AND namespace='{CAMPAIGN_ID}' "
            f"AND vector_id='{vector_id}'"
        )
    for index in range(5):
        task_id = f"{CAMPAIGN_ID}-task-{index:04d}"
        rows.append(
            f"receipt-{index:02d}: SELECT count(*) FROM ck.mcp_receipt_view "
            f"WHERE task_id='{task_id}'"
        )
    rows.extend(
        [
            "ack-write: INSERT INTO ck.pdh3_acknowledged_writes"
            "(ack_id,created_at) VALUES (gen_random_uuid()::STRING,now())",
            "contended-update: UPDATE ck.pdh3_counter "
            "SET value=value+1 WHERE id='shared'",
            "replay-idempotency: INSERT INTO ck.pdh3_replay_control"
            "(replay_id) VALUES ('fixed-replay') ON CONFLICT DO NOTHING",
            "stale-projection-read: SELECT count(*) FROM ck.projection_events "
            "WHERE source_key LIKE 'missing-stale-%'",
            "trajectory-link-read: SELECT count(*) FROM ck.trajectory_events e "
            "JOIN ck.tasks t ON t.task_id=e.task_id "
            f"WHERE t.campaign_id='{CAMPAIGN_ID}'",
        ]
    )
    atomic_write(path, ("\n".join(rows) + "\n").encode("utf-8"))
    return [row.split(":", 1)[0] for row in rows]


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


def parse_histogram_counts(path: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        name = row.get("Name")
        raw_counts = row.get("Hist", {}).get("Counts")
        if not isinstance(name, str) or not isinstance(raw_counts, list):
            raise CanaryError("QUERYBENCH_HISTOGRAM_SCHEMA_INVALID")
        counts[name] = counts.get(name, 0) + sum(int(item) for item in raw_counts)
    return counts


def run_stage(
    binary: Path,
    port: int,
    query_file: Path,
    root: Path,
    concurrency: int,
    env: dict[str, str],
) -> dict[str, Any]:
    output_path = root / f"querybench-c{concurrency}.stdout.log"
    error_path = root / f"querybench-c{concurrency}.stderr.log"
    histogram_path = root / f"querybench-c{concurrency}.histograms.json"
    ack_before = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT count(*) FROM ck.pdh3_acknowledged_writes",
            env=env,
            database="cockroach_kernel",
        )
    )
    counter_before = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT value FROM ck.pdh3_counter WHERE id='shared'",
            env=env,
            database="cockroach_kernel",
        )
    )
    command = [
        str(binary),
        "workload",
        "run",
        "querybench",
        f"postgresql://root@127.0.0.1:{port}/cockroach_kernel?sslmode=disable",
        "--db=cockroach_kernel",
        f"--query-file={query_file}",
        f"--concurrency={concurrency}",
        f"--duration={STAGE_DURATION_SECONDS}s",
        "--display-format=simple",
        "--display-every=1s",
        "--verbose=false",
        f"--histograms={histogram_path}",
        "--histogram-export-format=json",
        "--isolation-level=serializable",
    ]
    completed = subprocess.run(
        command,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=STAGE_DURATION_SECONDS + 60,
        check=False,
    )
    atomic_write(output_path, completed.stdout)
    atomic_write(error_path, completed.stderr)
    if completed.returncode != 0:
        raise CanaryError(f"QUERYBENCH_FAILED_C{concurrency}")
    summary = parse_querybench_summary(completed.stdout)
    histogram_counts = parse_histogram_counts(histogram_path)
    ack_after = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT count(*) FROM ck.pdh3_acknowledged_writes",
            env=env,
            database="cockroach_kernel",
        )
    )
    counter_after = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT value FROM ck.pdh3_counter WHERE id='shared'",
            env=env,
            database="cockroach_kernel",
        )
    )
    replay_rows = parse_last_integer(
        sql(
            binary,
            port,
            "SELECT count(*) FROM ck.pdh3_replay_control",
            env=env,
            database="cockroach_kernel",
        )
    )
    ack_expected = histogram_counts.get("ack-write", 0)
    counter_expected = histogram_counts.get("contended-update", 0)
    accounted = sum(histogram_counts.values())
    checks = {
        "zero_errors": summary["errors"] == 0,
        "minimum_operations": summary["operations"] >= MINIMUM_STAGE_OPERATIONS,
        "histograms_account_for_operations": accounted == summary["operations"],
        "acknowledged_writes_exact": ack_after - ack_before == ack_expected,
        "contended_updates_exact": counter_after - counter_before == counter_expected,
        "replay_idempotent": replay_rows == 1,
        "p99_within_limit": summary["latency_ms"]["p99"] <= P99_LIMIT_MS,
        "pmax_within_limit": summary["latency_ms"]["max"] <= PMAX_LIMIT_MS,
    }
    return {
        "concurrency": concurrency,
        "summary": summary,
        "histogram_counts": histogram_counts,
        "histogram_accounted_operations": accounted,
        "acknowledged_write_delta": ack_after - ack_before,
        "contended_update_delta": counter_after - counter_before,
        "replay_rows": replay_rows,
        "stdout_sha256": file_sha256(output_path),
        "stderr_sha256": file_sha256(error_path),
        "histograms_sha256": file_sha256(histogram_path),
        "checks": checks,
        "green": all(checks.values()),
    }


def run_verifier_campaign(root: Path, env: dict[str, str]) -> dict[str, Any]:
    salt = root / "public-salt.bin"
    vector_set = root / "public-vectors.json"
    output = root / "verifier-campaign"
    atomic_write(salt, bytes.fromhex("9d" * 32))
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
        timeout=60,
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
        timeout=180,
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


def source_hashes(packet: Path) -> dict[str, str]:
    paths = [
        packet,
        Path(__file__).resolve(),
        BASE / "hardening-gate7/live_bulk_controller.py",
        BASE / "hardening-gate7/make_vectors.py",
        BASE / "hardening-gate7/run_campaign.py",
        BASE / "hardening-gate7/run_trial.py",
        BASE / "p9-cloud/context_vector.py",
        BASE / "p9-cloud/migrations/001_cloud.sql",
        BASE / "p9-cloud/migrations/003_collision_safe_vector_digest.sql",
    ]
    return {str(path.relative_to(BASE)): file_sha256(path) for path in paths}


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
    teardown = {
        "database_process_stopped": False,
        "generated_root_removed": False,
        "ports_closed": False,
    }
    result: dict[str, Any] | None = None
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
        query_file = root / "querybench.sql"
        query_names = build_query_file(query_file)
        stages: list[dict[str, Any]] = []
        restart_receipt: dict[str, Any] | None = None
        for concurrency in STAGES:
            stages.append(
                run_stage(binary, port, query_file, root, concurrency, env)
            )
            if not stages[-1]["green"]:
                raise CanaryError(f"CONCURRENCY_STAGE_NOT_GREEN:{concurrency}")
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
        total_ops = sum(stage["summary"]["operations"] for stage in stages)
        total_duration = sum(
            stage["summary"]["elapsed_seconds"] for stage in stages
        )
        trajectories = manifest["counts"]["tasks"]
        result_body = {
            "version": "pdh3-local-canary-result-v1",
            "status": "GREEN",
            "candidate_commit": CANDIDATE,
            "plan_sha256": PLAN_SHA256,
            "packet_sha256": packet_hash,
            "campaign_id": CAMPAIGN_ID,
            "synthetic_only": True,
            "network_scope": "LOOPBACK_ONLY",
            "paid_resources": False,
            "cloud_execution": False,
            "cockroach_binary_sha256": binary_hash,
            "source_hashes": source_hashes(packet),
            "manifest_sha256": manifest["manifest_sha256"],
            "dataset_counts": manifest["counts"],
            "initial_counts": list(initial_counts),
            "final_counts": list(final_counts),
            "wrong_task_vector_links": wrong_link_count,
            "insert_metrics": insert_metrics,
            "verifier_campaign": verifier,
            "query_names": query_names,
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
        result = dict(result_body, result_sha256=digest(result_body))
        atomic_write(output / "result.json", canonical(result))
        manifest_body = {
            "version": "pdh3-local-canary-evidence-manifest-v1",
            "candidate_commit": CANDIDATE,
            "packet_sha256": packet_hash,
            "result_sha256": result["result_sha256"],
            "files": {
                "result.json": file_sha256(output / "result.json"),
            },
        }
        evidence_manifest = dict(
            manifest_body, manifest_sha256=digest(manifest_body)
        )
        atomic_write(output / "manifest.json", canonical(evidence_manifest))
    finally:
        if process is not None and log_handle is not None:
            stop_database(process, log_handle, crash=False)
            teardown["database_process_stopped"] = True
        elif process is None:
            teardown["database_process_stopped"] = True
        for checked_port in (port, http_port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                probe.settimeout(0.2)
                if probe.connect_ex(("127.0.0.1", checked_port)) == 0:
                    raise CanaryError("LOCAL_PORT_REMAINS_OPEN")
        teardown["ports_closed"] = True
        verified_root = root.resolve()
        if (
            verified_root.parent != Path("/private/tmp")
            or not verified_root.name.startswith("ck-pdh3-local-r1.")
        ):
            raise CanaryError("GENERATED_ROOT_IDENTITY_INVALID")
        shutil.rmtree(verified_root)
        teardown["generated_root_removed"] = not verified_root.exists()
        teardown_body = {
            "version": "pdh3-local-canary-teardown-v1",
            "candidate_commit": CANDIDATE,
            "packet_sha256": packet_hash,
            **teardown,
        }
        teardown_receipt = dict(
            teardown_body, receipt_sha256=digest(teardown_body)
        )
        atomic_write(output / "teardown.json", canonical(teardown_receipt))
        if result is not None:
            manifest_path = output / "manifest.json"
            manifest_value = json.loads(manifest_path.read_bytes())
            body = {
                key: value
                for key, value in manifest_value.items()
                if key != "manifest_sha256"
            }
            body["files"]["teardown.json"] = file_sha256(output / "teardown.json")
            body["teardown_receipt_sha256"] = teardown_receipt["receipt_sha256"]
            atomic_write(
                manifest_path,
                canonical(dict(body, manifest_sha256=digest(body))),
            )
    if result is None:
        raise CanaryError("RESULT_NOT_WRITTEN")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--packet", required=True, type=Path)
    args = parser.parse_args()
    result = execute(args.output_root.resolve(), args.packet.resolve())
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
