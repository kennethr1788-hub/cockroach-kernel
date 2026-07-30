#!/usr/bin/env python3
"""Prepare the source-bound disposable EV1-T03 workspace."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "EV1-T03"
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
DEPENDENCY_SOURCE = ROOT / ".ev1-runtime" / "EV1-T02" / "dependency-runtime" / "node_modules"
T01_RUNNER = ROOT / "external-validity" / "run_ev1_t01.py"
T02_RUNNER = ROOT / "external-validity" / "run_ev1_t02.py"
T01_RUNNER_SHA256 = "daf88b6029cfb44bd183ab1af87dcd22c0213fc4ea27bbe90d62994086bc5271"
T02_RUNNER_SHA256 = "8db6767d881b5fd0d8e6c8a8b52e130d1f43b5fc232e7137d3106ee4143c784c"
T02_TEARDOWN = ROOT / ".ev1-runtime" / "EV1-T02" / "control" / "TEARDOWN_RECEIPT.json"
T02_TEARDOWN_FILE_SHA256 = "f047baccc911cac87301c9f758e71d28e831bb7d703767ced2849265369ef263"
SOURCE_COMMIT = "1a92380a9edf12337f80b3c42ba098a7c1724664"
SOURCE_MANIFEST_SHA256 = "d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706"
BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"


class PreparationError(RuntimeError):
    pass


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


def load_frozen(path: Path, expected_hash: str, name: str) -> Any:
    if digest(path) != expected_hash:
        raise PreparationError(f"{name}_SOURCE_DRIFT")
    spec = importlib.util.spec_from_file_location(name.lower(), path)
    if spec is None or spec.loader is None:
        raise PreparationError(f"{name}_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return run(["git", *arguments], cwd=WORKSPACE, timeout=120)


def initialize_baseline() -> str:
    commands = (
        ["init", "-b", "main"],
        ["config", "user.name", "EV1 Disposable Campaign"],
        ["config", "user.email", "ev1@invalid.local"],
        ["add", "-A"],
        ["commit", "-m", "Bind EV1-T03 source baseline"],
    )
    for arguments in commands:
        completed = git(*arguments)
        if completed.returncode != 0:
            raise PreparationError("DISPOSABLE_GIT_BASELINE_FAILED")
    head = git("rev-parse", "HEAD")
    if head.returncode != 0:
        raise PreparationError("DISPOSABLE_GIT_HEAD_MISSING")
    return head.stdout.decode("ascii").strip()


def clone_dependencies(t02: Any) -> dict[str, Any]:
    if DEPENDENCY_SOURCE.is_symlink() or not DEPENDENCY_SOURCE.is_dir():
        raise PreparationError("VERIFIED_DEPENDENCY_SOURCE_MISSING")
    source_shape = t02.dependency_shape(DEPENDENCY_SOURCE)
    destination = WORKSPACE / "node_modules"
    completed = run(["cp", "-cR", str(DEPENDENCY_SOURCE), str(destination)], cwd=ROOT)
    if completed.returncode != 0:
        raise PreparationError("DEPENDENCY_CLONE_FAILED")
    destination_shape = t02.dependency_shape(destination)
    if destination_shape != source_shape:
        raise PreparationError("DEPENDENCY_CLONE_SHAPE_MISMATCH")
    return {
        "source_relative": ".ev1-runtime/EV1-T02/dependency-runtime/node_modules",
        "clone_mode": "APFS_COPY_ON_WRITE",
        "shape": source_shape,
    }


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


def environment() -> dict[str, str]:
    empty_home = CONTROL / "empty-home"
    temporary = CONTROL / "tmp"
    empty_home.mkdir(parents=True, exist_ok=True)
    temporary.mkdir(parents=True, exist_ok=True)
    return {
        "CI": "1",
        "HOME": str(empty_home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        "NEXT_TELEMETRY_DISABLED": "1",
        "PATH": f"{WORKSPACE / 'node_modules' / '.bin'}:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
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
    return {"exit": completed.returncode, "log_bytes": len(raw), "log_sha256": digest(raw)}


def main() -> int:
    if CAMPAIGN.exists() or CAMPAIGN.is_symlink():
        raise PreparationError("EV1_T03_CAMPAIGN_ALREADY_EXISTS")
    if digest(T02_TEARDOWN) != T02_TEARDOWN_FILE_SHA256:
        raise PreparationError("T02_TEARDOWN_DRIFT")
    t01 = load_frozen(T01_RUNNER, T01_RUNNER_SHA256, "T01")
    t02 = load_frozen(T02_RUNNER, T02_RUNNER_SHA256, "T02")

    CONTROL.mkdir(parents=True, mode=0o700)
    WORKSPACE.mkdir(parents=True, mode=0o700)
    baseline_files = t01.export_baseline(WORKSPACE, omit=set())
    if baseline_files != 76:
        raise PreparationError("SOURCE_FILE_COUNT_MISMATCH")
    baseline_commit = initialize_baseline()
    dependency = clone_dependencies(t02)
    lockfile = validate_lockfile()
    atomic_write(CONTROL / "offline.sb", b"(version 1)\n(allow default)\n(deny network*)\n")
    env = environment()

    dependency_tree = run(["npm", "ls", "--all", "--json"], cwd=WORKSPACE, env=env, timeout=120)
    dependency_raw = dependency_tree.stdout + dependency_tree.stderr
    atomic_write(CONTROL / "npm-ls.log", dependency_raw)
    if dependency_tree.returncode != 0:
        raise PreparationError("DEPENDENCY_TREE_INVALID")

    typecheck = offline(["/usr/local/bin/npm", "run", "typecheck"], env, "baseline-typecheck")
    build = offline(["/usr/local/bin/npm", "run", "build"], env, "baseline-build")
    missing_test = offline(
        ["/usr/local/bin/npm", "run", "test:recipe-invariants"],
        env,
        "baseline-recipe-invariants",
    )
    if typecheck["exit"] != 0 or build["exit"] != 0 or missing_test["exit"] == 0:
        raise PreparationError("BASELINE_ACCEPTANCE_CALIBRATION_FAILED")
    status = git("status", "--porcelain=v1", "-uall")
    if status.returncode != 0 or status.stdout:
        raise PreparationError("BASELINE_WORKSPACE_NOT_CLEAN")

    body = {
        "version": "ev1-t03-preparation-receipt-v1",
        "status": "EV1_T03_READY_FOR_AUTONOMOUS_TASK_WORK",
        "task_id": TASK_ID,
        "task_start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "backlog_sha256": BACKLOG_SHA256,
        "preflight_packet_sha256": PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "source_commit": SOURCE_COMMIT,
        "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
        "source_permitted_files": baseline_files,
        "source_excluded_files": ["CLAUDE.md"],
        "disposable_baseline_commit": baseline_commit,
        "workspace_relative": ".ev1-runtime/EV1-T03/workspace",
        "objective": (
            "Add deterministic tests for monotonic version labels, exclusive favorite and dial-in "
            "pointers, cross-group rejection, and cascading cleanup of version-linked Quick Brews."
        ),
        "acceptance_commands": [
            "npm run typecheck",
            "npm run build",
            "npm run test:recipe-invariants",
        ],
        "expected_state_mix": ["COMMITTED", "UNCOMMITTED", "UNTRACKED"],
        "human_edit_required": False,
        "predeclared_refusal_or_invalid": "NONE",
        "data_classification": "SYNTHETIC",
        "baseline": {
            "typecheck": typecheck,
            "build": build,
            "recipe_invariants_absent": missing_test,
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
            {"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}
        ).decode("utf-8")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
