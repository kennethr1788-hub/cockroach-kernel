#!/usr/bin/env python3
"""Verify and freeze EV1-T04 task work before capture."""
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
TASK_ID = "EV1-T04"
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
PREPARATION = CONTROL / "PREPARATION_RECEIPT.json"
WORK_RECEIPT = CONTROL / "WORK_RECEIPT.json"
EXPECTED_PREPARATION_FILE_SHA256 = "27ce9f904902d6d322776504bc79d9b4f8dddc968820c305bf996b6f323e0809"
EXPECTED_PREPARATION_RECEIPT_SHA256 = "f38d933177ee6674d082cea1a175673fa4ae94d3444206123788d76e2c32b3bd"
EXPECTED_TASK_COMMIT = "c27bb9b9023a5b8ce4f5fb7cfa8fdf9d157b3502"
DECLARED = (
    "package.json",
    "scripts/dashboard-date-cases.cjs",
    "scripts/run-dashboard-date.mjs",
    "src/app/page.tsx",
    "src/lib/dashboardDate.ts",
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


def environment(timezone: str | None = None) -> dict[str, str]:
    result = {
        "CI": "1",
        "HOME": str(CONTROL / "empty-home"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        "NEXT_TELEMETRY_DISABLED": "1",
        "PATH": f"{WORKSPACE / 'node_modules' / '.bin'}:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "TMPDIR": str(CONTROL / "tmp"),
    }
    if timezone is not None:
        result["TZ"] = timezone
    return result


def offline(
    command: list[str], name: str, *, timezone: str | None = None, timeout: int = 600
) -> dict[str, Any]:
    completed = run(
        ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command],
        env=environment(timezone),
        timeout=timeout,
    )
    raw = completed.stdout + completed.stderr
    atomic_write(CONTROL / f"{name}.log", raw)
    return {
        "exit": completed.returncode,
        "log_bytes": len(raw),
        "log_sha256": digest(raw),
        "name": name,
        "timezone": timezone,
    }


def preparation() -> dict[str, Any]:
    if not PREPARATION.is_file() or digest(PREPARATION) != EXPECTED_PREPARATION_FILE_SHA256:
        raise WorkError("PREPARATION_FILE_DRIFT")
    value = json.loads(PREPARATION.read_text(encoding="utf-8"))
    if value.get("receipt_sha256") != EXPECTED_PREPARATION_RECEIPT_SHA256:
        raise WorkError("PREPARATION_RECEIPT_DRIFT")
    if value.get("status") != "EV1_T04_READY_FOR_AUTONOMOUS_TASK_WORK":
        raise WorkError("PREPARATION_STATUS_INVALID")
    return value


def changed_paths(prepared: dict[str, Any]) -> dict[str, list[str]]:
    head = git("rev-parse", "HEAD")
    if head.returncode != 0 or head.stdout.decode().strip() != EXPECTED_TASK_COMMIT:
        raise WorkError("TASK_COMMIT_MISMATCH")
    commands = {
        "committed": ("diff", "--name-only", f"{prepared['disposable_baseline_commit']}..HEAD"),
        "uncommitted": ("diff", "--name-only"),
        "untracked": ("ls-files", "--others", "--exclude-standard"),
        "status": ("status", "--porcelain=v1", "-uall"),
    }
    result: dict[str, list[str]] = {}
    for name, arguments in commands.items():
        completed = git(*arguments)
        if completed.returncode != 0:
            raise WorkError("TASK_GIT_INSPECTION_FAILED")
        result[name] = completed.stdout.decode().splitlines()
    expected = {
        "committed": ["scripts/run-dashboard-date.mjs", "src/lib/dashboardDate.ts"],
        "uncommitted": ["package.json", "src/app/page.tsx"],
        "untracked": ["scripts/dashboard-date-cases.cjs"],
        "status": [" M package.json", " M src/app/page.tsx", "?? scripts/dashboard-date-cases.cjs"],
    }
    if result != expected:
        raise WorkError(f"TASK_STATE_MIX_MISMATCH:{result}")
    paths = sorted(set(result["committed"] + result["uncommitted"] + result["untracked"]))
    if paths != sorted(DECLARED):
        raise WorkError("DECLARED_WORK_UNITS_MISMATCH")
    return result


def main() -> int:
    if WORK_RECEIPT.exists():
        raise WorkError("EV1_T04_WORK_ALREADY_RECORDED")
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

    pacific = offline(
        ["/usr/local/bin/npm", "run", "test:dashboard-date"],
        "work-dashboard-date-pacific",
        timezone="America/Los_Angeles",
    )
    utc = offline(
        ["/usr/local/bin/npm", "run", "test:dashboard-date"],
        "work-dashboard-date-utc",
        timezone="UTC",
    )
    typecheck = offline(["/usr/local/bin/npm", "run", "typecheck"], "work-typecheck")
    build = offline(["/usr/local/bin/npm", "run", "build"], "work-build")
    if any(item["exit"] != 0 for item in (pacific, utc, typecheck, build)):
        raise WorkError("PRE_LOSS_ACCEPTANCE_FAILED")

    repeated: dict[str, list[dict[str, Any]]] = {}
    for label, timezone in (("pacific", "America/Los_Angeles"), ("utc", "UTC")):
        repeated[label] = [
            offline(
                ["/usr/local/bin/npm", "run", "test:dashboard-date"],
                f"work-dashboard-date-{label}-repeat-{index}",
                timezone=timezone,
            )
            for index in range(1, 6)
        ]
        if any(item["exit"] != 0 for item in repeated[label]):
            raise WorkError("DETERMINISM_REPEAT_FAILED")
        if len({item["log_sha256"] for item in repeated[label]}) != 1:
            raise WorkError("DETERMINISM_LOG_MISMATCH")

    temporary_residue = sorted(
        path.name for path in (CONTROL / "tmp").glob("brew-ledger-dashboard-date-*")
    )
    if temporary_residue:
        raise WorkError("TASK_TEST_TEMP_RESIDUE")

    body = {
        "version": "ev1-t04-work-receipt-v1",
        "status": "EV1_T04_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED",
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
        "task_commits": [
            "82706e36143ce3909615254eaae30b9ffea1dfc3",
            EXPECTED_TASK_COMMIT,
        ],
        "state_mix": state,
        "declared_paths": sorted(DECLARED),
        "declared_file_hashes": dict(sorted(file_hashes.items())),
        "declared_aggregate_bytes": aggregate_bytes,
        "acceptance": {
            "dashboard_date_pacific": pacific,
            "dashboard_date_utc": utc,
            "typecheck": typecheck,
            "build": build,
        },
        "determinism": {
            "executions_per_timezone": 5,
            "pacific_identical_log_sha256": repeated["pacific"][0]["log_sha256"],
            "utc_identical_log_sha256": repeated["utc"][0]["log_sha256"],
            "results": repeated,
        },
        "implementation_corrections_before_freeze": [
            "standalone test compiler changed type-only import from tsconfig alias to relative path"
        ],
        "offline_profile_sha256": digest(CONTROL / "offline.sb"),
        "private_marker_matches": 0,
        "test_temp_residue": 0,
        "capture_started": False,
        "deletion_started": False,
        "recovery_started": False,
        "capture_declaration_required": True,
    }
    receipt_hash, file_hash = atomic_record(WORK_RECEIPT, body)
    print(canonical({
        "file_sha256": file_hash,
        "receipt_sha256": receipt_hash,
        "status": body["status"],
    }).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
