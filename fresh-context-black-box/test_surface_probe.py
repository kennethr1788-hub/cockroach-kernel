from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


MODULE_PATH = Path(__file__).with_name("surface_probe.py")
SPEC = importlib.util.spec_from_file_location("black_box_surface_probe", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("SURFACE_PROBE_IMPORT_FAILED")
surface_probe = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = surface_probe
SPEC.loader.exec_module(surface_probe)


class SurfaceProbeTests(unittest.TestCase):
    def test_frozen_candidate_has_no_hidden_scenario_binding(self) -> None:
        result = surface_probe.probe()
        self.assertEqual(result["status"], "SURFACE_BLOCKED")
        self.assertEqual(result["blocker"], "FROZEN_CLI_NOT_SCENARIO_DRIVEN")
        self.assertEqual(result["declared_demo_input_flags"], [])
        self.assertTrue(result["workspaces_distinct"])
        self.assertTrue(result["workspaces_unchanged"])
        self.assertTrue(result["demo_outputs_identical"])
        self.assertFalse(result["scenario_binding_proved"])
        self.assertTrue(result["teardown_verified"])

    def test_hash_constants_match_frozen_candidate_files(self) -> None:
        self.assertEqual(
            surface_probe.sha256_file(surface_probe.REPOSITORY_ROOT / "pyproject.toml"),
            surface_probe.EXPECTED_PYPROJECT_SHA256,
        )
        self.assertEqual(
            surface_probe.sha256_file(
                surface_probe.REPOSITORY_ROOT / "cockroach_kernel" / "cli.py"
            ),
            surface_probe.EXPECTED_CLI_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
