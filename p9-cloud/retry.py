"""Deterministic bounded retry, idempotency, and invocation accounting."""
from __future__ import annotations

from typing import Any, Callable

from records import MAX_MESSAGE_BYTES, canonical_json, require_hash, require_id

MAX_RETRY_ATTEMPTS = 8
MAX_INVOCATIONS = 1000


class RetryError(RuntimeError):
    """Stable fail-closed retry or accounting error."""


class SqlStateError(RuntimeError):
    def __init__(self, sqlstate: str) -> None:
        super().__init__(sqlstate)
        self.sqlstate = sqlstate


def run_serializable(operation: Callable[[int], Any], max_attempts: int = 3) -> tuple[Any, list[dict[str, Any]]]:
    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int):
        raise RetryError("INVALID_ATTEMPT_BOUND")
    if not 1 <= max_attempts <= MAX_RETRY_ATTEMPTS:
        raise RetryError("INVALID_ATTEMPT_BOUND")
    receipts: list[dict[str, Any]] = []
    for attempt in range(1, max_attempts + 1):
        try:
            result = operation(attempt)
        except SqlStateError as exc:
            if exc.sqlstate != "40001":
                raise
            receipts.append({"attempt": attempt, "result": "RETRY", "sqlstate": "40001"})
            if attempt == max_attempts:
                error = RetryError("SERIALIZATION_RETRY_EXHAUSTED")
                error.receipts = tuple(receipts)
                raise error from exc
        else:
            receipts.append({"attempt": attempt, "result": "SUCCESS", "sqlstate": None})
            return result, receipts
    raise RetryError("UNREACHABLE_RETRY_STATE")


class IdempotencyLedger:
    def __init__(self) -> None:
        self._digests: dict[str, str] = {}

    def record(self, record_id: str, digest: str) -> str:
        require_id(record_id)
        require_hash(digest)
        prior = self._digests.get(record_id)
        if prior is None:
            self._digests[record_id] = digest
            return "INSERTED"
        if prior == digest:
            return "DUPLICATE"
        raise RetryError("DUPLICATE_CONFLICT")


class InvocationBudget:
    def __init__(self, cap: int = MAX_INVOCATIONS) -> None:
        if isinstance(cap, bool) or not isinstance(cap, int) or not 1 <= cap <= MAX_INVOCATIONS:
            raise RetryError("INVALID_INVOCATION_CAP")
        self.cap = cap
        self.used = 0
        self.request_bytes = 0
        self.response_bytes = 0

    def consume(self, request: Any, response: Any | None = None) -> None:
        request_size = len(canonical_json(request))
        if request_size > MAX_MESSAGE_BYTES:
            raise RetryError("REQUEST_TOO_LARGE")
        response_size = 0 if response is None else len(canonical_json(response))
        if response_size > MAX_MESSAGE_BYTES:
            raise RetryError("RESPONSE_TOO_LARGE")
        if self.used >= self.cap:
            raise RetryError("INVOCATION_CAP_EXHAUSTED")
        self.used += 1
        self.request_bytes += request_size
        self.response_bytes += response_size
