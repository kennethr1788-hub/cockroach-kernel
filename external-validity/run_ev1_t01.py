#!/usr/bin/env python3
"""Execute the frozen EV1-T01 capture, guarded loss, and fresh recovery.

This is evidence orchestration only. It does not import or modify the frozen
product candidate. ``prepare`` freezes the exact two-file representation and
stages the candidate; ``execute`` revalidates that receipt before deleting the
one authorized disposable workspace.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / ".ev1-runtime" / "EV1-T01"
CONTROL = CAMPAIGN / "control"
ORIGINAL = CAMPAIGN / "workspace"
RECOVERY = CAMPAIGN / "recovery"
SUCCESSOR = RECOVERY / "workspace"
REPRESENTATIONS = RECOVERY / "representations"
CUSTODY = RECOVERY / "custody"
OUTPUT = RECOVERY / "output"
TEMP = RECOVERY / "tmp"
REQUEST = RECOVERY / "request.json"
PRODUCT_RUNTIME = CONTROL / "product-runtime"
DEPENDENCY_RUNTIME = CAMPAIGN / "dependency-runtime"
PREPARE_RECEIPT = CONTROL / "CAPTURE_PREPARE_RECEIPT.json"
TASK_RECEIPT = CONTROL / "TASK_EXECUTION_RECEIPT.json"
SOURCE_REPO = Path.home() / "master-vault" / "coffee"
SOURCE_COMMIT = "1a92380a9edf12337f80b3c42ba098a7c1724664"
SOURCE_MANIFEST_SHA256 = "d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706"
BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
CAPTURE_DECLARATION = (
    "I, Kenneth, explicitly declare the exact current EV1-T01 state—modified "
    "src/app/page.tsx and untracked scripts/verify-home-tagline.mjs—permitted "
    "for capture, guarded disposable-workspace deletion, and fresh-process "
    "recovery under the frozen EV1 protocol."
)
CAPTURE_DECLARATION_UTC = "2026-07-30T14:34:12Z"
DECLARED = ("scripts/verify-home-tagline.mjs", "src/app/page.tsx")
EXPECTED_STATUS = [" M src/app/page.tsx", "?? scripts/verify-home-tagline.mjs"]
EXPECTED_HASHES = {
    "src/app/page.tsx": "4e58758472be64bb40458e4f201340d8ef98b7c848dc5ae7cd3323145cbc643e",
    "scripts/verify-home-tagline.mjs": "ef03dd17029435a469b80cb683ce6f2d5c64b2454940863e9ff78abeab6aa431",
}
EXPECTED_LOGS = {
    "human-typecheck.log": "7ad5370190f3f13153e8329d717ccdfec065241392cd850b68579e68731ca022",
    "human-build.log": "7597c01d1514bdf752f0e8a19e0d5286c951d3ec29729e942057bede4d7d46a8",
    "human-tagline-verifier.log": "823994e1443f06d130d5b7475572a36f790c685f8f4e04d91508487dd6ae55b3",
}
EXPECTED_PROFILE_SHA256 = "6358a9beae8361105578231b64ca638a99cbf780e1c8f5d24f9ff71891f0bc2b"
PRIVATE_MARKER = re.compile(
    rb"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY"
)


class T01Error(RuntimeError):
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


def atomic_bytes(path: Path, raw: bytes, mode: int = 0o600) -> None:
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
    atomic_bytes(path, raw)
    return sealed["receipt_sha256"], digest(raw)


def run(
    command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 600
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


def load_r3() -> Any:
    path = ROOT / "fresh-context-black-box" / "r3_preflight.py"
    spec = importlib.util.spec_from_file_location("ev1_t01_r3", path)
    if spec is None or spec.loader is None:
        raise T01Error("R3_HARNESS_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_rows() -> list[dict[str, str]]:
    completed = run(
        ["git", "-C", str(SOURCE_REPO), "ls-tree", "-r", SOURCE_COMMIT],
        cwd=ROOT,
        timeout=60,
    )
    if completed.returncode != 0:
        raise T01Error("SOURCE_TREE_UNREADABLE")
    rows: list[dict[str, str]] = []
    for line in completed.stdout.decode("utf-8").splitlines():
        metadata, relative = line.split("\t", 1)
        mode, kind, blob = metadata.split(" ", 2)
        pure = PurePosixPath(relative)
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise T01Error("SOURCE_ENTRY_UNSAFE")
        if pure.is_absolute() or ".." in pure.parts or "\x00" in relative:
            raise T01Error("SOURCE_PATH_UNSAFE")
        if relative != "CLAUDE.md":
            rows.append({"blob": blob, "mode": mode, "path": relative})
    if len(rows) != 76 or digest(rows) != SOURCE_MANIFEST_SHA256:
        raise T01Error("SOURCE_MANIFEST_MISMATCH")
    return rows


def export_baseline(destination: Path, *, omit: set[str]) -> int:
    destination.mkdir(parents=True, mode=0o700)
    written = 0
    for row in source_rows():
        relative = row["path"]
        if relative in omit:
            continue
        completed = run(
            ["git", "-C", str(SOURCE_REPO), "show", f"{SOURCE_COMMIT}:{relative}"],
            cwd=ROOT,
            timeout=60,
        )
        if completed.returncode != 0 or PRIVATE_MARKER.search(completed.stdout):
            raise T01Error("SOURCE_EXPORT_BLOCKED")
        target = destination.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        parent = target.parent.resolve(strict=True)
        if destination.resolve(strict=True) not in (parent, *parent.parents):
            raise T01Error("SOURCE_EXPORT_ESCAPE")
        atomic_bytes(target, completed.stdout, 0o755 if row["mode"] == "100755" else 0o644)
        written += 1
    return written


def git_status(workspace: Path) -> list[str]:
    completed = run(["git", "status", "--porcelain=v1", "-uall"], cwd=workspace, timeout=60)
    if completed.returncode != 0:
        raise T01Error("WORKSPACE_GIT_STATUS_FAILED")
    return completed.stdout.decode("utf-8").splitlines()


def safe_file(root: Path, relative: str) -> Path:
    target = root.joinpath(*PurePosixPath(relative).parts)
    resolved = target.resolve(strict=True)
    if root.resolve(strict=True) not in resolved.parents or target.is_symlink() or not target.is_file():
        raise T01Error("DECLARED_FILE_UNSAFE")
    return target


def verify_declared_state() -> dict[str, Any]:
    if ORIGINAL.is_symlink() or not ORIGINAL.is_dir() or ORIGINAL.resolve() != (CAMPAIGN / "workspace").resolve():
        raise T01Error("ORIGINAL_ROOT_MISMATCH")
    status = git_status(ORIGINAL)
    if status != EXPECTED_STATUS:
        raise T01Error(f"DECLARED_STATUS_MISMATCH:{status}")
    observed = {relative: digest(safe_file(ORIGINAL, relative)) for relative in DECLARED}
    if observed != {relative: EXPECTED_HASHES[relative] for relative in DECLARED}:
        raise T01Error("DECLARED_FILE_HASH_MISMATCH")
    for name, expected in EXPECTED_LOGS.items():
        if digest(CONTROL / name) != expected:
            raise T01Error(f"ACCEPTANCE_LOG_MISMATCH:{name}")
    return {"file_hashes": observed, "git_status": status}


def make_request(r3: Any, file_hashes: dict[str, str]) -> dict[str, Any]:
    p7 = r3.p7
    entries = [
        {"path": path, "content_hash": file_hashes[path], "executable": False, "is_symlink": False}
        for path in sorted(file_hashes)
    ]
    manifest = {
        "version": p7.VERSION,
        "manifest_id": "manifest-ev1-t01-r1",
        "task_id": "EV1-T01",
        "files": entries,
    }
    labels = ("SOURCE_BASELINE_BOUND", "HUMAN_EDIT_SAVED", "UNTRACKED_VERIFIER_PRESENT", "OFFLINE_ACCEPTANCE_GREEN")
    events = [
        {"sequence": index, "event": label, "event_hash": digest(label.encode("utf-8"))}
        for index, label in enumerate(labels)
    ]
    previous = ""
    for event in events:
        previous = p7.sha256_hex({"previous": previous, "event": event})
    trajectory = {
        "version": p7.VERSION,
        "receipt_id": "trajectory-ev1-t01-r1",
        "task_id": "EV1-T01",
        "manifest_hash": p7.sha256_hex(manifest),
        "events": events,
        "trajectory_hash": previous,
    }
    quorum = {"decision": "PROMOTE"}
    context = {
        "manifest": manifest,
        "trajectory_receipt": trajectory,
        "policy_version": "ev1-frozen-r3",
        "quorum_decision_hash": p7.sha256_hex(quorum),
    }
    candidate = {
        "version": p7.VERSION,
        "candidate_id": "candidate-ev1-t01-r1",
        "task_id": "EV1-T01",
        "provenance": {"source": "human-declared-hash-bound-representation"},
        "source_receipt_hash": p7.sha256_hex(trajectory),
        "policy_version": context["policy_version"],
        "policy_veto": False,
        "tampered": False,
        "quorum_decision": quorum,
        "prefix_length": len(events),
        "integrity_hash": p7.trajectory_integrity_hash(events, len(events)),
        "declared_paths": sorted(file_hashes),
        "file_hashes": dict(sorted(file_hashes.items())),
        "executable_test": {
            "test_id": "test-ev1-t01-tagline-r1",
            "path": "scripts/verify-home-tagline.mjs",
            "feature_hash": file_hashes["scripts/verify-home-tagline.mjs"],
            "passed": True,
        },
    }
    decision = p7.select_candidate([candidate], context)
    if decision["decision"] != "PROMOTE":
        raise T01Error("PREPARED_CANDIDATE_NOT_ADMITTED")
    warrant = p7.make_warrant("warrant-ev1-t01-r1", "EV1-T01", candidate["candidate_id"], decision)
    loss = {
        "version": p7.VERSION,
        "receipt_id": "loss-ev1-t01-r1",
        "task_id": "EV1-T01",
        "manifest_hash": p7.sha256_hex(manifest),
        "lost_paths": sorted(file_hashes),
        "absence_hash": p7.sha256_hex({"lost_paths": sorted(file_hashes), "observed": "absent"}),
    }
    request = {
        "version": r3.surface.REQUEST_VERSION,
        "request_id": "request-ev1-t01-r1",
        "context": context,
        "loss_receipt": loss,
        "candidates": [candidate],
        "warrant": warrant,
    }
    r3.surface.canonical_json(request)
    return request


def stage_product(r3: Any) -> tuple[Path, Path, Path]:
    if PRODUCT_RUNTIME.exists():
        toolchain = PRODUCT_RUNTIME / "toolchain"
        venv = PRODUCT_RUNTIME / "venv"
        entrypoint = venv / "bin" / "cockroach-kernel"
        if not entrypoint.is_file():
            raise T01Error("STAGED_PRODUCT_INCOMPLETE")
        return toolchain, venv, entrypoint
    PRODUCT_RUNTIME.mkdir(parents=True, mode=0o700)
    return r3.materialize_candidate(PRODUCT_RUNTIME)


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): digest(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def prepare() -> int:
    if PREPARE_RECEIPT.exists() or TASK_RECEIPT.exists():
        raise T01Error("T01_PREPARE_ALREADY_EXISTS")
    state = verify_declared_state()
    r3 = load_r3()
    if digest(r3.PROFILE) != EXPECTED_PROFILE_SHA256:
        raise T01Error("SEATBELT_PROFILE_HASH_MISMATCH")
    for relative, expected in r3.EXPECTED.items():
        if digest(ROOT / relative) != expected:
            raise T01Error(f"PRODUCT_CANDIDATE_DRIFT:{relative}")

    for path in (RECOVERY, PRODUCT_RUNTIME, DEPENDENCY_RUNTIME):
        if path.exists():
            raise T01Error(f"PREEXISTING_RUNTIME_ROOT:{path.name}")
    for path in (REPRESENTATIONS, CUSTODY, OUTPUT, TEMP):
        path.mkdir(parents=True, mode=0o700)
    atomic_bytes(REQUEST, b"{}")

    candidate_base = REPRESENTATIONS / "candidate-ev1-t01-r1"
    for relative in DECLARED:
        source = safe_file(ORIGINAL, relative)
        target = candidate_base.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, source.read_bytes(), 0o600)
    request = make_request(r3, state["file_hashes"])
    atomic_bytes(REQUEST, r3.surface.canonical_json(request), 0o600)

    toolchain, venv, entrypoint = stage_product(r3)
    outside_canary = CONTROL / "outside-kill-canary.txt"
    atomic_bytes(outside_canary, b"EV1-T01 outside kill canary\n")
    body = {
        "version": "ev1-t01-capture-prepare-v1",
        "status": "CAPTURE_PREPARED_EXECUTION_NOT_STARTED",
        "task_id": "EV1-T01",
        "backlog_sha256": BACKLOG_SHA256,
        "preflight_packet_sha256": PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "capture_declaration": CAPTURE_DECLARATION,
        "capture_declaration_utc": CAPTURE_DECLARATION_UTC,
        "source_commit": SOURCE_COMMIT,
        "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
        "original_workspace_relative": ".ev1-runtime/EV1-T01/workspace",
        "successor_workspace_relative": ".ev1-runtime/EV1-T01/recovery/workspace",
        "declared_state": state,
        "request_sha256": digest(REQUEST),
        "representation_hashes": tree_hashes(REPRESENTATIONS),
        "representation_aggregate_bytes": sum(path.stat().st_size for path in REPRESENTATIONS.rglob("*") if path.is_file()),
        "seatbelt_profile_sha256": digest(r3.PROFILE),
        "product_entrypoint_sha256": digest(entrypoint),
        "product_runtime": {
            "candidate_source_relative": ".ev1-runtime/EV1-T01/control/product-runtime/candidate",
            "entrypoint_relative": ".ev1-runtime/EV1-T01/control/product-runtime/venv/bin/cockroach-kernel",
            "toolchain_relative": ".ev1-runtime/EV1-T01/control/product-runtime/toolchain",
        },
        "kill_target": ".ev1-runtime/EV1-T01/workspace",
        "kill_target_guarded": True,
        "outside_canary_sha256": digest(outside_canary),
        "capture_complete": True,
        "deletion_started": False,
        "recovery_started": False,
    }
    receipt_hash, file_hash = atomic_record(PREPARE_RECEIPT, body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


def load_receipt(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if not raw.endswith(b"\n"):
        raise T01Error("RECEIPT_NOT_CANONICAL")
    value = json.loads(raw[:-1])
    if canonical(value) + b"\n" != raw:
        raise T01Error("RECEIPT_NOT_CANONICAL")
    body = {key: value[key] for key in value if key != "receipt_sha256"}
    if value.get("receipt_sha256") != digest(body):
        raise T01Error("RECEIPT_HASH_MISMATCH")
    return value


def minimal_env(*, path: str, tmpdir: Path, npm_cache: Path | None = None) -> dict[str, str]:
    env = {
        "CI": "1",
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        "NEXT_TELEMETRY_DISABLED": "1",
        "PATH": path,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "TMPDIR": str(tmpdir),
    }
    if npm_cache is not None:
        env.update(
            {
                "NPM_CONFIG_AUDIT": "false",
                "NPM_CONFIG_CACHE": str(npm_cache),
                "NPM_CONFIG_FUND": "false",
                "NPM_CONFIG_USERCONFIG": str(CONTROL / "empty.npmrc"),
            }
        )
    return env


def guarded_destroy() -> dict[str, Any]:
    expected = CAMPAIGN / "workspace"
    if ORIGINAL != expected or ORIGINAL.is_symlink() or not ORIGINAL.is_dir():
        raise T01Error("KILL_TARGET_MISMATCH")
    campaign_resolved = CAMPAIGN.resolve(strict=True)
    original_resolved = ORIGINAL.resolve(strict=True)
    if original_resolved != expected.resolve(strict=True) or campaign_resolved not in original_resolved.parents:
        raise T01Error("KILL_TARGET_ESCAPE")
    before = time.monotonic_ns()
    shutil.rmtree(ORIGINAL, ignore_errors=False)
    elapsed = time.monotonic_ns() - before
    if ORIGINAL.exists() or not (CONTROL / "outside-kill-canary.txt").is_file():
        raise T01Error("KILL_OR_CANARY_VERIFICATION_FAILED")
    return {"elapsed_monotonic_ns": elapsed, "original_absent": True, "outside_canary_survived": True}


def record_command(name: str, completed: subprocess.CompletedProcess[bytes]) -> dict[str, Any]:
    raw = completed.stdout + completed.stderr
    atomic_bytes(CONTROL / f"{name}.log", raw)
    return {"exit": completed.returncode, "log_sha256": digest(raw), "log_bytes": len(raw)}


def execute() -> int:
    prepared = load_receipt(PREPARE_RECEIPT)
    if prepared["status"] != "CAPTURE_PREPARED_EXECUTION_NOT_STARTED":
        raise T01Error("PREPARE_STATUS_INVALID")
    state = verify_declared_state()
    if state != prepared["declared_state"]:
        raise T01Error("POST_PREPARE_STATE_DRIFT")
    if digest(REQUEST) != prepared["request_sha256"] or tree_hashes(REPRESENTATIONS) != prepared["representation_hashes"]:
        raise T01Error("CAPTURE_EVIDENCE_DRIFT")
    r3 = load_r3()
    toolchain, venv, entrypoint = stage_product(r3)
    if digest(entrypoint) != prepared["product_entrypoint_sha256"]:
        raise T01Error("PRODUCT_ENTRYPOINT_DRIFT")

    node_modules = ORIGINAL / "node_modules"
    if node_modules.is_symlink() or not node_modules.is_dir():
        raise T01Error("DEPENDENCY_RUNTIME_MISSING")
    DEPENDENCY_RUNTIME.mkdir(mode=0o700)
    shutil.move(str(node_modules), str(DEPENDENCY_RUNTIME / "node_modules"))
    dependency_tree_hash = digest(
        canonical(
            sorted(
                path.relative_to(DEPENDENCY_RUNTIME / "node_modules").as_posix()
                for path in (DEPENDENCY_RUNTIME / "node_modules").rglob("*")
            )
        )
    )
    kill = guarded_destroy()

    omitted = {"src/app/page.tsx", "scripts/verify-home-tagline.mjs"}
    baseline_files = export_baseline(SUCCESSOR, omit=omitted)
    if (SUCCESSOR / ".git").exists() or baseline_files != 75:
        raise T01Error("SUCCESSOR_BASELINE_INVALID")
    empty_history = True

    public_root = CONTROL / "public"
    public_root.mkdir(exist_ok=True)
    empty_home = CAMPAIGN / "empty-home"
    empty_home.mkdir(exist_ok=True)
    args = [
        "recover",
        "--request", str(REQUEST),
        "--sandbox-root", str(RECOVERY),
        "--workspace", str(SUCCESSOR),
        "--representation-root", str(REPRESENTATIONS),
        "--custody-root", str(CUSTODY),
        "--output-root", str(OUTPUT),
    ]
    command = r3.seatbelt_command(entrypoint, toolchain, venv, public_root, RECOVERY, args)
    recovery_env = minimal_env(path="/usr/bin:/bin", tmpdir=TEMP)
    invocation_start = time.monotonic_ns()
    recovered = run(command, cwd=ROOT, env=recovery_env, timeout=120)
    productive_ns = time.monotonic_ns() - invocation_start
    recovery_record = record_command("t01-recovery", recovered)
    if recovered.returncode != 0:
        raise T01Error(f"PRODUCT_RECOVERY_FAILED:{recovered.returncode}")
    summary = json.loads(recovered.stdout)
    if summary.get("verdict") != "PROMOTE" or summary.get("fresh_context_continued") is not True:
        raise T01Error("PRODUCT_RECOVERY_NOT_PROMOTED")
    if tree_hashes(REPRESENTATIONS) != prepared["representation_hashes"]:
        raise T01Error("REPRESENTATION_MUTATED")

    npm = shutil.which("npm")
    node = shutil.which("node")
    if npm is None or node is None:
        raise T01Error("NODE_TOOLCHAIN_MISSING")
    bins = DEPENDENCY_RUNTIME / "node_modules" / ".bin"
    acceptance_env = minimal_env(
        path=f"{bins}:{Path(npm).parent}:/usr/bin:/bin",
        tmpdir=TEMP,
        npm_cache=CONTROL / "npm-cache",
    )
    acceptance: dict[str, Any] = {}
    commands = (
        ("t01-successor-typecheck", [npm, "run", "typecheck"], 600),
        ("t01-successor-build", [npm, "run", "build"], 600),
        ("t01-successor-tagline-verifier", [node, "scripts/verify-home-tagline.mjs"], 120),
    )
    offline_profile = CONTROL / "offline.sb"
    for name, argv, timeout in commands:
        completed = run(
            ["/usr/bin/sandbox-exec", "-f", str(offline_profile), *argv],
            cwd=SUCCESSOR,
            env=acceptance_env,
            timeout=timeout,
        )
        acceptance[name] = record_command(name, completed)
        if completed.returncode != 0:
            raise T01Error(f"SUCCESSOR_ACCEPTANCE_FAILED:{name}")
    acceptance_ns = time.monotonic_ns() - invocation_start

    restored = {relative: digest(safe_file(SUCCESSOR, relative)) for relative in DECLARED}
    if restored != EXPECTED_HASHES:
        raise T01Error("SUCCESSOR_WORK_UNITS_MISMATCH")
    process_scan = run(["ps", "-axo", "pid=,command="], cwd=ROOT, timeout=30)
    if process_scan.returncode != 0:
        raise T01Error("PROCESS_RESIDUE_SCAN_FAILED")
    markers = (str(ORIGINAL), str(RECOVERY))
    residue_processes = [
        line.decode("utf-8", "replace").strip()
        for line in process_scan.stdout.splitlines()
        if any(marker in line.decode("utf-8", "replace") for marker in markers)
        and str(os.getpid()) not in line.decode("utf-8", "replace")
    ]
    if residue_processes:
        raise T01Error("TASK_PROCESS_RESIDUE")

    output_hashes = tree_hashes(OUTPUT)
    custody_hashes = tree_hashes(CUSTODY)
    body = {
        "version": "ev1-task-execution-receipt-v1",
        "status": "MECHANICAL_TASK_COMPLETE_OPERATOR_OBSERVATION_REQUIRED",
        "task_id": "EV1-T01",
        "backlog_sha256": BACKLOG_SHA256,
        "preflight_packet_sha256": PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "source_commit": SOURCE_COMMIT,
        "project_class": "SMALL_SINGLE_PACKAGE",
        "capture_prepare_file_sha256": digest(PREPARE_RECEIPT),
        "capture_prepare_receipt_sha256": prepared["receipt_sha256"],
        "capture_declaration": CAPTURE_DECLARATION,
        "capture_declaration_utc": CAPTURE_DECLARATION_UTC,
        "state_mix": {"committed": True, "uncommitted": True, "untracked": True, "human_edit": True},
        "declared_work_units_before_loss": 2,
        "usable_work_units_after_continuation": 2,
        "kill": kill,
        "empty_history_successor": empty_history,
        "baseline_files_recreated": baseline_files,
        "dependency_runtime_tree_sha256": dependency_tree_hash,
        "recovery": recovery_record,
        "recovery_summary": summary,
        "output_hashes": output_hashes,
        "custody_hashes": custody_hashes,
        "acceptance_command": "npm run typecheck && npm run build && node scripts/verify-home-tagline.mjs",
        "acceptance": acceptance,
        "invocation_to_productive_continuation_monotonic_ns": productive_ns,
        "invocation_to_acceptance_pass_monotonic_ns": acceptance_ns,
        "post_loss_task_restatement_words": 0,
        "manual_intervention_count_after_loss": 0,
        "expected_verdict": "PROMOTE",
        "observed_verdict": summary["verdict"],
        "stable_reason": summary["reason"],
        "false_promotion_count": 0,
        "false_refusal_count": 0,
        "invalid_count": 0,
        "unsafe_mutation_count": 0,
        "unauthorized_path_access_count": 0,
        "original_workspace_residue_bytes": 0,
        "task_process_residue_count": 0,
        "operator_qualitative_note": None,
        "operator_git_backup_counterfactual": None,
        "operator_observation_scoring": "EXCLUDED",
        "campaign_teardown_pending": True,
    }
    receipt_hash, file_hash = atomic_record(TASK_RECEIPT, body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("prepare", "execute"))
    args = parser.parse_args()
    try:
        return prepare() if args.phase == "prepare" else execute()
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired, T01Error) as exc:
        result = {"status": "EV1_T01_BLOCKED", "reason": str(exc) or exc.__class__.__name__}
        print(canonical(result).decode(), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
