#!/usr/bin/env python3
"""Run GLM 5.2 and AGY over the frozen EV1 aggregate R2 packet."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".ev1-runtime" / "EV1-AGGREGATE"
PACKET = OUT / "EV1_AGGREGATE_REVIEW_PACKET_R2.md"
GLM_RAW = OUT / "EV1_AGGREGATE_GLM_RAW_R1.txt"
AGY_RAW = OUT / "EV1_AGGREGATE_AGY_RAW_R1.txt"
RECEIPT = OUT / "EV1_AGGREGATE_JUDGE_RECEIPT_R1.json"
PACKET_SHA256 = "bcf2c335d6e2b735bc781f85e17f4e823ff0518f79ae4897d8c45fecd7adc6e6"
REVIEW_CONTENT_SHA256 = "73b0a764924ae787ed30f59742aaaf92fc78a665fea0913935f30572975c4bb3"
MANIFEST_SHA256 = "080e8e2d4e944e2466430681b2e91373d5e7d7087eea2dffa6dc7fc701ed6f4a"
GLM = Path("/Users/kennethruedas/.local/bin/glm-zai")
AGY = Path("/Users/kennethruedas/.local/bin/agy-judge")
GLM_SHA256 = "0b94755754de89557ffb9d00b45b8d8fef6578614d00563db2320e940f83748f"
AGY_SHA256 = "e90a7eca1526dd31b522fdbcb1b52e0083c93a0984e4d2f4edf8bde9eb0dd716"


class JudgeError(RuntimeError):
    pass


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, raw: bytes) -> None:
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


def invoke(command: list[str], *, input_bytes: bytes | None = None, env: dict[str, str] | None = None) -> tuple[int, bytes]:
    completed = subprocess.run(command, cwd=ROOT, env=env, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=900, check=False)
    return completed.returncode, completed.stdout + completed.stderr


def label(pattern: str) -> str:
    return rf"\**`?{pattern}`?\**\s*:\s*"


def validate_glm(raw: bytes) -> None:
    text = raw.decode("utf-8", "strict")
    required = (
        r"glm-zai:\s*served by glm-5\.2",
        label(r"REVIEW[- _]CONTENT[- _]SHA(?:-256|256)") + rf"`?{REVIEW_CONTENT_SHA256}`?",
        label("VERDICT") + r"`?GREEN`?",
        label("OUTCOME[- _]ACCOUNTING") + r"`?SUPPORTED`?",
        label("METRICS") + r"`?SUPPORTED`?",
        label("LIMITATIONS") + r"`?SUPPORTED`?",
        label("CLAIM[- _]ALLOWED") + r"`?SUPPORTED`?",
    )
    if any(not re.search(pattern, text, re.IGNORECASE) for pattern in required):
        raise JudgeError("GLM_AGGREGATE_OUTPUT_CONTRACT_FAILED")
    for heading in ("BLOCKERS", "EVIDENCE[- _]GAPS"):
        section = re.search(label(heading) + r"(.{0,240})", text, re.IGNORECASE | re.DOTALL)
        if section is None or not re.search(r"\b(?:none|\[\])\b", section.group(1), re.IGNORECASE):
            raise JudgeError(f"GLM_AGGREGATE_{heading}_NOT_EMPTY")
    if not (
        re.search(r"12/12.{0,220}(?:not supported|blocked|prohibited|reject)", text, re.IGNORECASE | re.DOTALL)
        or re.search(r"(?:not supported|blocked|prohibited|reject).{0,220}12/12", text, re.IGNORECASE | re.DOTALL)
    ):
        raise JudgeError("GLM_UNQUALIFIED_DENOMINATOR_REJECTION_MISSING")
    recusal = re.search(label("RECUSAL(?:[- _]STATUS)?") + r"(.+)", text, re.IGNORECASE)
    if recusal is None or re.match(r"\s*`?(?:required|recusal_required|recuse)\b", recusal.group(1), re.IGNORECASE):
        raise JudgeError("GLM_RECUSAL_NOT_CLEAR")


def validate_agy(raw: bytes) -> None:
    text = raw.decode("utf-8", "strict")
    required = (
        f"PACKET_SHA256: {PACKET_SHA256}",
        "AGY_VERDICT: GREEN",
        "RECUSAL_CHECK: clear",
        "BLOCKERS:\n- NONE",
        "EVIDENCE_GAPS:\n- NONE",
        "provider execution bound:",
    )
    if any(item not in text for item in required):
        raise JudgeError("AGY_AGGREGATE_OUTPUT_CONTRACT_FAILED")


def main() -> int:
    if GLM_RAW.exists() or AGY_RAW.exists() or RECEIPT.exists():
        raise JudgeError("AGGREGATE_JUDGE_OUTPUT_ALREADY_EXISTS")
    if digest(PACKET) != PACKET_SHA256 or digest(OUT / "EV1_AGGREGATE_MANIFEST_R2.json") != MANIFEST_SHA256:
        raise JudgeError("AGGREGATE_PACKET_OR_MANIFEST_DRIFT")
    if digest(GLM) != GLM_SHA256 or digest(AGY) != AGY_SHA256:
        raise JudgeError("JUDGE_WRAPPER_DRIFT")
    environment = os.environ.copy()
    environment.update({
        "GLM_ZAI_MODEL": "glm-5.2",
        "GLM_ZAI_PRIMARY_RETRIES": "0",
        "GLM_ZAI_DISABLE_FALLBACK": "1",
        "GLM_ZAI_VERIFY_MODEL": "glm-5.2",
        "GLM_ZAI_REPORT_MODEL": "1",
        "GLM_ZAI_MAX_TOKENS": "16384",
    })
    glm_exit, glm_raw = invoke([str(GLM)], input_bytes=PACKET.read_bytes(), env=environment)
    atomic_write(GLM_RAW, glm_raw)
    if glm_exit != 0:
        raise JudgeError(f"GLM_PROCESS_FAILED:{glm_exit}")
    validate_glm(glm_raw)
    agy_exit, agy_raw = invoke([str(AGY), "--packet", str(PACKET), "--timeout", "600"])
    atomic_write(AGY_RAW, agy_raw)
    if agy_exit != 0:
        raise JudgeError(f"AGY_PROCESS_FAILED:{agy_exit}")
    validate_agy(agy_raw)
    body = {
        "version": "ev1-aggregate-judge-receipt-v1",
        "status": "EV1_AGGREGATE_INDEPENDENT_REVIEW_GREEN",
        "packet_sha256": PACKET_SHA256,
        "review_content_sha256": REVIEW_CONTENT_SHA256,
        "manifest_file_sha256": MANIFEST_SHA256,
        "glm_model": "glm-5.2",
        "glm_verdict": "GREEN",
        "glm_raw_sha256": digest(GLM_RAW),
        "agy_route": "Gemini 3.1 Pro (High)",
        "agy_verdict": "GREEN",
        "agy_raw_sha256": digest(AGY_RAW),
        "same_packet": True,
        "recusal_clear": True,
        "blockers": [],
        "evidence_gaps": [],
        "unqualified_12_of_12_claim_rejected": True,
    }
    receipt_hash = hashlib.sha256(canonical(body)).hexdigest()
    raw = canonical(dict(body, receipt_sha256=receipt_hash)) + b"\n"
    atomic_write(RECEIPT, raw)
    print(canonical({"agy_raw_sha256": digest(AGY_RAW), "file_sha256": digest(RECEIPT), "glm_raw_sha256": digest(GLM_RAW), "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
