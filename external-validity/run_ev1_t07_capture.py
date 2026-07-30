#!/usr/bin/env python3
"""Preflight and perform the non-destructive EV1-T07 expected-invalid capture."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TASK_ID = "EV1-T07"
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
WORK_RECEIPT = CONTROL / "WORK_RECEIPT.json"
AUTHORIZATION = ROOT / "EXTERNAL_VALIDITY_EV1_T07_CAPTURE_AUTHORIZATION_R1.md"
PREFLIGHT_RECEIPT = CONTROL / "CAPTURE_ONLY_PREFLIGHT_RECEIPT_R2.json"
PACKET = CONTROL / "EV1_T07_CAPTURE_ONLY_PREFLIGHT_PACKET_R2.md"
JUDGE_RECEIPT = CONTROL / "CAPTURE_ONLY_JUDGE_RECEIPT_R2.json"
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
PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
WORK_RECEIPT_FILE_SHA256 = "6d9e2238c5c10419efdadad8e4435e91afa566a4f0150c441985ae1848f4288a"
WORK_RECEIPT_SHA256 = "485aed463767d66080f994ce5e7cb3b3b84eee671627006f07dd475481482e2b"
TASK_COMMIT = "f1b13c8a3b6fb2ba2affcdf358ccbc7535b626a9"
EXPECTED_STATUS = [
    " M app/api/analyze/route.ts",
    " M package.json",
    "?? fixtures/oversized-analyze-request.json",
]
EXPECTED_HASHES = {
    "app/api/analyze/route.ts": "54f50341759b0d7d8056b9ae97acef89df05ed5ef07ff6f5ca79c4526a3b03ec",
    "fixtures/oversized-analyze-request.json": "c0ac38a6ab2ea1f1c716f454b78c4c1491ed6be3ee4f7eff68ac72cc6b6d6280",
    "lib/requestLimits.ts": "7dc4505518406653ff91e89d1a02d6cdb2596aa6196cec67de23de50dc93b96e",
    "package.json": "bbd3cc1beee6ec05f7c87058db70afc8ca54e1c5e2e119777de482361c633959",
    "scripts/run-api-limits.mjs": "4293a154e9bf6a8f45f2b9604f8b810ed247fd701f8c4984aeda4bd0dc0c1d8c",
}
DECLARATION = (
    "I, Kenneth, explicitly declare the exact current EV1-T07 state—committed "
    "lib/requestLimits.ts and scripts/run-api-limits.mjs at task commit "
    "f1b13c8a3b6fb2ba2affcdf358ccbc7535b626a9, modified "
    "app/api/analyze/route.ts and package.json, and untracked exact 80 KiB "
    "fixtures/oversized-analyze-request.json—permitted for capture under the frozen "
    "EV1 protocol. I understand the predeclared outcome is INVALID_OVERSIZED_RECORD; "
    "after that INVALID result, deletion and recovery are forbidden and the workspace "
    "must remain intact."
)
DECLARATION_UTC = "2026-07-30T20:11:03Z"


class T07Error(RuntimeError):
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
        raise T07Error(f"RECEIPT_NOT_CANONICAL:{path.name}")
    value = json.loads(raw[:-1])
    if canonical(value) + b"\n" != raw:
        raise T07Error(f"RECEIPT_NOT_CANONICAL:{path.name}")
    body = {key: value[key] for key in value if key != "receipt_sha256"}
    if value.get("receipt_sha256") != digest(canonical(body)):
        raise T07Error(f"RECEIPT_HASH_MISMATCH:{path.name}")
    return value


def safe_file(relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or "\x00" in relative:
        raise T07Error("DECLARED_PATH_UNSAFE")
    target = WORKSPACE.joinpath(*pure.parts)
    resolved = target.resolve(strict=True)
    if WORKSPACE.resolve(strict=True) not in resolved.parents or target.is_symlink() or not target.is_file():
        raise T07Error("DECLARED_FILE_UNSAFE")
    return target


def git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *arguments], cwd=WORKSPACE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=120)


def verify_state() -> dict[str, Any]:
    if digest(WORK_RECEIPT) != WORK_RECEIPT_FILE_SHA256:
        raise T07Error("WORK_RECEIPT_FILE_DRIFT")
    receipt = load_receipt(WORK_RECEIPT)
    if receipt.get("receipt_sha256") != WORK_RECEIPT_SHA256 or receipt.get("status") != "EV1_T07_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED":
        raise T07Error("WORK_RECEIPT_DRIFT")
    head = git("rev-parse", "HEAD")
    status = git("status", "--porcelain=v1", "-uall")
    if head.returncode != 0 or head.stdout.decode().strip() != TASK_COMMIT:
        raise T07Error("TASK_COMMIT_DRIFT")
    if status.returncode != 0 or status.stdout.decode().splitlines() != EXPECTED_STATUS:
        raise T07Error("TASK_STATUS_DRIFT")
    hashes = {relative: digest(safe_file(relative)) for relative in sorted(EXPECTED_HASHES)}
    if hashes != EXPECTED_HASHES or receipt.get("declared_file_hashes") != EXPECTED_HASHES:
        raise T07Error("TASK_FILE_HASH_DRIFT")
    fixture = safe_file("fixtures/oversized-analyze-request.json")
    if fixture.stat().st_size != 81_920:
        raise T07Error("FIXTURE_SIZE_DRIFT")
    return {
        "declared_file_hashes": hashes,
        "git_status": EXPECTED_STATUS,
        "task_commit": TASK_COMMIT,
        "workspace_inode": WORKSPACE.stat().st_ino,
        "fixture_inode": fixture.stat().st_ino,
        "fixture_bytes": fixture.stat().st_size,
    }


def product_surface() -> Any:
    package_init = ROOT / "cockroach_kernel" / "__init__.py"
    surface_path = ROOT / "cockroach_kernel" / "recovery_surface.py"
    if digest(package_init) != PRODUCT_PACKAGE_INIT_SHA256 or digest(surface_path) != PRODUCT_SURFACE_SHA256:
        raise T07Error("PRODUCT_SURFACE_DRIFT")
    shown_init = subprocess.run(
        ["git", "show", f"{PRODUCT_CANDIDATE}:cockroach_kernel/__init__.py"],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=120,
    )
    shown = subprocess.run(
        ["git", "show", f"{PRODUCT_CANDIDATE}:cockroach_kernel/recovery_surface.py"],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=120,
    )
    if shown_init.returncode != 0 or digest(shown_init.stdout) != PRODUCT_PACKAGE_INIT_SHA256:
        raise T07Error("PRODUCT_PACKAGE_INIT_BINDING_DRIFT")
    if shown.returncode != 0 or digest(shown.stdout) != PRODUCT_SURFACE_SHA256:
        raise T07Error("PRODUCT_CANDIDATE_BINDING_DRIFT")
    for relative, expected in P7_RUNTIME_HASHES.items():
        path = ROOT / relative
        bound = subprocess.run(
            ["git", "show", f"{PRODUCT_CANDIDATE}:{relative}"], cwd=ROOT,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=120,
        )
        if digest(path) != expected or bound.returncode != 0 or digest(bound.stdout) != expected:
            raise T07Error("PRODUCT_P7_RUNTIME_BINDING_DRIFT")
    if importlib.util.find_spec("p7_runtime") is None:
        package_root = ROOT / "p7-recovery"
        package_spec = importlib.util.spec_from_file_location(
            "p7_runtime", package_root / "__init__.py",
            submodule_search_locations=[str(package_root)],
        )
        if package_spec is None or package_spec.loader is None:
            raise T07Error("PRODUCT_P7_RUNTIME_IMPORT_FAILED")
        package_module = importlib.util.module_from_spec(package_spec)
        sys.modules["p7_runtime"] = package_module
        package_spec.loader.exec_module(package_module)
    module = importlib.import_module("cockroach_kernel.recovery_surface")
    if module.MAX_FILE_BYTES != 65_536:
        raise T07Error("PRODUCT_FILE_LIMIT_DRIFT")
    return module


def exercise_bound(handle: Any, surface: Any) -> tuple[str, int]:
    try:
        surface._read_bounded(handle, surface.MAX_FILE_BYTES, "AGGREGATE_LIMIT_EXCEEDED")
    except surface.SurfaceError as exc:
        if exc.reason != "AGGREGATE_LIMIT_EXCEEDED" or exc.verdict != "INVALID" or exc.action_taken != "NONE":
            raise T07Error("PRODUCT_INVALID_SEMANTICS_DRIFT") from exc
        return exc.reason, handle.tell()
    raise T07Error("OVERSIZED_INPUT_ACCEPTED")


def preflight() -> int:
    if PREFLIGHT_RECEIPT.exists() or RESULT_RECEIPT.exists():
        raise T07Error("PREFLIGHT_ALREADY_STARTED")
    state = verify_state()
    surface = product_surface()
    reason, read_bytes = exercise_bound(io.BytesIO(b"x" * (surface.MAX_FILE_BYTES + 1)), surface)
    body = {
        "version": "ev1-t07-capture-only-preflight-v2",
        "status": "EV1_T07_CAPTURE_ONLY_PREFLIGHT_R2_GREEN",
        "task_id": TASK_ID,
        "authorization_sha256": digest(AUTHORIZATION),
        "backlog_sha256": BACKLOG_SHA256,
        "preflight_packet_sha256": PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "product_package_init_sha256": PRODUCT_PACKAGE_INIT_SHA256,
        "product_surface_sha256": PRODUCT_SURFACE_SHA256,
        "runner_sha256": digest(Path(__file__).resolve()),
        "state": state,
        "canary": {"input_bytes": 65_537, "bytes_read": read_bytes, "verdict": "INVALID", "reason": reason, "action_taken": "NONE"},
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
        raise T07Error("CAPTURE_ALREADY_TERMINAL")
    preflighted = load_receipt(PREFLIGHT_RECEIPT)
    judged = load_receipt(JUDGE_RECEIPT)
    if preflighted.get("status") != "EV1_T07_CAPTURE_ONLY_PREFLIGHT_R2_GREEN":
        raise T07Error("LOCAL_PREFLIGHT_NOT_GREEN")
    if preflighted.get("runner_sha256") != digest(Path(__file__).resolve()):
        raise T07Error("RUNNER_DRIFT")
    if judged.get("status") != "EV1_T07_CAPTURE_ONLY_R2_JUDGES_GREEN" or judged.get("packet_sha256") != digest(PACKET):
        raise T07Error("INDEPENDENT_PREFLIGHT_NOT_GREEN")
    if judged.get("glm_verdict") != "GREEN" or judged.get("agy_verdict") != "GREEN":
        raise T07Error("INDEPENDENT_PREFLIGHT_NOT_GREEN")
    before = verify_state()
    surface = product_surface()
    fixture = safe_file("fixtures/oversized-analyze-request.json")
    with fixture.open("rb") as handle:
        reason, read_bytes = exercise_bound(handle, surface)
    after = verify_state()
    if after != before or read_bytes != 65_537:
        raise T07Error("CAPTURE_MUTATED_STATE_OR_READ_BOUND_DRIFT")
    forbidden_paths = (CAMPAIGN / "recovery", CAMPAIGN / "representations", CAMPAIGN / "successor", Path("/private/tmp/ck-ev1-t07-r1"))
    if any(path.exists() or path.is_symlink() for path in forbidden_paths):
        raise T07Error("FORBIDDEN_POST_INVALID_PATH_EXISTS")
    body = {
        "version": "ev1-t07-capture-invalid-result-v1",
        "status": "EV1_T07_CLOSED_EXPECTED_INVALID",
        "task_id": TASK_ID,
        "capture_declaration": DECLARATION,
        "capture_declaration_utc": DECLARATION_UTC,
        "authorization_sha256": digest(AUTHORIZATION),
        "packet_sha256": digest(PACKET),
        "judge_receipt_sha256": judged["receipt_sha256"],
        "product_candidate": PRODUCT_CANDIDATE,
        "product_package_init_sha256": PRODUCT_PACKAGE_INIT_SHA256,
        "product_surface_sha256": PRODUCT_SURFACE_SHA256,
        "observed_product_reason": reason,
        "campaign_outcome": "INVALID_OVERSIZED_RECORD",
        "verdict": "INVALID",
        "action_taken": "NONE",
        "fixture_bytes": 81_920,
        "bounded_bytes_read": read_bytes,
        "workspace_state_before": before,
        "workspace_state_after": after,
        "workspace_present": WORKSPACE.is_dir(),
        "workspace_unchanged": True,
        "fixture_present": fixture.is_file(),
        "fixture_unchanged": digest(fixture) == EXPECTED_HASHES["fixtures/oversized-analyze-request.json"],
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
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired, T07Error) as exc:
        print(canonical({"phase": phase, "reason": str(exc) or exc.__class__.__name__, "status": "EV1_T07_CAPTURE_ONLY_BLOCKED"}).decode())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
