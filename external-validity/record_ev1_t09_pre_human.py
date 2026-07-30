#!/usr/bin/env python3
"""Verify EV1-T09 task work and stop at Kenneth's frozen human-edit gate."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / ".ev1-runtime" / "EV1-T09"
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
PREPARATION = CONTROL / "PREPARATION_RECEIPT.json"
HUMAN_CONTRACT = CONTROL / "HUMAN_EDIT_CONTRACT.json"
RECEIPT = CONTROL / "WORK_PRE_HUMAN_RECEIPT.json"
PREPARATION_FILE_SHA256 = "620e1ed092b32d2328c4ef3b2223d0400ae4841f558f5afe22fd6099b3844c0e"
PREPARATION_RECEIPT_SHA256 = "d05d6980c5c5806a4cb07b1020def33bf1e8dab40fe3c4e2aae765fa77ac3685"
HUMAN_CONTRACT_FILE_SHA256 = "4d52a6c7ef817cb4868421bed2859c3c1e23e14a8865fa9e04c9991840f8dc0e"
HUMAN_CONTRACT_RECEIPT_SHA256 = "be459fd4c8a2f51f39461d5d24996245d7ffee866423d8ce31069e578ce7de3b"
TASK_COMMIT = "3210c33c2a551f64d8a89270bfbc24d212f9d3ec"
MARKER = "> Release principle: [KENNETH: replace this bracketed instruction with one sentence in your own words.]"
EXPECTED_STATUS = [" M docs/RELEASE.md", "?? scripts/release-policy-cases.json"]
EXPECTED_HASHES = {
    "docs/RELEASE.md": "9eb4c707cc992ce4535af37690c70553164792657f6f18162012ed932708a871",
    "scripts/release-policy-cases.json": "07fb4cf7d9e0777730ecc370a50e34381b7b0c55208cc85d93a63c544322265f",
    "scripts/validate-release-policy.mjs": "8980709503fbd02a9ab1fcad575896e50c4947e603a7609e2b5fb432c67e831c",
}
PNPM = CONTROL / "pnpm-runtime" / "node_modules" / "pnpm" / "bin" / "pnpm.cjs"
PRETTIER = CAMPAIGN / "dependency-runtime" / "node_modules" / "prettier" / "bin" / "prettier.cjs"
PNPM_SHA256 = "b276da51dc8ca5b0d3ee3371695b50fc8b3244b281b091c63a3f082a88dadeb9"
PRETTIER_SHA256 = "ac5523cd57e7e9d8eac71caef7e022a8a8489bcdc19ca8a778b7e728ec103b93"


class WorkError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: bytes | Path | Any) -> str:
    raw = value.read_bytes() if isinstance(value, Path) else value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


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


def run(command: list[str], *, timeout: int = 300) -> subprocess.CompletedProcess[bytes]:
    fake_home = CONTROL / "fake-home"
    fake_home.mkdir(exist_ok=True)
    environment = {
        "CI": "1",
        "HOME": str(fake_home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        "PATH": f"{CONTROL / 'bin'}:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "TMPDIR": str(CONTROL / "tmp"),
        "XDG_CACHE_HOME": str(CONTROL / "xdg-cache"),
        "XDG_CONFIG_HOME": str(CONTROL / "xdg-config"),
        "XDG_STATE_HOME": str(CONTROL / "xdg-state"),
    }
    for path in (CONTROL / "tmp", CONTROL / "xdg-cache", CONTROL / "xdg-config", CONTROL / "xdg-state"):
        path.mkdir(exist_ok=True)
    return subprocess.run(["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command], cwd=WORKSPACE, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)


def logged(command: list[str], name: str, expected_exit: int) -> dict[str, Any]:
    completed = run(command)
    raw = completed.stdout + completed.stderr
    atomic(CONTROL / f"{name}.log", raw)
    if completed.returncode != expected_exit:
        raise WorkError(f"COMMAND_EXIT_MISMATCH:{name}:{completed.returncode}")
    return {"command_label": name, "exit": completed.returncode, "log_bytes": len(raw), "log_sha256": digest(raw), "network_mode": "DENIED_SEATBELT"}


def git(*arguments: str) -> list[str]:
    completed = subprocess.run(["git", *arguments], cwd=WORKSPACE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120, check=False)
    if completed.returncode != 0:
        raise WorkError("GIT_INSPECTION_FAILED")
    return completed.stdout.decode().splitlines()


def main() -> int:
    if RECEIPT.exists():
        raise WorkError("PRE_HUMAN_WORK_ALREADY_RECORDED")
    if digest(PREPARATION) != PREPARATION_FILE_SHA256 or digest(HUMAN_CONTRACT) != HUMAN_CONTRACT_FILE_SHA256:
        raise WorkError("PREPARATION_OR_CONTRACT_FILE_DRIFT")
    preparation = json.loads(PREPARATION.read_text())
    contract = json.loads(HUMAN_CONTRACT.read_text())
    if preparation.get("receipt_sha256") != PREPARATION_RECEIPT_SHA256 or contract.get("receipt_sha256") != HUMAN_CONTRACT_RECEIPT_SHA256:
        raise WorkError("PREPARATION_OR_CONTRACT_RECEIPT_DRIFT")
    if git("rev-parse", "HEAD") != [TASK_COMMIT] or git("status", "--porcelain=v1", "-uall") != EXPECTED_STATUS:
        raise WorkError("TASK_STATE_DRIFT")
    hashes = {relative: digest(WORKSPACE / relative) for relative in sorted(EXPECTED_HASHES)}
    if hashes != EXPECTED_HASHES:
        raise WorkError("TASK_FILE_HASH_DRIFT")
    release = (WORKSPACE / "docs" / "RELEASE.md").read_text()
    if release.count(MARKER) != 1:
        raise WorkError("HUMAN_EDIT_MARKER_DRIFT")
    validator = (WORKSPACE / "scripts" / "validate-release-policy.mjs").read_text()
    forbidden_network = ("node:http", "node:https", "node:net", "fetch(", "child_process", "npm publish")
    if any(token in validator for token in forbidden_network):
        raise WorkError("VALIDATOR_NETWORK_OR_PUBLISH_SURFACE")
    package = json.loads((WORKSPACE / "package.json").read_text())
    if package.get("private") is not True:
        raise WorkError("PRIVATE_PACKAGE_SAFEGUARD_MISSING")
    if digest(PNPM) != PNPM_SHA256 or digest(PRETTIER) != PRETTIER_SHA256:
        raise WorkError("PINNED_TOOL_DRIFT")
    profile = CONTROL / "offline.sb"
    atomic(profile, b"(version 1)\n(allow default)\n(deny network*)\n")
    prettier = logged([str(PNPM), "exec", "prettier", "--check", "docs/RELEASE.md"], "pre-human-prettier", 0)
    structural = logged(["/usr/local/bin/node", "scripts/validate-release-policy.mjs", "--sections", "versioning,changelog", "--allow-human-placeholder"], "pre-human-structural", 0)
    gate = logged(["/usr/local/bin/node", "scripts/validate-release-policy.mjs", "--sections", "versioning,changelog"], "pre-human-required-gate", 1)
    if (CONTROL / "pre-human-required-gate.log").read_text().strip() != "HUMAN_RELEASE_PRINCIPLE_REQUIRED":
        raise WorkError("HUMAN_GATE_REASON_DRIFT")
    body = {
        "version": "ev1-t09-work-pre-human-receipt-v1",
        "status": "EV1_T09_WORK_GREEN_HUMAN_EDIT_REQUIRED",
        "task_id": "EV1-T09",
        "utc_recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "backlog_sha256": preparation["backlog_sha256"],
        "global_ev1_preflight_packet_sha256": preparation["global_ev1_preflight_packet_sha256"],
        "product_candidate": preparation["product_candidate"],
        "source_commit": preparation["source_commit"],
        "source_manifest_sha256": preparation["source_manifest_sha256"],
        "preparation_file_sha256": PREPARATION_FILE_SHA256,
        "preparation_receipt_sha256": PREPARATION_RECEIPT_SHA256,
        "human_edit_contract_file_sha256": HUMAN_CONTRACT_FILE_SHA256,
        "human_edit_contract_receipt_sha256": HUMAN_CONTRACT_RECEIPT_SHA256,
        "task_commit": TASK_COMMIT,
        "state_mix": {"committed": ["scripts/validate-release-policy.mjs"], "uncommitted": ["docs/RELEASE.md"], "untracked": ["scripts/release-policy-cases.json"], "status": EXPECTED_STATUS},
        "declared_file_hashes_before_human_edit": hashes,
        "private_package_safeguard": True,
        "validator_network_or_publish_surface": False,
        "pinned_tools": {"pnpm_version": "10.17.0", "pnpm_entry_sha256": PNPM_SHA256, "prettier_version": "3.8.1", "prettier_entry_sha256": PRETTIER_SHA256},
        "acceptance_before_human_edit": {"prettier": prettier, "structural_policy": structural, "required_human_gate": gate},
        "human_edit_marker_present": True,
        "human_edit_received": False,
        "capture_started": False,
        "deletion_started": False,
        "recovery_started": False,
        "public_action": False,
    }
    receipt_hash = digest(body)
    raw = canonical(dict(body, receipt_sha256=receipt_hash)) + b"\n"
    atomic(RECEIPT, raw)
    print(canonical({"file_sha256": digest(raw), "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
