#!/usr/bin/env python3
"""Mechanically compose the byte-complete hidden-campaign review packet."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "FRESH_CONTEXT_BLACK_BOX_HIDDEN_CAMPAIGN_AUTHORIZATION_R1.md",
    "FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_RAW_R1.txt",
    "FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_RECEIPT_R1.md",
    "FRESH_CONTEXT_BLACK_BOX_HIDDEN_ROUTE_AMENDMENT_R2.md",
    "FRESH_CONTEXT_BLACK_BOX_HIDDEN_ROUTE_PREFLIGHT_R2.md",
    "FRESH_CONTEXT_BLACK_BOX_PLAN_R3.md",
    "FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_STATUS_R3.md",
    "FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_GLM_RECEIPT_R3B.md",
    "fresh-context-black-box/r3_actor_response.schema.json",
    "fresh-context-black-box/r3_hidden_campaign.py",
    "fresh-context-black-box/test_r3_hidden_campaign.py",
)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def build(commit: str) -> bytes:
    header = (
        "# Hidden Black-Box Campaign Execution Preflight Packet R2\n\n"
        "- TARGET: authorize seed commitment then exactly 18 fresh synthetic local actor invocations\n"
        f"- CONTROLLER_COMMIT: {commit}\n"
        "- PRODUCT_CANDIDATE: 1c483b1930e629c9ecb6d73418b9554897dc08ad\n"
        "- R3_PREFLIGHT_PACKET_SHA256: 2a273eabffa107e0056c512dcc10b6f34398220fe97c949924552e9843bfb8f0\n"
        "- R1_EXECUTION_PACKET_SHA256: ae17bfd313163575a315a60a8048e16ff35345dcf5f018a3c50842c50871877e\n"
        "- R1_JUDGE_RESULT: BLOCKED and preserved\n"
        "- ACTOR_ROUTE: local Ollama / qwen2.5-coder:7b / exact digest verified\n"
        "- EXTERNAL_EGRESS: none\n"
        "- HIDDEN_SEED_CREATED: NO\n"
        "- HIDDEN_EXECUTIONS: 0\n"
        "- REVIEW_AUTHORITY: verdict only; no edits, tools, seed, execution, or public authority\n"
    ).encode()
    chunks = [header]
    for relative in FILES:
        raw = (ROOT / relative).read_bytes()
        chunks.append(
            (
                f"\n\n---\n\n## FILE: {relative}\n\n"
                f"- BYTE_LENGTH: {len(raw)}\n"
                f"- SHA256: {sha256(raw)}\n\n"
                "```text\n"
            ).encode()
        )
        chunks.append(raw)
        if not raw.endswith(b"\n"):
            chunks.append(b"\n")
        chunks.append(b"```\n")
    return b"".join(chunks)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = build(args.commit)
    if len(raw) >= 262_144:
        raise SystemExit(f"packet too large: {len(raw)}")
    args.output.write_bytes(raw)
    print(f"{sha256(raw)}  {args.output}")
    print(f"bytes={len(raw)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
