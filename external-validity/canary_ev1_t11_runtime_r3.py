#!/usr/bin/env python3
"""Preserved R3 attempt with private-hoist-only external link resolution."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import time
from typing import Any

from canary_ev1_t11_runtime_r2 import (
    ROOT,
    SOURCE,
    SOURCE_COMMIT,
    LOCK_SHA256,
    DEPENDENCIES,
    PNPM,
    PNPM_SHA256,
    CanaryError,
    atomic,
    canonical,
    digest,
    resolved_links,
    run,
    tree_manifest,
)


CAMPAIGN = ROOT / ".ev1-runtime" / "EV1-T11" / "canary-r3"
WORKSPACE_PREFIXES = ("apps", "extensions", "packages", "skills")


def workspace_packages(workspace: Path) -> dict[str, Path]:
    manifests = [workspace / "package.json", workspace / "ui" / "package.json"]
    for prefix in WORKSPACE_PREFIXES:
        base = workspace / prefix
        if base.is_dir():
            manifests.extend(sorted(base.glob("*/package.json")))
    packages: dict[str, Path] = {}
    for manifest in manifests:
        if not manifest.is_file() or manifest.is_symlink():
            raise CanaryError("WORKSPACE_PACKAGE_MANIFEST_UNSAFE")
        package = json.loads(manifest.read_text())
        name = package.get("name")
        if not isinstance(name, str) or not name or name in packages:
            raise CanaryError("WORKSPACE_PACKAGE_NAME_INVALID")
        packages[name] = manifest.parent
    return packages


def declared_links(workspace: Path) -> list[dict[str, str]]:
    packages = workspace_packages(workspace)
    virtual_hoist = workspace / "node_modules" / ".pnpm" / "node_modules"
    rows: list[dict[str, str]] = []
    for importer_name, importer in sorted(packages.items()):
        if importer == workspace:
            continue
        package = json.loads((importer / "package.json").read_text())
        declarations: dict[str, str] = {}
        for field in ("dependencies", "devDependencies", "optionalDependencies"):
            value = package.get(field, {})
            if not isinstance(value, dict):
                raise CanaryError("WORKSPACE_DEPENDENCY_MAP_INVALID")
            for dependency, specifier in value.items():
                if dependency in declarations and declarations[dependency] != specifier:
                    raise CanaryError("WORKSPACE_DEPENDENCY_SPECIFIER_CONFLICT")
                declarations[dependency] = specifier
        for dependency, specifier in sorted(declarations.items()):
            if dependency in packages:
                if not isinstance(specifier, str) or not specifier.startswith("workspace:"):
                    raise CanaryError("LOCAL_DEPENDENCY_NOT_WORKSPACE_BOUND")
                target = packages[dependency]
                source = "workspace"
            else:
                target = virtual_hoist.joinpath(*dependency.split("/"))
                source = "virtual-hoist"
            if not target.exists() or target.is_symlink() and not target.resolve(strict=True).exists():
                raise CanaryError(f"DECLARED_DEPENDENCY_TARGET_MISSING:{importer_name}:{dependency}")
            link = importer / "node_modules" / Path(*dependency.split("/"))
            link.parent.mkdir(parents=True, exist_ok=True)
            if link.exists() or link.is_symlink():
                raise CanaryError("DECLARED_DEPENDENCY_LINK_ALREADY_EXISTS")
            relative = os.path.relpath(target, link.parent)
            os.symlink(relative, link)
            rows.append(
                {
                    "dependency": dependency,
                    "importer": importer.relative_to(workspace).as_posix() or ".",
                    "link": link.relative_to(workspace).as_posix(),
                    "source": source,
                    "specifier": str(specifier),
                    "target": relative,
                }
            )
    return rows


def main() -> int:
    if CAMPAIGN.exists():
        raise CanaryError("CANARY_R3_ALREADY_EXISTS")
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

    temporary = Path(tempfile.mkdtemp(prefix="ck-ev1-t11-canary-r3.", dir="/private/tmp"))
    workspace = temporary / "workspace"
    result: dict[str, Any] = {
        "version": "ev1-t11-runtime-canary-v3",
        "status": "EV1_T11_DEPENDENCY_CANARY_R3_BLOCKED",
        "source_commit": SOURCE_COMMIT,
        "dependency_provenance": "EV1_T09_FAILED_DEPENDENCY_ATTEMPT_REUSED_AS_T11_RUNTIME_ONLY",
        "dependency_input_manifest_sha256": input_manifest_sha256,
        "dependency_input_entries": len(input_manifest),
        "network_mode": "DENIED_SEATBELT",
        "install_command_executed": False,
        "lifecycle_script_executed": False,
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
        if output_manifest_sha256 != input_manifest_sha256:
            raise CanaryError("DEPENDENCY_CLONE_DRIFT")

        links = declared_links(workspace)
        atomic(CAMPAIGN / "declared-links.json", canonical(links) + b"\n")
        link_count, broken, escapes = resolved_links(workspace / "node_modules", workspace)
        result.update(
            {
                "dependency_output_manifest_sha256_before_declared_links": output_manifest_sha256,
                "declared_link_count": len(links),
                "declared_links_sha256": digest(links),
                "dependency_symlink_count_after_declared_links": link_count,
                "dependency_broken_links": broken,
                "dependency_escape_links": escapes,
            }
        )
        if broken:
            raise CanaryError("DEPENDENCY_BROKEN_LINKS_AFTER_RECONSTRUCTION")
        if escapes:
            raise CanaryError("DEPENDENCY_LINK_ESCAPE_AFTER_RECONSTRUCTION")

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
        result["status"] = "EV1_T11_DEPENDENCY_CANARY_R3_GREEN"
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
