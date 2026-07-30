#!/usr/bin/env python3
"""Prepare the exact-commit disposable EV1-T12 workspace and offline runtime."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import tarfile
import time

import prepare_ev1_t11 as BASE


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "EV1-T12"
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
DEPENDENCY_SOURCE = ROOT / ".ev1-runtime" / "EV1-T11" / "dependency-runtime" / "node_modules"
DEPENDENCY_MANIFEST_SHA256 = "bda7fc8f96d452960e7174cc6b84f05708f763ebf2e10dbdd40a1eca87b06dbe"
PINNED_PNPM_SOURCE = ROOT / ".ev1-runtime" / "EV1-T11" / "control" / "pnpm-runtime"
PNPM_SHA256 = "b276da51dc8ca5b0d3ee3371695b50fc8b3244b281b091c63a3f082a88dadeb9"
T11_TEARDOWN = ROOT / ".ev1-runtime" / "EV1-T11" / "control" / "TEARDOWN_RECEIPT.json"
T11_TEARDOWN_FILE_SHA256 = "09501fd4cace34bcbcbdb99a21d6d73de9a7db842998e93536e9829ff1695cd5"
T11_TEARDOWN_RECEIPT_SHA256 = "426179115273c393a787bf58aaa828059691b157821b9a9dc0b4735d9121e001"
PRIVATE = re.compile(rb"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY")


class PreparationError(RuntimeError):
    pass


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


def offline(command: list[str], *, timeout: int = 900):
    return BASE.run(
        ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command],
        cwd=WORKSPACE,
        env=offline_env(),
        timeout=timeout,
    )


def workspace_manifest() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(WORKSPACE.rglob("*")):
        relative = path.relative_to(WORKSPACE).as_posix()
        if relative == ".git" or relative.startswith(".git/") or "node_modules" in Path(relative).parts:
            continue
        if path.is_symlink():
            rows.append({"kind": "symlink", "path": relative, "target": os.readlink(path)})
        elif path.is_file():
            rows.append({"bytes": path.stat().st_size, "kind": "file", "path": relative, "sha256": BASE.digest(path)})
        elif path.is_dir():
            rows.append({"kind": "directory", "path": relative})
        else:
            raise PreparationError("SPECIAL_FILE_IN_WORKSPACE")
    return rows


def main() -> int:
    if CAMPAIGN.exists():
        raise PreparationError("EV1_T12_TASK_RUNTIME_ALREADY_EXISTS")
    if BASE.digest(T11_TEARDOWN) != T11_TEARDOWN_FILE_SHA256:
        raise PreparationError("T11_TEARDOWN_FILE_DRIFT")
    teardown = json.loads(T11_TEARDOWN.read_bytes())
    if teardown.get("receipt_sha256") != T11_TEARDOWN_RECEIPT_SHA256 or teardown.get("status") != "EV1_T11_TEMPORARY_SUCCESSOR_TEARDOWN_GREEN":
        raise PreparationError("T11_TEARDOWN_RECEIPT_DRIFT")
    if not SOURCE.is_dir() or SOURCE.is_symlink():
        raise PreparationError("SOURCE_ROOT_UNSAFE")
    rows = BASE.source_rows()
    if len(rows) != SOURCE_FILE_COUNT or BASE.digest(rows) != SOURCE_MANIFEST_SHA256:
        raise PreparationError("SOURCE_MANIFEST_DRIFT")
    forbidden = [row["path"] for row in rows if Path(row["path"]).name.lower() in {".env", "credentials.json", "secrets.json", "id_rsa", "id_ed25519"} or Path(row["path"]).suffix.lower() in {".pem", ".p12", ".pfx"}]
    if forbidden:
        raise PreparationError("SOURCE_FORBIDDEN_TRACKED_FILE")
    if not DEPENDENCY_SOURCE.is_dir() or DEPENDENCY_SOURCE.is_symlink() or not PINNED_PNPM_SOURCE.is_dir():
        raise PreparationError("PINNED_RUNTIME_INPUT_MISSING")
    if BASE.digest(PINNED_PNPM_SOURCE / "node_modules" / "pnpm" / "bin" / "pnpm.cjs") != PNPM_SHA256:
        raise PreparationError("PNPM_INPUT_DRIFT")
    dependency_manifest = BASE.tree_manifest(DEPENDENCY_SOURCE)
    if BASE.digest(dependency_manifest) != DEPENDENCY_MANIFEST_SHA256:
        raise PreparationError("DEPENDENCY_INPUT_MANIFEST_DRIFT")

    CONTROL.mkdir(parents=True, mode=0o700)
    archive = CONTROL / "source.tar"
    archived = BASE.run(["git", "archive", "--format=tar", "-o", str(archive), SOURCE_COMMIT], cwd=SOURCE)
    if archived.returncode != 0:
        raise PreparationError("SOURCE_ARCHIVE_FAILED")
    WORKSPACE.mkdir(mode=0o700)
    with tarfile.open(archive, "r:") as handle:
        for member in handle.getmembers():
            member_path = Path(member.name)
            if member_path.is_absolute() or ".." in member_path.parts or member.issym() or member.islnk():
                raise PreparationError("ARCHIVE_ENTRY_UNSAFE")
        handle.extractall(WORKSPACE)
    archive.unlink()
    extracted_files = [path for path in WORKSPACE.rglob("*") if path.is_file()]
    if len(extracted_files) != SOURCE_FILE_COUNT or any(PRIVATE.search(path.read_bytes()) for path in extracted_files):
        raise PreparationError("EXTRACTED_SOURCE_BOUNDARY_FAILED")
    if BASE.digest(WORKSPACE / "pnpm-lock.yaml") != LOCK_SHA256:
        raise PreparationError("LOCKFILE_DRIFT")
    package = json.loads((WORKSPACE / "package.json").read_text())
    if package.get("private") is not True or package.get("packageManager") != "pnpm@10.17.0":
        raise PreparationError("PRIVATE_PACKAGE_SAFEGUARD_DRIFT")

    shutil.copytree(PINNED_PNPM_SOURCE, CONTROL / "pnpm-runtime", symlinks=True)
    DEPENDENCY_RUNTIME.parent.mkdir(mode=0o700)
    for source, destination in ((DEPENDENCY_SOURCE, DEPENDENCY_RUNTIME), (DEPENDENCY_SOURCE, WORKSPACE / "node_modules")):
        completed = BASE.run(["/bin/cp", "-cR", str(source), str(destination)], cwd=ROOT)
        if completed.returncode != 0 or BASE.digest(BASE.tree_manifest(destination)) != DEPENDENCY_MANIFEST_SHA256:
            raise PreparationError("DEPENDENCY_RUNTIME_CLONE_DRIFT")
    links = BASE.declared_links(WORKSPACE)
    BASE.atomic(CONTROL / "declared-links.json", BASE.canonical(links) + b"\n")
    link_count, broken, escapes = BASE.resolved_links(WORKSPACE / "node_modules", WORKSPACE)
    if broken or escapes:
        raise PreparationError("WORKSPACE_DEPENDENCY_LINK_CONTAINMENT_FAILED")
    BASE.atomic(CONTROL / "offline.sb", b"(version 1)\n(allow default)\n(deny network*)\n")

    for command in (["git", "init", "-b", "main"], ["git", "config", "user.name", "EV1 Disposable Campaign"], ["git", "config", "user.email", "ev1@invalid.local"], ["git", "add", "-A"], ["git", "commit", "-m", "Bind EV1-T12 public source baseline"]):
        if BASE.run(command, cwd=WORKSPACE).returncode != 0:
            raise PreparationError("DISPOSABLE_GIT_BASELINE_FAILED")
    head = BASE.run(["git", "rev-parse", "HEAD"], cwd=WORKSPACE)
    if head.returncode != 0 or BASE.run(["git", "status", "--porcelain=v1", "-uall"], cwd=WORKSPACE).stdout:
        raise PreparationError("BASELINE_GIT_STATE_INVALID")

    pnpm = CONTROL / "pnpm-runtime" / "node_modules" / "pnpm" / "bin" / "pnpm.cjs"
    prettier = offline(["/usr/local/bin/node", str(pnpm), "exec", "prettier", "--check", "docs/RELEASE.md"])
    BASE.atomic(CONTROL / "t12-baseline-prettier.log", prettier.stdout + prettier.stderr)
    tests = offline(["/usr/local/bin/node", str(pnpm), "test"])
    BASE.atomic(CONTROL / "t12-baseline-tests.log", tests.stdout + tests.stderr)
    if prettier.returncode != 0 or tests.returncode != 0:
        raise PreparationError("BASELINE_ACCEPTANCE_FAILED")
    if (WORKSPACE / "scripts" / "build-release-manifest.mjs").exists() or (WORKSPACE / "scripts" / "build-release-manifest.test.ts").exists():
        raise PreparationError("TASK_SURFACE_ALREADY_PRESENT")
    if BASE.run(["git", "status", "--porcelain=v1", "-uall"], cwd=WORKSPACE).stdout:
        raise PreparationError("BASELINE_TEST_MUTATION")

    manifest = workspace_manifest()
    body = {
        "version": "ev1-t12-preparation-receipt-v1",
        "status": "EV1_T12_READY_FOR_TASK_WORK",
        "task_id": TASK_ID,
        "task_start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "backlog_sha256": BACKLOG_SHA256,
        "global_ev1_preflight_packet_sha256": GLOBAL_EV1_PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "source_commit": SOURCE_COMMIT,
        "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
        "source_file_count": SOURCE_FILE_COUNT,
        "workspace_manifest_sha256": BASE.digest(manifest),
        "workspace_file_count": len(extracted_files),
        "disposable_baseline_commit": head.stdout.decode().strip(),
        "workspace_relative": ".ev1-runtime/EV1-T12/workspace",
        "objective": "Add an offline deterministic binary checksum-manifest generator with duplicate-platform refusal and synthetic fixture tests.",
        "acceptance_command": "pnpm exec prettier --check docs/RELEASE.md scripts/build-release-manifest.mjs scripts/build-release-manifest.test.ts && pnpm vitest run scripts/build-release-manifest.test.ts",
        "expected_state_mix": ["COMMITTED", "UNCOMMITTED", "UNTRACKED"],
        "human_edit_required": False,
        "data_classification": "PUBLIC_PERMISSIVE_WITH_SYNTHETIC_BINARY_FIXTURES_ONLY",
        "external_release_action_authorized": False,
        "private_package_safeguard": True,
        "runtime": {
            "dependency_provenance": "EV1_T11_HASH_BOUND_OFFLINE_RUNTIME",
            "dependency_manifest_sha256": DEPENDENCY_MANIFEST_SHA256,
            "declared_link_count": len(links),
            "declared_links_sha256": BASE.digest(links),
            "symlink_count": link_count,
            "broken_links": 0,
            "escape_links": 0,
            "install_command_executed": False,
            "lifecycle_script_executed": False,
        },
        "baseline_acceptance": {
            "prettier_exit": prettier.returncode,
            "prettier_log_sha256": BASE.digest(CONTROL / "t12-baseline-prettier.log"),
            "full_tests_exit": tests.returncode,
            "full_tests_log_sha256": BASE.digest(CONTROL / "t12-baseline-tests.log"),
            "network_mode": "DENIED_SEATBELT",
        },
        "t11_teardown_file_sha256": T11_TEARDOWN_FILE_SHA256,
        "t11_teardown_receipt_sha256": T11_TEARDOWN_RECEIPT_SHA256,
    }
    receipt_hash, file_hash = BASE.record(CONTROL / "PREPARATION_RECEIPT.json", body)
    print(BASE.canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
