#!/usr/bin/env python3
"""Validate and freeze one collision-safe public live Gate 7 canary."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any


BASE = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BASE / "s3-soak"))
import live_bulk_controller as bulk  # type: ignore  # noqa: E402
import cloud_adapter  # type: ignore  # noqa: E402

CAMPAIGN_RE = re.compile(r"^ck-g7r5-public-[A-Za-z0-9-]+$")
EXPECTED_COUNTS = [2000, 20000, 4000, 20000]


class CanaryError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: bytes | Any) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    path = path.resolve()
    if path.exists() or path.is_symlink():
        raise CanaryError("OUTPUT_EXISTS")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(canonical(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def read_json(path: Path) -> tuple[dict[str, Any], str]:
    if path.is_symlink() or not path.is_file():
        raise CanaryError("EVIDENCE_FILE_INVALID:" + path.name)
    raw = path.read_bytes()
    return json.loads(raw), digest(raw)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--generated-root", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not CAMPAIGN_RE.fullmatch(args.campaign_id):
        raise CanaryError("CAMPAIGN_ID_INVALID")
    generated = args.generated_root.resolve()
    evidence = args.evidence_root.resolve()
    terminal_link = bulk.validate_terminal_evidence(evidence)
    if terminal_link["status"] != "GREEN":
        raise CanaryError("TERMINAL_NOT_GREEN")
    manifest, manifest_file_hash = read_json(generated / "manifest.json")
    result, result_file_hash = read_json(evidence / "result.json")
    cleanup, cleanup_file_hash = read_json(evidence / "cleanup.json")
    terminal, terminal_file_hash = read_json(evidence / "terminal.json")
    journal_path = evidence / "journal.ndjson"
    journal_raw = journal_path.read_bytes()
    journal_rows = [json.loads(line) for line in journal_raw.splitlines() if line]
    expected_manifest_hash = digest({k: v for k, v in manifest.items()
                                     if k != "manifest_sha256"})
    if manifest.get("manifest_sha256") != expected_manifest_hash:
        raise CanaryError("MANIFEST_HASH_INVALID")
    if not (
        manifest.get("campaign_id") == args.campaign_id
        and manifest.get("counts", {}).get("vectors") == 20000
        and manifest.get("vector_digest_policy") ==
            "NON_UNIQUE_CONTENT_DIGEST_EXACT_ROW_LINKAGE"
        and manifest.get("unique_vector_ids") == 20000
        and manifest.get("unique_vector_linkages") == 20000
        and manifest.get("unique_vector_digests", 0) +
            manifest.get("vector_digest_collisions", -1) == 20000
        and manifest.get("cleanup_batch_count") == 107
    ):
        raise CanaryError("MANIFEST_SEMANTICS_INVALID")
    if not (
        result.get("green") is True
        and result.get("campaign_id") == args.campaign_id
        and result.get("actual_counts") == EXPECTED_COUNTS
        and result.get("query_count") == 200
        and result.get("cleanup_batches") == 107
        and result.get("residue_counts") == [0, 0, 0, 0]
        and result.get("configured_concurrency") == 4
        and result.get("observed_concurrency_max") == 4
        and result.get("credential_bytes_recorded") is False
        and result.get("worker_received_credentials") is False
    ):
        raise CanaryError("RESULT_SEMANTICS_INVALID")
    if cleanup.get("receipt_sha256") != terminal_link["cleanup_receipt_sha256"]:
        raise CanaryError("CLEANUP_LINK_INVALID")
    if terminal.get("receipt_sha256") != terminal_link["terminal_receipt_sha256"]:
        raise CanaryError("TERMINAL_LINK_INVALID")

    config = cloud_adapter._read_config(args.config.resolve())
    secret = bytearray()
    try:
        secret.extend(cloud_adapter._password(config))
        sql_env = cloud_adapter._sql_env(config, bytes(secret))
        direct_raw, direct_ms = cloud_adapter._sql(
            config, sql_env, execute=bulk.campaign_count_sql(
                bulk.campaign_prefix(args.campaign_id)
            ), timeout=120,
        )
        direct_counts = list(bulk.parse_count_row(direct_raw))
    finally:
        if "sql_env" in locals():
            sql_env.pop("PGPASSWORD", None)
        for index in range(len(secret)):
            secret[index] = 0
    if direct_counts != [0, 0, 0, 0]:
        raise CanaryError("DIRECT_RESIDUE_NONZERO")
    body = {
        "version": "hardening-gate7-run5-public-canary-v1",
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "campaign_id": args.campaign_id,
        "measured_hidden_campaign": False,
        "runpod_worker_created": False,
        "manifest_sha256": manifest["manifest_sha256"],
        "manifest_file_sha256": manifest_file_hash,
        "result_sha256": result["result_sha256"],
        "result_file_sha256": result_file_hash,
        "cleanup_receipt_sha256": cleanup["receipt_sha256"],
        "cleanup_file_sha256": cleanup_file_hash,
        "terminal_receipt_sha256": terminal["receipt_sha256"],
        "terminal_file_sha256": terminal_file_hash,
        "journal_file_sha256": digest(journal_raw),
        "journal_records": len(journal_rows),
        "actual_counts": result["actual_counts"],
        "vector_queries": result["query_count"],
        "unique_vector_digests": manifest["unique_vector_digests"],
        "vector_digest_collisions": manifest["vector_digest_collisions"],
        "max_vector_digest_multiplicity": manifest["max_vector_digest_multiplicity"],
        "unique_vector_ids": manifest["unique_vector_ids"],
        "unique_vector_linkages": manifest["unique_vector_linkages"],
        "serialization_retries": result["serialization_retries"],
        "query_latency_ms": result["query_latency_ms"],
        "insert_total_ms": result["insert_total_ms"],
        "cleanup_batches": result["cleanup_batches"],
        "cleanup_retries": result["cleanup_retries"],
        "cleanup_ms": result["cleanup_ms"],
        "canonical_residue_counts": result["residue_counts"],
        "direct_residue_counts": direct_counts,
        "direct_residue_output_sha256": digest(direct_raw),
        "direct_residue_ms": direct_ms,
        "credential_bytes_recorded": False,
        "status": "RUN5_PUBLIC_FULL_CANARY_GREEN",
    }
    receipt = dict(body, receipt_sha256=digest(body))
    atomic_write(args.output, receipt)
    print(canonical({"status": receipt["status"],
                     "receipt_sha256": receipt["receipt_sha256"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
