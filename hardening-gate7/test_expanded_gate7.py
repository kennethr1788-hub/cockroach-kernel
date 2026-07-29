#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import shutil
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


def canonical(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


class ExpandedGate7Tests(unittest.TestCase):
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
        helper = next(row for row in rows
                      if row["path"] == "s3-soak/freeze_evidence_manifest.py")
        self.assertEqual(helper["mode"], "0755")
        self.assertEqual(len(helper["sha256"]), 64)
        self.assertEqual(sum(".s3-runtime" in row["path"] for row in rows), 0)
        self.assertEqual(sum(".hardening-runtime" in row["path"] for row in rows), 0)

    def test_bulk_live_track_generation_is_exact_and_synthetic(self):
        with tempfile.TemporaryDirectory(prefix="ck-g7-bulk-") as temporary:
            root = Path(temporary) / "generated"
            manifest = bulk.build_sql("ck-g7r3-public-unit", root)
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
            self.assertEqual(manifest["unique_vector_digests"], 20000)
            self.assertEqual(sum(len(rows) for rows in manifest["batches"].values()), 184)
            self.assertEqual(
                len(json.loads((root / "query-specs.json").read_bytes())), 200
            )
            for path in root.iterdir():
                self.assertNotIn(b"/Users/", path.read_bytes())
                self.assertNotIn(b"password", path.read_bytes().lower())

    def test_run2_vector_collision_is_reproduced_and_run3_binding_is_unique(self):
        old_seen = set()
        old_collisions = 0
        new_seen = set()
        for task_index in range(2000):
            for sequence in range(10):
                old = bulk.context_vector.context_vector(
                    f"continue synthetic task {task_index} trajectory segment {sequence}",
                    "ck-g7r3-vector-proof",
                )
                old_digest = bulk.context_vector.vector_digest(old)
                old_collisions += old_digest in old_seen
                old_seen.add(old_digest)
                new = bulk.context_vector.context_vector(
                    bulk.vector_text(task_index, sequence), "ck-g7r3-vector-proof",
                )
                new_digest = bulk.context_vector.vector_digest(new)
                self.assertNotIn(new_digest, new_seen)
                new_seen.add(new_digest)
        self.assertGreater(old_collisions, 0)
        self.assertEqual(len(new_seen), 20000)

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
            with mock.patch.object(bulk.cloud_adapter, "_sql", side_effect=[transient, (b"ok", 2)]):
                elapsed, hashes, retries = bulk.execute_batches(
                    {}, {}, root, manifest, "vectors", journal)
            self.assertEqual((elapsed, retries, len(hashes)), (2, 1, 1))
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
            (generated / "query-specs.json").write_text("[]", encoding="utf-8")
            manifest_body = {
                "version": "hardening-gate7-live-bulk-manifest-v2",
                "campaign_id": campaign_id,
                "counts": {"tasks": 1, "events": 1, "receipts": 1,
                           "vectors": 1, "vector_queries": 0},
                "batches": batches,
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
                if file is not None and Path(file).name == "cleanup.sql":
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
            self.assertEqual(calls["cleanup"], 2)
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
