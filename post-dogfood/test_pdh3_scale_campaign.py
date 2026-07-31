from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_scale_campaign_tested", HERE / "run_pdh3_scale_campaign.py"
)
assert SPEC is not None and SPEC.loader is not None
campaign = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = campaign
SPEC.loader.exec_module(campaign)


class ScaleCampaignUnitTests(unittest.TestCase):
    def test_seed_statement_counts_and_bounds(self) -> None:
        rows = campaign.seed_batch_statements(
            "ck-pdh3-scale-test",
            0,
            100,
            10,
            2,
            50,
        )
        self.assertEqual([row[0] for row in rows], [
            "tasks", "events", "receipts", "vectors"
        ])
        self.assertTrue(all("generate_series" in row[1] for row in rows))
        self.assertNotIn("AWS", "\n".join(row[1] for row in rows))

    def test_vector_statement_omitted_after_vector_ceiling(self) -> None:
        rows = campaign.seed_batch_statements(
            "ck-pdh3-scale-test",
            100,
            200,
            10,
            2,
            50,
        )
        self.assertNotIn("vectors", [row[0] for row in rows])

    def test_campaign_name_boundary(self) -> None:
        arguments = campaign.parser().parse_args([
            "--binary", "/tmp/cockroach",
            "--packet", "/tmp/packet",
            "--output", "/tmp/output",
            "--campaign-id", "wrong",
        ])
        with self.assertRaisesRegex(campaign.CampaignError, "CAMPAIGN_ID_INVALID"):
            # Reach the campaign check before any runtime work.
            binary = Path("/tmp/cockroach")
            packet = Path("/tmp/packet")
            binary.write_bytes(b"")
            packet.write_bytes(b"")
            try:
                binary.chmod(0o700)
                campaign.execute(arguments)
            finally:
                binary.unlink(missing_ok=True)
                packet.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
