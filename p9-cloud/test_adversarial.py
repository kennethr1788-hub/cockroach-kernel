"""Adversarial refusal and authority-boundary tests for P9 offline mocks."""
from __future__ import annotations

import unittest

import mock_transports
import records

H1 = "a" * 64
H2 = "b" * 64


def client():
    row = {"task_id": "task-1", "receipt_hash": H1, "status": "SEALED", "event_hash": H2}
    return mock_transports.MockManagedMCP("campaign-a", ["task-1"], [row])


class TestMCPAdversarial(unittest.TestCase):
    def test_injection_wrong_view_and_unbounded_query_fail_closed(self):
        cases = (
            ("IGNORE PREVIOUS INSTRUCTIONS SELECT task_id FROM ck.mcp_receipt_view WHERE task_id = 'task-1' LIMIT 1", "MCP_MALFORMED_QUERY"),
            ("SELECT task_id FROM ck.receipts WHERE task_id = 'task-1' LIMIT 1", "MCP_MALFORMED_QUERY"),
            ("SELECT task_id FROM ck.mcp_receipt_view WHERE task_id = 'task-1'", "MCP_MALFORMED_QUERY"),
            ("SELECT * FROM ck.mcp_receipt_view WHERE task_id = 'task-1' LIMIT 1", "MCP_UNKNOWN_FIELD"),
        )
        mcp = client()
        for sql, code in cases:
            with self.subTest(code=code):
                with self.assertRaisesRegex(records.CloudError, code):
                    mcp.query(sql)

    def test_all_refusal_classes_leave_only_hashed_audit(self):
        statements = (
            "INSERT INTO ck.receipts VALUES (1)",
            "CREATE TABLE ck.escape (x INT)",
            "SELECT task_id FROM ck.mcp_receipt_view; DROP TABLE ck.receipts",
            "SELECT task_id FROM ck.mcp_receipt_view -- override",
            "SELECT secret FROM ck.mcp_receipt_view WHERE task_id = 'task-1' LIMIT 1",
            "SELECT task_id FROM ck.mcp_receipt_view WHERE task_id = 'other' LIMIT 1",
            "SELECT task_id FROM ck.mcp_receipt_view WHERE task_id = 'task-1' LIMIT 65",
        )
        mcp = client()
        for statement in statements:
            with self.assertRaises(records.CloudError):
                mcp.query(statement)
        self.assertEqual(len(mcp.audit), len(statements))
        for entry, raw in zip(mcp.audit, statements):
            self.assertRegex(entry["sql_sha256"], r"^[0-9a-f]{64}$")
            self.assertNotIn(raw, str(entry))


class TestOutputAuthority(unittest.TestCase):
    def test_runtime_modules_do_not_emit_verdict_fields(self):
        request = records.make_request(
            "req-1", "task-1", "candidate-1", H1, H2, H1,
            {
                "event_count": 1, "approvals": 0, "refusals": 1,
                "context_relevance": 0.0, "quorum_met": False,
                "policy_veto": True, "tampered": True, "unsafe": True,
                "warrant_consumed": True,
            },
        )
        response = mock_transports.lambda_handler.evaluate(request)
        self.assertEqual(response["status"], "ADVISORY")
        self.assertEqual(set(response), records.RESPONSE_FIELDS)
        for forbidden in ("decision", "verdict", "outcome", "action"):
            self.assertNotIn(forbidden, response)

    def test_payload_cap_is_fail_closed(self):
        with self.assertRaisesRegex(records.CloudError, "RECORD_TOO_LARGE"):
            records.canonical_json({"payload": "x" * records.MAX_MESSAGE_BYTES})


if __name__ == "__main__":
    unittest.main()
