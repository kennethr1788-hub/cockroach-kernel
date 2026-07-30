#!/usr/bin/env python3
"""Verify and freeze EV1-T02 task work before the human capture declaration."""
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
TASK_ID = "EV1-T02"
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
PREPARATION = CONTROL / "PREPARATION_RECEIPT.json"
WORK_RECEIPT = CONTROL / "WORK_RECEIPT.json"
EXPECTED_PREPARATION_FILE_SHA256 = "1acd22bf030fc8c532327b002ca150a9b094456c263200aea0c4259b90e7a264"
EXPECTED_PREPARATION_RECEIPT_SHA256 = "e5d1057a384a653fb743ca92530aa5d79feaafb5f38a25792f721d70d44397f2"
EXPECTED_TASK_COMMIT = "769321ec9828948afdacc7856321495c0ffd40a6"
EXPECTED_STATUS = [" M package.json", "?? scripts/storage-contract-cases.cjs"]
DECLARED = (
    "package.json",
    "scripts/run-storage-contract.mjs",
    "scripts/storage-contract-cases.cjs",
)
PRIVATE_MARKER = re.compile(
    rb"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY"
)


class WorkError(RuntimeError):
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
    command: list[str], *, cwd: Path = WORKSPACE, env: dict[str, str] | None = None,
    timeout: int = 600,
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


def git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return run(["git", *arguments], timeout=120)


def safe_file(relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or "\x00" in relative:
        raise WorkError("DECLARED_PATH_UNSAFE")
    target = WORKSPACE.joinpath(*pure.parts)
    resolved = target.resolve(strict=True)
    if WORKSPACE.resolve(strict=True) not in resolved.parents:
        raise WorkError("DECLARED_PATH_ESCAPE")
    if target.is_symlink() or not target.is_file():
        raise WorkError("DECLARED_FILE_UNSAFE")
    return target


def environment() -> dict[str, str]:
    return {
        "CI": "1",
        "HOME": str(CONTROL / "empty-home"),
        "LANG": "C.UTF-8",
        "NEXT_TELEMETRY_DISABLED": "1",
        "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "TMPDIR": str(CONTROL / "tmp"),
    }


def offline(command: list[str], name: str, timeout: int = 600) -> dict[str, Any]:
    completed = run(
        ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command],
        env=environment(),
        timeout=timeout,
    )
    raw = completed.stdout + completed.stderr
    atomic_write(CONTROL / f"{name}.log", raw)
    return {
        "exit": completed.returncode,
        "log_bytes": len(raw),
        "log_sha256": digest(raw),
        "name": name,
    }


def preparation() -> dict[str, Any]:
    if not PREPARATION.is_file() or digest(PREPARATION) != EXPECTED_PREPARATION_FILE_SHA256:
        raise WorkError("PREPARATION_FILE_DRIFT")
    value = json.loads(PREPARATION.read_text(encoding="utf-8"))
    if value.get("receipt_sha256") != EXPECTED_PREPARATION_RECEIPT_SHA256:
        raise WorkError("PREPARATION_RECEIPT_DRIFT")
    if value.get("status") != "EV1_T02_READY_FOR_AUTONOMOUS_TASK_WORK":
        raise WorkError("PREPARATION_STATUS_INVALID")
    return value


def changed_paths(prepared: dict[str, Any]) -> dict[str, list[str]]:
    head = git("rev-parse", "HEAD")
    if head.returncode != 0 or head.stdout.decode().strip() != EXPECTED_TASK_COMMIT:
        raise WorkError("TASK_COMMIT_MISMATCH")
    committed = git("diff", "--name-only", f"{prepared['disposable_baseline_commit']}..HEAD")
    unstaged = git("diff", "--name-only")
    untracked = git("ls-files", "--others", "--exclude-standard")
    status = git("status", "--porcelain=v1", "-uall")
    if any(item.returncode != 0 for item in (committed, unstaged, untracked, status)):
        raise WorkError("TASK_GIT_INSPECTION_FAILED")
    result = {
        "committed": committed.stdout.decode().splitlines(),
        "uncommitted": unstaged.stdout.decode().splitlines(),
        "untracked": untracked.stdout.decode().splitlines(),
        "status": status.stdout.decode().splitlines(),
    }
    if result != {
        "committed": ["scripts/run-storage-contract.mjs"],
        "uncommitted": ["package.json"],
        "untracked": ["scripts/storage-contract-cases.cjs"],
        "status": EXPECTED_STATUS,
    }:
        raise WorkError(f"TASK_STATE_MIX_MISMATCH:{result}")
    if sorted(set(result["committed"] + result["uncommitted"] + result["untracked"])) != sorted(DECLARED):
        raise WorkError("DECLARED_WORK_UNITS_MISMATCH")
    return result


