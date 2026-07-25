import unittest

from verifier import Quarantine, digest, verify


def record(**overrides):
    payload = {"op": "continue", "sequence": 1}
    value = {
        "version": "p4-v1", "candidate_id": "cand-1", "source_receipt_hash": "a" * 64,
        "payload": payload, "payload_hash": digest(payload), "schema_version": "p4-v1",
        "provenance": {"source": "synthetic-receipt"}, "supported": True,
        "one_use_state": "ISSUED", "quarantined": False, "policy_veto": False,
        "requested_paths": ["src/main.py"], "declared_paths": ["src/main.py"],
    }
    value.update(overrides)
    return value


class VerifierTests(unittest.TestCase):
    def test_promotion(self):
        self.assertEqual(verify(record()), ("PROMOTE", "VERIFIED"))

    def test_malformed_and_unknown(self):
        self.assertEqual(verify(None), ("INVALID", "MALFORMED_RECORD"))
        self.assertEqual(verify({**record(), "extra": 1}), ("INVALID", "UNKNOWN_FIELD"))

    def test_hash_and_schema(self):
        self.assertEqual(verify(record(payload_hash="0" * 64)), ("REFUSE", "HASH_MISMATCH"))
        self.assertEqual(verify(record(schema_version="p4-v0")), ("REFUSE", "UNSUPPORTED_SCHEMA"))

    def test_replay_unsafe_and_policy(self):
        self.assertEqual(verify(record(one_use_state="CONSUMED")), ("REFUSE", "REPLAYED_TICKET"))
        self.assertEqual(verify(record(requested_paths=["../escape"])), ("REFUSE", "UNSAFE_PATH"))
        self.assertEqual(verify(record(policy_veto=True)), ("REFUSE", "POLICY_VETO"))

    def test_unsupported_and_quarantine(self):
        self.assertEqual(verify(record(supported=False)), ("REFUSE", "UNSUPPORTED_INPUT"))
        quarantine = Quarantine(); quarantine.insert(record())
        self.assertEqual(verify(record(), quarantine), ("REFUSE", "QUARANTINED_INPUT"))
        self.assertEqual(quarantine.active(), [])
        self.assertIsNone(quarantine.retrieve("cand-1"))

    def test_missing_provenance_and_five_repeat_determinism(self):
        self.assertEqual(verify(record(provenance={})), ("INVALID", "MISSING_PROVENANCE"))
        outputs = [verify(record()) for _ in range(5)]
        self.assertEqual(outputs, [("PROMOTE", "VERIFIED")] * 5)


if __name__ == "__main__":
    unittest.main()
