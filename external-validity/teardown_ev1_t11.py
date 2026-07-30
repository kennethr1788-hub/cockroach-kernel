#!/usr/bin/env python3
"""Tear down only the bounded EV1-T11 temporary successor after final audit."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / ".ev1-runtime" / "EV1-T11"
CONTROL = CAMPAIGN / "control"
TARGET = Path("/private/tmp/ck-ev1-t11-r1")
SNAPSHOT = CONTROL / "POST_RECOVERY_SNAPSHOT"
TASK_RECEIPT = CONTROL / "TASK_EXECUTION_RECEIPT.json"
AUDIT_RAW = CONTROL / "EV1_T11_RESULT_AUDIT_GLM_RAW_R1.txt"
AUDIT_REPORT = ROOT / "EXTERNAL_VALIDITY_EV1_T11_RESULT_AUDIT_R1.md"
TEARDOWN_RECEIPT = CONTROL / "TEARDOWN_RECEIPT.json"
EXPECTED_TASK_FILE_SHA256 = "d66f1d6ba998a1d350197848761b1aee19cf99ccea42eee498b4b46d7951e575"
EXPECTED_TASK_RECEIPT_SHA256 = "8346b4855279ec1b6056acd8159e6ce986dc63c884d545c7de84ef7da50ac380"
EXPECTED_AUDIT_RAW_SHA256 = "e994de0963fbbee38fd0cebd947695f4065eb2f0bb3a6f61b54b7293a9dbeeb5"
EXPECTED_AUDIT_REPORT_SHA256 = "3d96d87821d10ed46e1c8879308c8fa124fc7710c5670feb39699b5bf474b047"
T07_WORKSPACE = ROOT / ".ev1-runtime" / "EV1-T07" / "workspace"
T08_WORKSPACE = ROOT / ".ev1-runtime" / "EV1-T08" / "workspace"


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: bytes | Path | Any) -> str:
    if isinstance(value, Path):
        raw = value.read_bytes()
    elif isinstance(value, bytes):
        raw = value
    else:
        raw = canonical(value)
    return hashlib.sha256(raw).hexdigest()


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


def load_receipt(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if not raw.endswith(b"\n"):
        raise RuntimeError("TASK_RECEIPT_NOT_CANONICAL")
    value = json.loads(raw[:-1])
    if canonical(value) + b"\n" != raw:
        raise RuntimeError("TASK_RECEIPT_NOT_CANONICAL")
    body = {key: value[key] for key in value if key != "receipt_sha256"}
    if value.get("receipt_sha256") != digest(body):
        raise RuntimeError("TASK_RECEIPT_HASH_INVALID")
    return value


def tree(root: Path) -> tuple[list[dict[str, Any]], dict[str, str]]:
    rows: list[dict[str, Any]] = []
    file_hashes: dict[str, str] = {}
    resolved_root = root.resolve(strict=True)
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raw_target = os.readlink(path)
            resolved = path.resolve(strict=True)
            if resolved != resolved_root and resolved_root not in resolved.parents:
                raise RuntimeError("TEARDOWN_TREE_SYMLINK_ESCAPE")
            rows.append({"kind": "symlink", "path": relative, "target": raw_target})
        elif path.is_file():
            file_hash = digest(path)
            rows.append({
                "kind": "file",
                "path": relative,
                "sha256": file_hash,
                "size": path.stat().st_size,
            })
            file_hashes[relative] = file_hash
        elif path.is_dir():
            rows.append({"kind": "directory", "path": relative})
        else:
            raise RuntimeError("TEARDOWN_TREE_SPECIAL_FILE")
    return rows, file_hashes


def related_processes() -> list[str]:
    completed = subprocess.run(
        ["ps", "-axo", "pid=,command="], check=False, capture_output=True, text=True, timeout=30
    )
    if completed.returncode != 0:
        raise RuntimeError("PROCESS_SCAN_FAILED")
    marker = str(TARGET)
    own_pid = os.getpid()
    results = []
    for line in completed.stdout.splitlines():
        fields = line.strip().split(maxsplit=1)
        if len(fields) == 2 and fields[0].isdigit() and int(fields[0]) != own_pid and marker in fields[1]:
            results.append(line.strip())
    return results


def open_files() -> list[str]:
    completed = subprocess.run(
        ["lsof", "+D", str(TARGET)], check=False, capture_output=True, text=True, timeout=120
    )
    if completed.returncode not in (0, 1):
        raise RuntimeError("OPEN_FILE_SCAN_FAILED")
    return [line for line in completed.stdout.splitlines() if line.strip()]


def main() -> int:
    if TEARDOWN_RECEIPT.exists():
        raise RuntimeError("TEARDOWN_ALREADY_RECORDED")
    if TARGET.is_symlink() or not TARGET.is_dir() or TARGET.resolve(strict=True) != TARGET:
        raise RuntimeError("TEARDOWN_TARGET_MISMATCH")
    if sorted(path.name for path in TARGET.iterdir()) != ["recovery"]:
        raise RuntimeError("TEARDOWN_TOP_LEVEL_MISMATCH")
    if digest(TASK_RECEIPT) != EXPECTED_TASK_FILE_SHA256:
        raise RuntimeError("TASK_RECEIPT_FILE_DRIFT")
    task = load_receipt(TASK_RECEIPT)
    if task.get("receipt_sha256") != EXPECTED_TASK_RECEIPT_SHA256:
        raise RuntimeError("TASK_RECEIPT_INTERNAL_DRIFT")
    if task.get("status") != "MECHANICAL_TASK_COMPLETE_OPERATOR_OBSERVATION_REQUIRED":
        raise RuntimeError("TASK_STATUS_INVALID")
    if task.get("state_mix", {}).get("human_edit_required") is not False:
        raise RuntimeError("TASK_CLASSIFICATION_DRIFT")
    if digest(AUDIT_RAW) != EXPECTED_AUDIT_RAW_SHA256:
        raise RuntimeError("RESULT_AUDIT_DRIFT")
    if digest(AUDIT_REPORT) != EXPECTED_AUDIT_REPORT_SHA256:
        raise RuntimeError("RESULT_AUDIT_REPORT_DRIFT")
    if not T07_WORKSPACE.is_dir() or not T08_WORKSPACE.is_dir():
        raise RuntimeError("EXPECTED_INVALID_WORKSPACE_MISSING")
    snapshot_rows, snapshot_hashes = tree(SNAPSHOT)
    if snapshot_hashes != task.get("post_recovery_snapshot_hashes"):
        raise RuntimeError("PRESERVED_SNAPSHOT_DRIFT")
    if related_processes():
        raise RuntimeError("TEARDOWN_RELATED_PROCESS_PRESENT")
    if open_files():
        raise RuntimeError("TEARDOWN_OPEN_FILE_PRESENT")
    rows, _ = tree(TARGET)
    file_rows = [row for row in rows if row["kind"] == "file"]
    directory_rows = [row for row in rows if row["kind"] == "directory"]
    symlink_rows = [row for row in rows if row["kind"] == "symlink"]
    pre_tree_sha256 = digest(rows)
    pre_bytes = sum(row["size"] for row in file_rows)

    shutil.rmtree(TARGET)
    directory = os.open(TARGET.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    if TARGET.exists() or TARGET.is_symlink():
        raise RuntimeError("TEARDOWN_TARGET_REMAINS")
    if related_processes():
        raise RuntimeError("POST_TEARDOWN_RELATED_PROCESS_PRESENT")
    if not T07_WORKSPACE.is_dir() or not T08_WORKSPACE.is_dir():
        raise RuntimeError("EXPECTED_INVALID_WORKSPACE_CHANGED")

    body = {
        "version": "ev1-t11-teardown-receipt-v1",
        "status": "EV1_T11_TEMPORARY_SUCCESSOR_TEARDOWN_GREEN",
        "task_id": "EV1-T11",
        "exact_teardown_root": "/private/tmp/ck-ev1-t11-r1",
        "root_resolved_exactly": True,
        "root_was_directory": True,
        "root_was_symlink": False,
        "expected_top_level_entries": ["recovery"],
        "open_file_lines_before_teardown": 0,
        "related_processes_before_teardown": 0,
        "pre_teardown_files": len(file_rows),
        "pre_teardown_directories": len(directory_rows),
        "pre_teardown_symlinks": len(symlink_rows),
        "pre_teardown_bytes": pre_bytes,
        "pre_teardown_tree_sha256": pre_tree_sha256,
        "post_teardown_root_exists": False,
        "post_teardown_related_processes": 0,
        "preserved_snapshot_files": len([row for row in snapshot_rows if row["kind"] == "file"]),
        "preserved_snapshot_tree_sha256": digest(snapshot_rows),
        "preserved_snapshot_hashes": snapshot_hashes,
        "project_capture_root_retained": (CAMPAIGN / "recovery").is_dir(),
        "project_dependency_runtime_retained_for_next_frozen_task": (
            CAMPAIGN / "dependency-runtime" / "node_modules"
        ).is_dir(),
        "second_recovery_attempted": False,
        "product_candidate_changed": False,
        "human_edit_required": False,
        "independent_human_edit_claim": "NOT_APPLICABLE",
        "expected_invalid_t07_t08_workspaces_touched": False,
    }
    receipt_hash, file_hash = atomic_record(TEARDOWN_RECEIPT, body)
    print(canonical({
        "file_sha256": file_hash,
        "receipt_sha256": receipt_hash,
        "status": body["status"],
    }).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
