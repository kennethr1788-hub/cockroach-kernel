"""Mechanical tests for the P9 completion coordinator core."""
from __future__ import annotations

import copy
import json
import unittest

import coordinator
import records


class TestFixtures(unittest.TestCase):
    def test_two_fixed_trials_are_distinct_and_complete(self):
        promote = coordinator.trial_fixture(coordinator.PROMOTE_TRIAL_ID)
        refuse = coordinator.trial_fixture(coordinator.REFUSE_TRIAL_ID)
        self.assertEqual(promote["expected_verdict"], "PROMOTE")
        self.assertEqual(refuse["expected_verdict"], "REFUSE")
        self.assertNotEqual(promote["fixture_hash"], refuse["fixture_hash"])
        self.assertEqual(len(promote["commands"]), len(coordinator.ORDER))
        self.assertEqual(len(refuse["commands"]), len(coordinator.ORDER))
        self.assertTrue(refuse["commands"][7]["payload"]["tampered"])
        self.assertFalse(promote["commands"][7]["payload"]["tampered"])
        promote_hashes = {item["command_hash"] for item in promote["commands"]}
        refuse_hashes = {item["command_hash"] for item in refuse["commands"]}
        self.assertFalse(promote_hashes & refuse_hashes)

    def test_fixture_is_repeatable(self):
        first = coordinator.trial_fixture(coordinator.PROMOTE_TRIAL_ID)
        second = coordinator.trial_fixture(coordinator.PROMOTE_TRIAL_ID)
        self.assertEqual(records.canonical_json(first), records.canonical_json(second))


class TestCoordinator(unittest.TestCase):
    def setUp(self):
        self.fixture = coordinator.trial_fixture(coordinator.PROMOTE_TRIAL_ID)

    def test_accepts_exact_sequence_and_exports_fresh_snapshot(self):
        instance = coordinator.Coordinator(coordinator.PROMOTE_TRIAL_ID)
        for sequence, command in enumerate(self.fixture["commands"][:8]):
            receipt = instance.accept(records.canonical_json(command))
            self.assertEqual(receipt["sequence"], sequence)
            self.assertEqual(receipt["result"], "ACCEPTED")
            self.assertNotIn("verdict", receipt)
        restored = coordinator.Coordinator.restore(instance.snapshot())
        self.assertEqual(restored.next_sequence, 8)
        for command in self.fixture["commands"][8:]:
            restored.accept(command)
        self.assertEqual(restored.next_sequence, len(coordinator.ORDER))

    def test_unknown_and_dynamic_fields_are_refused(self):
        command = copy.deepcopy(self.fixture["commands"][0])
        command["payload"]["sql"] = "DROP TABLE ck.receipts"
        command["command_hash"] = records.sha256_hex(coordinator.command_body(command))
        with self.assertRaisesRegex(coordinator.CoordinatorError, "PAYLOAD_FIELDS_INVALID"):
            coordinator.validate_command(command)
        command = copy.deepcopy(self.fixture["commands"][0])
        command["operation"] = "RUN_SHELL"
        command["command_hash"] = records.sha256_hex(coordinator.command_body(command))
        with self.assertRaisesRegex(coordinator.CoordinatorError, "OPERATION_INVALID"):
            coordinator.validate_command(command)

    def test_stale_out_of_order_parent_and_replay_refuse(self):
        instance = coordinator.Coordinator(coordinator.PROMOTE_TRIAL_ID)
        with self.assertRaisesRegex(coordinator.CoordinatorError, "SEQUENCE_MISMATCH"):
            instance.accept(self.fixture["commands"][1])
        first = self.fixture["commands"][0]
        instance.accept(first)
        replay_instance = coordinator.Coordinator(coordinator.PROMOTE_TRIAL_ID)
        replay_instance.accept(first)
        replay_instance.next_sequence = 0
        replay_instance.last_hash = coordinator.GENESIS_HASH
        with self.assertRaisesRegex(coordinator.CoordinatorError, "COMMAND_REPLAY"):
            replay_instance.accept(first)
        bad_parent = copy.deepcopy(self.fixture["commands"][1])
        bad_parent["parent_hash"] = "f" * 64
        bad_parent["command_hash"] = records.sha256_hex(coordinator.command_body(bad_parent))
        with self.assertRaisesRegex(coordinator.CoordinatorError, "PARENT_HASH_MISMATCH"):
            instance.accept(bad_parent)

    def test_hash_mismatch_noncanonical_and_oversize_refuse(self):
        command = copy.deepcopy(self.fixture["commands"][0])
        command["command_hash"] = "f" * 64
        with self.assertRaisesRegex(coordinator.CoordinatorError, "COMMAND_HASH_MISMATCH"):
            coordinator.validate_command(command)
        raw = json.dumps(self.fixture["commands"][0], indent=2).encode()
        with self.assertRaisesRegex(coordinator.CoordinatorError, "COMMAND_NON_CANONICAL"):
            coordinator.validate_command_bytes(raw)
        with self.assertRaisesRegex(coordinator.CoordinatorError, "COMMAND_BYTES_INVALID"):
            coordinator.validate_command_bytes(b"x" * (records.MAX_MESSAGE_BYTES + 1))

    def test_invalid_limits_and_authority_field_refuse(self):
        vector = copy.deepcopy(self.fixture["commands"][2])
        vector["payload"]["limit"] = coordinator.MAX_VECTOR_ROWS + 1
        vector["command_hash"] = records.sha256_hex(coordinator.command_body(vector))
        with self.assertRaisesRegex(coordinator.CoordinatorError, "VECTOR_LIMIT_INVALID"):
            coordinator.validate_command(vector)
        verify = copy.deepcopy(self.fixture["commands"][7])
        verify["payload"]["verdict"] = "PROMOTE"
        verify["command_hash"] = records.sha256_hex(coordinator.command_body(verify))
        with self.assertRaisesRegex(coordinator.CoordinatorError, "PAYLOAD_FIELDS_INVALID"):
            coordinator.validate_command(verify)

    def test_snapshot_tamper_refuses(self):
        instance = coordinator.Coordinator(coordinator.PROMOTE_TRIAL_ID)
        instance.accept(self.fixture["commands"][0])
        value = json.loads(instance.snapshot())
        value["state_hash"] = "f" * 64
        raw = records.canonical_json(value)
        with self.assertRaisesRegex(coordinator.CoordinatorError, "SNAPSHOT_HASH_MISMATCH"):
            coordinator.Coordinator.restore(raw)


class TestStaticBoundary(unittest.TestCase):
    def test_fixed_plan_contains_no_worker_supplied_text(self):
        expected = {
            coordinator.Operation.COMMIT_DECLARATION,
            coordinator.Operation.STORE_CONTEXT_VECTOR,
            coordinator.Operation.QUERY_CONTEXT_VECTOR,
            coordinator.Operation.COMMIT_WORKER_RESULT,
            coordinator.Operation.STREAM_WORKER_RESULT,
            coordinator.Operation.RESUME_STREAM,
            coordinator.Operation.QUERY_MCP_LINKAGE,
            coordinator.Operation.CLEANUP_TRIAL,
        }
        self.assertEqual(set(coordinator.SQL_OPERATION_PLANS), expected)
        for plan in coordinator.SQL_OPERATION_PLANS.values():
            self.assertRegex(plan, r"^P9_[A-Z0-9_]+_V1$")


if __name__ == "__main__":
    unittest.main()
