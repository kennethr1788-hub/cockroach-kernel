#!/usr/bin/env python3
"""Prepare the source-bound disposable EV1-T07 workspace offline."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "EV1-T07"
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
SOURCE = ROOT / ".ev1-runtime" / "EV1-T06" / "control" / "BASELINE_SNAPSHOT"
DEPENDENCIES = ROOT / ".ev1-runtime" / "EV1-T06" / "dependency-runtime" / "node_modules"
T06_PREPARATION = ROOT / ".ev1-runtime" / "EV1-T06" / "control" / "PREPARATION_RECEIPT.json"
T06_PREPARATION_FILE_SHA256 = "01b4f7b60ee02ce518b3f2df5f00f3b186b43f9d97c5702305a9c8b1cd1b1a4a"
T06_PREPARATION_RECEIPT_SHA256 = "1a5caffc5e89e5cc3a1f4ef6583ae408e13b10387fcabed6f3e7edf4c0bfd3bb"
BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
SOURCE_COMMIT = "2c088ba8599c75cb02fbd61dfcf259d000729131"
LOCK_SHA256 = "7e0238617f56ecd9ab4c99bcc6d41a8a7e4c2635707c19247ddf082b94eacd7a"


class PreparationError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: bytes | Path | Any) -> str:
    if isinstance(value, Path):
        raw = value.read_bytes()
    elif isinstance(value, bytes):
        raw = value
    else:
        raw = canonical(value)
    return hashlib.sha256(raw).hexdigest()


def atomic_write(path: Path, raw: bytes, mode: int = 0o600) -> None:
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


def atomic_record(path: Path, body: dict[str, Any]) -> tuple[str, str]:
    sealed = dict(body, receipt_sha256=digest(body))
    raw = canonical(sealed) + b"\n"
    atomic_write(path, raw)
    return sealed["receipt_sha256"], digest(raw)


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 1200) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)


def manifest(root: Path, *, exclude_node_modules: bool = False) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if exclude_node_modules and (relative == "node_modules" or relative.startswith("node_modules/")):
            continue
        if path.is_symlink():
            rows.append({"kind": "symlink", "path": relative, "target": os.readlink(path)})
        elif path.is_file():
            rows.append({"kind": "file", "path": relative, "bytes": path.stat().st_size, "sha256": digest(path)})
        elif path.is_dir():
            rows.append({"kind": "directory", "path": relative})
        else:
            raise PreparationError("SPECIAL_FILE_IN_MANIFEST")
    return rows


def environment() -> dict[str, str]:
    for name in ("tmp", "npm-cache", "xdg-cache", "xdg-config", "xdg-state"):
        (CONTROL / name).mkdir(parents=True, exist_ok=True)
    npmrc = CONTROL / "npmrc"
    atomic_write(npmrc, b"offline=true\nignore-scripts=true\n")
    return {
        "CI": "1", "LANG": "C.UTF-8", "LC_ALL": "C", "NEXT_TELEMETRY_DISABLED": "1",
        "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin", "TMPDIR": str(CONTROL / "tmp"),
        "XDG_CACHE_HOME": str(CONTROL / "xdg-cache"), "XDG_CONFIG_HOME": str(CONTROL / "xdg-config"),
        "XDG_STATE_HOME": str(CONTROL / "xdg-state"), "npm_config_cache": str(CONTROL / "npm-cache"),
        "npm_config_userconfig": str(npmrc), "npm_config_update_notifier": "false",
    }


def logged(command: list[str], name: str, env: dict[str, str], timeout: int = 1200) -> dict[str, Any]:
    actual = ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command]
    completed = run(actual, cwd=WORKSPACE, env=env, timeout=timeout)
    raw = completed.stdout + completed.stderr
    atomic_write(CONTROL / f"{name}.log", raw)
    return {"exit": completed.returncode, "log_bytes": len(raw), "log_sha256": digest(raw), "network_mode": "DENIED_SEATBELT"}


def main() -> int:
    if CAMPAIGN.exists():
        raise PreparationError("EV1_T07_CAMPAIGN_ALREADY_EXISTS")
    if digest(T06_PREPARATION) != T06_PREPARATION_FILE_SHA256:
        raise PreparationError("T06_PREPARATION_FILE_DRIFT")
    prior = json.loads(T06_PREPARATION.read_text())
    if prior.get("receipt_sha256") != T06_PREPARATION_RECEIPT_SHA256:
        raise PreparationError("T06_PREPARATION_RECEIPT_DRIFT")
    if digest(SOURCE / "package-lock.json") != LOCK_SHA256:
        raise PreparationError("LOCKFILE_DRIFT")
    if SOURCE.is_symlink() or DEPENDENCIES.is_symlink() or not SOURCE.is_dir() or not DEPENDENCIES.is_dir():
        raise PreparationError("FROZEN_INPUT_UNSAFE")

    CONTROL.mkdir(parents=True, mode=0o700)
    source_manifest = manifest(SOURCE)
    copy_source = run(["cp", "-cR", str(SOURCE), str(WORKSPACE)], cwd=ROOT)
    if copy_source.returncode != 0:
        raise PreparationError("SOURCE_CLONE_FAILED")
    copy_dependencies = run(["cp", "-cR", str(DEPENDENCIES), str(WORKSPACE / "node_modules")], cwd=ROOT, timeout=1800)
    if copy_dependencies.returncode != 0:
        raise PreparationError("DEPENDENCY_CLONE_FAILED")
    if digest(manifest(WORKSPACE, exclude_node_modules=True)) != digest(source_manifest):
        raise PreparationError("SOURCE_CLONE_MANIFEST_MISMATCH")

    atomic_write(CONTROL / "offline.sb", b"(version 1)\n(allow default)\n(deny network*)\n")
    env = environment()
    typecheck = logged(["/usr/local/bin/npm", "run", "typecheck"], "baseline-typecheck", env)
    build = logged(["/usr/local/bin/npm", "run", "build"], "baseline-build", env)
    missing = logged(["/usr/local/bin/npm", "run", "test:api-limits"], "baseline-api-limits-absent", env)
    if typecheck["exit"] != 0 or build["exit"] != 0 or missing["exit"] == 0:
        raise PreparationError("BASELINE_ACCEPTANCE_CALIBRATION_FAILED")

    for command in (
        ["git", "init", "-b", "main"],
        ["git", "config", "user.name", "EV1 Disposable Campaign"],
        ["git", "config", "user.email", "ev1@invalid.local"],
        ["git", "add", "-A"],
        ["git", "commit", "-m", "Bind EV1-T07 source and dependency baseline"],
    ):
        completed = run(command, cwd=WORKSPACE, timeout=180)
        if completed.returncode != 0:
            raise PreparationError("DISPOSABLE_GIT_BASELINE_FAILED")
    head = run(["git", "rev-parse", "HEAD"], cwd=WORKSPACE, timeout=60)
    status = run(["git", "status", "--porcelain=v1", "-uall"], cwd=WORKSPACE, timeout=60)
    if head.returncode != 0 or status.returncode != 0 or status.stdout:
        raise PreparationError("BASELINE_GIT_STATE_INVALID")

    body = {
        "version": "ev1-t07-preparation-receipt-v1", "status": "EV1_T07_READY_FOR_AUTONOMOUS_TASK_WORK",
        "task_id": TASK_ID, "task_start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "backlog_sha256": BACKLOG_SHA256, "preflight_packet_sha256": PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE, "source_commit": SOURCE_COMMIT,
        "source_manifest_sha256": digest(source_manifest), "source_file_count": len([r for r in source_manifest if r["kind"] == "file"]),
        "disposable_baseline_commit": head.stdout.decode().strip(), "workspace_relative": ".ev1-runtime/EV1-T07/workspace",
        "objective": "Add explicit length and cardinality limits for analyze requests and return a stable 400 before provider invocation.",
        "acceptance_commands": ["npm run typecheck", "npm run build", "npm run test:api-limits"],
        "expected_state_mix": ["COMMITTED", "UNCOMMITTED", "UNTRACKED"], "human_edit_required": False,
        "predeclared_refusal_or_invalid": "EXPECTED_INVALID_OVERSIZED_80_KIB_FIXTURE", "data_classification": "SYNTHETIC",
        "dependency_setup": {"mode": "APFS_COPY_ON_WRITE_FROM_FROZEN_T05_GRAPH", "lockfile_sha256": LOCK_SHA256, "lifecycle_scripts_executed": False},
        "baseline": {"typecheck": typecheck, "build": build, "api_limits_test_absent": missing},
        "offline_profile_sha256": digest(CONTROL / "offline.sb"), "capture_started": False,
        "deletion_started": False, "recovery_started": False,
    }
    receipt_hash, file_hash = atomic_record(CONTROL / "PREPARATION_RECEIPT.json", body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
