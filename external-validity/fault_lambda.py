"""Disposable EV2 fault-injection Lambda.

This is campaign infrastructure, never product authority. It exists only to
produce a provider-observed timeout and a stale advisory payload, then it is
deleted. It has no network, filesystem, credential, or mutation surface.
"""
from __future__ import annotations

import time


def lambda_handler(event, context):
    del context
    if not isinstance(event, dict) or set(event) != {"fault_mode", "request_id"}:
        raise ValueError("MALFORMED_RECORD")
    if event["fault_mode"] == "timeout":
        time.sleep(3)
        return {"status": "ADVISORY", "request_id": event["request_id"]}
    if event["fault_mode"] == "stale":
        return {
            "status": "ADVISORY",
            "request_id": "stale-request-r0",
            "unknown_authority": "PROMOTE",
        }
    raise ValueError("UNSUPPORTED_FAULT_MODE")
