#!/usr/bin/env python3
"""Prepare the source-bound EV1-T02 disposable workspace.

This script exports the frozen Brew Ledger source, creates a disposable Git
baseline, clones the already verified project-local dependency tree, calibrates
the frozen acceptance sequence offline, and stops before task work begins.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPO = Path.home() / "master-vault" / "coffee"
SOURCE_COMMIT = "1a92380a9edf12337f80b3c42ba098a7c1724664"
SOURCE_MANIFEST_SHA256 = "d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706"
BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
TASK_ID = "EV1-T02"
EXCLUDED = {"CLAUDE.md"}
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
DEPENDENCY_SOURCE = ROOT / ".ev1-runtime" / "EV1-T01" / "dependency-runtime" / "node_modules"
PRIVATE_MARKER = re.compile(
    rb"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY"
)


class PreparationError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


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


def run(
    command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 600
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def git_source(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return run(["git", "-C", str(SOURCE_REPO), *arguments], cwd=ROOT, timeout=60)


def git_workspace(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return run(["git", *arguments], cwd=WORKSPACE, timeout=120)


def source_rows() -> list[dict[str, str]]:
    tree = git_source("ls-tree", "-r", SOURCE_COMMIT)
    if tree.returncode != 0:
        raise PreparationError("SOURCE_TREE_UNREADABLE")
    rows: list[dict[str, str]] = []
    for raw_line in tree.stdout.decode("utf-8").splitlines():
        metadata, relative = raw_line.split("\t", 1)
        mode, object_type, blob = metadata.split(" ", 2)
        pure = PurePosixPath(relative)
        if (
            object_type != "blob"
            or mode not in {"100644", "100755"}
            or pure.is_absolute()
            or ".." in pure.parts
            or "\x00" in relative
        ):
            raise PreparationError("SOURCE_PATH_OR_MODE_UNSAFE")
        if relative not in EXCLUDED:
            rows.append({"blob": blob, "mode": mode, "path": relative})
    if len(rows) != 76 or digest(rows) != SOURCE_MANIFEST_SHA256:
        raise PreparationError("SOURCE_MANIFEST_MISMATCH")
    return rows


def safe_target(relative: str) -> Path:
    target = WORKSPACE.joinpath(*PurePosixPath(relative).parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    parent = target.parent.resolve(strict=True)
    if WORKSPACE.resolve(strict=True) not in (parent, *parent.parents):
        raise PreparationError("SOURCE_EXPORT_ESCAPE")
    return target


def export_source(rows: list[dict[str, str]]) -> None:
    for row in rows:
        blob = git_source("show", f"{SOURCE_COMMIT}:{row['path']}")
        if blob.returncode != 0 or PRIVATE_MARKER.search(blob.stdout):
            raise PreparationError("SOURCE_EXPORT_BLOCKED")
        atomic_write(
            safe_target(row["path"]),
            blob.stdout,
            0o755 if row["mode"] == "100755" else 0o644,
        )


def initialize_baseline() -> str:
    commands = (
        ["init", "-b", "main"],
        ["config", "user.name", "EV1 Disposable Campaign"],
        ["config", "user.email", "ev1@invalid.local"],
        ["add", "-A"],
        ["commit", "-m", "Bind EV1-T02 source baseline"],
    )
    for arguments in commands:
        completed = git_workspace(*arguments)
        if completed.returncode != 0:
            raise PreparationError("DISPOSABLE_GIT_BASELINE_FAILED")
    head = git_workspace("rev-parse", "HEAD")
    if head.returncode != 0:
        raise PreparationError("DISPOSABLE_GIT_HEAD_MISSING")
    return head.stdout.decode("ascii").strip()


def clone_dependencies() -> dict[str, Any]:
    if not DEPENDENCY_SOURCE.is_dir() or DEPENDENCY_SOURCE.is_symlink():
        raise PreparationError("VERIFIED_DEPENDENCY_SOURCE_MISSING")
    destination = WORKSPACE / "node_modules"
    completed = run(
        ["cp", "-cR", str(DEPENDENCY_SOURCE), str(destination)],
        cwd=ROOT,
        timeout=600,
    )
    if completed.returncode != 0 or not (destination / ".bin" / "tsc").is_file():
        raise PreparationError("DEPENDENCY_CLONE_FAILED")
    return {
        "source_relative": ".ev1-runtime/EV1-T01/dependency-runtime/node_modules",
        "clone_mode": "APFS_COPY_ON_WRITE",
        "tsc_sha256": digest(destination / "typescript" / "bin" / "tsc"),
    }


def environment() -> dict[str, str]:
    empty_home = CONTROL / "empty-home"
    temporary = CONTROL / "tmp"
    empty_home.mkdir(parents=True, exist_ok=True)
    temporary.mkdir(parents=True, exist_ok=True)
    return {
        "CI": "1",
        "HOME": str(empty_home),
        "LANG": "C.UTF-8",
        "NEXT_TELEMETRY_DISABLED": "1",
        "PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/sbin:/sbin"),
        "TMPDIR": str(temporary),
    }


def offline(command: list[str], env: dict[str, str], name: str, timeout: int = 600) -> dict[str, Any]:
    completed = run(
        ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command],
        cwd=WORKSPACE,
        env=env,
        timeout=timeout,
    )
    raw = completed.stdout + completed.stderr
    atomic_write(CONTROL / f"{name}.log", raw)
    return {"exit": completed.returncode, "log_sha256": digest(raw), "name": name}


def validate_lockfile() -> dict[str, Any]:
    lock = json.loads((WORKSPACE / "package-lock.json").read_text(encoding="utf-8"))
    urls = sorted(
        value["resolved"]
        for value in lock.get("packages", {}).values()
        if isinstance(value, dict) and isinstance(value.get("resolved"), str)
    )
    if any(not url.startswith("https://registry.npmjs.org/") for url in urls):
        raise PreparationError("DEPENDENCY_URL_NOT_ALLOWLISTED")
    return {
        "lockfile_sha256": digest(WORKSPACE / "package-lock.json"),
        "lockfile_version": lock.get("lockfileVersion"),
        "package_entries": len(lock.get("packages", {})),
        "resolved_urls": len(urls),
    }


def main() -> int:
    if CAMPAIGN.exists():
        raise PreparationError("EV1_T02_CAMPAIGN_ALREADY_EXISTS")
    CONTROL.mkdir(parents=True, mode=0o700)
    WORKSPACE.mkdir(parents=True, mode=0o700)
    rows = source_rows()
    export_source(rows)
    baseline_commit = initialize_baseline()
    dependency = clone_dependencies()
    lockfile = validate_lockfile()
    atomic_write(CONTROL / "offline.sb", b"(version 1)\n(allow default)\n(deny network*)\n")
    env = environment()

    dependency_tree = run(["npm", "ls", "--all", "--json"], cwd=WORKSPACE, env=env, timeout=120)
    dependency_raw = dependency_tree.stdout + dependency_tree.stderr
    atomic_write(CONTROL / "npm-ls.log", dependency_raw)
    if dependency_tree.returncode != 0:
        raise PreparationError("DEPENDENCY_TREE_INVALID")

    typecheck = offline(["npm", "run", "typecheck"], env, "baseline-typecheck")
    build = offline(["npm", "run", "build"], env, "baseline-build")
    missing_test = offline(
        ["npm", "run", "test:storage-contract"], env, "baseline-storage-contract"
    )
    if typecheck["exit"] != 0 or build["exit"] != 0 or missing_test["exit"] == 0:
        raise PreparationError("BASELINE_ACCEPTANCE_CALIBRATION_FAILED")

    status = git_workspace("status", "--porcelain=v1", "-uall")
    if status.returncode != 0 or status.stdout:
        raise PreparationError("BASELINE_WORKSPACE_NOT_CLEAN")

    body = {
        "version": "ev1-t02-preparation-receipt-v1",
        "status": "EV1_T02_READY_FOR_AUTONOMOUS_TASK_WORK",
        "task_id": TASK_ID,
        "task_start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "backlog_sha256": BACKLOG_SHA256,
        "preflight_packet_sha256": PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "source_commit": SOURCE_COMMIT,
        "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
        "source_permitted_files": len(rows),
        "source_excluded_files": sorted(EXCLUDED),
        "disposable_baseline_commit": baseline_commit,
        "workspace_relative": ".ev1-runtime/EV1-T02/workspace",
        "objective": "Add deterministic corrupt-storage and import-repair contract tests.",
        "acceptance_commands": [
            "npm run typecheck",
            "npm run build",
            "npm run test:storage-contract",
        ],
        "expected_state_mix": ["COMMITTED", "UNCOMMITTED", "UNTRACKED"],
        "human_edit_required": False,
        "baseline": {
            "typecheck": typecheck,
            "build": build,
            "storage_contract_absent": missing_test,
        },
        "dependency": dependency,
        "dependency_tree_log_sha256": digest(dependency_raw),
        "lockfile": lockfile,
        "offline_profile_sha256": digest(CONTROL / "offline.sb"),
        "capture_started": False,
        "deletion_started": False,
        "recovery_started": False,
    }
    receipt_hash, file_hash = atomic_record(CONTROL / "PREPARATION_RECEIPT.json", body)
    print(
        canonical(
            {
                "file_sha256": file_hash,
                "receipt_sha256": receipt_hash,
                "status": body["status"],
                "task_start_utc": body["task_start_utc"],
            }
        ).decode()
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired, PreparationError) as exc:
        print(canonical({"status": "EV1_T02_PREPARATION_BLOCKED", "reason": str(exc)}).decode())
        raise SystemExit(1)
