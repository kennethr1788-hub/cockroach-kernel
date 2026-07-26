"""P9 local deterministic mock transports for Lambda and Managed MCP.

Synthetic, deterministic, standard library only. These mocks stand in for the
two cloud edges of the bounded P9 vertical slice so the slice can be exercised
offline with byte-identical repeatability:

- MockLambdaTransport: a scripted, local stand-in for the Lambda invocation
  path. It can produce success, timeout, throttle, malformed, duplicate, and
  stale response cases. It performs no network I/O, no threads, no clock, and
  no randomness; every behavior is derived from an explicit per-request script.
- CheckedLambdaClient: the strict client side. It validates every response
  against the canonical schema, binds it to its request, treats byte-identical
  repeat delivery of an accepted response as an idempotent duplicate, refuses
  stale or conflicting responses, and retries only timeout/throttle with a
  bounded attempt budget.
- MockManagedMCP: an exact read-only allowlist for one bounded SELECT against
  ck.mcp_receipt_view by task_id with a finite LIMIT. DDL, DML, comments,
  multi-statements, unknown fields, oversized results, and namespace mismatch
  are refused with stable codes, and every decision is audit-logged as a hash.

These mocks produce untrusted evidence only. No mock output is a promotion,
refusal, or invalid decision. No network, filesystem, credential, model,
random, or time access.
"""
from __future__ import annotations

import copy
import re
from typing import Any

import lambda_handler
from records import (
    CloudError,
    VERSION,
    request_body,
    require_hash,
    require_id,
    response_matches_request,
    sha256_hex,
    validate_request,
    validate_response,
)

# ---------------------------------------------------------------------------
# Mock Lambda transport
# ---------------------------------------------------------------------------

# Closed set of scripted per-invocation behaviors.
LAMBDA_BEHAVIORS = ("success", "timeout", "throttle", "malformed", "duplicate", "stale")

# Client-side outcome labels for CheckedLambdaClient.call.
CALL_ACCEPTED = "ACCEPTED"
CALL_DUPLICATE = "DUPLICATE"

# Retryable transport fault codes; everything else fails immediately.
RETRYABLE_CODES = ("LAMBDA_TIMEOUT", "LAMBDA_THROTTLED")


class MockLambdaTransport:
    """Deterministic scripted local stand-in for the Lambda invocation path.

    The script maps request_id to an ordered queue of behavior labels. Each
    invoke consumes the head of the queue; once one label remains it repeats
    for every further invoke of that request, so every script is total and
    deterministic. Unscripted requests behave as "success".
    """

    def __init__(self, script: dict[str, list[str]] | None = None) -> None:
        self._script: dict[str, list[str]] = {}
        for request_id, queue in (script or {}).items():
            require_id(request_id)
            if not isinstance(queue, list) or not queue:
                raise CloudError("MALFORMED_RECORD")
            for behavior in queue:
                if behavior not in LAMBDA_BEHAVIORS:
                    raise CloudError("MALFORMED_RECORD")
            self._script[request_id] = list(queue)
        # request_ids in invocation order (includes faulted attempts).
        self.invocations: list[str] = []
        # First recorded successful response per request_id (duplicate source).
        self.responses: dict[str, dict[str, Any]] = {}

    def _next_behavior(self, request_id: str) -> str:
        queue = self._script.get(request_id)
        if not queue:
            return "success"
        behavior = queue[0]
        if len(queue) > 1:
            queue.pop(0)
        return behavior

    def _record_success(self, request: dict[str, Any]) -> dict[str, Any]:
        response = lambda_handler.evaluate(request)
        self.responses.setdefault(request["request_id"], copy.deepcopy(response))
        return response

    def _malformed_response(self, request: dict[str, Any]) -> dict[str, Any]:
        # Deterministic structurally broken payload: fails strict validation.
        return {
            "version": VERSION,
            "request_id": request["request_id"],
            "status": "GARBAGE",
        }

    def _duplicate_response(self, request: dict[str, Any]) -> dict[str, Any]:
        # Re-serve the first recorded response byte-identically (at-least-once
        # replay). If no delivery was recorded yet, this IS the first delivery.
        recorded = self.responses.get(request["request_id"])
        if recorded is not None:
            return copy.deepcopy(recorded)
        return self._record_success(request)

    def _stale_response(self, request: dict[str, Any]) -> dict[str, Any]:
        # A well-formed response bound to a superseded candidate hash: it
        # passes response validation but does not match the live request.
        modified = copy.deepcopy(request)
        candidate_hash = modified["candidate_hash"]
        flipped = "1" if candidate_hash[0] == "0" else "0"
        modified["candidate_hash"] = flipped + candidate_hash[1:]
        modified["request_hash"] = sha256_hex(request_body(modified))
        return lambda_handler.evaluate(modified)

    def invoke(self, request: dict[str, Any]) -> dict[str, Any]:
        """One deterministic local invocation; timeout/throttle raise CloudError."""
        validate_request(request)
        request_id = request["request_id"]
        behavior = self._next_behavior(request_id)
        self.invocations.append(request_id)
        if behavior == "timeout":
            raise CloudError("LAMBDA_TIMEOUT")
        if behavior == "throttle":
            raise CloudError("LAMBDA_THROTTLED")
        if behavior == "malformed":
            return self._malformed_response(request)
        if behavior == "duplicate":
            return self._duplicate_response(request)
        if behavior == "stale":
            return self._stale_response(request)
        return self._record_success(request)


