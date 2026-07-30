#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

import protocol
import freeze_evidence_manifest
import coordinator_guard
import remote_bridge


def metrics() -> dict[str, int]:
    return {name: 1 for name in protocol.CLOUD_METRIC_FIELDS}


def hashes() -> dict[str, str]:
    return {name: "a" * 64 for name in protocol.EVIDENCE_HASH_FIELDS}


class ProtocolTests(unittest.TestCase):
    def test_remote_bridge_and_coordinator_share_atomic_staging_contract(self):
        with tempfile.TemporaryDirectory(prefix="s3-topology-proof-") as temporary:
            root = Path(temporary)
            bridge = root / "bridge"
            evidence = root / "evidence"
            identity = root / "identity"
            known_hosts = root / "known_hosts"
            log = root / "bridge.ndjson"
            identity.write_text("proof", encoding="utf-8")
            identity.chmod(0o600)
            known_hosts.write_text("proof", encoding="utf-8")
            campaign = "ck-s3-topology-proof"
            request_raw_by_name: dict[str, bytes] = {}
            parent_hash = protocol.GENESIS_HASH
            for sequence in range(1, 13):
                operation = (protocol.Operation.RUN_PROMOTE if sequence % 2
                             else protocol.Operation.RUN_REFUSE)
                request = protocol.make_request(
                    campaign, sequence, parent_hash, operation,
                    f"hour-{sequence:02d}")
                request_raw_by_name[f"request-{sequence:04d}.json"] = protocol.canonical(request)
                parent_hash = request["request_hash"]
            uploaded: dict[str, bytes] = {}
            observed: dict[str, object] = {
                "request_entries_during_transfer": [],
                "target_parents": [],
            }

            coordinator = subprocess.Popen([
                sys.executable, str(Path(__file__).parent / "host_coordinator.py"),
                "--bridge-root", str(bridge), "--evidence-root", str(evidence),
                "--campaign-id", campaign, "--expected-requests", "12",
                "--lambda-call-ceiling", "12", "--cockroach-operation-ceiling", "108",
                "--deadline-epoch", str(int(time.time()) + 20),
                "--mode", "fixture", "--heartbeat-seconds", "1",
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            def fake_transport(command: list[str], timeout: int = 30):
                del timeout
                if command[0] == "/usr/bin/ssh" and "test" in command:
                    return subprocess.CompletedProcess(command, 0, stdout=b"")
                if command[0] == "/usr/bin/scp":
                    source, destination = command[-2:]
                    if source.startswith("root@example.invalid:"):
                        request_name = Path(source.split(":", 1)[1]).name
                        request_raw = request_raw_by_name[request_name]
                        target = Path(destination)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        midpoint = len(request_raw) // 2
                        target.write_bytes(request_raw[:midpoint])
                        observed["request_entries_during_transfer"].append(
                            list((bridge / "requests").iterdir()))
                        observed["target_parents"].append(target.parent)
                        time.sleep(0.02)
                        with target.open("ab") as handle:
                            handle.write(request_raw[midpoint:])
                        return subprocess.CompletedProcess(command, 0, stdout=b"")
                    uploaded[destination] = Path(source).read_bytes()
                    return subprocess.CompletedProcess(command, 0, stdout=b"")
                if command[0] == "/usr/bin/ssh" and "mv" in command:
                    return subprocess.CompletedProcess(command, 0, stdout=b"")
                return subprocess.CompletedProcess(command, 1, stdout=b"unexpected")

            arguments = [
                "remote_bridge.py", "--host", "example.invalid", "--port", "22",
                "--user", "root", "--identity", str(identity),
                "--known-hosts", str(known_hosts),
                "--remote-root", f"/workspace/{campaign}/bridge",
                "--local-root", str(bridge), "--campaign-id", campaign,
                "--expected-requests", "12",
                "--deadline-epoch", str(int(time.time()) + 20),
                "--heartbeat-seconds", "1", "--log", str(log),
            ]
            try:
                with mock.patch.object(remote_bridge, "run", side_effect=fake_transport), \
                        mock.patch.object(sys, "argv", arguments):
                    bridge_exit = remote_bridge.main()
                self.assertEqual(
                    bridge_exit, 0,
                    log.read_text(encoding="utf-8") if log.exists() else "bridge log missing",
                )
                coordinator_output, _ = coordinator.communicate(timeout=20)
            finally:
                if coordinator.poll() is None:
                    coordinator.terminate()
                    coordinator.wait(timeout=5)
            self.assertEqual(coordinator.returncode, 0, coordinator_output)
            for index, entries in enumerate(
                    observed["request_entries_during_transfer"]):
                self.assertEqual(len(entries), index)
                self.assertTrue(all(path.name.endswith(".json") for path in entries))
            self.assertEqual(
                observed["target_parents"],
                [(bridge / "staging").resolve() for _ in range(12)],
            )
            self.assertEqual(
                len([key for key in uploaded if key.endswith(".json.tmp")]), 12)
            self.assertEqual(list((bridge / "staging").iterdir()), [])
            events = [json.loads(line)["event"] for line in log.read_bytes().splitlines()]
            self.assertEqual(events[-1], "BRIDGE_GREEN")

    def test_coordinator_rejects_temporary_file_in_watched_directory(self):
        with tempfile.TemporaryDirectory(prefix="s3-watched-temp-proof-") as temporary:
            root = Path(temporary)
            requests = root / "requests"
            requests.mkdir()
            (requests / "request-0001.json.tmp").write_bytes(b"partial")
            with self.assertRaisesRegex(
                    RuntimeError, "REQUEST_FILE_UNKNOWN"):
                import host_coordinator
                host_coordinator.verify_request_directory(requests, 1, set())

    def test_frozen_evidence_manifest_is_sorted_and_atomic(self):
        with tempfile.TemporaryDirectory(prefix="s3-manifest-proof-") as temporary:
            campaign = Path(temporary) / "ck-s3-proof"
            production = campaign / "production"
            production.mkdir(parents=True)
            (production / "b.txt").write_bytes(b"b")
            nested = production / "nested"
            nested.mkdir()
            (nested / "a.txt").write_bytes(b"a")
            output = campaign / "production-tree.sha256"
            original = freeze_evidence_manifest.ROOT_RE
            freeze_evidence_manifest.ROOT_RE = re.compile(
                re.escape(production.resolve().as_posix()))
            try:
                result = freeze_evidence_manifest.freeze(production, output)
            finally:
                freeze_evidence_manifest.ROOT_RE = original
            lines = output.read_text(encoding="utf-8").splitlines()
            self.assertEqual(result["files"], 2)
            self.assertTrue(lines[0].endswith("  production/b.txt"))
            self.assertTrue(lines[1].endswith("  production/nested/a.txt"))
            self.assertFalse(output.with_name(output.name + ".tmp").exists())

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

    def test_guard_ignores_only_in_progress_final_fragment(self):
        with tempfile.TemporaryDirectory(prefix="s3-chain-fragment-") as temporary:
            path = Path(temporary) / "chain.ndjson"
            core = {
                "version": "proof-log-v1", "campaign_id": "ck-s3-fragment-proof",
                "sequence": 1, "previous_hash": protocol.GENESIS_HASH,
                "event": "HEARTBEAT", "details": {},
                "utc": "2026-07-26T00:00:00Z", "monotonic_ns": 1,
            }
            record = {**core, "event_hash": protocol.sha256(core)}
            path.write_bytes(protocol.canonical(record) + b"\n{\"partial\":")
            self.assertEqual(coordinator_guard.read_chain(path), [record])

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
