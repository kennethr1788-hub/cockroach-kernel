from __future__ import annotations

import copy
import unittest

import golden as g
import make_fixtures as fx


class TestCanonicalValidation(unittest.TestCase):
    def test_canonical_json(self):
        self.assertEqual(g.canonical_json({"b": 1, "a": 2}), b'{"a":2,"b":1}')

    def test_unknown_field_rejected(self):
        bad = dict(fx.BASE_POLICY, hidden=True)
        with self.assertRaisesRegex(g.GoldenError, "UNKNOWN_FIELD"):
            g.validate_policy(bad)

    def test_size_cap(self):
        with self.assertRaisesRegex(g.GoldenError, "RECORD_TOO_LARGE"):
            g.canonical_json({"pad": "x" * g.MAX_RECORD_BYTES})

    def test_incident_hash_binding(self):
        bad = copy.deepcopy(fx.INCIDENTS[0])
        bad["critical"] = True
        with self.assertRaisesRegex(g.GoldenError, "STALE_HASH"):
            g.validate_incident(bad)

    def test_success_and_failure_coverage_required(self):
        with self.assertRaisesRegex(g.GoldenError, "INCIDENT_COVERAGE_MISSING"):
            g.validate_incident_set([fx.INCIDENTS[0]])


class TestReplay(unittest.TestCase):
    def test_safe_proposal_promotes(self):
        result = g.replay_proposal(fx.PROPOSALS["proposal-safe"], fx.BASE_POLICY, fx.INCIDENTS)
        self.assertEqual(result["receipt"]["outcome"], "PROMOTE")
        self.assertTrue(result["replay"]["passed"])
        self.assertEqual(len(result["replay"]["results"]), len(fx.INCIDENTS))
        self.assertIn("golden_pair", result)

    def test_regression_rejects_with_replay(self):
        result = g.replay_proposal(fx.PROPOSALS["proposal-regression"],
                                   fx.BASE_POLICY, fx.INCIDENTS)
        self.assertEqual(result["receipt"]["outcome"], "REJECT")
        self.assertEqual(result["receipt"]["reason"], "REGRESSION_DETECTED")
        self.assertFalse(result["replay"]["passed"])

    def test_structural_rejections_are_receipted(self):
        expected = {
            "proposal-weaken-ordinary": "SAFETY_INVARIANT_FAILED",
            "proposal-weaken-critical": "SAFETY_INVARIANT_FAILED",
            "proposal-unsafe-correlation": "SAFETY_INVARIANT_FAILED",
            "proposal-unsafe-correlation-low": "SAFETY_INVARIANT_FAILED",
            "proposal-stale": "STALE_BASE_POLICY",
            "proposal-noop": "NO_POLICY_CHANGE",
        }
        for name, reason in expected.items():
            with self.subTest(name=name):
                result = g.replay_proposal(fx.PROPOSALS[name], fx.BASE_POLICY, fx.INCIDENTS)
                self.assertEqual(result["outcome"], "REJECT")
                self.assertEqual(result["reason"], reason)
                self.assertRegex(result["receipt_hash"], r"^[0-9a-f]{64}$")

    def test_every_fixture_proposal_has_exactly_one_outcome_receipt(self):
        for name, proposal in fx.PROPOSALS.items():
            with self.subTest(name=name):
                result = g.replay_proposal(proposal, fx.BASE_POLICY, fx.INCIDENTS)
                receipt = result["receipt"] if "receipt" in result else result
                self.assertIn(receipt["outcome"], ("PROMOTE", "REJECT"))
                self.assertRegex(receipt["receipt_hash"], r"^[0-9a-f]{64}$")
                self.assertEqual(receipt["proposal_hash"], g.sha256_hex(proposal))
                self.assertEqual(receipt["incident_set_hash"],
                                 g.incident_set_hash(fx.INCIDENTS))
                self.assertNotIn("authority", result)

    def test_malformed_and_unsupported_are_receipted(self):
        malformed = copy.deepcopy(fx.PROPOSALS["proposal-safe"])
        del malformed["reflection_hash"]
        self.assertEqual(g.replay_proposal(malformed, fx.BASE_POLICY, fx.INCIDENTS)["reason"],
                         "MISSING_FIELD")
        unsupported = copy.deepcopy(fx.PROPOSALS["proposal-safe"])
        unsupported["version"] = "p8-v999"
        self.assertEqual(g.replay_proposal(unsupported, fx.BASE_POLICY, fx.INCIDENTS)["reason"],
                         "UNSUPPORTED_SCHEMA")

    def test_proposal_order_independent(self):
        forward = [g.replay_proposal(fx.PROPOSALS[name], fx.BASE_POLICY, fx.INCIDENTS)
                   for name in sorted(fx.PROPOSALS)]
        reverse = [g.replay_proposal(fx.PROPOSALS[name], fx.BASE_POLICY, fx.INCIDENTS)
                   for name in reversed(sorted(fx.PROPOSALS))]
        self.assertEqual({g.sha256_hex(item) for item in forward},
                         {g.sha256_hex(item) for item in reverse})

    def test_five_repeat_determinism(self):
        outputs = [g.canonical_json(g.replay_proposal(
            fx.PROPOSALS["proposal-safe"], fx.BASE_POLICY, fx.INCIDENTS))
            for _ in range(5)]
        self.assertEqual(len(set(outputs)), 1)

    def test_incident_order_independent(self):
        a = g.replay_proposal(fx.PROPOSALS["proposal-safe"], fx.BASE_POLICY, fx.INCIDENTS)
        b = g.replay_proposal(fx.PROPOSALS["proposal-safe"], fx.BASE_POLICY,
                              list(reversed(fx.INCIDENTS)))
        self.assertEqual(a, b)


class TestRollback(unittest.TestCase):
    def test_exact_rollback(self):
        result = g.replay_proposal(fx.PROPOSALS["proposal-safe"], fx.BASE_POLICY, fx.INCIDENTS)
        receipt = g.build_rollback_receipt(result["receipt"], fx.SAFE_POLICY, fx.BASE_POLICY)
        self.assertEqual(receipt["from_policy_hash"], g.sha256_hex(fx.SAFE_POLICY))
        self.assertEqual(receipt["to_policy_hash"], g.sha256_hex(fx.BASE_POLICY))

    def test_wrong_rollback_target_refuses(self):
        result = g.replay_proposal(fx.PROPOSALS["proposal-safe"], fx.BASE_POLICY, fx.INCIDENTS)
        with self.assertRaisesRegex(g.GoldenError, "ROLLBACK_TARGET_MISMATCH"):
            g.build_rollback_receipt(result["receipt"], fx.SAFE_POLICY, fx.SAFE_POLICY)


if __name__ == "__main__":
    unittest.main()
