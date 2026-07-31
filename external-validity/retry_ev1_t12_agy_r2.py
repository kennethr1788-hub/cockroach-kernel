#!/usr/bin/env python3
"""Retry only the EV1-T12 AGY pre-execution lane over the frozen R1 packet."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess

import run_ev1_t12 as T12


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / ".ev1-runtime" / "EV1-T12" / "control"
PACKET = CONTROL / "EV1_T12_EXECUTION_PREFLIGHT_PACKET_R1.md"
GLM_RAW = CONTROL / "EV1_T12_EXECUTION_PREFLIGHT_GLM_RAW_R1.txt"
AGY_RAW_R1 = CONTROL / "EV1_T12_EXECUTION_PREFLIGHT_AGY_RAW_R1.txt"
AGY_RAW_R2 = CONTROL / "EV1_T12_EXECUTION_PREFLIGHT_AGY_RAW_R2.txt"
GATE = CONTROL / "INDEPENDENT_EXECUTION_GATE.json"
PACKET_SHA256 = "6f3ce1685524589b901553adcc11e10aafa6180924041f9bbef112065495dc09"
REVIEW_CONTENT_SHA256 = "4a6e76150e5ee0a4610716fe6c108995b7264c2dc0e88ca76bea47f638bc2bf3"
GLM_RAW_SHA256 = "4f8e24ecdf9c6b4645bbe9939384bc13710d329cee52f1c20241ec1893fda4c3"
AGY_RAW_R1_SHA256 = "6fdbab705b0e72d99a8199b3274e09ff8066cafbc408e683e324381baf33c760"
AGY = Path("/Users/kennethruedas/.local/bin/agy-judge")
AGY_SHA256 = "e90a7eca1526dd31b522fdbcb1b52e0083c93a0984e4d2f4edf8bde9eb0dd716"


class RetryError(RuntimeError):
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
        raise RetryError("AGY_R2_OUTPUT_CONTRACT_FAILED")


def main() -> int:
    if AGY_RAW_R2.exists() or GATE.exists():
        raise RetryError("R2_OUTPUT_OR_GATE_ALREADY_EXISTS")
    bindings = (
        (PACKET, PACKET_SHA256),
        (GLM_RAW, GLM_RAW_SHA256),
        (AGY_RAW_R1, AGY_RAW_R1_SHA256),
        (AGY, AGY_SHA256),
    )
    for path, expected in bindings:
        if not path.is_file() or digest(path) != expected:
            raise RetryError(f"BINDING_DRIFT:{path}")

    completed = subprocess.run(
        [str(AGY), "--packet", str(PACKET), "--timeout", "600"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=900,
        check=False,
    )
    raw = completed.stdout + completed.stderr
    atomic_write(AGY_RAW_R2, raw)
    if completed.returncode != 0:
        raise RetryError(f"AGY_R2_PROCESS_FAILED:{completed.returncode}")
    validate_agy(raw)

    body = {
        "version": "ev1-t12-independent-execution-gate-v1",
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
        "agy_raw_sha256": digest(AGY_RAW_R2),
        "agy_attempt": "R2",
        "preserved_failed_agy_attempt_sha256": digest(AGY_RAW_R1),
        "same_packet": True,
        "recusal_clear": True,
        "deletion_started": False,
    }
    receipt_hash, file_hash = T12.atomic_record(GATE, body)
    print(
        T12.canonical(
            {
                "agy_raw_sha256": digest(AGY_RAW_R2),
                "file_sha256": file_hash,
                "receipt_sha256": receipt_hash,
                "status": body["status"],
            }
        ).decode()
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
