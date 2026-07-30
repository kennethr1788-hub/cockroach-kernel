#!/usr/bin/env python3
"""Capture and execute the frozen EV1-T06 recovery campaign.

The exact disposable Git baseline is retained separately from the five declared
task work units.  Only those five units enter the product recovery
representation; the baseline and dependency graph are reconstructed before the
fresh-process recovery invocation.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "EV1-T06"
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
ORIGINAL = CAMPAIGN / "workspace"
RECOVERY = CAMPAIGN / "recovery"
REPRESENTATIONS = RECOVERY / "representations"
CUSTODY = RECOVERY / "custody"
OUTPUT = RECOVERY / "output"
TEMP = RECOVERY / "tmp"
REQUEST = RECOVERY / "request.json"
BASELINE_SNAPSHOT = CONTROL / "BASELINE_SNAPSHOT"
DEPENDENCY_RUNTIME = CAMPAIGN / "dependency-runtime"
PREPARATION_RECEIPT = CONTROL / "PREPARATION_RECEIPT.json"
WORK_RECEIPT = CONTROL / "WORK_RECEIPT.json"
CAPTURE_RECEIPT = CONTROL / "CAPTURE_RECEIPT.json"
PREFLIGHT_RECEIPT = CONTROL / "EXECUTION_PREFLIGHT_RECEIPT.json"
TASK_RECEIPT = CONTROL / "TASK_EXECUTION_RECEIPT.json"
FAILURE_RECEIPT = CONTROL / "TASK_FAILURE_RECEIPT.json"
FAILURE_SNAPSHOT = CONTROL / "FAILURE_SNAPSHOT"
PREFLIGHT_CAMPAIGN = Path("/private/tmp/ck-ev1-t06-preflight-r1")
EXECUTION_CAMPAIGN = Path("/private/tmp/ck-ev1-t06-r1")
EXECUTION_RECOVERY = EXECUTION_CAMPAIGN / "recovery"
EXECUTION_SUCCESSOR = EXECUTION_RECOVERY / "workspace"
EXECUTION_REPRESENTATIONS = EXECUTION_RECOVERY / "representations"
EXECUTION_CUSTODY = EXECUTION_RECOVERY / "custody"
EXECUTION_OUTPUT = EXECUTION_RECOVERY / "output"
EXECUTION_TEMP = EXECUTION_RECOVERY / "tmp"
EXECUTION_REQUEST = EXECUTION_RECOVERY / "request.json"
SOURCE_COMMIT = "2c088ba8599c75cb02fbd61dfcf259d000729131"
SOURCE_MANIFEST_SHA256 = "cf4170e9e35023fc139a1e56d86ab775bbe73e14bd79a4568edf176acce4f7a9"
BASELINE_COMMIT = "ed7a9384de87370fc98537684f24686e8fa057c8"
BASELINE_FILE_COUNT = 20
BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
T04_RUNNER = ROOT / "external-validity" / "run_ev1_t04.py"
T04_RUNNER_SHA256 = "adf276cab76dc77e76e81fa5a33573c23d6192a5f719ee0ac1df96c882eca1fc"
AUTHORIZATION_FILE_SHA256 = "5d69f8a356b745da7f373210a9ab5e1bcf031f7bb4341ebf66677039611b3708"
PREPARATION_FILE_SHA256 = "01b4f7b60ee02ce518b3f2df5f00f3b186b43f9d97c5702305a9c8b1cd1b1a4a"
PREPARATION_INTERNAL_SHA256 = "1a5caffc5e89e5cc3a1f4ef6583ae408e13b10387fcabed6f3e7edf4c0bfd3bb"
WORK_RECEIPT_FILE_SHA256 = "78cf0fb8f07ee61d86eb37b6970c087df21deac6b22e3f6ba671b5ae9489f602"
WORK_RECEIPT_INTERNAL_SHA256 = "7a31602588f1e319d70b9bd202e15683862fe7f061786f14e76a1b27e8896780"
TASK_COMMIT = "a3e5cd8f7dda19dd04df5904b5671f955a5c7adb"
CAPTURE_DECLARATION = (
    "I, Kenneth, explicitly declare the exact current EV1-T06 state—committed "
    "lib/ranking.ts and scripts/run-stable-ranking.mjs at task commit "
    "a3e5cd8f7dda19dd04df5904b5671f955a5c7adb, modified lib/signals.ts and "
    "package.json, and untracked scripts/stable-ranking-cases.cjs—permitted for "
    "capture, guarded disposable-workspace deletion, and fresh-process recovery "
    "under the frozen EV1 protocol."
)
CAPTURE_DECLARATION_UTC = "2026-07-30T19:36:27Z"
DECLARED = (
    "lib/ranking.ts",
    "lib/signals.ts",
    "package.json",
    "scripts/run-stable-ranking.mjs",
    "scripts/stable-ranking-cases.cjs",
)
EXPECTED_STATUS = [
    " M lib/signals.ts",
    " M package.json",
    "?? scripts/stable-ranking-cases.cjs",
]
EXPECTED_HASHES = {
    "lib/ranking.ts": "01a919cd1a6ef265018524838fb38f0b2bbb3305b1241a982d29314fd1353e3a",
    "lib/signals.ts": "2cf7f8ae0473520a113dc121d45bfe1ee8c0f2e7254734c51ea490dd309c0fe2",
    "package.json": "a6275ccb9cf21ad1c4b22a59d393d0f792bdabc080f0312aeb4cdc1e43603263",
    "scripts/run-stable-ranking.mjs": "1df0888b5dd337cb5eb5ae173d9bf8952f9f10159ed2cda3ebd19cf42acdfc1c",
    "scripts/stable-ranking-cases.cjs": "4f3f40fa9f78e2d3c5b9e59bdfb79c6f9bb0ccd12b585b5335978d02eddeb5a4",
}
EXPECTED_LOGS = {
    "work-stable-ranking.log": "99d76eb83d32dcf28074bb7117ada2a8b1860460bc116ea7d5947ad9f0a56d9e",
    "work-typecheck.log": "8c0af875a1ab948857b68d4f22b66e9bce86deedfdf47d7ba6ea1d528e01bbda",
    "work-build.log": "676b9352b4198af0b73b884925fd687f8b5c2f35ed4868fd140e477975dbb6ba",
}
EXPECTED_PROFILE_SHA256 = "6358a9beae8361105578231b64ca638a99cbf780e1c8f5d24f9ff71891f0bc2b"
OFFLINE_PROFILE_SHA256 = "5c358b8d847211333e7ba22df82d84f796b5f30a41a2682209a949d783adbd08"


class T06Error(RuntimeError):
    pass


def load_t04() -> Any:
    if hashlib.sha256(T04_RUNNER.read_bytes()).hexdigest() != T04_RUNNER_SHA256:
        raise T06Error("T04_PRIMITIVE_SOURCE_DRIFT")
    spec = importlib.util.spec_from_file_location("ev1_t04_frozen", T04_RUNNER)
    if spec is None or spec.loader is None:
        raise T06Error("T04_PRIMITIVE_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


T04 = load_t04()
T01 = T04.T01
canonical = T01.canonical
digest = T01.digest
atomic_bytes = T01.atomic_bytes
atomic_record = T01.atomic_record
run = T01.run
tree_hashes = T01.tree_hashes


def load_r3() -> Any:
    return T01.load_r3()


def load_receipt(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if not raw.endswith(b"\n"):
        raise T06Error("RECEIPT_NOT_CANONICAL")
    value = json.loads(raw[:-1])
    if canonical(value) + b"\n" != raw:
        raise T06Error("RECEIPT_NOT_CANONICAL")
    body = {key: value[key] for key in value if key != "receipt_sha256"}
    if value.get("receipt_sha256") != digest(body):
        raise T06Error("RECEIPT_HASH_MISMATCH")
    return value


def git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return run(["git", *arguments], cwd=ORIGINAL, timeout=180)


def safe_file(root: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or "\x00" in relative:
        raise T06Error("DECLARED_PATH_UNSAFE")
    target = root.joinpath(*pure.parts)
    resolved = target.resolve(strict=True)
    resolved_root = root.resolve(strict=True)
    if resolved_root not in resolved.parents:
        raise T06Error("DECLARED_PATH_ESCAPE")
    if target.is_symlink() or not target.is_file():
        raise T06Error("DECLARED_FILE_UNSAFE")
    return target


def verify_work_state() -> dict[str, Any]:
    if digest(PREPARATION_RECEIPT) != PREPARATION_FILE_SHA256:
        raise T06Error("PREPARATION_FILE_DRIFT")
    preparation = load_receipt(PREPARATION_RECEIPT)
    if preparation.get("receipt_sha256") != PREPARATION_INTERNAL_SHA256:
        raise T06Error("PREPARATION_INTERNAL_DRIFT")
    if digest(WORK_RECEIPT) != WORK_RECEIPT_FILE_SHA256:
        raise T06Error("WORK_RECEIPT_FILE_DRIFT")
    receipt = load_receipt(WORK_RECEIPT)
    if receipt.get("receipt_sha256") != WORK_RECEIPT_INTERNAL_SHA256:
        raise T06Error("WORK_RECEIPT_INTERNAL_DRIFT")
    if receipt.get("status") != "EV1_T06_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED":
        raise T06Error("WORK_RECEIPT_STATUS_INVALID")
    head = git("rev-parse", "HEAD")
    status = git("status", "--porcelain=v1", "-uall")
    if head.returncode != 0 or head.stdout.decode().strip() != TASK_COMMIT:
        raise T06Error("TASK_COMMIT_DRIFT")
    if status.returncode != 0 or status.stdout.decode().splitlines() != EXPECTED_STATUS:
        raise T06Error("TASK_STATUS_DRIFT")
    hashes = {relative: digest(safe_file(ORIGINAL, relative)) for relative in DECLARED}
    if hashes != EXPECTED_HASHES or receipt.get("declared_file_hashes") != EXPECTED_HASHES:
        raise T06Error("TASK_FILE_HASH_DRIFT")
    for name, expected in EXPECTED_LOGS.items():
        if digest(CONTROL / name) != expected:
            raise T06Error(f"PRE_LOSS_LOG_DRIFT:{name}")
    authorization = ROOT / "EXTERNAL_VALIDITY_EV1_T06_CAPTURE_AUTHORIZATION_R1.md"
    if digest(authorization) != AUTHORIZATION_FILE_SHA256:
        raise T06Error("CAPTURE_AUTHORIZATION_DRIFT")
    return {"file_hashes": hashes, "git_status": EXPECTED_STATUS, "task_commit": TASK_COMMIT}


def make_request(r3: Any, file_hashes: dict[str, str]) -> dict[str, Any]:
    p7 = r3.p7
    paths = sorted(file_hashes)
    manifest = {
        "version": p7.VERSION,
        "manifest_id": "manifest-ev1-t06-r1",
        "task_id": TASK_ID,
        "files": [
            {
                "path": path,
                "content_hash": file_hashes[path],
                "executable": False,
                "is_symlink": False,
            }
            for path in paths
        ],
    }
    labels = (
        "SOURCE_AND_LOCKED_BASELINE_BOUND",
        "COMMITTED_DETERMINISTIC_COMPARATOR_PRESENT",
        "COMMITTED_TEST_RUNNER_PRESENT",
        "UNCOMMITTED_RUNTIME_LOADER_PRESENT",
        "UNCOMMITTED_PACKAGE_SCRIPT_PRESENT",
        "UNTRACKED_RANKING_CASES_PRESENT",
        "DETERMINISM_AND_OFFLINE_ACCEPTANCE_GREEN",
    )
    events = [
        {"sequence": index, "event": label, "event_hash": digest(label.encode("utf-8"))}
        for index, label in enumerate(labels)
    ]
    previous = ""
    for event in events:
        previous = p7.sha256_hex({"previous": previous, "event": event})
    trajectory = {
        "version": p7.VERSION,
        "receipt_id": "trajectory-ev1-t06-r1",
        "task_id": TASK_ID,
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
        "candidate_id": "candidate-ev1-t06-r1",
        "task_id": TASK_ID,
        "provenance": {"source": "human-declared-hash-bound-representation"},
        "source_receipt_hash": p7.sha256_hex(trajectory),
        "policy_version": context["policy_version"],
        "policy_veto": False,
        "tampered": False,
        "quorum_decision": quorum,
        "prefix_length": len(events),
        "integrity_hash": p7.trajectory_integrity_hash(events, len(events)),
        "declared_paths": paths,
        "file_hashes": dict(sorted(file_hashes.items())),
        "executable_test": {
            "test_id": "test-ev1-t06-stable-ranking-r1",
            "path": "scripts/stable-ranking-cases.cjs",
            "feature_hash": file_hashes["scripts/stable-ranking-cases.cjs"],
            "passed": True,
        },
    }
    decision = p7.select_candidate([candidate], context)
    if decision.get("decision") != "PROMOTE":
        raise T06Error("PREPARED_CANDIDATE_NOT_ADMITTED")
    warrant = p7.make_warrant("warrant-ev1-t06-r1", TASK_ID, candidate["candidate_id"], decision)
    loss = {
        "version": p7.VERSION,
        "receipt_id": "loss-ev1-t06-r1",
        "task_id": TASK_ID,
        "manifest_hash": p7.sha256_hex(manifest),
        "lost_paths": paths,
        "absence_hash": p7.sha256_hex({"lost_paths": paths, "observed": "absent"}),
    }
    request = {
        "version": r3.surface.REQUEST_VERSION,
        "request_id": "request-ev1-t06-r1",
        "context": context,
        "loss_receipt": loss,
        "candidates": [candidate],
        "warrant": warrant,
    }
    r3.surface.canonical_json(request)
    return request


def minimal_env(*, tmpdir: Path, path: str) -> dict[str, str]:
    return {
        "CI": "1",
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        "NEXT_TELEMETRY_DISABLED": "1",
        "PATH": path,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "TMPDIR": str(tmpdir),
        "XDG_CACHE_HOME": str(CONTROL / "xdg-cache"),
        "XDG_CONFIG_HOME": str(CONTROL / "xdg-config"),
        "XDG_STATE_HOME": str(CONTROL / "xdg-state"),
        "npm_config_cache": str(CONTROL / "npm-cache"),
        "npm_config_userconfig": str(CONTROL / "npmrc"),
        "npm_config_update_notifier": "false",
    }


def record_command(name: str, completed: subprocess.CompletedProcess[bytes]) -> dict[str, Any]:
    raw = completed.stdout + completed.stderr
    atomic_bytes(CONTROL / f"{name}.log", raw)
    return {"exit": completed.returncode, "log_bytes": len(raw), "log_sha256": digest(raw)}


def verify_product(r3: Any) -> tuple[Path, Path, Path]:
    if digest(r3.PROFILE) != EXPECTED_PROFILE_SHA256:
        raise T06Error("SEATBELT_PROFILE_HASH_MISMATCH")
    try:
        return T04.verify_product(r3)
    except RuntimeError as exc:
        raise T06Error(f"PRODUCT_RUNTIME_INVALID:{exc}") from exc


def dependency_shape(root: Path) -> dict[str, Any]:
    try:
        return T04.dependency_shape(root)
    except RuntimeError as exc:
        raise T06Error(f"DEPENDENCY_SHAPE_INVALID:{exc}") from exc


def clone_dependencies(source: Path, destination: Path) -> dict[str, Any]:
    try:
        return T04.clone_dependencies(source, destination)
    except RuntimeError as exc:
        raise T06Error(f"DEPENDENCY_CLONE_INVALID:{exc}") from exc


def export_baseline_snapshot() -> dict[str, str]:
    if BASELINE_SNAPSHOT.exists() or BASELINE_SNAPSHOT.is_symlink():
        raise T06Error("BASELINE_SNAPSHOT_PREEXISTS")
    listed = git("ls-tree", "-r", "-z", BASELINE_COMMIT)
    if listed.returncode != 0:
        raise T06Error("BASELINE_TREE_LIST_FAILED")
    count = 0
    for record in listed.stdout.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split()
        relative = raw_path.decode("utf-8")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or "\x00" in relative:
            raise T06Error("BASELINE_PATH_UNSAFE")
        if object_type != "blob" or mode == "120000":
            raise T06Error("BASELINE_ENTRY_NOT_REGULAR_FILE")
        blob = git("cat-file", "blob", object_id)
        if blob.returncode != 0:
            raise T06Error("BASELINE_BLOB_READ_FAILED")
        target = BASELINE_SNAPSHOT.joinpath(*pure.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, blob.stdout, 0o600)
        count += 1
    if count != BASELINE_FILE_COUNT:
        raise T06Error("BASELINE_FILE_COUNT_MISMATCH")
    return tree_hashes(BASELINE_SNAPSHOT)


def restore_baseline(destination: Path, omit: set[str]) -> int:
    if destination.exists() or destination.is_symlink():
        raise T06Error("SUCCESSOR_BASELINE_DESTINATION_PREEXISTS")
    destination.mkdir(parents=True, mode=0o700)
    count = 0
    for relative in sorted(tree_hashes(BASELINE_SNAPSHOT)):
        if relative in omit:
            continue
        source = safe_file(BASELINE_SNAPSHOT, relative)
        target = destination.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, source.read_bytes(), 0o600)
        count += 1
    return count


def copy_representations_into(destination: Path) -> None:
    candidate = REPRESENTATIONS / "candidate-ev1-t06-r1"
    for relative in DECLARED:
        source = safe_file(candidate, relative)
        target = destination.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, source.read_bytes(), 0o600)


def capture() -> int:
    if CAPTURE_RECEIPT.exists() or TASK_RECEIPT.exists() or FAILURE_RECEIPT.exists():
        raise T06Error("T05_CAPTURE_ALREADY_STARTED")
    if any(
        path.exists()
        for path in (
            RECOVERY,
            BASELINE_SNAPSHOT,
            DEPENDENCY_RUNTIME,
            EXECUTION_CAMPAIGN,
            PREFLIGHT_CAMPAIGN,
        )
    ):
        raise T06Error("PREEXISTING_CAMPAIGN_ROOT")
    state = verify_work_state()
    r3 = load_r3()
    toolchain, _venv, entrypoint = verify_product(r3)
    baseline_hashes = export_baseline_snapshot()
    for path in (REPRESENTATIONS, CUSTODY, OUTPUT, TEMP):
        path.mkdir(parents=True, mode=0o700)
    candidate = REPRESENTATIONS / "candidate-ev1-t06-r1"
    for relative in DECLARED:
        target = candidate.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, safe_file(ORIGINAL, relative).read_bytes(), 0o600)
    request = make_request(r3, state["file_hashes"])
    atomic_bytes(REQUEST, r3.surface.canonical_json(request), 0o600)
    outside = CONTROL / "outside-kill-canary.txt"
    atomic_bytes(outside, b"EV1-T06 outside kill canary\n")
    body = {
        "version": "ev1-t06-capture-receipt-v1",
        "status": "EV1_T06_CAPTURE_GREEN_EXECUTION_NOT_STARTED",
        "task_id": TASK_ID,
        "capture_declaration": CAPTURE_DECLARATION,
        "capture_declaration_utc": CAPTURE_DECLARATION_UTC,
        "authorization_file_sha256": AUTHORIZATION_FILE_SHA256,
        "backlog_sha256": BACKLOG_SHA256,
        "preflight_packet_sha256": PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "source_commit": SOURCE_COMMIT,
        "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
        "baseline_commit": BASELINE_COMMIT,
        "baseline_snapshot_hashes": baseline_hashes,
        "baseline_snapshot_file_count": len(baseline_hashes),
        "baseline_attribution": "ORDINARY_GIT_EQUIVALENT_NOT_RECOVERED_TASK_WORK",
        "work_receipt_file_sha256": WORK_RECEIPT_FILE_SHA256,
        "work_receipt_internal_sha256": WORK_RECEIPT_INTERNAL_SHA256,
        "declared_state": state,
        "request_sha256": digest(REQUEST),
        "representation_hashes": tree_hashes(REPRESENTATIONS),
        "representation_aggregate_bytes": sum(
            path.stat().st_size for path in REPRESENTATIONS.rglob("*") if path.is_file()
        ),
        "seatbelt_profile_sha256": digest(r3.PROFILE),
        "offline_profile_sha256": digest(CONTROL / "offline.sb"),
        "product_entrypoint_sha256": digest(entrypoint),
        "product_runtime": {
            "toolchain_sha256": digest(toolchain / "bin" / "python3.12"),
            "entrypoint_sha256": digest(entrypoint),
            "source": "hash-bound closed T01 project-local product runtime",
        },
        "kill_target": ".ev1-runtime/EV1-T06/workspace",
        "kill_target_guarded": True,
        "outside_canary_sha256": digest(outside),
        "capture_complete": True,
        "deletion_started": False,
        "recovery_started": False,
    }
    receipt_hash, file_hash = atomic_record(CAPTURE_RECEIPT, body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


def run_acceptance(workspace: Path, prefix: str, tmpdir: Path) -> dict[str, Any]:
    environment = minimal_env(
        tmpdir=tmpdir,
        path=f"{workspace / 'node_modules' / '.bin'}:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
    )
    results: dict[str, Any] = {}
    commands = (
        (f"{prefix}-stable-ranking", ["/usr/local/bin/npm", "run", "test:stable-ranking"], 300),
        (f"{prefix}-typecheck", ["/usr/local/bin/npm", "run", "typecheck"], 600),
        (f"{prefix}-build", ["/usr/local/bin/npm", "run", "build"], 1200),
    )
    for name, argv, timeout in commands:
        completed = run(
            ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *argv],
            cwd=workspace,
            env=environment,
            timeout=timeout,
        )
        results[name] = record_command(name, completed)
        if completed.returncode != 0:
            raise T06Error(f"SUCCESSOR_ACCEPTANCE_FAILED:{name}")
    return results


def preflight() -> int:
    if PREFLIGHT_RECEIPT.exists() or TASK_RECEIPT.exists() or FAILURE_RECEIPT.exists():
        raise T06Error("T05_PREFLIGHT_ALREADY_STARTED")
    captured = load_receipt(CAPTURE_RECEIPT)
    if captured.get("status") != "EV1_T06_CAPTURE_GREEN_EXECUTION_NOT_STARTED":
        raise T06Error("CAPTURE_STATUS_INVALID")
    if verify_work_state() != captured.get("declared_state"):
        raise T06Error("POST_CAPTURE_STATE_DRIFT")
    if digest(REQUEST) != captured.get("request_sha256"):
        raise T06Error("CAPTURE_REQUEST_DRIFT")
    if tree_hashes(REPRESENTATIONS) != captured.get("representation_hashes"):
        raise T06Error("CAPTURE_REPRESENTATION_DRIFT")
    if tree_hashes(BASELINE_SNAPSHOT) != captured.get("baseline_snapshot_hashes"):
        raise T06Error("CAPTURE_BASELINE_DRIFT")
    if PREFLIGHT_CAMPAIGN.exists() or EXECUTION_CAMPAIGN.exists():
        raise T06Error("TEMP_ROOT_PREEXISTS")

    r3 = load_r3()
    toolchain, venv, entrypoint = verify_product(r3)
    product_canary = PREFLIGHT_CAMPAIGN / "product-canary"
    product_canary.mkdir(parents=True, mode=0o700)
    r3.make_fixture(product_canary, "ev1-t06-predelete")
    representation_before = r3.tree(product_canary / "representations")
    public_root = CONTROL / "public"
    public_root.mkdir(exist_ok=True)
    product_tmp = product_canary / "tmp"
    product_tmp.mkdir(mode=0o700, exist_ok=True)
    args = [
        "recover",
        "--request", str(product_canary / "request.json"),
        "--sandbox-root", str(product_canary),
        "--workspace", str(product_canary / "workspace"),
        "--representation-root", str(product_canary / "representations"),
        "--custody-root", str(product_canary / "custody"),
        "--output-root", str(product_canary / "output"),
    ]
    command = r3.seatbelt_command(entrypoint, toolchain, venv, public_root, product_canary, args)
    product = run(
        command,
        cwd=ROOT,
        env=minimal_env(tmpdir=product_tmp, path="/usr/bin:/bin"),
        timeout=120,
    )
    product_record = record_command("t06-product-preflight", product)
    if product.returncode != 0:
        raise T06Error("PRODUCT_PREFLIGHT_FAILED")
    summary = json.loads(product.stdout)
    if summary.get("verdict") != "PROMOTE" or summary.get("fresh_context_continued") is not True:
        raise T06Error("PRODUCT_PREFLIGHT_NOT_PROMOTED")
    if r3.tree(product_canary / "representations") != representation_before:
        raise T06Error("PRODUCT_PREFLIGHT_REPRESENTATION_MUTATED")

    dependency_workspace = PREFLIGHT_CAMPAIGN / "dependency-canary" / "workspace"
    baseline_files = restore_baseline(dependency_workspace, set(DECLARED))
    if baseline_files != 18 or (dependency_workspace / ".git").exists():
        raise T06Error("DEPENDENCY_CANARY_BASELINE_INVALID")
    copy_representations_into(dependency_workspace)
    dependency = clone_dependencies(ORIGINAL / "node_modules", dependency_workspace / "node_modules")
    dependency_tmp = PREFLIGHT_CAMPAIGN / "dependency-canary" / "tmp"
    dependency_tmp.mkdir(mode=0o700)
    acceptance = run_acceptance(dependency_workspace, "t06-dependency-preflight", dependency_tmp)
    hashes = {relative: digest(safe_file(dependency_workspace, relative)) for relative in DECLARED}
    if hashes != EXPECTED_HASHES:
        raise T06Error("DEPENDENCY_CANARY_WORK_UNITS_MISMATCH")

    shutil.rmtree(PREFLIGHT_CAMPAIGN)
    if PREFLIGHT_CAMPAIGN.exists():
        raise T06Error("PREFLIGHT_TEARDOWN_FAILED")
    body = {
        "version": "ev1-t06-execution-preflight-receipt-v1",
        "status": "EV1_T06_EXECUTION_PREFLIGHT_GREEN_DELETION_NOT_STARTED",
        "task_id": TASK_ID,
        "capture_file_sha256": digest(CAPTURE_RECEIPT),
        "capture_receipt_sha256": captured["receipt_sha256"],
        "runner_sha256": digest(Path(__file__).resolve()),
        "t04_primitive_source_sha256": T04_RUNNER_SHA256,
        "execution_root": "/private/tmp/ck-ev1-t06-r1",
        "successor_dependency_topology": "SUCCESSOR_ROOT/node_modules",
        "baseline_attribution": captured["baseline_attribution"],
        "product_canary": {**product_record, "summary": summary, "representation_unchanged": True},
        "dependency_topology_canary": {
            "acceptance": acceptance,
            "dependency_shape": dependency,
            "declared_file_hashes": hashes,
        },
        "preflight_temp_root_absent": True,
        "execution_temp_root_absent": not EXECUTION_CAMPAIGN.exists(),
        "deletion_started": False,
        "recovery_started": False,
    }
    receipt_hash, file_hash = atomic_record(PREFLIGHT_RECEIPT, body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


def guarded_destroy() -> dict[str, Any]:
    expected = CAMPAIGN / "workspace"
    if ORIGINAL != expected or ORIGINAL.is_symlink() or not ORIGINAL.is_dir():
        raise T06Error("KILL_TARGET_MISMATCH")
    campaign_resolved = CAMPAIGN.resolve(strict=True)
    original_resolved = ORIGINAL.resolve(strict=True)
    if original_resolved != expected.resolve(strict=True) or campaign_resolved not in original_resolved.parents:
        raise T06Error("KILL_TARGET_ESCAPE")
    before = time.monotonic_ns()
    shutil.rmtree(ORIGINAL)
    elapsed = time.monotonic_ns() - before
    if ORIGINAL.exists() or not (CONTROL / "outside-kill-canary.txt").is_file():
        raise T06Error("KILL_OR_CANARY_VERIFICATION_FAILED")
    return {"elapsed_monotonic_ns": elapsed, "original_absent": True, "outside_canary_survived": True}


def preserve_failure(reason: str) -> None:
    if not FAILURE_SNAPSHOT.exists():
        if EXECUTION_OUTPUT.is_dir():
            shutil.copytree(EXECUTION_OUTPUT, FAILURE_SNAPSHOT / "output", copy_function=shutil.copy2)
        if EXECUTION_CUSTODY.is_dir():
            shutil.copytree(EXECUTION_CUSTODY, FAILURE_SNAPSHOT / "custody", copy_function=shutil.copy2)
        if EXECUTION_SUCCESSOR.is_dir():
            for relative in DECLARED:
                source = EXECUTION_SUCCESSOR.joinpath(*PurePosixPath(relative).parts)
                if source.is_file() and not source.is_symlink():
                    target = FAILURE_SNAPSHOT / "restored" / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    atomic_bytes(target, source.read_bytes())
    if not FAILURE_RECEIPT.exists():
        atomic_record(
            FAILURE_RECEIPT,
            {
                "version": "ev1-t06-failure-receipt-v1",
                "status": "EV1_T06_BLOCKED",
                "reason": reason,
                "original_workspace_exists": ORIGINAL.exists(),
                "successor_workspace_exists": EXECUTION_SUCCESSOR.exists(),
                "capture_receipt_exists": CAPTURE_RECEIPT.exists(),
                "preflight_receipt_exists": PREFLIGHT_RECEIPT.exists(),
                "task_receipt_exists": TASK_RECEIPT.exists(),
                "failure_snapshot_hashes": tree_hashes(FAILURE_SNAPSHOT),
                "utc_recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )


def execute() -> int:
    if TASK_RECEIPT.exists() or FAILURE_RECEIPT.exists():
        raise T06Error("T05_EXECUTION_ALREADY_TERMINAL")
    captured = load_receipt(CAPTURE_RECEIPT)
    preflighted = load_receipt(PREFLIGHT_RECEIPT)
    if captured.get("status") != "EV1_T06_CAPTURE_GREEN_EXECUTION_NOT_STARTED":
        raise T06Error("CAPTURE_STATUS_INVALID")
    if preflighted.get("status") != "EV1_T06_EXECUTION_PREFLIGHT_GREEN_DELETION_NOT_STARTED":
        raise T06Error("EXECUTION_PREFLIGHT_STATUS_INVALID")
    if preflighted.get("capture_file_sha256") != digest(CAPTURE_RECEIPT):
        raise T06Error("PREFLIGHT_CAPTURE_DRIFT")
    if preflighted.get("runner_sha256") != digest(Path(__file__).resolve()):
        raise T06Error("RUNNER_DRIFT")
    if verify_work_state() != captured.get("declared_state"):
        raise T06Error("PRE_EXECUTION_STATE_DRIFT")
    if digest(REQUEST) != captured.get("request_sha256"):
        raise T06Error("REQUEST_DRIFT")
    if tree_hashes(REPRESENTATIONS) != captured.get("representation_hashes"):
        raise T06Error("REPRESENTATION_DRIFT")
    if tree_hashes(BASELINE_SNAPSHOT) != captured.get("baseline_snapshot_hashes"):
        raise T06Error("BASELINE_SNAPSHOT_DRIFT")
    if EXECUTION_CAMPAIGN.exists() or DEPENDENCY_RUNTIME.exists():
        raise T06Error("EXECUTION_ROOT_PREEXISTS")

    r3 = load_r3()
    toolchain, venv, entrypoint = verify_product(r3)
    if digest(entrypoint) != captured.get("product_entrypoint_sha256"):
        raise T06Error("PRODUCT_ENTRYPOINT_DRIFT")
    for path in (EXECUTION_REPRESENTATIONS, EXECUTION_CUSTODY, EXECUTION_OUTPUT, EXECUTION_TEMP):
        path.mkdir(parents=True, mode=0o700)
    shutil.copytree(REPRESENTATIONS, EXECUTION_REPRESENTATIONS, dirs_exist_ok=True, copy_function=shutil.copy2)
    atomic_bytes(EXECUTION_REQUEST, REQUEST.read_bytes())
    if tree_hashes(EXECUTION_REPRESENTATIONS) != captured["representation_hashes"]:
        raise T06Error("EXECUTION_REPRESENTATION_COPY_MISMATCH")
    if digest(EXECUTION_REQUEST) != captured["request_sha256"]:
        raise T06Error("EXECUTION_REQUEST_COPY_MISMATCH")

    source_dependencies = ORIGINAL / "node_modules"
    if source_dependencies.is_symlink() or not source_dependencies.is_dir():
        raise T06Error("ORIGINAL_DEPENDENCY_RUNTIME_MISSING")
    DEPENDENCY_RUNTIME.mkdir(mode=0o700)
    shutil.move(str(source_dependencies), str(DEPENDENCY_RUNTIME / "node_modules"))
    dependency = dependency_shape(DEPENDENCY_RUNTIME / "node_modules")
    kill = guarded_destroy()

    baseline_files = restore_baseline(EXECUTION_SUCCESSOR, set(DECLARED))
    if baseline_files != 18 or (EXECUTION_SUCCESSOR / ".git").exists():
        raise T06Error("SUCCESSOR_BASELINE_INVALID")
    successor_dependency = clone_dependencies(
        DEPENDENCY_RUNTIME / "node_modules", EXECUTION_SUCCESSOR / "node_modules"
    )
    if successor_dependency != dependency:
        raise T06Error("SUCCESSOR_DEPENDENCY_DRIFT")

    public_root = CONTROL / "public"
    public_root.mkdir(exist_ok=True)
    args = [
        "recover",
        "--request", str(EXECUTION_REQUEST),
        "--sandbox-root", str(EXECUTION_RECOVERY),
        "--workspace", str(EXECUTION_SUCCESSOR),
        "--representation-root", str(EXECUTION_REPRESENTATIONS),
        "--custody-root", str(EXECUTION_CUSTODY),
        "--output-root", str(EXECUTION_OUTPUT),
    ]
    command = r3.seatbelt_command(entrypoint, toolchain, venv, public_root, EXECUTION_RECOVERY, args)
    invocation_start = time.monotonic_ns()
    recovered = run(
        command,
        cwd=ROOT,
        env=minimal_env(tmpdir=EXECUTION_TEMP, path="/usr/bin:/bin"),
        timeout=120,
    )
    productive_ns = time.monotonic_ns() - invocation_start
    recovery_record = record_command("t06-recovery", recovered)
    if recovered.returncode != 0:
        raise T06Error(f"PRODUCT_RECOVERY_FAILED:{recovered.returncode}")
    summary = json.loads(recovered.stdout)
    if summary.get("verdict") != "PROMOTE" or summary.get("fresh_context_continued") is not True:
        raise T06Error("PRODUCT_RECOVERY_NOT_PROMOTED")
    if tree_hashes(EXECUTION_REPRESENTATIONS) != captured["representation_hashes"]:
        raise T06Error("EXECUTION_REPRESENTATION_MUTATED")
    if tree_hashes(REPRESENTATIONS) != captured["representation_hashes"]:
        raise T06Error("AUTHORITATIVE_REPRESENTATION_MUTATED")
    if tree_hashes(BASELINE_SNAPSHOT) != captured["baseline_snapshot_hashes"]:
        raise T06Error("AUTHORITATIVE_BASELINE_MUTATED")

    acceptance = run_acceptance(EXECUTION_SUCCESSOR, "t06-successor", EXECUTION_TEMP)
    acceptance_ns = time.monotonic_ns() - invocation_start
    restored = {relative: digest(safe_file(EXECUTION_SUCCESSOR, relative)) for relative in DECLARED}
    if restored != EXPECTED_HASHES:
        raise T06Error("SUCCESSOR_WORK_UNITS_MISMATCH")
    process_scan = run(["ps", "-axo", "pid=,command="], cwd=ROOT, timeout=30)
    if process_scan.returncode != 0:
        raise T06Error("PROCESS_RESIDUE_SCAN_FAILED")
    markers = (str(ORIGINAL), str(EXECUTION_RECOVERY))
    residue: list[str] = []
    for raw_line in process_scan.stdout.splitlines():
        line = raw_line.decode("utf-8", "replace").strip()
        fields = line.split(maxsplit=1)
        if len(fields) == 2 and fields[0].isdigit() and int(fields[0]) != os.getpid():
            if any(marker in fields[1] for marker in markers):
                residue.append(line)
    if residue:
        raise T06Error("TASK_PROCESS_RESIDUE")

    snapshot = CONTROL / "POST_RECOVERY_SNAPSHOT"
    if snapshot.exists():
        raise T06Error("POST_RECOVERY_SNAPSHOT_PREEXISTS")
    shutil.copytree(EXECUTION_OUTPUT, snapshot / "output", copy_function=shutil.copy2)
    shutil.copytree(EXECUTION_CUSTODY, snapshot / "custody", copy_function=shutil.copy2)
    for relative in DECLARED:
        target = snapshot / "restored" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, safe_file(EXECUTION_SUCCESSOR, relative).read_bytes())
    body = {
        "version": "ev1-task-execution-receipt-v1",
        "status": "MECHANICAL_TASK_COMPLETE_OPERATOR_OBSERVATION_REQUIRED",
        "task_id": TASK_ID,
        "backlog_sha256": BACKLOG_SHA256,
        "preflight_packet_sha256": PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "source_commit": SOURCE_COMMIT,
        "project_class": "MEDIUM_MULTI_MODULE",
        "capture_file_sha256": digest(CAPTURE_RECEIPT),
        "capture_receipt_sha256": captured["receipt_sha256"],
        "execution_preflight_file_sha256": digest(PREFLIGHT_RECEIPT),
        "execution_preflight_receipt_sha256": preflighted["receipt_sha256"],
        "capture_declaration": CAPTURE_DECLARATION,
        "capture_declaration_utc": CAPTURE_DECLARATION_UTC,
        "state_mix": {"committed": True, "uncommitted": True, "untracked": True, "human_edit": False},
        "declared_work_units_before_loss": 5,
        "usable_work_units_after_continuation": 5,
        "kill": kill,
        "empty_history_successor": True,
        "execution_root_class": "BOUNDED_PRIVATE_TMP",
        "baseline_attribution": captured["baseline_attribution"],
        "baseline_files_recreated": baseline_files,
        "dependency_runtime": dependency,
        "successor_dependency_topology": "SUCCESSOR_ROOT/node_modules",
        "recovery": recovery_record,
        "recovery_summary": summary,
        "output_hashes": tree_hashes(EXECUTION_OUTPUT),
        "custody_hashes": tree_hashes(EXECUTION_CUSTODY),
        "post_recovery_snapshot_hashes": tree_hashes(snapshot),
        "restored_file_hashes": restored,
        "acceptance_command": "npm run test:stable-ranking && npm run typecheck && npm run build",
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
    parser.add_argument("phase", choices=("capture", "preflight", "execute"))
    arguments = parser.parse_args()
    try:
        if arguments.phase == "capture":
            return capture()
        if arguments.phase == "preflight":
            return preflight()
        return execute()
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired, T06Error) as exc:
        reason = str(exc) or exc.__class__.__name__
        if arguments.phase == "execute":
            try:
                preserve_failure(reason)
            except OSError:
                pass
        print(canonical({"status": "EV1_T06_BLOCKED", "phase": arguments.phase, "reason": reason}).decode())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
