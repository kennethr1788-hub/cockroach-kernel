#!/usr/bin/env python3
"""Tear down only the audited EV1-T12 temporary successor."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / ".ev1-runtime" / "EV1-T12"
CONTROL = CAMPAIGN / "control"
TARGET = Path("/private/tmp/ck-ev1-t12-r1")
SNAPSHOT = CONTROL / "POST_RECOVERY_SNAPSHOT"
TASK = CONTROL / "TASK_EXECUTION_RECEIPT.json"
AUDIT_RAW = CONTROL / "EV1_T12_RESULT_AUDIT_GLM_RAW_R1.txt"
AUDIT_REPORT = ROOT / "EXTERNAL_VALIDITY_EV1_T12_RESULT_AUDIT_R1.md"
TEARDOWN = CONTROL / "TEARDOWN_RECEIPT.json"
EXPECTED_TASK_FILE = "7569976cc103696106b7880f85c1ad178fe3d7a2524267f3967818fa99d4c3c9"
EXPECTED_TASK_INTERNAL = "2d1c812da116d8c37dde46e7b5f35e08d7d74493bcd0772830bae09278ce6459"
EXPECTED_AUDIT_RAW = "504b7f518e71597529a2cd5fd56cbe49b8a18a827e729f5c2d6ee02fcb22fc17"
EXPECTED_AUDIT_REPORT = "40160f0c5e2d36bd12c5d1454192b11ec216e6892c2a49e6225b16512ba4bf97"
T07 = ROOT / ".ev1-runtime" / "EV1-T07" / "workspace"
T08 = ROOT / ".ev1-runtime" / "EV1-T08" / "workspace"


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: bytes | Path | Any) -> str:
    raw = value.read_bytes() if isinstance(value, Path) else value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def load_receipt(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if raw != canonical(value) + b"\n":
        raise RuntimeError("TASK_RECEIPT_NOT_CANONICAL")
    body = {key: value[key] for key in value if key != "receipt_sha256"}
    if value.get("receipt_sha256") != digest(body):
        raise RuntimeError("TASK_RECEIPT_HASH_INVALID")
    return value


def atomic_record(path: Path, body: dict[str, Any]) -> tuple[str, str]:
    sealed = dict(body, receipt_sha256=digest(body))
    raw = canonical(sealed) + b"\n"
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
    return sealed["receipt_sha256"], digest(raw)


def tree(root: Path) -> tuple[list[dict[str, Any]], dict[str, str]]:
    rows: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    resolved_root = root.resolve(strict=True)
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            resolved = path.resolve(strict=True)
            if resolved != resolved_root and resolved_root not in resolved.parents:
                raise RuntimeError("TEARDOWN_TREE_SYMLINK_ESCAPE")
            rows.append({"kind": "symlink", "path": relative, "target": os.readlink(path)})
        elif path.is_file():
            file_hash = digest(path)
            rows.append({"kind": "file", "path": relative, "sha256": file_hash, "size": path.stat().st_size})
            hashes[relative] = file_hash
        elif path.is_dir():
            rows.append({"kind": "directory", "path": relative})
        else:
            raise RuntimeError("TEARDOWN_TREE_SPECIAL_FILE")
    return rows, hashes


def related_processes() -> list[str]:
    completed = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True, text=True, timeout=30, check=False)
    if completed.returncode != 0:
        raise RuntimeError("PROCESS_SCAN_FAILED")
    marker = str(TARGET)
    return [line.strip() for line in completed.stdout.splitlines() if marker in line and not line.strip().startswith(str(os.getpid()) + " ")]


def open_files() -> list[str]:
    completed = subprocess.run(["lsof", "+D", str(TARGET)], capture_output=True, text=True, timeout=120, check=False)
    if completed.returncode not in (0, 1):
        raise RuntimeError("OPEN_FILE_SCAN_FAILED")
    return [line for line in completed.stdout.splitlines() if line.strip()]


def main() -> int:
    if TEARDOWN.exists():
        raise RuntimeError("TEARDOWN_ALREADY_RECORDED")
    if TARGET.is_symlink() or not TARGET.is_dir() or TARGET.resolve(strict=True) != TARGET:
        raise RuntimeError("TEARDOWN_TARGET_MISMATCH")
    if sorted(path.name for path in TARGET.iterdir()) != ["recovery"]:
        raise RuntimeError("TEARDOWN_TOP_LEVEL_MISMATCH")
    if digest(TASK) != EXPECTED_TASK_FILE or digest(AUDIT_RAW) != EXPECTED_AUDIT_RAW or digest(AUDIT_REPORT) != EXPECTED_AUDIT_REPORT:
        raise RuntimeError("AUDITED_INPUT_DRIFT")
    task = load_receipt(TASK)
    if task.get("receipt_sha256") != EXPECTED_TASK_INTERNAL or task.get("status") != "MECHANICAL_TASK_COMPLETE_OPERATOR_OBSERVATION_REQUIRED":
        raise RuntimeError("TASK_RECEIPT_DRIFT")
    if not T07.is_dir() or not T08.is_dir():
        raise RuntimeError("EXPECTED_INVALID_WORKSPACE_MISSING")
    snapshot_rows, snapshot_hashes = tree(SNAPSHOT)
    if snapshot_hashes != task.get("post_recovery_snapshot_hashes"):
        raise RuntimeError("PRESERVED_SNAPSHOT_DRIFT")
    if related_processes() or open_files():
        raise RuntimeError("TEARDOWN_RESOURCE_BUSY")
    rows, _ = tree(TARGET)
    files = [row for row in rows if row["kind"] == "file"]
    directories = [row for row in rows if row["kind"] == "directory"]
    symlinks = [row for row in rows if row["kind"] == "symlink"]
    pre_bytes = sum(row["size"] for row in files)
    pre_hash = digest(rows)
    shutil.rmtree(TARGET)
    descriptor = os.open(TARGET.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    if TARGET.exists() or related_processes() or not T07.is_dir() or not T08.is_dir():
        raise RuntimeError("POST_TEARDOWN_VERIFICATION_FAILED")
    body = {
        "version": "ev1-t12-teardown-receipt-v1",
        "status": "EV1_T12_TEMPORARY_SUCCESSOR_TEARDOWN_GREEN",
        "task_id": "EV1-T12",
        "exact_teardown_root": "/private/tmp/ck-ev1-t12-r1",
        "root_resolved_exactly": True,
        "expected_top_level_entries": ["recovery"],
        "pre_teardown_files": len(files),
        "pre_teardown_directories": len(directories),
        "pre_teardown_symlinks": len(symlinks),
        "pre_teardown_bytes": pre_bytes,
        "pre_teardown_tree_sha256": pre_hash,
        "post_teardown_root_exists": False,
        "post_teardown_related_processes": 0,
        "preserved_snapshot_files": len([row for row in snapshot_rows if row["kind"] == "file"]),
        "preserved_snapshot_tree_sha256": digest(snapshot_rows),
        "preserved_snapshot_hashes": snapshot_hashes,
        "second_recovery_attempted": False,
        "product_candidate_changed": False,
        "human_edit_required": False,
        "independent_human_edit_claim": "NOT_APPLICABLE",
        "expected_invalid_t07_t08_workspaces_touched": False,
    }
    receipt_hash, file_hash = atomic_record(TEARDOWN, body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
