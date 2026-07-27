"""Bounded AWS HTTP API facade over live CockroachDB memory linkage.

The HTTP surface accepts only two fixed GET routes. CockroachDB supplies the
persistent receipt, request, result, and vector linkage; the packaged P4
verifier remains the sole verdict authority. Cloud and database output is
strictly checked and never chooses code, SQL, paths, tools, or destinations.
"""
from __future__ import annotations

import hashlib
import json
import os
import ssl
from typing import Any, Protocol

from cockroach_kernel.cli import canonical_json, digest


MAX_HTTP_EVENT_BYTES = 32_768
MAX_HTTP_RESPONSE_BYTES = 16_384
ROUTES = {
    "/demo/promote": "promote",
    "/demo/refuse": "refuse",
}
EXPECTED_MEMORY_FIELDS = {
    "task_id",
    "receipt_hash",
    "event_hash",
    "vector_digest",
    "request_hash",
    "response_hash",
    "result_hash",
    "candidate_id",
    "status",
    "distance",
}


class MemoryReader(Protocol):
    def fetch(self, branch: str, query_vector: list[float]) -> dict[str, Any]: ...


class ApiFailure(RuntimeError):
    """Stable sanitized HTTP failure; raw provider errors never enter output."""

    def __init__(self, code: str, status: int) -> None:
        super().__init__(code)
        self.code = code
        self.status = status


def _runtime_modules() -> tuple[Any, Any]:
    from cockroach_kernel.cli import _runtime

    run_offline = _runtime()
    import lambda_handler
    import live_completion

    return lambda_handler, live_completion


def _require_hex(value: Any) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ApiFailure("MEMORY_RECORD_INVALID", 503)
    try:
        int(value, 16)
    except ValueError as exc:
        raise ApiFailure("MEMORY_RECORD_INVALID", 503) from exc
    return value


def _bounded_event(event: Any) -> dict[str, Any]:
    if not isinstance(event, dict):
        raise ApiFailure("REQUEST_INVALID", 400)
    try:
        encoded = canonical_json(event)
    except ValueError as exc:
        raise ApiFailure("REQUEST_INVALID", 400) from exc
    if len(encoded) > MAX_HTTP_EVENT_BYTES:
        raise ApiFailure("REQUEST_TOO_LARGE", 413)
    return event


def _route(event: dict[str, Any]) -> str:
    request_context = event.get("requestContext")
    http = request_context.get("http") if isinstance(request_context, dict) else None
    method = http.get("method") if isinstance(http, dict) else None
    path = event.get("rawPath")
    if method != "GET":
        raise ApiFailure("METHOD_NOT_ALLOWED", 405)
    if event.get("body") not in (None, ""):
        raise ApiFailure("BODY_NOT_ALLOWED", 400)
    query = event.get("queryStringParameters")
    if query not in (None, {}):
        raise ApiFailure("QUERY_NOT_ALLOWED", 400)
    if path not in ROUTES:
        raise ApiFailure("ROUTE_NOT_FOUND", 404)
    return ROUTES[path]


def _expected(branch: str) -> dict[str, Any]:
    _, live_completion = _runtime_modules()
    trial_id = (
        live_completion.coordinator.PROMOTE_TRIAL_ID
        if branch == "promote"
        else live_completion.coordinator.REFUSE_TRIAL_ID
    )
    return live_completion.prepared_trial(trial_id)


def _validate_memory(record: Any, trial: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict) or set(record) != EXPECTED_MEMORY_FIELDS:
        raise ApiFailure("MEMORY_RECORD_INVALID", 503)
    for key in (
        "receipt_hash",
        "event_hash",
        "vector_digest",
        "request_hash",
        "response_hash",
        "result_hash",
    ):
        _require_hex(record[key])
    if record["status"] != "ADVISORY":
        raise ApiFailure("MEMORY_AUTHORITY_INVALID", 503)
    if isinstance(record["distance"], bool) or not isinstance(record["distance"], (int, float)):
        raise ApiFailure("MEMORY_RECORD_INVALID", 503)
    expected = {
        "task_id": trial["task_id"],
        "receipt_hash": trial["receipt_hash"],
        "event_hash": trial["event_hash"],
        "vector_digest": trial["vector_digest"],
        "request_hash": trial["request"]["request_hash"],
        "candidate_id": trial["candidate"]["candidate_id"],
    }
    if any(record[key] != value for key, value in expected.items()):
        raise ApiFailure("MEMORY_LINKAGE_INVALID", 503)
    if abs(float(record["distance"])) > 0.000001:
        raise ApiFailure("MEMORY_VECTOR_MISMATCH", 503)
    return record


