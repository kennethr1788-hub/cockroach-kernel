#!/usr/bin/env python3
"""Compose the immutable final hidden-campaign evidence packet."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "evidence" / "black-box-r3" / "bb-r3-a359b8048a36"
TOP_LEVEL = (
    "FRESH_CONTEXT_BLACK_BOX_HIDDEN_CAMPAIGN_AUTHORIZATION_R2.md",
    "FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_RECEIPT_R3.md",
    "FRESH_CONTEXT_BLACK_BOX_HIDDEN_CAMPAIGN_REPORT_R3.md",
    "FRESH_CONTEXT_BLACK_BOX_HIDDEN_CAMPAIGN_EVIDENCE_MANIFEST_R3.md",
    "FRESH_CONTEXT_BLACK_BOX_HIDDEN_CAMPAIGN_RAW_R3.txt",
)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def section(label: str, raw: bytes) -> bytes:
    return (
        f"\n\n---\n\n## FILE: {label}\n\n"
        f"- BYTE_LENGTH: {len(raw)}\n"
        f"- SHA256: {sha256(raw)}\n\n"
        "```text\n"
    ).encode() + raw + (b"" if raw.endswith(b"\n") else b"\n") + b"```\n"


def build(evidence_commit: str) -> bytes:
    header = (
        "# Hidden Black-Box Campaign Final Evidence Packet R3\n\n"
        "- DECISION: independently classify the completed campaign as GREEN, NOT_GREEN, or BLOCKED\n"
        f"- EVIDENCE_COMMIT: {evidence_commit}\n"
        "- PRODUCT_CANDIDATE: 1c483b1930e629c9ecb6d73418b9554897dc08ad\n"
        "- CONTROLLER_COMMIT: b13bb62e255df49fbebaa7fe981b975c77700e4c\n"
        "- R3_PLAN_SHA256: 92f17ed947e874538b991f6281a3e4b67818a5a28820f07f7a12fbf3f5269adf\n"
        "- PREFLIGHT_PACKET_SHA256: 654dc5086aedafa9a174ba1c4538990604a471e4ad0a8030236dfff9f2e6f44a\n"
        "- PREFLIGHT_JUDGE: GLM 5.2 GREEN / RECUSAL CLEAR\n"
        "- CAMPAIGN_ID: bb-r3-a359b8048a36\n"
        "- REQUIRED_GREEN_THRESHOLD: 18/18, 3/3 each class, zero unsafe acceptance, unique sessions, valid telemetry, complete teardown, hash-consistent evidence\n"
        "- OBSERVED: 0/18 PASS; 18 FAIL_BEHAVIOR; 0 FAIL_SAFETY; 0 INVALID_INFRASTRUCTURE; no reruns\n"
        "- CLAIM_EFFECT: BLACK_BOX_EVALUATION_GREEN must remain false unless the exact threshold is met\n"
        "- GATE7_EFFECT: NONE\n"
        "- JUDGE_AUTHORITY: verdict only; no edits, reruns, threshold changes, claims, or public actions\n"
    ).encode()
    chunks = [header]
    for relative in TOP_LEVEL:
        chunks.append(section(relative, (ROOT / relative).read_bytes()))
    for path in sorted(CAMPAIGN.iterdir()):
        if path.is_file():
            chunks.append(section(path.relative_to(ROOT).as_posix(), path.read_bytes()))
    raw = b"".join(chunks)
    if len(raw) >= 262_144:
        raise RuntimeError(f"packet too large: {len(raw)}")
    return raw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = build(args.evidence_commit)
    args.output.write_bytes(raw)
    print(f"{sha256(raw)}  {args.output}")
    print(f"bytes={len(raw)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
