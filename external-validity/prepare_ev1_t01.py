#!/usr/bin/env python3
"""Prepare the exact EV1-T01 disposable workspace and stop at its human edit gate."""
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
EXCLUDED = {"CLAUDE.md"}
CAMPAIGN = ROOT / ".ev1-runtime" / "EV1-T01"
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
PRIVATE_MARKER = re.compile(
    rb"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY"
)
VERIFIER = r'''import fs from "node:fs";

const page = fs.readFileSync("src/app/page.tsx", "utf8");
const phrase = "Document every extraction.";
const occurrences = page.split(phrase).length - 1;
const semantic = /<(p|h[1-6])\b[^>]*>\s*Document every extraction\.\s*<\/\1>/m.test(page);

if (occurrences !== 1 || !semantic) {
  console.error("TAGLINE_MISSING_OR_NOT_SEMANTIC");
  process.exit(1);
}
console.log("TAGLINE_SEMANTIC_AND_UNIQUE");
'''


class PreparationError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


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


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 600) -> subprocess.CompletedProcess[bytes]:
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


def source_rows() -> list[dict[str, str]]:
    tree = git_source("ls-tree", "-r", SOURCE_COMMIT)
    if tree.returncode != 0:
        raise PreparationError("SOURCE_TREE_UNREADABLE")
    rows: list[dict[str, str]] = []
    for raw_line in tree.stdout.decode("utf-8").splitlines():
        metadata, path = raw_line.split("\t", 1)
        mode, object_type, blob = metadata.split(" ", 2)
        pure = PurePosixPath(path)
        if (
            object_type != "blob"
            or mode not in {"100644", "100755"}
            or pure.is_absolute()
            or ".." in pure.parts
            or "\x00" in path
        ):
            raise PreparationError("SOURCE_PATH_OR_MODE_UNSAFE")
        if path not in EXCLUDED:
            rows.append({"blob": blob, "mode": mode, "path": path})
    if len(rows) != 76 or digest(rows) != SOURCE_MANIFEST_SHA256:
        raise PreparationError("SOURCE_MANIFEST_MISMATCH")
    return rows


