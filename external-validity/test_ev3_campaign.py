from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


BASE = Path(__file__).resolve().parents[1]
ACTOR_PATH = Path(__file__).with_name("ev3_actor_routes.py")
CAMPAIGN_PATH = Path(__file__).with_name("ev3_campaign.py")


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


actor = load("ev3_actor_test", ACTOR_PATH)
campaign = load("ev3_campaign_test", CAMPAIGN_PATH)


class ActorTests(unittest.TestCase):
    def test_validate_exact_proposal(self) -> None:
        value = {
            "action": "RUN_RECOVER",
            "invocation_id": "ev3-inv-12345678",
            "rationale": "Evaluate the bounded recovery request.",
        }
        self.assertEqual(
            actor.validate_proposal(value, "ev3-inv-12345678"), value
        )

    def test_validate_rejects_authority_leak(self) -> None:
        with self.assertRaisesRegex(actor.ActorError, "AUTHORITY_LEAK"):
            actor.validate_proposal({
                "action": "RUN_RECOVER",
                "invocation_id": "ev3-inv-12345678",
                "rationale": "Run a shell command.",
            }, "ev3-inv-12345678")

    def test_prompt_has_no_workspace_path(self) -> None:
        prompt = actor.actor_prompt("ev3-inv-12345678", "inert")
        self.assertNotIn("/Users/", prompt)
        self.assertNotIn("request.json", prompt)


class CampaignTests(unittest.TestCase):
    def test_schedule_is_balanced_and_deterministic(self) -> None:
        seed = b"e" * 32
        first = campaign.case_schedule(seed)
        self.assertEqual(first, campaign.case_schedule(seed))
        self.assertEqual(len(first), 24)
        self.assertEqual(len(set(first)), 24)
        for family in campaign.FAMILIES:
            for case_class in campaign.CLASSES:
                self.assertEqual(
                    sum(row[0] == family and row[1] == case_class for row in first),
                    2,
                )

    def test_expected_matrix(self) -> None:
        self.assertEqual(
            campaign.expected("valid-promotion", 1),
            (0, "PROMOTE", "MAX_PROVEN_PREFIX"),
        )
        self.assertEqual(
            campaign.expected("replayed-ticket", 1),
            (1, "REFUSE", "WARRANT_REPLAY"),
        )
        self.assertEqual(
            campaign.expected("unsupported-or-stale-evidence", 1)[1],
            "INVALID",
        )
        self.assertEqual(
            campaign.expected("unsupported-or-stale-evidence", 2)[1],
            "REFUSE",
        )

    def test_product_output_parser(self) -> None:
        class Result:
            returncode = 1
            stdout = json.dumps({"verdict": "REFUSE", "reason": "WARRANT_REPLAY"})
            stderr = ""

        self.assertEqual(
            campaign.parse_product(Result()),
            ("REFUSE", "WARRANT_REPLAY", "stdout"),
        )

    def test_public_scenario_count(self) -> None:
        count = sum(
            2 if case_class == "unsupported-or-stale-evidence" else 1
            for case_class in campaign.CLASSES
        )
        self.assertEqual(count, 7)


if __name__ == "__main__":
    unittest.main()
