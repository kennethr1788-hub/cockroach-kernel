#!/usr/bin/env python3
"""Run 84 oracle-free Gate 7 observations and freeze them before scoring."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ZERO_HASH = "0" * 64


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


def atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_canonical(path: Path) -> Any:
    raw = path.read_bytes()
    value = json.loads(raw)
    if canonical(value) != raw:
        raise ValueError("NON_CANONICAL_FILE")
    return value


def validate_input_manifest(path: Path, input_root: Path) -> dict[str, Any]:
    manifest = load_canonical(path)
    required = {
        "version", "campaign_id", "candidate_commit", "execution_order",
        "case_files", "case_count", "oracle_included", "manifest_sha256",
    }
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise ValueError("INPUT_MANIFEST_SCHEMA_INVALID")
    body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    if manifest["manifest_sha256"] != digest(body):
        raise ValueError("INPUT_MANIFEST_HASH_INVALID")
    order = manifest["execution_order"]
    if manifest["case_count"] != 84 or len(order) != 84 or len(set(order)) != 84:
        raise ValueError("INPUT_MANIFEST_COUNT_INVALID")
    if manifest["oracle_included"] is not False:
        raise ValueError("ORACLE_EXPOSED_TO_RUNNER")
    if any("oracle" in name.lower() for name in manifest["case_files"]):
        raise ValueError("ORACLE_FILE_EXPOSED_TO_RUNNER")
    for slot_id in order:
        name = f"{slot_id}.json"
        case_path = input_root / name
        if not case_path.is_file() or digest(case_path.read_bytes()) != manifest["case_files"].get(name):
            raise ValueError("CASE_FILE_HASH_INVALID")
    return manifest


def isolated_env(home: Path) -> dict[str, str]:
    allowed = {
        "HOME": str(home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "TZ": "UTC",
    }
    for name in (
        "CK_GATE6_ISOLATION_ATTESTATION",
        "CK_GATE6_ISOLATION_ATTESTATION_SHA256",
    ):
        if name in os.environ:
            allowed[name] = os.environ[name]
    return allowed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-manifest", required=True, type=Path)
    parser.add_argument("--input-root", required=True, type=Path)
    parser.add_argument("--python-bin", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--packet-sha256", required=True)
    parser.add_argument("--source-bindings-sha256", required=True)
    args = parser.parse_args()
    input_root = args.input_root.resolve()
    manifest = validate_input_manifest(args.input_manifest.resolve(), input_root)
    python = args.python_bin.resolve()
    if not python.is_file() or not os.access(python, os.X_OK):
        raise ValueError("PYTHON_BINARY_INVALID")
    output = args.output_root.resolve()
    if output.exists():
        raise ValueError("OUTPUT_ROOT_EXISTS")
    raw_root = output / "raw-observations"
    receipt_root = output / "unscored-receipts"
    work_root = output / "work"
    home = output / "empty-home"
    for item in (raw_root, receipt_root, work_root, home):
        item.mkdir(parents=True)
    previous = ZERO_HASH
    receipt_hashes: list[str] = []
    observation_hashes: list[str] = []
    for execution_order, slot_id in enumerate(manifest["execution_order"], start=1):
        case_path = input_root / f"{slot_id}.json"
        trial_root = work_root / f"trial-{execution_order:03d}"
        observation_path = raw_root / f"{execution_order:03d}-{slot_id}.json"
        command = [
            str(python), str(HERE / "run_expanded_case.py"),
            "--case", str(case_path),
            "--trial-root", str(trial_root),
            "--output", str(observation_path),
            "--packet-sha256", args.packet_sha256,
            "--execution-order", str(execution_order),
            "--source-bindings-sha256", args.source_bindings_sha256,
        ]
        completed = subprocess.run(
            command,
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=isolated_env(home),
            timeout=120,
        )
        if completed.returncode != 0:
            failure_root = output / "terminal-failures"
            failure_root.mkdir(exist_ok=True)
            stdout_path = failure_root / f"{execution_order:03d}-{slot_id}.stdout.bin"
            stderr_path = failure_root / f"{execution_order:03d}-{slot_id}.stderr.bin"
            atomic_write(stdout_path, completed.stdout)
            atomic_write(stderr_path, completed.stderr)
            failure_body = {
                "version": "hardening-gate7-terminal-failure-v1",
                "campaign_id": manifest["campaign_id"],
                "slot_id": slot_id,
                "execution_order": execution_order,
                "child_exit": completed.returncode,
                "stdout_sha256": digest(completed.stdout),
                "stderr_sha256": digest(completed.stderr),
                "stdout_file": stdout_path.name,
                "stderr_file": stderr_path.name,
                "input_manifest_sha256": manifest["manifest_sha256"],
                "terminal_classification": "UNSCORED_EXECUTION_FAILURE",
            }
            failure = dict(failure_body, failure_receipt_sha256=digest(failure_body))
            atomic_write(
                failure_root / f"{execution_order:03d}-{slot_id}.receipt.json",
                canonical(failure),
            )
            raise RuntimeError(
                f"CASE_PROCESS_FAILED:{slot_id}:exit={completed.returncode}:"
                f"stderr_sha256={digest(completed.stderr)}"
            )
        observation = load_canonical(observation_path)
        if observation.get("slot_id") != slot_id or observation.get("execution_order") != execution_order:
            raise RuntimeError("OBSERVATION_IDENTITY_MISMATCH")
        if observation.get("terminal_classification") != "UNSCORED_IMMUTABLE_OUTPUT":
            raise RuntimeError("PREMATURE_SCORING_DETECTED")
        if observation.get("oracle_loaded") is not False:
            raise RuntimeError("ORACLE_RUNNER_BOUNDARY_VIOLATED")
        observation_hash = digest(observation_path.read_bytes())
        observation_hashes.append(observation_hash)
        if trial_root.exists():
            shutil.rmtree(trial_root, ignore_errors=False)
        if trial_root.exists():
            raise RuntimeError("TRIAL_ROOT_RESIDUE")
        receipt_body = {
            "version": "hardening-gate7-unscored-receipt-v1",
            "campaign_id": manifest["campaign_id"],
            "slot_id": slot_id,
            "execution_order": execution_order,
            "input_manifest_sha256": manifest["manifest_sha256"],
            "observation_sha256": observation_hash,
            "previous_receipt_sha256": previous,
            "cleanup": "GREEN",
            "residue": False,
            "child_exit": completed.returncode,
            "stdout_sha256": digest(completed.stdout),
            "stderr_sha256": digest(completed.stderr),
            "terminal_classification": "UNSCORED_IMMUTABLE_OUTPUT",
        }
        receipt = dict(receipt_body, receipt_sha256=digest(receipt_body))
        receipt_path = receipt_root / f"{execution_order:03d}-{slot_id}.json"
        atomic_write(receipt_path, canonical(receipt))
        previous = receipt["receipt_sha256"]
        receipt_hashes.append(previous)
    if any(work_root.iterdir()):
        raise RuntimeError("CAMPAIGN_WORK_ROOT_RESIDUE")
    work_root.rmdir()
    raw_body = {
        "version": "hardening-gate7-raw-campaign-manifest-v1",
        "campaign_id": manifest["campaign_id"],
        "candidate_commit": manifest["candidate_commit"],
        "packet_sha256": args.packet_sha256,
        "source_bindings_sha256": args.source_bindings_sha256,
        "input_manifest_sha256": manifest["manifest_sha256"],
        "raw_observation_count": 84,
        "observation_hashes": observation_hashes,
        "receipt_hashes": receipt_hashes,
        "final_receipt_sha256": previous,
        "oracle_loaded": False,
        "scoring_performed": False,
        "post_reveal_tuning_events": 0,
        "work_root_removed": not work_root.exists(),
    }
    raw_manifest = dict(raw_body, raw_manifest_sha256=digest(raw_body))
    atomic_write(output / "raw-campaign-manifest.json", canonical(raw_manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
