"""P7 fresh-context continuation harness plumbing.

Accepts only a canonical recovery decision record plus the promoted surviving
candidate record, and deterministically verifies the expected synthetic
feature file binding. There is no hidden session state: the expected feature
content is a pure function of (task_id, candidate_id) already bound inside
the two input records, and verification recomputes it from those inputs
alone. Standard library only; no filesystem writes, no network, no authority.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from records import (
    RecoveryError, load_canonical, sha256_hex, validate_candidate,
    validate_recovery_decision,
)

def verify_continuation(decision: Any, candidate: Any) -> tuple[bool, str]:
    """Verify a fresh-context continuation against only the two inputs.

    Returns (ok, stable_reason). Fails closed on any malformed input,
    non-promotion decision, record mismatch, or feature binding drift.
    """
    try:
        validate_recovery_decision(decision)
        validate_candidate(candidate)
    except RecoveryError as exc:
        return False, str(exc)
    if decision["decision"] != "PROMOTE":
        return False, "NOT_A_PROMOTION"
    if decision["task_id"] != candidate["task_id"]:
        return False, "TASK_MISMATCH"
    if decision["candidate_id"] != candidate["candidate_id"]:
        return False, "CANDIDATE_MISMATCH"
    test = candidate["executable_test"]
    if test["passed"] is not True:
        return False, "EXECUTABLE_TEST_FAILED"
    if test["path"] not in candidate["file_hashes"]:
        return False, "FEATURE_MISMATCH"
    if test["feature_hash"] != candidate["file_hashes"][test["path"]]:
        return False, "FEATURE_MISMATCH"
    return True, "FRESH_CONTEXT_PASS"


def verify_workspace(decision: Any, candidate: Any,
                     workspace: str | Path) -> tuple[bool, str]:
    """Verify the actual successor bytes from explicit record + workspace inputs."""
    ok, reason = verify_continuation(decision, candidate)
    if not ok:
        return ok, reason
    root = Path(workspace).resolve()
    test_path = candidate["executable_test"]["path"]
    target = root.joinpath(*test_path.split("/"))
    try:
        resolved = target.resolve(strict=True)
    except (FileNotFoundError, RuntimeError, OSError):
        return False, "FEATURE_MISSING"
    if root not in resolved.parents or target.is_symlink() or not target.is_file():
        return False, "UNSAFE_PATH"
    if sha256_hex(target.read_bytes()) != candidate["executable_test"]["feature_hash"]:
        return False, "FEATURE_MISMATCH"
    return True, "FRESH_CONTEXT_PASS"


def main(argv: list[str] | None = None) -> int:
    """CLI: fresh_context.py <decision.json> <candidate.json> <workspace>.

    Both files must be stored in exact canonical form; anything else is
    rejected before verification. Prints a deterministic verdict line.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 3:
        print("usage: fresh_context.py <decision.json> <candidate.json> <workspace>")
        return 2
    try:
        decision = load_canonical(args[0])
        candidate = load_canonical(args[1])
    except RecoveryError as exc:
        print(json.dumps({"ok": False, "reason": str(exc)}, sort_keys=True))
        return 1
    ok, reason = verify_workspace(decision, candidate, args[2])
    print(json.dumps({"ok": ok, "reason": reason}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
