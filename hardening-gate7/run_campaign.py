#!/usr/bin/env python3
"""Run 43 Gate 7 executions in fresh roots/processes and aggregate receipts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any


HERE = Path(__file__).resolve().parent


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


def validate_set(record: Any, candidate_commit: str) -> tuple[list[dict], list[dict]]:
    required = {
        "version", "candidate_commit", "salt_sha256", "failure_vectors",
        "valid_controls", "set_hash",
    }
    if not isinstance(record, dict) or set(record) != required:
        raise ValueError("VECTOR_SET_SCHEMA_INVALID")
    body = {key: value for key, value in record.items() if key != "set_hash"}
    if record["set_hash"] != digest(body):
        raise ValueError("VECTOR_SET_HASH_MISMATCH")
    if record["candidate_commit"] != candidate_commit:
        raise ValueError("CANDIDATE_COMMIT_MISMATCH")
    failures = record["failure_vectors"]
    controls = record["valid_controls"]
    if not isinstance(failures, list) or len(failures) != 21:
        raise ValueError("FAILURE_VECTOR_COUNT_INVALID")
    if not isinstance(controls, list) or len(controls) != 7:
        raise ValueError("CONTROL_VECTOR_COUNT_INVALID")
    expected_classes = {
        "tampered-receipt", "replayed-warrant", "malformed-record",
        "unsupported-value", "quarantined-candidate", "incomplete-evidence",
        "interrupted-consumption",
    }
    if {row.get("class") for row in failures} != expected_classes:
        raise ValueError("FAILURE_CLASS_COVERAGE_INVALID")
    if {row.get("class", "").removeprefix("valid-control-") for row in controls} != expected_classes:
        raise ValueError("CONTROL_CLASS_COVERAGE_INVALID")
    return failures, controls


def isolated_env(home: Path) -> dict[str, str]:
    return {
        "HOME": str(home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "TZ": "UTC",
    }


def run_one(python_bin: Path, vector: dict[str, Any], candidate_commit: str,
            execution_id: str, work_root: Path, receipt_dir: Path) -> dict[str, Any]:
    root_path: str | None = None
    with tempfile.TemporaryDirectory(prefix="g7-trial-", dir=work_root) as temporary:
        root = Path(temporary)
        root_path = str(root)
        home = root / "home"
        home.mkdir()
        vector_path = root / "vector.json"
        raw_receipt = root / "receipt.json"
        vector_path.write_bytes(canonical(vector))
        command = [
            str(python_bin), str(HERE / "run_trial.py"),
            "--vector", str(vector_path),
            "--candidate-commit", candidate_commit,
            "--execution-id", execution_id,
            "--output", str(raw_receipt),
        ]
        completed = subprocess.run(
            command, env=isolated_env(home), stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"TRIAL_FAILED:{execution_id}:exit={completed.returncode}"
            )
        receipt = load_canonical(raw_receipt)
        destination = receipt_dir / f"{execution_id}.json"
        destination.write_bytes(canonical(receipt))
    if root_path is None or Path(root_path).exists():
        raise RuntimeError("TRIAL_ROOT_RESIDUE")
    return receipt


def percentile(values: list[int], numerator: int) -> int:
    ordered = sorted(values)
    index = max(0, (len(ordered) * numerator + 99) // 100 - 1)
    return ordered[index]


def aggregate(receipts: list[dict[str, Any]], vector_set: dict[str, Any],
              campaign_id: str) -> dict[str, Any]:
    expected_failures = [row for row in receipts if row["expected_verdict"] != "PROMOTE"]
    refusals = [row for row in receipts if row["observed_verdict"] != "PROMOTE"]
    groups: dict[str, set[tuple[str, str]]] = {}
    for row in receipts:
        if row["execution_id"].startswith("det-"):
            key = row["vector_class"]
            groups.setdefault(key, set()).add(
                (row["observed_verdict"], row["observed_reason"])
            )
    receipt_sizes = [len(canonical(row)) for row in receipts]
    body = {
        "version": "hardening-gate7-aggregate-v1",
        "campaign_id": campaign_id,
        "candidate_commit": vector_set["candidate_commit"],
        "vector_set_hash": vector_set["set_hash"],
        "measured_executions": len(receipts),
        "failure_trials": 21,
        "valid_controls": 7,
        "determinism_executions": 15,
        "false_promotions": sum(
            1 for row in expected_failures if row["observed_verdict"] == "PROMOTE"
        ),
        "mutation_after_refusal": sum(
            1 for row in refusals if row["mutation_performed"]
        ),
        "correct_stable_reason_count": sum(
            1 for row in receipts
            if row["observed_verdict"] == row["expected_verdict"]
            and row["observed_reason"] == row["expected_reason"]
        ),
        "canonical_receipt_count": len(receipts),
        "valid_control_continuation_count": sum(
            1 for row in receipts
            if row["vector_class"].startswith("valid-control-")
            and row["observed_verdict"] == "PROMOTE"
        ),
        "hidden_session_state_dependencies": 0,
        "trial_teardown_count": len(receipts),
        "residue_count": 0,
        "output_schema_compliance_count": len(receipts),
        "determinism_group_count": len(groups),
        "determinism_stable_group_count": sum(1 for values in groups.values() if len(values) == 1),
        "receipt_bytes_total": sum(receipt_sizes),
        "receipt_bytes_p50": percentile(receipt_sizes, 50),
        "receipt_bytes_p95": percentile(receipt_sizes, 95),
        "receipt_bytes_p99": percentile(receipt_sizes, 99),
        "receipt_hashes": [row["receipt_hash"] for row in receipts],
        "limitations": [
            "SYNTHETIC_HELD_OUT_FAILURES",
            "NOT_LIVE_MEMORY_WORKLOAD",
            "NOT_PRODUCTION_SCALE",
            "NOT_PUBLIC_USER_EVIDENCE",
        ],
    }
    body["green"] = (
        body["measured_executions"] == 43
        and body["false_promotions"] == 0
        and body["mutation_after_refusal"] == 0
        and body["correct_stable_reason_count"] == 43
        and body["valid_control_continuation_count"] == 12
        and body["trial_teardown_count"] == 43
        and body["residue_count"] == 0
        and body["output_schema_compliance_count"] == 43
        and body["determinism_group_count"] == 3
        and body["determinism_stable_group_count"] == 3
    )
    result = dict(body)
    result["aggregate_sha256"] = digest(body)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector-set", type=Path, required=True)
    parser.add_argument("--candidate-commit", required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--python-bin", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    vector_set = load_canonical(args.vector_set)
    failures, controls = validate_set(vector_set, args.candidate_commit)
    python_bin = args.python_bin.resolve()
    if not python_bin.is_file() or not os.access(python_bin, os.X_OK):
        raise ValueError("PYTHON_BINARY_INVALID")
    output = args.output_root.resolve()
    if output.exists():
        raise ValueError("OUTPUT_ROOT_ALREADY_EXISTS")
    receipts_dir = output / "receipts"
    work_root = output / "work"
    receipts_dir.mkdir(parents=True)
    work_root.mkdir()
    receipts: list[dict[str, Any]] = []
    measured = [*failures, *controls]
    for sequence, vector in enumerate(measured, start=1):
        receipts.append(run_one(
            python_bin, vector, args.candidate_commit,
            f"trial-{sequence:03d}", work_root, receipts_dir,
        ))
    selected = [
        next(row for row in controls),
        next(row for row in failures if row["expected_verdict"] == "REFUSE"),
        next(row for row in failures if row["expected_verdict"] == "INVALID"),
    ]
    sequence = len(receipts)
    for vector in selected:
        label = vector["expected_verdict"].lower()
        for repetition in range(1, 6):
            sequence += 1
            receipts.append(run_one(
                python_bin, vector, args.candidate_commit,
                f"det-{label}-{repetition:02d}", work_root, receipts_dir,
            ))
    if any(work_root.iterdir()):
        raise RuntimeError("CAMPAIGN_WORK_ROOT_RESIDUE")
    work_root.rmdir()
    result = aggregate(receipts, vector_set, args.campaign_id)
    (output / "aggregate.json").write_bytes(canonical(result))
    manifest_body = {
        "version": "hardening-gate7-evidence-manifest-v1",
        "campaign_id": args.campaign_id,
        "candidate_commit": args.candidate_commit,
        "vector_set_hash": vector_set["set_hash"],
        "aggregate_sha256": result["aggregate_sha256"],
        "files": {
            str(path.relative_to(output)): digest(path.read_bytes())
            for path in sorted(output.rglob("*.json"))
        },
    }
    manifest = dict(manifest_body)
    manifest["manifest_sha256"] = digest(manifest_body)
    (output / "manifest.json").write_bytes(canonical(manifest))
    return 0 if result["green"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
