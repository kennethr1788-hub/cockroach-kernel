#!/usr/bin/env python3
"""Deterministic keyless P9 vertical-slice replay using existing local authority."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

import context_vector
import faults
import lambda_handler
import mock_transports
import records

BASE = Path(__file__).resolve().parents[1]


def _load_verifier():
    path = BASE / "p4-verifier" / "verifier.py"
    spec = importlib.util.spec_from_file_location("p4_verifier_authority", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("P4_VERIFIER_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _features() -> dict[str, Any]:
    return {
        "event_count": 3,
        "approvals": 2,
        "refusals": 0,
        "context_relevance": 0.875,
        "quorum_met": True,
        "policy_veto": False,
        "tampered": False,
        "unsafe": False,
        "warrant_consumed": False,
    }


def fresh_resume(capsule_bytes: bytes) -> tuple[bool, str]:
    try:
        capsule = json.loads(capsule_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False, "MALFORMED_CAPSULE"
    if records.canonical_json(capsule) != capsule_bytes:
        return False, "NON_CANONICAL_CAPSULE"
    if set(capsule) != {"version", "task_id", "receipt_hash", "candidate_id", "verdict", "capsule_hash"}:
        return False, "CAPSULE_FIELDS_INVALID"
    body = {key: capsule[key] for key in capsule if key != "capsule_hash"}
    if capsule["capsule_hash"] != records.sha256_hex(body):
        return False, "CAPSULE_HASH_MISMATCH"
    if capsule["version"] != "p9-resume-v1" or capsule["verdict"] != "PROMOTE":
        return False, "CAPSULE_NOT_PROMOTED"
    return True, "FRESH_CONTEXT_PASS"


def run() -> dict[str, Any]:
    verifier = _load_verifier()
    task_id = "p9-offline-task-1"
    candidate_id = "p9-offline-candidate-1"
    declared = {"task_id": task_id, "work": "continue synthetic feature"}
    declared_hash = records.sha256_hex(declared)
    event = {"sequence": 0, "parent_hash": "0" * 64, "state_hash": declared_hash}
    event_hash = records.sha256_hex(event)
    receipt = {"task_id": task_id, "event_hash": event_hash, "status": "SEALED"}
    receipt_hash = records.sha256_hex(receipt)

    vector = context_vector.context_vector("continue synthetic feature", "p9-offline")
    vector_hash = context_vector.vector_digest(vector)

    request = records.make_request(
        "p9-offline-request-1", task_id, candidate_id,
        event_hash, records.sha256_hex({"candidate": candidate_id}),
        records.sha256_hex({"policy": "p8-frozen"}), _features(),
    )
    lambda_client = mock_transports.CheckedLambdaClient(mock_transports.MockLambdaTransport())
    delivery, response = lambda_client.call(request)
    if response["status"] != "ADVISORY":
        raise RuntimeError("CLOUD_AUTHORITY_VIOLATION")
    worker_result = {
        "request_hash": request["request_hash"],
        "response_hash": response["response_hash"],
        "status": response["status"],
    }
    worker_result_hash = records.sha256_hex(worker_result)

    projection_body = {
        "event_id": "projection-1", "cursor": 1,
        "source_hash": worker_result_hash, "receipt_hash": receipt_hash,
        "payload_hash": records.sha256_hex(worker_result),
    }
    projection = dict(projection_body, projection_hash=records.sha256_hex(projection_body))
    projector = faults.ChangefeedProjection()
    projection_state = projector.accept(projection)

    mcp = mock_transports.MockManagedMCP(
        "p9-offline", [task_id],
        [{"task_id": task_id, "receipt_hash": receipt_hash,
          "status": "SEALED", "event_hash": event_hash}],
    )
    mcp_result = mcp.query(
        "SELECT task_id, receipt_hash, status, event_hash "
        "FROM ck.mcp_receipt_view WHERE task_id = 'p9-offline-task-1' LIMIT 1"
    )

    payload = {"path": "src/feature.py", "content_hash": records.sha256_hex(b"synthetic feature")}
    candidate = {
        "version": "p4-v1",
        "candidate_id": candidate_id,
        "source_receipt_hash": receipt_hash,
        "payload": payload,
        "payload_hash": verifier.digest(payload),
        "schema_version": "p4-v1",
        "provenance": {"source": "p9-offline-evidence"},
        "supported": True,
        "one_use_state": "ISSUED",
        "quarantined": False,
        "policy_veto": False,
        "requested_paths": ["src/feature.py"],
        "declared_paths": ["src/feature.py"],
    }
    tampered = copy.deepcopy(candidate)
    tampered["payload"]["content_hash"] = "f" * 64
    tampered_verdict, tampered_reason = verifier.verify(tampered)
    verdict, verdict_reason = verifier.verify(candidate)

    capsule_body = {
        "version": "p9-resume-v1", "task_id": task_id,
        "receipt_hash": receipt_hash, "candidate_id": candidate_id,
        "verdict": verdict,
    }
    capsule = dict(capsule_body, capsule_hash=records.sha256_hex(capsule_body))
    capsule_bytes = records.canonical_json(capsule)
    resumed, resume_reason = fresh_resume(capsule_bytes)

    result = {
        "version": "p9-offline-result-v1",
        "task_id": task_id,
        "declared_hash": declared_hash,
        "receipt_hash": receipt_hash,
        "vector_hash": vector_hash,
        "lambda_delivery": delivery,
        "lambda_status": response["status"],
        "worker_result_hash": worker_result_hash,
        "projection_state": projection_state,
        "projection_cursor": projector.cursor,
        "mcp_result_hash": mcp_result["result_hash"],
        "mcp_rows": mcp_result["row_count"],
        "tampered_verdict": tampered_verdict,
        "tampered_reason": tampered_reason,
        "local_verdict": verdict,
        "local_reason": verdict_reason,
        "fresh_context": resumed,
        "fresh_context_reason": resume_reason,
        "capsule_hash": capsule["capsule_hash"],
    }
    result["result_hash"] = records.sha256_hex(result)
    return result


def main() -> int:
    result = run()
    print(records.canonical_json(result).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
