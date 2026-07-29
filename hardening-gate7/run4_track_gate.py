#!/usr/bin/env python3
"""Authorize Run 4 Track 2 only after sealed Track 1 and clean Track 3."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any


CAMPAIGN_RE = re.compile(r"^ck-g7r4-[A-Za-z0-9-]+$")
EXPECTED_COUNTS = [2000, 20000, 4000, 20000]


class TrackGateError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(raw: bytes | Any) -> str:
    return hashlib.sha256(raw if isinstance(raw, bytes) else canonical(raw)).hexdigest()


def read(path: Path) -> tuple[dict[str, Any], str]:
    if path.is_symlink() or not path.is_file():
        raise TrackGateError("INPUT_INVALID:" + path.name)
    raw = path.read_bytes()
    return json.loads(raw), digest(raw)


def receipt_hash(value: dict[str, Any], field: str) -> None:
    body = {key: item for key, item in value.items() if key != field}
    if value.get(field) != digest(body):
        raise TrackGateError("RECEIPT_HASH_INVALID")


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise TrackGateError("OUTPUT_EXISTS")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(canonical(value))
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


def evaluate(campaign_id: str, aggregate_path: Path, custody_path: Path,
             terminal_path: Path, cleanup_path: Path, result_path: Path,
             output: Path) -> dict[str, Any]:
    if not CAMPAIGN_RE.fullmatch(campaign_id):
        raise TrackGateError("CAMPAIGN_ID_INVALID")
    aggregate, aggregate_file_hash = read(aggregate_path)
    custody, custody_file_hash = read(custody_path)
    terminal, terminal_file_hash = read(terminal_path)
    cleanup, cleanup_file_hash = read(cleanup_path)
    result, result_file_hash = read(result_path)
    receipt_hash(aggregate, "aggregate_sha256")
    receipt_hash(custody, "receipt_sha256")
    receipt_hash(terminal, "receipt_sha256")
    receipt_hash(cleanup, "receipt_sha256")
    receipt_hash(result, "result_sha256")
    if not (
        aggregate.get("green") is True
        and aggregate.get("pass_count") == 84
        and aggregate.get("scored_execution_count") == 84
        and aggregate.get("behavior_failure_count") == 0
        and aggregate.get("safety_failure_count") == 0
        and aggregate.get("false_promotions") == 0
        and aggregate.get("mutation_after_refusal_or_invalid") == 0
        and aggregate.get("residue_count") == 0
        and aggregate.get("post_reveal_tuning_events") == 0
    ):
        raise TrackGateError("TRACK1_NOT_GREEN")
    if not (
        custody.get("campaign_id") == campaign_id
        and custody.get("status") == "SEALED"
        and custody.get("archive_mode_after") == "0000"
        and custody.get("extracted_before_track2") is False
    ):
        raise TrackGateError("TRACK1_CUSTODY_INVALID")
    if terminal.get("status") != "GREEN" or cleanup.get("status") != "PASS":
        raise TrackGateError("TRACK3_TERMINAL_NOT_GREEN")
    if cleanup.get("residue_counts") != [0, 0, 0, 0]:
        raise TrackGateError("TRACK3_RESIDUE")
    if result.get("green") is not True or result.get("actual_counts") != EXPECTED_COUNTS:
        raise TrackGateError("TRACK3_RESULT_INVALID")
    if terminal.get("result_sha256") != result["result_sha256"]:
        raise TrackGateError("TRACK3_RESULT_LINK_INVALID")
    if terminal.get("cleanup_receipt_sha256") != cleanup["receipt_sha256"]:
        raise TrackGateError("TRACK3_CLEANUP_LINK_INVALID")
    if not str(aggregate.get("campaign_id", "")).startswith(campaign_id):
        raise TrackGateError("TRACK1_CAMPAIGN_LINK_INVALID")
    if not str(result.get("campaign_id", "")).startswith(campaign_id):
        raise TrackGateError("TRACK3_CAMPAIGN_LINK_INVALID")
    body = {
        "version": "hardening-gate7-run4-track2-start-gate-v1",
        "campaign_id": campaign_id,
        "track1_aggregate_file_sha256": aggregate_file_hash,
        "track1_custody_file_sha256": custody_file_hash,
        "track3_terminal_file_sha256": terminal_file_hash,
        "track3_cleanup_file_sha256": cleanup_file_hash,
        "track3_result_file_sha256": result_file_hash,
        "track1_execution_count": 84,
        "track3_actual_counts": EXPECTED_COUNTS,
        "track3_residue_counts": [0, 0, 0, 0],
        "database_heavy_tracks_overlap": False,
        "status": "TRACK2_START_AUTHORIZED",
    }
    marker = dict(body, receipt_sha256=digest(body))
    atomic_write(output.resolve(), marker)
    return marker


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--track1-aggregate", type=Path, required=True)
    parser.add_argument("--track1-custody", type=Path, required=True)
    parser.add_argument("--track3-terminal", type=Path, required=True)
    parser.add_argument("--track3-cleanup", type=Path, required=True)
    parser.add_argument("--track3-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    marker = evaluate(
        args.campaign_id, args.track1_aggregate, args.track1_custody,
        args.track3_terminal, args.track3_cleanup, args.track3_result, args.output,
    )
    print(canonical(marker).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
