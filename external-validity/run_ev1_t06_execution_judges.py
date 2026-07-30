#!/usr/bin/env python3
"""Run and validate the two frozen EV1-T06 pre-execution judge lanes."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / ".ev1-runtime" / "EV1-T06" / "control"
PACKET = CONTROL / "EV1_T06_EXECUTION_PREFLIGHT_PACKET_R1.md"
GLM_RAW = CONTROL / "EV1_T06_EXECUTION_PREFLIGHT_GLM_RAW_R3.txt"
AGY_RAW = CONTROL / "EV1_T06_EXECUTION_PREFLIGHT_AGY_RAW_R1.txt"
PACKET_SHA256 = "8f8aa8398fdff0d94898a942f7973bd4d3bf98df1be97e144e90dccf4fe6671f"
REVIEW_CONTENT_SHA256 = "e5ea458cde647a582de5a2a3c83b1e461a31ba3263268955dd5f0f1d405627b2"
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


def run(
    command: list[str], *, input_bytes: bytes | None = None, env: dict[str, str] | None = None
) -> tuple[int, bytes]:
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
    raw = completed.stdout + completed.stderr
    return completed.returncode, raw


def validate_glm(raw: bytes) -> None:
    text = raw.decode("utf-8", "strict")
    required_patterns = (
        r"glm-zai:\s*served by glm-5\.2",
        rf"review[- ]content\s+sha-256\**:\s*`?{REVIEW_CONTENT_SHA256}`?",
        r"recusal[- ]status\**:\s*`?NOT_RECUSED`?",
        r"verdict\**:\s*`?GREEN`?",
    )
    if any(not re.search(pattern, text, re.IGNORECASE) for pattern in required_patterns):
        raise JudgeError("GLM_OUTPUT_CONTRACT_FAILED")
    if not re.search(r"Concrete[- ]Blockers\**:\s*`?(?:None|NONE|\[\])`?", text, re.IGNORECASE):
        raise JudgeError("GLM_BLOCKERS_NOT_EMPTY")
    if not re.search(r"Evidence[- ]Gaps\**:\s*`?(?:None|NONE|\[\])`?", text, re.IGNORECASE):
        raise JudgeError("GLM_EVIDENCE_GAPS_NOT_EMPTY")


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
        raise JudgeError("AGY_OUTPUT_CONTRACT_FAILED")


def main() -> int:
    if AGY_RAW.exists():
        raise JudgeError("AGY_OUTPUT_ALREADY_EXISTS")
    if digest(PACKET) != PACKET_SHA256:
        raise JudgeError("PACKET_DRIFT")
    if digest(GLM) != GLM_SHA256 or digest(AGY) != AGY_SHA256:
        raise JudgeError("JUDGE_WRAPPER_DRIFT")
    packet_raw = PACKET.read_bytes()

    glm_env = os.environ.copy()
    glm_env.update(
        {
            "GLM_ZAI_MODEL": "glm-5.2",
            "GLM_ZAI_PRIMARY_RETRIES": "0",
            "GLM_ZAI_DISABLE_FALLBACK": "1",
            "GLM_ZAI_VERIFY_MODEL": "glm-5.2",
            "GLM_ZAI_REPORT_MODEL": "1",
            "GLM_ZAI_MAX_TOKENS": "8192",
        }
    )
    if GLM_RAW.exists():
        glm_raw = GLM_RAW.read_bytes()
    else:
        glm_exit, glm_raw = run([str(GLM)], input_bytes=packet_raw, env=glm_env)
        atomic_write(GLM_RAW, glm_raw)
        if glm_exit != 0:
            raise JudgeError(f"GLM_PROCESS_FAILED:{glm_exit}:{glm_raw[-1000:]!r}")
    validate_glm(glm_raw)

    agy_exit, agy_raw = run([str(AGY), "--packet", str(PACKET), "--timeout", "600"])
    atomic_write(AGY_RAW, agy_raw)
    if agy_exit != 0:
        raise JudgeError(f"AGY_PROCESS_FAILED:{agy_exit}:{agy_raw[-1000:]!r}")
    validate_agy(agy_raw)
    print(
        "GLM_5_2_GREEN AGY_GREEN "
        f"PACKET_SHA256={PACKET_SHA256} "
        f"GLM_RAW_SHA256={digest(GLM_RAW)} AGY_RAW_SHA256={digest(AGY_RAW)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
