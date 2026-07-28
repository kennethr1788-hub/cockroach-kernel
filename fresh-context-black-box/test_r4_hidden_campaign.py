from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import unittest


PATH = Path(__file__).with_name("r4_hidden_campaign.py")
SPEC = importlib.util.spec_from_file_location("r4_hidden_campaign", PATH)
assert SPEC and SPEC.loader
campaign = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(campaign)


class R4HiddenCampaignTests(unittest.TestCase):
    def test_sequence_is_balanced_deterministic_and_seed_dependent(self):
        first = campaign.case_sequence(bytes(32))
        again = campaign.case_sequence(bytes(32))
        second = campaign.case_sequence(bytes([1]) * 32)
        self.assertEqual(first, again)
        self.assertNotEqual(first, second)
        self.assertEqual(len(first), 18)
        self.assertEqual({case: first.count(case) for case in campaign.CLASSES}, {case: 3 for case in campaign.CLASSES})

    def test_actor_schema_has_no_authority_bearing_fields(self):
        schema = campaign.effective_schema("inv-12345678")
        fields = set(schema["properties"])
        self.assertEqual(fields, {"action", "invocation_id", "rationale"})
        self.assertEqual(schema["properties"]["invocation_id"]["enum"], ["inv-12345678"])
        for forbidden in {"argv", "path", "request_path", "output_root", "verdict", "url"}:
            self.assertNotIn(forbidden, fields)

    def test_validator_accepts_exact_invocation(self):
        value = {"action": "RUN_RECOVER", "invocation_id": "inv-12345678", "rationale": "bounded"}
        self.assertEqual(campaign.validate_proposal(value, "inv-12345678"), value)

    def test_validator_rejects_extra_path(self):
        value = {"action": "RUN_RECOVER", "invocation_id": "inv-12345678", "rationale": "bounded", "output_root": "/tmp/escape"}
        with self.assertRaisesRegex(RuntimeError, "ACTOR_SCHEMA_KEYS_INVALID"):
            campaign.validate_proposal(value, "inv-12345678")

    def test_validator_rejects_wrong_invocation(self):
        value = {"action": "RUN_RECOVER", "invocation_id": "inv-87654321", "rationale": "bounded"}
        with self.assertRaisesRegex(RuntimeError, "ACTOR_FIELD_MISMATCH:invocation_id"):
            campaign.validate_proposal(value, "inv-12345678")

    def test_expected_exit_verdict_contract(self):
        self.assertEqual(campaign.expected_pair("PROMOTE"), (0, "PROMOTE"))
        self.assertEqual(campaign.expected_pair("NO_ACTION"), (0, "NO_ACTION"))
        self.assertEqual(campaign.expected_pair("REFUSE"), (1, "REFUSE"))
        self.assertEqual(campaign.expected_pair("INVALID"), (2, "INVALID"))

    def test_decoder_rejects_mismatched_exit(self):
        completed = subprocess.CompletedProcess([], 1, '{"verdict":"PROMOTE"}', "")
        with self.assertRaisesRegex(RuntimeError, "PRODUCT_EXIT_VERDICT_MISMATCH"):
            campaign.r4.decode_product(completed)

    def test_injection_prompt_has_no_paths_or_expected_verdict(self):
        prompt = campaign.actor_prompt("inv-12345678", True)
        self.assertIn("UNTRUSTED_WORKSPACE_TEXT", prompt)
        self.assertNotIn("--output-root", prompt)
        self.assertNotIn("PROMOTE", prompt)
        self.assertNotIn("INVALID", prompt)

    def test_preflight_functions_do_not_create_seed_or_lock(self):
        before = campaign.LOCK_PATH.exists()
        campaign.case_sequence(bytes(32))
        campaign.effective_schema("inv-12345678")
        self.assertEqual(campaign.LOCK_PATH.exists(), before)


if __name__ == "__main__":
    unittest.main()
