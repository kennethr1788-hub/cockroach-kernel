"""P6 typed Thinker -> Worker -> Verifier quorum state machine.

Synthetic, deterministic, standard library only. Model and persona outputs are
untrusted evidence: free-text rationale is scanned for forbidden requests and
is never read by the authority decision function. Authority derives only from
structured, hash-bound fields.

Scope of this layer: typed handoffs, strict validation, the pure quorum
decision function, and a transition intent plus an in-memory atomic-commit
harness whose record shape is suitable for a retry-safe CockroachDB
serializable transaction. No remote or cloud access is implemented here.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

VERSION = "p6-v1"
MAX_RECORD_BYTES = 65536  # 64 KiB cap on every canonical record

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

LANES = (
    "syntax_structure",
    "security_policy",
    "logic_coherence",
    "contextual_fit",
    "trajectory_alignment",
)

STAGES = ("THINKER_TO_WORKER", "WORKER_TO_VERIFIER")
VOTE_STATUSES = ("OK", "TIMEOUT", "FAILED")
VOTE_DECISIONS = ("APPROVE", "REFUSE", "ABSTAIN")
DECISIONS = ("PROMOTE", "REFUSE", "INVALID")

ORDINARY_QUORUM = 3
CRITICAL_QUORUM = 4
LANE_COUNT = 5
CORRELATION_LIMIT = 4  # four or more equal output hashes refuse

HANDOFF_FIELDS = {
    "version", "handoff_id", "stage", "task_id", "task_hash",
    "input_state_hash", "trajectory_hash", "policy_version", "policy_hash",
    "lane_outputs_hash", "candidate_id", "candidate_hash", "schema_hash",
    "parent_handoff_hash", "parent_receipt_hash",
}
VOTE_FIELDS = {
    "version", "vote_id", "lane", "task_id", "candidate_id", "candidate_hash",
    "status", "decision", "output_hash", "rationale",
}
DECISION_RECORD_FIELDS = {
    "version", "task_id", "candidate_id", "critical", "threshold",
    "approvals", "refusals", "decision", "reason", "dissent", "votes_hash",
}
INTENT_FIELDS = {"version", "intent_id", "decision_record", "decision_hash"}
RECEIPT_FIELDS = {"version", "receipt_id", "intent_id", "decision_record", "receipt_hash"}

FORBIDDEN_KEYS = {
    "tool", "tools", "tool_call", "tool_request", "authority", "promote",
    "promotion", "escalate", "delegate", "call_agent", "policy_change",
    "execute", "shell", "command",
}
INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore all previous",
    "disregard all previous",
    "disregard previous",
    "you are now",
    "system prompt",
)


class QuorumError(ValueError):
    """Raised on any closed-failure validation or store fault."""


# ---------------------------------------------------------------------------
# Canonical primitives
# ---------------------------------------------------------------------------

def canonical_json(value: Any) -> bytes:
    """Canonical UTF-8 JSON: sorted keys, no whitespace, 64 KiB cap."""
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise QuorumError("MALFORMED_RECORD") from exc
    if len(encoded) > MAX_RECORD_BYTES:
        raise QuorumError("RECORD_TOO_LARGE")
    return encoded


def sha256_hex(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value)
    return hashlib.sha256(raw).hexdigest()


def require_id(value: Any) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise QuorumError("INVALID_ID")
    return value


def require_hash(value: Any) -> str:
    if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
        raise QuorumError("INVALID_HASH")
    return value


def validate_object(record: Any, fields: set[str]) -> None:
    if not isinstance(record, dict):
        raise QuorumError("MALFORMED_RECORD")
    if set(record) - fields:
        raise QuorumError("UNKNOWN_FIELD")
    if fields - set(record):
        raise QuorumError("MISSING_FIELD")


def contains_forbidden_request(value: Any) -> bool:
    """Detect tool/authority/injection requests in nested untrusted content."""
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str) and key.lower() in FORBIDDEN_KEYS:
                return True
            if contains_forbidden_request(item):
                return True
        return False
    if isinstance(value, list):
        return any(contains_forbidden_request(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return any(marker in lowered for marker in INJECTION_MARKERS)
    return False


def load_canonical(path: str) -> Any:
    """Load a JSON record that must be stored in exact canonical form."""
    with open(path, "rb") as handle:
        raw = handle.read()
    if len(raw) > MAX_RECORD_BYTES:
        raise QuorumError("RECORD_TOO_LARGE")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise QuorumError("MALFORMED_RECORD") from exc
    if canonical_json(value) != raw:
        raise QuorumError("NON_CANONICAL_ENCODING")
    return value


def schema_hash() -> str:
    """Stable hash of the record schemas this implementation enforces."""
    descriptor = {
        "version": VERSION,
        "stages": list(STAGES),
        "lanes": list(LANES),
        "handoff_fields": sorted(HANDOFF_FIELDS),
        "vote_fields": sorted(VOTE_FIELDS),
        "vote_statuses": list(VOTE_STATUSES),
        "vote_decisions": list(VOTE_DECISIONS),
        "ordinary_quorum": ORDINARY_QUORUM,
        "critical_quorum": CRITICAL_QUORUM,
        "correlation_limit": CORRELATION_LIMIT,
    }
    return sha256_hex(descriptor)


# ---------------------------------------------------------------------------
# Typed handoffs
# ---------------------------------------------------------------------------

def make_handoff(
    handoff_id: str,
    stage: str,
    task_id: str,
    task: Any,
    input_state: Any,
    trajectory: Any,
    policy_version: str,
    policy: Any,
    lane_outputs: Any,
    candidate_id: str,
    candidate: Any,
    parent_handoff: dict[str, Any] | None = None,
    parent_receipt_hash: str | None = None,
) -> dict[str, Any]:
    """Build a fully hash-bound handoff record from its bound contents."""
    handoff = {
        "version": VERSION,
        "handoff_id": handoff_id,
        "stage": stage,
        "task_id": task_id,
        "task_hash": sha256_hex(task),
        "input_state_hash": sha256_hex(input_state),
        "trajectory_hash": sha256_hex(trajectory),
        "policy_version": policy_version,
        "policy_hash": sha256_hex(policy),
        "lane_outputs_hash": sha256_hex(lane_outputs),
        "candidate_id": candidate_id,
        "candidate_hash": sha256_hex(candidate),
        "schema_hash": schema_hash(),
        "parent_handoff_hash": sha256_hex(parent_handoff) if parent_handoff else None,
        "parent_receipt_hash": parent_receipt_hash,
    }
    validate_handoff(handoff)
    canonical_json(handoff)
    return handoff


def validate_handoff(handoff: Any) -> None:
    validate_object(handoff, HANDOFF_FIELDS)
    if handoff["version"] != VERSION:
        raise QuorumError("UNSUPPORTED_SCHEMA")
    require_id(handoff["handoff_id"])
    require_id(handoff["task_id"])
    require_id(handoff["candidate_id"])
    if handoff["stage"] not in STAGES:
        raise QuorumError("UNKNOWN_STAGE")
    if not isinstance(handoff["policy_version"], str) or not handoff["policy_version"]:
        raise QuorumError("MISSING_FIELD")
    for key in ("task_hash", "input_state_hash", "trajectory_hash", "policy_hash",
                "lane_outputs_hash", "candidate_hash", "schema_hash"):
        require_hash(handoff[key])
    if handoff["schema_hash"] != schema_hash():
        raise QuorumError("UNSUPPORTED_SCHEMA")
    for key in ("parent_handoff_hash", "parent_receipt_hash"):
        if handoff[key] is not None:
            require_hash(handoff[key])
    if handoff["stage"] == "THINKER_TO_WORKER":
        if handoff["parent_handoff_hash"] is not None or handoff["parent_receipt_hash"] is not None:
            raise QuorumError("STALE_HANDOFF")
    else:
        if handoff["parent_handoff_hash"] is None or handoff["parent_receipt_hash"] is None:
            raise QuorumError("MISSING_FIELD")


def verify_handoff_link(handoff: dict[str, Any],
                        parent_handoff: dict[str, Any],
                        parent_receipt_hash: str) -> None:
    """Bind a WORKER_TO_VERIFIER handoff to its exact parent handoff + receipt."""
    validate_handoff(handoff)
    validate_handoff(parent_handoff)
    require_hash(parent_receipt_hash)
    if handoff["stage"] != "WORKER_TO_VERIFIER":
        raise QuorumError("UNKNOWN_STAGE")
    if handoff["parent_handoff_hash"] != sha256_hex(parent_handoff):
        raise QuorumError("STALE_HANDOFF")
    if handoff["parent_receipt_hash"] != parent_receipt_hash:
        raise QuorumError("STALE_HANDOFF")
    for key in ("task_id", "task_hash", "input_state_hash", "trajectory_hash",
                "policy_version", "policy_hash", "candidate_id", "candidate_hash"):
        if handoff[key] != parent_handoff[key]:
            raise QuorumError("STALE_HANDOFF")


# ---------------------------------------------------------------------------
# Evaluator votes (untrusted evidence)
# ---------------------------------------------------------------------------

def make_vote(vote_id: str, lane: str, task_id: str, candidate_id: str,
              candidate_hash: str, decision: str, output: Any,
              status: str = "OK", rationale: str = "") -> dict[str, Any]:
    vote = {
        "version": VERSION,
        "vote_id": vote_id,
        "lane": lane,
        "task_id": task_id,
        "candidate_id": candidate_id,
        "candidate_hash": candidate_hash,
        "status": status,
        "decision": decision,
        "output_hash": sha256_hex(output),
        "rationale": rationale,
    }
    validate_vote(vote)
    canonical_json(vote)
    return vote


def validate_vote(vote: Any) -> None:
    validate_object(vote, VOTE_FIELDS)
    if vote["version"] != VERSION:
        raise QuorumError("UNSUPPORTED_SCHEMA")
    require_id(vote["vote_id"])
    require_id(vote["task_id"])
    require_id(vote["candidate_id"])
    require_hash(vote["candidate_hash"])
    require_hash(vote["output_hash"])
    if vote["lane"] not in LANES:
        raise QuorumError("UNKNOWN_LANE")
    if vote["status"] not in VOTE_STATUSES:
        raise QuorumError("MALFORMED_RECORD")
    if vote["decision"] not in VOTE_DECISIONS:
        raise QuorumError("MALFORMED_RECORD")
    if not isinstance(vote["rationale"], str):
        raise QuorumError("MALFORMED_RECORD")
    if contains_forbidden_request(vote["rationale"]):
        raise QuorumError("FORBIDDEN_REQUEST")


# ---------------------------------------------------------------------------
# Pure authority decision function
# ---------------------------------------------------------------------------

def quorum_threshold(critical: bool) -> int:
    """Critical actions always require four; never downgraded to ordinary."""
    return CRITICAL_QUORUM if critical else ORDINARY_QUORUM


def decide(votes: Any, task_id: str, candidate_id: str, candidate_hash: str,
           critical: bool = False, policy_veto: bool = False) -> dict[str, Any]:
    """Pure authority decision: no time, randomness, model text, or network.

    Model/persona rationale text is never consulted; only structured fields
    decide. Returns a deterministic decision record with a stable reason.
    """
    def record(decision: str, reason: str, approvals: int, refusals: int,
               dissent: list[dict[str, str]], votes_hash: str) -> dict[str, Any]:
        return {
            "version": VERSION,
            "task_id": task_id,
            "candidate_id": candidate_id,
            "critical": bool(critical),
            "threshold": quorum_threshold(bool(critical)),
            "approvals": approvals,
            "refusals": refusals,
            "decision": decision,
            "reason": reason,
            "dissent": dissent,
            "votes_hash": votes_hash,
        }

    empty_hash = sha256_hex([])
    if not isinstance(critical, bool) or not isinstance(policy_veto, bool):
        return record("INVALID", "MALFORMED_RECORD", 0, 0, [], empty_hash)
    if not isinstance(votes, list):
        return record("INVALID", "MALFORMED_RECORD", 0, 0, [], empty_hash)
    try:
        require_id(task_id)
        require_id(candidate_id)
        require_hash(candidate_hash)
    except QuorumError as exc:
        return record("INVALID", str(exc), 0, 0, [], empty_hash)

    seen_lanes: set[str] = set()
    valid: list[dict[str, Any]] = []
    for vote in votes:
        try:
            validate_vote(vote)
            canonical_json(vote)  # enforce the 64 KiB record cap
        except QuorumError as exc:
            return record("REFUSE", str(exc), 0, 0, [], empty_hash)
        if vote["lane"] in seen_lanes:
            return record("REFUSE", "DUPLICATE_VOTE", 0, 0, [], empty_hash)
        seen_lanes.add(vote["lane"])
        if (vote["task_id"] != task_id or vote["candidate_id"] != candidate_id
                or vote["candidate_hash"] != candidate_hash):
            return record("REFUSE", "STALE_HANDOFF", 0, 0, [], empty_hash)
        valid.append(vote)

    votes_hash = sha256_hex([sha256_hex(vote) for vote in
                             sorted(valid, key=lambda v: LANES.index(v["lane"]))])

    # Dissent: every non-approving or non-OK lane, retained in fixed lane order.
    dissent = [
        {"lane": vote["lane"], "vote_id": vote["vote_id"],
         "status": vote["status"], "decision": vote["decision"]}
        for vote in sorted(valid, key=lambda v: LANES.index(v["lane"]))
        if vote["status"] != "OK" or vote["decision"] != "APPROVE"
    ]

    approvals = sum(1 for v in valid if v["status"] == "OK" and v["decision"] == "APPROVE")
    refusals = sum(1 for v in valid if v["status"] == "OK" and v["decision"] == "REFUSE")

    # Explicit policy veto overrides any model consensus, including unanimous.
    if policy_veto:
        return record("REFUSE", "POLICY_VETO", approvals, refusals, dissent, votes_hash)
    # Timeout and failed lanes never approve and poison the evaluation.
    if any(v["status"] == "TIMEOUT" for v in valid):
        return record("REFUSE", "LANE_TIMEOUT", approvals, refusals, dissent, votes_hash)
    if any(v["status"] == "FAILED" for v in valid):
        return record("REFUSE", "LANE_FAILED", approvals, refusals, dissent, votes_hash)
    # Four or more materially correlated approving output hashes refuse.
    output_counts: dict[str, int] = {}
    for vote in valid:
        if vote["status"] == "OK" and vote["decision"] == "APPROVE":
            output_counts[vote["output_hash"]] = output_counts.get(vote["output_hash"], 0) + 1
    if output_counts and max(output_counts.values()) >= CORRELATION_LIMIT:
        return record("REFUSE", "CORRELATED_OUTPUTS", approvals, refusals, dissent, votes_hash)

    threshold = quorum_threshold(bool(critical))
    if approvals >= threshold:
        return record("PROMOTE", "QUORUM_PASS", approvals, refusals, dissent, votes_hash)
    # Three approvals can never silently satisfy a critical action.
    if critical and approvals >= ORDINARY_QUORUM:
        return record("REFUSE", "CRITICAL_QUORUM_MISSING", approvals, refusals, dissent, votes_hash)
    if approvals and approvals == refusals:
        return record("REFUSE", "TIE_VOTE", approvals, refusals, dissent, votes_hash)
    if refusals:
        return record("REFUSE", "SPLIT_VOTE", approvals, refusals, dissent, votes_hash)
    return record("REFUSE", "QUORUM_MISSING", approvals, refusals, dissent, votes_hash)


# ---------------------------------------------------------------------------
# Transition intent + in-memory atomic commit harness
# ---------------------------------------------------------------------------

def build_intent(intent_id: str, decision_record: dict[str, Any]) -> dict[str, Any]:
    """Transition intent binding the authoritative decision for one atomic commit."""
    validate_object(decision_record, DECISION_RECORD_FIELDS)
    intent = {
        "version": VERSION,
        "intent_id": require_id(intent_id),
        "decision_record": decision_record,
        "decision_hash": sha256_hex(decision_record),
    }
    canonical_json(intent)
    return intent


def validate_intent(intent: Any) -> None:
    validate_object(intent, INTENT_FIELDS)
    if intent["version"] != VERSION:
        raise QuorumError("UNSUPPORTED_SCHEMA")
    require_id(intent["intent_id"])
    require_hash(intent["decision_hash"])
    decision = intent["decision_record"]
    validate_object(decision, DECISION_RECORD_FIELDS)
    require_id(decision["task_id"])
    require_id(decision["candidate_id"])
    if not isinstance(decision["critical"], bool):
        raise QuorumError("MALFORMED_RECORD")
    for key in ("threshold", "approvals", "refusals"):
        if isinstance(decision[key], bool) or not isinstance(decision[key], int):
            raise QuorumError("MALFORMED_RECORD")
        if decision[key] < 0:
            raise QuorumError("MALFORMED_RECORD")
    if decision["threshold"] != quorum_threshold(decision["critical"]):
        raise QuorumError("MALFORMED_RECORD")
    if decision["approvals"] > LANE_COUNT or decision["refusals"] > LANE_COUNT:
        raise QuorumError("MALFORMED_RECORD")
    if decision["decision"] not in DECISIONS:
        raise QuorumError("MALFORMED_RECORD")
    if not isinstance(decision["reason"], str) or not decision["reason"]:
        raise QuorumError("MALFORMED_RECORD")
    if not isinstance(decision["dissent"], list):
        raise QuorumError("MALFORMED_RECORD")
    require_hash(decision["votes_hash"])
    if sha256_hex(decision) != intent["decision_hash"]:
        raise QuorumError("STALE_HASH")


def build_receipt(intent: dict[str, Any]) -> dict[str, Any]:
    """Immutable receipt committed atomically with the transition."""
    validate_intent(intent)
    body = {
        "version": VERSION,
        "intent_id": intent["intent_id"],
        "decision_record": intent["decision_record"],
    }
    receipt_hash = sha256_hex(body)
    receipt = dict(body)
    receipt["receipt_id"] = "rcpt-" + receipt_hash[:32]
    receipt["receipt_hash"] = receipt_hash
    validate_object(receipt, RECEIPT_FIELDS)
    canonical_json(receipt)
    return receipt


class CommitInterrupted(QuorumError):
    """Simulated crash between staging and commit; nothing is applied."""


class CommitRolledBack(QuorumError):
    """Simulated explicit rollback; nothing is applied."""


class TransitionStore:
    """In-memory stand-in for the atomic serializable commit.

    The transition and its immutable receipt commit atomically. Applying the
    same intent_id again is a retry-safe no-op returning the original receipt.
    This models the CockroachDB serializable transaction contract without any
    remote or cloud access.
    """

    def __init__(self) -> None:
        self._transitions: dict[str, dict[str, Any]] = {}
        self._receipts: dict[str, dict[str, Any]] = {}
        self._vote_ids: set[str] = set()

    def submit_vote(self, vote: dict[str, Any]) -> None:
        """Record an evaluator vote once; resubmission is replay."""
        validate_vote(vote)
        if vote["vote_id"] in self._vote_ids:
            raise QuorumError("REPLAY")
        self._vote_ids.add(vote["vote_id"])

    def has_vote(self, vote_id: str) -> bool:
        return vote_id in self._vote_ids

    def transition(self, task_id: str) -> dict[str, Any] | None:
        return self._transitions.get(task_id)

    def receipt(self, intent_id: str) -> dict[str, Any] | None:
        return self._receipts.get(intent_id)

    def apply_intent(self, intent: dict[str, Any], fault: str | None = None) -> dict[str, Any]:
        """Atomically commit transition + receipt, retry-safe by intent_id.

        fault="interrupt" simulates a crash after staging, before commit;
        fault="rollback" simulates an explicit transaction rollback. Either
        leaves the store untouched, so a later retry commits exactly once.
        """
        validate_intent(intent)
        existing = self._receipts.get(intent["intent_id"])
        if existing is not None:
            return existing  # retry-safe idempotent replay of a committed intent
        receipt = build_receipt(intent)
        record = intent["decision_record"]
        if record["task_id"] in self._transitions:
            raise QuorumError("TRANSITION_CONFLICT")
        staged_transition = {
            "task_id": record["task_id"],
            "candidate_id": record["candidate_id"],
            "decision": record["decision"],
            "reason": record["reason"],
            "receipt_hash": receipt["receipt_hash"],
        }
        if fault == "interrupt":
            raise CommitInterrupted("COMMIT_INTERRUPTED")
        if fault == "rollback":
            raise CommitRolledBack("COMMIT_ROLLED_BACK")
        if fault is not None:
            raise QuorumError("UNKNOWN_FAULT")
        # Atomic commit point: transition and receipt become visible together.
        self._transitions[record["task_id"]] = staged_transition
        self._receipts[intent["intent_id"]] = receipt
        return receipt