def safe_target(relative: str) -> Path:
    target = WORKSPACE.joinpath(*PurePosixPath(relative).parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    resolved_parent = target.parent.resolve(strict=True)
    try:
        resolved_parent.relative_to(WORKSPACE.resolve(strict=True))
    except ValueError as error:
        raise PreparationError("EXPORT_PATH_ESCAPE") from error
    return target


def export_source(rows: list[dict[str, str]]) -> None:
    for row in rows:
        blob = git_source("show", f"{SOURCE_COMMIT}:{row['path']}")
        if blob.returncode != 0:
            raise PreparationError("SOURCE_BLOB_UNREADABLE")
        if PRIVATE_MARKER.search(blob.stdout):
            raise PreparationError("PERMITTED_SOURCE_PRIVATE_MARKER")
        target = safe_target(row["path"])
        atomic_write(target, blob.stdout, 0o755 if row["mode"] == "100755" else 0o644)


def git_workspace(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return run(["git", *arguments], cwd=WORKSPACE, timeout=120)


def initialize_baseline() -> str:
    commands = (
        ["init", "-b", "main"],
        ["config", "user.name", "EV1 Disposable Campaign"],
        ["config", "user.email", "ev1@invalid.local"],
        ["add", "-A"],
        ["commit", "-m", "Bind EV1-T01 source baseline"],
    )
    for arguments in commands:
        completed = git_workspace(*arguments)
        if completed.returncode != 0:
            raise PreparationError("DISPOSABLE_GIT_BASELINE_FAILED")
    head = git_workspace("rev-parse", "HEAD")
    if head.returncode != 0:
        raise PreparationError("DISPOSABLE_GIT_HEAD_MISSING")
    return head.stdout.decode("ascii").strip()


def dependency_environment() -> dict[str, str]:
    cache = CONTROL / "npm-cache"
    cache.mkdir(parents=True, exist_ok=True)
    user_config = CONTROL / "empty.npmrc"
    atomic_write(user_config, b"registry=https://registry.npmjs.org/\n", 0o600)
    return {
        "CI": "1",
        "LANG": "C.UTF-8",
        "NEXT_TELEMETRY_DISABLED": "1",
        "NPM_CONFIG_AUDIT": "false",
        "NPM_CONFIG_CACHE": str(cache),
        "NPM_CONFIG_FUND": "false",
        "NPM_CONFIG_USERCONFIG": str(user_config),
        "PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/sbin:/sbin"),
        "TMPDIR": os.environ.get("TMPDIR", "/private/tmp"),
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


def record_command(name: str, completed: subprocess.CompletedProcess[bytes]) -> dict[str, Any]:
    raw = completed.stdout + completed.stderr
    atomic_write(CONTROL / f"{name}.log", raw)
    return {"exit": completed.returncode, "log_sha256": digest(raw), "name": name}


def offline(command: list[str], env: dict[str, str], name: str, timeout: int = 600) -> dict[str, Any]:
    completed = run(
        ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command],
        cwd=WORKSPACE,
        env=env,
        timeout=timeout,
    )
    return record_command(name, completed)


def main() -> int:
    if CAMPAIGN.exists():
        raise SystemExit("EV1_T01_CAMPAIGN_ALREADY_EXISTS")
    CONTROL.mkdir(parents=True, mode=0o700)
    WORKSPACE.mkdir(parents=True, mode=0o700)
    rows = source_rows()
    export_source(rows)
    baseline_commit = initialize_baseline()
    lock = validate_lockfile()
    env = dependency_environment()

    install = run(
        ["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"],
        cwd=WORKSPACE,
        env=env,
        timeout=600,
    )
    install_record = record_command("npm-ci", install)
    if install.returncode != 0:
        raise PreparationError("DEPENDENCY_INSTALL_FAILED")
    dependency_tree = run(["npm", "ls", "--all", "--json"], cwd=WORKSPACE, env=env, timeout=120)
    dependency_record = record_command("npm-ls", dependency_tree)
    if dependency_tree.returncode != 0:
        raise PreparationError("DEPENDENCY_TREE_INVALID")

    verifier_path = WORKSPACE / "scripts" / "verify-home-tagline.mjs"
    atomic_write(verifier_path, VERIFIER.encode("utf-8"), 0o644)
    profile = b"(version 1)\n(allow default)\n(deny network*)\n"
    atomic_write(CONTROL / "offline.sb", profile, 0o600)

    typecheck = offline(["npm", "run", "typecheck"], env, "baseline-typecheck")
    build = offline(["npm", "run", "build"], env, "baseline-build")
    verifier = offline(["node", "scripts/verify-home-tagline.mjs"], env, "baseline-tagline-verifier")
    if typecheck["exit"] != 0 or build["exit"] != 0 or verifier["exit"] != 1:
        raise PreparationError("BASELINE_ACCEPTANCE_CALIBRATION_FAILED")

    status = git_workspace("status", "--porcelain=v1", "-uall")
    if status.returncode != 0:
        raise PreparationError("DISPOSABLE_GIT_STATUS_FAILED")
    status_lines = status.stdout.decode("utf-8").splitlines()
    if status_lines != ["?? scripts/verify-home-tagline.mjs"]:
        raise PreparationError("PRE_HUMAN_STATE_MIX_UNEXPECTED")

    start_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    body = {
        "acceptance_command": "npm run typecheck && npm run build && node scripts/verify-home-tagline.mjs",
        "backlog_sha256": BACKLOG_SHA256,
        "baseline": {"build": build, "tagline_verifier": verifier, "typecheck": typecheck},
        "dependency_install": install_record,
        "dependency_tree": dependency_record,
        "disposable_baseline_commit": baseline_commit,
        "human_edit": {
            "file": "src/app/page.tsx",
            "required": True,
            "semantic_element": "p",
            "text": "Document every extraction.",
            "status": "PENDING_KENNETH_VISIBLE_SAVE",
        },
        "lockfile": lock,
        "measured_clock_started": True,
        "offline_profile_sha256": digest(CONTROL / "offline.sb"),
        "preflight_packet_sha256": PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "source_commit": SOURCE_COMMIT,
        "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
        "source_permitted_files": len(rows),
        "source_excluded_files": 1,
        "state_before_human_edit": status_lines,
        "status": "EV1_T01_READY_FOR_HUMAN_EDIT",
        "task_id": "EV1-T01",
        "task_start_utc": start_utc,
        "version": "ev1-t01-preparation-receipt-v1",
        "workspace_relative": ".ev1-runtime/EV1-T01/workspace",
    }
    body["receipt_sha256"] = digest(body)
    atomic_write(CONTROL / "PREPARATION_RECEIPT.json", canonical(body) + b"\n")
    print(canonical({"receipt_sha256": body["receipt_sha256"], "status": body["status"], "task_start_utc": start_utc}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
