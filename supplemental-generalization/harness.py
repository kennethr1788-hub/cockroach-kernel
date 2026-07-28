#!/usr/bin/env python3
"""Compact deterministic scale extension for the frozen Gate 6 comparator.

The generated repository bytes are described by seed/size metadata and are
materialized inside each isolated trial.  No large byte payload is embedded in
the transfer archive or scenario record.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import sys
import tempfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "hardening-gate5/comparative.py"
CANDIDATE_COMMIT = "8718fbecc2b145ff36ce8c3ed655e92b5906aeab"
EVIDENCE_MODE = "SUPPLEMENTAL_GENERALIZATION"
PROFILES = {
    "small": {"file_count": 16, "bytes_per_file": 8192},
    "medium": {"file_count": 64, "bytes_per_file": 65536},
    "large": {"file_count": 128, "bytes_per_file": 524288},
}


def load_base():
    spec = importlib.util.spec_from_file_location("supplemental_gate5_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("COMPARATIVE_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = load_base()


def generated_content(seed: str, relative: str, size: int) -> bytes:
    # SHAKE gives deterministic high-entropy bytes without embedding a payload.
    # It prevents compression/deduplication from turning the byte-scale profile
    # into a trivial repeated-block benchmark.
    return hashlib.shake_256(f"{seed}:{relative}".encode("utf-8")).digest(size)


def generated_specs(profile: str, scenario: str, repetition: int) -> list[dict[str, Any]]:
    values = PROFILES[profile]
    seed = base.digest({"version": "supplemental-scale-seed-v1", "profile": profile,
                        "scenario": scenario, "repetition": repetition})
    return [
        {
            "path": f"bulk/module-{index:04d}.bin",
            "seed": seed,
            "size": values["bytes_per_file"],
        }
        for index in range(values["file_count"])
    ]


def spec_manifest(specs: list[dict[str, Any]]) -> dict[str, str]:
    return {
        item["path"]: base.digest(generated_content(item["seed"], item["path"], item["size"]))
        for item in specs
    }


def build_scenario(profile: str, scenario_class: str, repetition: int) -> dict[str, Any]:
    scenario = base.generate_scenario(scenario_class, repetition)
    specs = generated_specs(profile, scenario_class, repetition)
    generated_manifest = spec_manifest(specs)
    scenario["public"]["scale_profile"] = {
        "name": profile,
        **PROFILES[profile],
        "total_generated_bytes": sum(item["size"] for item in specs),
        "generator": "shake256-deterministic-bytes-v1",
    }
    scenario["public"]["generated_files"] = specs
    for packet in scenario["public"]["events"]:
        packet["generated_files"] = specs
        small = {path: base.digest(bytes.fromhex(payload))
                 for path, payload in packet["files"].items()}
        packet["workspace_manifest_hash"] = base.digest({**small, **generated_manifest})
        packet["event_hash"] = base.digest({key: value for key, value in packet.items()
                                             if key != "event_hash"})
    scenario["expected_manifest"].update(generated_manifest)
    scenario["expected_manifest"] = dict(sorted(scenario["expected_manifest"].items()))
    scenario["expected_manifest_hash"] = base.digest(scenario["expected_manifest"])
    scenario["public"]["work_units"].extend(
        {"id": path, "category": "committed"} for path in sorted(generated_manifest)
    )
    if scenario["public"]["loss"]["type"] == "COMPLETE":
        scenario["public"]["loss"]["paths"] = sorted(scenario["expected_manifest"])
    scenario["source_bundle_hash"] = base.digest(scenario["public"])
    return scenario


def materialize_event(workspace: Path, packet: dict[str, Any]) -> None:
    specs = packet.get("generated_files", [])
    desired = set(packet["files"]) | {item["path"] for item in specs}
    for relative in list(base.manifest(workspace)):
        if relative not in desired:
            base.safe_path(workspace, relative).unlink()
    for relative, encoded in packet["files"].items():
        target = base.safe_path(workspace, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(bytes.fromhex(encoded))
    for item in specs:
        target = base.safe_path(workspace, item["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        content = generated_content(item["seed"], item["path"], item["size"])
        if not target.exists() or target.stat().st_size != item["size"] or base.digest(target.read_bytes()) != base.digest(content):
            target.write_bytes(content)


def limitations(mode: str) -> list[str]:
    if mode == EVIDENCE_MODE:
        return [
            "SYNTHETIC_PAIRED_SCALE_GENERALIZATION",
            "RUNPOD_GENERIC_COMPUTE",
            "NO_POPULATION_INFERENCE",
            "PRODUCT_TEAM_AUTHORED_PROTOCOL_AND_SUCCESS_RULES",
            "NOT_PRODUCTION_SCALE",
            "NOT_INDEPENDENT_USER_EVIDENCE",
        ]
    return original_limitations(mode)


def validate_context(mode: str, runtime_platform: str,
                     candidate_commit: str, campaign_id: str) -> None:
    if mode == EVIDENCE_MODE:
        if runtime_platform != "Linux":
            raise base.HarnessError("SUPPLEMENTAL_MODE_REQUIRES_LINUX")
        if candidate_commit != CANDIDATE_COMMIT:
            raise base.HarnessError("CANDIDATE_COMMIT_INVALID")
        if not campaign_id.startswith("ck-supp-generalization-"):
            raise base.HarnessError("CAMPAIGN_ID_INVALID")
        return
    original_validate_context(mode, runtime_platform, candidate_commit, campaign_id)


original_materialize = base.materialize_event
original_limitations = base.evidence_limitations
original_validate_context = base.validate_evidence_context
base.materialize_event = materialize_event
base.evidence_limitations = limitations
base.validate_evidence_context = validate_context
base.EVIDENCE_MODES = (*base.EVIDENCE_MODES, EVIDENCE_MODE)


def run_one(profile: str, scenario_class: str, repetition: int, method: str,
            output: Path, campaign_id: str, execution_order: int) -> dict[str, Any]:
    scenario = build_scenario(profile, scenario_class, repetition)
    run_root = Path(tempfile.mkdtemp(prefix="supp-generalization-", dir=output.parent))
    env = base.isolated_env(run_root)
    adapter = base.ADAPTERS[method](run_root, scenario, env)
    setup_started = time.monotonic_ns()
    try:
        adapter.setup()
        for packet in scenario["public"]["events"]:
            adapter.checkpoint(packet)
        if base.manifest(adapter.workspace) != {
                **{path: base.digest(bytes.fromhex(payload))
                   for path, payload in scenario["public"]["events"][-1]["files"].items()},
                **spec_manifest(scenario["public"]["generated_files"])}:
            raise base.HarnessError("SOURCE_PAIRING_DRIFT")
        setup_ms = int((time.monotonic_ns() - setup_started) / 1_000_000)
        adapter.lose()
        recovery_started = time.monotonic_ns()
        prior_handler = signal.getsignal(signal.SIGALRM)

        def timeout_handler(_signum: int, _frame: Any) -> None:
            raise base.HarnessError("RECOVERY_TIMEOUT")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, base.RECOVERY_BUDGET_SECONDS)
        try:
            target, operation = adapter.recover()
            recovery_ms = int((time.monotonic_ns() - recovery_started) / 1_000_000)
            receipt = base.score(adapter, target, operation, scenario, recovery_ms,
                                 setup_ms, 0, 0, campaign_id=campaign_id,
                                 candidate_commit=CANDIDATE_COMMIT,
                                 execution_order=execution_order,
                                 evidence_mode=EVIDENCE_MODE,
                                 runtime_platform="Linux")
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, prior_handler)
    finally:
        teardown_started = time.monotonic_ns()
        shutil.rmtree(run_root, ignore_errors=False)
        teardown_ms = int((time.monotonic_ns() - teardown_started) / 1_000_000)
    receipt["teardown_ms"] = teardown_ms
    receipt["residue_bytes_after_teardown"] = base.tree_bytes(run_root)
    receipt["cleanup_pass"] = receipt["residue_bytes_after_teardown"] == 0
    receipt["receipt_sha256"] = base.digest({key: value for key, value in receipt.items()
                                             if key != "receipt_sha256"})
    base.validate_receipt(receipt)
    wrapped = {
        "version": "supplemental-generalization-receipt-v1",
        "scale_profile": scenario["public"]["scale_profile"],
        "base_receipt": receipt,
    }
    wrapped["receipt_sha256"] = base.digest(wrapped)
    base.atomic_write(output, wrapped)
    return wrapped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", choices=PROFILES)
    parser.add_argument("scenario", choices=base.SCENARIO_CLASSES)
    parser.add_argument("repetition", type=int, choices=(1, 2))
    parser.add_argument("method", choices=base.METHODS)
    parser.add_argument("output", type=Path)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--execution-order", type=int, choices=(1, 2, 3), required=True)
    args = parser.parse_args()
    receipt = run_one(args.profile, args.scenario, args.repetition, args.method,
                      args.output.resolve(), args.campaign_id, args.execution_order)
    print(base.canonical({"status": "GREEN", "receipt_sha256":
                          receipt["receipt_sha256"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
