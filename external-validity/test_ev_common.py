from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import ev_common


class CommonTests(unittest.TestCase):
    def test_canonical_is_stable(self):
        self.assertEqual(ev_common.canonical({"b": 2, "a": 1}), b'{"a":1,"b":2}')

    def test_receipt_binds_previous_hash(self):
        first = ev_common.chained_receipt(
            campaign_id="campaign-r1", sequence=1, kind="canary",
            result="PASS", details={"ok": True}, previous_hash="0" * 64,
        )
        second = ev_common.chained_receipt(
            campaign_id="campaign-r1", sequence=2, kind="canary",
            result="PASS", details={"ok": True}, previous_hash=first["receipt_hash"],
        )
        self.assertNotEqual(first["receipt_hash"], second["receipt_hash"])
        self.assertEqual(second["previous_hash"], first["receipt_hash"])

    def test_atomic_output_is_canonical_json(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "receipt.json"
            ev_common.write_atomic(path, {"b": 2, "a": 1})
            self.assertEqual(json.loads(path.read_bytes()), {"a": 1, "b": 2})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
