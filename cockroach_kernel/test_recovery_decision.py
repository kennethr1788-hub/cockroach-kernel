import unittest

from cockroach_kernel.continuation_brief import build_brief, digest
from cockroach_kernel.recovery_decision import DecisionError, evaluate_recovery, validate_decision


def rep(name, content, *, status="VERIFIED", lineage="e" * 64, facts=None):
    return {"representation_id": name, "content_hash": content * 64,
            "lineage_hash": lineage, "status": status, "facts": facts or {"state": "ready"}}


class RecoveryDecisionTests(unittest.TestCase):
    def test_agreement_allows_supported_continuation(self):
        decision = evaluate_recovery([rep("a", "a"), rep("b", "b")])
        self.assertEqual(decision["outcome"], "CONTINUE")
        self.assertEqual(decision["conflicts"], [])
        validate_decision(decision)

    def test_conflict_blocks_unsafe_continuation(self):
        decision = evaluate_recovery([
            rep("a", "a", facts={"state": "ready"}),
            rep("b", "b", facts={"state": "broken"}),
        ])
        self.assertEqual(decision["outcome"], "HUMAN_REVIEW_REQUIRED")
        self.assertIn("FACT_CONFLICT", decision["reason_codes"])

    def test_tampered_evidence_is_quarantined(self):
        decision = evaluate_recovery([rep("a", "a"), rep("b", "b", status="TAMPERED")])
        self.assertEqual(decision["outcome"], "QUARANTINE")
        self.assertIn("TAMPERED_REPRESENTATION", decision["reason_codes"])

    def test_missing_lineage_requires_review(self):
        decision = evaluate_recovery([rep("a", "a", lineage=None)])
        self.assertEqual(decision["outcome"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(decision["missing_lineage"], ["a"])

    def test_duplicate_conflict_is_quarantined(self):
        decision = evaluate_recovery([rep("a", "a"), rep("a", "b")])
        self.assertEqual(decision["outcome"], "QUARANTINE")
        self.assertEqual(decision["duplicate_ids"], ["a"])

    def test_same_hash_duplicate_with_changed_facts_is_quarantined(self):
        decision = evaluate_recovery([
            rep("a", "a", facts={"state": "ready"}),
            rep("a", "a", facts={"state": "broken"}),
        ])
        self.assertEqual(decision["outcome"], "QUARANTINE")
        self.assertEqual(decision["duplicate_ids"], ["a"])

    def test_permutation_invariant(self):
        first = evaluate_recovery([rep("a", "a"), rep("b", "b")])
        second = evaluate_recovery([rep("b", "b"), rep("a", "a")])
        self.assertEqual(first, second)

    def test_overflow_fails_closed(self):
        with self.assertRaises(DecisionError):
            evaluate_recovery([rep(str(i), "a") for i in range(33)])

    def test_tampered_decision_fails_validation(self):
        decision = evaluate_recovery([rep("a", "a")])
        decision["reason_codes"] = ["FACT_CONFLICT"]
        with self.assertRaises(DecisionError):
            validate_decision(decision)

    def test_decision_is_bound_into_new_continuation_brief(self):
        result = {"receipt_hash": "b" * 64, "local_verdict": "PROMOTE",
                  "fresh_context": True, "value": "declared"}
        result["result_hash"] = digest(result)
        decision = evaluate_recovery([rep("a", "a")])
        brief = build_brief(result, [{"trajectory_id": "t1", "content_hash": "c" * 64}],
                            recovery_decision=decision)
        self.assertEqual(brief["recovery_decision"]["decision_id"], decision["decision_id"])


if __name__ == "__main__":
    unittest.main()
