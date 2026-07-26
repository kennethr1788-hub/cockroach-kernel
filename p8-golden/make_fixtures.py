#!/usr/bin/env python3
"""Generate P8 synthetic fixtures in canonical encoding."""
from __future__ import annotations

from pathlib import Path

import golden as g

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"

BASE_POLICY = {
    "version": g.VERSION, "policy_id": "policy-p8-v1",
    "ordinary_quorum": 3, "critical_quorum": 4, "correlation_limit": 4,
}
SAFE_POLICY = dict(BASE_POLICY, policy_id="policy-p8-v2", correlation_limit=3)


def incident(identifier: str, *, critical: bool = False, approvals: int = 0,
             refusals: int = 0, correlated: int = 0, veto: bool = False,
             tampered: bool = False, unsafe: bool = False,
             warrant_state: str | None = "ISSUED",
             expected: tuple[str, str]) -> dict:
    value = {
        "version": g.VERSION, "incident_id": identifier,
        "task_id": "task-p8-synthetic-001", "critical": critical,
        "approvals": approvals, "refusals": refusals,
        "correlated_votes": correlated, "policy_veto": veto,
        "tampered": tampered, "unsafe": unsafe,
        "warrant_state": warrant_state,
        "expected_decision": expected[0], "expected_reason": expected[1],
        "input_hash": "",
    }
    value["input_hash"] = g.sha256_hex(g.incident_input(value))
    return value


INCIDENTS = [
    incident("incident-success-ordinary", approvals=3, refusals=2,
             expected=("PROMOTE", "QUORUM_PASS")),
    incident("incident-success-critical", critical=True, approvals=4, refusals=1,
             expected=("PROMOTE", "QUORUM_PASS")),
    incident("incident-failed-quorum", approvals=2, refusals=3,
             expected=("REFUSE", "QUORUM_MISSING")),
    incident("incident-failed-critical", critical=True, approvals=3, refusals=2,
             expected=("REFUSE", "QUORUM_MISSING")),
    incident("incident-failed-correlated", approvals=4, refusals=1, correlated=4,
             expected=("REFUSE", "CORRELATED_OUTPUTS")),
    incident("incident-failed-veto", approvals=5, veto=True,
             expected=("REFUSE", "POLICY_VETO")),
    incident("incident-failed-tamper", approvals=5, tampered=True,
             expected=("REFUSE", "TAMPERED_EVIDENCE")),
    incident("incident-failed-unsafe", approvals=5, unsafe=True,
             expected=("REFUSE", "POLICY_UNSAFE")),
    incident("incident-failed-replay", approvals=5, warrant_state="CONSUMED",
             expected=("REFUSE", "WARRANT_REPLAY")),
]


def proposal(identifier: str, candidate: dict, base_hash: str | None = None) -> dict:
    return {
        "version": g.VERSION, "proposal_id": identifier,
        "base_policy_hash": base_hash or g.sha256_hex(BASE_POLICY),
        "candidate_policy": candidate,
        "reflection_hash": g.sha256_hex({"incident_set": g.incident_set_hash(INCIDENTS),
                                         "proposal": identifier}),
    }


PROPOSALS = {
    "proposal-safe": proposal("proposal-safe", SAFE_POLICY),
    "proposal-weaken-ordinary": proposal(
        "proposal-weaken-ordinary",
        dict(BASE_POLICY, policy_id="policy-p8-bad-ordinary", ordinary_quorum=2)),
    "proposal-weaken-critical": proposal(
        "proposal-weaken-critical",
        dict(BASE_POLICY, policy_id="policy-p8-bad-critical", critical_quorum=3)),
    "proposal-unsafe-correlation": proposal(
        "proposal-unsafe-correlation",
        dict(BASE_POLICY, policy_id="policy-p8-bad-correlation", correlation_limit=5)),
    "proposal-stale": proposal("proposal-stale", SAFE_POLICY, "0" * 64),
    "proposal-noop": proposal("proposal-noop", dict(BASE_POLICY)),
    "proposal-regression": proposal(
        "proposal-regression",
        dict(BASE_POLICY, policy_id="policy-p8-regression", ordinary_quorum=4)),
}


def write(name: str, value: object) -> None:
    (FIXTURES / f"{name}.json").write_bytes(g.canonical_json(value))


def main() -> None:
    FIXTURES.mkdir(exist_ok=True)
    write("policy-base", BASE_POLICY)
    write("policy-safe", SAFE_POLICY)
    write("incidents", INCIDENTS)
    for name, value in PROPOSALS.items():
        write(name, value)
    safe_result = g.replay_proposal(PROPOSALS["proposal-safe"], BASE_POLICY, INCIDENTS)
    write("replay-safe", safe_result["replay"])
    write("promotion-safe", safe_result["receipt"])
    write("golden-pair-safe", safe_result["golden_pair"])


if __name__ == "__main__":
    main()
