#!/usr/bin/env python3
"""Mechanically assemble the exact sanitized S3 preflight review packet."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = Path(
    "/Users/kennethruedas/Documents/Codex/2026-07-18/"
    "read-and-execute-the-prompt-afterlife/"
    "COCKROACH_KERNEL_P9_COMPLETION_S3_RETRY_EXECUTION_PROMPT_20260726_R1.md"
)
OUTPUT = ROOT / "S3_PREFLIGHT_PACKET_R10.md"

FILES = [
    ROOT / "S3_FEATURE_FREEZE_RECEIPT_R1.md",
    ROOT / "S3_BUILDER_CONTINUITY_RECEIPT_R1.md",
    ROOT / "S3_CONTRACT_R1.md",
    ROOT / "S3_EXECUTION_WIRING_R1.md",
    ROOT / "S3_PREFLIGHT_REPAIR_RECEIPT_R10.md",
    ROOT / "S3_ATTEMPT_A02_RECEIPT.md",
    ROOT / "S3_EXECUTION_SCHEDULE_R1.json",
    ROOT / "S3_RESOURCE_ALLOWLIST_R1.json",
    ROOT / "S3_THRESHOLDS_R1.json",
    ROOT / "S3_RUNTIME_HASHES_R1.json",
    ROOT / "S3_STATUS.md",
    ROOT / "S3_PREFLIGHT_CHECKPOINT_R10.md",
    ROOT / "P9_FINAL_JUDGE_RECEIPT_R1.md",
    ROOT / "s2-soak/lifecycle_guard.py",
    ROOT / "s2-soak/run_soak.py",
    ROOT / "p4-verifier/verifier.py",
    ROOT / "p9-cloud/live_completion.py",
    ROOT / "p9-cloud/records.py",
    ROOT / "s3-soak/protocol.py",
    ROOT / "s3-soak/worker.py",
    ROOT / "s3-soak/host_coordinator.py",
    ROOT / "s3-soak/cloud_adapter.py",
    ROOT / "s3-soak/remote_bridge.py",
    ROOT / "s3-soak/coordinator_guard.py",
    ROOT / "s3-soak/freeze_evidence_manifest.py",
    ROOT / "s3-soak/prove_coordinator_guard.py",
    ROOT / "s3-soak/test_protocol.py",
    PROMPT,
]


def label(path: Path) -> str:
    if path == PROMPT:
        return "AUTHORIZATION_PROMPT"
    return str(path.relative_to(ROOT))


def main() -> int:
    chunks = [
        b"# S3 Preflight Packet R10\n\n",
        b"Decision requested: return GREEN only if the frozen S3 design can "
        b"safely create one bounded credential-free RunPod worker and begin "
        b"the one authorized release soak. Otherwise return NOT_GREEN with "
        b"evidence-backed findings. Do not author code or prescribe repairs.\n\n",
        b"The packet is sanitized. Judges have no tools, shell, repository, "
        b"browser, credential, cloud, deployment, or public-action authority.\n",
    ]
    for path in FILES:
        raw = path.read_bytes()
        if b"\x00" in raw:
            raise SystemExit(f"NUL byte in {path}")
        raw = raw.replace(b"/Users/kennethruedas", b"<LOCAL_ROOT>")
        chunks.extend([
            b"\n\n---\n\n## FILE: " + label(path).encode("utf-8") + b"\n\n",
            b"```text\n",
            raw,
            b"\n```\n",
        ])
    value = b"".join(chunks)
    if len(value) > 262_144:
        raise SystemExit(f"packet too large: {len(value)}")
    OUTPUT.write_bytes(value)
    print(f"{OUTPUT.name} {len(value)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
