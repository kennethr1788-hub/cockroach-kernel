from __future__ import annotations

import json
import unittest

from cockroach_kernel.recovery_preview import preview_recovery
from cockroach_kernel.test_recovery_surface import Scenario


class RecoveryPreviewTests(unittest.TestCase):
    def test_preview_is_hash_bound_and_does_not_mutate(self):
        scenario = Scenario()
        try:
            before = scenario.workspace.read_bytes() if scenario.workspace.is_file() else sorted(
                p.relative_to(scenario.workspace).as_posix()
                for p in scenario.workspace.rglob("*")
                if p.is_file()
            )
            report = preview_recovery(
                request_path=scenario.request_path,
                sandbox_root=scenario.root,
                workspace=scenario.workspace,
                representation_root=scenario.representations,
                custody_root=scenario.custody,
                output_root=scenario.output,
            )
            self.assertEqual(report["projected_verdict"], "PROMOTE")
            self.assertTrue(report["no_side_effects"])
            self.assertFalse(report["warrant_consumed"])
            self.assertTrue(report["surviving_paths"])
            self.assertEqual(before, sorted(
                p.relative_to(scenario.workspace).as_posix()
                for p in scenario.workspace.rglob("*")
                if p.is_file()
            ))
            body = dict(report)
            supplied = body.pop("preview_hash")
            from cockroach_kernel.continuation_brief import digest
            self.assertEqual(supplied, digest(body))
        finally:
            scenario.cleanup()

    def test_preview_marks_missing_representation(self):
        scenario = Scenario()
        try:
            missing = scenario.representations / scenario.candidate["candidate_id"] / "src" / "feature.py"
            missing.unlink()
            report = preview_recovery(
                request_path=scenario.request_path,
                sandbox_root=scenario.root,
                workspace=scenario.workspace,
                representation_root=scenario.representations,
                custody_root=scenario.custody,
                output_root=scenario.output,
            )
            self.assertIn("src/feature.py", report["unavailable_paths"])
            self.assertIn(
                {"path": "src/feature.py", "status": "MISSING_REPRESENTATION"},
                report["path_status"],
            )
        finally:
            scenario.cleanup()
