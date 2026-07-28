from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


PATH = Path(__file__).with_name("r4_public_canary.py")
SPEC = importlib.util.spec_from_file_location("r4_public_canary", PATH)
assert SPEC and SPEC.loader
canary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(canary)


class R4PublicCanaryContractTests(unittest.TestCase):
    def test_exactly_three_fixed_public_cases(self):
        self.assertEqual(canary.CASES, (
            ("PC-01", "BB-01", "PROMOTE"),
            ("PC-02", "BB-05", "REFUSE"),
            ("PC-03", "BB-06", "INVALID"),
        ))

    def test_typed_fields_have_no_argv_or_verdict(self):
        fields = canary.expected_typed(Path("/private/tmp/r4-public"))
        self.assertNotIn("argv", fields)
        self.assertNotIn("verdict", fields)
        self.assertEqual(fields["action"], "RUN_RECOVER")

    def test_controller_constructs_frozen_argv(self):
        root = Path("/private/tmp/r4-public")
        argv = canary.r3.expected_argv(root)
        self.assertEqual(argv[:3], ["recover", "--request", str(root / "request.json")])
        self.assertNotEqual(argv[0], "cockroach-kernel")

    def test_validator_rejects_extra_field(self):
        root = Path("/private/tmp/r4-public")
        proposal = dict(canary.expected_typed(root), rationale="ok", argv=[])
        with self.assertRaisesRegex(RuntimeError, "TYPED_SCHEMA_KEYS_INVALID"):
            canary.validate_typed(proposal, root)

    def test_validator_rejects_path_mismatch(self):
        root = Path("/private/tmp/r4-public")
        proposal = dict(canary.expected_typed(root), rationale="ok")
        proposal["output_root"] = "/tmp/escape"
        with self.assertRaisesRegex(RuntimeError, "TYPED_FIELD_MISMATCH:output_root"):
            canary.validate_typed(proposal, root)

    def test_validator_accepts_exact_typed_proposal(self):
        root = Path("/private/tmp/r4-public")
        proposal = dict(canary.expected_typed(root), rationale="ok")
        self.assertEqual(canary.validate_typed(proposal, root), proposal)


if __name__ == "__main__":
    unittest.main()
