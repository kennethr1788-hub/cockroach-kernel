"""Mechanical tests for the live-evidence preparation adapter."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import coordinator
import live_completion
import records


class LiveCompletionTests(unittest.TestCase):
    def test_prepared_trials_are_distinct_and_bound(self):
        promote = live_completion.prepared_trial(coordinator.PROMOTE_TRIAL_ID)
        refuse = live_completion.prepared_trial(coordinator.REFUSE_TRIAL_ID)
        self.assertNotEqual(promote["request"]["request_hash"], refuse["request"]["request_hash"])
        self.assertNotEqual(promote["receipt_hash"], refuse["receipt_hash"])
        self.assertNotEqual(promote["vector_digest"], refuse["vector_digest"])
        self.assertEqual(len(promote["commands"]), 4)
        self.assertEqual(len(refuse["commands"]), 4)

    def test_candidate_verdicts_are_expected_and_repeatable(self):
        verifier = live_completion._load_verifier()
        promote = live_completion.prepared_trial(coordinator.PROMOTE_TRIAL_ID)
        refuse = live_completion.prepared_trial(coordinator.REFUSE_TRIAL_ID)
        self.assertEqual([verifier.verify(promote["candidate"])] * 5,
                         [("PROMOTE", "VERIFIED")] * 5)
        self.assertEqual([verifier.verify(refuse["candidate"])] * 5,
                         [("REFUSE", "HASH_MISMATCH")] * 5)

    def test_sql_is_fixed_prepared_and_campaign_scoped(self):
        trial = live_completion.prepared_trial(coordinator.PROMOTE_TRIAL_ID)
        sql = live_completion.seed_sql(trial)
        self.assertIn("PREPARE p9_task", sql)
        self.assertIn("PREPARE p9_vector", sql)
        self.assertIn(coordinator.CAMPAIGN_ID, sql)
        self.assertNotIn("DELETE FROM", sql)
        self.assertNotIn("UPDATE ", sql)

    def test_prepare_writes_only_declared_artifacts(self):
        with tempfile.TemporaryDirectory() as root:
            out = Path(root) / "evidence"
            manifest = live_completion.prepare(out)
            self.assertEqual(manifest["campaign_id"], coordinator.CAMPAIGN_ID)
            self.assertEqual(len(manifest["trials"]), 2)
            names = {item.name for item in out.iterdir()}
            self.assertEqual(names, {
                "promote-prepared.json", "promote-request.json", "promote-candidate.json",
                "promote-seed.sql", "promote-vector-query.sql",
                "refuse-prepared.json", "refuse-request.json", "refuse-candidate.json",
                "refuse-seed.sql", "refuse-vector-query.sql", "prepare-manifest.json",
            })
            loaded = json.loads((out / "prepare-manifest.json").read_bytes())
            self.assertEqual(loaded, manifest)

    def test_sql_quote_doubles_apostrophe_and_rejects_nul(self):
        self.assertEqual(live_completion._sql_string("a'b"), "'a''b'")
        with self.assertRaisesRegex(RuntimeError, "SQL_VALUE_INVALID"):
            live_completion._sql_string("a\x00b")

    def test_all_messages_remain_under_bound(self):
        for trial_id in live_completion.TRIALS:
            trial = live_completion.prepared_trial(trial_id)
            self.assertLessEqual(len(records.canonical_json(trial["request"])),
                                 records.MAX_MESSAGE_BYTES)
            self.assertLessEqual(len(records.canonical_json(trial["candidate"])),
                                 records.MAX_MESSAGE_BYTES)

    def test_changefeed_inspection_decodes_only_bounded_shapes(self):
        resolved = json.dumps({"resolved": "123.0000000000"}, separators=(",", ":")).encode()
        data = json.dumps({"after": {"request_id": "ck-p9-live-promote-request-r1"}},
                          separators=(",", ":")).encode()
        envelopes = [
            {"key": "NULL", "table": "NULL", "value": "\\x" + resolved.hex()},
            {"key": "x", "table": "worker_results", "value": "\\x" + data.hex()},
        ]
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "feed.ndjson"
            path.write_text("\n".join(json.dumps(item) for item in envelopes) + "\n")
            result = live_completion.inspect_changefeed(path)
        self.assertEqual(result["resolved"], ["123.0000000000"])
        self.assertEqual(result["request_ids"], ["ck-p9-live-promote-request-r1"])

    def test_changefeed_inspection_rejects_malformed(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "feed.ndjson"
            path.write_text('{"value":"not-hex"}\n')
            with self.assertRaisesRegex(RuntimeError, "CHANGEFEED_EVIDENCE_INVALID"):
                live_completion.inspect_changefeed(path)

    def test_fresh_trial_promotes_only_valid_capsule(self):
        with tempfile.TemporaryDirectory() as root:
            out = Path(root) / "evidence"
            live_completion.prepare(out)
            for branch in ("promote", "refuse"):
                prepared = json.loads((out / f"{branch}-prepared.json").read_bytes())
                response = live_completion.records.canonical_json(
                    live_completion.records.make_response(
                        prepared["request"], [{
                            "code": "EVALUATION_COMPLETE",
                            "severity": "INFO",
                            "message": "advisory evaluation complete",
                        }]
                    )
                )
                (out / f"{branch}-lambda-response.json").write_bytes(response + b"\n")
                (out / f"{branch}-lambda-meta.json").write_text(
                    '{"aws_request_id":"request-12345678","function_error":null,"status_code":200}\n'
                )
            live_completion.reconcile(out)
            promote = live_completion.fresh_trial(out, "promote")
            refuse = live_completion.fresh_trial(out, "refuse")
        self.assertTrue(promote["fresh_context_continued"])
        self.assertEqual(promote["fresh_context_reason"], "FRESH_CONTEXT_PASS")
        self.assertFalse(refuse["fresh_context_continued"])
        self.assertEqual(refuse["fresh_context_reason"], "CAPSULE_NOT_PROMOTED")
        self.assertEqual(promote["replay_label"], "KEYLESS_LOCAL_REPLAY")
        self.assertFalse(promote["credentials_used"])
        self.assertFalse(promote["network_used"])


if __name__ == "__main__":
    unittest.main()
