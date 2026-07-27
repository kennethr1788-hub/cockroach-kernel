#!/usr/bin/env python3
"""Credential-free smoke of the installed Gate 2 bundle tree."""
from __future__ import annotations

import json

from cockroach_kernel import http_api


class Reader:
    def fetch(self, branch: str, query_vector: list[float]):
        del query_vector
        trial = http_api._expected(branch)
        return {
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


def event(path: str):
    return {
        "version": "2.0",
        "rawPath": path,
        "body": None,
        "queryStringParameters": None,
        "requestContext": {"http": {"method": "GET"}},
    }


def main() -> int:
    promote = http_api.handler(event("/demo/promote"), None, Reader())
    refuse = http_api.handler(event("/demo/refuse"), None, Reader())
    promote_body = json.loads(promote["body"])
    refuse_body = json.loads(refuse["body"])
    assert promote["statusCode"] == 200
    assert promote_body["verdict"] == "PROMOTE"
    assert promote_body["reason"] == "VERIFIED"
    assert refuse["statusCode"] == 200
    assert refuse_body["verdict"] == "REFUSE"
    assert refuse_body["reason"] == "HASH_MISMATCH"
    assert refuse_body["action_taken"] == "NONE"
    print(json.dumps({"bundle_smoke": "GREEN"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
