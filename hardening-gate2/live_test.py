#!/usr/bin/env python3
"""Exercise the deployed Gate 2 public API and direct Lambda boundary."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from deploy_demo import Aws, NAME, canonical, verify


PUBLIC_SPACING_SECONDS = 21.0


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_once(path: Path, value: bytes) -> str:
    if path.exists():
        raise RuntimeError(f"EVIDENCE_ALREADY_EXISTS:{path.name}")
    path.write_bytes(value)
    return sha256_bytes(value)


def event(path: str, method: str = "GET", body: str | None = None, query=None):
    return {
        "version": "2.0",
        "rawPath": path,
        "body": body,
        "queryStringParameters": query,
        "requestContext": {"http": {"method": method}},
    }


def public_call(
    endpoint: str,
    path: str,
    *,
    method: str = "GET",
    body: bytes | None = None,
) -> dict[str, Any]:
    request = Request(
        endpoint + path,
        data=body,
        method=method,
        headers={"user-agent": "ck-hardening-gate2-proof/1"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            raw = response.read()
            status = response.status
            headers = response.headers
    except HTTPError as exc:
        raw = exc.read()
        status = exc.code
        headers = exc.headers
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = None
    selected_headers = {
        key.lower(): headers.get(key)
        for key in ("cache-control", "content-type", "x-content-type-options")
        if headers.get(key) is not None
    }
    return {
        "status": status,
        "body": parsed,
        "body_bytes": len(raw),
        "body_sha256": sha256_bytes(raw),
        "headers": selected_headers,
        "raw": raw,
    }


def invoke(aws: Aws, evidence: Path, name: str, payload: dict[str, Any]):
    payload_path = evidence / f"{name}-request.json"
    response_path = evidence / f"{name}-response.json"
    request_bytes = canonical(payload) + b"\n"
    write_once(payload_path, request_bytes)
    metadata = aws.run(
        "lambda",
        "invoke",
        "--function-name",
        NAME,
        "--cli-binary-format",
        "raw-in-base64-out",
        "--payload",
        canonical(payload).decode("utf-8"),
        str(response_path),
    )
    if metadata.get("FunctionError") or metadata.get("StatusCode") != 200:
        raise RuntimeError(f"LAMBDA_INVOCATION_FAILED:{name}")
    raw = response_path.read_bytes()
    response = json.loads(raw)
    return {
        "request_sha256": sha256_bytes(request_bytes),
        "response_sha256": sha256_bytes(raw),
        "response": response,
        "executed_version": metadata.get("ExecutedVersion"),
    }


def response_body(invocation: dict[str, Any]) -> dict[str, Any]:
    response = invocation["response"]
    if not isinstance(response, dict) or not isinstance(response.get("body"), str):
        raise RuntimeError("LAMBDA_RESPONSE_INVALID")
    return json.loads(response["body"])


def require_live_result(result: dict[str, Any], branch: str) -> None:
    body = result.get("body")
    expected = (
        ("PROMOTE", "VERIFIED", "VERIFIED_CONTINUATION_AVAILABLE")
        if branch == "promote"
        else ("REFUSE", "HASH_MISMATCH", "NONE")
    )
    if result.get("status") != 200 or not isinstance(body, dict):
        raise RuntimeError(f"PUBLIC_{branch.upper()}_FAILED")
    observed = (body.get("verdict"), body.get("reason"), body.get("action_taken"))
    if observed != expected:
        raise RuntimeError(f"PUBLIC_{branch.upper()}_SEMANTICS_MISMATCH")
    if body.get("authority") != "P4_DETERMINISTIC_VERIFIER":
        raise RuntimeError("PUBLIC_AUTHORITY_MISMATCH")
    if body.get("cloud_status") != "ADVISORY":
        raise RuntimeError("PUBLIC_CLOUD_AUTHORITY_MISMATCH")
    if body.get("cockroachdb_operations") != [
        "TRANSACTIONAL_RECEIPT_LINKAGE_QUERY",
        "DISTRIBUTED_VECTOR_INDEX_QUERY",
    ]:
        raise RuntimeError("PUBLIC_COCKROACH_OPERATIONS_MISMATCH")


def strip_raw(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "raw"}


def main() -> int:
    repo = Path.cwd().resolve()
    evidence = repo / "evidence/hardening-gate2-live-r1"
    if evidence.exists():
        raise RuntimeError("LIVE_EVIDENCE_DIRECTORY_ALREADY_EXISTS")
    evidence.mkdir(parents=True)
    aws = Aws(repo)
    configuration = verify(repo)
    endpoint = configuration["endpoint"]

    public_results: dict[str, Any] = {}
    last_public = 0.0

    def paced_public(
        name: str,
        path: str,
        *,
        method: str = "GET",
        body: bytes | None = None,
        paced: bool = False,
    ) -> dict[str, Any]:
        nonlocal last_public
        if paced:
            remaining = PUBLIC_SPACING_SECONDS - (time.monotonic() - last_public)
            if remaining > 0:
                time.sleep(remaining)
        result = public_call(endpoint, path, method=method, body=body)
        last_public = time.monotonic()
        write_once(evidence / f"public-{name}-body.bin", result["raw"])
        public_results[name] = strip_raw(result)
        return result

    promote = paced_public("promote", "/demo/promote")
    refuse = paced_public("refuse", "/demo/refuse")
    require_live_result(promote, "promote")
    require_live_result(refuse, "refuse")

    invocations: dict[str, Any] = {}
    for branch in ("promote", "refuse"):
        responses = []
        for index in range(5):
            name = f"direct-{branch}-{index + 1}"
            record = invoke(aws, evidence, name, event(f"/demo/{branch}"))
            invocations[name] = record
            body_value = response_body(record)
            responses.append(
                (
                    record["response"].get("statusCode"),
                    body_value.get("verdict"),
                    body_value.get("reason"),
                    body_value.get("receipt_hash"),
                )
            )
        if len(set(responses)) != 1:
            raise RuntimeError(f"DIRECT_{branch.upper()}_NONDETERMINISTIC")

    direct_negative_cases = {
        "method": (event("/demo/promote", method="POST"), 405, "METHOD_NOT_ALLOWED"),
        "body": (event("/demo/promote", body="x"), 400, "BODY_NOT_ALLOWED"),
        "query": (
            event("/demo/promote", query={"x": "y"}),
            400,
            "QUERY_NOT_ALLOWED",
        ),
    }
    for name, (payload, expected_status, expected_reason) in direct_negative_cases.items():
        record = invoke(aws, evidence, f"direct-negative-{name}", payload)
        invocations[f"direct-negative-{name}"] = record
        body_value = response_body(record)
        if record["response"].get("statusCode") != expected_status:
            raise RuntimeError(f"DIRECT_NEGATIVE_{name.upper()}_STATUS_MISMATCH")
        if body_value.get("reason") != expected_reason or body_value.get(
            "action_taken"
        ) != "NONE":
            raise RuntimeError(f"DIRECT_NEGATIVE_{name.upper()}_SEMANTICS_MISMATCH")

    public_negative = {
        "method": paced_public(
            "negative-method", "/demo/promote", method="POST", paced=True
        ),
        "route": paced_public("negative-route", "/demo/unknown", paced=True),
        "query": paced_public("negative-query", "/demo/promote?x=y", paced=True),
        "body": paced_public(
            "negative-body", "/demo/promote", body=b"x", paced=True
        ),
    }
    expected_public = {
        "method": (404, None),
        "route": (404, None),
        "query": (400, "QUERY_NOT_ALLOWED"),
        "body": (400, "BODY_NOT_ALLOWED"),
    }
    for name, result in public_negative.items():
        status, reason = expected_public[name]
        if result["status"] != status:
            raise RuntimeError(f"PUBLIC_NEGATIVE_{name.upper()}_STATUS_MISMATCH")
        if reason is not None:
            body_value = result.get("body")
            if not isinstance(body_value, dict) or body_value.get("reason") != reason:
                raise RuntimeError(
                    f"PUBLIC_NEGATIVE_{name.upper()}_SEMANTICS_MISMATCH"
                )

    local_promote = json.loads(
        (repo / "evidence/p9-completion-live-r1/promote-fresh-trial.json").read_text()
    )
    local_refuse = json.loads(
        (repo / "evidence/p9-completion-live-r1/refuse-fresh-trial.json").read_text()
    )
    live_promote = promote["body"]
    live_refuse = refuse["body"]
    equivalence = {
        "promote": {
            "local": [
                local_promote["verdicts"][0]["verdict"],
                local_promote["verdicts"][0]["reason"],
            ],
            "live": [live_promote["verdict"], live_promote["reason"]],
        },
        "refuse": {
            "local": [
                local_refuse["verdicts"][0]["verdict"],
                local_refuse["verdicts"][0]["reason"],
            ],
            "live": [live_refuse["verdict"], live_refuse["reason"]],
        },
    }
    if any(item["local"] != item["live"] for item in equivalence.values()):
        raise RuntimeError("LIVE_REPLAY_EQUIVALENCE_MISMATCH")

    result = {
        "version": "ck-hardening-gate2-live-proof-v1",
        "status": "LIVE_BEHAVIOR_GREEN",
        "configuration": configuration,
        "public_results": public_results,
        "direct_invocation_count": len(invocations),
        "direct_invocation_hashes": {
            name: {
                "request_sha256": item["request_sha256"],
                "response_sha256": item["response_sha256"],
            }
            for name, item in invocations.items()
        },
        "five_repeat_promote": "GREEN",
        "five_repeat_refuse": "GREEN",
        "negative_method": "GREEN",
        "negative_route": "GREEN",
        "negative_query": "GREEN",
        "negative_body": "GREEN",
        "live_replay_equivalence": equivalence,
        "judge_credentials_required": False,
        "secret_value_read": False,
    }
    result_path = evidence / "live-test-result.json"
    result_bytes = canonical(result) + b"\n"
    write_once(result_path, result_bytes)
    manifest = {
        "version": "ck-hardening-gate2-live-manifest-v1",
        "files": [
            {
                "path": path.relative_to(evidence).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in sorted(evidence.rglob("*"))
            if path.is_file()
        ],
    }
    manifest["manifest_hash"] = hashlib.sha256(canonical(manifest)).hexdigest()
    write_once(evidence / "evidence-manifest.json", canonical(manifest) + b"\n")
    print(
        canonical(
            {
                "status": result["status"],
                "public_endpoint": endpoint,
                "direct_invocation_count": len(invocations),
                "manifest_hash": manifest["manifest_hash"],
            }
        ).decode("utf-8")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
