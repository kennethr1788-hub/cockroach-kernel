#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("MODULE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


make_vectors = load_module("test_gate7_make_vectors", HERE / "make_vectors.py")
trial = load_module("test_gate7_trial", HERE / "run_trial.py")
campaign = load_module("test_gate7_campaign", HERE / "run_campaign.py")


CANDIDATE = "8718fbecc2b145ff36ce8c3ed655e92b5906aeab"


class Gate7Tests(unittest.TestCase):
    def setUp(self):
        self.record = make_vectors.build(CANDIDATE, bytes.fromhex("7e" * 32))

    def test_vector_set_has_exact_coverage(self):
        failures, controls = campaign.validate_set(self.record, CANDIDATE)
        self.assertEqual(len(failures), 21)
        self.assertEqual(len(controls), 7)
        self.assertEqual(len({row["vector_hash"] for row in failures + controls}), 28)

    def test_every_failure_and_control_matches_expected_semantics(self):
        for vector in self.record["failure_vectors"] + self.record["valid_controls"]:
            trial.validate_vector(vector)
            verdict, reason, _ = trial.execute(vector)
            self.assertEqual((verdict, reason),
                             (vector["expected_verdict"], vector["expected_reason"]))

    def test_interruption_consumes_and_never_promotes(self):
        vector = next(
            row for row in self.record["failure_vectors"]
            if row["class"] == "interrupted-consumption"
        )
        verdict, reason, details = trial.execute(vector)
        self.assertEqual((verdict, reason),
                         ("REFUSE", "RECOVERY_INTERRUPTED_FAIL_CLOSED"))
        self.assertEqual(details["warrant_state"], "CONSUMED")
        self.assertFalse(details["promotion_recorded"])
        self.assertEqual(details["replay_reason"], "WARRANT_REPLAY")

    def test_full_campaign_is_43_fresh_process_receipts(self):
        with tempfile.TemporaryDirectory(prefix="gate7-test-") as temporary:
            root = Path(temporary)
            vector_set = root / "vectors.json"
            vector_set.write_bytes(make_vectors.canonical(self.record))
            output = root / "evidence"
            rc = campaign.main_from_args if hasattr(campaign, "main_from_args") else None
            self.assertIsNone(rc)
            import subprocess
            completed = subprocess.run([
                sys.executable, str(HERE / "run_campaign.py"),
                "--vector-set", str(vector_set),
                "--candidate-commit", CANDIDATE,
                "--campaign-id", "ck-gate7-test-r1",
                "--python-bin", sys.executable,
                "--output-root", str(output),
            ], cwd=BASE, check=False, stdout=subprocess.PIPE,
               stderr=subprocess.PIPE, timeout=60)
            if completed.returncode != 0:
                self.fail(completed.stderr.decode("utf-8", "replace"))
            aggregate = json.loads((output / "aggregate.json").read_bytes())
            self.assertTrue(aggregate["green"])
            self.assertEqual(aggregate["measured_executions"], 43)
            self.assertEqual(len(list((output / "receipts").glob("*.json"))), 43)
            self.assertFalse((output / "work").exists())


if __name__ == "__main__":
    unittest.main()
