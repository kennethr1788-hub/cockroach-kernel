#!/usr/bin/env python3
"""Preserved R2 attempt to requalify the offline EV1-T11 runtime."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/kennethruedas/master-vault/tools/step-realtime-cli")
SOURCE_COMMIT = "ee6862f7d65d24d4de11eda8306d29356873b529"
LOCK_SHA256 = "c16bd11ac537f1e60402f867ac2b1ac62a0479889addb879e284b3f1d3465c36"
DEPENDENCIES = ROOT / ".ev1-runtime" / "EV1-T09" / "dependency-attempt-r1-node_modules"
PNPM = ROOT / ".ev1-runtime" / "EV1-T10" / "control" / "pnpm-runtime" / "node_modules" / "pnpm" / "bin" / "pnpm.cjs"
PNPM_SHA256 = "b276da51dc8ca5b0d3ee3371695b50fc8b3244b281b091c63a3f082a88dadeb9"
CAMPAIGN = ROOT / ".ev1-runtime" / "EV1-T11" / "canary-r2"
PRIVATE = (b"/Users/", b"AKIA", b"BEGIN PRIVATE KEY", b"ghp_")


class CanaryError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: bytes | Path | Any) -> str:
    raw = value.read_bytes() if isinstance(value, Path) else value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def atomic(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 900) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)


def tree_manifest(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            rows.append({"kind": "symlink", "path": relative, "target": os.readlink(path)})
        elif path.is_file():
            rows.append({"bytes": path.stat().st_size, "kind": "file", "path": relative, "sha256": digest(path)})
        elif path.is_dir():
            rows.append({"kind": "directory", "path": relative})
        else:
            raise CanaryError("DEPENDENCY_SPECIAL_FILE")
    return rows


def resolved_links(root: Path, workspace: Path) -> tuple[int, list[str], list[str]]:
    count = 0
    broken: list[str] = []
    escapes: list[str] = []
    allowed = workspace.resolve(strict=True)
    for path in sorted(root.rglob("*")):
        if not path.is_symlink():
            continue
        count += 1
        try:
            target = path.resolve(strict=True)
        except FileNotFoundError:
            broken.append(path.relative_to(root).as_posix())
            continue
        if target != allowed and allowed not in target.parents:
            escapes.append(path.relative_to(root).as_posix())
    return count, broken, escapes


def main() -> int:
    if CAMPAIGN.exists():
        raise CanaryError("CANARY_R2_ALREADY_EXISTS")
    if not DEPENDENCIES.is_dir() or DEPENDENCIES.is_symlink():
        raise CanaryError("DEPENDENCY_INPUT_UNSAFE")
    if not PNPM.is_file() or digest(PNPM) != PNPM_SHA256:
        raise CanaryError("PNPM_INPUT_DRIFT")
    identity = run(["git", "cat-file", "-e", f"{SOURCE_COMMIT}^{{commit}}"], cwd=SOURCE)
    if identity.returncode != 0:
        raise CanaryError("SOURCE_COMMIT_MISSING")

    CAMPAIGN.mkdir(parents=True, mode=0o700)
    input_manifest = tree_manifest(DEPENDENCIES)
    input_manifest_sha256 = digest(input_manifest)
    atomic(CAMPAIGN / "dependency-input-manifest.json", canonical(input_manifest) + b"\n")

    temporary = Path(tempfile.mkdtemp(prefix="ck-ev1-t11-canary-r2.", dir="/private/tmp"))
    workspace = temporary / "workspace"
    result: dict[str, Any] = {
        "version": "ev1-t11-runtime-canary-v2",
        "status": "EV1_T11_DEPENDENCY_CANARY_R2_BLOCKED",
        "source_commit": SOURCE_COMMIT,
        "dependency_provenance": "EV1_T09_FAILED_DEPENDENCY_ATTEMPT_REUSED_AS_T11_RUNTIME_ONLY",
        "dependency_input_manifest_sha256": input_manifest_sha256,
        "dependency_input_entries": len(input_manifest),
        "network_mode": "DENIED_SEATBELT",
        "task_work_started": False,
        "product_candidate_changed": False,
        "source_repository_changed": False,
    }
    try:
        workspace.mkdir(mode=0o700)
        archive = temporary / "source.tar"
        exported = run(["git", "archive", "--format=tar", "-o", str(archive), SOURCE_COMMIT], cwd=SOURCE)
        if exported.returncode != 0:
            raise CanaryError("SOURCE_ARCHIVE_FAILED")
        with tarfile.open(archive, "r:") as handle:
            for member in handle.getmembers():
                path = Path(member.name)
                if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                    raise CanaryError("SOURCE_ARCHIVE_ENTRY_UNSAFE")
            handle.extractall(workspace)
        archive.unlink()
        if digest(workspace / "pnpm-lock.yaml") != LOCK_SHA256:
            raise CanaryError("LOCKFILE_DRIFT")

        cloned = run(["/bin/cp", "-cR", str(DEPENDENCIES), str(workspace / "node_modules")], cwd=temporary, timeout=900)
        atomic(CAMPAIGN / "copy.log", cloned.stdout + cloned.stderr)
        if cloned.returncode != 0:
            raise CanaryError(f"DEPENDENCY_CLONE_FAILED:{cloned.returncode}")
        output_manifest = tree_manifest(workspace / "node_modules")
        output_manifest_sha256 = digest(output_manifest)
        atomic(CAMPAIGN / "dependency-output-manifest.json", canonical(output_manifest) + b"\n")
        if output_manifest_sha256 != input_manifest_sha256:
            raise CanaryError("DEPENDENCY_CLONE_DRIFT")
        link_count, broken, escapes = resolved_links(workspace / "node_modules", workspace)
        result["dependency_output_manifest_sha256"] = output_manifest_sha256
        result["dependency_symlink_count"] = link_count
        result["dependency_broken_links"] = broken
        result["dependency_escape_links"] = escapes
        if broken:
            raise CanaryError("DEPENDENCY_BROKEN_LINKS_AFTER_CLONE")
        if escapes:
            raise CanaryError("DEPENDENCY_LINK_ESCAPE_AFTER_CLONE")

        fake_home = temporary / "fake-home"
        tmp = temporary / "tmp"
        xdg_cache = temporary / "xdg-cache"
        xdg_config = temporary / "xdg-config"
        xdg_state = temporary / "xdg-state"
        for path in (fake_home, tmp, xdg_cache, xdg_config, xdg_state):
            path.mkdir(mode=0o700)
        profile = temporary / "offline.sb"
        profile.write_text("(version 1)\n(allow default)\n(deny network*)\n")
        environment = {
            "CI": "1",
            "HOME": str(fake_home),
            "LANG": "C.UTF-8",
            "LC_ALL": "C",
            "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "TMPDIR": str(tmp),
            "XDG_CACHE_HOME": str(xdg_cache),
            "XDG_CONFIG_HOME": str(xdg_config),
            "XDG_STATE_HOME": str(xdg_state),
        }
        started = time.monotonic()
        tested = run(
            ["/usr/bin/sandbox-exec", "-f", str(profile), "/usr/local/bin/node", str(PNPM), "test"],
            cwd=workspace,
            env=environment,
            timeout=900,
        )
        elapsed_ms = round((time.monotonic() - started) * 1000)
        log = tested.stdout + tested.stderr
        atomic(CAMPAIGN / "pnpm-test.log", log)
        result.update(
            {
                "pnpm_test_exit": tested.returncode,
                "pnpm_test_elapsed_ms": elapsed_ms,
                "pnpm_test_log_bytes": len(log),
                "pnpm_test_log_sha256": digest(log),
            }
        )
        if tested.returncode != 0:
            raise CanaryError(f"FULL_TEST_SUITE_FAILED:{tested.returncode}")
        result["status"] = "EV1_T11_DEPENDENCY_CANARY_R2_GREEN"
    except (CanaryError, subprocess.TimeoutExpired) as error:
        result["blocker"] = str(error)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
        result["temporary_root_absent"] = not temporary.exists()
        result["utc_recorded"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        receipt_hash = digest(result)
        raw = canonical(dict(result, receipt_sha256=receipt_hash)) + b"\n"
        atomic(CAMPAIGN / "CANARY_RECEIPT.json", raw)
        print(canonical({"file_sha256": digest(raw), "receipt_sha256": receipt_hash, "status": result["status"]}).decode())
    return 0 if result["status"].endswith("_GREEN") else 1


if __name__ == "__main__":
    raise SystemExit(main())
