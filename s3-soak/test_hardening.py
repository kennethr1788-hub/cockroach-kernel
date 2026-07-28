#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import cloud_adapter
import hardening
import protocol


BASE = Path(__file__).resolve().parents[1]
PRESERVED = BASE / "hardening-gate5/fixtures/s3-preserved-pairs.json"


class HardeningTests(unittest.TestCase):
    def test_failure_classes_are_stable_and_sanitized(self):
        vectors = (
            ("aws", b"ExpiredToken: token has expired", hardening.AWS_AUTHENTICATION),
            ("aws", b"AccessDenied: not authorized", hardening.AWS_AUTHORIZATION_OR_THROTTLING),
            ("cockroach", b"dial tcp: connection refused", hardening.COCKROACH_CONNECTIVITY),
            ("cockroach", b"syntax error at or near x", hardening.UNKNOWN_EXTERNAL_COMMAND),
        )
        for family, output, expected in vectors:
            with self.subTest(expected=expected):
                failure = hardening.command_failure(family, 1, output)
                self.assertEqual(failure.failure_class, expected)
                self.assertNotIn(output.decode(), str(failure))
                receipt = hardening.failure_receipt(
                    campaign_id="ck-s3-hardening-test", sequence=1,
                    stage="TEST_STAGE", request_hash="a" * 64,
                    failure=failure, utc="2026-07-27T00:00:00Z")
                self.assertFalse(receipt["raw_output_stored"])
                self.assertNotIn(output.decode(), protocol.canonical(receipt).decode())

    def test_stage_failure_is_fsynced_before_exact_cleanup(self):
        with tempfile.TemporaryDirectory(prefix="s3-stage-failure-") as temporary:
            root = Path(temporary)
            for name in ("cockroach", "ca.crt", "aws"):
                (root / name).write_bytes(b"fixture")
            config = root / "config.json"
            config.write_text(json.dumps({
                "cockroach_bin": str(root / "cockroach"),
                "cockroach_host": "proof.cockroachlabs.cloud",
                "ca_cert": str(root / "ca.crt"),
                "keychain_account": "fixture-account",
                "keychain_service": "fixture-service",
                "aws_cli": str(root / "aws"),
                "aws_profile": "ck-s3",
                "aws_region": "us-west-2",
            }), encoding="utf-8")
            evidence = root / "evidence"
            request = protocol.make_request(
                "ck-s3-hardening-test", 1, protocol.GENESIS_HASH,
                protocol.Operation.RUN_PROMOTE, "hour-01")

            def prepare(trial: Path) -> None:
                trial.mkdir()
                (trial / "promote-prepared.json").write_text(
                    json.dumps({"task_id": "ck-p9-live-promote-r1"}), encoding="utf-8")

            external = hardening.command_failure(
                "aws", 255, b"ExpiredToken: private bytes are not retained")
            with mock.patch.object(cloud_adapter, "_password", return_value=b"synthetic"), \
                    mock.patch.object(cloud_adapter, "_load_live_completion",
                                      return_value=SimpleNamespace(prepare=prepare)), \
                    mock.patch.object(cloud_adapter, "_sql", side_effect=external):
                with self.assertRaisesRegex(
                        cloud_adapter.CloudAdapterError,
                        "AWS_AUTHENTICATION"):
                    cloud_adapter.run_live(request, config, evidence)
            failure = json.loads((evidence / "failure.json").read_bytes())
            cleanup = json.loads((evidence / "cleanup.json").read_bytes())
            self.assertEqual(failure["failure_class"], hardening.AWS_AUTHENTICATION)
            self.assertEqual(failure["stage"], "PRESEED_CLEANUP")
            self.assertEqual(cleanup["status"], "PASS")
            self.assertEqual(cleanup["residue_entries"], 0)
            self.assertFalse((evidence / "trial-0001").exists())

    def test_preserved_eleven_pairs_and_expiry_exchange_twelve(self):
        frozen = json.loads(PRESERVED.read_bytes())
        self.assertEqual(len(frozen["pairs"]), 11)
        prior = protocol.GENESIS_HASH
        custody_hashes = []
        with tempfile.TemporaryDirectory(prefix="s3-custody-") as temporary:
            custody = hardening.CheckpointCustody(
                Path(temporary) / "custody", "ck-s3-20260727-release-r1")
            for expected, pair in enumerate(frozen["pairs"], 1):
                request = protocol.validate_request(pair["request"])
                result = protocol.validate_result(pair["result"], request)
                self.assertEqual(request["sequence"], expected)
                self.assertEqual(request["parent_hash"], prior)
                receipt = custody.capture(request, result)
                custody_hashes.append(receipt["receipt_hash"])
                prior = request["request_hash"]
            self.assertEqual(custody.sequence, 11)
            self.assertEqual(len(set(custody_hashes)), 11)
        exchange_12 = protocol.validate_request(frozen["exchange_12_request"])
        self.assertEqual(exchange_12["sequence"], 12)
        self.assertEqual(exchange_12["parent_hash"], prior)
        with self.assertRaisesRegex(RuntimeError, "AWS_SESSION_MARGIN_INSUFFICIENT"):
            hardening.validate_session_window(
                expires_epoch=20_000, final_exchange_epoch=19_500,
                margin_seconds=900)
        passing = hardening.validate_session_window(
            expires_epoch=20_400, final_exchange_epoch=19_500,
            margin_seconds=900)
        self.assertEqual(passing["status"], "PASS")

    def test_login_refresh_mode_requires_a_real_post_exchange_margin(self):
        with mock.patch.object(hardening.time, "time", return_value=10_000):
            pending = hardening.login_refresh_pending_receipt(
                final_exchange_deadline_epoch=20_000,
                margin_seconds=900,
                provider_receipt_hash="a" * 64,
            )
        self.assertEqual(pending["status"], "PENDING_POST_EXCHANGE_PROBE")
        self.assertFalse(pending["future_expiry_claimed"])
        early = hardening.login_refresh_postcheck_receipt(
            provider_receipt_hash="a" * 64,
            last_exchange_epoch=20_000,
            probe_epoch=20_899,
            margin_seconds=900,
            identity_output_sha256="b" * 64,
            latency_ms=7,
        )
        self.assertEqual(early["status"], "BLOCKED")
        passing = hardening.login_refresh_postcheck_receipt(
            provider_receipt_hash="a" * 64,
            last_exchange_epoch=20_000,
            probe_epoch=20_900,
            margin_seconds=900,
            identity_output_sha256="b" * 64,
            latency_ms=7,
        )
        self.assertEqual(passing["status"], "PASS")
        self.assertEqual(
            passing["stable_reason_code"],
            "AWS_LOGIN_POST_EXCHANGE_MARGIN_VERIFIED",
        )

    def test_coordinated_local_shutdown_proves_all_processes_absent(self):
        processes = [
            subprocess.Popen(["/bin/sleep", "30"]),
            subprocess.Popen(["/bin/sleep", "30"]),
            subprocess.Popen(["/bin/sleep", "30"]),
        ]
        try:
            receipt = hardening.coordinated_local_shutdown([
                ("worker", processes[2].pid),
                ("bridge", processes[0].pid),
                ("coordinator", processes[1].pid),
            ])
            self.assertEqual(receipt["status"], "PASS")
            self.assertEqual(receipt["live_roles_after_shutdown"], [])
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                    process.wait()


if __name__ == "__main__":
    unittest.main()
