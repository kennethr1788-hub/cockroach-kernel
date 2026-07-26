"""Offline adversarial tests for the bounded Lambda and MCP mocks."""
from __future__ import annotations

import unittest

import mock_transports as mt
import records as r

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def request(request_id="req-1"):
    return r.make_request(
        request_id=request_id,
        task_id="task-1",
        candidate_id="candidate-1",
        trajectory_hash=HASH_A,
        candidate_hash=HASH_B,
        policy_hash=HASH_C,
        features={
            "event_count": 1,
            "approvals": 1,
            "refusals": 0,
            "context_relevance": 0.75,
            "quorum_met": True,
            "policy_veto": False,
            "tampered": False,
            "unsafe": False,
            "warrant_consumed": False,
        },
    )


def mcp():
    row = {
        "task_id": "task-1",
        "receipt_hash": HASH_A,
        "status": "SEALED",
        "event_hash": HASH_B,
    }
    return mt.MockManagedMCP("campaign-a", ["task-1"], [row])


class TestLambdaTransport(unittest.TestCase):
    def test_success_and_duplicate_are_idempotent(self):
        transport = mt.MockLambdaTransport({"req-1": ["success", "duplicate"]})
        client = mt.CheckedLambdaClient(transport)
        first, first_response = client.call(request())
        second, second_response = client.call(request())
        self.assertEqual(first, mt.CALL_ACCEPTED)
        self.assertEqual(second, mt.CALL_DUPLICATE)
        self.assertEqual(r.canonical_json(first_response), r.canonical_json(second_response))

    def test_timeout_and_throttle_retry_then_succeed(self):
        transport = mt.MockLambdaTransport({"req-1": ["timeout", "throttle", "success"]})
        outcome, response = mt.CheckedLambdaClient(transport).call_with_retries(request(), 3)
        self.assertEqual(outcome, mt.CALL_ACCEPTED)
        self.assertEqual(response["status"], "ADVISORY")
        self.assertEqual(len(transport.invocations), 3)

    def test_retry_exhaustion(self):
        transport = mt.MockLambdaTransport({"req-1": ["timeout"]})
        with self.assertRaisesRegex(r.CloudError, "RETRY_EXHAUSTED"):
            mt.CheckedLambdaClient(transport).call_with_retries(request(), 2)

    def test_malformed_and_stale_fail_closed(self):
        for behavior, code in (("malformed", "MISSING_FIELD"), ("stale", "STALE_RESPONSE")):
            with self.subTest(behavior=behavior):
                client = mt.CheckedLambdaClient(mt.MockLambdaTransport({"req-1": [behavior]}))
                with self.assertRaisesRegex(r.CloudError, code):
                    client.call(request())


class TestManagedMCP(unittest.TestCase):
    def test_exact_read_only_query(self):
        client = mcp()
        result = client.query(
            "SELECT task_id, receipt_hash, status, event_hash "
            "FROM ck.mcp_receipt_view WHERE task_id = 'task-1' LIMIT 1"
        )
        self.assertEqual(result["row_count"], 1)
        self.assertRegex(result["result_hash"], r"^[0-9a-f]{64}$")
        self.assertEqual(client.audit[-1]["outcome"], "ACCEPT")

    def test_write_ddl_comment_and_multi_statement_refused(self):
        cases = (
            ("UPDATE ck.receipts SET status='SEALED'", "MCP_DML_REFUSED"),
            ("DROP TABLE ck.receipts", "MCP_DDL_REFUSED"),
            ("SELECT task_id FROM ck.mcp_receipt_view -- x", "MCP_COMMENT_REFUSED"),
            ("SELECT task_id FROM ck.mcp_receipt_view; SELECT 1", "MCP_MULTI_STATEMENT_REFUSED"),
        )
        client = mcp()
        for sql, code in cases:
            with self.subTest(sql=sql):
                with self.assertRaisesRegex(r.CloudError, code):
                    client.query(sql)

    def test_unknown_field_namespace_and_limit_refused(self):
        client = mcp()
        cases = (
            ("SELECT secret FROM ck.mcp_receipt_view WHERE task_id = 'task-1' LIMIT 1", "MCP_UNKNOWN_FIELD"),
            ("SELECT task_id FROM ck.mcp_receipt_view WHERE task_id = 'task-2' LIMIT 1", "MCP_NAMESPACE_MISMATCH"),
            ("SELECT task_id FROM ck.mcp_receipt_view WHERE task_id = 'task-1' LIMIT 65", "MCP_RESULT_TOO_LARGE"),
        )
        for sql, code in cases:
            with self.subTest(code=code):
                with self.assertRaisesRegex(r.CloudError, code):
                    client.query(sql)

    def test_query_audit_stores_hash_not_raw_sql(self):
        client = mcp()
        sql = "DROP TABLE ck.receipts"
        with self.assertRaises(r.CloudError):
            client.query(sql)
        entry = client.audit[-1]
        self.assertNotIn(sql, str(entry))
        self.assertRegex(entry["sql_sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
