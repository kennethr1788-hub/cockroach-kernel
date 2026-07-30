#!/usr/bin/env python3
"""Run and validate the final GLM 5.2 EV1-T07 result audit."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / ".ev1-runtime" / "EV1-T07" / "control"
PACKET = CONTROL / "EV1_T07_RESULT_AUDIT_PACKET_R2.md"
RAW = CONTROL / "EV1_T07_RESULT_AUDIT_GLM_RAW_R2.txt"
RECEIPT = CONTROL / "RESULT_AUDIT_JUDGE_RECEIPT_R2.json"
PACKET_SHA256 = "2a0fcc45389400427f9fed8782a76e5eeb6712580f780b8127f5140b711996fe"
CONTENT_SHA256 = "a8ef9eec869f069c115270d6dbc60ad45dc99879541b8d1fae6d0e9fd020df2b"
GLM = Path("/Users/kennethruedas/.local/bin/glm-zai")
GLM_SHA256 = "0b94755754de89557ffb9d00b45b8d8fef6578614d00563db2320e940f83748f"


def digest(raw: bytes | Path) -> str:
    value = raw.read_bytes() if isinstance(raw, Path) else raw
    return hashlib.sha256(value).hexdigest()


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


def main() -> int:
    if RAW.exists() or RECEIPT.exists():
        raise RuntimeError("T07_RESULT_AUDIT_ALREADY_STARTED")
    if digest(PACKET) != PACKET_SHA256 or digest(GLM) != GLM_SHA256:
        raise RuntimeError("T07_RESULT_PACKET_OR_JUDGE_DRIFT")
    environment = os.environ.copy()
    environment.update({
        "GLM_ZAI_MODEL": "glm-5.2",
        "GLM_ZAI_PRIMARY_RETRIES": "0",
        "GLM_ZAI_DISABLE_FALLBACK": "1",
        "GLM_ZAI_VERIFY_MODEL": "glm-5.2",
        "GLM_ZAI_REPORT_MODEL": "1",
        "GLM_ZAI_MAX_TOKENS": "16384",
    })
    completed = subprocess.run([str(GLM)], cwd=ROOT, env=environment, input=PACKET.read_bytes(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=900)
    raw = completed.stdout + completed.stderr
    atomic(RAW, raw)
    if completed.returncode != 0:
        raise RuntimeError(f"T07_RESULT_GLM_PROCESS_FAILED:{completed.returncode}")
    text = raw.decode("utf-8", "strict")
    patterns = (
        r"glm-zai:\s*served by glm-5\.2",
        rf"REVIEW_CONTENT_SHA256[^\n]*{CONTENT_SHA256}",
        r"RECUSAL_STATUS[^\n]*NOT_RECUSED",
        r"VERDICT[^\n]*GREEN",
        r"CONCRETE_BLOCKERS[^\n]*NONE",
        r"EVIDENCE_GAPS[^\n]*NONE",
        r"SCORING_CLASSIFICATION[^\n]*expected.invalid",
        r"SCORING_CLASSIFICATION[^\n]*not[^\n]*successful continuation",
    )
    if any(re.search(pattern, text, re.IGNORECASE) is None for pattern in patterns):
        raise RuntimeError("T07_RESULT_GLM_OUTPUT_CONTRACT_FAILED")
    body = {
        "version": "ev1-t07-result-audit-judge-receipt-v2",
        "status": "EV1_T07_RESULT_AUDIT_R2_GREEN",
        "task_id": "EV1-T07",
        "packet_sha256": PACKET_SHA256,
        "review_content_sha256": CONTENT_SHA256,
        "glm_wrapper_sha256": GLM_SHA256,
        "glm_raw_sha256": digest(RAW),
        "verdict": "GREEN",
        "recusal_clear": True,
        "concrete_blockers": [],
        "evidence_gaps": [],
        "scoring_classification": "EXPECTED_INVALID_SAFETY_RESULT_NOT_SUCCESSFUL_CONTINUATION",
        "utc_recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    receipt_hash = digest(canonical(body))
    atomic(RECEIPT, canonical(dict(body, receipt_sha256=receipt_hash)) + b"\n")
    print(canonical({"packet_sha256": PACKET_SHA256, "raw_sha256": digest(RAW), "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
