from __future__ import annotations

import json
from pathlib import Path
import unittest

import fault_lambda
import live_fault_campaign as campaign


BASE = Path(__file__).resolve().parents[1]
FAILED_R1 = BASE / "evidence" / "external-validity-ev2-live-r1" / "execution-01"


class BoundResponseCompatibilityTests(unittest.TestCase):
    def test_preserved_live_response_uses_current_validator_interface(self):
        request = json.loads((FAILED_R1 / "lambda.request.json").read_bytes())
        response = json.loads((FAILED_R1 / "lambda.json").read_bytes())

        campaign._validate_bound_response(response, request)

    def test_valid_response_for_another_request_is_rejected(self):
        response = json.loads((FAILED_R1 / "lambda.json").read_bytes())
        other_request = campaign._make_request("ev2-linkage-canary-2-r2")

        with self.assertRaisesRegex(campaign.cloud_records.CloudError, "STALE_RESPONSE"):
            campaign._validate_bound_response(response, other_request)

    def test_fault_lambda_stale_authority_payload_is_rejected(self):
        request = campaign._make_request("ev2-stale-canary-1-r2")
        response = fault_lambda.lambda_handler(
            {"fault_mode": "stale", "request_id": request["request_id"]}, None
        )

        with self.assertRaises(campaign.cloud_records.CloudError):
            campaign._validate_bound_response(response, request)


if __name__ == "__main__":
    unittest.main()