def evaluate(branch: str, reader: MemoryReader) -> dict[str, Any]:
    lambda_handler, live_completion = _runtime_modules()
    trial = _expected(branch)
    memory = _validate_memory(reader.fetch(branch, trial["vector"]), trial)
    advisory = lambda_handler.evaluate(trial["request"])
    if advisory["status"] != "ADVISORY":
        raise ApiFailure("ADVISORY_AUTHORITY_INVALID", 503)
    verifier = live_completion._load_verifier()
    verdicts = [verifier.verify(trial["candidate"]) for _ in range(5)]
    if len(set(verdicts)) != 1:
        raise ApiFailure("VERDICT_NONDETERMINISTIC", 503)
    verdict, reason = verdicts[0]
    expected_verdict = "PROMOTE" if branch == "promote" else "REFUSE"
    if verdict != expected_verdict:
        raise ApiFailure("VERDICT_UNEXPECTED", 503)
    body = {
        "version": "ck-public-demo-v1",
        "mode": "LIVE_COCKROACH_MEMORY_WITH_DETERMINISTIC_LOCAL_AUTHORITY",
        "branch": branch,
        "verdict": verdict,
        "reason": reason,
        "provable_state": {
            "candidate_id": memory["candidate_id"],
            "event_hash": memory["event_hash"],
            "receipt_hash": memory["receipt_hash"],
            "request_hash": memory["request_hash"],
            "response_hash": memory["response_hash"],
            "result_hash": memory["result_hash"],
            "vector_digest": memory["vector_digest"],
            "vector_distance": round(float(memory["distance"]), 6),
        },
        "action_taken": "VERIFIED_CONTINUATION_AVAILABLE" if verdict == "PROMOTE" else "NONE",
        "next_safe_action": (
            "Inspect the linked receipt before continuing."
            if verdict == "PROMOTE"
            else "Inspect the linked receipt and provide an untampered declared candidate."
        ),
        "authority": "P4_DETERMINISTIC_VERIFIER",
        "cloud_status": advisory["status"],
        "cockroachdb_operations": [
            "TRANSACTIONAL_RECEIPT_LINKAGE_QUERY",
            "DISTRIBUTED_VECTOR_INDEX_QUERY",
        ],
    }
    body["receipt_hash"] = digest(body)
    return body


def _http_response(status: int, body: dict[str, Any]) -> dict[str, Any]:
    raw = canonical_json(body)
    if len(raw) > MAX_HTTP_RESPONSE_BYTES:
        raise ApiFailure("RESPONSE_TOO_LARGE", 500)
    return {
        "statusCode": status,
        "headers": {
            "cache-control": "no-store",
            "content-type": "application/json; charset=utf-8",
            "x-content-type-options": "nosniff",
        },
        "isBase64Encoded": False,
        "body": raw.decode("utf-8"),
    }


def handler(event: Any, context: Any, reader: MemoryReader | None = None) -> dict[str, Any]:
    del context
    try:
        bounded = _bounded_event(event)
        branch = _route(bounded)
        result = evaluate(branch, reader or PgMemoryReader.from_environment())
        return _http_response(200, result)
    except ApiFailure as exc:
        return _http_response(
            exc.status,
            {
                "version": "ck-public-demo-error-v1",
                "verdict": "INVALID",
                "reason": exc.code,
                "action_taken": "NONE",
            },
        )
    except Exception:
        return _http_response(
            503,
            {
                "version": "ck-public-demo-error-v1",
                "verdict": "INVALID",
                "reason": "DEPENDENCY_UNAVAILABLE",
                "action_taken": "NONE",
            },
        )


_SECRET_CACHE: dict[str, Any] | None = None


