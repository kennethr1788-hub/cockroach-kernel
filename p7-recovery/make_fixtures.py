"""Generate deterministic synthetic P7 fixtures into p7-recovery/fixtures/.

All contents are synthetic and non-sensitive. Re-running this script always
produces byte-identical canonical JSON files.
"""
from __future__ import annotations

import copy
import os

import records as rc

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

TASK_ID = "task-p7-synthetic-001"
POLICY_VERSION = "policy-v1"
ALPHA_ID = "cand-p7-alpha"
BETA_ID = "cand-p7-beta"

# Synthetic declared workspace contents (never written to disk).
FILE_CONTENTS = {
    "data/state.json": b'{"synthetic":"state"}',
    "docs/notes.md": b"# synthetic notes\n",
    "src/feature.py": b"# synthetic feature\n",
}


def build_manifest() -> dict:
    return {
        "version": rc.VERSION,
        "manifest_id": "manifest-p7-001",
        "task_id": TASK_ID,
        "files": [
            {"path": path, "content_hash": rc.sha256_hex(content),
             "executable": False, "is_symlink": False}
            for path, content in sorted(FILE_CONTENTS.items())
        ],
    }


def build_events() -> list[dict]:
    names = ["DECLARE", "RECORD", "EVALUATE"]
    return [
        {"sequence": index, "event": name,
         "event_hash": rc.sha256_hex({"sequence": index, "event": name})}
        for index, name in enumerate(names)
    ]


def build_trajectory_receipt(manifest: dict, events: list[dict]) -> dict:
    previous = ""
    for event in events:
        previous = rc.sha256_hex({"previous": previous, "event": event})
    return {
        "version": rc.VERSION,
        "receipt_id": "rcpt-trajectory-p7-001",
        "task_id": TASK_ID,
        "manifest_hash": rc.sha256_hex(manifest),
        "events": events,
        "trajectory_hash": previous,
    }


def build_loss_receipt(manifest: dict) -> dict:
    lost = rc.declared_paths(manifest)
    return {
        "version": rc.VERSION,
        "receipt_id": "rcpt-loss-p7-001",
        "task_id": TASK_ID,
        "manifest_hash": rc.sha256_hex(manifest),
        "lost_paths": lost,
        "absence_hash": rc.sha256_hex({"lost_paths": sorted(lost),
                                       "observed": "absent"}),
    }


def build_quorum_decision() -> dict:
    """Synthetic P6-style quorum decision record (PROMOTE, 3 of 5 lanes)."""
    votes_hash = rc.sha256_hex([rc.sha256_hex("vote-%d" % idx) for idx in range(5)])
    return {
        "version": "p6-v1",
        "task_id": TASK_ID,
        "candidate_id": "cand-p6-synthetic-001",
        "critical": False,
        "threshold": 3,
        "approvals": 3,
        "refusals": 2,
        "decision": "PROMOTE",
        "reason": "QUORUM_PASS",
        "dissent": [],
        "votes_hash": votes_hash,
    }


def build_candidate(candidate_id: str, prefix_length: int,
                    declared: list[str], events: list[dict],
                    trajectory: dict, quorum: dict) -> dict:
    file_hashes = {path: rc.sha256_hex(FILE_CONTENTS[path]) for path in declared}
    candidate = {
        "version": rc.VERSION,
        "candidate_id": candidate_id,
        "task_id": TASK_ID,
        "provenance": {"source": "p6-quorum-synthetic", "builder": "kimi"},
        "source_receipt_hash": rc.sha256_hex(trajectory),
        "policy_version": POLICY_VERSION,
        "policy_veto": False,
        "tampered": False,
        "quorum_decision": quorum,
        "prefix_length": prefix_length,
        "integrity_hash": rc.trajectory_integrity_hash(events, prefix_length),
        "declared_paths": declared,
        "file_hashes": file_hashes,
        "executable_test": {
            "test_id": "exectest-" + candidate_id,
            "path": "src/feature.py",
            "feature_hash": file_hashes["src/feature.py"],
            "passed": True,
        },
    }
    rc.validate_candidate(candidate)
    return candidate


