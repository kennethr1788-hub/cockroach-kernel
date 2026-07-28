#!/usr/bin/env python3
"""Execute one Gate 7 vector in a fresh process and emit one canonical receipt."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


BASE = Path(__file__).resolve().parents[1]
VERIFIER_PATH = BASE / "p4-verifier" / "verifier.py"
RECOVERY_PATH = BASE / "p7-recovery" / "records.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("MODULE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


verifier = load_module("gate7_verifier", VERIFIER_PATH)
recovery = load_module("gate7_recovery", RECOVERY_PATH)


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: bytes | Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def load_canonical(path: Path) -> Any:
    raw = path.read_bytes()
    value = json.loads(raw)
    if canonical(value) != raw:
        raise ValueError("NON_CANONICAL_INPUT")
    return value


def validate_vector(vector: Any) -> None:
    required = {
        "version", "class", "variant", "seed_hash", "input",
        "expected_verdict", "expected_reason", "mutation_allowed",
        "vector_hash",
    }
    if not isinstance(vector, dict) or set(vector) != required:
        raise ValueError("VECTOR_SCHEMA_INVALID")
    body = {key: value for key, value in vector.items() if key != "vector_hash"}
    if vector["vector_hash"] != digest(body):
        raise ValueError("VECTOR_HASH_MISMATCH")
    if vector["mutation_allowed"] is not False:
        raise ValueError("VECTOR_MUTATION_AUTHORITY_INVALID")
    if vector["expected_verdict"] not in {"PROMOTE", "REFUSE", "INVALID"}:
        raise ValueError("EXPECTED_VERDICT_INVALID")


def interrupted_result(vector: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    seed = vector["seed_hash"]
    task_id = f"g7-task-{seed[:16]}"
    candidate_id = f"g7-cand-{seed[16:32]}"
    warrant_id = f"g7-warrant-{seed[32:48]}"
    decision = recovery.make_decision(
        task_id, "PROMOTE", recovery.MAX_PROVEN_PREFIX, candidate_id, []
    )
    warrant = recovery.make_warrant(warrant_id, task_id, candidate_id, decision)
    harness = recovery.RecoveryHarness()
    harness.register_warrant(warrant)
    interrupted = False
    try:
        harness.recover(decision, warrant_id, fault="interrupt")
    except recovery.RecoveryInterrupted:
        interrupted = True
    replay = harness.recover(decision, warrant_id)
    state = harness.warrant_state(warrant_id)
    no_promotion = harness.promotion(task_id) is None
    replay_reason = replay.get("reason")
    passed = (
        interrupted and state == "CONSUMED" and no_promotion and
        replay_reason == recovery.WARRANT_REPLAY
    )
    observed = (
        ("REFUSE", "RECOVERY_INTERRUPTED_FAIL_CLOSED")
        if passed else ("INVALID", "INTERRUPTION_INVARIANT_FAILED")
    )
    return observed[0], observed[1], {
        "interruption_observed": interrupted,
        "warrant_state": state,
        "promotion_recorded": not no_promotion,
        "replay_reason": replay_reason,
    }


def execute(vector: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    if vector["class"] == "interrupted-consumption":
        return interrupted_result(vector)
    verdict, reason = verifier.verify(vector["input"])
    return verdict, reason, {"p4_verifier": True}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector", type=Path, required=True)
    parser.add_argument("--candidate-commit", required=True)
    parser.add_argument("--execution-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    vector = load_canonical(args.vector)
    validate_vector(vector)
    verdict, reason, details = execute(vector)
    body = {
        "version": "hardening-gate7-trial-receipt-v1",
        "candidate_commit": args.candidate_commit,
        "execution_id": args.execution_id,
        "vector_hash": vector["vector_hash"],
        "vector_class": vector["class"],
        "variant": vector["variant"],
        "expected_verdict": vector["expected_verdict"],
        "expected_reason": vector["expected_reason"],
        "observed_verdict": verdict,
        "observed_reason": reason,
        "mutation_performed": False,
        "details": details,
        "passed": (
            verdict == vector["expected_verdict"] and
            reason == vector["expected_reason"]
        ),
    }
    receipt = dict(body)
    receipt["receipt_hash"] = digest(body)
    args.output.write_bytes(canonical(receipt))
    return 0 if receipt["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
