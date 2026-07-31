#!/usr/bin/env python3
"""Run both EV1-T12 judges over the corrected, byte-frozen R2 transport."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import run_ev1_t12 as T12


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / ".ev1-runtime" / "EV1-T12" / "control"
PACKET = CONTROL / "EV1_T12_EXECUTION_PREFLIGHT_PACKET_R2.md"
GLM_RAW = CONTROL / "EV1_T12_EXECUTION_PREFLIGHT_GLM_RAW_R2.txt"
AGY_RAW = CONTROL / "EV1_T12_EXECUTION_PREFLIGHT_AGY_RAW_R3.txt"
GATE = CONTROL / "INDEPENDENT_EXECUTION_GATE.json"
PACKET_SHA256 = "fdec4b7b77e0872349205537929a16bf5576cc3b5d69ce63796b5204bcb5243f"
REVIEW_CONTENT_SHA256 = "4a6e76150e5ee0a4610716fe6c108995b7264c2dc0e88ca76bea47f638bc2bf3"
GLM = Path("/Users/kennethruedas/.local/bin/glm-zai")
AGY = Path("/Users/kennethruedas/.local/bin/agy-judge")
GLM_SHA256 = "0b94755754de89557ffb9d00b45b8d8fef6578614d00563db2320e940f83748f"
AGY_SHA256 = "e90a7eca1526dd31b522fdbcb1b52e0083c93a0984e4d2f4edf8bde9eb0dd716"


class JudgeError(RuntimeError):
    pass


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
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=900,
        check=False,
    )
    return completed.returncode, completed.stdout + completed.stderr


def validate_glm(raw: bytes) -> None:
    text = raw.decode("utf-8", "strict")
    patterns = (
        r"glm-zai:\s*served by glm-5\.2",
        rf"review[- _]content(?:[- _]+sha-?256)?[\s\S]{{0,120}}{REVIEW_CONTENT_SHA256}",
        r"recusal(?:[- ]status|[- ]check)?[\s\S]{0,120}(?:NOT_RECUSED|not recused|clear)",
        r"(?:^|\n)#+\s*verdict\s*\n+[\s`*_-]*GREEN\b|verdict[^\n]*GREEN",
    )
    if any(not re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
        raise JudgeError("GLM_R2_OUTPUT_CONTRACT_FAILED")
    blockers = re.search(r"(?:concrete\s+)?blockers?[\s\S]{0,160}", text, re.IGNORECASE)
    gaps = re.search(r"evidence[- ]gaps?[\s\S]{0,160}", text, re.IGNORECASE)
    if blockers is None or not re.search(r"\b(?:none|\[\])\b", blockers.group(0), re.IGNORECASE):
        raise JudgeError("GLM_R2_BLOCKERS_NOT_EMPTY")
    if gaps is None or not re.search(r"\b(?:none|\[\])\b", gaps.group(0), re.IGNORECASE):
        raise JudgeError("GLM_R2_GAPS_NOT_EMPTY")


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
        raise JudgeError("AGY_R3_OUTPUT_CONTRACT_FAILED")


def main() -> int:
    if GLM_RAW.exists() or AGY_RAW.exists() or GATE.exists():
        raise JudgeError("R2_OUTPUT_ALREADY_EXISTS")
    if digest(PACKET) != PACKET_SHA256 or digest(GLM) != GLM_SHA256 or digest(AGY) != AGY_SHA256:
        raise JudgeError("R2_PACKET_OR_WRAPPER_DRIFT")

    environment = os.environ.copy()
    environment.update(
        {
            "GLM_ZAI_MODEL": "glm-5.2",
            "GLM_ZAI_PRIMARY_RETRIES": "0",
            "GLM_ZAI_DISABLE_FALLBACK": "1",
            "GLM_ZAI_VERIFY_MODEL": "glm-5.2",
            "GLM_ZAI_REPORT_MODEL": "1",
            "GLM_ZAI_MAX_TOKENS": "32768",
        }
    )
    glm_exit, glm_raw = invoke([str(GLM)], input_bytes=PACKET.read_bytes(), env=environment)
    atomic_write(GLM_RAW, glm_raw)
    if glm_exit != 0:
        raise JudgeError(f"GLM_R2_PROCESS_FAILED:{glm_exit}")
    validate_glm(glm_raw)

    agy_exit, agy_raw = invoke([str(AGY), "--packet", str(PACKET), "--timeout", "600"])
    atomic_write(AGY_RAW, agy_raw)
    if agy_exit != 0:
        raise JudgeError(f"AGY_R3_PROCESS_FAILED:{agy_exit}")
    validate_agy(agy_raw)

    body = {
        "version": "ev1-t12-independent-execution-gate-v2",
        "status": "EV1_T12_INDEPENDENT_EXECUTION_GATE_GREEN",
        "task_id": "EV1-T12",
        "packet_sha256": PACKET_SHA256,
        "review_content_sha256": REVIEW_CONTENT_SHA256,
        "runner_sha256": digest(ROOT / "external-validity" / "run_ev1_t12.py"),
        "capture_file_sha256": digest(CONTROL / "CAPTURE_RECEIPT.json"),
        "preflight_file_sha256": digest(CONTROL / "EXECUTION_PREFLIGHT_RECEIPT.json"),
        "glm_model": "glm-5.2",
        "glm_verdict": "GREEN",
        "glm_raw_sha256": digest(GLM_RAW),
        "agy_route": "Gemini 3.1 Pro (High)",
        "agy_verdict": "GREEN",
        "agy_raw_sha256": digest(AGY_RAW),
        "preserved_failed_agy_attempts": {
            "R1": digest(CONTROL / "EV1_T12_EXECUTION_PREFLIGHT_AGY_RAW_R1.txt"),
            "R2": digest(CONTROL / "EV1_T12_EXECUTION_PREFLIGHT_AGY_RAW_R2.txt"),
        },
        "transport_correction": "Removed conflicting inner instruction to return review-content hash; review body is byte-identical.",
        "same_packet": True,
        "recusal_clear": True,
        "deletion_started": False,
    }
    receipt_hash, file_hash = T12.atomic_record(GATE, body)
    print(
        T12.canonical(
            {
                "agy_raw_sha256": digest(AGY_RAW),
                "file_sha256": file_hash,
                "glm_raw_sha256": digest(GLM_RAW),
                "receipt_sha256": receipt_hash,
                "status": body["status"],
            }
        ).decode()
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
