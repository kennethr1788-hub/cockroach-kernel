#!/usr/bin/env python3
"""Run the Gate 5 local paired smoke in fresh processes with network denied."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

import comparative


DARWIN_PROFILE = "(version 1)(allow default)(deny network*)"


def guarded(command: list[str]) -> list[str]:
    system = platform.system()
    if system == "Darwin":
        sandbox = Path("/usr/bin/sandbox-exec")
        if not sandbox.is_file():
            raise RuntimeError("NETWORK_DENY_RUNTIME_MISSING")
        return [str(sandbox), "-p", DARWIN_PROFILE, *command]
    if system == "Linux":
        unshare = shutil.which("unshare")
        if unshare is None:
            raise RuntimeError("NETWORK_DENY_RUNTIME_MISSING")
        return [unshare, "--user", "--map-root-user", "--net", "--mount-proc", *command]
    raise RuntimeError("NETWORK_DENY_PLATFORM_UNSUPPORTED")


def network_deny_proof() -> dict[str, object]:
    probe = [sys.executable, "-c", (
        "import socket,sys\n"
        "s=socket.socket()\n"
        "try:\n s.connect(('1.1.1.1',53))\n"
        "except OSError:\n sys.exit(0)\n"
        "sys.exit(91)\n"
    )]
    result = subprocess.run(guarded(probe), stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False, timeout=20)
    if result.returncode != 0:
        raise RuntimeError("NETWORK_DENY_PROOF_FAILED")
    return {
        "platform": platform.system(),
        "guard_prefix": guarded(["COMMAND"])[:-1],
        "forbidden_egress_result": "BLOCKED",
        "probe_output_sha256": comparative.digest(result.stdout),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_root", type=Path)
    args = parser.parse_args()
    output = args.output_root.resolve()
    output.mkdir(parents=True, exist_ok=False)
    restic = shutil.which("restic")
    if restic is None:
        raise RuntimeError("RESTIC_BINARY_NOT_FOUND")
    child_env = dict(os.environ, CK_GATE5_RESTIC=str(Path(restic).resolve()))
    proof = network_deny_proof()
    receipts = []
    script = Path(__file__).with_name("comparative.py")
    for scenario_index, scenario in enumerate(comparative.SCENARIO_CLASSES):
        methods = list(comparative.METHODS)
        rotation = scenario_index % len(methods)
        methods = methods[rotation:] + methods[:rotation]
        for execution_order, method in enumerate(methods, 1):
            destination = output / f"{scenario}--{method}.json"
            command = guarded([
                sys.executable, str(script), scenario, "1", method, str(destination),
                "--execution-order", str(execution_order),
            ])
            result = subprocess.run(command, cwd=comparative.BASE,
                                    env=child_env,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    check=False, timeout=240)
            if result.returncode != 0:
                raise RuntimeError(
                    f"SMOKE_EXECUTION_FAILED:{scenario}:{method}:"
                    f"{comparative.digest(result.stdout)}")
            receipt = json.loads(destination.read_bytes())
            comparative.validate_receipt(receipt, destination.read_bytes())
            if not receipt["cleanup_pass"]:
                raise RuntimeError("SMOKE_CLEANUP_FAILED")
            receipts.append(receipt)

    # Repeat one representative class for each method in new processes. Only
    # frozen semantic fields are compared; native timestamps/storage differ.
    deterministic = []
    probes = (
        ("committed-plus-uncommitted", "ordinary-git"),
        ("complete-loss", "git-plus-restic-0.19.0"),
        ("conflicting-stale", "product"),
    )
    first = {(item["scenario_class"], item["method"]): item for item in receipts}
    for scenario in comparative.SCENARIO_CLASSES:
        paired = [item for item in receipts if item["scenario_class"] == scenario]
        if len({item["source_manifest_sha256"] for item in paired}) != 1:
            raise RuntimeError("PAIR_SOURCE_HASH_MISMATCH")
        if len({item["event_stream_sha256"] for item in paired}) != 1:
            raise RuntimeError("PAIR_EVENT_HASH_MISMATCH")
        if len({item["loss_receipt_sha256"] for item in paired}) != 1:
            raise RuntimeError("PAIR_LOSS_HASH_MISMATCH")
    for scenario, method in probes:
        destination = output / f"determinism--{scenario}--{method}.json"
        result = subprocess.run(guarded([
            sys.executable, str(script), scenario, "1", method, str(destination)
        ]), cwd=comparative.BASE, env=child_env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            check=False, timeout=240)
        if result.returncode != 0:
            raise RuntimeError("DETERMINISM_EXECUTION_FAILED")
        repeat = json.loads(destination.read_bytes())
        comparative.validate_receipt(repeat, destination.read_bytes())
        original = first[(scenario, method)]
        if repeat["deterministic_outcome"] != original["deterministic_outcome"]:
            raise RuntimeError("SEMANTIC_DETERMINISM_FAILED")
        deterministic.append({
            "scenario": scenario, "method": method,
            "semantic_sha256": comparative.digest(repeat["deterministic_outcome"]),
            "status": "PASS",
        })

    # Generator/scorer inputs must reproduce for every frozen seed.
    generator_hashes = []
    for scenario in comparative.SCENARIO_CLASSES:
        for repetition in (1, 2, 3):
            one = comparative.generate_scenario(scenario, repetition)
            two = comparative.generate_scenario(scenario, repetition)
            if comparative.canonical(one) != comparative.canonical(two):
                raise RuntimeError("GENERATOR_NONDETERMINISTIC")
            generator_hashes.append({
                "scenario": scenario,
                "repetition": repetition,
                "source_bundle_hash": one["source_bundle_hash"],
                "expected_manifest_hash": one["expected_manifest_hash"],
            })
    leaked_roots = [path.name for path in output.parent.glob("gate5-trial-*")]
    if leaked_roots:
        raise RuntimeError("TRIAL_RESIDUE_DETECTED")
    summary = {
        "version": "gate5-local-smoke-v1",
        "status": "GREEN",
        "measured_campaign": False,
        "executions": len(receipts),
        "classes": list(comparative.SCENARIO_CLASSES),
        "methods": list(comparative.METHODS),
        "network_deny_proof": proof,
        "semantic_determinism": deterministic,
        "generator_hashes": generator_hashes,
        "receipt_hashes": sorted(item["receipt_sha256"] for item in receipts),
        "trial_residue": [],
    }
    summary["summary_sha256"] = comparative.digest(summary)
    comparative.atomic_write(output / "summary.json", summary)
    print(comparative.canonical({"status": "GREEN",
                                 "summary_sha256": summary["summary_sha256"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
