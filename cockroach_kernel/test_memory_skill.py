import hashlib
import json
import unittest

from cockroach_kernel.memory_skill import MemorySkillError, inspect_snapshot


H1 = "1" * 64
H2 = "2" * 64
H3 = "3" * 64


def snapshot(*, orphan=False):
    return {
        "version": "ck-memory-snapshot-v1",
        "receipts": [{"task_id": "task-1", "receipt_hash": H1,
                       "event_hash": H2, "status": "SEALED"}],
        "vectors": [{"task_id": "task-1" if not orphan else "task-2",
                     "event_hash": H2, "namespace": "trajectory",
                     "vector_digest": H3, "distance": 0.25}],
    }


class MemorySkillTests(unittest.TestCase):
    def test_linked_snapshot_is_advisory(self):
        report = inspect_snapshot(snapshot())
        self.assertEqual(report["status"], "INSPECTED")
        self.assertEqual(report["linked_vector_count"], 1)
        self.assertEqual(report["authority"], "NONE_ADVISORY_ONLY")
        self.assertFalse(report["mutation_performed"])
        self.assertNotIn("verdict", report)
        body = dict(report)
        evidence_hash = body.pop("evidence_hash")
        self.assertEqual(evidence_hash, hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        ).hexdigest())

    def test_orphan_is_incomplete(self):
        report = inspect_snapshot(snapshot(orphan=True))
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertEqual(report["warnings"], ["ORPHAN_VECTOR"])

    def test_unknown_fields_and_bad_hash_fail_closed(self):
        value = snapshot()
        value["vectors"][0]["extra"] = True
        with self.assertRaisesRegex(MemorySkillError, "ROW_FIELDS_INVALID"):
            inspect_snapshot(value)
        value = snapshot()
        value["receipts"][0]["receipt_hash"] = "bad"
        with self.assertRaisesRegex(MemorySkillError, "HASH_INVALID"):
            inspect_snapshot(value)
