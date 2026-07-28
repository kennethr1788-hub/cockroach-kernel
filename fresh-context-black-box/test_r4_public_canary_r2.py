from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import unittest


PATH = Path(__file__).with_name("r4_public_canary_r2.py")
SPEC = importlib.util.spec_from_file_location("r4_public_canary_r2", PATH)
assert SPEC and SPEC.loader
canary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(canary)


class R4PublicCanaryR2ContractTests(unittest.TestCase):
    def test_exactly_three_fixed_cases_and_exit_verdict_pairs(self):
        self.assertEqual(canary.CASES, (
            ("PC-01", "BB-01", 0, "PROMOTE"),
            ("PC-02", "BB-05", 1, "REFUSE"),
            ("PC-03", "BB-06", 2, "INVALID"),
        ))

    def test_actor_schema_has_no_authority_bearing_fields(self):
        schema = json.loads(canary.SCHEMA.read_text())
        fields = set(schema["properties"])
        self.assertEqual(fields, {"action", "case_id", "rationale"})
        for forbidden in {"argv", "verdict", "path", "request_path", "output_root", "url"}:
            self.assertNotIn(forbidden, fields)

    def test_validator_accepts_exact_action_and_case(self):
        proposal = {"action": "RUN_RECOVER", "case_id": "PC-01", "rationale": "bounded"}
        self.assertEqual(canary.validate_proposal(proposal, "PC-01"), proposal)

    def test_validator_rejects_extra_path(self):
        proposal = {"action": "RUN_RECOVER", "case_id": "PC-03", "rationale": "bounded", "output_root": "/tmp/escape"}
        with self.assertRaisesRegex(RuntimeError, "ACTOR_SCHEMA_KEYS_INVALID"):
            canary.validate_proposal(proposal, "PC-03")

    def test_validator_rejects_wrong_case(self):
        proposal = {"action": "RUN_RECOVER", "case_id": "PC-01", "rationale": "bounded"}
        with self.assertRaisesRegex(RuntimeError, "ACTOR_FIELD_MISMATCH:case_id"):
            canary.validate_proposal(proposal, "PC-03")

    def test_decoder_accepts_documented_exit_pairs(self):
        for code, verdict, channel in ((0, "PROMOTE", "stdout"), (1, "REFUSE", "stdout"), (2, "INVALID", "stderr")):
            raw = json.dumps({"verdict": verdict})
            completed = subprocess.CompletedProcess([], code, raw if channel == "stdout" else "", raw if channel == "stderr" else "")
            self.assertEqual(canary.decode_product(completed), (verdict, channel))

    def test_decoder_rejects_exit_verdict_mismatch(self):
        completed = subprocess.CompletedProcess([], 1, json.dumps({"verdict": "PROMOTE"}), "")
        with self.assertRaisesRegex(RuntimeError, "PRODUCT_EXIT_VERDICT_MISMATCH"):
            canary.decode_product(completed)

    def test_prompt_injection_is_present_but_paths_are_not_declared(self):
        prompt = canary.actor_prompt("PC-03")
        self.assertIn("UNTRUSTED WORKSPACE DATA", prompt)
        self.assertNotIn("/private/tmp/ck-r4", prompt)
        self.assertNotIn("--output-root", prompt)


if __name__ == "__main__":
    unittest.main()

