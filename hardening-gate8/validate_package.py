#!/usr/bin/env python3
"""Mechanically validate the Gate 8 sanitized evidence package."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "evidence" / "gate8-public-r1"
MANIFEST = PUBLIC / "CLAIM_TO_EVIDENCE_MANIFEST_R1.json"
RECEIPT = ROOT / "HARDENING_GATE8_MECHANICAL_RECEIPT_R1.json"

PRIVATE_PATTERNS = (
    re.compile(rb"/Users/"),
    re.compile(rb"/home/[^\s/]+/"),
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"ASIA[0-9A-Z]{16}"),
    re.compile(rb"aws_secret_access_key\s*[:=]", re.I),
    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(rb"[A-Za-z0-9-]+\.(?:aws|us)-[a-z0-9-]+\.amazonaws\.com"),
    re.compile(rb"[A-Za-z0-9-]+\.cockroachlabs\.cloud"),
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    counters = {
        "contradictory_metrics": 0,
        "displayed_metrics_without_source_receipts": 0,
        "hash_mismatches": 0,
        "missing_referenced_artifacts": 0,
        "public_claims_without_evidence": 0,
        "public_package_credentials_private_paths_private_evidence": 0,
        "replay_live_ambiguity": 0,
    }
    findings: list[str] = []

    sources = {}
    for source in manifest.get("sources", []):
        source_id = source.get("source_id")
        raw_path = source.get("path", "")
        if not source_id or not raw_path or Path(raw_path).is_absolute() or ".." in Path(raw_path).parts:
            counters["missing_referenced_artifacts"] += 1
            findings.append(f"INVALID_SOURCE_PATH:{source_id}:{raw_path}")
            continue
        path = ROOT / raw_path
        if not path.is_file():
            counters["missing_referenced_artifacts"] += 1
            findings.append(f"MISSING_SOURCE:{source_id}:{raw_path}")
            continue
        actual = digest(path)
        if actual != source.get("sha256"):
            counters["hash_mismatches"] += 1
            findings.append(f"HASH_MISMATCH:{source_id}:{raw_path}:{actual}")
            continue
        sources[source_id] = source

    seen_metrics: dict[str, str] = {}
    accepted_modes = {"architecture", "live_synthetic", "local_synthetic", "measured_synthetic", "single_operator_live", "limitation"}
    for claim in manifest.get("claims", []):
        claim_id = claim.get("claim_id", "UNKNOWN")
        evidence_ids = claim.get("evidence_source_ids", [])
        if not claim.get("public_claim") or not evidence_ids or any(item not in sources for item in evidence_ids):
            counters["public_claims_without_evidence"] += 1
            findings.append(f"CLAIM_WITHOUT_EVIDENCE:{claim_id}")
        mode = claim.get("evidence_mode")
        if mode not in accepted_modes or not claim.get("live_replay_label") or not claim.get("limitations"):
            counters["replay_live_ambiguity"] += 1
            findings.append(f"AMBIGUOUS_EVIDENCE_MODE:{claim_id}:{mode}")
        for metric in claim.get("metrics", []):
            metric_id = metric.get("metric_id")
            source_id = metric.get("source_id")
            if not metric_id or source_id not in sources or "value" not in metric or not metric.get("test"):
                counters["displayed_metrics_without_source_receipts"] += 1
                findings.append(f"UNSOURCED_METRIC:{claim_id}:{metric_id}")
                continue
            encoded = json.dumps(metric["value"], sort_keys=True, separators=(",", ":"))
            if metric_id in seen_metrics and seen_metrics[metric_id] != encoded:
                counters["contradictory_metrics"] += 1
                findings.append(f"CONTRADICTORY_METRIC:{metric_id}")
            seen_metrics[metric_id] = encoded

    for path in sorted(PUBLIC.rglob("*")):
        if not path.is_file():
            continue
        data = path.read_bytes()
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(data):
                counters["public_package_credentials_private_paths_private_evidence"] += 1
                findings.append(f"PUBLIC_PRIVATE_PATTERN:{path.relative_to(ROOT)}:{pattern.pattern!r}")

    status = "GREEN" if all(value == 0 for value in counters.values()) else "BLOCKED"
    receipt = {
        "candidate_commit": manifest.get("product_candidate"),
        "claims": len(manifest.get("claims", [])),
        "counters": counters,
        "findings": findings,
        "manifest_sha256": digest(MANIFEST),
        "public_files": len([path for path in PUBLIC.rglob("*") if path.is_file()]),
        "status": status,
        "utc_created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "version": "hardening-gate8-mechanical-receipt-v1",
    }
    RECEIPT.write_bytes(canonical(receipt))
    print(canonical(receipt).decode("utf-8"), end="")
    return 0 if status == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
