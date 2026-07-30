#!/usr/bin/env python3
"""Run and validate the frozen EV1-T09 pre-execution judge lanes."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / ".ev1-runtime" / "EV1-T09" / "control"
PACKET = CONTROL / "EV1_T09_EXECUTION_PREFLIGHT_PACKET_R1.md"
GLM_INVALID_R1 = CONTROL / "EV1_T09_EXECUTION_PREFLIGHT_GLM_RAW_R1.txt"
GLM_INVALID_R1_SHA256 = "fe590c1b1c98947e0c4331ea877ef623c98a631974c0775f7ac9031d03b816b1"
GLM_RAW = CONTROL / "EV1_T09_EXECUTION_PREFLIGHT_GLM_RAW_R2.txt"
GLM_RAW_SHA256 = "e05b962186fadbef8d5657065f0bbd1b0c071b689443f45e729d936ded15883b"
AGY_RAW = CONTROL / "EV1_T09_EXECUTION_PREFLIGHT_AGY_RAW_R1.txt"
PACKET_SHA256 = "341a54c7528213f76896237b2387dd1dfdf2845fb472ebac2929a7fdea1b6f50"
REVIEW_CONTENT_SHA256 = "3e8bea049a0197eb3757526e2208e543fd9847a55bf2cf66cbcc5a9a44d6ca3d"
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
    required_patterns = (
        r"glm-zai:\s*served by glm-5\.2",
        rf"review[- _]content(?:\s+sha-256)?\**:\s*`?{REVIEW_CONTENT_SHA256}`?",
        r"recusal(?:[- ]status|[- ]check)?\**:\s*`?(?:NOT_RECUSED|clear)`?",
        r"verdict\**:\s*`?GREEN`?",
    )
    if any(not re.search(pattern, text, re.IGNORECASE) for pattern in required_patterns):
        raise JudgeError("GLM_OUTPUT_CONTRACT_FAILED")
    if not re.search(r"blockers\**:\s*`?(?:None|NONE|\[\])`?", text, re.IGNORECASE):
        raise JudgeError("GLM_BLOCKERS_NOT_EMPTY")
    if not re.search(r"evidence[- ]gaps\**:\s*`?(?:None|NONE|\[\])`?", text, re.IGNORECASE):
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
    if not GLM_INVALID_R1.is_file() or digest(GLM_INVALID_R1) != GLM_INVALID_R1_SHA256:
        raise JudgeError("PRESERVED_GLM_R1_DRIFT")
    if digest(PACKET) != PACKET_SHA256:
        raise JudgeError("PACKET_DRIFT")
    if digest(GLM) != GLM_SHA256 or digest(AGY) != AGY_SHA256:
        raise JudgeError("JUDGE_WRAPPER_DRIFT")
    if GLM_RAW.is_file():
        if digest(GLM_RAW) != GLM_RAW_SHA256:
            raise JudgeError("PRESERVED_GLM_R2_DRIFT")
        glm_raw = GLM_RAW.read_bytes()
    else:
        packet_raw = PACKET.read_bytes()
        glm_env = os.environ.copy()
        glm_env.update(
            {
                "GLM_ZAI_MODEL": "glm-5.2",
                "GLM_ZAI_PRIMARY_RETRIES": "0",
                "GLM_ZAI_DISABLE_FALLBACK": "1",
                "GLM_ZAI_VERIFY_MODEL": "glm-5.2",
                "GLM_ZAI_REPORT_MODEL": "1",
                "GLM_ZAI_MAX_TOKENS": "32768",
            }
        )
        glm_exit, glm_raw = invoke([str(GLM)], input_bytes=packet_raw, env=glm_env)
        atomic_write(GLM_RAW, glm_raw)
        if glm_exit != 0:
            raise JudgeError(f"GLM_PROCESS_FAILED:{glm_exit}:{glm_raw[-1000:]!r}")
    validate_glm(glm_raw)
    agy_exit, agy_raw = invoke([str(AGY), "--packet", str(PACKET), "--timeout", "600"])
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
