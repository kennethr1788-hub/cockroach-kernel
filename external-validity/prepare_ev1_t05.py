#!/usr/bin/env python3
"""Prepare the source-bound disposable EV1-T05 workspace.

The source commit intentionally has no lockfile.  This preparation step resolves
one dependency graph in a project-local cache with lifecycle scripts disabled,
freezes it, and proves the baseline under the network-denied verifier profile.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "EV1-T05"
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
SOURCE_COMMIT = "2c088ba8599c75cb02fbd61dfcf259d000729131"
EXPECTED_SOURCE_FILES = 19
BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
INCIDENT_LOG = CONTROL / "source-probe-unexpected-home-log.txt"
INCIDENT_LOG_SHA256 = "a822f559f20a7f33eb30f4b56055b4524f2bacc46c371dc7edde3c02f4d8e485"
ALLOWED_INITIAL_RELATIVE = {"control/source-probe-unexpected-home-log.txt"}
NPM_REGISTRY = "https://registry.npmjs.org/"
ATTEMPT1 = ROOT / ".ev1-runtime" / "EV1-T05-preparation-attempt-1"
ATTEMPT1_LOCK = ATTEMPT1 / "workspace" / "package-lock.json"
ATTEMPT1_LOCK_SHA256 = "7e0238617f56ecd9ab4c99bcc6d41a8a7e4c2635707c19247ddf082b94eacd7a"
ATTEMPT1_CACHE = ATTEMPT1 / "control" / "npm-cache"
ATTEMPT1_REPORT = ROOT / "EXTERNAL_VALIDITY_EV1_T05_PREPARATION_ATTEMPT1_R1.md"
ATTEMPT1_REPORT_SHA256 = "0f7be0a30e9599cca04861f64a27562c8277f133649b97e40f6ab93873c87c5a"


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
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    input_bytes: bytes | None = None,
    timeout: int = 900,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def git(source: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    return run(["git", *arguments], cwd=source, timeout=180)


def check_initial_campaign() -> None:
    if not CAMPAIGN.exists():
        raise PreparationError("CORRECTED_INCIDENT_EVIDENCE_MISSING")
    if CAMPAIGN.is_symlink() or CONTROL.is_symlink():
        raise PreparationError("CAMPAIGN_PATH_UNSAFE")
    existing = {
        path.relative_to(CAMPAIGN).as_posix()
        for path in CAMPAIGN.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    if existing != ALLOWED_INITIAL_RELATIVE:
        raise PreparationError(f"EV1_T05_UNEXPECTED_INITIAL_STATE:{sorted(existing)}")
    if not INCIDENT_LOG.is_file() or INCIDENT_LOG.is_symlink():
        raise PreparationError("CORRECTED_INCIDENT_LOG_UNSAFE")
    if digest(INCIDENT_LOG) != INCIDENT_LOG_SHA256:
        raise PreparationError("CORRECTED_INCIDENT_LOG_DRIFT")


def source_state(source: Path) -> None:
    if source.is_symlink() or not (source / ".git").is_dir():
        raise PreparationError("SOURCE_REPOSITORY_INVALID")
    head = git(source, "rev-parse", "HEAD")
    status = git(source, "status", "--porcelain=v1", "-uall")
    if head.returncode != 0 or head.stdout.decode("ascii").strip() != SOURCE_COMMIT:
        raise PreparationError("SOURCE_COMMIT_DRIFT")
    if status.returncode != 0 or status.stdout:
        raise PreparationError("SOURCE_CHECKOUT_NOT_CLEAN")


def source_entries(source: Path) -> list[dict[str, Any]]:
    listed = git(source, "ls-tree", "-rz", SOURCE_COMMIT)
    if listed.returncode != 0:
        raise PreparationError("SOURCE_TREE_LIST_FAILED")
    entries: list[dict[str, Any]] = []
    for record in listed.stdout.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split()
        relative = raw_path.decode("utf-8")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or "\x00" in relative:
            raise PreparationError("SOURCE_PATH_UNSAFE")
        if object_type != "blob" or mode == "120000":
            raise PreparationError("SOURCE_ENTRY_NOT_REGULAR_FILE")
        blob = run(["git", "cat-file", "blob", object_id], cwd=source, timeout=120)
        if blob.returncode != 0:
            raise PreparationError("SOURCE_BLOB_READ_FAILED")
        destination = WORKSPACE.joinpath(*pure.parts)
        atomic_write(destination, blob.stdout, mode=0o755 if mode == "100755" else 0o644)
        entries.append(
            {
                "bytes": len(blob.stdout),
                "git_mode": mode,
                "path": relative,
                "sha256": digest(blob.stdout),
            }
        )
    entries.sort(key=lambda item: item["path"])
    if len(entries) != EXPECTED_SOURCE_FILES:
        raise PreparationError("SOURCE_FILE_COUNT_MISMATCH")
    return entries


def isolated_environment() -> dict[str, str]:
    cache = CONTROL / "npm-cache"
    temporary = CONTROL / "tmp"
    xdg_config = CONTROL / "xdg-config"
    xdg_cache = CONTROL / "xdg-cache"
    xdg_state = CONTROL / "xdg-state"
    for path in (cache, temporary, xdg_config, xdg_cache, xdg_state):
        path.mkdir(parents=True, exist_ok=True)
    userconfig = CONTROL / "npmrc"
    atomic_write(userconfig, f"registry={NPM_REGISTRY}\n".encode("ascii"))
    return {
        "CI": "1",
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        "NEXT_TELEMETRY_DISABLED": "1",
        "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "TMPDIR": str(temporary),
        "XDG_CACHE_HOME": str(xdg_cache),
        "XDG_CONFIG_HOME": str(xdg_config),
        "XDG_STATE_HOME": str(xdg_state),
        "npm_config_audit": "false",
        "npm_config_cache": str(cache),
        "npm_config_fund": "false",
        "npm_config_ignore_scripts": "true",
        "npm_config_progress": "false",
        "npm_config_registry": NPM_REGISTRY,
        "npm_config_update_notifier": "false",
        "npm_config_userconfig": str(userconfig),
    }


def reuse_attempt1_dependency_resolution() -> dict[str, Any]:
    if digest(ATTEMPT1_REPORT) != ATTEMPT1_REPORT_SHA256:
        raise PreparationError("ATTEMPT1_REPORT_DRIFT")
    if digest(ATTEMPT1_LOCK) != ATTEMPT1_LOCK_SHA256:
        raise PreparationError("ATTEMPT1_LOCK_DRIFT")
    if ATTEMPT1_CACHE.is_symlink() or not ATTEMPT1_CACHE.is_dir():
        raise PreparationError("ATTEMPT1_CACHE_MISSING")
    atomic_write(WORKSPACE / "package-lock.json", ATTEMPT1_LOCK.read_bytes(), mode=0o644)
    destination = CONTROL / "npm-cache"
    completed = run(["cp", "-cR", str(ATTEMPT1_CACHE), str(destination)], cwd=ROOT, timeout=900)
    if completed.returncode != 0:
        raise PreparationError("ATTEMPT1_CACHE_CLONE_FAILED")
    return {
        "mode": "OFFLINE_REUSE_OF_PRESERVED_ATTEMPT1_LOCK_AND_CACHE",
        "attempt1_report_sha256": ATTEMPT1_REPORT_SHA256,
        "lockfile_sha256": ATTEMPT1_LOCK_SHA256,
        "cache_clone_mode": "APFS_COPY_ON_WRITE",
        "new_registry_resolution": False,
    }


def apply_platform_baseline_adaptations(entries: list[dict[str, Any]]) -> dict[str, Any]:
    original = {entry["path"]: entry["sha256"] for entry in entries}
    package_path = WORKSPACE / "package.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    scripts = package.get("scripts")
    if not isinstance(scripts, dict) or scripts.get("build") != "next build":
        raise PreparationError("SOURCE_BUILD_SCRIPT_DRIFT")
    scripts["build"] = "next build --webpack"
    atomic_write(
        package_path,
        (json.dumps(package, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        mode=0o644,
    )
    return {
        "reason": "NEXT16_TURBOPACK_INTERNAL_PORT_BIND_IS_DENIED_BY_OFFLINE_PROFILE",
        "official_cli_mode": "next build --webpack",
        "package_json_source_sha256": original["package.json"],
        "package_json_adapted_sha256": digest(package_path),
        "tsconfig_source_sha256": original["tsconfig.json"],
    }


def logged(
    command: list[str],
    *,
    env: dict[str, str],
    name: str,
    timeout: int = 900,
    offline: bool = False,
) -> dict[str, Any]:
    actual = command
    if offline:
        actual = ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command]
    completed = run(actual, cwd=WORKSPACE, env=env, timeout=timeout)
    raw = completed.stdout + completed.stderr
    atomic_write(CONTROL / f"{name}.log", raw)
    return {
        "exit": completed.returncode,
        "log_bytes": len(raw),
        "log_sha256": digest(raw),
        "network_mode": "DENIED_SEATBELT" if offline else "NPM_REGISTRY_SETUP",
    }


def validate_lockfile() -> dict[str, Any]:
    lock_path = WORKSPACE / "package-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    packages = lock.get("packages")
    if not isinstance(packages, dict):
        raise PreparationError("LOCKFILE_PACKAGES_INVALID")
    urls = sorted(
        value["resolved"]
        for value in packages.values()
        if isinstance(value, dict) and isinstance(value.get("resolved"), str)
    )
    if not urls or any(not url.startswith(NPM_REGISTRY) for url in urls):
        raise PreparationError("DEPENDENCY_URL_NOT_ALLOWLISTED")
    missing_integrity = sorted(
        path
        for path, value in packages.items()
        if path
        and isinstance(value, dict)
        and isinstance(value.get("resolved"), str)
        and not isinstance(value.get("integrity"), str)
    )
    if missing_integrity:
        raise PreparationError("LOCKFILE_INTEGRITY_MISSING")
    lifecycle_packages = sorted(
        path
        for path, value in packages.items()
        if path
        and isinstance(value, dict)
        and value.get("hasInstallScript") is True
    )
    return {
        "lockfile_sha256": digest(lock_path),
        "lockfile_version": lock.get("lockfileVersion"),
        "package_entries": len(packages),
        "resolved_urls": len(urls),
        "all_urls_allowlisted": True,
        "all_resolved_entries_have_integrity": True,
        "lifecycle_packages_present_but_not_executed": lifecycle_packages,
    }


def initialize_baseline() -> str:
    commands = (
        ["init", "-b", "main"],
        ["config", "user.name", "EV1 Disposable Campaign"],
        ["config", "user.email", "ev1@invalid.local"],
        ["add", "-A"],
        ["commit", "-m", "Bind EV1-T05 source and dependency baseline"],
    )
    for arguments in commands:
        completed = run(["git", *arguments], cwd=WORKSPACE, timeout=180)
        if completed.returncode != 0:
            raise PreparationError("DISPOSABLE_GIT_BASELINE_FAILED")
    head = run(["git", "rev-parse", "HEAD"], cwd=WORKSPACE, timeout=120)
    if head.returncode != 0:
        raise PreparationError("DISPOSABLE_GIT_HEAD_MISSING")
    return head.stdout.decode("ascii").strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    arguments = parser.parse_args()
    source = arguments.source.resolve(strict=True)

    check_initial_campaign()
    source_state(source)
    CONTROL.mkdir(parents=True, exist_ok=True, mode=0o700)
    WORKSPACE.mkdir(parents=True, mode=0o700)
    entries = source_entries(source)
    manifest_hash = digest(entries)
    reused_resolution = reuse_attempt1_dependency_resolution()
    env = isolated_environment()
    atomic_write(CONTROL / "offline.sb", b"(version 1)\n(allow default)\n(deny network*)\n")
    platform_adaptations = apply_platform_baseline_adaptations(entries)

    node_version = logged(["/usr/local/bin/node", "--version"], env=env, name="node-version")
    npm_version = logged(["/usr/local/bin/npm", "--version"], env=env, name="npm-version")
    if node_version["exit"] != 0 or npm_version["exit"] != 0:
        raise PreparationError("RUNTIME_VERSION_PROBE_FAILED")
    lockfile = validate_lockfile()
    install = logged(
        ["/usr/local/bin/npm", "ci", "--offline", "--ignore-scripts"],
        env=env,
        name="npm-ci",
        timeout=1800,
        offline=True,
    )
    if install["exit"] != 0:
        raise PreparationError("DEPENDENCY_INSTALL_FAILED")
    dependency_tree = logged(
        ["/usr/local/bin/npm", "ls", "--all", "--json"],
        env=env,
        name="npm-ls",
        timeout=300,
        offline=True,
    )
    if dependency_tree["exit"] != 0:
        raise PreparationError("DEPENDENCY_TREE_INVALID")

    first_build = logged(
        ["/usr/local/bin/npm", "run", "build"],
        env=env,
        name="baseline-build-platform-adaptation",
        timeout=1200,
        offline=True,
    )
    if first_build["exit"] != 0:
        raise PreparationError("PLATFORM_ADAPTED_BASELINE_BUILD_FAILED")
    platform_adaptations["first_build"] = first_build
    platform_adaptations["tsconfig_adapted_sha256"] = digest(WORKSPACE / "tsconfig.json")

    typecheck = logged(
        ["/usr/local/bin/npm", "run", "typecheck"],
        env=env,
        name="baseline-typecheck",
        offline=True,
    )
    build = logged(
        ["/usr/local/bin/npm", "run", "build"],
        env=env,
        name="baseline-build",
        timeout=1200,
        offline=True,
    )
    missing_test = logged(
        ["/usr/local/bin/npm", "run", "test:signal-schema"],
        env=env,
        name="baseline-signal-schema-absent",
        offline=True,
    )
    if typecheck["exit"] != 0 or build["exit"] != 0 or missing_test["exit"] == 0:
        raise PreparationError("BASELINE_ACCEPTANCE_CALIBRATION_FAILED")
    baseline_commit = initialize_baseline()
    status = run(["git", "status", "--porcelain=v1", "-uall"], cwd=WORKSPACE, timeout=120)
    if status.returncode != 0 or status.stdout:
        raise PreparationError("BASELINE_WORKSPACE_NOT_CLEAN")

    incident_body = {
        "version": "ev1-t05-preparation-incident-receipt-v1",
        "status": "UNEXPECTED_HOME_WRITE_CORRECTED_AND_RETAINED",
        "task_id": TASK_ID,
        "unexpected_write_kind": "NPM_DEBUG_LOG_FROM_READ_ONLY_SOURCE_PROBE",
        "original_home_path_present": False,
        "retained_relative_path": ".ev1-runtime/EV1-T05/control/source-probe-unexpected-home-log.txt",
        "retained_sha256": digest(INCIDENT_LOG),
        "remediation": "MOVED_INTO_PROJECT_LOCAL_CONTROL_ROOT_WITH_BYTES_PRESERVED",
        "preparation_continued_only_WITH_ISOLATED_NPM_CACHE_AND_CONFIG": True,
    }
    incident_receipt_hash, incident_file_hash = atomic_record(
        CONTROL / "PREPARATION_INCIDENT_RECEIPT.json", incident_body
    )

    body = {
        "version": "ev1-t05-preparation-receipt-v1",
        "status": "EV1_T05_READY_FOR_AUTONOMOUS_TASK_WORK",
        "task_id": TASK_ID,
        "task_start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "backlog_sha256": BACKLOG_SHA256,
        "preflight_packet_sha256": PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "source_commit": SOURCE_COMMIT,
        "source_file_count": len(entries),
        "source_manifest_sha256": manifest_hash,
        "source_checkout_used_only_as_exact_commit_object_store": True,
        "disposable_baseline_commit": baseline_commit,
        "workspace_relative": ".ev1-runtime/EV1-T05/workspace",
        "objective": (
            "Replace the unchecked JSON cast with a strict runtime schema rejecting duplicate IDs, "
            "invalid sources, malformed timestamps, empty titles, and non-array tags before analysis."
        ),
        "acceptance_commands": [
            "npm run typecheck",
            "npm run build",
            "npm run test:signal-schema",
        ],
        "expected_state_mix": ["COMMITTED", "UNCOMMITTED", "UNTRACKED"],
        "human_edit_required": False,
        "predeclared_refusal_or_invalid": "NONE",
        "data_classification": "SYNTHETIC",
        "dependency_setup": {
            "network_phase": "NONE_R2_REUSED_ATTEMPT1_LOCK_AND_CACHE",
            "registry": NPM_REGISTRY,
            "lifecycle_scripts": "DISABLED",
            "reused_resolution": reused_resolution,
            "install": install,
            "dependency_tree": dependency_tree,
            "node_version_log_sha256": node_version["log_sha256"],
            "npm_version_log_sha256": npm_version["log_sha256"],
            "lockfile": lockfile,
        },
        "baseline": {
            "typecheck": typecheck,
            "build": build,
            "signal_schema_test_absent": missing_test,
        },
        "platform_baseline_adaptations": platform_adaptations,
        "offline_profile_sha256": digest(CONTROL / "offline.sb"),
        "incident": {
            "status": incident_body["status"],
            "receipt_file_sha256": incident_file_hash,
            "receipt_sha256": incident_receipt_hash,
        },
        "capture_started": False,
        "deletion_started": False,
        "recovery_started": False,
    }
    receipt_hash, file_hash = atomic_record(CONTROL / "PREPARATION_RECEIPT.json", body)
    print(canonical({
        "file_sha256": file_hash,
        "receipt_sha256": receipt_hash,
        "source_manifest_sha256": manifest_hash,
        "status": body["status"],
    }).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
