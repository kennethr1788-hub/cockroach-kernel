#!/usr/bin/env python3
"""Build the byte-complete Gate 7 AWS-login orchestration amendment packet."""
from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess


BASE = Path(__file__).resolve().parents[1]
OUTPUT = BASE / "HARDENING_GATE7_AWS_LOGIN_REFRESH_PREFLIGHT_PACKET_R1.md"
PRIOR_PACKET_SHA256 = "4fd89d699dccd0d3e15451fab40435ad2e9b3f7300061ff8791913dc4b7ecf44"
CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
FILES = (
    BASE / "HARDENING_GATE7_AWS_LOGIN_REFRESH_AMENDMENT_R1.md",
    BASE / "HARDENING_GATE7_AWS_LOGIN_REFRESH_TEST_RECEIPT_R1.md",
    BASE / "HARDENING_GATE7_AWS_LOGIN_REFRESH_CLOUD_ADAPTER_REVIEW_R1.md",
    BASE / "HARDENING_GATE7_AWS_LOGIN_REFRESH_CODE_REVIEW_R1.md",
    BASE / "HARDENING_GATE7_A03_CAMPAIGN_READY_PRECHECK_RECEIPT_R1.md",
    BASE / "HARDENING_GATE7_REPAIRED_PREFLIGHT_JUDGE_RECEIPT_R2.md",
    BASE / ".hardening-runtime/gate7-r2/aws-login-provider-proof-a03.json",
    BASE / ".hardening-runtime/gate7-r2/live-readiness-after-refresh-a03.json",
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=BASE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("GIT_COMMAND_FAILED:" + sha(result.stdout))
    return result.stdout.decode("utf-8")


def main() -> int:
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("TRACKED_WORKTREE_NOT_CLEAN")
    head = git("rev-parse", "HEAD").strip()
    changed = git("diff", "--name-only", CANDIDATE, "--").splitlines()
    packet: list[str] = [
        "# Hardening Gate 7 AWS Login Refresh Preflight Packet R1\n",
        "## Decision requested\n",
        "GLM and AGY are independent, non-authoring, tool-disabled judges. Review "
        "only whether this narrow host-orchestration correction may replace the false "
        "static access-credential expiry check before A03 becomes CAMPAIGN_READY. "
        "Do not write code, direct implementation, predict the campaign outcome, or "
        "treat this preflight as measured evidence.\n",
        "Return GREEN only if the correction preserves the frozen product candidate, "
        "84-case semantics, live-track thresholds, credential separation, and fail-closed "
        "behavior, and if the real post-exchange 900-second provider probe is at least as "
        "strong as the intended session-margin gate.\n",
        "## Bindings\n",
        f"- `PACKET_VERSION`: `gate7-aws-login-refresh-preflight-r1`\n",
        f"- `PRODUCT_CANDIDATE`: `{CANDIDATE}`\n",
        f"- `ORCHESTRATION_HEAD`: `{head}`\n",
        f"- `PRIOR_PACKET_SHA256`: `{PRIOR_PACKET_SHA256}`\n",
        "- `PRIOR_JUDGES`: `GLM_5_2_GREEN; AGY_GEMINI_3_1_PRO_HIGH_GREEN; SAME_HASH; RECUSAL_CLEAR`\n",
        "- `REMOTE_BUNDLE_SHA256`: `b95c6b8e20ec30473676b8f2dbe7e128fdb78bfd33a72105131c51bf45634eb0`\n",
        "- `REMOTE_BUNDLE_FILES`: `87_OF_87_EXACT`\n",
        "- `POD_ID`: `xvxonfa5ck8wpq`\n",
        "- `HIDDEN_SEED_EXISTS`: `NO`\n",
        "- `MEASURED_EXECUTION_STARTED`: `NO`\n",
        "- `AWS_PRIMARY_DOC`: `https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html`\n",
        "- `AWS_SDK_DOC`: `https://docs.aws.amazon.com/sdkref/latest/guide/feature-login-credentials.html`\n",
        "## Candidate path classification\n",
        "The candidate commit remains immutable. Paths changed after it include prior "
        "harness/evidence work. This amendment changes only the four `s3-soak` host "
        "orchestration/test files embedded below; the already accepted remote payload "
        "contains only `s3-soak/protocol.py` and `s3-soak/worker.py`, neither changed.\n",
        "```text\n" + "\n".join(changed) + "\n```\n",
        "## Required judge output\n",
        "GLM returns exactly one JSON object with keys: `lane`, `model_identity`, "
        "`packet_sha256`, `verdict` (`GREEN|NOT_GREEN|RECUSAL_REQUIRED`), "
        "`recusal_clear` (boolean), `blocking_findings` (array), "
        "`non_blocking_risks` (array), and `summary`. AGY returns its wrapper-native "
        "validated fields: `PACKET_SHA256`, `AGY_VERDICT`, `BLOCKERS`, "
        "`NON_BLOCKING_RISKS`, `EVIDENCE_GAPS`, `RECUSAL_CHECK`, and "
        "`REQUIRED_RERUNS`. The out-of-band packet SHA-256 supplied by the caller "
        "must be copied exactly. Any implementation direction, tool request, or "
        "identity adoption invalidates the lane.\n",
    ]
    for path in FILES:
        raw = path.read_bytes()
        relative = path.relative_to(BASE)
        packet.extend((
            f"\n## FILE: {relative}\n",
            f"- `BYTES`: `{len(raw)}`\n",
            f"- `SHA256`: `{sha(raw)}`\n",
            "```text\n",
            raw.decode("utf-8"),
            "\n```\n",
        ))
    encoded = "".join(packet).encode("utf-8")
    if len(encoded) >= 262_144:
        raise RuntimeError(f"PACKET_TOO_LARGE:{len(encoded)}")
    OUTPUT.write_bytes(encoded)
    print(f"bytes={len(encoded)}")
    print(f"sha256={sha(encoded)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
