from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_local_canary_tested", HERE / "run_pdh3_local_canary.py"
)
assert SPEC is not None and SPEC.loader is not None
canary = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = canary
SPEC.loader.exec_module(canary)


class LocalCanaryDeadlineTests(unittest.TestCase):
    def test_verifier_salt_is_deterministic_and_batch_bound(self) -> None:
        first = canary.verifier_public_salt("ck-pdh3-scale-r8-measured-v0001")
        repeated = canary.verifier_public_salt("ck-pdh3-scale-r8-measured-v0001")
        second = canary.verifier_public_salt("ck-pdh3-scale-r8-measured-v0002")
        self.assertEqual(first, repeated)
        self.assertNotEqual(first, second)
        self.assertEqual(len(first), 32)
        with self.assertRaisesRegex(
            canary.CanaryError, "VERIFIER_CAMPAIGN_ID_INVALID"
        ):
            canary.verifier_public_salt("../escape")

    def test_dataset_builder_has_no_live_cloud_adapter_imports(self) -> None:
        source = (HERE / "pdh3_synthetic_dataset.py").read_text()
        for forbidden in (
            "import cloud_adapter",
            "import boto3",
            "import hardening",
            "import protocol",
            "live_bulk_controller.py",
        ):
            self.assertNotIn(forbidden, source)

    def test_dataset_builder_uses_configured_id_width(self) -> None:
        old_values = (
            canary.CAMPAIGN_ID,
            canary.TASK_ID_WIDTH,
            canary.TASKS,
            canary.EVENTS_PER_TASK,
            canary.RECEIPTS_PER_TASK,
            canary.VECTORS_PER_TASK,
            canary.QUERY_SAMPLES,
        )
        try:
            canary.CAMPAIGN_ID = "ck-pdh3-synthetic-test"
            canary.TASK_ID_WIDTH = 6
            canary.TASKS = 2
            canary.EVENTS_PER_TASK = 2
            canary.RECEIPTS_PER_TASK = 1
            canary.VECTORS_PER_TASK = 2
            canary.QUERY_SAMPLES = 1
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "generated"
                manifest = canary.build_dataset(root)
                task_sql = (root / manifest["batches"]["tasks"][0]["path"]).read_text()
                self.assertIn("task-000000", task_sql)
                self.assertEqual(manifest["task_id_width"], 6)
                self.assertFalse(manifest["credential_material"])
        finally:
            (
                canary.CAMPAIGN_ID,
                canary.TASK_ID_WIDTH,
                canary.TASKS,
                canary.EVENTS_PER_TASK,
                canary.RECEIPTS_PER_TASK,
                canary.VECTORS_PER_TASK,
                canary.QUERY_SAMPLES,
            ) = old_values

    def test_scale_query_files_use_configured_width(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old_id = canary.CAMPAIGN_ID
            old_width = canary.TASK_ID_WIDTH
            try:
                canary.CAMPAIGN_ID = "ck-pdh3-scale-test"
                canary.TASK_ID_WIDTH = 6
                definitions = canary.build_query_files(root)
            finally:
                canary.CAMPAIGN_ID = old_id
                canary.TASK_ID_WIDTH = old_width
            raw = definitions["read_mix"]["path"].read_text()
            self.assertIn("ck-pdh3-scale-test-task-000000", raw)
            self.assertNotIn("ck-pdh3-scale-test-task-0000'", raw)
            self.assertIn(
                "WHERE t.task_id='ck-pdh3-scale-test-task-000000'",
                raw,
            )
            self.assertNotIn(
                "WHERE t.campaign_id='ck-pdh3-scale-test'",
                raw,
            )

    def test_contended_updates_use_exact_bounded_hot_shards(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            definitions = canary.build_query_files(Path(temporary))
            rows = definitions["contended_update"]["path"].read_text().splitlines()
        self.assertEqual(len(rows), canary.CONTENDED_COUNTER_SHARDS)
        self.assertEqual(canary.CONTENDED_COUNTER_SHARDS, 16)
        self.assertEqual(
            {row.rsplit("'", 2)[1] for row in rows},
            {f"shard-{index:02d}" for index in range(16)},
        )
        self.assertTrue(
            all("SET value=value+1" in row for row in rows)
        )

    def test_failed_command_preserves_stdout_and_stderr(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            stdout_path = root / "stdout.log"
            stderr_path = root / "stderr.log"
            with self.assertRaisesRegex(
                canary.CanaryError,
                r"^COMMAND_FAILED:-c:[0-9a-f]{64}:stdout=[0-9a-f]{64}:stderr=[0-9a-f]{64}$",
            ):
                canary.run(
                    [
                        sys.executable,
                        "-c",
                        "import sys; print('out'); print('err', file=sys.stderr); raise SystemExit(7)",
                    ],
                    env={"PATH": "/usr/bin:/bin"},
                    timeout=5,
                    stdout_path=stdout_path,
                    stderr_path=stderr_path,
                )
            self.assertEqual(stdout_path.read_bytes(), b"out\n")
            self.assertEqual(stderr_path.read_bytes(), b"err\n")

    def test_bounded_timeout_refuses_exhausted_deadline(self) -> None:
        with mock.patch.object(canary.time, "monotonic", return_value=100.0):
            with self.assertRaisesRegex(
                canary.CanaryError, "EPOCH_DEADLINE_EXHAUSTED"
            ):
                canary.bounded_timeout(100.5, 120, required_seconds=1)

    def test_bounded_timeout_reserves_tail(self) -> None:
        with mock.patch.object(canary.time, "monotonic", return_value=100.0):
            self.assertEqual(
                canary.bounded_timeout(130.0, 120, reserve_seconds=10),
                20,
            )

    def test_query_target_cardinality_must_match(self) -> None:
        outputs = iter((b"20\n", b"10\n"))
        with mock.patch.object(canary, "sql", side_effect=lambda *a, **k: next(outputs)):
            result = canary.verify_query_targets(
                Path("/tmp/cockroach"),
                26257,
                {"PATH": "/usr/bin:/bin"},
                campaign_id="ck-pdh3-scale-test",
                id_width=6,
            )
        self.assertTrue(result["green"])

    def test_query_target_zero_rows_block(self) -> None:
        outputs = iter((b"0\n", b"0\n"))
        with mock.patch.object(canary, "sql", side_effect=lambda *a, **k: next(outputs)):
            with self.assertRaisesRegex(
                canary.CanaryError, "QUERY_TARGET_CARDINALITY_MISMATCH"
            ):
                canary.verify_query_targets(
                    Path("/tmp/cockroach"),
                    26257,
                    {"PATH": "/usr/bin:/bin"},
                    campaign_id="ck-pdh3-scale-test",
                    id_width=6,
                )

    def test_timeout_is_canonical_and_process_group_is_terminated(self) -> None:
        command = [
            sys.executable,
            "-c",
            "import time; time.sleep(60)",
        ]
        with self.assertRaisesRegex(
            canary.CanaryError, r"^COMMAND_TIMEOUT:python.*:1:"
        ):
            canary.run(
                command,
                env={"PATH": "/usr/bin:/bin"},
                timeout=1,
            )

    def test_green_result_requires_verified_green_teardown(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdh3-terminal-test.") as temporary:
            output = Path(temporary)
            packet_hash = "a" * 64
            body = {
                "version": "pdh3-local-canary-teardown-v2",
                "status": "BLOCKED",
                "candidate_commit": canary.CANDIDATE,
                "packet_sha256": packet_hash,
                "database_process_stopped": False,
                "generated_root_removed": True,
                "ports_closed": True,
                "open_ports": [],
                "errors": ["DATABASE_STOP_FAILED:CanaryError"],
                "workload_exception": None,
            }
            canary.atomic_write(
                output / "teardown.json",
                canary.canonical(
                    dict(body, receipt_sha256=canary.digest(body))
                ),
            )
            with self.assertRaisesRegex(
                canary.CanaryError, "TEARDOWN_RECEIPT_NOT_GREEN"
            ):
                canary.publish_green_result(
                    output,
                    packet_hash,
                    {"status": "GREEN", "version": "test-result"},
                )
            self.assertFalse((output / "result.json").exists())
            self.assertFalse((output / "manifest.json").exists())

    def test_green_result_is_terminal_file_committed_last(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdh3-terminal-test.") as temporary:
            output = Path(temporary)
            packet_hash = "b" * 64
            body = {
                "version": "pdh3-local-canary-teardown-v2",
                "status": "GREEN",
                "candidate_commit": canary.CANDIDATE,
                "packet_sha256": packet_hash,
                "database_process_stopped": True,
                "generated_root_removed": True,
                "ports_closed": True,
                "open_ports": [],
                "errors": [],
                "workload_exception": None,
            }
            canary.atomic_write(
                output / "teardown.json",
                canary.canonical(
                    dict(body, receipt_sha256=canary.digest(body))
                ),
            )
            original_atomic_write = canary.atomic_write
            writes: list[str] = []

            def recording_write(path: Path, raw: bytes) -> None:
                writes.append(path.name)
                original_atomic_write(path, raw)

            with mock.patch.object(
                canary, "atomic_write", side_effect=recording_write
            ):
                result = canary.publish_green_result(
                    output,
                    packet_hash,
                    {"status": "GREEN", "version": "test-result"},
                )
            self.assertEqual(writes, ["manifest.json", "result.json"])
            self.assertEqual(result["status"], "GREEN")
            self.assertFalse((output / "failure.json").exists())
            self.assertEqual(json.loads((output / "result.json").read_bytes()), result)

    def test_blocked_failure_removes_terminal_green_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdh3-terminal-test.") as temporary:
            output = Path(temporary)
            packet = output / "packet.md"
            packet.write_text("frozen packet")
            (output / "result.json").write_text('{"status":"GREEN"}')
            (output / "manifest.json").write_text("{}")
            canary.publish_blocked_failure(
                output,
                packet,
                canary.CanaryError("LOCAL_TEARDOWN_BLOCKED"),
            )
            self.assertFalse((output / "result.json").exists())
            self.assertFalse((output / "manifest.json").exists())
            failure = json.loads((output / "failure.json").read_bytes())
            self.assertEqual(failure["status"], "BLOCKED")

    def test_teardown_stop_failure_is_receipted_blocked(self) -> None:
        class FakeProcess:
            def poll(self) -> None:
                return None

        class FakeLog:
            closed = False

            def close(self) -> None:
                self.closed = True

        with tempfile.TemporaryDirectory(prefix="pdh3-teardown-output.") as temporary:
            output = Path(temporary)
            root = Path(
                tempfile.mkdtemp(prefix="ck-pdh3-local-r1.", dir="/private/tmp")
            )
            try:
                with (
                    mock.patch.object(
                        canary,
                        "stop_database",
                        side_effect=canary.CanaryError("STOP_FAILED"),
                    ),
                    mock.patch.object(canary, "port_is_closed", return_value=True),
                ):
                    receipt = canary.finalize_local_teardown(
                        output=output,
                        root=root,
                        process=FakeProcess(),  # type: ignore[arg-type]
                        log_handle=FakeLog(),
                        ports=(26257, 28080),
                        packet_hash="c" * 64,
                        workload_exception=None,
                    )
                self.assertEqual(receipt["status"], "BLOCKED")
                self.assertIn("DATABASE_STOP_FAILED:CanaryError", receipt["errors"])
                self.assertTrue(receipt["generated_root_removed"])
                self.assertFalse((output / "result.json").exists())
            finally:
                if root.exists():
                    import shutil

                    shutil.rmtree(root)


if __name__ == "__main__":
    unittest.main()
