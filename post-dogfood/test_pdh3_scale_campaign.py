from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_scale_campaign_tested", HERE / "run_pdh3_scale_campaign.py"
)
assert SPEC is not None and SPEC.loader is not None
campaign = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = campaign
SPEC.loader.exec_module(campaign)


class ScaleCampaignUnitTests(unittest.TestCase):
    def test_canary_helpers_bind_declared_reduced_cardinality(self) -> None:
        canary = type("Canary", (), {})()
        args = argparse.Namespace(
            query_duration_seconds=2,
            tasks=100,
            events_per_task=3,
            receipts_per_task=1,
            vectors=50,
        )
        campaign.configure_canary_module(canary, args)
        self.assertEqual(canary.TASKS, 100)
        self.assertEqual(canary.EVENTS_PER_TASK, 3)
        self.assertEqual(canary.RECEIPTS_PER_TASK, 1)
        self.assertEqual(canary.VECTORS_PER_TASK, 1)
        self.assertEqual(canary.QUERY_SAMPLES, 50)
        self.assertEqual(canary.TASK_ID_WIDTH, 6)

    def test_fault_transition_retries_only_declared_transport_race(self) -> None:
        transient = campaign.CommandError(
            "FAILED",
            "cockroach",
            "a" * 64,
            returncode=1,
            output_tail="rpc error: code = Canceled desc = grpc: the client connection is closing",
        )
        operation = mock.Mock(side_effect=[transient, (1, 2, 3, 4)])
        value = campaign.fault_transition_read(
            operation,
            deadline=time.monotonic() + 5,
        )
        self.assertEqual(value, (1, 2, 3, 4))
        self.assertEqual(operation.call_count, 2)

    def test_fault_transition_does_not_retry_permanent_sql_failure(self) -> None:
        permanent = campaign.CommandError(
            "FAILED",
            "cockroach",
            "b" * 64,
            returncode=1,
            sqlstate="23505",
            output_tail="duplicate key",
        )
        operation = mock.Mock(side_effect=permanent)
        with self.assertRaises(campaign.CommandError):
            campaign.fault_transition_read(
                operation,
                deadline=time.monotonic() + 5,
            )
        self.assertEqual(operation.call_count, 1)

    @staticmethod
    def journal() -> object:
        class Journal:
            def __init__(self) -> None:
                self.events: list[tuple[str, dict[str, object]]] = []

            def emit(self, event: str, details: dict[str, object]) -> None:
                self.events.append((event, details))

        return Journal()

    @staticmethod
    def sql_error(
        kind: str,
        statement: str,
        *,
        stage: str,
        start: int,
        stop: int,
        sqlstate: str | None = None,
    ) -> Exception:
        cause = campaign.CommandError(
            kind,
            "cockroach",
            "a" * 64,
            timeout_seconds=7 if kind == "TIMEOUT" else None,
            returncode=1 if kind == "FAILED" else None,
            sqlstate=sqlstate,
        )
        return campaign.SqlOperationError(
            cause,
            stage=stage,
            start=start,
            stop=stop,
            statement_sha256=campaign.digest(statement.encode("utf-8")),
        )

    def test_seed_statement_counts_and_bounds(self) -> None:
        rows = campaign.seed_batch_statements(
            "ck-pdh3-scale-test",
            0,
            100,
            10,
            2,
            50,
        )
        self.assertEqual(
            [row[0] for row in rows],
            ["tasks", "events", "receipts", "vectors"],
        )
        self.assertTrue(all("generate_series" in row[1] for row in rows))
        targets = {
            "tasks": "ON CONFLICT (task_id) DO NOTHING",
            "events": "ON CONFLICT (event_id) DO NOTHING",
            "receipts": "ON CONFLICT (receipt_hash) DO NOTHING",
            "vectors": "ON CONFLICT (vector_id) DO NOTHING",
        }
        for stage, statement in rows:
            self.assertIn(targets[stage], statement)
            self.assertNotIn("ON CONFLICT DO NOTHING", statement)
        self.assertNotIn("AWS", "\n".join(row[1] for row in rows))

    def test_timeout_is_typed_and_bounded(self) -> None:
        with mock.patch.object(
            campaign.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["cockroach"], 7),
        ):
            with self.assertRaises(campaign.CommandError) as raised:
                campaign.run(
                    ["cockroach"],
                    env={"PATH": "/usr/bin:/bin"},
                    timeout=7,
                )
        self.assertEqual(raised.exception.kind, "TIMEOUT")
        self.assertEqual(raised.exception.timeout_seconds, 7)
        self.assertTrue(raised.exception.retryable)

    def test_sql_error_binds_stage_range_hash_and_sqlstate(self) -> None:
        statement = "SELECT 1"
        cause = campaign.CommandError(
            "FAILED",
            "cockroach",
            "b" * 64,
            returncode=1,
            sqlstate="40001",
        )
        with mock.patch.object(campaign, "run", side_effect=cause):
            with self.assertRaises(campaign.SqlOperationError) as raised:
                campaign.sql(
                    Path("/tmp/cockroach"),
                    26257,
                    statement,
                    env={"PATH": "/usr/bin:/bin"},
                    timeout=5,
                    stage="seed_tasks",
                    start=10,
                    stop=20,
                )
        error = raised.exception
        self.assertEqual(error.stage, "seed_tasks")
        self.assertEqual((error.start, error.stop), (10, 20))
        self.assertEqual(
            error.statement_sha256,
            campaign.digest(statement.encode("utf-8")),
        )
        self.assertEqual(error.sqlstate, "40001")
        self.assertTrue(error.retryable)

    def test_timeout_after_commit_reconciles_exact_without_reinsert(self) -> None:
        insert_calls: dict[str, int] = {}

        def fake_sql(*args: object, **kwargs: object) -> bytes:
            statement = str(args[2])
            stage = str(kwargs.get("stage"))
            if statement.startswith("INSERT INTO"):
                insert_calls[stage] = insert_calls.get(stage, 0) + 1
                if stage == "seed_tasks" and insert_calls[stage] == 1:
                    raise self.sql_error(
                        "TIMEOUT",
                        statement,
                        stage=stage,
                        start=int(kwargs["start"]),
                        stop=int(kwargs["stop"]),
                    )
                return b""
            if stage == "reconcile_tasks":
                return b"actual_rows\tcontent_mismatches\n2\t0\n"
            raise AssertionError(f"unexpected SQL: {stage}")

        with mock.patch.object(campaign, "sql", side_effect=fake_sql):
            result = campaign.seed_dataset(
                Path("/tmp/cockroach"),
                26257,
                {"PATH": "/usr/bin:/bin"},
                self.journal(),
                campaign_id="ck-pdh3-scale-test",
                tasks=2,
                events_per_task=1,
                receipts_per_task=1,
                vectors=2,
                batch_tasks=2,
                setup_deadline=campaign.time.monotonic() + 30,
                tail_reserve_seconds=5,
            )
        self.assertEqual(insert_calls["seed_tasks"], 1)
        self.assertEqual(result["retries"], 0)
        self.assertEqual(result["uncertain_timeouts"], 1)
        self.assertEqual(
            result["timeout_reconciliations"][0]["state"],
            "EXACT",
        )

    def test_timeout_reconciliation_mismatch_fails_closed(self) -> None:
        def fake_sql(*args: object, **kwargs: object) -> bytes:
            statement = str(args[2])
            stage = str(kwargs.get("stage"))
            if stage == "seed_tasks":
                raise self.sql_error(
                    "TIMEOUT",
                    statement,
                    stage=stage,
                    start=int(kwargs["start"]),
                    stop=int(kwargs["stop"]),
                )
            if stage == "reconcile_tasks":
                return b"1\t1\n"
            raise AssertionError(f"unexpected SQL: {stage}")

        with mock.patch.object(campaign, "sql", side_effect=fake_sql):
            with self.assertRaisesRegex(
                campaign.CampaignError,
                "SEED_RECONCILIATION_MISMATCH",
            ):
                campaign.seed_dataset(
                    Path("/tmp/cockroach"),
                    26257,
                    {"PATH": "/usr/bin:/bin"},
                    self.journal(),
                    campaign_id="ck-pdh3-scale-test",
                    tasks=2,
                    events_per_task=1,
                    receipts_per_task=1,
                    vectors=2,
                    batch_tasks=2,
                    setup_deadline=campaign.time.monotonic() + 30,
                    tail_reserve_seconds=5,
                )

    def test_permanent_sql_error_is_not_retried(self) -> None:
        calls = 0

        def fake_sql(*args: object, **kwargs: object) -> bytes:
            nonlocal calls
            calls += 1
            statement = str(args[2])
            raise self.sql_error(
                "FAILED",
                statement,
                stage=str(kwargs["stage"]),
                start=int(kwargs["start"]),
                stop=int(kwargs["stop"]),
                sqlstate="23505",
            )

        with mock.patch.object(campaign, "sql", side_effect=fake_sql):
            with self.assertRaises(campaign.SqlOperationError):
                campaign.seed_dataset(
                    Path("/tmp/cockroach"),
                    26257,
                    {"PATH": "/usr/bin:/bin"},
                    self.journal(),
                    campaign_id="ck-pdh3-scale-test",
                    tasks=1,
                    events_per_task=1,
                    receipts_per_task=1,
                    vectors=1,
                    batch_tasks=1,
                    setup_deadline=campaign.time.monotonic() + 30,
                    tail_reserve_seconds=5,
                )
        self.assertEqual(calls, 1)

    def test_sqlstate_40001_is_retried_once(self) -> None:
        task_calls = 0

        def fake_sql(*args: object, **kwargs: object) -> bytes:
            nonlocal task_calls
            statement = str(args[2])
            if kwargs.get("stage") == "seed_tasks":
                task_calls += 1
                if task_calls == 1:
                    raise self.sql_error(
                        "FAILED",
                        statement,
                        stage="seed_tasks",
                        start=int(kwargs["start"]),
                        stop=int(kwargs["stop"]),
                        sqlstate="40001",
                    )
            return b""

        with mock.patch.object(campaign, "sql", side_effect=fake_sql):
            with mock.patch.object(campaign.time, "sleep"):
                result = campaign.seed_dataset(
                    Path("/tmp/cockroach"),
                    26257,
                    {"PATH": "/usr/bin:/bin"},
                    self.journal(),
                    campaign_id="ck-pdh3-scale-test",
                    tasks=1,
                    events_per_task=1,
                    receipts_per_task=1,
                    vectors=1,
                    batch_tasks=1,
                    setup_deadline=campaign.time.monotonic() + 30,
                    tail_reserve_seconds=5,
                )
        self.assertEqual(task_calls, 2)
        self.assertEqual(result["retries"], 1)

    def test_expired_reserved_deadline_starts_no_sql(self) -> None:
        with mock.patch.object(campaign, "sql") as sql_mock:
            with self.assertRaises(campaign.SetupDeadlineError):
                campaign.seed_dataset(
                    Path("/tmp/cockroach"),
                    26257,
                    {"PATH": "/usr/bin:/bin"},
                    self.journal(),
                    campaign_id="ck-pdh3-scale-test",
                    tasks=1,
                    events_per_task=1,
                    receipts_per_task=1,
                    vectors=1,
                    batch_tasks=1,
                    setup_deadline=campaign.time.monotonic() + 0.5,
                    tail_reserve_seconds=1,
                )
        sql_mock.assert_not_called()

    def test_sql_timeout_preserves_the_declared_tail(self) -> None:
        with mock.patch.object(campaign.time, "monotonic", return_value=100.0):
            self.assertEqual(
                campaign.setup_timeout(111.9, 900, reserve_seconds=5),
                6,
            )
            with self.assertRaises(campaign.SetupDeadlineError):
                campaign.setup_timeout(105.9, 900, reserve_seconds=5)

    def test_vector_index_defer_and_restore_are_explicit(self) -> None:
        calls: list[str] = []

        def fake_sql(*args: object, **kwargs: object) -> bytes:
            statement = str(args[2])
            calls.append(statement)
            if "SHOW INDEXES FROM ck.context_vectors" in statement:
                if any(item.startswith("CREATE VECTOR INDEX") for item in calls):
                    return b"2\t1\t1\t0\n"
                return b"0\t0\t0\t0\n"
            if "FROM [SHOW JOBS]" in statement:
                if not any(item.startswith("CREATE VECTOR INDEX") for item in calls):
                    return (
                        b"job_id\tstatus\tfraction_completed\tdescription\n"
                        b"old-job\tsucceeded\t1\tCREATE VECTOR INDEX "
                        b"context_vectors_vector_idx ON ck.context_vectors (vector)\n"
                    )
                return (
                    b"job_id\tstatus\tfraction_completed\tdescription\n"
                    b"new-job\tsucceeded\t1\tCREATE VECTOR INDEX "
                    b"context_vectors_vector_idx ON ck.context_vectors (vector)\n"
                    b"old-job\tsucceeded\t1\tCREATE VECTOR INDEX "
                    b"context_vectors_vector_idx ON ck.context_vectors (vector)\n"
                )
            if "ORDER BY vector <->" in statement:
                return b"5\t5\n"
            return b""

        with mock.patch.object(campaign, "sql", side_effect=fake_sql):
            deferred = campaign.defer_vector_index(
                Path("/tmp/cockroach"),
                26257,
                {"PATH": "/usr/bin:/bin"},
                campaign.time.monotonic() + 60,
                10,
            )
            restored = campaign.restore_vector_index(
                Path("/tmp/cockroach"),
                26257,
                {"PATH": "/usr/bin:/bin"},
                campaign.time.monotonic() + 60,
                5,
                10,
            )
        self.assertTrue(deferred["green"])
        self.assertTrue(restored["green"])
        self.assertEqual(restored["completion_mode"], "ASYNCHRONOUS_JOB")
        self.assertEqual(restored["job"]["job_id"], "new-job")
        self.assertEqual(restored["pre_create_job_ids"], ["old-job"])
        self.assertIn(
            "DROP INDEX IF EXISTS ck.context_vectors@context_vectors_vector_idx",
            calls,
        )
        self.assertTrue(
            any(item.startswith("CREATE VECTOR INDEX IF NOT EXISTS") for item in calls)
        )
        self.assertTrue(any("FROM [SHOW JOBS]" in item for item in calls))
        self.assertTrue(any("ORDER BY vector <->" in item for item in calls))

    def test_synchronous_vector_index_without_job_is_directly_proved(self) -> None:
        def fake_sql(*args: object, **kwargs: object) -> bytes:
            statement = str(args[2])
            if "SHOW INDEXES FROM ck.context_vectors" in statement:
                return b"2\t1\t1\t0\n"
            if "FROM [SHOW JOBS]" in statement:
                return (
                    b"job_id\tstatus\tfraction_completed\tdescription\n"
                    b"old-job\tsucceeded\t1\tCREATE VECTOR INDEX "
                    b"context_vectors_vector_idx ON ck.context_vectors (vector)\n"
                )
            if "ORDER BY vector <->" in statement:
                return b"50\t50\n"
            return b""

        with mock.patch.object(campaign, "sql", side_effect=fake_sql):
            proof = campaign.vector_index_proof(
                Path("/tmp/cockroach"),
                26257,
                {"PATH": "/usr/bin:/bin"},
                campaign.time.monotonic() + 60,
                50,
                frozenset({"old-job"}),
            )
        self.assertTrue(proof["green"])
        self.assertEqual(proof["completion_mode"], "SYNCHRONOUS_DDL_NO_JOB")
        self.assertEqual(proof["job"]["job_id"], None)
        self.assertEqual(proof["job"]["new_job_ids"], [])

    def test_vector_index_timeout_reconciles_server_job_without_duplicate_ddl(self) -> None:
        statements: list[str] = []
        job_polls = 0

        def fake_sql(*args: object, **kwargs: object) -> bytes:
            nonlocal job_polls
            statement = str(args[2])
            statements.append(statement)
            if statement.startswith("CREATE VECTOR INDEX"):
                cause = campaign.CommandError(
                    "TIMEOUT",
                    "cockroach",
                    "a" * 64,
                    timeout_seconds=1_800,
                )
                raise campaign.SqlOperationError(
                    cause,
                    stage="vector_index_create",
                    start=None,
                    stop=None,
                    statement_sha256="b" * 64,
                )
            if "SHOW INDEXES FROM ck.context_vectors" in statement:
                return b"2\t1\t1\t0\n"
            if "FROM [SHOW JOBS]" in statement:
                job_polls += 1
                if job_polls == 1:
                    return b"job_id\tstatus\tfraction_completed\tdescription\n"
                status = "running" if job_polls == 2 else "succeeded"
                fraction = "0.5" if status == "running" else "1"
                return (
                    b"job_id\tstatus\tfraction_completed\tdescription\n"
                    + f"new-job\t{status}\t{fraction}\tCREATE VECTOR INDEX "
                    "context_vectors_vector_idx ON ck.context_vectors (vector)\n".encode()
                )
            if "ORDER BY vector <->" in statement:
                return b"250000\t250000\n"
            return b""

        with mock.patch.object(campaign, "sql", side_effect=fake_sql), mock.patch.object(
            campaign.time, "sleep", return_value=None
        ):
            restored = campaign.restore_vector_index(
                Path("/tmp/cockroach"),
                26257,
                {"PATH": "/usr/bin:/bin"},
                campaign.time.monotonic() + 60,
                250_000,
                10,
            )

        self.assertTrue(restored["green"])
        self.assertTrue(restored["uncertain_timeout_reconciled"])
        self.assertEqual(restored["attempts"], 1)
        self.assertEqual(
            sum(item.startswith("CREATE VECTOR INDEX") for item in statements),
            1,
        )

    def test_vector_index_connection_loss_reconciles_job_without_duplicate_ddl(self) -> None:
        statements: list[str] = []
        job_polls = 0

        def fake_sql(*args: object, **kwargs: object) -> bytes:
            nonlocal job_polls
            statement = str(args[2])
            statements.append(statement)
            if statement.startswith("CREATE VECTOR INDEX"):
                cause = campaign.CommandError(
                    "FAILED",
                    "cockroach",
                    "a" * 64,
                    returncode=1,
                    output_tail=(
                        "NOTICE: waiting for job(s) to complete: 123\\n"
                        "If the statement is canceled, jobs will continue in the "
                        "background.\\nERROR: connection lost."
                    ),
                )
                raise campaign.SqlOperationError(
                    cause,
                    stage="vector_index_create",
                    start=None,
                    stop=None,
                    statement_sha256="b" * 64,
                )
            if "SHOW INDEXES FROM ck.context_vectors" in statement:
                return b"2\t1\t1\t0\n"
            if "FROM [SHOW JOBS]" in statement:
                job_polls += 1
                if job_polls == 1:
                    return b"job_id\tstatus\tfraction_completed\tdescription\n"
                status = "running" if job_polls == 2 else "succeeded"
                fraction = "0.5" if status == "running" else "1"
                return (
                    b"job_id\tstatus\tfraction_completed\tdescription\n"
                    + f"new-job\t{status}\t{fraction}\tCREATE VECTOR INDEX "
                    "context_vectors_vector_idx ON ck.context_vectors (vector)\n".encode()
                )
            if "ORDER BY vector <->" in statement:
                return b"250000\t250000\n"
            return b""

        with mock.patch.object(campaign, "sql", side_effect=fake_sql), mock.patch.object(
            campaign.time, "sleep", return_value=None
        ):
            restored = campaign.restore_vector_index(
                Path("/tmp/cockroach"),
                26257,
                {"PATH": "/usr/bin:/bin"},
                campaign.time.monotonic() + 60,
                250_000,
                10,
            )

        self.assertTrue(restored["green"])
        self.assertTrue(restored["uncertain_timeout_reconciled"])
        self.assertEqual(restored["attempts"], 1)
        self.assertEqual(
            sum(item.startswith("CREATE VECTOR INDEX") for item in statements),
            1,
        )

    def test_vector_index_reconciliation_survives_one_connection_loss(self) -> None:
        statements: list[str] = []
        metadata_polls = 0
        job_polls = 0

        def uncertain_failure(stage: str) -> campaign.SqlOperationError:
            cause = campaign.CommandError(
                "FAILED",
                "cockroach",
                "a" * 64,
                returncode=1,
                output_tail=(
                    "NOTICE: waiting for job(s) to complete: 123\\n"
                    "If the statement is canceled, jobs will continue in the "
                    "background.\\nERROR: connection lost."
                ),
            )
            return campaign.SqlOperationError(
                cause,
                stage=stage,
                start=None,
                stop=None,
                statement_sha256="b" * 64,
            )

        def fake_sql(*args: object, **kwargs: object) -> bytes:
            nonlocal metadata_polls, job_polls
            statement = str(args[2])
            statements.append(statement)
            if statement.startswith("CREATE VECTOR INDEX"):
                raise uncertain_failure("vector_index_create")
            if "SHOW INDEXES FROM ck.context_vectors" in statement:
                metadata_polls += 1
                if metadata_polls == 1:
                    raise uncertain_failure("vector_index_metadata")
                return b"2\t1\t1\t0\n"
            if "FROM [SHOW JOBS]" in statement:
                job_polls += 1
                if job_polls == 1:
                    return b"job_id\tstatus\tfraction_completed\tdescription\n"
                return (
                    b"job_id\tstatus\tfraction_completed\tdescription\n"
                    b"new-job\tsucceeded\t1\tCREATE VECTOR INDEX "
                    b"context_vectors_vector_idx ON ck.context_vectors (vector)\n"
                )
            if "ORDER BY vector <->" in statement:
                return b"250000\t250000\n"
            return b""

        with mock.patch.object(campaign, "sql", side_effect=fake_sql), mock.patch.object(
            campaign.time, "sleep", return_value=None
        ):
            restored = campaign.restore_vector_index(
                Path("/tmp/cockroach"),
                26257,
                {"PATH": "/usr/bin:/bin"},
                campaign.time.monotonic() + 60,
                250_000,
                10,
            )

        self.assertTrue(restored["green"])
        self.assertTrue(restored["uncertain_timeout_reconciled"])
        self.assertEqual(
            sum(item.startswith("CREATE VECTOR INDEX") for item in statements),
            1,
        )

    def test_generic_vector_index_connection_failure_remains_fail_closed(self) -> None:
        cause = campaign.CommandError(
            "FAILED",
            "cockroach",
            "a" * 64,
            returncode=1,
            output_tail="ERROR: connection lost.",
        )
        failure = campaign.SqlOperationError(
            cause,
            stage="vector_index_create",
            start=None,
            stop=None,
            statement_sha256="b" * 64,
        )
        self.assertFalse(failure.retryable)
        self.assertFalse(failure.server_effect_uncertain)

        with mock.patch.object(campaign, "sql", side_effect=failure):
            with self.assertRaises(campaign.SqlOperationError):
                campaign.restore_vector_index(
                    Path("/tmp/cockroach"),
                    26257,
                    {"PATH": "/usr/bin:/bin"},
                    campaign.time.monotonic() + 60,
                    250_000,
                    10,
                )

    def test_vector_index_timeout_without_server_effect_retries_ddl(self) -> None:
        create_calls = 0

        def fake_sql(*args: object, **kwargs: object) -> bytes:
            nonlocal create_calls
            statement = str(args[2])
            if statement.startswith("CREATE VECTOR INDEX"):
                create_calls += 1
                if create_calls == 1:
                    cause = campaign.CommandError(
                        "TIMEOUT",
                        "cockroach",
                        "a" * 64,
                        timeout_seconds=1_800,
                    )
                    raise campaign.SqlOperationError(
                        cause,
                        stage="vector_index_create",
                        start=None,
                        stop=None,
                        statement_sha256="b" * 64,
                    )
                return b""
            if "SHOW INDEXES FROM ck.context_vectors" in statement:
                return b"0\t0\t0\t0\n" if create_calls < 2 else b"2\t1\t1\t0\n"
            if "FROM [SHOW JOBS]" in statement:
                if create_calls < 2:
                    return b"job_id\tstatus\tfraction_completed\tdescription\n"
                return (
                    b"job_id\tstatus\tfraction_completed\tdescription\n"
                    b"new-job\tsucceeded\t1\tCREATE VECTOR INDEX "
                    b"context_vectors_vector_idx ON ck.context_vectors (vector)\n"
                )
            if "ORDER BY vector <->" in statement:
                return b"250000\t250000\n"
            return b""

        with mock.patch.object(campaign, "sql", side_effect=fake_sql), mock.patch.object(
            campaign.time, "sleep", return_value=None
        ):
            restored = campaign.restore_vector_index(
                Path("/tmp/cockroach"),
                26257,
                {"PATH": "/usr/bin:/bin"},
                campaign.time.monotonic() + 60,
                250_000,
                10,
            )

        self.assertTrue(restored["green"])
        self.assertFalse(restored["uncertain_timeout_reconciled"])
        self.assertEqual(create_calls, 2)

    def test_preexisting_successful_job_cannot_prove_async_completion(self) -> None:
        def fake_sql(*args: object, **kwargs: object) -> bytes:
            statement = str(args[2])
            if "SHOW INDEXES FROM ck.context_vectors" in statement:
                return b"2\t1\t1\t0\n"
            if "FROM [SHOW JOBS]" in statement:
                return (
                    b"job_id\tstatus\tfraction_completed\tdescription\n"
                    b"stale-success\tsucceeded\t1\tCREATE VECTOR INDEX "
                    b"context_vectors_vector_idx ON ck.context_vectors (vector)\n"
                )
            if "ORDER BY vector <->" in statement:
                return b"50\t50\n"
            return b""

        with mock.patch.object(campaign, "sql", side_effect=fake_sql):
            proof = campaign.vector_index_proof(
                Path("/tmp/cockroach"),
                26257,
                {"PATH": "/usr/bin:/bin"},
                campaign.time.monotonic() + 60,
                50,
                frozenset({"stale-success"}),
            )
        self.assertTrue(proof["green"])
        self.assertEqual(proof["completion_mode"], "SYNCHRONOUS_DDL_NO_JOB")
        self.assertEqual(proof["job"]["observed_job_ids"], ["stale-success"])
        self.assertEqual(proof["job"]["new_job_ids"], [])

    def test_vector_index_full_coverage_is_exact_and_forced(self) -> None:
        statements: list[str] = []

        def fake_sql(*args: object, **kwargs: object) -> bytes:
            statement = str(args[2])
            statements.append(statement)
            if "ORDER BY vector <->" in statement:
                return b"250000\t250000\n"
            return b""

        with mock.patch.object(campaign, "sql", side_effect=fake_sql):
            coverage = campaign.vector_index_coverage(
                Path("/tmp/cockroach"),
                26257,
                {"PATH": "/usr/bin:/bin"},
                campaign.time.monotonic() + 60,
                250_000,
            )
        self.assertTrue(coverage["green"])
        self.assertEqual(coverage["returned_rows"], 250_000)
        self.assertEqual(coverage["distinct_vector_ids"], 250_000)
        self.assertIn(
            "ck.context_vectors@context_vectors_vector_idx",
            statements[0],
        )
        self.assertIn("LIMIT 250000", statements[0])

    def test_vector_index_partial_or_duplicate_coverage_fails_closed(self) -> None:
        for observed in (b"249999\t249999\n", b"250000\t249999\n"):
            with self.subTest(observed=observed):
                with mock.patch.object(campaign, "sql", return_value=observed):
                    coverage = campaign.vector_index_coverage(
                        Path("/tmp/cockroach"),
                        26257,
                        {"PATH": "/usr/bin:/bin"},
                        campaign.time.monotonic() + 60,
                        250_000,
                    )
                self.assertFalse(coverage["green"])

    def test_multiple_new_vector_jobs_fail_closed(self) -> None:
        def fake_sql(*args: object, **kwargs: object) -> bytes:
            statement = str(args[2])
            if "SHOW INDEXES FROM ck.context_vectors" in statement:
                return b"2\t1\t1\t0\n"
            if "FROM [SHOW JOBS]" in statement:
                return (
                    b"job_id\tstatus\tfraction_completed\tdescription\n"
                    b"new-2\trunning\t0.5\tCREATE VECTOR INDEX "
                    b"context_vectors_vector_idx ON ck.context_vectors (vector)\n"
                    b"new-1\tsucceeded\t1\tCREATE VECTOR INDEX "
                    b"context_vectors_vector_idx ON ck.context_vectors (vector)\n"
                )
            return b""

        with mock.patch.object(campaign, "sql", side_effect=fake_sql):
            with self.assertRaisesRegex(
                campaign.CampaignError,
                "VECTOR_INDEX_MULTIPLE_NEW_JOBS",
            ):
                campaign.vector_index_proof(
                    Path("/tmp/cockroach"),
                    26257,
                    {"PATH": "/usr/bin:/bin"},
                    campaign.time.monotonic() + 60,
                    50,
                    frozenset(),
                )

    def test_local_store_size_is_explicit_and_optional(self) -> None:
        node = campaign.Node(
            index=0,
            sql_port=26257,
            http_port=8080,
            store=Path("/tmp/node/store"),
            log=Path("/tmp/node/log"),
            store_size="2GiB",
        )
        command = campaign.node_command(
            Path("/tmp/cockroach"), node, "127.0.0.1:26257", "1MiB", "1MiB"
        )
        self.assertIn("--store=path=/tmp/node/store,size=2GiB", command)

    def test_vector_statement_omitted_after_vector_ceiling(self) -> None:
        rows = campaign.seed_batch_statements(
            "ck-pdh3-scale-test",
            100,
            200,
            10,
            2,
            50,
        )
        self.assertNotIn("vectors", [row[0] for row in rows])

    def test_reconciliation_detects_missing_and_corrupt_rows(self) -> None:
        with mock.patch.object(campaign, "sql", return_value=b"8\t1\n"):
            result = campaign.reconcile_seed_batch(
                Path("/tmp/cockroach"),
                26257,
                {"PATH": "/usr/bin:/bin"},
                stage="events",
                campaign_id="ck-pdh3-scale-test",
                start=0,
                stop=5,
                events_per_task=2,
                receipts_per_task=1,
                vector_stop=5,
                setup_deadline=campaign.time.monotonic() + 30,
                reserve_seconds=5,
            )
        self.assertEqual(result["expected_rows"], 10)
        self.assertEqual(result["missing_rows"], 2)
        self.assertEqual(result["content_mismatches"], 1)
        self.assertEqual(result["mismatch_rows"], 3)
        self.assertEqual(result["state"], "MISMATCH")

    def test_production_rejects_local_store_size_before_io(self) -> None:
        arguments = campaign.parser().parse_args([
            "--binary", "/tmp/does-not-exist",
            "--packet", "/tmp/does-not-exist",
            "--output", "/tmp/does-not-exist",
            "--campaign-id", "ck-pdh3-scale-test",
            "--production",
            "--store-size", "2GiB",
        ])
        with self.assertRaisesRegex(
            campaign.CampaignError,
            "PRODUCTION_STORE_SIZE_FORBIDDEN",
        ):
            campaign.execute(arguments)

    def test_production_schedule_is_exact(self) -> None:
        arguments = campaign.parser().parse_args([
            "--binary", "/tmp/cockroach",
            "--packet", "/tmp/packet",
            "--output", "/tmp/output",
            "--campaign-id", "ck-pdh3-scale-test",
            "--production",
            "--duration-seconds", str(campaign.contract.MEASURED_SECONDS),
            "--checkpoint-seconds", str(campaign.contract.CHECKPOINT_SECONDS),
            "--fault-every-checkpoints", str(
                campaign.contract.FAULT_EVERY_CHECKPOINTS
            ),
        ])
        value = campaign.production_schedule(arguments)
        self.assertEqual(value["checkpoints"], 288)
        self.assertEqual(value["verifier_batches"], 232)
        self.assertEqual(value["verifier_executions"], 9_976)
        self.assertEqual(value["fault_count"], 24)
        self.assertEqual(value["fault_epochs"], list(range(12, 289, 12)))

    def test_deadline_timeout_preserves_epoch_reserve(self) -> None:
        with mock.patch.object(campaign.time, "monotonic", return_value=100.0):
            self.assertEqual(
                campaign.deadline_timeout(
                    120.5, 300, reserve_seconds=15, label="EPOCH"
                ),
                5,
            )
            with self.assertRaisesRegex(
                campaign.CampaignError, "EPOCH_DEADLINE_RESERVE_EXHAUSTED"
            ):
                campaign.deadline_timeout(
                    115.5, 300, reserve_seconds=15, label="EPOCH"
                )

    def test_query_files_use_six_digit_seed_ids(self) -> None:
        class Canary:
            CAMPAIGN_ID = ""
            TASK_ID_WIDTH = 4

            @staticmethod
            def build_query_files(root: Path) -> dict[str, dict[str, object]]:
                return {
                    "width": {"value": Canary.TASK_ID_WIDTH},
                    "campaign": {"value": Canary.CAMPAIGN_ID},
                }

        value = campaign.create_query_files(
            Canary, Path("/tmp"), "ck-pdh3-scale-test"
        )
        self.assertEqual(value["width"]["value"], 6)
        self.assertEqual(value["campaign"]["value"], "ck-pdh3-scale-test")

    def test_fault_cycle_proves_sigkill_fresh_pid_and_control_durability(self) -> None:
        class Process:
            def __init__(self, pid: int) -> None:
                self.pid = pid

            @staticmethod
            def poll() -> None:
                return None

        nodes = [
            campaign.Node(index, 26000 + index, 27000 + index,
                          Path(f"/tmp/n{index}"), Path(f"/tmp/n{index}.log"))
            for index in range(3)
        ]
        for index, node in enumerate(nodes):
            node.process = Process(100 + index)

        def fake_stop(node: object, *, crash: bool) -> int:
            self.assertTrue(crash)
            node.process = None
            return -campaign.signal.SIGKILL

        def fake_start(*args: object, **kwargs: object) -> None:
            node = args[1]
            node.process = Process(999)

        with mock.patch.object(campaign, "stop_node", side_effect=fake_stop), \
             mock.patch.object(campaign, "start_node", side_effect=fake_start), \
             mock.patch.object(campaign, "campaign_counts", return_value=(1, 2, 3, 4)), \
             mock.patch.object(campaign, "control_counts", return_value=(10, 20, 1)), \
             mock.patch.object(
                 campaign,
                 "cluster_status",
                 return_value={"green": True, "nodes": []},
             ):
            value = campaign.fault_cycle(
                Path("/tmp/cockroach"), nodes, 0, "join", "1GiB", "1GiB",
                {"PATH": "/usr/bin:/bin"}, "ck-pdh3-scale-test",
                deadline=time.monotonic() + 30,
            )
        self.assertTrue(value["green"])
        self.assertEqual(value["returncode"], -campaign.signal.SIGKILL)
        self.assertEqual(value["old_pid"], 100)
        self.assertEqual(value["new_pid"], 999)
        self.assertEqual(value["controls_before"], value["controls_after"])

    def test_partial_cluster_start_failure_stops_started_nodes(self) -> None:
        class Process:
            pid = 123

            @staticmethod
            def poll() -> None:
                return None

        starts = 0

        def fake_start(*args: object, **kwargs: object) -> None:
            nonlocal starts
            starts += 1
            node = args[1]
            if starts == 2:
                raise campaign.CampaignError("START_FAILED")
            node.process = Process()

        def fake_stop(node: object, *, crash: bool) -> int:
            node.process = None
            return 0

        startup: dict[str, object] = {}
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(campaign, "start_node", side_effect=fake_start), \
                 mock.patch.object(campaign, "stop_node", side_effect=fake_stop), \
                 mock.patch.object(campaign, "file_sha256", return_value="a" * 64):
                with self.assertRaisesRegex(campaign.CampaignError, "START_FAILED"):
                    campaign.start_cluster(
                        Path("/tmp/cockroach"), Path(temporary),
                        {"PATH": "/usr/bin:/bin"}, "1GiB", "1GiB",
                        startup_evidence=startup,
                    )
        self.assertEqual(starts, 2)
        self.assertEqual(startup["started_nodes"], 1)
        self.assertEqual(startup["stop_returncodes"], [0])
        self.assertTrue(startup["partial_teardown_required"])
        self.assertTrue(startup["partial_teardown_proved"])
        self.assertEqual(startup["open_ports_after_failure"], [])

    def test_preflight_control_reset_is_atomic_and_exact(self) -> None:
        control_values = iter([(10, 20, 1), (0, 0, 0)])
        with mock.patch.object(
            campaign, "control_counts", side_effect=lambda *a, **k: next(control_values)
        ), mock.patch.object(campaign, "sql", return_value=b"0\n") as sql_mock:
            value = campaign.reset_preflight_controls(
                Path("/tmp/cockroach"), 26257,
                {"PATH": "/usr/bin:/bin"}, "ck-pdh3-scale-test",
                deadline=time.monotonic() + 30,
            )
        self.assertTrue(value["green"])
        self.assertIn("BEGIN;", str(sql_mock.call_args_list[0].args[2]))
        self.assertIn("COMMIT;", str(sql_mock.call_args_list[0].args[2]))

    def test_trace_progress_receipt_gate_rejects_projection_and_accepts_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            progress = root / "progress.json"
            output = root / "output"
            output.mkdir()
            body = {
                "version": "ck-pdh3-process-tree-egress-observer-v2",
                "status": "IN_PROGRESS",
                "authoritative": False,
                "trace_stream_count": 1,
                "maximum_trace_bytes": campaign.contract.TRACE_BYTES_LIMIT,
                "trace_bytes": 1234,
                "projected_trace_bytes_24h_conservative": 10_000,
                "projected_cap_exceeded": False,
                "scan_count": 3,
                "packet_sha256": "a" * 64,
                "child_command_sha256": "b" * 64,
                "campaign_id": "ck-pdh3-scale-test",
                "progress_receipt_path": str(progress),
            }
            progress.write_bytes(campaign.canonical({
                **body,
                "progress_receipt_sha256": campaign.digest(body),
            }))
            now = time.time()
            os.utime(progress, (now, now))
            with mock.patch.dict(
                os.environ,
                {
                    "PDH3_TRACE_PROGRESS_RECEIPT": str(progress),
                    "PDH3_PACKET_SHA256": "a" * 64,
                    "PDH3_TRACE_PACKET_SHA256": "a" * 64,
                    "PDH3_TRACE_CHILD_COMMAND_SHA256": "b" * 64,
                },
                clear=False,
            ):
                value = campaign.validate_trace_progress_receipt(
                    output,
                    campaign_id="ck-pdh3-scale-test",
                    now=now,
                )
                self.assertTrue(value["green"])
                self.assertEqual(value["trace_bytes"], 1234)
                self.assertEqual(
                    value["projected_trace_bytes_24h_conservative"], 10_000
                )
                self.assertEqual(
                    value["destination"], "preflight-trace-progress.json"
                )
                self.assertEqual(
                    value["source_file_sha256"], value["file_sha256"]
                )
                with mock.patch.dict(
                    os.environ,
                    {"PDH3_PACKET_SHA256": "c" * 64},
                    clear=False,
                ):
                    with self.assertRaisesRegex(
                        campaign.CampaignError,
                        "TRACE_PROGRESS_RECEIPT_NOT_GREEN",
                    ):
                        campaign.validate_trace_progress_receipt(
                            root / "packet-mismatch-output",
                            campaign_id="ck-pdh3-scale-test",
                            now=now,
                        )
                symlink = root / "progress-link.json"
                symlink.symlink_to(progress)
                with mock.patch.dict(
                    os.environ,
                    {"PDH3_TRACE_PROGRESS_RECEIPT": str(symlink)},
                    clear=False,
                ):
                    with self.assertRaisesRegex(
                        campaign.CampaignError,
                        "TRACE_PROGRESS_RECEIPT_INVALID_PATH",
                    ):
                        campaign.validate_trace_progress_receipt(
                            root / "symlink-output",
                            campaign_id="ck-pdh3-scale-test",
                            now=now,
                        )
                with self.assertRaisesRegex(
                    campaign.CampaignError,
                    "TRACE_PROGRESS_DESTINATION_INVALID",
                ):
                    campaign.validate_trace_progress_receipt(
                        output,
                        campaign_id="ck-pdh3-scale-test",
                        now=now,
                        destination_name="../escape.json",
                    )
                broken = dict(body)
                broken["projected_trace_bytes_24h_conservative"] = (
                    campaign.contract.TRACE_PREFLIGHT_PROJECTION_LIMIT + 1
                )
                progress.write_bytes(campaign.canonical({
                    **broken,
                    "progress_receipt_sha256": campaign.digest(broken),
                }))
                with self.assertRaisesRegex(
                    campaign.CampaignError, "TRACE_PROGRESS_RECEIPT_NOT_GREEN"
                ):
                    campaign.validate_trace_progress_receipt(
                        root / "second-output",
                        campaign_id="ck-pdh3-scale-test",
                        now=now,
                    )
                os.utime(progress, (now - 1000, now - 1000))
                with self.assertRaisesRegex(
                    campaign.CampaignError, "TRACE_PROGRESS_RECEIPT_STALE"
                ):
                    campaign.validate_trace_progress_receipt(
                        root / "stale-output",
                        campaign_id="ck-pdh3-scale-test",
                        now=now,
                    )
            with mock.patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(
                    campaign.CampaignError, "TRACE_PROGRESS_RECEIPT_MISSING"
                ):
                    campaign.validate_trace_progress_receipt(
                        root / "missing-output",
                        campaign_id="ck-pdh3-scale-test",
                        now=now,
                    )

    def test_terminal_green_requires_hash_valid_green_teardown_and_no_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            teardown_body = {
                "version": "test",
                "green": False,
            }
            teardown = {
                **teardown_body,
                "receipt_sha256": campaign.digest(teardown_body),
            }
            with self.assertRaisesRegex(
                campaign.CampaignError, "PREMATURE_GREEN_TEARDOWN_NOT_GREEN"
            ):
                campaign.commit_success_evidence(
                    output, {"campaign_id": "ck-pdh3-scale-test"}, teardown
                )
            self.assertFalse((output / "result.json").exists())
            self.assertFalse((output / "MEASURED_CAMPAIGN_GREEN").exists())
            good_body = {"version": "test", "green": True}
            good = {
                **good_body,
                "receipt_sha256": campaign.digest(good_body),
            }
            (output / "failure.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(
                campaign.CampaignError, "FAILURE_RESULT_MUTUAL_EXCLUSION_BREACH"
            ):
                campaign.commit_success_evidence(
                    output, {"campaign_id": "ck-pdh3-scale-test"}, good
                )
            (output / "failure.json").unlink()
            result = campaign.commit_success_evidence(
                output, {"campaign_id": "ck-pdh3-scale-test"}, good
            )
            self.assertEqual(
                json.loads((output / "result.json").read_bytes()), result
            )
            marker = json.loads(
                (output / "MEASURED_CAMPAIGN_GREEN").read_bytes()
            )
            marker_body = {
                key: value for key, value in marker.items()
                if key != "marker_sha256"
            }
            self.assertEqual(marker["marker_sha256"], campaign.digest(marker_body))

    def test_reconstructs_exactly_9976_unique_verifier_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            sequence = 0
            for batch in range(1, campaign.contract.VERIFIER_BATCHES + 1):
                root = (
                    output / "raw" / "measured" / f"epoch-{batch:04d}"
                    / "verifier" / "verifier-campaign"
                )
                receipts = root / "receipts"
                receipts.mkdir(parents=True)
                aggregate = root / "aggregate.json"
                aggregate.write_bytes(campaign.canonical({"green": True}))
                for index in range(campaign.contract.VERIFIER_BATCH_SIZE):
                    sequence += 1
                    body = {
                        "version": "test-verifier-receipt-v1",
                        "batch": batch,
                        "execution": index,
                        "global_sequence": sequence,
                    }
                    (receipts / f"trial-{index:03d}.json").write_bytes(
                        campaign.canonical({
                            **body,
                            "receipt_hash": campaign.digest(body),
                        })
                    )
                files = {
                    str(path.relative_to(root)): campaign.file_sha256(path)
                    for path in sorted(root.rglob("*.json"))
                }
                manifest_body = {
                    "version": "test-verifier-manifest-v1",
                    "batch": batch,
                    "files": files,
                }
                (root / "manifest.json").write_bytes(
                    campaign.canonical({
                        **manifest_body,
                        "manifest_sha256": campaign.digest(manifest_body),
                    })
                )
            value = campaign.validate_verifier_evidence(
                output,
                lane="measured",
                expected_batches=campaign.contract.VERIFIER_BATCHES,
                expected_receipts=campaign.contract.VERIFIER_EXECUTIONS,
            )
        self.assertTrue(value["green"])
        self.assertEqual(value["batch_count"], 232)
        self.assertEqual(value["receipt_count"], 9_976)
        self.assertEqual(value["unique_receipt_hashes"], 9_976)

    def test_remote_preflight_is_three_500_worker_epochs_three_rotating_faults(self) -> None:
        class Canary:
            @staticmethod
            def verify_query_targets(*args: object, **kwargs: object) -> dict[str, object]:
                return {"green": True}

        arguments = campaign.parser().parse_args([
            "--binary", "/tmp/cockroach",
            "--packet", "/tmp/packet",
            "--output", "/tmp/output",
            "--campaign-id", "ck-pdh3-scale-test",
            "--production",
        ])
        calls: list[dict[str, object]] = []

        def fake_epoch(**kwargs: object) -> dict[str, object]:
            calls.append(kwargs)
            body = {
                "epoch": kwargs["epoch"],
                "fault": {"green": True},
            }
            return {**body, "checkpoint_sha256": campaign.digest(body)}

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "root"
            output = Path(temporary) / "output"
            root.mkdir()
            output.mkdir()
            with mock.patch.object(campaign, "run_campaign_epoch", side_effect=fake_epoch), \
                 mock.patch.object(
                     campaign,
                     "validate_verifier_evidence",
                     return_value={"green": True},
                 ), \
                 mock.patch.object(
                     campaign,
                     "validate_trace_progress_receipt",
                     return_value={"green": True},
                 ), \
                 mock.patch.object(
                     campaign,
                     "reset_preflight_controls",
                     return_value={"green": True, "reset_sha256": "a" * 64},
                 ), \
                 mock.patch.object(
                     campaign, "campaign_counts", return_value=(1, 2, 3, 4)
                 ):
                value = campaign.run_remote_preflight(
                    args=arguments,
                    canary=Canary,
                    binary=Path("/tmp/cockroach"),
                    nodes=[mock.Mock(sql_port=26257) for _ in range(3)],
                    join="join",
                    env={"PATH": "/usr/bin:/bin"},
                    root=root,
                    output=output,
                    query_files={},
                    expected_counts=(1, 2, 3, 4),
                )
        self.assertTrue(value["green"])
        self.assertEqual(len(calls), 3)
        self.assertEqual([row["fault_target"] for row in calls], [0, 1, 2])
        self.assertEqual(
            {row["concurrency"] for row in calls},
            {campaign.contract.REMOTE_PREFLIGHT_CONCURRENCY},
        )
        self.assertTrue(all(row["verifier_required"] for row in calls))

    def test_epoch_snapshot_uses_shared_deadline_and_hits_boundary(self) -> None:
        class Clock:
            value = 0.0

            def monotonic(self) -> float:
                return self.value

            def monotonic_ns(self) -> int:
                return int(self.value * 1_000_000_000)

            def sleep(self, seconds: float) -> None:
                self.value += seconds

        class Canary:
            MINIMUM_ACK_WRITE_OPERATIONS = 0
            MINIMUM_CONTENDED_UPDATE_OPERATIONS = 0
            MINIMUM_REPLAY_OPERATIONS = 0

            @staticmethod
            def run_stage(*args: object, **kwargs: object) -> dict[str, object]:
                self.assertEqual(kwargs["deadline"], 285.0)
                return {
                    "green": True,
                    "total_operations": 4,
                    "maximum_latency_ms": {"p99": 1.0, "max": 2.0},
                    "acknowledged_write_delta": 1,
                    "contended_update_delta": 1,
                }

        clock = Clock()
        nodes = [
            campaign.Node(i, 26000 + i, 27000 + i,
                          Path(f"/tmp/n{i}"), Path(f"/tmp/n{i}.log"))
            for i in range(3)
        ]
        for index, node in enumerate(nodes):
            node.process = mock.Mock(pid=100 + index)
            node.process.poll.return_value = None
        resources = {
            "nodes": [
                {"node": i + 1, "pid": 100 + i, "alive": True,
                 "rss_kb": 1, "descriptors": 1}
                for i in range(3)
            ],
            "process_tree": {
                "available": True,
                "complete": True,
                "required_pids_present": True,
                "member_count": 4,
                "member_pid_set_sha256": "a" * 64,
            },
            "database_bytes": 1,
            "evidence_bytes": 1,
            "disk_total_bytes": 100,
            "disk_used_bytes": 1,
            "disk_used_fraction": 0.01,
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "root"
            output = Path(temporary) / "output"
            root.mkdir()
            output.mkdir()
            with mock.patch.object(campaign.time, "monotonic", clock.monotonic), \
                 mock.patch.object(campaign.time, "monotonic_ns", clock.monotonic_ns), \
                 mock.patch.object(campaign.time, "sleep", clock.sleep), \
                 mock.patch.object(campaign, "cleanup_probe", return_value={"residue": 0}), \
                 mock.patch.object(campaign, "dependency_matrix", return_value={"rows": 5}), \
                 mock.patch.object(campaign, "campaign_counts", return_value=(1, 2, 3, 4)), \
                 mock.patch.object(campaign, "control_counts", return_value=(1, 1, 1)), \
                 mock.patch.object(campaign, "sql", return_value=b"0\n"), \
                 mock.patch.object(campaign, "cluster_status", return_value={"green": True}), \
                 mock.patch.object(campaign, "process_metrics", return_value=resources), \
                 mock.patch.object(
                     campaign,
                     "validate_trace_progress_receipt",
                     return_value={
                         "green": True,
                         "trace_bytes": 100,
                         "projected_trace_bytes_24h_conservative": 1000,
                     },
                 ):
                value = campaign.run_campaign_epoch(
                    canary=Canary,
                    binary=Path("/tmp/cockroach"),
                    nodes=nodes,
                    join="join",
                    env={"PATH": "/usr/bin:/bin"},
                    root=root,
                    output=output,
                    query_files={},
                    campaign_id="ck-pdh3-scale-test",
                    expected_counts=(1, 2, 3, 4),
                    cache="1GiB",
                    sql_memory="1GiB",
                    lane="measured",
                    epoch=1,
                    concurrency=10,
                    boundary_ns=300_000_000_000,
                    verifier_required=False,
                    fault_target=None,
                    disk_used_fraction_limit=0.7,
                    production=True,
                )
        self.assertEqual(value["snapshot_monotonic_ns"], 300_000_000_000)
        self.assertEqual(value["boundary_drift_ns"], 0)
        self.assertTrue(value["trace_progress_at_boundary"]["green"])

    def test_production_resource_gate_requires_three_measured_nodes(self) -> None:
        resources = {
            "nodes": [
                {"alive": True, "rss_kb": None, "descriptors": None}
                for _ in range(3)
            ],
            "process_tree": {
                "available": True,
                "complete": True,
                "required_pids_present": True,
                "member_count": 4,
                "member_pid_set_sha256": "a" * 64,
            },
            "database_bytes": 0,
            "evidence_bytes": 0,
        }
        with self.assertRaisesRegex(
            campaign.CampaignError, "PRODUCTION_RSS_METRICS_UNAVAILABLE"
        ):
            campaign.enforce_resource_thresholds(resources, production=True)
        resources["process_tree"]["member_count"] = (
            campaign.contract.PROCESS_TREE_COUNT_LIMIT + 1
        )
        with self.assertRaisesRegex(
            campaign.CampaignError, "PROCESS_TREE_COUNT_LIMIT"
        ):
            campaign.enforce_resource_thresholds(resources, production=True)
        resources["nodes"][2]["alive"] = False
        with self.assertRaisesRegex(
            campaign.CampaignError, "LIVE_NODE_PROCESS_COUNT_INVALID"
        ):
            campaign.enforce_resource_thresholds(resources, production=False)

    def test_linux_process_tree_snapshot_is_complete_and_binds_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            proc = Path(temporary)
            for pid, ppid in ((100, 1), (101, 100), (102, 100), (103, 101)):
                status = proc / str(pid) / "status"
                status.parent.mkdir()
                status.write_text(f"Name:\ttest\nPPid:\t{ppid}\n")
            value = campaign.linux_process_tree_snapshot(
                100, [101, 102, 103], proc_root=proc
            )
            self.assertTrue(value["complete"])
            self.assertEqual(value["member_count"], 4)
            self.assertTrue(value["required_pids_present"])
            malformed = proc / "104" / "status"
            malformed.parent.mkdir()
            malformed.write_text("Name:\tmalformed\n")
            incomplete = campaign.linux_process_tree_snapshot(
                100, [101, 102, 103], proc_root=proc
            )
            self.assertFalse(incomplete["complete"])
            self.assertEqual(incomplete["unreadable_status_count"], 1)
            missing = campaign.linux_process_tree_snapshot(
                100, [999], proc_root=proc
            )
            self.assertFalse(missing["complete"])
            self.assertEqual(missing["missing_required_pids"], [999])
            absent = campaign.linux_process_tree_snapshot(
                999, [], proc_root=proc
            )
            self.assertFalse(absent["complete"])

    def test_process_metrics_polls_each_node_once_for_membership(self) -> None:
        nodes = [
            campaign.Node(
                index,
                26000 + index,
                27000 + index,
                Path(f"/tmp/node-{index}"),
                Path(f"/tmp/node-{index}.log"),
            )
            for index in range(3)
        ]
        processes = []
        for index, node in enumerate(nodes):
            process = mock.Mock(pid=700 + index)
            process.poll.side_effect = [None, 1]
            node.process = process
            processes.append(process)
        captured: dict[str, object] = {}

        def snapshot(root_pid: int, required_pids: list[int]) -> dict[str, object]:
            captured["root_pid"] = root_pid
            captured["required_pids"] = list(required_pids)
            return {
                "available": True,
                "complete": True,
                "required_pids_present": True,
                "member_count": 4,
                "member_pid_set_sha256": "a" * 64,
            }

        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            campaign, "linux_process_tree_snapshot", side_effect=snapshot
        ):
            root = Path(temporary)
            output = root / "output"
            output.mkdir()
            value = campaign.process_metrics(nodes, root, output)
        self.assertEqual(captured["required_pids"], [700, 701, 702])
        self.assertEqual(value["process_tree"]["member_count"], 4)
        for process in processes:
            self.assertEqual(process.poll.call_count, 1)

    def test_result_mode_metadata_never_labels_reduced_smoke_as_runpod(self) -> None:
        reduced = campaign.result_mode_metadata(False)
        serialized = json.dumps(reduced, sort_keys=True)
        self.assertEqual(
            reduced["version"], "ck-pdh3-reduced-local-smoke-result-v1"
        )
        self.assertNotIn("SECURE_RUNPOD", serialized)
        self.assertNotIn("SINGLE_RUNPOD_HOST", serialized)
        self.assertIn("NOT_RUNPOD_EVIDENCE", reduced["limitations"])
        production = campaign.result_mode_metadata(True)
        self.assertEqual(
            production["version"], "ck-pdh3-production-scale-result-v1"
        )

    def test_setup_margin_gate_is_quantitative_and_fail_closed(self) -> None:
        passing = campaign.setup_margin_gate(5_400, 5_100, production=True)
        self.assertEqual(
            passing["required_setup_margin_seconds"],
            campaign.contract.SETUP_SUCCESS_MARGIN_SECONDS,
        )
        self.assertEqual(passing["setup_margin_seconds"], 300)
        self.assertTrue(passing["setup_margin_met"])
        failing = campaign.setup_margin_gate(5_400, 5_100.001, production=True)
        self.assertFalse(failing["setup_margin_met"])
        reduced = campaign.setup_margin_gate(60, 30, production=False)
        self.assertEqual(reduced["required_setup_margin_seconds"], 30)
        self.assertTrue(reduced["setup_margin_met"])

    def test_campaign_name_boundary(self) -> None:
        arguments = campaign.parser().parse_args([
            "--binary", "/tmp/cockroach",
            "--packet", "/tmp/packet",
            "--output", "/tmp/output",
            "--campaign-id", "wrong",
        ])
        with self.assertRaisesRegex(campaign.CampaignError, "CAMPAIGN_ID_INVALID"):
            campaign.execute(arguments)


if __name__ == "__main__":
    unittest.main()
