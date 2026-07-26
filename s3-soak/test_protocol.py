#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

import protocol


def metrics() -> dict[str, int]:
    return {name: 1 for name in protocol.CLOUD_METRIC_FIELDS}


def hashes() -> dict[str, str]:
    return {name: "a" * 64 for name in protocol.EVIDENCE_HASH_FIELDS}


class ProtocolTests(unittest.TestCase):
    def request(self, sequence: int = 1):
        operation = protocol.Operation.RUN_PROMOTE if sequence % 2 else protocol.Operation.RUN_REFUSE
        parent = protocol.GENESIS_HASH if sequence == 1 else "b" * 64
        return protocol.make_request("ck-s3-smoke-r1", sequence, parent,
                                     operation, f"hour-{sequence:02d}")

    def test_round_trip(self):
        request = self.request()
        self.assertEqual(protocol.decode_request(protocol.canonical(request)), request)
        result = protocol.make_result(request, metrics(), hashes())
        self.assertEqual(protocol.decode_result(protocol.canonical(result), request), result)

    def test_unknown_field_rejected(self):
        request = self.request()
        request["shell"] = "rm -rf /"
        with self.assertRaisesRegex(protocol.ProtocolError, "REQUEST_FIELDS_INVALID"):
            protocol.validate_request(request)

    def test_injection_operation_rejected(self):
        request = self.request()
        request["operation"] = "RUN_PROMOTE; DROP TABLE ck.tasks"
        request["request_hash"] = protocol.sha256(protocol.request_body(request))
        with self.assertRaisesRegex(protocol.ProtocolError, "OPERATION_INVALID"):
            protocol.validate_request(request)

    def test_duplicate_and_out_of_order_are_caller_enforced(self):
        one = self.request(1)
        two = self.request(2)
        self.assertNotEqual(one["request_hash"], two["request_hash"])
        self.assertEqual(two["sequence"], 2)

    def test_hash_mismatch_rejected(self):
        request = self.request()
        request["payload"]["scenario"] = "changed"
        with self.assertRaisesRegex(protocol.ProtocolError, "REQUEST_HASH_MISMATCH"):
            protocol.validate_request(request)

    def test_result_linkage_rejected(self):
        request = self.request()
        result = protocol.make_result(request, metrics(), hashes())
        other = self.request(2)
        with self.assertRaisesRegex(protocol.ProtocolError, "RESULT_LINKAGE_INVALID"):
            protocol.validate_result(result, other)

    def test_bool_hour_rejected(self):
        request = self.request()
        request["payload"]["hour"] = True
        request["request_hash"] = protocol.sha256(protocol.request_body(request))
        with self.assertRaisesRegex(protocol.ProtocolError, "PAYLOAD_HOUR_INVALID"):
            protocol.validate_request(request)

    def test_out_of_order_request_file_blocks_coordinator(self):
        with tempfile.TemporaryDirectory(prefix="s3-out-of-order-") as temporary:
            root = Path(temporary)
            bridge = root / "bridge"
            (bridge / "requests").mkdir(parents=True)
            (bridge / "results").mkdir()
            evidence = root / "evidence"
            request = self.request(2)
            (bridge / "requests/request-0002.json").write_bytes(
                protocol.canonical(request))
            command = [
                sys.executable, str(Path(__file__).parent / "host_coordinator.py"),
                "--bridge-root", str(bridge), "--evidence-root", str(evidence),
                "--campaign-id", request["campaign_id"], "--expected-requests", "2",
                "--lambda-call-ceiling", "2", "--cockroach-operation-ceiling", "18",
                "--deadline-epoch", str(int(time.time()) + 20),
                "--mode", "fixture", "--heartbeat-seconds", "1",
            ]
            result = subprocess.run(command, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=10, check=False)
            self.assertEqual(result.returncode, 1, result.stdout.decode(errors="replace"))
            records = [json.loads(line) for line in
                       (evidence / "coordinator.ndjson").read_bytes().splitlines()]
            self.assertEqual(records[-1]["event"], "COORDINATOR_BLOCKED")

    def test_coordinator_waits_for_completion_marker(self):
        with tempfile.TemporaryDirectory(prefix="s3-completion-marker-") as temporary:
            root = Path(temporary)
            bridge = root / "bridge"
            (bridge / "requests").mkdir(parents=True)
            (bridge / "results").mkdir()
            evidence = root / "evidence"
            marker = root / "worker-complete"
            campaign = "ck-s3-completion-proof"
            request = protocol.make_request(
                campaign, 1, protocol.GENESIS_HASH,
                protocol.Operation.RUN_PROMOTE, "hour-01")
            (bridge / "requests/request-0001.json").write_bytes(
                protocol.canonical(request))
            command = [
                sys.executable, str(Path(__file__).parent / "host_coordinator.py"),
                "--bridge-root", str(bridge), "--evidence-root", str(evidence),
                "--campaign-id", campaign, "--expected-requests", "1",
                "--lambda-call-ceiling", "1", "--cockroach-operation-ceiling", "9",
                "--deadline-epoch", str(int(time.time()) + 20),
                "--mode", "fixture", "--heartbeat-seconds", "1",
                "--completion-marker", str(marker),
            ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            result_path = bridge / "results/result-0001.json"
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline and not result_path.exists():
                time.sleep(0.05)
            self.assertTrue(result_path.exists())
            self.assertIsNone(process.poll(), "coordinator exited before marker")
            marker.write_bytes(b"GREEN\n")
            stdout, _ = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, stdout.decode(errors="replace"))
            records = [json.loads(line) for line in
                       (evidence / "coordinator.ndjson").read_bytes().splitlines()]
            self.assertEqual(records[-1]["event"], "COORDINATOR_GREEN")


if __name__ == "__main__":
    unittest.main()
