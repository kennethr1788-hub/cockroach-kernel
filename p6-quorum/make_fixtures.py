"""Generate deterministic synthetic P6 fixtures into p6-quorum/fixtures/.

All contents are synthetic and non-sensitive. Re-running this script always
produces byte-identical canonical JSON files.
"""
from __future__ import annotations

import os

from state_machine import (
    LANES, VERSION, build_intent, build_receipt, canonical_json, decide,
    make_handoff, make_vote, sha256_hex,
)

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

TASK_ID = "task-p6-synthetic-001"
CANDIDATE_ID = "cand-p6-synthetic-001"
POLICY_VERSION = "policy-v1"

TASK = {"kind": "synthetic-quorum-evaluation", "goal": "evaluate synthetic candidate"}
INPUT_STATE = {"step": 0, "synthetic": True}
TRAJECTORY = [{"sequence": 0, "event": "DECLARE"}, {"sequence": 1, "event": "EVALUATE"}]
POLICY = {"version": POLICY_VERSION, "critical_actions": ["recovery"], "veto": False}
CANDIDATE = {"candidate_id": CANDIDATE_ID, "task_id": TASK_ID, "payload": "synthetic"}

# Per-lane deterministic outputs; lane index 3 and 4 share outputs for the
# correlation fixture only.
LANE_OUTPUTS = {lane: {"lane": lane, "note": "synthetic output %d" % idx}
                for idx, lane in enumerate(LANES)}
CORRELATED_OUTPUT = {"lane": "shared", "note": "identical synthetic output"}


def candidate_hash() -> str:
    return sha256_hex(CANDIDATE)


def build_handoffs() -> tuple[dict, dict, str]:
    first = make_handoff(
        "handoff-001", "THINKER_TO_WORKER", TASK_ID, TASK, INPUT_STATE,
        TRAJECTORY, POLICY_VERSION, POLICY, LANE_OUTPUTS, CANDIDATE_ID, CANDIDATE,
    )
    parent_receipt_hash = sha256_hex({"stage": "THINKER", "handoff": sha256_hex(first)})
    second = make_handoff(
        "handoff-002", "WORKER_TO_VERIFIER", TASK_ID, TASK, INPUT_STATE,
        TRAJECTORY, POLICY_VERSION, POLICY, LANE_OUTPUTS, CANDIDATE_ID, CANDIDATE,
        parent_handoff=first, parent_receipt_hash=parent_receipt_hash,
    )
    return first, second, parent_receipt_hash


def vote_set(name: str) -> list[dict]:
    """Deterministic synthetic vote sets, one per named authority vector."""
    ch = candidate_hash()

    def vote(idx: int, decision: str, status: str = "OK", output=None) -> dict:
        lane = LANES[idx]
        return make_vote("vote-%s-%d" % (name, idx), lane, TASK_ID, CANDIDATE_ID,
                         ch, decision, output if output is not None else LANE_OUTPUTS[lane],
                         status=status, rationale="synthetic rationale %s %d" % (name, idx))

    sets = {
        "ordinary-approval": [vote(0, "APPROVE"), vote(1, "APPROVE"), vote(2, "APPROVE"),
                              vote(3, "REFUSE"), vote(4, "REFUSE")],
        "critical-approval": [vote(i, "APPROVE") for i in range(4)] + [vote(4, "REFUSE")],
        "critical-three": [vote(i, "APPROVE") for i in range(3)] + [vote(3, "REFUSE"), vote(4, "REFUSE")],
        "correlated-four": [vote(i, "APPROVE", output=CORRELATED_OUTPUT) for i in range(4)]
                           + [vote(4, "REFUSE")],
        "unanimous-veto": [vote(i, "APPROVE") for i in range(5)],
        "split": [vote(0, "APPROVE"), vote(1, "APPROVE"), vote(2, "REFUSE"),
                  vote(3, "REFUSE"), vote(4, "REFUSE")],
        "tie": [vote(0, "APPROVE"), vote(1, "APPROVE"), vote(2, "REFUSE"),
                vote(3, "REFUSE"), vote(4, "ABSTAIN")],
        "timeout": [vote(0, "APPROVE"), vote(1, "APPROVE"), vote(2, "APPROVE"),
                    vote(3, "APPROVE"), vote(4, "ABSTAIN", status="TIMEOUT")],
        "failed-lane": [vote(0, "APPROVE"), vote(1, "APPROVE"), vote(2, "APPROVE"),
                        vote(3, "APPROVE"), vote(4, "ABSTAIN", status="FAILED")],
        "missing-quorum": [vote(0, "APPROVE"), vote(1, "APPROVE"), vote(2, "ABSTAIN"),
                           vote(3, "ABSTAIN"), vote(4, "ABSTAIN")],
        "duplicate-vote": [vote(0, "APPROVE"), vote(0, "APPROVE"), vote(1, "APPROVE"),
                           vote(2, "APPROVE"), vote(3, "APPROVE")],
    }
    return sets[name]


def write_fixture(name: str, value) -> None:
    path = os.path.join(FIXTURE_DIR, name + ".json")
    with open(path, "wb") as handle:
        handle.write(canonical_json(value))


def main() -> None:
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    first, second, parent_receipt_hash = build_handoffs()
    write_fixture("handoff-thinker-to-worker", first)
    write_fixture("handoff-worker-to-verifier", second)
    write_fixture("parent-receipt", {"version": VERSION, "receipt_hash": parent_receipt_hash})

    decisions = {}
    for name in ("ordinary-approval", "critical-approval", "critical-three",
                 "correlated-four", "unanimous-veto", "split", "tie", "timeout",
                 "failed-lane", "missing-quorum", "duplicate-vote"):
        votes = vote_set(name)
        write_fixture("votes-" + name, votes)
        record = decide(votes, TASK_ID, CANDIDATE_ID, candidate_hash(),
                        critical=name in ("critical-approval", "critical-three"),
                        policy_veto=name == "unanimous-veto")
        decisions[name] = record
    write_fixture("decisions", decisions)

    intent = build_intent("intent-ordinary-001", decisions["ordinary-approval"])
    write_fixture("intent-ordinary-approval", intent)
    write_fixture("receipt-ordinary-approval", build_receipt(intent))
    print("wrote %d fixtures to %s" % (len(os.listdir(FIXTURE_DIR)), FIXTURE_DIR))


if __name__ == "__main__":
    main()
