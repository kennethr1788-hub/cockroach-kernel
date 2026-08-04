#!/usr/bin/env python3
"""Fixed-budget, immutable-evaluator recovery benchmark.

This is an offline evidence harness, not a self-modifying runtime. It runs the
frozen evaluator, records keep/discard/crash outcomes, and never edits product
code, invokes a model, opens a network connection, or promotes a candidate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_manifest(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    manifest = json.loads(raw)
    if manifest.get("version") != "ck-recovery-eval-v1":
        raise SystemExit("MANIFEST_VERSION_INVALID")
    required = {"budget_seconds", "kill_seconds", "evaluator_command", "immutable_paths", "metrics"}
    if set(manifest) - required - {"version", "mutable_scope"} or not required.issubset(manifest):
        raise SystemExit("MANIFEST_FIELDS_INVALID")
    return manifest, sha256_bytes(raw)


def verify_immutable(root: Path, manifest: dict) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative in manifest["immutable_paths"]:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"IMMUTABLE_PATH_INVALID:{relative}")
        hashes[relative] = sha256_file(path)
    return hashes


def run_one(root: Path, manifest: dict, manifest_hash: str, baseline: dict[str, str], iteration: int, budget: float) -> dict:
    start = time.monotonic()
    start_utc = time.time()
    status = "keep"
    reason = "EVALUATOR_PASS"
    stdout = b""
    stderr = b""
    try:
        environment = os.environ.copy()
        path_entries = [str(root)]
        for candidate in (root / "build" / "lib", root / "p7-recovery", root / "p9-cloud", root / "p4-verifier"):
            if candidate.is_dir():
                path_entries.insert(0, str(candidate))
        existing = environment.get("PYTHONPATH")
        if existing:
            path_entries.append(existing)
        environment["PYTHONPATH"] = os.pathsep.join(path_entries)
        completed = subprocess.run(
            [sys.executable, *manifest["evaluator_command"]],
            cwd=root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=budget,
            check=False,
        )
        stdout, stderr = completed.stdout, completed.stderr
        if completed.returncode != 0:
            status, reason = "discard", f"EVALUATOR_EXIT_{completed.returncode}"
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
        status, reason = "crash", "EVALUATOR_TIMEOUT"
    elapsed = time.monotonic() - start
    hashes_after = verify_immutable(root, manifest)
    if hashes_after != baseline:
        raise SystemExit("IMMUTABLE_EVALUATOR_CHANGED")
    return {
        "version": "ck-recovery-eval-result-v1",
        "iteration": iteration,
        "status": status,
        "reason": reason,
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "manifest_hash": manifest_hash,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "elapsed_seconds": round(elapsed, 6),
        "stdout_hash": sha256_bytes(stdout),
        "stderr_hash": sha256_bytes(stderr),
        "metrics": {
            "preservation_coverage": 1 if status == "keep" else 0,
            "refusal_correctness": 1 if status == "keep" else 0,
            "determinism": 1 if status == "keep" else 0,
            "latency_seconds": round(elapsed, 6),
            "evidence_bytes": len(stdout) + len(stderr),
        },
        "immutable_hashes": hashes_after,
        "no_network": True,
        "no_model": True,
        "no_product_mutation": True,
        "started_unix": start_utc,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(Path(__file__).with_name("manifest.json")))
    parser.add_argument("--output", required=True)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--budget-seconds", type=float)
    args = parser.parse_args(argv)
    if args.iterations < 1 or args.iterations > 100:
        raise SystemExit("ITERATIONS_INVALID")
    root = Path(__file__).resolve().parents[2]
    manifest, manifest_hash = load_manifest(Path(args.manifest).resolve())
    budget = args.budget_seconds if args.budget_seconds is not None else float(manifest["budget_seconds"])
    if budget <= 0 or budget > float(manifest["kill_seconds"]):
        raise SystemExit("BUDGET_INVALID")
    baseline = verify_immutable(root, manifest)
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("ab") as handle:
        for iteration in range(1, args.iterations + 1):
            result = run_one(root, manifest, manifest_hash, baseline, iteration, budget)
            raw = canonical(result) + b"\n"
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
            print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
