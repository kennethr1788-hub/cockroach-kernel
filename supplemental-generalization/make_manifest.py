#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


PROFILES = ("small", "medium", "large")
SCENARIOS = ("committed-only", "committed-plus-uncommitted", "complete-loss",
             "partial-loss", "conflicting-stale", "clean-control")
METHODS = ("ordinary-git", "git-plus-restic-0.19.0", "product")
CANDIDATE = "8718fbecc2b145ff36ce8c3ed655e92b5906aeab"


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()


def digest(value: object) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def build(campaign_id: str) -> dict[str, object]:
    rows = []
    sequence = 0
    for profile_index, profile in enumerate(PROFILES):
        for scenario_index, scenario in enumerate(SCENARIOS):
            rotation = (profile_index + scenario_index) % 3
            ordered = METHODS[rotation:] + METHODS[:rotation]
            for repetition in (1, 2):
                for order, method in enumerate(ordered, 1):
                    sequence += 1
                    row = {"sequence": sequence, "profile": profile,
                           "scenario": scenario, "repetition": repetition,
                           "method": method, "execution_order": order,
                           "receipt_name": f"{sequence:03d}--{profile}--{scenario}--r{repetition}--{method}.json"}
                    row["row_sha256"] = digest(row)
                    rows.append(row)
    manifest = {"version": "supplemental-generalization-manifest-v1",
                "campaign_id": campaign_id, "candidate_commit": CANDIDATE,
                "profiles": list(PROFILES), "scenarios": list(SCENARIOS),
                "methods": list(METHODS), "repetitions": [1, 2],
                "row_count": len(rows), "rows": rows}
    manifest["manifest_sha256"] = digest(manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--campaign-id", required=True)
    args = parser.parse_args()
    value = build(args.campaign_id)
    raw = canonical(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_bytes(raw)
    os.replace(temporary, args.output)
    print(canonical({"status": "GREEN", "rows": len(value["rows"]),
                     "manifest_sha256": value["manifest_sha256"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
