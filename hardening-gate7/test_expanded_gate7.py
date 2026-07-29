#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import tarfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
PUBLIC_SEED = bytes.fromhex("0123456789abcdef" * 4)
CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
TEST_HASH = "1" * 64


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("MODULE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


contract = load("test_gate7_expanded_contract", HERE / "expanded_contract.py")
generator = load("test_gate7_expanded_generator", HERE / "generate_expanded_inputs.py")
campaign = load("test_gate7_expanded_campaign", HERE / "run_expanded_campaign.py")
bulk = load("test_gate7_live_bulk", HERE / "live_bulk_controller.py")
bundle = load("test_gate7_bundle", HERE / "build_expanded_bundle.py")
custody = load("test_gate7_run4_custody", HERE / "run4_evidence_custody.py")
track_gate = load("test_gate7_run4_track_gate", HERE / "run4_track_gate.py")


def canonical(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


class ExpandedGate7Tests(unittest.TestCase):
    def test_measured_track1_custody_seal_and_unseal_are_hash_bound(self):
        with tempfile.TemporaryDirectory(prefix="ck-g7r5-custody-") as temporary:
            root = Path(temporary)
            archive = root / "track1-evidence.tar.gz"
            archive.write_bytes(b"synthetic-track1-evidence\n")
            receipt_path = root / "track1-custody.json"
            unseal_path = root / "track1-unseal.json"

            receipt = custody.seal(
                archive, receipt_path, "ck-g7r5-unit-custody",
            )
            self.assertEqual(receipt["status"], "SEALED")
            self.assertEqual(stat.S_IMODE(archive.stat().st_mode), 0)
            custody.validate_receipt(json.loads(receipt_path.read_bytes()))

            result = custody.unseal(archive, receipt_path, unseal_path)
            self.assertEqual(result["status"], "UNSEALED_HASH_VERIFIED")
            self.assertEqual(stat.S_IMODE(archive.stat().st_mode), stat.S_IRUSR)
            custody.validate_receipt(json.loads(unseal_path.read_bytes()))
            self.assertEqual(result["archive_sha256"], receipt["archive_sha256"])

    def test_measured_track2_gate_requires_green_sealed_and_zero_residue(self):
        def hashed(body, field):
            return dict(body, **{field: track_gate.digest(body)})

        campaign_id = "ck-g7r5-unit-gate"
        with tempfile.TemporaryDirectory(prefix="ck-g7r5-track-gate-") as temporary:
            root = Path(temporary)
            aggregate = hashed({
                "version": "unit-track1",
                "campaign_id": campaign_id + "-track1",
                "green": True,
                "pass_count": 84,
                "scored_execution_count": 84,
                "behavior_failure_count": 0,
                "safety_failure_count": 0,
                "false_promotions": 0,
                "mutation_after_refusal_or_invalid": 0,
                "residue_count": 0,
                "post_reveal_tuning_events": 0,
            }, "aggregate_sha256")
            custody_record = hashed({
                "version": "unit-custody",
                "campaign_id": campaign_id,
                "status": "SEALED",
                "archive_mode_after": "0000",
                "extracted_before_track2": False,
            }, "receipt_sha256")
            cleanup_record = hashed({
                "version": "unit-cleanup",
                "campaign_id": campaign_id + "-track3",
                "status": "PASS",
                "residue_counts": [0, 0, 0, 0],
            }, "receipt_sha256")
            result_record = hashed({
                "version": "unit-result",
                "campaign_id": campaign_id + "-track3",
                "green": True,
                "actual_counts": [2000, 20000, 4000, 20000],
            }, "result_sha256")
            terminal_record = hashed({
                "version": "unit-terminal",
                "campaign_id": campaign_id + "-track3",
                "status": "GREEN",
                "result_sha256": result_record["result_sha256"],
                "cleanup_receipt_sha256": cleanup_record["receipt_sha256"],
            }, "receipt_sha256")
            records = {
                "aggregate.json": aggregate,
                "custody.json": custody_record,
                "terminal.json": terminal_record,
                "cleanup.json": cleanup_record,
                "result.json": result_record,
            }
            for name, value in records.items():
                (root / name).write_bytes(canonical(value))

            marker = track_gate.evaluate(
                campaign_id, root / "aggregate.json", root / "custody.json",
                root / "terminal.json", root / "cleanup.json",
                root / "result.json", root / "track2-start.json",
            )
            self.assertEqual(marker["status"], "TRACK2_START_AUTHORIZED")
            self.assertFalse(marker["database_heavy_tracks_overlap"])

            for field, replacement, expected in (
                ("status", "BLOCKED", "TRACK3_TERMINAL_NOT_GREEN"),
                ("cleanup_residue", [1, 0, 0, 0], "TRACK3_RESIDUE"),
                ("custody_status", "UNSEALED", "TRACK1_CUSTODY_INVALID"),
            ):
                case_root = root / field
                case_root.mkdir()
                case_records = {name: dict(value) for name, value in records.items()}
                if field == "status":
                    body = {key: value for key, value in terminal_record.items()
                            if key != "receipt_sha256"}
                    body["status"] = replacement
                    case_records["terminal.json"] = hashed(body, "receipt_sha256")
                elif field == "cleanup_residue":
                    body = {key: value for key, value in cleanup_record.items()
                            if key != "receipt_sha256"}
                    body["residue_counts"] = replacement
                    changed_cleanup = hashed(body, "receipt_sha256")
                    case_records["cleanup.json"] = changed_cleanup
                    terminal_body = {key: value for key, value in terminal_record.items()
                                     if key != "receipt_sha256"}
                    terminal_body["cleanup_receipt_sha256"] = changed_cleanup["receipt_sha256"]
                    case_records["terminal.json"] = hashed(terminal_body, "receipt_sha256")
                else:
                    body = {key: value for key, value in custody_record.items()
                            if key != "receipt_sha256"}
                    body["status"] = replacement
                    case_records["custody.json"] = hashed(body, "receipt_sha256")
                for name, value in case_records.items():
                    (case_root / name).write_bytes(canonical(value))
                with self.assertRaisesRegex(track_gate.TrackGateError, expected):
                    track_gate.evaluate(
                        campaign_id, case_root / "aggregate.json",
                        case_root / "custody.json", case_root / "terminal.json",
                        case_root / "cleanup.json", case_root / "result.json",
                        case_root / "marker.json",
                    )

    def test_schedule_thresholds_and_transfer_allowlist_are_exact(self):
        schedule = json.loads(
            (BASE / "HARDENING_GATE7_EXPANDED_RUNPOD_SCHEDULE_R1.json").read_bytes()
        )
        thresholds = json.loads(
            (BASE / "HARDENING_GATE7_EXPANDED_THRESHOLDS_R1.json").read_bytes()
        )
        self.assertEqual(schedule["maximum_concurrent_workers"], 1)
        self.assertEqual(schedule["accepted_gpu_count"], 0)
        self.assertEqual(schedule["worker_volume_gb"], 0)
        self.assertEqual(schedule["aggregate_runpod_exposure_usd_max"], "5.00")
        self.assertEqual(thresholds["campaign"]["hidden_scored_executions"], 84)
        self.assertEqual(thresholds["live_track"]["duration_seconds"], 3600)
        paths = bundle.collect()
        rows = bundle.scan(paths)
        self.assertGreaterEqual(len(rows), 80)
        self.assertIn(
            Path("hardening-gate5/heldout_contract.py"), paths,
        )
        self.assertIn(Path("s3-soak/freeze_evidence_manifest.py"), paths)
        self.assertIn(Path("p9-cloud/migrations/003_collision_safe_vector_digest.sql"), paths)
        helper = next(row for row in rows
                      if row["path"] == "s3-soak/freeze_evidence_manifest.py")
        self.assertEqual(helper["mode"], "0755")
        self.assertEqual(len(helper["sha256"]), 64)
        self.assertEqual(sum(".s3-runtime" in row["path"] for row in rows), 0)
        self.assertEqual(sum(".hardening-runtime" in row["path"] for row in rows), 0)

    def test_bulk_live_track_generation_is_exact_and_synthetic(self):
        with tempfile.TemporaryDirectory(prefix="ck-g7-bulk-") as temporary:
            root = Path(temporary)
            generated_a = root / "generated-a"
            generated_b = root / "generated-b"
            manifest = bulk.build_sql("ck-g7r3-public-unit", generated_a)
            repeated = bulk.build_sql("ck-g7r3-public-unit", generated_b)
            self.assertEqual(manifest, repeated)
            self.assertEqual(
                {path.name: path.read_bytes() for path in generated_a.iterdir()},
                {path.name: path.read_bytes() for path in generated_b.iterdir()},
            )
            self.assertTrue(manifest["synthetic_only"])
            self.assertEqual(manifest["counts"], {
                "tasks": 2000,
                "events": 20000,
                "receipts": 4000,
                "vectors": 20000,
                "vector_queries": 200,
                "aws_calls_separate_track": 12,
            })
            self.assertEqual(manifest["concurrency"], 4)
            self.assertLessEqual(manifest["unique_vector_digests"], 20000)
            self.assertEqual(
                manifest["vector_digest_collisions"],
                20000 - manifest["unique_vector_digests"],
            )
            self.assertGreaterEqual(manifest["max_vector_digest_multiplicity"], 1)
            self.assertEqual(manifest["unique_vector_ids"], 20000)
            self.assertEqual(manifest["unique_vector_linkages"], 20000)
            self.assertEqual(
                manifest["vector_digest_policy"],
                "NON_UNIQUE_CONTENT_DIGEST_EXACT_ROW_LINKAGE",
            )
            self.assertEqual(sum(len(rows) for rows in manifest["batches"].values()), 184)
            self.assertEqual(manifest["cleanup_batch_count"], 107)
            self.assertEqual(manifest["execution_policy"], {
                "batch_timeout_seconds": 120,
                "vector_batch_timeout_seconds": 300,
                "serialization_retries": 3,
                "serialization_retry_backoff_ms": 250,
            })
            cleanup_manifest = json.loads(
                (generated_a / "cleanup-manifest.json").read_bytes()
            )
            self.assertEqual(cleanup_manifest["batch_count"], 107)
            self.assertEqual(cleanup_manifest["vector_row_batch_size"], 250)
            self.assertEqual(cleanup_manifest["vector_batch_count"], 80)
            self.assertEqual(cleanup_manifest["default_task_batch_size"], 250)
            first_vector_cleanup = generated_a / next(
                row["path"] for row in cleanup_manifest["batches"]
                if row["stage"] == "vectors"
            )
            cleanup_sql = first_vector_cleanup.read_text(encoding="utf-8")
            self.assertIn("ISOLATION LEVEL READ COMMITTED", cleanup_sql)
            self.assertIn("ORDER BY vector_id LIMIT 250", cleanup_sql)
            self.assertEqual(
                cleanup_manifest["cleanup_manifest_sha256"],
                manifest["cleanup_manifest_sha256"],
            )
            self.assertEqual(
                len(json.loads((generated_a / "query-specs.json").read_bytes())), 200
            )
            for path in generated_a.iterdir():
                self.assertNotIn(b"/Users/", path.read_bytes())
                self.assertNotIn(b"password", path.read_bytes().lower())

    def test_full_46000_controller_success_repeats_deterministic_semantics(self):
        campaign_id = "ck-g7r3-success-unit"
        expected_counts = [2000, 20000, 4000, 20000]
        with tempfile.TemporaryDirectory(prefix="ck-g7-success-") as temporary:
            root = Path(temporary)
            generated = root / "generated"
            manifest = bulk.build_sql(campaign_id, generated)

            def execute_once(name):
                evidence = root / name
                evidence.mkdir()
                journal = bulk.DurableJournal(
                    evidence / "journal.ndjson", campaign_id,
                )
                lock = bulk.threading.Lock()
                calls = {"cleanup": 0, "batch_files": [], "queries": 0,
                         "counts": 0}

                def fake_sql(_config, _env, *, execute=None, file=None,
                             timeout=60, fmt="tsv"):
                    del timeout, fmt
                    if file is not None:
                        filename = Path(file).name
                        with lock:
                            if filename.startswith("cleanup-") and filename.endswith(".sql"):
                                calls["cleanup"] += 1
                            else:
                                calls["batch_files"].append(filename)
                        return b"COMMIT\n", 2
                    if execute is None:
                        raise AssertionError("SQL_OPERATION_MISSING")
                    if execute.startswith("EXPLAIN "):
                        return b"plan\nvector index\n", 3
                    if execute == "SHOW REGIONS FROM CLUSTER;":
                        return b"region\nus-west1\n", 3
                    if " ROLLBACK;" in execute:
                        return b"count\n0\n", 3
                    if "ON CONFLICT DO NOTHING" in execute:
                        return b"count\n1\n", 3
                    if execute.startswith("SELECT vector_id FROM"):
                        task_id = execute.split("WHERE task_id='", 1)[1].split("'", 1)[0]
                        with lock:
                            calls["queries"] += 1
                            query_number = calls["queries"]
                        bulk.time.sleep(0.002)
                        return (
                            f"vector_id\n{task_id}-vector-00\n".encode("utf-8"),
                            query_number % 5 + 1,
                        )
                    if "(SELECT count(*) FROM ck.tasks" in execute:
                        with lock:
                            calls["counts"] += 1
                            count_call = calls["counts"]
                        counts = expected_counts if count_call == 2 else [0, 0, 0, 0]
                        return (
                            b"tasks\tevents\treceipts\tvectors\n" +
                            ("\t".join(str(value) for value in counts) + "\n").encode("utf-8"),
                            3,
                        )
                    if execute.startswith("SELECT count(*) FROM ck.tasks"):
                        return b"count\n0\n", 1
                    raise AssertionError("UNEXPECTED_SQL_OPERATION")

                try:
                    with mock.patch.object(
                            bulk.cloud_adapter, "_read_config", return_value={}), \
                            mock.patch.object(
                                bulk.cloud_adapter, "_password", return_value=b"synthetic"), \
                            mock.patch.object(
                                bulk.cloud_adapter, "_sql_env",
                                side_effect=lambda *_args: {"PGPASSWORD": "synthetic"}), \
                            mock.patch.object(
                                bulk.cloud_adapter, "_sql", side_effect=fake_sql):
                        result = bulk.run_live(
                            root / "config.json", generated, evidence, journal,
                        )
                finally:
                    journal.close()

                self.assertTrue(result["green"])
                self.assertEqual(result["actual_counts"], expected_counts)
                self.assertEqual(result["query_count"], 200)
                self.assertEqual(calls["queries"], 200)
                self.assertEqual(calls["cleanup"], manifest["cleanup_batch_count"])
                self.assertEqual(len(calls["batch_files"]), 184)
                self.assertEqual(
                    sorted(calls["batch_files"]),
                    sorted(row["path"] for rows in manifest["batches"].values()
                           for row in rows),
                )
                self.assertEqual(
                    bulk.validate_terminal_evidence(evidence)["status"], "GREEN",
                )

                stable_result = dict(result)
                for field in (
                    "result_sha256", "journal_terminal_prior_hash",
                    "cleanup_receipt_sha256",
                ):
                    stable_result.pop(field)
                terminal = json.loads((evidence / "terminal.json").read_bytes())
                stable_terminal = {
                    "version": terminal["version"],
                    "campaign_id": terminal["campaign_id"],
                    "status": terminal["status"],
                    "process_exit_status": terminal["process_exit_status"],
                    "signal": terminal["signal"],
                }
                return stable_result, stable_terminal, (evidence / "cleanup.json").read_bytes()

            first = execute_once("evidence-a")
            second = execute_once("evidence-b")
            self.assertEqual(first, second)

    def test_projection_digest_is_not_used_as_row_identity(self):
        old_seen = set()
        old_collisions = 0
        for task_index in range(2000):
            for sequence in range(10):
                old = bulk.context_vector.context_vector(
                    f"continue synthetic task {task_index} trajectory segment {sequence}",
                    "ck-g7r3-vector-proof",
                )
                old_digest = bulk.context_vector.vector_digest(old)
                old_collisions += old_digest in old_seen
                old_seen.add(old_digest)
        self.assertGreater(old_collisions, 0)

    def test_adversarial_vector_digest_collisions_preserve_unique_linkage(self):
        with tempfile.TemporaryDirectory(prefix="ck-g7-collision-safe-") as temporary:
            root = Path(temporary)
            with (
                mock.patch.object(bulk, "TASKS", 2),
                mock.patch.object(bulk, "EVENTS_PER_TASK", 2),
                mock.patch.object(bulk, "VECTORS_PER_TASK", 2),
                mock.patch.object(bulk, "RECEIPTS_PER_TASK", 1),
                mock.patch.object(bulk, "QUERY_SAMPLES", 2),
                mock.patch.object(
                    bulk.context_vector, "vector_digest", return_value="ab" * 32,
                ),
            ):
                manifest = bulk.build_sql("ck-g7r5-public-collision", root / "generated")
            self.assertEqual(manifest["counts"]["vectors"], 4)
            self.assertEqual(manifest["unique_vector_digests"], 1)
            self.assertEqual(manifest["vector_digest_collisions"], 3)
            self.assertEqual(manifest["max_vector_digest_multiplicity"], 4)
            self.assertEqual(manifest["unique_vector_ids"], 4)
            self.assertEqual(manifest["unique_vector_linkages"], 4)

    def test_packaged_manifest_helper_negative_archive_cases(self):
        helper_path = BASE / "s3-soak/freeze_evidence_manifest.py"
        raw = helper_path.read_bytes()
        row = {
            "path": "s3-soak/freeze_evidence_manifest.py",
            "sha256": bundle.digest(raw), "bytes": str(len(raw)), "mode": "0755",
        }

        def write_archive(path, members):
            with tarfile.open(path, "w:gz") as archive:
                for name, value, kind in members:
                    info = tarfile.TarInfo(name)
                    info.mode = 0o755
                    if kind == "symlink":
                        info.type = tarfile.SYMTYPE
                        info.linkname = "target"
                        archive.addfile(info)
                    else:
                        info.size = len(value)
                        archive.addfile(info, io.BytesIO(value))

        with tempfile.TemporaryDirectory(prefix="ck-g7-helper-negative-") as temporary:
            root = Path(temporary)
            valid = root / "valid.tgz"
            expected_name = "bundle/" + row["path"]
            write_archive(valid, [(expected_name, raw, "file")])
            self.assertEqual(bundle.validate_archive(valid, [row])["file_count"], 1)
            cases = {
                "missing": [],
                "duplicate": [(expected_name, raw, "file"), (expected_name, raw, "file")],
                "renamed": [(expected_name + ".renamed", raw, "file")],
                "symlink": [(expected_name, b"", "symlink")],
                "altered": [(expected_name, raw + b"x", "file")],
            }
            for name, members in cases.items():
                with self.subTest(name=name):
                    path = root / f"{name}.tgz"
                    write_archive(path, members)
                    with self.assertRaises(bundle.BundleError):
                        bundle.validate_archive(path, [row])

    def test_serialization_retry_and_nonretryable_vector_failure(self):
        journal = mock.Mock()
        manifest = {"batches": {"vectors": [{
            "path": "batch.sql", "sha256": "", "rows": 1, "batch_index": 1,
        }]}}
        with tempfile.TemporaryDirectory(prefix="ck-g7-batch-retry-") as temporary:
            root = Path(temporary)
            batch = root / "batch.sql"
            batch.write_bytes(b"BEGIN; SELECT 1; COMMIT;\n")
            manifest["batches"]["vectors"][0]["sha256"] = bulk.digest(batch.read_bytes())
            transient = bulk.hardening.command_failure(
                "cockroach", 1, b"restart transaction\nSQLSTATE: 40001")
            with mock.patch.object(
                    bulk.cloud_adapter, "_sql",
                    side_effect=[transient, (b"ok", 2)]) as sql_call, \
                    mock.patch.object(bulk.time, "sleep") as sleep_call:
                elapsed, hashes, retries = bulk.execute_batches(
                    {}, {}, root, manifest, "vectors", journal)
            self.assertEqual((elapsed, retries, len(hashes)), (2, 1, 1))
            self.assertEqual(sql_call.call_args_list[0].kwargs["timeout"], 300)
            sleep_call.assert_called_once_with(0.25)
            permanent = bulk.hardening.command_failure(
                "cockroach", 1, b"duplicate\nSQLSTATE: 23505")
            with mock.patch.object(bulk.cloud_adapter, "_sql", side_effect=permanent):
                with self.assertRaises(bulk.hardening.ExternalCommandFailure):
                    bulk.execute_batches({}, {}, root, manifest, "vectors", journal)

    def test_terminal_evidence_missing_and_interrupted_are_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix="ck-g7-terminal-") as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(bulk.LiveBulkError, "TERMINAL_RECEIPT_MISSING"):
                bulk.validate_terminal_evidence(root)
        interrupted = bulk.external_failure_fields(bulk.LiveBulkInterrupted("SIGNAL_SIGTERM"))
        self.assertEqual(interrupted["failure_class"], "SIGNAL_SIGTERM")

    def test_partial_insert_failure_emits_durable_failure_cleanup_and_terminal(self):
        campaign_id = "ck-g7r3-partial-unit"
        with tempfile.TemporaryDirectory(prefix="ck-g7-partial-") as temporary:
            root = Path(temporary)
            generated = root / "generated"
            evidence = root / "evidence"
            generated.mkdir()
            evidence.mkdir()
            batches = {}
            for stage in ("tasks", "events", "receipts", "vectors"):
                path = generated / f"{stage}.sql"
                path.write_bytes(b"BEGIN; SELECT 1; COMMIT;\n")
                batches[stage] = [{
                    "path": path.name, "sha256": bulk.digest(path.read_bytes()),
                    "rows": 1, "batch_index": 1,
                }]
            (generated / "cleanup.sql").write_bytes(b"BEGIN; SELECT 1; COMMIT;\n")
            cleanup_batch = generated / "cleanup-unit-batch-0001.sql"
            cleanup_batch.write_bytes(b"BEGIN; SELECT 1; COMMIT;\n")
            cleanup_manifest_body = {
                "version": "hardening-gate7-live-bulk-cleanup-manifest-v1",
                "campaign_id": campaign_id,
                "task_batch_size": 1,
                "batch_count": 1,
                "batches": [{
                    "path": cleanup_batch.name,
                    "sha256": bulk.digest(cleanup_batch.read_bytes()),
                    "stage": "unit",
                    "batch_index": 1,
                    "task_count": 1,
                }],
                "composed_cleanup_sha256": bulk.digest(
                    (generated / "cleanup.sql").read_bytes()
                ),
            }
            cleanup_manifest = {
                **cleanup_manifest_body,
                "cleanup_manifest_sha256": bulk.digest(cleanup_manifest_body),
            }
            (generated / "cleanup-manifest.json").write_bytes(
                bulk.canonical(cleanup_manifest)
            )
            (generated / "query-specs.json").write_text("[]", encoding="utf-8")
            manifest_body = {
                "version": "hardening-gate7-live-bulk-manifest-v3",
                "campaign_id": campaign_id,
                "counts": {"tasks": 1, "events": 1, "receipts": 1,
                           "vectors": 1, "vector_queries": 0},
                "batches": batches,
                "cleanup_manifest_sha256": cleanup_manifest["cleanup_manifest_sha256"],
                "cleanup_batch_count": 1,
            }
            manifest = {**manifest_body, "manifest_sha256": bulk.digest(manifest_body)}
            (generated / "manifest.json").write_bytes(bulk.canonical(manifest))
            journal = bulk.DurableJournal(evidence / "journal.ndjson", campaign_id)
            calls = {"cleanup": 0}

            def fake_sql(_config, _env, *, execute=None, file=None, timeout=60, fmt="tsv"):
                del timeout, fmt
                if file is not None and Path(file).name == "vectors.sql":
                    raise bulk.hardening.command_failure(
                        "cockroach", 1, b"duplicate\nSQLSTATE: 23505")
                if file is not None and Path(file).name == cleanup_batch.name:
                    calls["cleanup"] += 1
                    return b"COMMIT\n", 1
                if execute is not None and "SELECT count" in execute:
                    return b"count\tcount\tcount\tcount\n0\t0\t0\t0\n", 1
                return b"COMMIT\n", 1

            try:
                with mock.patch.object(bulk.cloud_adapter, "_read_config", return_value={}), \
                        mock.patch.object(bulk.cloud_adapter, "_password", return_value=b"synthetic"), \
                        mock.patch.object(bulk.cloud_adapter, "_sql_env", return_value={}), \
                        mock.patch.object(bulk.cloud_adapter, "_sql", side_effect=fake_sql):
                    with self.assertRaises(bulk.hardening.ExternalCommandFailure):
                        bulk.run_live(root / "config.json", generated, evidence, journal)
            finally:
                journal.close()
            self.assertEqual(calls["cleanup"], 1)
            failure = json.loads((evidence / "failure.json").read_bytes())
            cleanup = json.loads((evidence / "cleanup.json").read_bytes())
            terminal = json.loads((evidence / "terminal.json").read_bytes())
            self.assertEqual(failure["sqlstate"], "23505")
            self.assertEqual(failure["stage"], "VECTORS")
            self.assertEqual(cleanup["status"], "PASS")
            self.assertEqual(terminal["status"], "BLOCKED")
            self.assertEqual(bulk.validate_terminal_evidence(evidence)["status"], "BLOCKED")

    def test_hidden_generation_source_commits_before_generation(self):
        source = (HERE / "prepare_hidden_campaign.py").read_text(encoding="utf-8")
        seed_write = source.index("atomic_write(seed_path, seed)")
        commitment_write = source.index(
            "atomic_write(commitment_path, canonical(commitment))"
        )
        generator_load = source.index("generator = load_generator()")
        self.assertLess(seed_write, commitment_write)
        self.assertLess(commitment_write, generator_load)
        self.assertIn("PRE_GENERATION_COMMITMENT_NOT_ISOLATED", source)

    def test_contract_has_exact_reachable_balanced_84_rows(self):
        rows = contract.slots()
        coverage = contract.validate_slots(rows)
        self.assertEqual(len(rows), 84)
        self.assertEqual(len({row["slot_id"] for row in rows}), 84)
        self.assertEqual(coverage["block_counts"], {
            "A_ORIGINAL_FAILURE": 21,
            "A_ORIGINAL_CONTROL": 7,
            "A_ORIGINAL_DETERMINISM": 15,
            "B_TOPOLOGY_WORKFLOW": 20,
            "C_COMPOUND": 9,
            "D_EXACT_BOUNDARY": 6,
            "E_TEMPORAL_CUSTODY": 6,
        })
        self.assertEqual(coverage["matrix_balance"], {
            "PROMOTE": 4, "REFUSE": 12, "INVALID": 4,
        })

    def test_generation_is_deterministic_and_oracle_is_separate(self):
        with tempfile.TemporaryDirectory(prefix="ck-g7-generation-") as temporary:
            root = Path(temporary)
            first = root / "first"
            second = root / "second"
            generator.write_campaign(PUBLIC_SEED, "ck-g7-known-r1", first)
            generator.write_campaign(PUBLIC_SEED, "ck-g7-known-r1", second)
            for relative in (
                "input-manifest.json", "sealed-oracle/oracle.json",
                "seed-commitment.json",
            ):
                self.assertEqual((first / relative).read_bytes(),
                                 (second / relative).read_bytes())
            manifest = json.loads((first / "input-manifest.json").read_bytes())
            self.assertFalse(manifest["oracle_included"])
            self.assertEqual(manifest["case_count"], 84)
            self.assertFalse(any("oracle" in name.lower()
                                 for name in manifest["case_files"]))
            for path in (first / "inputs").glob("*.json"):
                raw = path.read_bytes()
                self.assertNotIn(b"expected_", raw)
                self.assertNotIn(b"oracle", raw.lower())

    def test_runner_source_has_no_oracle_or_contract_dependency(self):
        for name in ("run_expanded_case.py", "surface_cases.py",
                     "run_expanded_campaign.py"):
            source = (HERE / name).read_text(encoding="utf-8")
            self.assertNotIn("expanded_contract", source)
            self.assertNotIn("sealed-oracle", source)
            self.assertNotIn("expected_verdict", source)
            self.assertNotIn("expected_reason", source)

    def test_input_with_oracle_like_field_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="ck-g7-oracle-attack-") as temporary:
            root = Path(temporary)
            campaign_root = root / "campaign"
            generator.write_campaign(PUBLIC_SEED, "ck-g7-known-r2", campaign_root)
            source = campaign_root / "inputs" / "E-R6.json"
            value = json.loads(source.read_bytes())
            value["oracle"] = {"expected_verdict": "PROMOTE"}
            attacked = root / "attacked.json"
            attacked.write_bytes(canonical(value))
            completed = subprocess.run([
                sys.executable, str(HERE / "run_expanded_case.py"),
                "--case", str(attacked), "--trial-root", str(root / "trial"),
                "--output", str(root / "observation.json"),
                "--packet-sha256", TEST_HASH, "--execution-order", "1",
                "--source-bindings-sha256", TEST_HASH,
            ], cwd=BASE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
               check=False, timeout=30)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(b"CASE_SCHEMA_INVALID", completed.stderr)
            self.assertFalse((root / "observation.json").exists())

    def test_two_known_nonmeasured_canaries_end_to_end(self):
        with tempfile.TemporaryDirectory(prefix="ck-g7-canaries-") as temporary:
            root = Path(temporary)
            campaign_root = root / "campaign"
            generator.write_campaign(PUBLIC_SEED, "ck-g7-known-r3", campaign_root)
            oracle = json.loads(
                (campaign_root / "sealed-oracle/oracle.json").read_bytes()
            )
            oracle_by_id = {row["slot_id"]: row for row in oracle["entries"]}
            for order, slot_id in enumerate(("B-1-2", "D-FILE-LP1"), start=1):
                trial_root = root / f"trial-{order}"
                observation_path = root / f"observation-{order}.json"
                completed = subprocess.run([
                    sys.executable, str(HERE / "run_expanded_case.py"),
                    "--case", str(campaign_root / "inputs" / f"{slot_id}.json"),
                    "--trial-root", str(trial_root),
                    "--output", str(observation_path),
                    "--packet-sha256", TEST_HASH,
                    "--execution-order", str(order),
                    "--source-bindings-sha256", TEST_HASH,
                ], cwd=BASE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                   check=False, timeout=30)
                if completed.returncode:
                    self.fail(completed.stderr.decode("utf-8", "replace"))
                observed = json.loads(observation_path.read_bytes())
                expected = oracle_by_id[slot_id]
                result = observed["observation"]
                self.assertEqual(
                    (result["observed_verdict"], result["observed_reason"]),
                    (expected["expected_verdict"], expected["expected_reason"]),
                )
                shutil.rmtree(trial_root)
                self.assertFalse(trial_root.exists())

    def test_full_public_campaign_is_84_oracle_free_fresh_processes(self):
        with tempfile.TemporaryDirectory(prefix="ck-g7-expanded-full-") as temporary:
            root = Path(temporary)
            generated = root / "generated"
            raw = root / "raw"
            scored = root / "scored"
            generator.write_campaign(PUBLIC_SEED, "ck-g7-known-r4", generated)
            completed = subprocess.run([
                sys.executable, str(HERE / "run_expanded_campaign.py"),
                "--input-manifest", str(generated / "input-manifest.json"),
                "--input-root", str(generated / "inputs"),
                "--python-bin", sys.executable,
                "--output-root", str(raw),
                "--packet-sha256", TEST_HASH,
                "--source-bindings-sha256", TEST_HASH,
            ], cwd=BASE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
               check=False, timeout=120)
            if completed.returncode:
                self.fail(completed.stderr.decode("utf-8", "replace"))
            raw_manifest = json.loads((raw / "raw-campaign-manifest.json").read_bytes())
            self.assertEqual(raw_manifest["raw_observation_count"], 84)
            self.assertFalse(raw_manifest["oracle_loaded"])
            self.assertFalse(raw_manifest["scoring_performed"])
            self.assertFalse((raw / "work").exists())
            scored_run = subprocess.run([
                sys.executable, str(HERE / "score_expanded_campaign.py"),
                "--campaign-root", str(raw),
                "--oracle", str(generated / "sealed-oracle/oracle.json"),
                "--input-manifest", str(generated / "input-manifest.json"),
                "--output-root", str(scored),
            ], cwd=BASE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
               check=False, timeout=60)
            if scored_run.returncode:
                self.fail(scored_run.stderr.decode("utf-8", "replace"))
            aggregate = json.loads((scored / "aggregate.json").read_bytes())
            self.assertTrue(aggregate["green"])
            self.assertEqual(aggregate["scored_execution_count"], 84)
            self.assertEqual(aggregate["pass_count"], 84)
            self.assertEqual(aggregate["false_promotions"], 0)
            self.assertEqual(aggregate["mutation_after_refusal_or_invalid"], 0)


if __name__ == "__main__":
    unittest.main()
