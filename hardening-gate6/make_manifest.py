#!/usr/bin/env python3
"""Generate the frozen Gate 6 R2 54-row execution manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


SCENARIOS = (
    "committed-only",
    "committed-plus-uncommitted",
    "complete-loss",
    "partial-loss",
    "conflicting-stale",
    "clean-control",
)
METHODS = ("ordinary-git", "git-plus-restic-0.19.0", "product")
CANDIDATE = "8718fbecc2b145ff36ce8c3ed655e92b5906aeab"
CAMPAIGN_ID = "ck-gate6-20260727-run1-r2"


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: object) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def build() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    sequence = 0
    for scenario_index, scenario in enumerate(SCENARIOS):
        rotation = scenario_index % len(METHODS)
        methods = METHODS[rotation:] + METHODS[:rotation]
        for repetition in (1, 2, 3):
            for execution_order, method in enumerate(methods, 1):
                sequence += 1
                row = {
                    "sequence": sequence,
                    "scenario_class": scenario,
                    "repetition": repetition,
                    "method": method,
                    "execution_order": execution_order,
                    "receipt_name": f"{sequence:03d}--{scenario}--r{repetition}--{method}.json",
                }
                row["row_sha256"] = digest(row)
                rows.append(row)
    manifest: dict[str, object] = {
        "version": "hardening-gate6-execution-manifest-v1",
        "execution_revision": "R2",
        "campaign_id": CAMPAIGN_ID,
        "candidate_commit": CANDIDATE,
        "evidence_mode": "MEASURED_GATE6",
        "scenario_classes": list(SCENARIOS),
        "methods": list(METHODS),
        "repetitions": [1, 2, 3],
        "rotation_rule": "scenario_index_mod_3_as_frozen_by_gate5_run_smoke",
        "recovery_budget_seconds": 180,
        "row_count": len(rows),
        "rows": rows,
    }
    manifest["manifest_sha256"] = digest(manifest)
    return manifest


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    manifest = build()
    atomic_write(args.output.resolve(), canonical(manifest))
    print(canonical({"status": "GREEN", "manifest_sha256":
                     manifest["manifest_sha256"], "rows": 54}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
