#!/usr/bin/env python3
"""Prepare the exact-commit disposable EV1-T09 workspace and human-edit contract."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "EV1-T09"
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
SOURCE = Path("/Users/kennethruedas/master-vault/tools/step-realtime-cli")
SOURCE_COMMIT = "ee6862f7d65d24d4de11eda8306d29356873b529"
SOURCE_MANIFEST_SHA256 = "6f81e7e81ad100b53163a13b11c5e7abcd437fe658f817e34905c02cbe0e7182"
SOURCE_FILE_COUNT = 410
BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
GLOBAL_EV1_PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
LOCK_SHA256 = "c16bd11ac537f1e60402f867ac2b1ac62a0479889addb879e284b3f1d3465c36"
HUMAN_EDIT_PATH = "docs/RELEASE.md"
HUMAN_EDIT_MARKER = "> Release principle: [KENNETH: replace this bracketed instruction with one sentence in your own words.]"
PRIVATE = re.compile(rb"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY")


class PreparationError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: bytes | Path | Any) -> str:
    raw = value.read_bytes() if isinstance(value, Path) else value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def atomic(path: Path, raw: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
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


def record(path: Path, body: dict[str, Any]) -> tuple[str, str]:
    receipt_hash = digest(body)
    raw = canonical(dict(body, receipt_sha256=receipt_hash)) + b"\n"
    atomic(path, raw)
    return receipt_hash, digest(raw)


def run(command: list[str], *, cwd: Path, timeout: int = 300) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)


def source_rows() -> list[dict[str, str]]:
    result = run(["git", "ls-tree", "-r", SOURCE_COMMIT], cwd=SOURCE)
    if result.returncode != 0:
        raise PreparationError("SOURCE_TREE_UNREADABLE")
    rows: list[dict[str, str]] = []
    for line in result.stdout.decode().splitlines():
        metadata, path = line.split("\t", 1)
        mode, object_type, blob = metadata.split(" ", 2)
        if object_type != "blob":
            raise PreparationError("SOURCE_NON_BLOB_ENTRY")
        rows.append({"blob": blob, "mode": mode, "path": path})
    return rows


def workspace_manifest() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(WORKSPACE.rglob("*")):
        relative = path.relative_to(WORKSPACE).as_posix()
        if relative == ".git" or relative.startswith(".git/"):
            continue
        if path.is_symlink():
            rows.append({"kind": "symlink", "path": relative, "target": os.readlink(path)})
        elif path.is_file():
            rows.append({"bytes": path.stat().st_size, "kind": "file", "path": relative, "sha256": digest(path)})
        elif path.is_dir():
            rows.append({"kind": "directory", "path": relative})
        else:
            raise PreparationError("SPECIAL_FILE_IN_WORKSPACE")
    return rows


def main() -> int:
    if CAMPAIGN.exists():
        raise PreparationError("EV1_T09_CAMPAIGN_ALREADY_EXISTS")
    if not SOURCE.is_dir() or SOURCE.is_symlink():
        raise PreparationError("SOURCE_ROOT_UNSAFE")
    identity = run(["git", "cat-file", "-e", f"{SOURCE_COMMIT}^{{commit}}"], cwd=SOURCE)
    if identity.returncode != 0:
        raise PreparationError("SOURCE_COMMIT_MISSING")
    rows = source_rows()
    if len(rows) != SOURCE_FILE_COUNT or digest(rows) != SOURCE_MANIFEST_SHA256:
        raise PreparationError("SOURCE_MANIFEST_DRIFT")
    forbidden = [row["path"] for row in rows if Path(row["path"]).name.lower() in {".env", "credentials.json", "secrets.json", "id_rsa", "id_ed25519"} or Path(row["path"]).suffix.lower() in {".pem", ".p12", ".pfx"}]
    if forbidden:
        raise PreparationError("SOURCE_FORBIDDEN_TRACKED_FILE")
    grep = run(["git", "grep", "-I", "-E", "(/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY)", SOURCE_COMMIT, "--"], cwd=SOURCE)
    if grep.returncode not in (0, 1) or grep.returncode == 0:
        raise PreparationError("SOURCE_PRIVATE_MARKER")
    CONTROL.mkdir(parents=True, mode=0o700)
    archive = CONTROL / "source.tar"
    archived = run(["git", "archive", "--format=tar", "-o", str(archive), SOURCE_COMMIT], cwd=SOURCE)
    if archived.returncode != 0:
        raise PreparationError("SOURCE_ARCHIVE_FAILED")
    WORKSPACE.mkdir(mode=0o700)
    with tarfile.open(archive, "r:") as handle:
        for member in handle.getmembers():
            pure = Path(member.name)
            if pure.is_absolute() or ".." in pure.parts or member.issym() or member.islnk():
                raise PreparationError("ARCHIVE_ENTRY_UNSAFE")
        # Every member was validated immediately above. The host Python lacks
        # the newer filter= API, so extract only after that fail-closed pass.
        handle.extractall(WORKSPACE)
    archive.unlink()
    extracted_files = [path for path in WORKSPACE.rglob("*") if path.is_file()]
    if len(extracted_files) != SOURCE_FILE_COUNT or any(PRIVATE.search(path.read_bytes()) for path in extracted_files):
        raise PreparationError("EXTRACTED_SOURCE_BOUNDARY_FAILED")
    if digest(WORKSPACE / "pnpm-lock.yaml") != LOCK_SHA256:
        raise PreparationError("LOCKFILE_DRIFT")
    package = json.loads((WORKSPACE / "package.json").read_text())
    if package.get("private") is not True or package.get("packageManager") != "pnpm@10.17.0":
        raise PreparationError("PRIVATE_PACKAGE_SAFEGUARD_DRIFT")
    release = (WORKSPACE / HUMAN_EDIT_PATH).read_text()
    if "版本号策略" not in release or "changelog" not in release or HUMAN_EDIT_MARKER in release:
        raise PreparationError("BASELINE_PLACEHOLDER_CALIBRATION_FAILED")
    for command in (["git", "init", "-b", "main"], ["git", "config", "user.name", "EV1 Disposable Campaign"], ["git", "config", "user.email", "ev1@invalid.local"], ["git", "add", "-A"], ["git", "commit", "-m", "Bind EV1-T09 public source baseline"]):
        completed = run(command, cwd=WORKSPACE)
        if completed.returncode != 0:
            raise PreparationError("DISPOSABLE_GIT_BASELINE_FAILED")
    head = run(["git", "rev-parse", "HEAD"], cwd=WORKSPACE)
    status = run(["git", "status", "--porcelain=v1", "-uall"], cwd=WORKSPACE)
    if head.returncode != 0 or status.returncode != 0 or status.stdout:
        raise PreparationError("BASELINE_GIT_STATE_INVALID")
    contract = {
        "version": "ev1-t09-human-edit-contract-v1",
        "task_id": TASK_ID,
        "path": HUMAN_EDIT_PATH,
        "marker": HUMAN_EDIT_MARKER,
        "required_edit": "Kenneth personally replaces the bracketed marker with exactly one nonempty declarative sentence in his own words while preserving the prefix '> Release principle: '.",
        "must_be_typed_and_visibly_saved_by": "KENNETH",
        "codex_may_supply_sentence": False,
        "capture_before_human_edit": False,
        "public_action_authorized": False,
    }
    contract_hash, contract_file_hash = record(CONTROL / "HUMAN_EDIT_CONTRACT.json", contract)
    manifest = workspace_manifest()
    body = {
        "version": "ev1-t09-preparation-receipt-v1",
        "status": "EV1_T09_READY_FOR_TASK_WORK",
        "task_id": TASK_ID,
        "task_start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "backlog_sha256": BACKLOG_SHA256,
        "global_ev1_preflight_packet_sha256": GLOBAL_EV1_PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "source_commit": SOURCE_COMMIT,
        "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
        "source_file_count": SOURCE_FILE_COUNT,
        "workspace_manifest_sha256": digest(manifest),
        "workspace_file_count": len(extracted_files),
        "disposable_baseline_commit": head.stdout.decode().strip(),
        "workspace_relative": ".ev1-runtime/EV1-T09/workspace",
        "objective": "Replace SemVer and changelog placeholders with explicit deterministic release policy while preserving the private-package safeguard.",
        "acceptance_commands": ["pnpm exec prettier --check docs/RELEASE.md", "node scripts/validate-release-policy.mjs --sections versioning,changelog"],
        "expected_state_mix": ["COMMITTED", "UNCOMMITTED", "UNTRACKED"],
        "human_edit_required": True,
        "human_edit_contract_file_sha256": contract_file_hash,
        "human_edit_contract_receipt_sha256": contract_hash,
        "private_package_safeguard": True,
        "package_manager": "pnpm@10.17.0",
        "lockfile_sha256": LOCK_SHA256,
        "data_classification": "PUBLIC_MIT",
        "public_or_upstream_action_authorized": False,
        "capture_started": False,
        "deletion_started": False,
        "recovery_started": False,
    }
    receipt_hash, file_hash = record(CONTROL / "PREPARATION_RECEIPT.json", body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
