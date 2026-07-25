import unittest

from ledger import EvidenceBudget, LedgerError, canonical_json, deterministic_verdict, sha256_hex, trajectory_hash, validate_candidate


def candidate(**overrides):
    value = {
        "version": "p3-v1", "candidate_id": "cand-1", "task_id": "task-1",
        "source_event_id": "evt-1", "prefix": [{"op": "keep"}],
        "state_hash": "state", "receipt_hash": "receipt", "policy_version": "p1",
        "votes": ["APPROVE", "APPROVE", "APPROVE"], "policy_veto": False,
        "tampered": False, "unsafe": False, "warrant_state": "ISSUED",
        "retention_class": "core",
    }
    value.update(overrides)
    return value


class LedgerTests(unittest.TestCase):
    def test_canonical_and_hash(self):
        self.assertEqual(canonical_json({"b": 2, "a": 1}), b'{"a":1,"b":2}')
        self.assertEqual(sha256_hex({"a": 1}), sha256_hex({"a": 1}))

    def test_unknown_and_malformed(self):
        with self.assertRaises(LedgerError):
            validate_candidate({**candidate(), "unexpected": 1})
        self.assertEqual(deterministic_verdict({}), ("INVALID", "MALFORMED_RECORD"))

    def test_verdict_vectors(self):
        self.assertEqual(deterministic_verdict(candidate()), ("PROMOTE", "QUORUM_PASS"))
        self.assertEqual(deterministic_verdict(candidate(unsafe=True)), ("REFUSE", "POLICY_UNSAFE"))
        self.assertEqual(deterministic_verdict(candidate(tampered=True)), ("REFUSE", "TAMPERED_EVIDENCE"))
        self.assertEqual(deterministic_verdict(candidate(policy_veto=True)), ("REFUSE", "POLICY_VETO"))
        self.assertEqual(deterministic_verdict(candidate(votes=["APPROVE"])), ("REFUSE", "QUORUM_MISSING"))
        self.assertEqual(deterministic_verdict(candidate(warrant_state="CONSUMED")), ("REFUSE", "WARRANT_REPLAY"))

    def test_trajectory_hash_determinism(self):
        one = {"version": "p3-v1", "event_id": "evt-1", "task_id": "task-1", "sequence": 0,
               "parent_event_id": None, "state": {"x": 1}, "state_hash": sha256_hex({"x": 1})}
        two = {"version": "p3-v1", "event_id": "evt-2", "task_id": "task-1", "sequence": 1,
               "parent_event_id": "evt-1", "state": {"x": 2}, "state_hash": sha256_hex({"x": 2})}
        self.assertEqual(trajectory_hash([two, one]), trajectory_hash([one, two]))

    def test_budget(self):
        budget = EvidenceBudget(1, 2, 3, 4, 5)
        self.assertEqual(sum(budget.as_record().values()), 15)


if __name__ == "__main__":
    unittest.main()
