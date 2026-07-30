#!/usr/bin/env python3
"""Preflight and perform the non-destructive EV1-T08 symlink capture."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TASK_ID = "EV1-T08"
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
OUTSIDE_TARGET = CAMPAIGN / "synthetic-outside-target.json"
WORK_RECEIPT = CONTROL / "WORK_RECEIPT.json"
AUTHORIZATION = ROOT / "EXTERNAL_VALIDITY_EV1_T08_CAPTURE_AUTHORIZATION_R1.md"
PREFLIGHT_RECEIPT = CONTROL / "CAPTURE_ONLY_PREFLIGHT_RECEIPT_R1.json"
PACKET = CONTROL / "EV1_T08_CAPTURE_ONLY_PREFLIGHT_PACKET_R1.md"
JUDGE_RECEIPT = CONTROL / "CAPTURE_ONLY_JUDGE_RECEIPT_R1.json"
RESULT_RECEIPT = CONTROL / "CAPTURE_INVALID_RESULT_RECEIPT.json"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
PRODUCT_SURFACE_SHA256 = "bf13e0cdac3a846c48308ad79c89772e1b533a73dec340f13e25180500f69586"
PRODUCT_PACKAGE_INIT_SHA256 = "f6a6f83bb26dd4cdcf469b4a4c8a086bee885b0ecc1f5d471baaf5a7eddbb321"
P7_RUNTIME_HASHES = {
    "p7-recovery/__init__.py": "488eaa0346f1dc7f07e5508e8c4248cbd8c3e9a50da0eb229979063f6d9fa784",
    "p7-recovery/fresh_context.py": "4fbe7ff002bcb26ceb649295a4a4e94d79f7aecbab10eff1e7a75d1c63c577f7",
    "p7-recovery/records.py": "97971f48852e94ada7ecabb7dd0390442b4bde11f38fbdb069b10d396355fd34",
}
BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
GLOBAL_EV1_PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
WORK_RECEIPT_FILE_SHA256 = "cd9f6293427dce01e855fcc310327310a6a7719b31814d0741202fac30cabfdf"
WORK_RECEIPT_SHA256 = "561e1d4bde9c67dd4f19435f59ee1bd9e68bca89a0e4e59f0d6d21121bb03c1f"
TASK_COMMIT = "6b81ce4eb1f1d7a6e83b733ef18d92cf7c44c178"
EXPECTED_STATUS = [
    " M lib/signals.ts",
    " M package.json",
    "?? data/escape-sample-signals.json",
]
EXPECTED_REGULAR_HASHES = {
    "lib/dataPath.ts": "236c286423ce180d3610f23b8eba6d8d26f6053eb85bab7c7061e915dbdab8a3",
    "lib/signals.ts": "e3a5df95cc3ee10ea49e3ec721986c8f457b6d43fcef4faad493357b1f9f2c09",
    "package.json": "694389f6aa0a6d1bc43a1fc512fec35ce64cdbce864ccbaf88db247dd4ade2b1",
    "scripts/run-data-path-containment.mjs": "f046e58fdab9e7f9c19ae8420485e7295fda1c321bb04be9388dfcb6df021289",
}
SYMLINK_RELATIVE = "data/escape-sample-signals.json"
SYMLINK_TEXT = "../../synthetic-outside-target.json"
EXPECTED_TARGET_METADATA = {
    "inode": 300917240,
    "mode": 33152,
    "mtime_ns": 1785443575334394987,
    "size": 79,
}
DECLARATION = (
    "I, Kenneth, explicitly declare the exact current EV1-T08 state—committed "
    "lib/dataPath.ts and scripts/run-data-path-containment.mjs at task commit "
    "6b81ce4eb1f1d7a6e83b733ef18d92cf7c44c178, modified lib/signals.ts and "
    "package.json, and untracked symlink data/escape-sample-signals.json pointing "
    "to ../../synthetic-outside-target.json—permitted for capture only under the "
    "frozen EV1 protocol. I understand the predeclared outcome is "
    "INVALID_UNSAFE_SYMLINK_ESCAPE; the synthetic target must not be read, "
    "modified, or deleted, and after INVALID, workspace deletion and recovery are "
    "forbidden."
)
DECLARATION_UTC = "2026-07-30T20:41:11Z"


class T08Error(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: bytes | Path) -> str:
    raw = value.read_bytes() if isinstance(value, Path) else value
    return hashlib.sha256(raw).hexdigest()


def atomic_record(path: Path, body: dict[str, Any]) -> tuple[str, str]:
    receipt_hash = digest(canonical(body))
    raw = canonical(dict(body, receipt_sha256=receipt_hash)) + b"\n"
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
    return receipt_hash, digest(raw)


def load_receipt(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if not raw.endswith(b"\n"):
        raise T08Error(f"RECEIPT_NOT_CANONICAL:{path.name}")
    value = json.loads(raw[:-1])
    if canonical(value) + b"\n" != raw:
        raise T08Error(f"RECEIPT_NOT_CANONICAL:{path.name}")
    body = {key: value[key] for key in value if key != "receipt_sha256"}
    if value.get("receipt_sha256") != digest(canonical(body)):
        raise T08Error(f"RECEIPT_HASH_MISMATCH:{path.name}")
    return value


def safe_regular_file(relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or "\x00" in relative:
        raise T08Error("DECLARED_PATH_UNSAFE")
    current = WORKSPACE
    for index, part in enumerate(pure.parts):
        current = current / part
        mode = current.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise T08Error("DECLARED_REGULAR_FILE_SYMLINK")
        if index < len(pure.parts) - 1 and not stat.S_ISDIR(mode):
            raise T08Error("DECLARED_PARENT_NOT_DIRECTORY")
        if index == len(pure.parts) - 1 and not stat.S_ISREG(mode):
            raise T08Error("DECLARED_FILE_NOT_REGULAR")
    return current


def metadata(path: Path) -> dict[str, int]:
    observed = os.stat(path, follow_symlinks=False)
    return {
        "inode": observed.st_ino,
        "mode": observed.st_mode,
        "mtime_ns": observed.st_mtime_ns,
        "size": observed.st_size,
    }


def git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *arguments], cwd=WORKSPACE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=120)


def verify_state() -> dict[str, Any]:
    if digest(WORK_RECEIPT) != WORK_RECEIPT_FILE_SHA256:
        raise T08Error("WORK_RECEIPT_FILE_DRIFT")
    receipt = load_receipt(WORK_RECEIPT)
    if receipt.get("receipt_sha256") != WORK_RECEIPT_SHA256 or receipt.get("status") != "EV1_T08_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED":
        raise T08Error("WORK_RECEIPT_DRIFT")
    head = git("rev-parse", "HEAD")
    status_result = git("status", "--porcelain=v1", "-uall")
    if head.returncode != 0 or head.stdout.decode().strip() != TASK_COMMIT:
        raise T08Error("TASK_COMMIT_DRIFT")
    status_lines = status_result.stdout.decode().splitlines()
    if status_result.returncode != 0 or status_lines != EXPECTED_STATUS:
        raise T08Error("TASK_STATUS_DRIFT")
    regular_hashes = {relative: digest(safe_regular_file(relative)) for relative in sorted(EXPECTED_REGULAR_HASHES)}
    if regular_hashes != EXPECTED_REGULAR_HASHES or receipt.get("declared_regular_file_hashes") != EXPECTED_REGULAR_HASHES:
        raise T08Error("TASK_REGULAR_FILE_HASH_DRIFT")
    link = WORKSPACE / SYMLINK_RELATIVE
    link_metadata = metadata(link)
    if not stat.S_ISLNK(link_metadata["mode"]) or os.readlink(link) != SYMLINK_TEXT:
        raise T08Error("TASK_SYMLINK_DRIFT")
    target_metadata = metadata(OUTSIDE_TARGET)
    if target_metadata != EXPECTED_TARGET_METADATA:
        raise T08Error("OUTSIDE_TARGET_METADATA_DRIFT")
    return {
        "git_status": status_lines,
        "task_commit": TASK_COMMIT,
        "regular_file_hashes": regular_hashes,
        "regular_file_inodes": {relative: safe_regular_file(relative).stat().st_ino for relative in sorted(EXPECTED_REGULAR_HASHES)},
        "workspace_inode": WORKSPACE.stat().st_ino,
        "symlink": {"inode": link_metadata["inode"], "mode": link_metadata["mode"], "path": SYMLINK_RELATIVE, "target_text": SYMLINK_TEXT},
        "outside_target_metadata": target_metadata,
        "outside_target_content_read": False,
    }


def product_surface() -> Any:
    package_init = ROOT / "cockroach_kernel" / "__init__.py"
    surface_path = ROOT / "cockroach_kernel" / "recovery_surface.py"
    if digest(package_init) != PRODUCT_PACKAGE_INIT_SHA256 or digest(surface_path) != PRODUCT_SURFACE_SHA256:
        raise T08Error("PRODUCT_SURFACE_DRIFT")
    for relative, expected in {"cockroach_kernel/__init__.py": PRODUCT_PACKAGE_INIT_SHA256, "cockroach_kernel/recovery_surface.py": PRODUCT_SURFACE_SHA256, **P7_RUNTIME_HASHES}.items():
        shown = subprocess.run(["git", "show", f"{PRODUCT_CANDIDATE}:{relative}"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=120)
        if shown.returncode != 0 or digest(shown.stdout) != expected or digest(ROOT / relative) != expected:
            raise T08Error(f"PRODUCT_CANDIDATE_BINDING_DRIFT:{relative}")
    if importlib.util.find_spec("p7_runtime") is None:
        package_root = ROOT / "p7-recovery"
        package_spec = importlib.util.spec_from_file_location("p7_runtime", package_root / "__init__.py", submodule_search_locations=[str(package_root)])
        if package_spec is None or package_spec.loader is None:
            raise T08Error("PRODUCT_P7_RUNTIME_IMPORT_FAILED")
        package_module = importlib.util.module_from_spec(package_spec)
        sys.modules["p7_runtime"] = package_module
        package_spec.loader.exec_module(package_module)
    return importlib.import_module("cockroach_kernel.recovery_surface")


def exercise_symlink(surface: Any, root: Path, relative: str) -> tuple[str, str, str]:
    try:
        surface._safe_relative_file(root, relative)
    except surface.SurfaceError as exc:
        if exc.reason != "REPRESENTATION_UNSAFE" or exc.verdict != "INVALID" or exc.action_taken != "NONE":
            raise T08Error("PRODUCT_INVALID_SEMANTICS_DRIFT") from exc
        return exc.reason, exc.verdict, exc.action_taken
    raise T08Error("UNSAFE_SYMLINK_ACCEPTED")


def forbidden_paths() -> tuple[Path, ...]:
    return (
        CAMPAIGN / "recovery",
        CAMPAIGN / "representations",
        CAMPAIGN / "representation",
        CAMPAIGN / "successor",
        Path("/private/tmp/ck-ev1-t08-r1"),
    )


def assert_no_recovery_state() -> None:
    if any(path.exists() or path.is_symlink() for path in forbidden_paths()):
        raise T08Error("FORBIDDEN_POST_INVALID_PATH_EXISTS")


def preflight() -> int:
    if PREFLIGHT_RECEIPT.exists() or RESULT_RECEIPT.exists():
        raise T08Error("PREFLIGHT_ALREADY_STARTED")
    state = verify_state()
    assert_no_recovery_state()
    surface = product_surface()
    canary_root = CONTROL / ".capture-preflight-canary"
    nested = canary_root / "nested"
    link = nested / "escape"
    if canary_root.exists() or canary_root.is_symlink():
        raise T08Error("PREFLIGHT_CANARY_RESIDUE")
    canary_root.mkdir(mode=0o700)
    nested.mkdir(mode=0o700)
    os.symlink("../../nonexistent-target", link)
    try:
        reason, verdict, action = exercise_symlink(surface, canary_root, "nested/escape")
    finally:
        os.unlink(link)
        os.rmdir(nested)
        os.rmdir(canary_root)
    if canary_root.exists() or canary_root.is_symlink():
        raise T08Error("PREFLIGHT_CANARY_TEARDOWN_FAILED")
    body = {
        "version": "ev1-t08-capture-only-preflight-v1",
        "status": "EV1_T08_CAPTURE_ONLY_PREFLIGHT_R1_GREEN",
        "task_id": TASK_ID,
        "authorization_sha256": digest(AUTHORIZATION),
        "backlog_sha256": BACKLOG_SHA256,
        "global_ev1_preflight_packet_sha256": GLOBAL_EV1_PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "product_package_init_sha256": PRODUCT_PACKAGE_INIT_SHA256,
        "product_surface_sha256": PRODUCT_SURFACE_SHA256,
        "p7_runtime_sha256": P7_RUNTIME_HASHES,
        "runner_sha256": digest(Path(__file__).resolve()),
        "state": state,
        "canary": {"target_exists": False, "target_content_read": False, "verdict": verdict, "reason": reason, "action_taken": action, "teardown_green": True},
        "workspace_present": WORKSPACE.is_dir(),
        "workspace_unchanged": verify_state() == state,
        "representation_created": False,
        "successor_created": False,
        "deletion_started": False,
        "recovery_started": False,
    }
    receipt_hash, file_hash = atomic_record(PREFLIGHT_RECEIPT, body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


def capture() -> int:
    if RESULT_RECEIPT.exists():
        raise T08Error("CAPTURE_ALREADY_TERMINAL")
    preflighted = load_receipt(PREFLIGHT_RECEIPT)
    judged = load_receipt(JUDGE_RECEIPT)
    if preflighted.get("status") != "EV1_T08_CAPTURE_ONLY_PREFLIGHT_R1_GREEN" or preflighted.get("runner_sha256") != digest(Path(__file__).resolve()):
        raise T08Error("LOCAL_PREFLIGHT_NOT_GREEN_OR_RUNNER_DRIFT")
    local_packet_sha256 = digest(PACKET)
    if judged.get("status") != "EV1_T08_CAPTURE_ONLY_R1_JUDGES_GREEN" or judged.get("local_capture_packet_sha256") != local_packet_sha256:
        raise T08Error("INDEPENDENT_PREFLIGHT_NOT_GREEN")
    if judged.get("glm_verdict") != "GREEN" or judged.get("agy_verdict") != "GREEN":
        raise T08Error("INDEPENDENT_PREFLIGHT_NOT_GREEN")
    before = verify_state()
    assert_no_recovery_state()
    surface = product_surface()
    reason, verdict, action = exercise_symlink(surface, WORKSPACE, SYMLINK_RELATIVE)
    after = verify_state()
    assert_no_recovery_state()
    if after != before:
        raise T08Error("CAPTURE_MUTATED_STATE")
    body = {
        "version": "ev1-t08-capture-invalid-result-v1",
        "status": "EV1_T08_CLOSED_EXPECTED_INVALID",
        "task_id": TASK_ID,
        "capture_declaration": DECLARATION,
        "capture_declaration_utc": DECLARATION_UTC,
        "authorization_sha256": digest(AUTHORIZATION),
        "global_ev1_preflight_packet_sha256": GLOBAL_EV1_PREFLIGHT_PACKET_SHA256,
        "local_capture_packet_sha256": local_packet_sha256,
        "local_capture_judge_receipt_sha256": judged["receipt_sha256"],
        "product_candidate": PRODUCT_CANDIDATE,
        "product_package_init_sha256": PRODUCT_PACKAGE_INIT_SHA256,
        "product_surface_sha256": PRODUCT_SURFACE_SHA256,
        "observed_product_reason": reason,
        "campaign_outcome": "INVALID_UNSAFE_SYMLINK_ESCAPE",
        "verdict": verdict,
        "action_taken": action,
        "workspace_state_before": before,
        "workspace_state_after": after,
        "workspace_present": WORKSPACE.is_dir(),
        "workspace_unchanged": True,
        "symlink_followed": False,
        "outside_target_content_read": False,
        "outside_target_metadata_unchanged": before["outside_target_metadata"] == after["outside_target_metadata"],
        "representation_created": False,
        "successor_created": False,
        "deletion_started": False,
        "recovery_started": False,
        "scoring_classification": "EXPECTED_INVALID_SAFETY_RESULT_NOT_SUCCESSFUL_CONTINUATION",
        "utc_recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    receipt_hash, file_hash = atomic_record(RESULT_RECEIPT, body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("preflight", "capture"))
    phase = parser.parse_args().phase
    try:
        return preflight() if phase == "preflight" else capture()
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired, T08Error) as exc:
        print(canonical({"phase": phase, "reason": str(exc) or exc.__class__.__name__, "status": "EV1_T08_CAPTURE_ONLY_BLOCKED"}).decode())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
