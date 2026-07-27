from __future__ import annotations

import json
import unittest

from cockroach_kernel import http_api


def event(path: str, method: str = "GET", body=None, query=None):
    return {
        "version": "2.0",
        "rawPath": path,
        "body": body,
        "queryStringParameters": query,
        "requestContext": {"http": {"method": method}},
    }


class FakeReader:
    def __init__(self, branch: str, mutate: str | None = None):
        self.branch = branch
        self.mutate = mutate

    def fetch(self, branch, query_vector):
        trial = http_api._expected(branch)
        record = {
            "task_id": trial["task_id"],
            "receipt_hash": trial["receipt_hash"],
            "event_hash": trial["event_hash"],
            "vector_digest": trial["vector_digest"],
            "request_hash": trial["request"]["request_hash"],
            "response_hash": "a" * 64,
            "result_hash": "b" * 64,
            "candidate_id": trial["candidate"]["candidate_id"],
            "status": "ADVISORY",
            "distance": 0.0,
        }
        if self.mutate:
            record[self.mutate] = "f" * 64
        return record


class HttpApiTests(unittest.TestCase):
    def test_promote_uses_live_memory_linkage_and_local_authority(self):
        response = http_api.handler(event("/demo/promote"), None, FakeReader("promote"))
        body = json.loads(response["body"])
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["verdict"], "PROMOTE")
        self.assertEqual(body["reason"], "VERIFIED")
        self.assertEqual(body["authority"], "P4_DETERMINISTIC_VERIFIER")
        self.assertEqual(body["cloud_status"], "ADVISORY")
        self.assertEqual(len(body["cockroachdb_operations"]), 2)

    def test_refuse_takes_no_action(self):
        response = http_api.handler(event("/demo/refuse"), None, FakeReader("refuse"))
        body = json.loads(response["body"])
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["verdict"], "REFUSE")
        self.assertEqual(body["reason"], "HASH_MISMATCH")
        self.assertEqual(body["action_taken"], "NONE")

    def test_memory_linkage_tamper_fails_closed(self):
        response = http_api.handler(
            event("/demo/promote"), None, FakeReader("promote", "receipt_hash")
        )
        body = json.loads(response["body"])
        self.assertEqual(response["statusCode"], 503)
        self.assertEqual(body["verdict"], "INVALID")
        self.assertEqual(body["reason"], "MEMORY_LINKAGE_INVALID")
        self.assertEqual(body["action_taken"], "NONE")

    def test_request_surface_is_fixed_and_bounded(self):
        cases = (
            (event("/demo/promote", "POST"), 405, "METHOD_NOT_ALLOWED"),
            (event("/demo/unknown"), 404, "ROUTE_NOT_FOUND"),
            (event("/demo/promote", body="x"), 400, "BODY_NOT_ALLOWED"),
            (event("/demo/promote", query={"x": "y"}), 400, "QUERY_NOT_ALLOWED"),
        )
        for request, status, reason in cases:
            with self.subTest(reason=reason):
                response = http_api.handler(request, None, FakeReader("promote"))
                body = json.loads(response["body"])
                self.assertEqual(response["statusCode"], status)
                self.assertEqual(body["reason"], reason)
                self.assertEqual(body["action_taken"], "NONE")

    def test_unknown_dependency_error_is_sanitized(self):
        class BrokenReader:
            def fetch(self, branch, query_vector):
                raise RuntimeError("password=do-not-leak")

        response = http_api.handler(event("/demo/promote"), None, BrokenReader())
        self.assertEqual(response["statusCode"], 503)
        self.assertNotIn("password", response["body"])
        self.assertIn("DEPENDENCY_UNAVAILABLE", response["body"])

    def test_response_is_deterministic(self):
        first = http_api.handler(event("/demo/promote"), None, FakeReader("promote"))
        second = http_api.handler(event("/demo/promote"), None, FakeReader("promote"))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
