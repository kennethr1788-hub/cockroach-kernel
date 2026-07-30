#!/usr/bin/env python3
"""Verify and freeze EV1-T05 task work before capture."""
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
TASK_ID = "EV1-T05"
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
PREPARATION = CONTROL / "PREPARATION_RECEIPT.json"
WORK_RECEIPT = CONTROL / "WORK_RECEIPT.json"
EXPECTED_PREPARATION_FILE_SHA256 = "43836cc3bb9a6f8cfdd730c1c199cbe165a79b8d4afd73c2ebf842eac82c701f"
EXPECTED_PREPARATION_RECEIPT_SHA256 = "5236b6f4e65195579f54976e1cf76ac4e61be332650f654aa69000d1e49f893a"
EXPECTED_TASK_COMMIT = "63f151a50d6e4b28cc2091f22c045d785c0261c1"
DECLARED = (
    "lib/signalSchema.ts",
    "lib/signals.ts",
    "package.json",
    "scripts/run-signal-schema.mjs",
    "scripts/signal-schema-cases.cjs",
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


def run(command: list[str], *, timeout: int = 1200) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        cwd=WORKSPACE,
        env={
            "CI": "1",
            "LANG": "C.UTF-8",
            "LC_ALL": "C",
            "NEXT_TELEMETRY_DISABLED": "1",
            "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "TMPDIR": str(CONTROL / "tmp"),
            "XDG_CACHE_HOME": str(CONTROL / "xdg-cache"),
            "XDG_CONFIG_HOME": str(CONTROL / "xdg-config"),
            "XDG_STATE_HOME": str(CONTROL / "xdg-state"),
            "npm_config_cache": str(CONTROL / "npm-cache"),
            "npm_config_userconfig": str(CONTROL / "npmrc"),
            "npm_config_update_notifier": "false",
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return run(["git", *arguments], timeout=180)


def offline(command: list[str], name: str, *, timeout: int = 1200) -> dict[str, Any]:
    completed = run(
        ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command],
        timeout=timeout,
    )
    raw = completed.stdout + completed.stderr
    atomic_write(CONTROL / f"{name}.log", raw)
    return {
        "exit": completed.returncode,
        "log_bytes": len(raw),
        "log_sha256": digest(raw),
        "name": name,
        "network_mode": "DENIED_SEATBELT",
    }


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


def preparation() -> dict[str, Any]:
    if not PREPARATION.is_file() or digest(PREPARATION) != EXPECTED_PREPARATION_FILE_SHA256:
        raise WorkError("PREPARATION_FILE_DRIFT")
    value = json.loads(PREPARATION.read_text(encoding="utf-8"))
    if value.get("receipt_sha256") != EXPECTED_PREPARATION_RECEIPT_SHA256:
        raise WorkError("PREPARATION_RECEIPT_DRIFT")
    if value.get("status") != "EV1_T05_READY_FOR_AUTONOMOUS_TASK_WORK":
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
        "committed": ["lib/signalSchema.ts", "scripts/run-signal-schema.mjs"],
        "uncommitted": ["lib/signals.ts", "package.json"],
        "untracked": ["scripts/signal-schema-cases.cjs"],
        "status": [
            " M lib/signals.ts",
            " M package.json",
            "?? scripts/signal-schema-cases.cjs",
        ],
    }
    if result != expected:
        raise WorkError(f"TASK_STATE_MIX_MISMATCH:{result}")
    paths = sorted(set(result["committed"] + result["uncommitted"] + result["untracked"]))
    if paths != sorted(DECLARED):
        raise WorkError("DECLARED_WORK_UNITS_MISMATCH")
    return result


def static_contract() -> dict[str, Any]:
    loader = (WORKSPACE / "lib" / "signals.ts").read_text(encoding="utf-8")
    schema = (WORKSPACE / "lib" / "signalSchema.ts").read_text(encoding="utf-8")
    runner = (WORKSPACE / "scripts" / "run-signal-schema.mjs").read_text(encoding="utf-8")
    checks = {
        "unchecked_signal_array_cast_absent": "as Signal[]" not in loader,
        "loader_calls_runtime_parser": "parseSignalDataset(JSON.parse(raw))" in loader,
        "schema_is_strict": ".strict()" in schema,
        "duplicate_check_present": "firstIndexById" in schema and "Duplicate signal id" in schema,
        "actual_sample_dataset_exercised": "sample-signals.json" in runner and "sampleDataset.length, 12" in runner,
    }
    if not all(checks.values()):
        raise WorkError("STATIC_RUNTIME_VALIDATION_CONTRACT_FAILED")
    return checks


def main() -> int:
    if WORK_RECEIPT.exists():
        raise WorkError("EV1_T05_WORK_ALREADY_RECORDED")
    prepared = preparation()
    state = changed_paths(prepared)
    static_checks = static_contract()

    file_hashes: dict[str, str] = {}
    aggregate_bytes = 0
    for relative in DECLARED:
        raw = safe_file(relative).read_bytes()
        if PRIVATE_MARKER.search(raw):
            raise WorkError(f"DECLARED_FILE_PRIVATE_MARKER:{relative}")
        file_hashes[relative] = digest(raw)
        aggregate_bytes += len(raw)

    schema_test = offline(
        ["/usr/local/bin/npm", "run", "test:signal-schema"], "work-signal-schema"
    )
    typecheck = offline(["/usr/local/bin/npm", "run", "typecheck"], "work-typecheck")
    build = offline(["/usr/local/bin/npm", "run", "build"], "work-build")
    if any(item["exit"] != 0 for item in (schema_test, typecheck, build)):
        raise WorkError("PRE_LOSS_ACCEPTANCE_FAILED")

    repeated = [
        offline(
            ["/usr/local/bin/npm", "run", "test:signal-schema"],
            f"work-signal-schema-repeat-{index}",
        )
        for index in range(1, 6)
    ]
    if any(item["exit"] != 0 for item in repeated):
        raise WorkError("DETERMINISM_REPEAT_FAILED")
    if len({item["log_sha256"] for item in repeated}) != 1:
        raise WorkError("DETERMINISM_LOG_MISMATCH")

    body = {
        "version": "ev1-t05-work-receipt-v1",
        "status": "EV1_T05_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED",
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
            "e039a70b299754a391dc52a43dd886ec63a5eebe",
            EXPECTED_TASK_COMMIT,
        ],
        "state_mix": state,
        "declared_paths": sorted(DECLARED),
        "declared_file_hashes": dict(sorted(file_hashes.items())),
        "declared_aggregate_bytes": aggregate_bytes,
        "static_contract": static_checks,
        "acceptance": {
            "signal_schema": schema_test,
            "typecheck": typecheck,
            "build": build,
        },
        "determinism": {
            "executions": 5,
            "identical_log_sha256": repeated[0]["log_sha256"],
            "results": repeated,
        },
        "validated_dataset_records": 12,
        "adversarial_schema_cases": 8,
        "offline_profile_sha256": digest(CONTROL / "offline.sb"),
        "dependency_lock_sha256": prepared["dependency_setup"]["lockfile"]["lockfile_sha256"],
        "private_marker_matches": 0,
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
