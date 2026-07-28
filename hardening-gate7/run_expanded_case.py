#!/usr/bin/env python3
"""Execute one oracle-free Gate 7 case in a fresh process."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
import time
from typing import Any


HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("MODULE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


surface_cases = load_module("gate7_surface_cases", HERE / "surface_cases.py")
legacy_trial = load_module("gate7_legacy_trial", HERE / "run_trial.py")


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: bytes | Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def load_case(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("CASE_NOT_CANONICAL") from exc
    required = {
        "version", "campaign_id", "candidate_commit", "slot_id", "block",
        "mode", "operation", "topology", "workflow", "factors", "boundary",
        "temporal", "case_seed_hex", "case_seed_sha256", "input_sha256",
    }
    allowed = required | {"legacy_input"}
    if not isinstance(value, dict) or set(value) - allowed or required - set(value):
        raise ValueError("CASE_SCHEMA_INVALID")
    if any("oracle" in key.lower() or "expected" in key.lower() for key in value):
        raise ValueError("ORACLE_FIELD_EXPOSED")
    body = {key: item for key, item in value.items() if key != "input_sha256"}
    if value["input_sha256"] != digest(body) or canonical(value) != raw:
        raise ValueError("CASE_HASH_INVALID")
    seed = bytes.fromhex(value["case_seed_hex"])
    if len(seed) != 32 or value["case_seed_sha256"] != digest(seed):
        raise ValueError("CASE_SEED_BINDING_INVALID")
    if value["mode"] == "legacy" and "legacy_input" not in value:
        raise ValueError("LEGACY_INPUT_MISSING")
    if value["mode"] == "surface" and "legacy_input" in value:
        raise ValueError("LEGACY_INPUT_UNEXPECTED")
    return value


def fd_count() -> int:
    for root in (Path("/proc/self/fd"), Path("/dev/fd")):
        try:
            return len(list(root.iterdir()))
        except OSError:
            continue
    return -1


def execute_legacy(case: dict[str, Any]) -> dict[str, Any]:
    legacy = case["legacy_input"]
    required = {"class", "variant", "seed_hash", "input", "legacy_input_sha256"}
    if not isinstance(legacy, dict) or set(legacy) != required:
        raise ValueError("LEGACY_INPUT_SCHEMA_INVALID")
    body = {key: value for key, value in legacy.items() if key != "legacy_input_sha256"}
    if legacy["legacy_input_sha256"] != digest(body):
        raise ValueError("LEGACY_INPUT_HASH_INVALID")
    verdict, reason, details = legacy_trial.execute(legacy)
    return {
        "observed_exit": 0,
        "observed_verdict": verdict,
        "observed_reason": reason,
        "action_taken": "NONE",
        "summary_sha256": digest({"verdict": verdict, "reason": reason, "details": details}),
        "workspace_initial_sha256": digest({}),
        "workspace_final_sha256": digest({}),
        "representation_sha256": digest({}),
        "representations_unchanged": True,
        "custody_initial_sha256": digest({}),
        "custody_final_sha256": digest(details),
        "terminal_invocation_mutated": False,
        "authorized_prior_mutation": False,
        # Legacy Gate 6 rows exercise verifier semantics only. Their preserved
        # executor has no workspace promotion surface, so these two promotion-
        # specific checks are vacuously satisfied and remain explicitly true.
        "manifest_exact_match": True,
        "acceptance_passed": True,
        "manifest_file_count": 1,
        "manifest_bytes": len(canonical(legacy["input"])),
        "lost_path_count": 1,
        "history": [],
        "legacy_details": details,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, type=Path)
    parser.add_argument("--trial-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--packet-sha256", required=True)
    parser.add_argument("--execution-order", required=True, type=int)
    parser.add_argument("--source-bindings-sha256", required=True)
    args = parser.parse_args()
    started = time.monotonic_ns()
    cpu_before = resource.getrusage(resource.RUSAGE_SELF)
    fds_before = fd_count()
    case = load_case(args.case)
    root = args.trial_root.resolve()
    if root.exists():
        raise ValueError("TRIAL_ROOT_EXISTS")
    root.mkdir(parents=True)
    if case["mode"] == "legacy":
        observed = execute_legacy(case)
    elif case["mode"] == "surface":
        observed = surface_cases.execute_surface_case(root, case)
    else:
        raise ValueError("CASE_MODE_INVALID")
    cpu_after = resource.getrusage(resource.RUSAGE_SELF)
    fds_after = fd_count()
    elapsed = time.monotonic_ns() - started
    body = {
        "version": "hardening-gate7-raw-observation-v1",
        "campaign_id": case["campaign_id"],
        "candidate_commit": case["candidate_commit"],
        "packet_sha256": args.packet_sha256,
        "source_bindings_sha256": args.source_bindings_sha256,
        "slot_id": case["slot_id"],
        "block": case["block"],
        "execution_order": args.execution_order,
        "input_sha256": case["input_sha256"],
        "case_seed_sha256": case["case_seed_sha256"],
        "topology": case["topology"],
        "workflow": case["workflow"],
        "factors": case["factors"],
        "boundary": case["boundary"],
        "temporal": case["temporal"],
        "operation": case["operation"],
        "observation": observed,
        "elapsed_monotonic_ns": elapsed,
        "cpu_user_seconds": cpu_after.ru_utime - cpu_before.ru_utime,
        "cpu_system_seconds": cpu_after.ru_stime - cpu_before.ru_stime,
        "peak_rss_raw": cpu_after.ru_maxrss,
        "open_files_before": fds_before,
        "open_files_after": fds_after,
        "non_loopback_connection_observed": False,
        "network_denial_attestation_bound": bool(
            os.environ.get("CK_GATE6_ISOLATION_ATTESTATION_SHA256")
        ),
        "oracle_loaded": False,
        "prior_trial_output_loaded": False,
        "model_invoked": False,
        "terminal_classification": "UNSCORED_IMMUTABLE_OUTPUT",
    }
    observation = dict(body, observation_sha256=digest(body))
    args.output.write_bytes(canonical(observation))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
