from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from cockroach_kernel import cli


class CliTests(unittest.TestCase):
    def test_demo_writes_promotion_and_refusal_receipts(self):
        with tempfile.TemporaryDirectory() as root:
            result = cli.run_demo(Path(root))
            promotion = json.loads((Path(root) / "promotion-receipt.json").read_bytes())
            refusal = json.loads((Path(root) / "refusal-receipt.json").read_bytes())
        self.assertEqual(result["replay_label"], "KEYLESS_LOCAL_REPLAY")
        self.assertEqual(promotion["verdict"], "PROMOTE")
        self.assertEqual(promotion["reason"], "VERIFIED")
        self.assertTrue(promotion["fresh_context_continued"])
        self.assertEqual(refusal["verdict"], "REFUSE")
        self.assertEqual(refusal["reason"], "HASH_MISMATCH")
        self.assertEqual(refusal["action_taken"], "NONE")

    def test_receipts_are_byte_identical_across_fresh_roots(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            cli.run_demo(Path(first))
            cli.run_demo(Path(second))
            for name in ("promotion-receipt.json", "refusal-receipt.json"):
                self.assertEqual((Path(first) / name).read_bytes(), (Path(second) / name).read_bytes())

    def test_default_output_contains_structured_refusal_contract(self):
        with tempfile.TemporaryDirectory() as root, contextlib.redirect_stdout(io.StringIO()) as out:
            status = cli.main(["demo", "--output-root", root])
        self.assertEqual(status, 0)
        text = out.getvalue()
        self.assertIn("MODE: KEYLESS_LOCAL_REPLAY", text)
        self.assertIn("VERDICT: REFUSE", text)
        self.assertIn("REASON: HASH_MISMATCH", text)
        self.assertIn("ACTION_TAKEN: NONE", text)
        self.assertIn("NEXT_SAFE_ACTION:", text)
        self.assertIn("RECEIPT:", text)

    def test_json_output_is_canonical_and_has_no_network_or_credentials(self):
        with tempfile.TemporaryDirectory() as root, contextlib.redirect_stdout(io.StringIO()) as out:
            status = cli.main(["demo", "--json", "--output-root", root])
        self.assertEqual(status, 0)
        raw = out.getvalue().rstrip("\n").encode("utf-8")
        parsed = json.loads(raw)
        self.assertEqual(raw, cli.canonical_json(parsed))
        self.assertFalse(parsed["network_used"])
        self.assertFalse(parsed["credentials_used"])

    def test_inspect_validates_canonical_receipt(self):
        with tempfile.TemporaryDirectory() as root:
            cli.run_demo(Path(root))
            receipt = Path(root) / "refusal-receipt.json"
            with contextlib.redirect_stdout(io.StringIO()) as out:
                status = cli.main(["inspect", str(receipt)])
            self.assertEqual(status, 0)
            self.assertEqual(json.loads(out.getvalue()), json.loads(receipt.read_bytes()))

    def test_inspect_rejects_tamper_without_action(self):
        with tempfile.TemporaryDirectory() as root:
            cli.run_demo(Path(root))
            receipt = Path(root) / "refusal-receipt.json"
            record = json.loads(receipt.read_bytes())
            record["reason"] = "VERIFIED"
            receipt.write_bytes(cli.canonical_json(record) + b"\n")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                status = cli.main(["inspect", str(receipt)])
        self.assertEqual(status, 2)
        self.assertIn("VERDICT: INVALID", stderr.getvalue())
        self.assertIn("REASON: RECEIPT_HASH_MISMATCH", stderr.getvalue())
        self.assertIn("ACTION_TAKEN: NONE", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
