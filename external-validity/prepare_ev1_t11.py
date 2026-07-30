#!/usr/bin/env python3
"""Prepare the exact-commit disposable EV1-T11 workspace and offline runtime."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import time
from typing import Any

from canary_ev1_t11_runtime import declared_links
from canary_ev1_t11_runtime_r2 import resolved_links, tree_manifest


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "EV1-T11"
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
DEPENDENCY_RUNTIME = CAMPAIGN / "dependency-runtime" / "node_modules"
SOURCE = Path("/Users/kennethruedas/master-vault/tools/step-realtime-cli")
SOURCE_COMMIT = "ee6862f7d65d24d4de11eda8306d29356873b529"
SOURCE_MANIFEST_SHA256 = "6f81e7e81ad100b53163a13b11c5e7abcd437fe658f817e34905c02cbe0e7182"
SOURCE_FILE_COUNT = 410
BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
GLOBAL_EV1_PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
LOCK_SHA256 = "c16bd11ac537f1e60402f867ac2b1ac62a0479889addb879e284b3f1d3465c36"
DEPENDENCY_SOURCE = ROOT / ".ev1-runtime" / "EV1-T09" / "dependency-attempt-r1-node_modules"
DEPENDENCY_MANIFEST_SHA256 = "bda7fc8f96d452960e7174cc6b84f05708f763ebf2e10dbdd40a1eca87b06dbe"
PINNED_PNPM_SOURCE = ROOT / ".ev1-runtime" / "EV1-T10" / "control" / "pnpm-runtime"
PNPM_SHA256 = "b276da51dc8ca5b0d3ee3371695b50fc8b3244b281b091c63a3f082a88dadeb9"
CANARY_RECEIPT = CAMPAIGN / "canary-r4" / "CANARY_RECEIPT.json"
CANARY_FILE_SHA256 = "e9ec4056a738bfad2b6a1d8a6eb5d82ec30a7dcd843fc480a312f2a39bc50f3a"
CANARY_RECEIPT_SHA256 = "d0db196763cab9888086191c0260543bd447cd0bde55d672fc4bc26927ef0476"
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


def run(command: list[str], *, cwd: Path, timeout: int = 900, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)


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
        if relative == ".git" or relative.startswith(".git/") or relative == "node_modules" or relative.startswith("node_modules/") or "/node_modules/" in relative or relative.endswith("/node_modules"):
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


def offline_env() -> dict[str, str]:
    fake_home = CONTROL / "fake-home"
    for path in (fake_home, CONTROL / "tmp", CONTROL / "xdg-cache", CONTROL / "xdg-config", CONTROL / "xdg-state"):
        path.mkdir(exist_ok=True)
    return {
        "CI": "1",
        "HOME": str(fake_home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "TMPDIR": str(CONTROL / "tmp"),
        "XDG_CACHE_HOME": str(CONTROL / "xdg-cache"),
        "XDG_CONFIG_HOME": str(CONTROL / "xdg-config"),
        "XDG_STATE_HOME": str(CONTROL / "xdg-state"),
    }


def offline(command: list[str], *, timeout: int = 900) -> subprocess.CompletedProcess[bytes]:
    return run(["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command], cwd=WORKSPACE, env=offline_env(), timeout=timeout)


def main() -> int:
    if CONTROL.exists() or WORKSPACE.exists() or DEPENDENCY_RUNTIME.exists():
        raise PreparationError("EV1_T11_TASK_RUNTIME_ALREADY_EXISTS")
    if not SOURCE.is_dir() or SOURCE.is_symlink():
        raise PreparationError("SOURCE_ROOT_UNSAFE")
    if digest(CANARY_RECEIPT) != CANARY_FILE_SHA256:
        raise PreparationError("CANARY_FILE_DRIFT")
    canary = json.loads(CANARY_RECEIPT.read_text())
    if canary.get("receipt_sha256") != CANARY_RECEIPT_SHA256 or canary.get("status") != "EV1_T11_DEPENDENCY_CANARY_R4_GREEN":
        raise PreparationError("CANARY_RECEIPT_DRIFT")
    rows = source_rows()
    if len(rows) != SOURCE_FILE_COUNT or digest(rows) != SOURCE_MANIFEST_SHA256:
        raise PreparationError("SOURCE_MANIFEST_DRIFT")
    forbidden = [row["path"] for row in rows if Path(row["path"]).name.lower() in {".env", "credentials.json", "secrets.json", "id_rsa", "id_ed25519"} or Path(row["path"]).suffix.lower() in {".pem", ".p12", ".pfx"}]
    if forbidden:
        raise PreparationError("SOURCE_FORBIDDEN_TRACKED_FILE")
    grep = run(["git", "grep", "-I", "-E", "(/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY)", SOURCE_COMMIT, "--"], cwd=SOURCE)
    if grep.returncode not in (0, 1) or grep.returncode == 0:
        raise PreparationError("SOURCE_PRIVATE_MARKER")
    if not DEPENDENCY_SOURCE.is_dir() or DEPENDENCY_SOURCE.is_symlink() or not PINNED_PNPM_SOURCE.is_dir():
        raise PreparationError("PINNED_RUNTIME_INPUT_MISSING")
    if digest(PINNED_PNPM_SOURCE / "node_modules" / "pnpm" / "bin" / "pnpm.cjs") != PNPM_SHA256:
        raise PreparationError("PNPM_INPUT_DRIFT")
    dependency_input_manifest = tree_manifest(DEPENDENCY_SOURCE)
    if digest(dependency_input_manifest) != DEPENDENCY_MANIFEST_SHA256:
        raise PreparationError("DEPENDENCY_INPUT_MANIFEST_DRIFT")

    CONTROL.mkdir(parents=True, mode=0o700)
    archive = CONTROL / "source.tar"
    archived = run(["git", "archive", "--format=tar", "-o", str(archive), SOURCE_COMMIT], cwd=SOURCE)
    if archived.returncode != 0:
        raise PreparationError("SOURCE_ARCHIVE_FAILED")
    WORKSPACE.mkdir(mode=0o700)
    with tarfile.open(archive, "r:") as handle:
        for member in handle.getmembers():
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                raise PreparationError("ARCHIVE_ENTRY_UNSAFE")
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

    shutil.copytree(PINNED_PNPM_SOURCE, CONTROL / "pnpm-runtime", symlinks=True)
    DEPENDENCY_RUNTIME.parent.mkdir(mode=0o700)
    cloned_runtime = run(["/bin/cp", "-cR", str(DEPENDENCY_SOURCE), str(DEPENDENCY_RUNTIME)], cwd=ROOT)
    if cloned_runtime.returncode != 0 or digest(tree_manifest(DEPENDENCY_RUNTIME)) != DEPENDENCY_MANIFEST_SHA256:
        raise PreparationError("DEPENDENCY_RUNTIME_CLONE_DRIFT")
    cloned_workspace = run(["/bin/cp", "-cR", str(DEPENDENCY_RUNTIME), str(WORKSPACE / "node_modules")], cwd=ROOT)
    if cloned_workspace.returncode != 0 or digest(tree_manifest(WORKSPACE / "node_modules")) != DEPENDENCY_MANIFEST_SHA256:
        raise PreparationError("WORKSPACE_DEPENDENCY_CLONE_DRIFT")
    links = declared_links(WORKSPACE)
    atomic(CONTROL / "declared-links.json", canonical(links) + b"\n")
    link_count, broken, escapes = resolved_links(WORKSPACE / "node_modules", WORKSPACE)
    if broken or escapes:
        raise PreparationError("WORKSPACE_DEPENDENCY_LINK_CONTAINMENT_FAILED")
    profile = CONTROL / "offline.sb"
    atomic(profile, b"(version 1)\n(allow default)\n(deny network*)\n")

    for command in (["git", "init", "-b", "main"], ["git", "config", "user.name", "EV1 Disposable Campaign"], ["git", "config", "user.email", "ev1@invalid.local"], ["git", "add", "-A"], ["git", "commit", "-m", "Bind EV1-T11 public source baseline"]):
        completed = run(command, cwd=WORKSPACE)
        if completed.returncode != 0:
            raise PreparationError("DISPOSABLE_GIT_BASELINE_FAILED")
    head = run(["git", "rev-parse", "HEAD"], cwd=WORKSPACE)
    status = run(["git", "status", "--porcelain=v1", "-uall"], cwd=WORKSPACE)
    if head.returncode != 0 or status.returncode != 0 or status.stdout:
        raise PreparationError("BASELINE_GIT_STATE_INVALID")

    pnpm = CONTROL / "pnpm-runtime" / "node_modules" / "pnpm" / "bin" / "pnpm.cjs"
    prettier = offline(["/usr/local/bin/node", str(pnpm), "exec", "prettier", "--check", "docs/RELEASE.md"])
    atomic(CONTROL / "t11-baseline-prettier.log", prettier.stdout + prettier.stderr)
    tests = offline(["/usr/local/bin/node", str(pnpm), "test"])
    atomic(CONTROL / "t11-baseline-tests.log", tests.stdout + tests.stderr)
    if prettier.returncode != 0 or tests.returncode != 0:
        raise PreparationError("BASELINE_ACCEPTANCE_FAILED")
    if (WORKSPACE / "scripts" / "check-release-readiness.mjs").exists() or (WORKSPACE / "scripts" / "release-readiness-cases.json").exists():
        raise PreparationError("TASK_SURFACE_ALREADY_PRESENT")
    post_status = run(["git", "status", "--porcelain=v1", "-uall"], cwd=WORKSPACE)
    if post_status.returncode != 0 or post_status.stdout:
        raise PreparationError("BASELINE_TEST_MUTATION")

    manifest = workspace_manifest()
    body = {
        "version": "ev1-t11-preparation-receipt-v1",
        "status": "EV1_T11_READY_FOR_TASK_WORK",
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
        "workspace_relative": ".ev1-runtime/EV1-T11/workspace",
        "objective": "Add a local fail-closed npm release dry-run guard that never contacts npm.",
        "acceptance_command": "pnpm exec prettier --check docs/RELEASE.md scripts/check-release-readiness.mjs && node scripts/check-release-readiness.mjs --offline-dry-run && pnpm test",
        "expected_state_mix": ["COMMITTED", "UNCOMMITTED", "UNTRACKED"],
        "human_edit_required": False,
        "private_package_safeguard": True,
        "package_manager": "pnpm@10.17.0",
        "lockfile_sha256": LOCK_SHA256,
        "runtime": {
            "dependency_provenance": "EV1_T09_FAILED_DEPENDENCY_ATTEMPT_REQUALIFIED_FOR_T11_ONLY",
            "dependency_manifest_sha256": DEPENDENCY_MANIFEST_SHA256,
            "declared_link_count": len(links),
            "declared_links_sha256": digest(links),
            "symlink_count": link_count,
            "broken_links": 0,
            "escape_links": 0,
            "install_command_executed": False,
            "lifecycle_script_executed": False,
            "canary_file_sha256": CANARY_FILE_SHA256,
            "canary_receipt_sha256": CANARY_RECEIPT_SHA256,
            "pnpm_entry_sha256": PNPM_SHA256,
        },
        "baseline": {
            "prettier_exit": prettier.returncode,
            "prettier_log_sha256": digest(prettier.stdout + prettier.stderr),
            "tests_exit": tests.returncode,
            "tests_log_sha256": digest(tests.stdout + tests.stderr),
            "network_mode": "DENIED_SEATBELT",
        },
        "task_surface_absent_before_work": True,
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
