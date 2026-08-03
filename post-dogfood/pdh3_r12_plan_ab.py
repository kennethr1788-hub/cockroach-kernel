#!/usr/bin/env python3
"""Representative-cardinality CockroachDB plan A/B for PDH-3 R12 PF-2.

Each scale uses a fresh generated root and an isolated single-node CockroachDB
v26.2.3 process.  Current plans and read-only results are frozen before either
candidate index is created.  The script never edits the product migration.
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
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable


BASE = Path(__file__).resolve().parents[1]
PLAN_SHA256 = "a1214b4779fe1495de219ed0033421ac810390641cd97742deb61cd3957df3d9"
SCALES = (10_000, 50_000, 100_000)
SEED_BATCH_TASKS = 5_000
PROJECTION_BATCH_TASKS = 5_000
SCALE_DEADLINE_SECONDS = 3_600
SEED_TAIL_RESERVE_SECONDS = 900
PROJECTION_TAIL_RESERVE_SECONDS = 600
RECEIPT_INDEX_DDL = (
    "CREATE INDEX receipts_task_id_idx ON ck.receipts(task_id) "
    "STORING(status,event_hash)"
)
PROJECTION_INDEX_DDL = (
    "CREATE INDEX projection_events_source_key_idx "
    "ON ck.projection_events(source_key)"
)


class PlanABError(RuntimeError):
    """Stable PF-2 error."""


def load_canary() -> Any:
    path = BASE / "post-dogfood/run_pdh3_local_canary.py"
    spec = importlib.util.spec_from_file_location("pdh3_r12_pf2_canary", path)
    if spec is None or spec.loader is None:
        raise PlanABError("CANARY_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_scale_campaign() -> Any:
    """Load the proven batched seeder without duplicating its custody rules."""
    path = BASE / "post-dogfood/run_pdh3_scale_campaign.py"
    module_root = str(path.parent)
    if module_root not in sys.path:
        sys.path.insert(0, module_root)
    spec = importlib.util.spec_from_file_location("pdh3_r12_pf2_scale", path)
    if spec is None or spec.loader is None:
        raise PlanABError("SCALE_CAMPAIGN_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


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
    value = {**body, field: digest(body)}
    atomic_write(path, canonical(value))
    return value


def preserve_database_log(
    root: Path, trial_output: Path, teardown: dict[str, Any]
) -> None:
    database_log = root / "cockroach.log"
    if database_log.is_file():
        copied_log = trial_output / "cockroach.log"
        shutil.copyfile(database_log, copied_log)
        teardown["database_log_sha256"] = file_sha256(copied_log)


def full_scan(plan: str) -> bool:
    lowered = plan.lower()
    return "full scan" in lowered or bool(
        re.search(r"spans?\s*:\s*(?:all|full)", lowered)
    )


def query_definitions(campaign: str, width: int = 6) -> dict[str, str]:
    queries: dict[str, str] = {}
    for index in range(20):
        task = f"{campaign}-task-{index:0{width}d}"
        vector = task + "-vector-00"
        queries[f"vector-{index:02d}"] = (
            "SELECT count(*) FROM ck.context_vectors "
            f"WHERE task_id='{task}' AND namespace='{campaign}' "
            f"AND vector_id='{vector}'"
        )
    for index in range(5):
        task = f"{campaign}-task-{index:0{width}d}"
        queries[f"receipt-{index:02d}"] = (
            "SELECT count(*) FROM ck.mcp_receipt_view " f"WHERE task_id='{task}'"
        )
    queries["stale-projection-read"] = (
        "SELECT count(*) FROM ck.projection_events "
        "WHERE source_key LIKE 'missing-stale-%'"
    )
    task = f"{campaign}-task-{0:0{width}d}"
    queries["trajectory-link-read"] = (
        "SELECT count(*) FROM ck.trajectory_events e "
        "JOIN ck.tasks t ON t.task_id=e.task_id "
        f"WHERE t.task_id='{task}' AND t.campaign_id='{campaign}'"
    )
    return queries


def run_sql(
    canary: Any,
    binary: Path,
    port: int,
    env: dict[str, str],
    statement: str,
    *,
    timeout: int = 300,
) -> tuple[bytes, float]:
    started = time.monotonic()
    command = [
        str(binary),
        "sql",
        "--insecure",
        f"--host=127.0.0.1:{port}",
        "--format=tsv",
        "--database=cockroach_kernel",
        "--execute",
        statement,
    ]
    try:
        completed = subprocess.run(
            command,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise PlanABError("SQL_TIMEOUT:" + digest(statement.encode())) from exc
    if completed.returncode != 0:
        tail = completed.stderr.decode("utf-8", "replace")[-1000:].replace("\n", " ")
        raise PlanABError(
            "SQL_FAILED:"
            + digest(statement.encode())
            + ":stderr="
            + digest(completed.stderr)
            + ":tail="
            + tail
        )
    return completed.stdout, time.monotonic() - started


def projection_seed_statement(campaign: str, start: int, stop: int) -> str:
    campaign_literal = "'" + campaign.replace("'", "''") + "'"
    task = f"{campaign_literal} || '-task-' || lpad(i::STRING,6,'0')"
    return (
        "INSERT INTO ck.projection_events"
        "(projection_id,source_table,source_key,receipt_hash,sequence,projected_json,projection_hash) "
        f"SELECT {campaign_literal} || '-projection-' || i::STRING,'tasks',{task},"
        f"decode(sha256(({campaign_literal} || '-receipt-' || i::STRING || '-0')::BYTES),'hex'),"
        "0,jsonb_build_object('synthetic',true),"
        f"decode(sha256(({campaign_literal} || '-projection-' || i::STRING)::BYTES),'hex') "
        f"FROM generate_series({start},{stop - 1}) g(i) "
        "ON CONFLICT (projection_id) DO NOTHING"
    )


def secondary_receipt_seed_statement(campaign: str, start: int, stop: int) -> str:
    campaign_literal = "'" + campaign.replace("'", "''") + "'"
    task = f"{campaign_literal} || '-task-' || lpad(i::STRING,6,'0')"
    event_hash = (
        f"decode(sha256(({campaign_literal} || '-event-' || i::STRING || '-0')::BYTES),'hex')"
    )
    return (
        "INSERT INTO ck.receipts"
        "(receipt_hash,task_id,event_hash,status,receipt_json) "
        f"SELECT decode(sha256(({campaign_literal} || '-receipt-' || i::STRING || '-1')::BYTES),'hex'),"
        f"{task},{event_hash},'SEALED',jsonb_build_object('synthetic',true,'receipt',1) "
        f"FROM generate_series({start},{stop - 1}) g(i) "
        "ON CONFLICT (receipt_hash) DO NOTHING"
    )


def secondary_receipt_reconciliation_statement(
    campaign: str, start: int, stop: int
) -> str:
    campaign_literal = "'" + campaign.replace("'", "''") + "'"
    task = f"{campaign_literal} || '-task-' || lpad(i::STRING,6,'0')"
    expected = (
        "SELECT "
        f"decode(sha256(({campaign_literal} || '-receipt-' || i::STRING || '-1')::BYTES),'hex') AS receipt_hash,"
        f"{task} AS task_id,"
        f"decode(sha256(({campaign_literal} || '-event-' || i::STRING || '-0')::BYTES),'hex') AS event_hash,"
        "'SEALED' AS status,jsonb_build_object('synthetic',true,'receipt',1) AS receipt_json "
        f"FROM generate_series({start},{stop - 1}) g(i)"
    )
    mismatch = (
        "a.task_id IS DISTINCT FROM e.task_id OR "
        "a.event_hash IS DISTINCT FROM e.event_hash OR "
        "a.status IS DISTINCT FROM e.status OR "
        "a.receipt_json IS DISTINCT FROM e.receipt_json"
    )
    return (
        f"WITH expected AS ({expected}) SELECT count(a.receipt_hash),"
        f"count(*) FILTER (WHERE a.receipt_hash IS NOT NULL AND ({mismatch})) "
        "FROM expected e LEFT JOIN ck.receipts a ON a.receipt_hash=e.receipt_hash"
    )


def seed_secondary_receipts(
    scale: Any,
    binary: Path,
    port: int,
    env: dict[str, str],
    journal: Any,
    *,
    campaign: str,
    tasks: int,
    deadline: float,
) -> dict[str, Any]:
    return seed_plan_specific_batches(
        scale,
        binary,
        port,
        env,
        journal,
        campaign=campaign,
        tasks=tasks,
        deadline=deadline,
        stage="secondary_receipt",
        statement_factory=secondary_receipt_seed_statement,
        reconciliation_factory=secondary_receipt_reconciliation_statement,
    )


def projection_reconciliation_statement(
    campaign: str, start: int, stop: int
) -> str:
    campaign_literal = "'" + campaign.replace("'", "''") + "'"
    task = f"{campaign_literal} || '-task-' || lpad(i::STRING,6,'0')"
    expected = (
        "SELECT "
        f"{campaign_literal} || '-projection-' || i::STRING AS projection_id,"
        "'tasks' AS source_table,"
        f"{task} AS source_key,"
        f"decode(sha256(({campaign_literal} || '-receipt-' || i::STRING || '-0')::BYTES),'hex') AS receipt_hash,"
        "0::INT8 AS sequence,jsonb_build_object('synthetic',true) AS projected_json,"
        f"decode(sha256(({campaign_literal} || '-projection-' || i::STRING)::BYTES),'hex') AS projection_hash "
        f"FROM generate_series({start},{stop - 1}) g(i)"
    )
    mismatch = (
        "a.source_table IS DISTINCT FROM e.source_table OR "
        "a.source_key IS DISTINCT FROM e.source_key OR "
        "a.receipt_hash IS DISTINCT FROM e.receipt_hash OR "
        "a.sequence IS DISTINCT FROM e.sequence OR "
        "a.projected_json IS DISTINCT FROM e.projected_json OR "
        "a.projection_hash IS DISTINCT FROM e.projection_hash"
    )
    return (
        f"WITH expected AS ({expected}) SELECT count(a.projection_id),"
        f"count(*) FILTER (WHERE a.projection_id IS NOT NULL AND ({mismatch})) "
        "FROM expected e LEFT JOIN ck.projection_events a "
        "ON a.projection_id=e.projection_id"
    )


def seed_projections(
    scale: Any,
    binary: Path,
    port: int,
    env: dict[str, str],
    journal: Any,
    *,
    campaign: str,
    tasks: int,
    deadline: float,
) -> dict[str, Any]:
    return seed_plan_specific_batches(
        scale,
        binary,
        port,
        env,
        journal,
        campaign=campaign,
        tasks=tasks,
        deadline=deadline,
        stage="projection",
        statement_factory=projection_seed_statement,
        reconciliation_factory=projection_reconciliation_statement,
    )


def seed_plan_specific_batches(
    scale: Any,
    binary: Path,
    port: int,
    env: dict[str, str],
    journal: Any,
    *,
    campaign: str,
    tasks: int,
    deadline: float,
    stage: str,
    statement_factory: Any,
    reconciliation_factory: Any,
) -> dict[str, Any]:
    statement_hashes: list[str] = []
    reconciliations: list[dict[str, Any]] = []
    retries = 0
    for start in range(0, tasks, PROJECTION_BATCH_TASKS):
        stop = min(tasks, start + PROJECTION_BATCH_TASKS)
        statement = statement_factory(campaign, start, stop)
        statement_hash = digest(statement.encode("utf-8"))
        completed = False
        for attempt in range(scale.MAX_SEED_ATTEMPTS):
            try:
                scale.sql(
                    binary,
                    port,
                    statement,
                    env=env,
                    timeout=scale.setup_timeout(
                        deadline,
                        scale.SETUP_SQL_TIMEOUT_SECONDS,
                        reserve_seconds=PROJECTION_TAIL_RESERVE_SECONDS,
                    ),
                    stage=f"pf2_{stage}_seed",
                    start=start,
                    stop=stop,
                )
                completed = True
            except scale.SqlOperationError as exc:
                if not exc.retryable:
                    raise
            raw = scale.sql(
                binary,
                port,
                reconciliation_factory(campaign, start, stop),
                env=env,
                timeout=scale.setup_timeout(
                    deadline,
                    scale.SETUP_SQL_TIMEOUT_SECONDS,
                    reserve_seconds=PROJECTION_TAIL_RESERVE_SECONDS,
                ),
                stage=f"pf2_{stage}_reconcile",
                start=start,
                stop=stop,
            )
            actual, mismatched = scale.parse_count_tuple(raw, 2)
            state = "EXACT" if actual == stop - start and mismatched == 0 else "MISMATCH"
            reconciliation = {
                "start": start,
                "stop": stop,
                "expected_rows": stop - start,
                "actual_rows": actual,
                "content_mismatches": mismatched,
                "state": state,
                "statement_sha256": statement_hash,
            }
            if state == "EXACT":
                completed = True
                reconciliations.append(reconciliation)
                break
            if actual not in (0, stop - start) or mismatched:
                raise PlanABError(f"PF2_{stage.upper()}_RECONCILIATION_MISMATCH")
            if attempt + 1 < scale.MAX_SEED_ATTEMPTS:
                retries += 1
                time.sleep(0.25 * (attempt + 1))
        if not completed:
            raise PlanABError(f"PF2_{stage.upper()}_BATCH_INCOMPLETE")
        statement_hashes.append(statement_hash)
        journal.emit(f"PF2_{stage.upper()}_BATCH", reconciliations[-1])
    return {
        "batch_tasks": PROJECTION_BATCH_TASKS,
        "stage": stage,
        "batches": len(reconciliations),
        "rows": tasks,
        "retries": retries,
        "statement_set_sha256": digest(statement_hashes),
        "reconciliations_sha256": digest(reconciliations),
        "green": all(row["state"] == "EXACT" for row in reconciliations),
    }


def capture_queries(
    canary: Any,
    binary: Path,
    port: int,
    env: dict[str, str],
    queries: dict[str, str],
    output: Path,
    label: str,
    *,
    deadline: float | None = None,
) -> dict[str, Any]:
    def remaining_timeout(cap: int = 300) -> int:
        if deadline is None:
            return cap
        available = deadline - time.monotonic() - 1
        if available < 1:
            raise PlanABError("QUERY_CAPTURE_DEADLINE_EXHAUSTED")
        return min(cap, max(1, int(available)))

    results: dict[str, Any] = {}
    for name, query in queries.items():
        plan_raw, plan_elapsed = run_sql(
            canary, binary, port, env, "EXPLAIN " + query,
            timeout=remaining_timeout(),
        )
        analyze_raw, analyze_elapsed = run_sql(
            canary, binary, port, env, "EXPLAIN ANALYZE (DISTSQL) " + query,
            timeout=remaining_timeout(),
        )
        result_raw, result_elapsed = run_sql(
            canary, binary, port, env, query, timeout=remaining_timeout()
        )
        plan_path = output / f"{label}-{name}.explain.txt"
        analyze_path = output / f"{label}-{name}.analyze.txt"
        atomic_write(plan_path, plan_raw)
        atomic_write(analyze_path, analyze_raw)
        results[name] = {
            "query_sha256": digest(query.encode()),
            "plan_sha256": digest(plan_raw),
            "analyze_sha256": digest(analyze_raw),
            "result_sha256": digest(result_raw),
            "full_scan": full_scan(plan_raw.decode("utf-8", "replace")),
            "analyze_full_scan": full_scan(analyze_raw.decode("utf-8", "replace")),
            "plan_elapsed_seconds": plan_elapsed,
            "analyze_elapsed_seconds": analyze_elapsed,
            "result_elapsed_seconds": result_elapsed,
        }
    return results


def table_evidence(
    canary: Any,
    binary: Path,
    port: int,
    env: dict[str, str],
    *,
    output: Path | None = None,
    label: str | None = None,
    deadline: float | None = None,
) -> dict[str, Any]:
    statements = {
        "receipts_indexes": "SHOW INDEXES FROM ck.receipts",
        "receipts_statistics": "SHOW STATISTICS FOR TABLE ck.receipts",
        "projection_indexes": "SHOW INDEXES FROM ck.projection_events",
        "projection_statistics": "SHOW STATISTICS FOR TABLE ck.projection_events",
    }
    result: dict[str, Any] = {}
    for name, statement in statements.items():
        timeout = 300
        if deadline is not None:
            available = deadline - time.monotonic() - 1
            if available < 1:
                raise PlanABError("TABLE_EVIDENCE_DEADLINE_EXHAUSTED")
            timeout = min(timeout, max(1, int(available)))
        raw, elapsed = run_sql(
            canary, binary, port, env, statement, timeout=timeout
        )
        entry: dict[str, Any] = {
            "sha256": digest(raw),
            "bytes": len(raw),
            "elapsed_seconds": elapsed,
        }
        if output is not None:
            if label is None:
                raise PlanABError("TABLE_EVIDENCE_LABEL_REQUIRED")
            path = output / f"{label}-{name}.tsv"
            atomic_write(path, raw)
            entry["path"] = path.name
        result[name] = entry
    return result


def scale_trial(
    canary: Any,
    output: Path,
    tasks: int,
    *,
    binary: Path | None = None,
    runtime_parent: Path | None = None,
) -> dict[str, Any]:
    scale = load_scale_campaign()
    binary = (binary or canary.find_cockroach()).resolve()
    if not binary.is_file() or binary.is_symlink() or not os.access(binary, os.X_OK):
        raise PlanABError("COCKROACH_BINARY_INVALID")
    runtime_parent = (runtime_parent or (output / "generated-roots")).resolve()
    runtime_parent.mkdir(parents=True, exist_ok=True)
    root = Path(
        tempfile.mkdtemp(prefix=f"pf2-{tasks}.", dir=runtime_parent.resolve())
    ).resolve()
    fake_home = root / "empty-home"
    (root / "temp").mkdir()
    fake_home.mkdir()
    env = canary.scrubbed_env(fake_home)
    port = canary.reserve_port()
    http_port = canary.reserve_port()
    while http_port == port:
        http_port = canary.reserve_port()
    process = None
    log = None
    trial_output = output / f"scale-{tasks}"
    trial_output.mkdir(parents=True)
    teardown: dict[str, Any] = {"process_stopped": False, "root_removed": False}
    try:
        scale_deadline = time.monotonic() + SCALE_DEADLINE_SECONDS

        def remaining_timeout(cap: int = 300) -> int:
            available = scale_deadline - time.monotonic() - 1
            if available < 1:
                raise PlanABError("PF2_SCALE_DEADLINE_EXHAUSTED")
            return min(cap, max(1, int(available)))

        process, log = canary.start_database(
            binary, root, port, http_port, env, append_log=False
        )
        canary.sql(binary, port, "CREATE DATABASE cockroach_kernel", env=env)
        canary.apply_file(
            binary,
            port,
            "cockroach_kernel",
            BASE / "p9-cloud/migrations/001_cloud.sql",
            env=env,
        )
        campaign = f"pf2-{tasks}"
        journal = scale.ChainLog(trial_output / "seed-journal.ndjson", campaign)
        preseed_vector_index = scale.prove_preseed_vector_index(
            binary,
            port,
            env,
            scale_deadline,
            reserve_seconds=SEED_TAIL_RESERVE_SECONDS,
        )
        if not preseed_vector_index["green"]:
            raise PlanABError("PF2_PRESEED_VECTOR_INDEX_INVALID")
        try:
            seed = scale.seed_dataset(
                binary,
                port,
                env,
                journal,
                campaign_id=campaign,
                tasks=tasks,
                events_per_task=1,
                receipts_per_task=1,
                vectors=tasks,
                batch_tasks=SEED_BATCH_TASKS,
                setup_deadline=scale_deadline,
                tail_reserve_seconds=SEED_TAIL_RESERVE_SECONDS,
            )
            reconciliations = scale.campaign_reconciliations(
                binary,
                port,
                env,
                campaign_id=campaign,
                tasks=tasks,
                events_per_task=1,
                receipts_per_task=1,
                vectors=tasks,
                setup_deadline=scale_deadline,
                reserve_seconds=PROJECTION_TAIL_RESERVE_SECONDS,
            )
            if any(row["state"] != "EXACT" for row in reconciliations.values()):
                raise PlanABError("PF2_CORE_SEED_RECONCILIATION_MISMATCH")
            seeded_vector_index_metadata = scale.vector_index_metadata(
                binary,
                port,
                env,
                scale_deadline,
                reserve_seconds=PROJECTION_TAIL_RESERVE_SECONDS,
            )
            if not seeded_vector_index_metadata["green"]:
                raise PlanABError("PF2_SEEDED_VECTOR_INDEX_INVALID")
            secondary_receipts = seed_secondary_receipts(
                scale,
                binary,
                port,
                env,
                journal,
                campaign=campaign,
                tasks=tasks,
                deadline=scale_deadline,
            )
            projections = seed_projections(
                scale,
                binary,
                port,
                env,
                journal,
                campaign=campaign,
                tasks=tasks,
                deadline=scale_deadline,
            )
        except scale.CampaignError as exc:
            raise PlanABError(f"PF2_BOUNDED_SEED_FAILED:{exc}") from exc
        counts_raw, _ = run_sql(
            canary,
            binary,
            port,
            env,
            "SELECT (SELECT count(*) FROM ck.tasks),"
            "(SELECT count(*) FROM ck.trajectory_events),"
            "(SELECT count(*) FROM ck.receipts),"
            "(SELECT count(*) FROM ck.context_vectors),"
            "(SELECT count(*) FROM ck.projection_events)",
            timeout=remaining_timeout(),
        )
        expected_counts = (tasks, tasks, tasks * 2, tasks, tasks)
        actual_counts = canary.parse_count_tuple(counts_raw, 5)
        if actual_counts != expected_counts:
            raise PlanABError("PF2_COUNT_MISMATCH")
        queries = query_definitions(campaign)
        before_metadata = table_evidence(
            canary,
            binary,
            port,
            env,
            output=trial_output,
            label="before",
            deadline=scale_deadline,
        )
        before = capture_queries(
            canary,
            binary,
            port,
            env,
            queries,
            trial_output,
            "before",
            deadline=scale_deadline,
        )
        receipt_scan = any(before[f"receipt-{i:02d}"]["full_scan"] for i in range(5))
        projection_scan = before["stale-projection-read"]["full_scan"]
        if not receipt_scan:
            raise PlanABError("PF2_EXPECTED_RECEIPT_FULL_SCAN_NOT_OBSERVED")
        run_sql(
            canary,
            binary,
            port,
            env,
            RECEIPT_INDEX_DDL,
            timeout=remaining_timeout(600),
        )
        selected_indexes = ["receipts_task_id_idx"]
        if projection_scan:
            run_sql(
                canary,
                binary,
                port,
                env,
                PROJECTION_INDEX_DDL,
                timeout=remaining_timeout(600),
            )
            selected_indexes.append("projection_events_source_key_idx")
        run_sql(
            canary,
            binary,
            port,
            env,
            "CREATE STATISTICS pf2_receipts_stats ON task_id FROM ck.receipts;"
            "CREATE STATISTICS pf2_projection_stats ON source_key FROM ck.projection_events",
            timeout=remaining_timeout(600),
        )
        after_metadata = table_evidence(
            canary,
            binary,
            port,
            env,
            output=trial_output,
            label="after",
            deadline=scale_deadline,
        )
        after = capture_queries(
            canary,
            binary,
            port,
            env,
            queries,
            trial_output,
            "after",
            deadline=scale_deadline,
        )
        mismatched_results = sorted(
            name for name in queries if before[name]["result_sha256"] != after[name]["result_sha256"]
        )
        prohibited_scans = sorted(
            name
            for name in queries
            if name.startswith("receipt-") or name == "stale-projection-read"
            if after[name]["full_scan"] or after[name]["analyze_full_scan"]
        )
        body = {
            "version": "ck-pdh3-r12-pf2-scale-v1",
            "tasks": tasks,
            "expected_counts": list(expected_counts),
            "actual_counts": list(actual_counts),
            "query_count": len(queries),
            "before_metadata": before_metadata,
            "after_metadata": after_metadata,
            "before": before,
            "after": after,
            "receipt_full_scan_before": receipt_scan,
            "projection_full_scan_before": projection_scan,
            "selected_indexes": selected_indexes,
            "seed_batch_tasks": SEED_BATCH_TASKS,
            "scale_deadline_seconds": SCALE_DEADLINE_SECONDS,
            "seed": seed,
            "core_reconciliations": reconciliations,
            "preseed_vector_index": preseed_vector_index,
            "seeded_vector_index": {
                "mode": "INCREMENTALLY_MAINTAINED_DURING_SEED",
                "metadata": seeded_vector_index_metadata,
                "exact_reconciliation": reconciliations["vectors"],
                "ann_quality_deferred_to_full_cardinality_pf5": True,
                "green": (
                    seeded_vector_index_metadata["green"]
                    and reconciliations["vectors"]["state"] == "EXACT"
                ),
            },
            "secondary_receipts": secondary_receipts,
            "projections": projections,
            "mismatched_results": mismatched_results,
            "prohibited_scans_after": prohibited_scans,
            "product_migration_modified": False,
            "green": not mismatched_results and not prohibited_scans,
        }
        if not body["green"]:
            raise PlanABError("PF2_PLAN_OR_RESULT_GATE_FAILED")
        return write_record(trial_output / "receipt.json", body, "receipt_sha256")
    finally:
        if process is not None and log is not None:
            canary.stop_database(process, log, crash=False)
            teardown["process_stopped"] = process.poll() is not None
        preserve_database_log(root, trial_output, teardown)
        shutil.rmtree(root, ignore_errors=False)
        teardown["root_removed"] = not root.exists()
        write_record(
            trial_output / "teardown.json",
            {
                "version": "ck-pdh3-r12-pf2-teardown-v1",
                "tasks": tasks,
                **teardown,
                "green": all(teardown.values()),
            },
            "receipt_sha256",
        )


def execute(
    output: Path,
    packet_sha256: str,
    *,
    binary: Path | None = None,
    runtime_parent: Path | None = None,
) -> dict[str, Any]:
    if output.exists():
        raise PlanABError("OUTPUT_EXISTS")
    if packet_sha256 != PLAN_SHA256:
        raise PlanABError("PLAN_HASH_BINDING_INVALID")
    output.mkdir(parents=True)
    canary = load_canary()
    receipts = [
        scale_trial(
            canary,
            output,
            scale,
            binary=binary,
            runtime_parent=runtime_parent,
        )
        for scale in SCALES
    ]
    body = {
        "version": "ck-pdh3-r12-pf2-plan-ab-v1",
        "plan_sha256": PLAN_SHA256,
        "scales": list(SCALES),
        "scale_receipts": [row["receipt_sha256"] for row in receipts],
        "fresh_root_count": len(receipts),
        "result_equivalence": all(not row["mismatched_results"] for row in receipts),
        "no_prohibited_full_scan_after": all(not row["prohibited_scans_after"] for row in receipts),
        "product_migration_modified": False,
        "green": all(row["green"] for row in receipts),
    }
    return write_record(output / "PF2_RESULT.json", body, "receipt_sha256")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--output", type=Path, required=True)
    value.add_argument("--packet-sha256", required=True)
    value.add_argument("--binary", type=Path)
    value.add_argument("--runtime-parent", type=Path)
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    try:
        result = execute(
            args.output,
            args.packet_sha256,
            binary=args.binary,
            runtime_parent=args.runtime_parent,
        )
    except (PlanABError, OSError, subprocess.SubprocessError) as exc:
        print(f"PDH3_R12_PF2_BLOCKED:{type(exc).__name__}:{exc}", file=sys.stderr)
        return 2
    print(canonical(result).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
