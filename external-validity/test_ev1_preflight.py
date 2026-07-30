from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("ev1_preflight.py")
SPEC = importlib.util.spec_from_file_location("ev1_preflight_test_target", MODULE_PATH)
assert SPEC and SPEC.loader
ev1 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ev1)


class EV1PreflightTests(unittest.TestCase):
    def test_backlog_is_exact_and_complete(self) -> None:
        result = ev1.parse_backlog()
        self.assertEqual(result["task_count"], 12)
        self.assertEqual(result["backlog_sha256"], ev1.EXPECTED_BACKLOG_SHA256)
        self.assertEqual(result["human_edit_count"], 2)
        self.assertEqual(result["expected_invalid_count"], 2)

    def test_human_receipt_is_bound(self) -> None:
        self.assertEqual(ev1.validate_human_receipt()["status"], "GREEN")

    def test_source_commits_are_bound(self) -> None:
        results = ev1.validate_source_bindings()
        self.assertEqual([row["label"] for row in results], [
            "brew-ledger", "ai-signal-dashboard", "step-realtime-cli"
        ])
        brew = results[0]
        self.assertEqual(brew["included_files"], 76)
        self.assertEqual(brew["excluded_file_count"], 1)
        self.assertEqual(brew["manifest_sha256"], ev1.BREW_LEDGER_MANIFEST_SHA256)
        self.assertNotIn("CLAUDE.md", repr(brew))

    def test_product_candidate_and_regressions(self) -> None:
        result = ev1.validate_product_candidate_and_regressions()
        self.assertEqual(result["status"], "GREEN")
        self.assertTrue(result["candidate_unchanged"])
        self.assertEqual(result["total_tests"], 51)

    def test_scorer_positive_and_negative_controls(self) -> None:
        result = ev1.scorer_canary()
        self.assertEqual(result["positive"]["status"], "GREEN")
        self.assertEqual(result["low_pass_negative"]["status"], "NOT_GREEN")
        self.assertEqual(result["unsafe_negative"]["status"], "NOT_GREEN")

    def test_receipt_chain(self) -> None:
        self.assertEqual(ev1.receipt_chain_canary()["status"], "GREEN")

    def test_kill_guard_rejects_root_and_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign = root / "campaign"
            task = campaign / "task"
            outside = root / "outside"
            campaign.mkdir()
            task.mkdir()
            outside.mkdir()
            escape = campaign / "escape"
            escape.symlink_to(outside, target_is_directory=True)
            self.assertEqual(ev1.guarded_kill_target(campaign, task), task.resolve())
            for candidate in (campaign, outside, escape):
                with self.assertRaises(ev1.PreflightError):
                    ev1.guarded_kill_target(campaign, candidate)

    def test_fresh_process_and_teardown(self) -> None:
        result = ev1.isolation_and_teardown_canary()
        self.assertEqual(result["status"], "GREEN")
        self.assertEqual(result["residue_bytes"], 0)
        self.assertTrue(result["outside_canary_survived_guarded_delete"])


if __name__ == "__main__":
    unittest.main()