def main() -> int:
    if WORK_RECEIPT.exists():
        raise WorkError("EV1_T02_WORK_ALREADY_RECORDED")
    prepared = preparation()
    state = changed_paths(prepared)
    file_hashes: dict[str, str] = {}
    aggregate_bytes = 0
    for relative in DECLARED:
        target = safe_file(relative)
        raw = target.read_bytes()
        if PRIVATE_MARKER.search(raw):
            raise WorkError(f"DECLARED_FILE_PRIVATE_MARKER:{relative}")
        file_hashes[relative] = digest(raw)
        aggregate_bytes += len(raw)

    typecheck = offline(["/usr/local/bin/npm", "run", "typecheck"], "work-typecheck")
    build = offline(["/usr/local/bin/npm", "run", "build"], "work-build")
    test = offline(
        ["/usr/local/bin/npm", "run", "test:storage-contract"],
        "work-storage-contract",
    )
    if any(item["exit"] != 0 for item in (typecheck, build, test)):
        raise WorkError("PRE_LOSS_ACCEPTANCE_FAILED")

    repeats = [
        offline(
            ["/usr/local/bin/npm", "run", "test:storage-contract"],
            f"work-storage-contract-repeat-{index}",
        )
        for index in range(1, 6)
    ]
    if any(item["exit"] != 0 for item in repeats):
        raise WorkError("DETERMINISM_REPEAT_FAILED")
    if len({item["log_sha256"] for item in repeats}) != 1:
        raise WorkError("DETERMINISM_LOG_MISMATCH")
    temporary_residue = sorted(
        path.name for path in (CONTROL / "tmp").glob("brew-ledger-storage-contract-*")
    )
    if temporary_residue:
        raise WorkError("TASK_TEST_TEMP_RESIDUE")

    body = {
        "version": "ev1-t02-work-receipt-v1",
        "status": "EV1_T02_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED",
        "task_id": TASK_ID,
        "utc_recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "backlog_sha256": prepared["backlog_sha256"],
        "preflight_packet_sha256": prepared["preflight_packet_sha256"],
        "product_candidate": prepared["product_candidate"],
        "source_commit": prepared["source_commit"],
        "source_manifest_sha256": prepared["source_manifest_sha256"],
        "preparation_file_sha256": digest(PREPARATION),
        "preparation_receipt_sha256": prepared["receipt_sha256"],
        "disposable_baseline_commit": prepared["disposable_baseline_commit"],
        "task_commit": EXPECTED_TASK_COMMIT,
        "state_mix": state,
        "declared_paths": sorted(DECLARED),
        "declared_file_hashes": dict(sorted(file_hashes.items())),
        "declared_aggregate_bytes": aggregate_bytes,
        "acceptance": {"typecheck": typecheck, "build": build, "storage_contract": test},
        "determinism": {
            "executions": 5,
            "identical_log_sha256": repeats[0]["log_sha256"],
            "results": repeats,
        },
        "offline_profile_sha256": digest(CONTROL / "offline.sb"),
        "private_marker_matches": 0,
        "test_temp_residue": 0,
        "capture_started": False,
        "deletion_started": False,
        "recovery_started": False,
        "capture_declaration_required": True,
    }
    receipt_hash, file_hash = atomic_record(WORK_RECEIPT, body)
    print(
        canonical(
            {
                "file_sha256": file_hash,
                "receipt_sha256": receipt_hash,
                "status": body["status"],
            }
        ).decode()
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired, WorkError) as exc:
        print(canonical({"status": "EV1_T02_WORK_BLOCKED", "reason": str(exc)}).decode())
        raise SystemExit(1)