class CheckedLambdaClient:
    """Strict client side of the mock Lambda path.

    Every response is schema-validated and bound to its request before
    acceptance. A byte-identical repeat of an already-accepted response is an
    idempotent duplicate, not new work; a different response for an accepted
    request_id is a conflict and fails closed.
    """

    def __init__(self, transport: MockLambdaTransport) -> None:
        self.transport = transport
        # request_id -> canonical digest of the accepted response.
        self.accepted: dict[str, str] = {}

    def call(self, request: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        validate_request(request)
        response = self.transport.invoke(request)
        validate_response(response)
        if not response_matches_request(request, response):
            raise CloudError("STALE_RESPONSE")
        digest = sha256_hex(response)
        prior = self.accepted.get(request["request_id"])
        if prior is not None:
            if prior == digest:
                return (CALL_DUPLICATE, response)
            raise CloudError("RESPONSE_CONFLICT")
        self.accepted[request["request_id"]] = digest
        return (CALL_ACCEPTED, response)

    def call_with_retries(self, request: dict[str, Any],
                          max_attempts: int = 3) -> tuple[str, dict[str, Any]]:
        """Bounded retry over timeout/throttle only; no sleeping, no clock."""
        if isinstance(max_attempts, bool) or not isinstance(max_attempts, int):
            raise CloudError("MALFORMED_RECORD")
        if max_attempts < 1:
            raise CloudError("MALFORMED_RECORD")
        attempts = 0
        while True:
            attempts += 1
            try:
                return self.call(request)
            except CloudError as exc:
                code = exc.args[0] if exc.args else ""
                if code not in RETRYABLE_CODES:
                    raise
                if attempts < max_attempts:
                    continue
                raise CloudError("RETRY_EXHAUSTED") from exc


# ---------------------------------------------------------------------------
# Mock Managed MCP transport
# ---------------------------------------------------------------------------

# Exact column surface of ck.mcp_receipt_view (mirrors migrations/001_cloud.sql).
VIEW_COLUMNS = ("task_id", "receipt_hash", "status", "event_hash")

# Receipt statuses the view may expose (mirrors the ck.receipts CHECK).
VIEW_STATUSES = ("DECLARED", "SEALED", "ADVISORY")

# Hard bound on rows any single query may return; LIMIT above this is refused.
MAX_MCP_ROWS = 64

# Word-boundary keyword refusals. The allowlist is one exact SELECT shape, so
# any DDL/DML/other statement keyword anywhere in the text fails closed.
_KEYWORD_REFUSALS = {
    # DDL
    "create": "MCP_DDL_REFUSED", "drop": "MCP_DDL_REFUSED",
    "alter": "MCP_DDL_REFUSED", "truncate": "MCP_DDL_REFUSED",
    "grant": "MCP_DDL_REFUSED", "revoke": "MCP_DDL_REFUSED",
    "comment": "MCP_DDL_REFUSED", "rename": "MCP_DDL_REFUSED",
    # DML
    "insert": "MCP_DML_REFUSED", "update": "MCP_DML_REFUSED",
    "delete": "MCP_DML_REFUSED", "upsert": "MCP_DML_REFUSED",
    "merge": "MCP_DML_REFUSED", "replace": "MCP_DML_REFUSED",
    "copy": "MCP_DML_REFUSED",
    # Anything else that is not the one allowed SELECT shape
    "set": "MCP_FORBIDDEN_STATEMENT", "show": "MCP_FORBIDDEN_STATEMENT",
    "explain": "MCP_FORBIDDEN_STATEMENT", "begin": "MCP_FORBIDDEN_STATEMENT",
    "commit": "MCP_FORBIDDEN_STATEMENT", "rollback": "MCP_FORBIDDEN_STATEMENT",
    "use": "MCP_FORBIDDEN_STATEMENT", "execute": "MCP_FORBIDDEN_STATEMENT",
    "call": "MCP_FORBIDDEN_STATEMENT", "prepare": "MCP_FORBIDDEN_STATEMENT",
    "deallocate": "MCP_FORBIDDEN_STATEMENT", "vacuum": "MCP_FORBIDDEN_STATEMENT",
    "analyze": "MCP_FORBIDDEN_STATEMENT", "import": "MCP_FORBIDDEN_STATEMENT",
    "export": "MCP_FORBIDDEN_STATEMENT", "backup": "MCP_FORBIDDEN_STATEMENT",
    "restore": "MCP_FORBIDDEN_STATEMENT", "cancel": "MCP_FORBIDDEN_STATEMENT",
}

_WORD_RE = re.compile(r"[A-Za-z]+")

# The one allowed shape: SELECT <cols> FROM ck.mcp_receipt_view
#   WHERE task_id = '<id>' LIMIT <n>
_STRICT_QUERY_RE = re.compile(
    r"\s*SELECT\s+(?P<cols>[A-Za-z0-9_]+(?:\s*,\s*[A-Za-z0-9_]+)*)"
    r"\s+FROM\s+ck\.mcp_receipt_view"
    r"\s+WHERE\s+task_id\s*=\s*'(?P<task_id>[A-Za-z0-9._-]+)'"
    r"\s+LIMIT\s+(?P<limit>[0-9]+)\s*",
    re.IGNORECASE,
)

# Loose prefix used only to classify unknown-field rejections precisely.
_SELECT_LIST_RE = re.compile(
    r"\s*SELECT\s+(?P<cols>.*?)\s+FROM\s+ck\.mcp_receipt_view\b",
    re.IGNORECASE | re.DOTALL,
)


class MockManagedMCP:
    """Deterministic local stand-in for read-only Managed MCP.

    Allows exactly one bounded SELECT shape against ck.mcp_receipt_view by
    task_id with a finite LIMIT, over an injected in-memory row set scoped to
    one declared namespace of synthetic task IDs. Everything else fails closed
    with a stable refusal code. Every decision is recorded in a sanitized
    audit log (outcome, code, and the SHA-256 of the query text — never the
    raw text or any payload).
    """

    def __init__(self, namespace: str, tasks: list[str],
                 rows: list[dict[str, Any]]) -> None:
        require_id(namespace)
        self.namespace = namespace
        self._tasks: set[str] = set()
        for task_id in tasks:
            require_id(task_id)
            self._tasks.add(task_id)
        self._rows: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            self._validate_row(row)
            self._rows.setdefault(row["task_id"], []).append(dict(row))
        self.audit: list[dict[str, Any]] = []

    def _validate_row(self, row: Any) -> None:
        if not isinstance(row, dict) or set(row) != set(VIEW_COLUMNS):
            raise CloudError("MALFORMED_RECORD")
        require_id(row["task_id"])
        require_hash(row["receipt_hash"])
        require_hash(row["event_hash"])
        if row["status"] not in VIEW_STATUSES:
            raise CloudError("MALFORMED_RECORD")
        if row["task_id"] not in self._tasks:
            raise CloudError("MCP_NAMESPACE_MISMATCH")

    def _audit(self, outcome: str, code: str, sql: Any) -> None:
        self.audit.append({
            "outcome": outcome,
            "code": code,
            "sql_sha256": sha256_hex(sql.encode("utf-8")) if isinstance(sql, str) else None,
        })

    def _check_statement_text(self, sql: str) -> None:
        if ";" in sql:
            raise CloudError("MCP_MULTI_STATEMENT_REFUSED")
        if "--" in sql or "/*" in sql or "*/" in sql:
            raise CloudError("MCP_COMMENT_REFUSED")
        for word in _WORD_RE.findall(sql):
            code = _KEYWORD_REFUSALS.get(word.lower())
            if code is not None:
                raise CloudError(code)

    def _parse_allowlisted_query(self, sql: str) -> tuple[list[str], str, int]:
        match = _STRICT_QUERY_RE.fullmatch(sql)
        if match is None:
            # Distinguish an unknown select-list field from a broken shape.
            loose = _SELECT_LIST_RE.match(sql)
            if loose is not None:
                cols = [part.strip().lower() for part in loose.group("cols").split(",")]
                if not cols or any(col not in VIEW_COLUMNS for col in cols):
                    raise CloudError("MCP_UNKNOWN_FIELD")
            raise CloudError("MCP_MALFORMED_QUERY")
        cols = [part.strip().lower() for part in match.group("cols").split(",")]
        if any(col not in VIEW_COLUMNS for col in cols):
            raise CloudError("MCP_UNKNOWN_FIELD")
        if len(set(cols)) != len(cols):
            raise CloudError("MCP_MALFORMED_QUERY")
        limit = int(match.group("limit"))
        if limit > MAX_MCP_ROWS:
            raise CloudError("MCP_RESULT_TOO_LARGE")
        if limit < 1:
            raise CloudError("MCP_MALFORMED_QUERY")
        task_id = match.group("task_id")
        require_id(task_id)
        if task_id not in self._tasks:
            raise CloudError("MCP_NAMESPACE_MISMATCH")
        return cols, task_id, limit

    def _execute(self, sql: Any) -> dict[str, Any]:
        if not isinstance(sql, str):
            raise CloudError("WRONG_TYPE")
        if not sql.strip():
            raise CloudError("MCP_MALFORMED_QUERY")
        self._check_statement_text(sql)
        cols, task_id, limit = self._parse_allowlisted_query(sql)
        selected = [
            {col: row[col] for col in cols}
            for row in self._rows.get(task_id, [])[:limit]
        ]
        result = {"columns": cols, "rows": selected, "row_count": len(selected)}
        result["result_hash"] = sha256_hex({"columns": cols, "rows": selected})
        return result

    def query(self, sql: Any) -> dict[str, Any]:
        """Run one query against the allowlist; refuses closed with audit."""
        try:
            result = self._execute(sql)
        except CloudError as exc:
            self._audit("REFUSE", exc.args[0] if exc.args else "MALFORMED_RECORD", sql)
            raise
        self._audit("ACCEPT", "OK", sql)
        return result