def refusal_candidates(alpha: dict) -> dict[str, dict]:
    """One fixture candidate per refusal vector, each drifting exactly one binding."""
    variants = {}

    vetoed = copy.deepcopy(alpha)
    vetoed["candidate_id"] = "cand-p7-veto"
    vetoed["policy_veto"] = True
    variants["policy-veto"] = vetoed

    tampered = copy.deepcopy(alpha)
    tampered["candidate_id"] = "cand-p7-tampered"
    tampered["tampered"] = True
    variants["tampered"] = tampered

    bad_schema = copy.deepcopy(alpha)
    bad_schema["candidate_id"] = "cand-p7-badschema"
    bad_schema["version"] = "p7-v0"
    variants["unsupported-schema"] = bad_schema

    stale = copy.deepcopy(alpha)
    stale["candidate_id"] = "cand-p7-stalepolicy"
    stale["policy_version"] = "policy-v0"
    variants["stale-policy"] = stale

    no_quorum = copy.deepcopy(alpha)
    no_quorum["candidate_id"] = "cand-p7-noquorum"
    no_quorum["quorum_decision"] = dict(no_quorum["quorum_decision"],
                                        decision="REFUSE", reason="QUORUM_MISSING")
    variants["missing-quorum"] = no_quorum

    failed_test = copy.deepcopy(alpha)
    failed_test["candidate_id"] = "cand-p7-failedtest"
    failed_test["executable_test"] = dict(failed_test["executable_test"],
                                          passed=False)
    variants["failed-exec-test"] = failed_test

    unsafe = copy.deepcopy(alpha)
    unsafe["candidate_id"] = "cand-p7-unsafepath"
    unsafe["declared_paths"] = list(unsafe["declared_paths"]) + ["secret/undeclared.txt"]
    unsafe["file_hashes"]["secret/undeclared.txt"] = rc.sha256_hex(
        b"synthetic undeclared bytes")
    variants["unsafe-path"] = unsafe

    return variants


def write_fixture(name: str, value) -> None:
    path = os.path.join(FIXTURE_DIR, name + ".json")
    with open(path, "wb") as handle:
        handle.write(rc.canonical_json(value))


def build_context(manifest: dict, trajectory: dict, quorum: dict) -> dict:
    return {
        "manifest": manifest,
        "trajectory_receipt": trajectory,
        "policy_version": POLICY_VERSION,
        "quorum_decision_hash": rc.sha256_hex(quorum),
    }


def main() -> None:
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    manifest = build_manifest()
    events = build_events()
    trajectory = build_trajectory_receipt(manifest, events)
    loss = build_loss_receipt(manifest)
    quorum = build_quorum_decision()
    context = build_context(manifest, trajectory, quorum)

    alpha = build_candidate(ALPHA_ID, 3, ["docs/notes.md", "src/feature.py"],
                            events, trajectory, quorum)
    beta = build_candidate(BETA_ID, 2, ["src/feature.py"],
                           events, trajectory, quorum)

    write_fixture("manifest", manifest)
    write_fixture("trajectory-receipt", trajectory)
    write_fixture("loss-receipt", loss)
    write_fixture("quorum-decision", quorum)
    write_fixture("candidate-alpha", alpha)
    write_fixture("candidate-beta", beta)
    for name, candidate in refusal_candidates(alpha).items():
        write_fixture("candidate-" + name, candidate)

    decision_promote = rc.select_candidate([alpha, beta], context)
    write_fixture("decision-promote", decision_promote)

    refusing = list(refusal_candidates(alpha).values())
    decision_refuse = rc.select_candidate(refusing, context)
    write_fixture("decision-no-surviving", decision_refuse)

    warrant = rc.make_warrant("warrant-p7-001", TASK_ID, ALPHA_ID, decision_promote)
    write_fixture("warrant-issued", warrant)

    harness = rc.RecoveryHarness()
    harness.register_warrant(warrant)
    promotion = harness.recover(decision_promote, "warrant-p7-001",
                                promoted_paths=alpha["declared_paths"])
    write_fixture("promotion-receipt", promotion)
    write_fixture("refusal-receipt-no-surviving", rc.build_refusal_receipt(decision_refuse))

    ledger = rc.make_unrecovered_ledger("ledger-p7-001", manifest,
                                        alpha["declared_paths"])
    write_fixture("unrecovered-ledger", ledger)
    write_fixture("feature-file", {
        "path": "src/feature.py",
        "content_hash": rc.sha256_hex(FILE_CONTENTS["src/feature.py"]),
    })

    print("wrote %d fixtures to %s" % (len(os.listdir(FIXTURE_DIR)), FIXTURE_DIR))


if __name__ == "__main__":
    main()
