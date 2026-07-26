"""Reliability tests for retries, budgets, workers, and changefeeds."""
from __future__ import annotations

import unittest

import faults
import lambda_handler
import records
import retry

H1 = "a" * 64
H2 = "b" * 64
H3 = "c" * 64


def request(request_id="req-1"):
    return records.make_request(
        request_id, "task-1", "candidate-1", H1, H2, H3,
        {
            "event_count": 1, "approvals": 1, "refusals": 0,
            "context_relevance": 0.75, "quorum_met": True,
            "policy_veto": False, "tampered": False, "unsafe": False,
            "warrant_consumed": False,
        },
    )


def projection(event_id="event-1", cursor=1, payload_hash=H3):
    body = {
        "event_id": event_id, "cursor": cursor, "source_hash": H1,
        "receipt_hash": H2, "payload_hash": payload_hash,
    }
    return dict(body, projection_hash=records.sha256_hex(body))


class TestRetry(unittest.TestCase):
    def test_40001_retries_then_succeeds(self):
        def operation(attempt):
            if attempt < 3:
                raise retry.SqlStateError("40001")
            return "done"
        result, receipts = retry.run_serializable(operation, 3)
        self.assertEqual(result, "done")
        self.assertEqual([item["result"] for item in receipts], ["RETRY", "RETRY", "SUCCESS"])

    def test_40001_exhaustion_and_nonretryable_passthrough(self):
        with self.assertRaisesRegex(retry.RetryError, "SERIALIZATION_RETRY_EXHAUSTED"):
            retry.run_serializable(lambda _: (_ for _ in ()).throw(retry.SqlStateError("40001")), 2)
        with self.assertRaisesRegex(retry.SqlStateError, "23505"):
            retry.run_serializable(lambda _: (_ for _ in ()).throw(retry.SqlStateError("23505")), 3)

    def test_duplicate_idempotency_and_conflict(self):
        ledger = retry.IdempotencyLedger()
        self.assertEqual(ledger.record("record-1", H1), "INSERTED")
        self.assertEqual(ledger.record("record-1", H1), "DUPLICATE")
        with self.assertRaisesRegex(retry.RetryError, "DUPLICATE_CONFLICT"):
            ledger.record("record-1", H2)


class TestBudgetsAndWorker(unittest.TestCase):
    def test_invocation_cap_and_byte_accounting(self):
        budget = retry.InvocationBudget(2)
        budget.consume({"a": 1}, {"b": 2})
        budget.consume({"a": 2})
        self.assertEqual(budget.used, 2)
        self.assertGreater(budget.request_bytes, 0)
        self.assertGreater(budget.response_bytes, 0)
        with self.assertRaisesRegex(retry.RetryError, "INVOCATION_CAP_EXHAUSTED"):
            budget.consume({"a": 3})

    def test_cold_start_equivalent_is_deterministic(self):
        worker = faults.ScriptedWorker(lambda_handler.evaluate, cap=5)
        outputs = [worker.invoke(request(f"req-{index}"), "cold_start", 5) for index in range(1, 6)]
        normalized = []
        for response in outputs:
            copy = dict(response)
            copy["request_id"] = "normalized"
            copy["response_hash"] = "0" * 64
            normalized.append(records.canonical_json(copy))
        self.assertEqual(len(set(normalized)), 1)

    def test_unavailable_and_hash_mismatch_fail_closed(self):
        worker = faults.ScriptedWorker(lambda_handler.evaluate, cap=2)
        with self.assertRaisesRegex(faults.FaultError, "WORKER_UNAVAILABLE"):
            worker.invoke(request(), "unavailable")
        response = worker.invoke(request("req-2"), "hash_mismatch")
        with self.assertRaisesRegex(records.CloudError, "STALE_HASH"):
            records.validate_response(response)


class TestChangefeed(unittest.TestCase):
    def test_duplicate_restart_and_no_write_back(self):
        feed = faults.ChangefeedProjection()
        event = projection()
        self.assertEqual(feed.accept(event), "PROJECTED")
        self.assertEqual(feed.accept(event), "DUPLICATE")
        restarted = faults.ChangefeedProjection.restart(feed.snapshot())
        self.assertEqual(restarted.cursor, 1)
        self.assertEqual(restarted.accept(projection("event-2", 2)), "PROJECTED")
        self.assertFalse(restarted.write_back_authorized)
        with self.assertRaisesRegex(faults.FaultError, "WRITE_BACK_FORBIDDEN"):
            restarted.write_back({"x": 1})

    def test_lag_projection_mismatch_and_conflict(self):
        feed = faults.ChangefeedProjection()
        with self.assertRaisesRegex(faults.FaultError, "CHANGEFEED_LAG"):
            feed.accept(projection("event-2", 2))
        bad = projection()
        bad["projection_hash"] = "0" * 64
        with self.assertRaisesRegex(faults.FaultError, "PROJECTION_HASH_MISMATCH"):
            feed.accept(bad)
        good = projection()
        feed.accept(good)
        conflicting = projection(payload_hash=H1)
        with self.assertRaisesRegex(faults.FaultError, "PROJECTION_CONFLICT"):
            feed.accept(conflicting)


if __name__ == "__main__":
    unittest.main()
