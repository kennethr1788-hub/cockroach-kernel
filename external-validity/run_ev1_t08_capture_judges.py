#!/usr/bin/env python3
"""Run and validate GLM 5.2 and AGY over the frozen EV1-T08 packet."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / ".ev1-runtime" / "EV1-T08" / "control"
PACKET = CONTROL / "EV1_T08_CAPTURE_ONLY_PREFLIGHT_PACKET_R1.md"
BODY = CONTROL / "EV1_T08_CAPTURE_ONLY_REVIEW_BODY_R1.md"
GLM_RAW = CONTROL / "EV1_T08_CAPTURE_ONLY_R1_GLM_RAW.txt"
AGY_RAW = CONTROL / "EV1_T08_CAPTURE_ONLY_R1_AGY_RAW.txt"
RECEIPT = CONTROL / "CAPTURE_ONLY_JUDGE_RECEIPT_R1.json"
GLM = Path("/Users/kennethruedas/.local/bin/glm-zai")
AGY = Path("/Users/kennethruedas/.local/bin/agy-judge")
GLM_SHA256 = "0b94755754de89557ffb9d00b45b8d8fef6578614d00563db2320e940f83748f"
AGY_SHA256 = "e90a7eca1526dd31b522fdbcb1b52e0083c93a0984e4d2f4edf8bde9eb0dd716"


class JudgeError(RuntimeError):
    pass


def digest(value: bytes | Path) -> str:
    raw = value.read_bytes() if isinstance(value, Path) else value
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def atomic(path: Path, raw: bytes) -> None:
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


def run(command: list[str], *, stdin: bytes | None = None, env: dict[str, str] | None = None) -> tuple[int, bytes]:
    completed = subprocess.run(command, cwd=ROOT, env=env, input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=900)
    return completed.returncode, completed.stdout + completed.stderr


def review_content_sha256() -> str:
    header = PACKET.read_text().splitlines()[0]
    prefix = "REVIEW_CONTENT_SHA256: "
    if not header.startswith(prefix):
        raise JudgeError("PACKET_HEADER_MISSING")
    value = header.removeprefix(prefix)
    if value != digest(BODY):
        raise JudgeError("PACKET_BODY_HASH_MISMATCH")
    return value


def validate_glm(raw: bytes, content_sha256: str) -> None:
    text = raw.decode("utf-8", "strict")
    required = (
        r"glm-zai:\s*served by glm-5\.2",
        rf"REVIEW_CONTENT_SHA256[^\n]*{content_sha256}",
        r"RECUSAL_STATUS[^\n]*NOT_RECUSED",
        r"VERDICT[^\n]*GREEN",
        r"CONCRETE_BLOCKERS[^\n]*NONE",
        r"EVIDENCE_GAPS[^\n]*NONE",
    )
    if any(re.search(pattern, text, re.IGNORECASE) is None for pattern in required):
        raise JudgeError("GLM_OUTPUT_CONTRACT_FAILED")


def validate_agy(raw: bytes, packet_sha256: str) -> None:
    text = raw.decode("utf-8", "strict")
    required = (
        f"PACKET_SHA256: {packet_sha256}",
        "AGY_VERDICT: GREEN",
        "RECUSAL_CHECK: clear",
        "BLOCKERS:\n- NONE",
        "EVIDENCE_GAPS:\n- NONE",
        "provider execution bound:",
    )
    if any(item not in text for item in required):
        raise JudgeError("AGY_OUTPUT_CONTRACT_FAILED")


def main() -> int:
    if RECEIPT.exists() or GLM_RAW.exists() or AGY_RAW.exists():
        raise JudgeError("T08_JUDGE_RUN_ALREADY_STARTED")
    if digest(GLM) != GLM_SHA256 or digest(AGY) != AGY_SHA256:
        raise JudgeError("JUDGE_WRAPPER_DRIFT")
    packet_sha256 = digest(PACKET)
    content_sha256 = review_content_sha256()
    packet_raw = PACKET.read_bytes()
    glm_env = os.environ.copy()
    glm_env.update({
        "GLM_ZAI_MODEL": "glm-5.2",
        "GLM_ZAI_PRIMARY_RETRIES": "0",
        "GLM_ZAI_DISABLE_FALLBACK": "1",
        "GLM_ZAI_VERIFY_MODEL": "glm-5.2",
        "GLM_ZAI_REPORT_MODEL": "1",
        "GLM_ZAI_MAX_TOKENS": "16384",
    })
    glm_exit, glm_raw = run([str(GLM)], stdin=packet_raw, env=glm_env)
    atomic(GLM_RAW, glm_raw)
    if glm_exit != 0:
        raise JudgeError(f"GLM_PROCESS_FAILED:{glm_exit}")
    validate_glm(glm_raw, content_sha256)
    agy_exit, agy_raw = run([str(AGY), "--packet", str(PACKET), "--timeout", "600"])
    atomic(AGY_RAW, agy_raw)
    if agy_exit != 0:
        raise JudgeError(f"AGY_PROCESS_FAILED:{agy_exit}")
    validate_agy(agy_raw, packet_sha256)
    body = {
        "version": "ev1-t08-capture-only-judge-receipt-v1",
        "status": "EV1_T08_CAPTURE_ONLY_R1_JUDGES_GREEN",
        "task_id": "EV1-T08",
        "local_capture_packet_sha256": packet_sha256,
        "review_content_sha256": content_sha256,
        "glm_wrapper_sha256": GLM_SHA256,
        "glm_raw_sha256": digest(GLM_RAW),
        "glm_verdict": "GREEN",
        "agy_wrapper_sha256": AGY_SHA256,
        "agy_raw_sha256": digest(AGY_RAW),
        "agy_verdict": "GREEN",
        "same_packet": True,
        "recusal_clear": True,
        "concrete_blockers": [],
        "evidence_gaps": [],
        "utc_recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    receipt_hash = digest(canonical(body))
    atomic(RECEIPT, canonical(dict(body, receipt_sha256=receipt_hash)) + b"\n")
    print(canonical({"agy_raw_sha256": digest(AGY_RAW), "glm_raw_sha256": digest(GLM_RAW), "local_capture_packet_sha256": packet_sha256, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