def _load_secret(secret_id: str) -> dict[str, Any]:
    global _SECRET_CACHE
    if _SECRET_CACHE is not None:
        return dict(_SECRET_CACHE)
    try:
        import boto3

        response = boto3.client("secretsmanager").get_secret_value(SecretId=secret_id)
        value = json.loads(response["SecretString"])
    except Exception as exc:
        raise ApiFailure("SECRET_UNAVAILABLE", 503) from exc
    required = {"host", "port", "database", "user", "password"}
    if not isinstance(value, dict) or set(value) != required:
        raise ApiFailure("SECRET_SCHEMA_INVALID", 503)
    if not isinstance(value["port"], int) or not 1 <= value["port"] <= 65535:
        raise ApiFailure("SECRET_SCHEMA_INVALID", 503)
    for key in required - {"port"}:
        if not isinstance(value[key], str) or not value[key]:
            raise ApiFailure("SECRET_SCHEMA_INVALID", 503)
    _SECRET_CACHE = dict(value)
    return value


class PgMemoryReader:
    """Read-only, parameterized CockroachDB query adapter."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    @classmethod
    def from_environment(cls) -> "PgMemoryReader":
        secret_id = os.environ.get("CK_DEMO_SECRET_ID")
        if not secret_id:
            raise ApiFailure("SECRET_CONFIGURATION_MISSING", 503)
        secret = _load_secret(secret_id)
        try:
            from pg8000.native import Connection

            connection = Connection(
                user=secret["user"],
                password=secret["password"],
                host=secret["host"],
                port=secret["port"],
                database=secret["database"],
                ssl_context=ssl.create_default_context(),
                timeout=4,
            )
        except Exception as exc:
            raise ApiFailure("COCKROACH_CONNECTION_FAILED", 503) from exc
        return cls(connection)

    def fetch(self, branch: str, query_vector: list[float]) -> dict[str, Any]:
        task_id = "ck-p9-live-promote-r1" if branch == "promote" else "ck-p9-live-refuse-r1"
        vector_text = "[" + ",".join(format(value, ".6f") for value in query_vector) + "]"
        linkage_sql = """
SELECT t.task_id,
       encode(r.receipt_hash, 'hex'),
       encode(r.event_hash, 'hex'),
       encode(v.vector_digest, 'hex'),
       encode(w.request_hash, 'hex'),
       encode(w.response_hash, 'hex'),
       encode(w.result_hash, 'hex'),
       w.candidate_id,
       w.status
FROM ck.tasks AS t
JOIN ck.receipts AS r ON r.task_id = t.task_id
JOIN ck.context_vectors AS v ON v.task_id = t.task_id AND v.event_hash = r.event_hash
JOIN ck.worker_results AS w ON w.task_id = t.task_id
WHERE t.task_id = :task_id
LIMIT 1
"""
        vector_sql = """
SELECT vector <-> CAST(:query_vector AS VECTOR(64)) AS distance
FROM ck.context_vectors
WHERE task_id = :task_id AND namespace = 'ck-p9-completion'
ORDER BY vector <-> CAST(:query_vector AS VECTOR(64))
LIMIT 1
"""
        try:
            linkage_rows = self.connection.run(linkage_sql, task_id=task_id)
            vector_rows = self.connection.run(
                vector_sql, task_id=task_id, query_vector=vector_text
            )
        except Exception as exc:
            raise ApiFailure("COCKROACH_QUERY_FAILED", 503) from exc
        if len(linkage_rows) != 1 or len(vector_rows) != 1:
            raise ApiFailure("MEMORY_RECORD_MISSING", 503)
        row = linkage_rows[0]
        if not isinstance(row, (list, tuple)) or len(row) != 9:
            raise ApiFailure("MEMORY_RECORD_INVALID", 503)
        return {
            "task_id": row[0],
            "receipt_hash": row[1],
            "event_hash": row[2],
            "vector_digest": row[3],
            "request_hash": row[4],
            "response_hash": row[5],
            "result_hash": row[6],
            "candidate_id": row[7],
            "status": row[8],
            "distance": vector_rows[0][0],
        }


lambda_handler = handler
