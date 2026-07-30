#!/usr/bin/env python3
"""Run and validate the frozen EV1-T09 objective-evidence GLM 5.2 audit."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / ".ev1-runtime" / "EV1-T09" / "control"
PACKET = CONTROL / "EV1_T09_RESULT_AUDIT_PACKET_R1.md"
GLM_RAW = CONTROL / "EV1_T09_RESULT_AUDIT_GLM_RAW_R1.txt"
PACKET_SHA256 = "90a21e73653d37f48e6802458e8a6808a792c46ce548cf27bc2acb9ec3b2cc69"
REVIEW_CONTENT_SHA256 = "a2ad10b073ff7b800127ce9c078404d876d0e55cf07e3566858cb672e9489e27"
GLM = Path("/Users/kennethruedas/.local/bin/glm-zai")
GLM_SHA256 = "0b94755754de89557ffb9d00b45b8d8fef6578614d00563db2320e940f83748f"


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


def label(pattern: str) -> str:
    return rf"\**`?{pattern}`?\**\s*:\s*"


def validate(raw: bytes) -> None:
    text = raw.decode("utf-8", "strict")
    required = (
        r"glm-zai:\s*served by glm-5\.2",
        label(r"REVIEW[- _]CONTENT[- _]SHA(?:-256|256)") + rf"`?{REVIEW_CONTENT_SHA256}`?",
        label("VERDICT") + r"`?GREEN`?",
        label("OBSERVATION[- _]1[- _]EVIDENCE") + r"`?SUPPORTED`?",
        label("OBSERVATION[- _]2[- _]EVIDENCE") + r"`?SUPPORTED`?",
        label("CLASSIFICATION[- _]EVIDENCE") + r"`?SUPPORTED`?",
        label("BLOCKERS") + r"`?(?:None|NONE|\[\])`?",
    )
    if any(not re.search(pattern, text, re.IGNORECASE) for pattern in required):
        raise JudgeError("GLM_OUTPUT_CONTRACT_FAILED")
    if not re.search(
        r"(?:subjective experience|usability).*(?:human-only|human only|cannot)",
        text,
        re.IGNORECASE | re.DOTALL,
    ):
        raise JudgeError("GLM_HUMAN_ONLY_LIMITATION_MISSING")
    if not re.search(
        r"model[- ]assisted.*(?:not|cannot|excluded).*(?:independent|human[- ]edited)",
        text,
        re.IGNORECASE | re.DOTALL,
    ):
        raise JudgeError("GLM_MODEL_ASSISTED_LIMITATION_MISSING")
    recusal = re.search(label("RECUSAL") + r"(.+)", text, re.IGNORECASE)
    if recusal is None or re.match(
        r"\s*`?(?:required|recusal_required|recuse)\b", recusal.group(1), re.IGNORECASE
    ):
        raise JudgeError("GLM_RECUSAL_NOT_CLEAR")


def main() -> int:
    if GLM_RAW.exists():
        raise JudgeError("GLM_OUTPUT_ALREADY_EXISTS")
    if digest(PACKET) != PACKET_SHA256:
        raise JudgeError("PACKET_DRIFT")
    if digest(GLM) != GLM_SHA256:
        raise JudgeError("JUDGE_WRAPPER_DRIFT")
    environment = os.environ.copy()
    environment.update(
        {
            "GLM_ZAI_MODEL": "glm-5.2",
            "GLM_ZAI_PRIMARY_RETRIES": "0",
            "GLM_ZAI_DISABLE_FALLBACK": "1",
            "GLM_ZAI_VERIFY_MODEL": "glm-5.2",
            "GLM_ZAI_REPORT_MODEL": "1",
            "GLM_ZAI_MAX_TOKENS": "8192",
        }
    )
    completed = subprocess.run(
        [str(GLM)],
        cwd=ROOT,
        env=environment,
        input=PACKET.read_bytes(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=900,
        check=False,
    )
    raw = completed.stdout + completed.stderr
    atomic_write(GLM_RAW, raw)
    if completed.returncode != 0:
        raise JudgeError(f"GLM_PROCESS_FAILED:{completed.returncode}:{raw[-1000:]!r}")
    validate(raw)
    print(
        "GLM_5_2_GREEN "
        f"PACKET_SHA256={PACKET_SHA256} "
        f"GLM_RAW_SHA256={digest(GLM_RAW)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
