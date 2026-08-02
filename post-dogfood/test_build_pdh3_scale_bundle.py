from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_bundle_tested", HERE / "build_pdh3_scale_bundle.py"
)
assert SPEC is not None and SPEC.loader is not None
bundle = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bundle
SPEC.loader.exec_module(bundle)


class BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="pdh3-bundle-test.")
        cls.root = Path(cls.temporary.name)
        cls.one = bundle.build(cls.root / "one.tgz", cls.root / "one.json")
        cls.two = bundle.build(cls.root / "two.tgz", cls.root / "two.json")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_paths_are_relative_unique_and_host_boundary_is_disjoint(self) -> None:
        self.assertEqual(len(bundle.REMOTE_FILES), len(set(bundle.REMOTE_FILES)))
        self.assertEqual(len(bundle.HOST_ONLY_FILES), len(set(bundle.HOST_ONLY_FILES)))
        self.assertFalse(set(bundle.REMOTE_FILES) & set(bundle.HOST_ONLY_FILES))
        for name in (*bundle.REMOTE_FILES, *bundle.HOST_ONLY_FILES):
            bundle.validate_relative(name)

    def test_required_runtime_and_test_sources_are_bound(self) -> None:
        required = {
            "post-dogfood/pdh3_scale_contract.py",
            "post-dogfood/run_pdh3_scale_campaign.py",
            "post-dogfood/run_pdh3_traced.py",
            "post-dogfood/run_pdh3_local_canary.py",
            "post-dogfood/pdh3_synthetic_dataset.py",
            "post-dogfood/pdh3_r12_cpu_affinity.py",
            "hardening-gate7/make_vectors.py",
            "hardening-gate7/run_campaign.py",
            "hardening-gate7/run_trial.py",
            "hardening-gate5/heldout_contract.py",
            "p4-verifier/verifier.py",
            "p7-recovery/records.py",
            "p9-cloud/records.py",
            "p9-cloud/context_vector.py",
            "p9-cloud/migrations/001_cloud.sql",
            "p9-cloud/migrations/002_runtime_grants.sql",
            "p9-cloud/migrations/003_collision_safe_vector_digest.sql",
            *bundle.SMOKE_TESTS,
        }
        self.assertTrue(required <= set(bundle.REMOTE_FILES))

    def test_deterministic_archive_and_exact_extracted_source_hashes(self) -> None:
        self.assertEqual(self.one["archive_sha256"], self.two["archive_sha256"])
        self.assertEqual(
            self.one["manifest"]["source_set_sha256"],
            self.two["manifest"]["source_set_sha256"],
        )
        extraction = self.root / "manual-extraction"
        verified = bundle.verify_and_extract(
            self.root / "one.tgz",
            extraction,
            self.one["manifest"],
            self.one["history_manifest"],
        )
        self.assertTrue(verified["exact_member_set"])
        self.assertTrue(verified["regular_files_only"])
        self.assertTrue(verified["source_bytes_match_current"])
        for row in self.one["manifest"]["files"]:
            self.assertEqual(
                bundle.file_digest(extraction / row["path"]), row["sha256"]
            )

    def test_archive_contains_only_sources_and_two_canonical_manifests(self) -> None:
        with tarfile.open(
            fileobj=io.BytesIO((self.root / "one.tgz").read_bytes()), mode="r:gz"
        ) as archive:
            members = archive.getmembers()
            names = [member.name for member in members]
            expected = set(bundle.REMOTE_FILES) | {
                bundle.MANIFEST_MEMBER,
                bundle.HISTORY_MEMBER,
            }
            self.assertEqual(set(names), expected)
            self.assertEqual(len(names), len(set(names)))
            self.assertTrue(all(member.isfile() for member in members))
            manifest_raw = archive.extractfile(bundle.MANIFEST_MEMBER).read()
            history_raw = archive.extractfile(bundle.HISTORY_MEMBER).read()
            self.assertEqual(manifest_raw, bundle.canonical(self.one["manifest"]))
            self.assertEqual(history_raw, bundle.canonical(self.one["history_manifest"]))

    def test_host_control_plane_is_hash_bound_but_not_transferred(self) -> None:
        bindings = self.one["host_only_bindings"]
        self.assertFalse(bindings["archive_transfer"])
        self.assertEqual(bindings["file_count"], len(bundle.HOST_ONLY_FILES))
        names = {row["path"] for row in bindings["files"]}
        self.assertEqual(names, set(bundle.HOST_ONLY_FILES))
        archived = {row["path"] for row in self.one["manifest"]["files"]}
        self.assertFalse(names & archived)
        self.assertFalse(self.one["manifest"]["host_control_plane_transferred"])

    def test_history_manifest_binds_all_seven_attempts_without_raw_evidence(self) -> None:
        history = self.one["history_manifest"]
        self.assertEqual(history["attempts_covered"], list(range(1, 8)))
        self.assertTrue(history["binding_only"])
        self.assertFalse(history["raw_evidence_embedded"])
        self.assertFalse(history["credential_material_copied"])
        paths = {row["path"] for row in history["entries"]}
        final_state = (
            ".pdh3-runtime/preflight-r7/attempt-07-final-retrieval/final-state.json"
        )
        final_archive = (
            ".pdh3-runtime/preflight-r7/attempt-07-final-retrieval/"
            "final-evidence.tgz"
        )
        self.assertIn(final_state, paths)
        self.assertIn(final_archive, paths)
        by_path = {row["path"]: row for row in history["entries"]}
        self.assertEqual(
            history["attempt_07_final_state_sha256"], by_path[final_state]["sha256"]
        )
        self.assertEqual(
            history["attempt_07_final_evidence_archive_sha256"],
            by_path[final_archive]["sha256"],
        )
        # Only the manifest member is transferred; none of its bound evidence is.
        archive_names = {row["path"] for row in self.one["manifest"]["files"]}
        self.assertFalse(paths & archive_names)

    def test_production_launch_binds_contract_and_omits_store_size_flag(self) -> None:
        launch = self.one["manifest"]["production_launch"]
        bindings = launch["argument_bindings"]
        self.assertIsNone(bindings["store_size"])
        self.assertEqual(
            bindings["setup_success_margin_seconds"],
            bundle.load_contract().SETUP_SUCCESS_MARGIN_SECONDS,
        )
        self.assertEqual(launch["store_size_flag"], "ABSENT")
        self.assertNotIn("--store-size", launch["controller_argv_template"])
        self.assertNotIn("--store-size", launch["traced_argv_template"])
        contract = bundle.load_contract()
        contract.validate_production_arguments(bindings)
        self.assertEqual(
            launch["traced_argv_template"][-len(launch["controller_argv_template"]):],
            launch["controller_argv_template"],
        )
        self.assertEqual(
            launch["launch_environment_template"]["PDH3_PACKET_SHA256"],
            "__FROZEN_PACKET_SHA256__",
        )
        self.assertIn("__TRACER_ROOT__", launch["tracer_binary_template"])
        self.assertEqual(
            launch["traced_argv_template"][
                launch["traced_argv_template"].index("--tracer") + 1
            ],
            launch["tracer_binary_template"],
        )
        self.assertEqual(
            launch["controller_argv_template_sha256"],
            bundle.digest(bundle.canonical(launch["controller_argv_template"])),
        )
        self.assertEqual(
            launch["traced_argv_template_sha256"],
            bundle.digest(bundle.canonical(launch["traced_argv_template"])),
        )
        self.assertEqual(
            launch["launch_environment_template_sha256"],
            bundle.digest(bundle.canonical(launch["launch_environment_template"])),
        )
        self.assertEqual(
            launch["tracer_setup_template_sha256"],
            bundle.digest(bundle.canonical(launch["tracer_setup_argv_templates"])),
        )
        self.assertEqual(
            {row["sha256"] for row in launch["tracer_artifact_bindings"]},
            {contract.STRACE_DEB_SHA256, contract.LIBUNWIND8_DEB_SHA256},
        )
        self.assertEqual(
            launch["tracer_binary_sha256"], contract.STRACE_BINARY_SHA256
        )
        self.assertTrue(
            all(isinstance(argv, list) and argv[0] == "dpkg-deb"
                for argv in launch["tracer_setup_argv_templates"])
        )
        self.assertFalse(launch["shell_interpolation"])

    def test_member_validator_rejects_missing_extra_duplicate_and_unsafe(self) -> None:
        def regular(name: str) -> tarfile.TarInfo:
            info = tarfile.TarInfo(name)
            info.type = tarfile.REGTYPE
            return info

        bundle.validate_tar_members([regular("a")], {"a"})
        cases = (
            ([regular("a")], {"a", "b"}),
            ([regular("a"), regular("b")], {"a"}),
            ([regular("a"), regular("a")], {"a"}),
            ([regular("/absolute")], {"/absolute"}),
            ([regular("a/../escape")], {"a/../escape"}),
        )
        for members, expected in cases:
            with self.subTest(names=[member.name for member in members]):
                with self.assertRaises(bundle.BundleError):
                    bundle.validate_tar_members(members, expected)
        symlink = tarfile.TarInfo("a")
        symlink.type = tarfile.SYMTYPE
        symlink.linkname = "elsewhere"
        with self.assertRaises(bundle.BundleError):
            bundle.validate_tar_members([symlink], {"a"})

    def test_manifest_verifier_rejects_tampered_source_hash(self) -> None:
        tampered = json.loads(bundle.canonical(self.one["manifest"]))
        tampered["files"][0]["sha256"] = "0" * 64
        body = {
            key: value for key, value in tampered.items() if key != "manifest_sha256"
        }
        tampered["manifest_sha256"] = bundle.digest(bundle.canonical(body))
        with self.assertRaises(bundle.BundleError):
            bundle.verify_and_extract(
                self.root / "one.tgz",
                self.root / "tampered-extraction",
                tampered,
                self.one["history_manifest"],
            )
        self.assertFalse((self.root / "tampered-extraction").exists())

    def test_extracted_bundle_smoke_is_green_but_explicitly_not_scale_proof(self) -> None:
        smoke = bundle.run_extracted_bundle_smoke(
            self.root / "one.tgz",
            self.one,
            self.root / "smoke-extraction",
            self.root / "smoke-receipt.json",
        )
        self.assertTrue(smoke["green"])
        self.assertFalse(smoke["target_scale_proof"])
        self.assertFalse(smoke["production_claim_allowed"])
        self.assertEqual(
            smoke["evidence_class"], "EXTRACTED_BUNDLE_INTEGRITY_SMOKE_ONLY"
        )
        self.assertIn("NO_FULL_CARDINALITY_SETUP", smoke["limitations"])
        self.assertIn("NO_24_HOUR_MEASUREMENT", smoke["limitations"])
        self.assertEqual(smoke["version"], "ck-pdh3-extracted-bundle-smoke-v3")
        self.assertEqual(smoke["failed_checks"], [])
        self.assertTrue(all(row["status"] == "PASS" for row in smoke["tests"]))

    def test_smoke_command_evidence_preserves_only_bounded_tail(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["python3"], returncode=7,
            stdout=b"a" * 5000,
            stderr=b"prefix:" + b"b" * 5000,
        )
        evidence = bundle.smoke_command_evidence(path="synthetic", completed=completed)
        self.assertEqual(evidence["status"], "FAIL")
        self.assertEqual(evidence["returncode"], 7)
        self.assertEqual(len(evidence["stdout_tail"].encode()), 4096)
        self.assertEqual(len(evidence["stderr_tail"].encode()), 4096)
        self.assertEqual(evidence["stdout_sha256"], bundle.digest(completed.stdout))

    def test_smoke_command_timeout_is_normalized(self) -> None:
        timeout = subprocess.TimeoutExpired(
            cmd=["python3"], timeout=300, output=b"partial", stderr=b"blocked"
        )
        evidence = bundle.smoke_command_evidence(path="synthetic", timeout=timeout)
        self.assertEqual(evidence["status"], "TIMEOUT")
        self.assertIsNone(evidence["returncode"])
        self.assertEqual(evidence["timeout_seconds"], 300)


if __name__ == "__main__":
    unittest.main()
