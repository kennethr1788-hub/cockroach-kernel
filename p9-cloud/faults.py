"""Pure local fault and changefeed models for P9 reliability evidence."""
from __future__ import annotations

import copy
from typing import Any, Callable

from records import canonical_json, require_hash, require_id, sha256_hex
from retry import InvocationBudget


class FaultError(RuntimeError):
    """Stable local fault-model error."""


class ScriptedWorker:
    def __init__(self, evaluator: Callable[[dict[str, Any]], dict[str, Any]], cap: int = 1000) -> None:
        self.evaluator = evaluator
        self.budget = InvocationBudget(cap)

    def invoke(self, request: dict[str, Any], behavior: str = "success", delay_steps: int = 0) -> dict[str, Any]:
        self.budget.consume(request)
        if behavior == "unavailable":
            raise FaultError("WORKER_UNAVAILABLE")
        if behavior not in ("success", "cold_start", "hash_mismatch"):
            raise FaultError("UNKNOWN_WORKER_BEHAVIOR")
        if isinstance(delay_steps, bool) or not isinstance(delay_steps, int) or not 0 <= delay_steps <= 32:
            raise FaultError("INVALID_DELAY_STEPS")
        state = sha256_hex({"request": request, "step": 0})
        for step in range(delay_steps):
            state = sha256_hex({"prior": state, "step": step + 1})
        response = self.evaluator(copy.deepcopy(request))
        if behavior == "hash_mismatch":
            response = copy.deepcopy(response)
            response["response_hash"] = "0" * 64
        self.budget.response_bytes += len(canonical_json(response))
        return response


class ChangefeedProjection:
    FIELDS = {"event_id", "cursor", "source_hash", "receipt_hash", "payload_hash", "projection_hash"}

    def __init__(self, cursor: int = 0, seen: dict[str, str] | None = None) -> None:
        if isinstance(cursor, bool) or not isinstance(cursor, int) or cursor < 0:
            raise FaultError("INVALID_CURSOR")
        self.cursor = cursor
        self.seen = dict(seen or {})
        self.projected: list[dict[str, Any]] = []
        self.write_back_authorized = False

    def snapshot(self) -> dict[str, Any]:
        return {"cursor": self.cursor, "seen": dict(sorted(self.seen.items()))}

    @classmethod
    def restart(cls, snapshot: dict[str, Any]) -> "ChangefeedProjection":
        if not isinstance(snapshot, dict) or set(snapshot) != {"cursor", "seen"}:
            raise FaultError("INVALID_SNAPSHOT")
        return cls(snapshot["cursor"], snapshot["seen"])

    def accept(self, event: dict[str, Any]) -> str:
        if not isinstance(event, dict) or set(event) != self.FIELDS:
            raise FaultError("MALFORMED_PROJECTION")
        require_id(event["event_id"])
        for key in ("source_hash", "receipt_hash", "payload_hash", "projection_hash"):
            require_hash(event[key])
        cursor = event["cursor"]
        if isinstance(cursor, bool) or not isinstance(cursor, int) or cursor < 1:
            raise FaultError("INVALID_CURSOR")
        body = {key: event[key] for key in self.FIELDS if key != "projection_hash"}
        if event["projection_hash"] != sha256_hex(body):
            raise FaultError("PROJECTION_HASH_MISMATCH")
        digest = sha256_hex(event)
        prior = self.seen.get(event["event_id"])
        if prior is not None:
            if prior == digest:
                return "DUPLICATE"
            raise FaultError("PROJECTION_CONFLICT")
        expected = self.cursor + 1
        if cursor > expected:
            raise FaultError("CHANGEFEED_LAG")
        if cursor < expected:
            raise FaultError("STALE_CURSOR")
        self.seen[event["event_id"]] = digest
        self.projected.append(copy.deepcopy(event))
        self.cursor = cursor
        return "PROJECTED"

    def write_back(self, _: Any) -> None:
        raise FaultError("WRITE_BACK_FORBIDDEN")
