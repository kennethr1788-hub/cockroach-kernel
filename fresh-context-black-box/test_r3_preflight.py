from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("r3_preflight.py")
SPEC = importlib.util.spec_from_file_location("r3_preflight", MODULE_PATH)
assert SPEC and SPEC.loader
r3 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r3)


class R3PreflightUnitTests(unittest.TestCase):
    def test_profile_is_deny_default_and_network_denied(self):
        profile = r3.PROFILE.read_text()
        self.assertIn("(deny default)", profile)
        self.assertIn("(deny network*)", profile)
        self.assertIn('(param "WORKSPACE_ROOT")', profile)
        self.assertNotIn("(allow default)", profile)

    def test_clean_ledger_and_all_required_faults(self):
        results = r3.telemetry_fault_calibration("a" * 64)
        self.assertEqual(results["clean"], "GREEN")
        self.assertEqual(
            set(results) - {"clean"},
            {"missing_start", "missing_end", "sequence_gap", "hash_break", "monitor_death", "unrepresented_child", "filesystem_omission", "counter_mismatch"},
        )

    def test_residue_mutations_and_clean_control(self):
        results = r3.residue_calibration()
        self.assertEqual(results["clean"], [])
        self.assertIn("UNDECLARED_FILE", results["undeclared_file"])
        self.assertIn("UNDECLARED_DIRECTORY", results["undeclared_directory"])
        self.assertIn("SYMLINK_ESCAPE", results["symlink_escape"])
        self.assertIn("LIVE_CHILD", results["live_child"])
        self.assertIn("OPEN_DESCRIPTOR", results["open_descriptor"])
        self.assertIn("OPEN_SOCKET", results["socket"])
        self.assertIn("STALE_LOCK_OR_PID", results["stale_lock"])
        self.assertIn("CROSS_SESSION_ARTIFACT", results["cross_session"])
        self.assertIn("UNEXPECTED_MODIFIED_FILE", results["modified_file"])

    def test_scorer_rejects_all_faults_and_allows_public_discovery(self):
        results = r3.scorer_calibration()
        self.assertEqual(results["allowed_discovery"], "PASS")
        self.assertEqual(len(results), 11)

    def test_candidate_bindings_are_current(self):
        for relative, expected in r3.EXPECTED.items():
            self.assertEqual(r3.file_hash(r3.REPO / relative), expected)


if __name__ == "__main__":
    unittest.main()
