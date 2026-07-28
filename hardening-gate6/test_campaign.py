#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


make_manifest = load("gate6_make_manifest", ROOT / "make_manifest.py")
run_campaign = load("gate6_run_campaign", ROOT / "run_campaign.py")


class Gate6CampaignTests(unittest.TestCase):
    def test_manifest_is_exactly_54_unique_rotated_rows(self):
        manifest = make_manifest.build()
        rows = run_campaign.validate_manifest(manifest)
        self.assertEqual(len(rows), 54)
        self.assertEqual(len({(row["scenario_class"], row["repetition"], row["method"])
                              for row in rows}), 54)

    def test_manifest_tamper_fails_closed(self):
        manifest = make_manifest.build()
        manifest["rows"][0]["method"] = "product"
        with self.assertRaisesRegex(run_campaign.CampaignError,
                                    "MANIFEST_HASH_MISMATCH"):
            run_campaign.validate_manifest(manifest)

    def test_checkpoint_chain_is_explicit(self):
        row = make_manifest.build()["rows"][0]
        receipt = {"receipt_sha256": "a" * 64}
        with tempfile.TemporaryDirectory(prefix="gate6-chain-") as temporary:
            path = Path(temporary) / "chain.ndjson"
            first = run_campaign.append_checkpoint(path, 1, row, receipt,
                                                    run_campaign.ZERO_HASH)
            second = run_campaign.append_checkpoint(path, 2, row, receipt, first)
            events = [json.loads(line) for line in path.read_text().splitlines()]
        self.assertEqual(len(events), 2)
        self.assertEqual(events[1]["previous_event_sha256"], first)
        self.assertEqual(events[1]["event_sha256"], second)


if __name__ == "__main__":
    unittest.main()
