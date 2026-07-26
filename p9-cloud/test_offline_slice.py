"""End-to-end deterministic tests for the keyless P9 mock/replay slice."""
from __future__ import annotations

import copy
import unittest

import records
import run_offline


class TestOfflineSlice(unittest.TestCase):
    def test_two_runs_are_byte_identical(self):
        first = run_offline.run()
        second = run_offline.run()
        self.assertEqual(records.canonical_json(first), records.canonical_json(second))
        self.assertEqual(first["result_hash"], second["result_hash"])

    def test_cloud_stays_advisory_and_local_verifier_is_authority(self):
        result = run_offline.run()
        self.assertEqual(result["lambda_status"], "ADVISORY")
        self.assertEqual(result["tampered_verdict"], "REFUSE")
        self.assertEqual(result["tampered_reason"], "HASH_MISMATCH")
        self.assertEqual(result["local_verdict"], "PROMOTE")
        self.assertEqual(result["local_reason"], "VERIFIED")

    def test_changefeed_mcp_and_fresh_context_complete(self):
        result = run_offline.run()
        self.assertEqual(result["projection_state"], "PROJECTED")
        self.assertEqual(result["projection_cursor"], 1)
        self.assertEqual(result["mcp_rows"], 1)
        self.assertTrue(result["fresh_context"])
        self.assertEqual(result["fresh_context_reason"], "FRESH_CONTEXT_PASS")

    def test_capsule_tamper_fails_closed(self):
        body = {
            "version": "p9-resume-v1", "task_id": "task-1",
            "receipt_hash": "a" * 64, "candidate_id": "candidate-1",
            "verdict": "PROMOTE",
        }
        capsule = dict(body, capsule_hash=records.sha256_hex(body))
        capsule["task_id"] = "task-2"
        ok, reason = run_offline.fresh_resume(records.canonical_json(capsule))
        self.assertFalse(ok)
        self.assertEqual(reason, "CAPSULE_HASH_MISMATCH")


if __name__ == "__main__":
    unittest.main()
