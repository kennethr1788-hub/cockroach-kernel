from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


harness = load("supplemental_harness", HERE / "harness.py")
manifest = load("supplemental_manifest", HERE / "make_manifest.py")


class SupplementalHarnessTests(unittest.TestCase):
    def test_manifest_has_full_108_row_coverage(self):
        value = manifest.build("ck-supp-generalization-test")
        self.assertEqual(value["row_count"], 108)
        self.assertEqual(len({(row["profile"], row["scenario"], row["repetition"], row["method"])
                              for row in value["rows"]}), 108)

    def test_profiles_are_exact_and_candidate_record_stays_bounded(self):
        for name, expected in (("small", 131072), ("medium", 4194304),
                               ("large", 67108864)):
            scenario = harness.build_scenario(name, "complete-loss", 1)
            self.assertEqual(scenario["public"]["scale_profile"]["total_generated_bytes"], expected)
            candidate_manifest = scenario["expected_manifest"]
            record_shape = {
                "version": "p4-v1", "candidate_id": "candidate-04",
                "source_receipt_hash": "f" * 64,
                "payload": {"checkpoint": "FINAL_PRELOSS",
                            "event_hash": "f" * 64,
                            "manifest": candidate_manifest},
                "payload_hash": "f" * 64, "schema_version": "p4-v1",
                "provenance": {"source": "gate5-common-event-packet"},
                "supported": True, "one_use_state": "ISSUED",
                "quarantined": False, "policy_veto": False,
                "requested_paths": sorted(candidate_manifest),
                "declared_paths": sorted(candidate_manifest),
            }
            self.assertLess(len(harness.base.canonical(record_shape)), 65536)

    def test_compact_materialization_matches_declared_manifest(self):
        scenario = harness.build_scenario("small", "complete-loss", 1)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            harness.materialize_event(root, scenario["public"]["events"][-1])
            self.assertEqual(harness.base.manifest(root), scenario["expected_manifest"])


if __name__ == "__main__":
    unittest.main()
