#!/usr/bin/env python3
"""Capture and execute the frozen EV1-T02 recovery campaign.

The runner reuses only hash-bound primitives from the closed T01 runner. It
changes the successor topology so the preserved dependency tree is cloned into
the successor's own ``node_modules`` ancestry before recovery and acceptance.
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
TASK_ID = "EV1-T02"
CAMPAIGN = ROOT / ".ev1-runtime" / TASK_ID
CONTROL = CAMPAIGN / "control"
ORIGINAL = CAMPAIGN / "workspace"
RECOVERY = CAMPAIGN / "recovery"
REPRESENTATIONS = RECOVERY / "representations"
CUSTODY = RECOVERY / "custody"
OUTPUT = RECOVERY / "output"
TEMP = RECOVERY / "tmp"
REQUEST = RECOVERY / "request.json"
DEPENDENCY_RUNTIME = CAMPAIGN / "dependency-runtime"
PREPARATION_RECEIPT = CONTROL / "PREPARATION_RECEIPT.json"
WORK_RECEIPT = CONTROL / "WORK_RECEIPT.json"
CAPTURE_RECEIPT = CONTROL / "CAPTURE_RECEIPT.json"
PREFLIGHT_RECEIPT = CONTROL / "EXECUTION_PREFLIGHT_RECEIPT.json"
TASK_RECEIPT = CONTROL / "TASK_EXECUTION_RECEIPT.json"
FAILURE_RECEIPT = CONTROL / "TASK_FAILURE_RECEIPT.json"
FAILURE_SNAPSHOT = CONTROL / "FAILURE_SNAPSHOT"
PREFLIGHT_CAMPAIGN = Path("/private/tmp/ck-ev1-t02-preflight-r1")
EXECUTION_CAMPAIGN = Path("/private/tmp/ck-ev1-t02-r1")
EXECUTION_RECOVERY = EXECUTION_CAMPAIGN / "recovery"
EXECUTION_SUCCESSOR = EXECUTION_RECOVERY / "workspace"
EXECUTION_REPRESENTATIONS = EXECUTION_RECOVERY / "representations"
EXECUTION_CUSTODY = EXECUTION_RECOVERY / "custody"
EXECUTION_OUTPUT = EXECUTION_RECOVERY / "output"
EXECUTION_TEMP = EXECUTION_RECOVERY / "tmp"
EXECUTION_REQUEST = EXECUTION_RECOVERY / "request.json"
SOURCE_COMMIT = "1a92380a9edf12337f80b3c42ba098a7c1724664"
SOURCE_MANIFEST_SHA256 = "d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706"
BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
T01_RUNNER_SHA256 = "daf88b6029cfb44bd183ab1af87dcd22c0213fc4ea27bbe90d62994086bc5271"
AUTHORIZATION_FILE_SHA256 = "28045cf30dd0219c6cbab3c55b7b0c0c1bcbc7563cc2a24e10781538c1257908"
WORK_RECEIPT_FILE_SHA256 = "48a5856158cc43884cfd1d500adb0121f207b5b1d05a172e759eab8de78571d9"
WORK_RECEIPT_INTERNAL_SHA256 = "a97a025c62baedbad53bdcda6baf668e603e755845613fb3c8d9e9e9d7cc1b91"
TASK_COMMIT = "769321ec9828948afdacc7856321495c0ffd40a6"
CAPTURE_DECLARATION = (
    "I, Kenneth, explicitly declare the exact current EV1-T02 state—committed "
    "scripts/run-storage-contract.mjs at task commit "
    "769321ec9828948afdacc7856321495c0ffd40a6, modified package.json, and "
    "untracked scripts/storage-contract-cases.cjs—permitted for capture, "
    "guarded disposable-workspace deletion, and fresh-process recovery under "
    "the frozen EV1 protocol."
)
CAPTURE_DECLARATION_UTC = "2026-07-30T16:39:22Z"
DECLARED = (
    "package.json",
    "scripts/run-storage-contract.mjs",
    "scripts/storage-contract-cases.cjs",
)
EXPECTED_STATUS = [" M package.json", "?? scripts/storage-contract-cases.cjs"]
EXPECTED_HASHES = {
    "package.json": "b66777767e93866256960f1bf03ace59a26b55c1c880a6a54ca8c74516379d10",
    "scripts/run-storage-contract.mjs": "92148e576b4a1415d6b5a23169d384b6262de3b8878b5dfbcabae6ca56f6e65c",
    "scripts/storage-contract-cases.cjs": "e402403a667ec1c4d889bddb181f34d2c98890ddb3b1bf8a823b0cc13584dc25",
}
EXPECTED_LOGS = {
    "work-typecheck.log": "7ad5370190f3f13153e8329d717ccdfec065241392cd850b68579e68731ca022",
    "work-build.log": "a7ad9f0d6a9b0ab7d3f7620f88b5a79541921f9f413da0f30d1b16efe3b271ec",
    "work-storage-contract.log": "e0e17be36612802c5e86564121147c291bd593e01277bc1d7b4adfa19a019e77",
}
EXPECTED_PROFILE_SHA256 = "6358a9beae8361105578231b64ca638a99cbf780e1c8f5d24f9ff71891f0bc2b"
OFFLINE_PROFILE_SHA256 = "5c358b8d847211333e7ba22df82d84f796b5f30a41a2682209a949d783adbd08"


class T02Error(RuntimeError):
    pass


def load_t01() -> Any:
    path = ROOT / "external-validity" / "run_ev1_t01.py"
    if hashlib.sha256(path.read_bytes()).hexdigest() != T01_RUNNER_SHA256:
        raise T02Error("T01_PRIMITIVE_SOURCE_DRIFT")
    spec = importlib.util.spec_from_file_location("ev1_t01_frozen", path)
    if spec is None or spec.loader is None:
        raise T02Error("T01_PRIMITIVE_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


T01 = load_t01()
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
        raise T02Error("RECEIPT_NOT_CANONICAL")
    value = json.loads(raw[:-1])
    if canonical(value) + b"\n" != raw:
        raise T02Error("RECEIPT_NOT_CANONICAL")
    body = {key: value[key] for key in value if key != "receipt_sha256"}
    if value.get("receipt_sha256") != digest(body):
        raise T02Error("RECEIPT_HASH_MISMATCH")
    return value


def git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return run(["git", *arguments], cwd=ORIGINAL, timeout=120)


def safe_file(root: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or "\x00" in relative:
        raise T02Error("DECLARED_PATH_UNSAFE")
    target = root.joinpath(*pure.parts)
    resolved = target.resolve(strict=True)
    if root.resolve(strict=True) not in resolved.parents:
        raise T02Error("DECLARED_PATH_ESCAPE")
    if target.is_symlink() or not target.is_file():
        raise T02Error("DECLARED_FILE_UNSAFE")
    return target


def verify_work_state() -> dict[str, Any]:
    if digest(WORK_RECEIPT) != WORK_RECEIPT_FILE_SHA256:
        raise T02Error("WORK_RECEIPT_FILE_DRIFT")
    receipt = load_receipt(WORK_RECEIPT)
    if receipt.get("receipt_sha256") != WORK_RECEIPT_INTERNAL_SHA256:
        raise T02Error("WORK_RECEIPT_INTERNAL_DRIFT")
    if receipt.get("status") != "EV1_T02_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED":
        raise T02Error("WORK_RECEIPT_STATUS_INVALID")
    head = git("rev-parse", "HEAD")
    status = git("status", "--porcelain=v1", "-uall")
    if head.returncode != 0 or head.stdout.decode().strip() != TASK_COMMIT:
        raise T02Error("TASK_COMMIT_DRIFT")
    if status.returncode != 0 or status.stdout.decode().splitlines() != EXPECTED_STATUS:
        raise T02Error("TASK_STATUS_DRIFT")
    hashes = {relative: digest(safe_file(ORIGINAL, relative)) for relative in DECLARED}
    if hashes != EXPECTED_HASHES or receipt.get("declared_file_hashes") != EXPECTED_HASHES:
        raise T02Error("TASK_FILE_HASH_DRIFT")
    for name, expected in EXPECTED_LOGS.items():
        if digest(CONTROL / name) != expected:
            raise T02Error(f"PRE_LOSS_LOG_DRIFT:{name}")
    authorization = ROOT / "EXTERNAL_VALIDITY_EV1_T02_CAPTURE_AUTHORIZATION_R1.md"
    if digest(authorization) != AUTHORIZATION_FILE_SHA256:
        raise T02Error("CAPTURE_AUTHORIZATION_DRIFT")
    return {"file_hashes": hashes, "git_status": EXPECTED_STATUS, "task_commit": TASK_COMMIT}


def make_request(r3: Any, file_hashes: dict[str, str]) -> dict[str, Any]:
    p7 = r3.p7
    paths = sorted(file_hashes)
    manifest = {
        "version": p7.VERSION,
        "manifest_id": "manifest-ev1-t02-r1",
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
        "SOURCE_BASELINE_BOUND",
        "COMMITTED_TEST_RUNNER_PRESENT",
        "UNCOMMITTED_PACKAGE_SCRIPT_PRESENT",
        "UNTRACKED_STORAGE_CASES_PRESENT",
        "OFFLINE_ACCEPTANCE_GREEN",
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
        "receipt_id": "trajectory-ev1-t02-r1",
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
        "candidate_id": "candidate-ev1-t02-r1",
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
            "test_id": "test-ev1-t02-storage-contract-r1",
            "path": "scripts/storage-contract-cases.cjs",
            "feature_hash": file_hashes["scripts/storage-contract-cases.cjs"],
            "passed": True,
        },
    }
    decision = p7.select_candidate([candidate], context)
    if decision.get("decision") != "PROMOTE":
        raise T02Error("PREPARED_CANDIDATE_NOT_ADMITTED")
    warrant = p7.make_warrant("warrant-ev1-t02-r1", TASK_ID, candidate["candidate_id"], decision)
    loss = {
        "version": p7.VERSION,
        "receipt_id": "loss-ev1-t02-r1",
        "task_id": TASK_ID,
        "manifest_hash": p7.sha256_hex(manifest),
        "lost_paths": paths,
        "absence_hash": p7.sha256_hex({"lost_paths": paths, "observed": "absent"}),
    }
    request = {
        "version": r3.surface.REQUEST_VERSION,
        "request_id": "request-ev1-t02-r1",
        "context": context,
        "loss_receipt": loss,
        "candidates": [candidate],
        "warrant": warrant,
    }
    r3.surface.canonical_json(request)
    return request


def minimal_env(*, home: Path, tmpdir: Path, path: str) -> dict[str, str]:
    return {
        "CI": "1",
        "HOME": str(home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        "NEXT_TELEMETRY_DISABLED": "1",
        "PATH": path,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "TMPDIR": str(tmpdir),
    }


def record_command(name: str, completed: subprocess.CompletedProcess[bytes]) -> dict[str, Any]:
    raw = completed.stdout + completed.stderr
    atomic_bytes(CONTROL / f"{name}.log", raw)
    return {
        "exit": completed.returncode,
        "log_bytes": len(raw),
        "log_sha256": digest(raw),
    }


def dependency_shape(root: Path) -> dict[str, Any]:
    if root.is_symlink() or not root.is_dir():
        raise T02Error("DEPENDENCY_ROOT_INVALID")
    resolved_root = root.resolve(strict=True)
    files = [path for path in root.rglob("*") if path.is_file() and not path.is_symlink()]
    directories = [path for path in root.rglob("*") if path.is_dir() and not path.is_symlink()]
    symlinks: list[dict[str, str]] = []
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_symlink()):
        raw_target = os.readlink(path)
        if Path(raw_target).is_absolute():
            raise T02Error("DEPENDENCY_ABSOLUTE_SYMLINK")
        try:
            resolved_target = path.resolve(strict=True)
        except OSError as exc:
            raise T02Error("DEPENDENCY_BROKEN_SYMLINK") from exc
        if resolved_target != resolved_root and resolved_root not in resolved_target.parents:
            raise T02Error("DEPENDENCY_SYMLINK_ESCAPE")
        symlinks.append(
            {
                "path": path.relative_to(root).as_posix(),
                "target": raw_target,
                "resolved_path": resolved_target.relative_to(resolved_root).as_posix(),
            }
        )
    special = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if not path.is_file() and not path.is_dir() and not path.is_symlink()
    ]
    if special:
        raise T02Error("DEPENDENCY_SPECIAL_FILE")
    tsc = root / "typescript" / "bin" / "tsc"
    if not tsc.is_file():
        raise T02Error("DEPENDENCY_TSC_MISSING")
    return {
        "file_count": len(files),
        "directory_count": len(directories),
        "file_bytes": sum(path.stat().st_size for path in files),
        "symlinks": symlinks,
        "tsc_sha256": digest(tsc),
    }


def clone_dependencies(source: Path, destination: Path) -> dict[str, Any]:
    if destination.exists() or destination.is_symlink():
        raise T02Error("DEPENDENCY_DESTINATION_PREEXISTS")
    source_shape = dependency_shape(source)
    completed = run(["cp", "-cR", str(source), str(destination)], cwd=ROOT, timeout=600)
    if completed.returncode != 0:
        raise T02Error("DEPENDENCY_CLONE_FAILED")
    destination_shape = dependency_shape(destination)
    if destination_shape != source_shape:
        raise T02Error("DEPENDENCY_CLONE_SHAPE_MISMATCH")
    return source_shape


def verify_product(r3: Any) -> tuple[Path, Path, Path]:
    if digest(r3.PROFILE) != EXPECTED_PROFILE_SHA256:
        raise T02Error("SEATBELT_PROFILE_HASH_MISMATCH")
    for relative, expected in r3.EXPECTED.items():
        if digest(ROOT / relative) != expected:
            raise T02Error(f"PRODUCT_CANDIDATE_DRIFT:{relative}")
    toolchain, venv, entrypoint = T01.stage_product(r3)
    if not entrypoint.is_file():
        raise T02Error("PRODUCT_ENTRYPOINT_MISSING")
    return toolchain, venv, entrypoint


def capture() -> int:
    if CAPTURE_RECEIPT.exists() or TASK_RECEIPT.exists() or FAILURE_RECEIPT.exists():
        raise T02Error("T02_CAPTURE_ALREADY_STARTED")
    if any(path.exists() for path in (RECOVERY, DEPENDENCY_RUNTIME, EXECUTION_CAMPAIGN, PREFLIGHT_CAMPAIGN)):
        raise T02Error("PREEXISTING_CAMPAIGN_ROOT")
    state = verify_work_state()
    r3 = load_r3()
    toolchain, venv, entrypoint = verify_product(r3)
    for path in (REPRESENTATIONS, CUSTODY, OUTPUT, TEMP):
        path.mkdir(parents=True, mode=0o700)
    candidate = REPRESENTATIONS / "candidate-ev1-t02-r1"
    for relative in DECLARED:
        target = candidate.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, safe_file(ORIGINAL, relative).read_bytes(), 0o600)
    request = make_request(r3, state["file_hashes"])
    atomic_bytes(REQUEST, r3.surface.canonical_json(request), 0o600)
    outside = CONTROL / "outside-kill-canary.txt"
    atomic_bytes(outside, b"EV1-T02 outside kill canary\n")
    body = {
        "version": "ev1-t02-capture-receipt-v1",
        "status": "EV1_T02_CAPTURE_GREEN_EXECUTION_NOT_STARTED",
        "task_id": TASK_ID,
        "capture_declaration": CAPTURE_DECLARATION,
        "capture_declaration_utc": CAPTURE_DECLARATION_UTC,
        "authorization_file_sha256": AUTHORIZATION_FILE_SHA256,
        "backlog_sha256": BACKLOG_SHA256,
        "preflight_packet_sha256": PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "source_commit": SOURCE_COMMIT,
        "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
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
        "kill_target": ".ev1-runtime/EV1-T02/workspace",
        "kill_target_guarded": True,
        "outside_canary_sha256": digest(outside),
        "capture_complete": True,
        "deletion_started": False,
        "recovery_started": False,
    }
    receipt_hash, file_hash = atomic_record(CAPTURE_RECEIPT, body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


def preflight() -> int:
    if PREFLIGHT_RECEIPT.exists() or TASK_RECEIPT.exists() or FAILURE_RECEIPT.exists():
        raise T02Error("T02_PREFLIGHT_ALREADY_STARTED")
    captured = load_receipt(CAPTURE_RECEIPT)
    if captured.get("status") != "EV1_T02_CAPTURE_GREEN_EXECUTION_NOT_STARTED":
        raise T02Error("CAPTURE_STATUS_INVALID")
    if verify_work_state() != captured.get("declared_state"):
        raise T02Error("POST_CAPTURE_STATE_DRIFT")
    if digest(REQUEST) != captured.get("request_sha256"):
        raise T02Error("CAPTURE_REQUEST_DRIFT")
    if tree_hashes(REPRESENTATIONS) != captured.get("representation_hashes"):
        raise T02Error("CAPTURE_REPRESENTATION_DRIFT")
    if PREFLIGHT_CAMPAIGN.exists() or EXECUTION_CAMPAIGN.exists():
        raise T02Error("TEMP_ROOT_PREEXISTS")

    r3 = load_r3()
    toolchain, venv, entrypoint = verify_product(r3)
    product_canary = PREFLIGHT_CAMPAIGN / "product-canary"
    product_canary.mkdir(parents=True, mode=0o700)
    r3.make_fixture(product_canary, "ev1-t02-predelete")
    representation_before = r3.tree(product_canary / "representations")
    public_root = CONTROL / "public"
    public_root.mkdir(exist_ok=True)
    empty_home = PREFLIGHT_CAMPAIGN / "empty-home"
    empty_home.mkdir(mode=0o700)
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
    env = minimal_env(
        home=empty_home,
        tmpdir=product_canary / "tmp",
        path="/usr/bin:/bin",
    )
    product = run(command, cwd=ROOT, env=env, timeout=120)
    product_record = record_command("t02-product-preflight", product)
    if product.returncode != 0:
        raise T02Error("PRODUCT_PREFLIGHT_FAILED")
    summary = json.loads(product.stdout)
    if summary.get("verdict") != "PROMOTE" or summary.get("fresh_context_continued") is not True:
        raise T02Error("PRODUCT_PREFLIGHT_NOT_PROMOTED")
    if r3.tree(product_canary / "representations") != representation_before:
        raise T02Error("PRODUCT_PREFLIGHT_REPRESENTATION_MUTATED")

    dependency_workspace = PREFLIGHT_CAMPAIGN / "dependency-canary" / "workspace"
    baseline_files = T01.export_baseline(dependency_workspace, omit=set())
    if baseline_files != 76 or (dependency_workspace / ".git").exists():
        raise T02Error("DEPENDENCY_CANARY_BASELINE_INVALID")
    dependency = clone_dependencies(ORIGINAL / "node_modules", dependency_workspace / "node_modules")
    dependency_tmp = PREFLIGHT_CAMPAIGN / "dependency-canary" / "tmp"
    dependency_tmp.mkdir(mode=0o700)
    typecheck = run(
        [
            "/usr/bin/sandbox-exec",
            "-f",
            str(CONTROL / "offline.sb"),
            "/usr/local/bin/npm",
            "run",
            "typecheck",
        ],
        cwd=dependency_workspace,
        env=minimal_env(
            home=empty_home,
            tmpdir=dependency_tmp,
            path=f"{dependency_workspace / 'node_modules' / '.bin'}:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        ),
        timeout=600,
    )
    typecheck_record = record_command("t02-dependency-topology-preflight", typecheck)
    if typecheck.returncode != 0:
        raise T02Error("DEPENDENCY_TOPOLOGY_PREFLIGHT_FAILED")

    shutil.rmtree(PREFLIGHT_CAMPAIGN)
    if PREFLIGHT_CAMPAIGN.exists():
        raise T02Error("PREFLIGHT_TEARDOWN_FAILED")
    body = {
        "version": "ev1-t02-execution-preflight-receipt-v1",
        "status": "EV1_T02_EXECUTION_PREFLIGHT_GREEN_DELETION_NOT_STARTED",
        "task_id": TASK_ID,
        "capture_file_sha256": digest(CAPTURE_RECEIPT),
        "capture_receipt_sha256": captured["receipt_sha256"],
        "runner_sha256": digest(Path(__file__).resolve()),
        "t01_primitive_source_sha256": T01_RUNNER_SHA256,
        "execution_root": "/private/tmp/ck-ev1-t02-r1",
        "successor_dependency_topology": "SUCCESSOR_ROOT/node_modules",
        "product_canary": {**product_record, "summary": summary, "representation_unchanged": True},
        "dependency_topology_canary": {**typecheck_record, "dependency_shape": dependency},
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
        raise T02Error("KILL_TARGET_MISMATCH")
    campaign_resolved = CAMPAIGN.resolve(strict=True)
    original_resolved = ORIGINAL.resolve(strict=True)
    if original_resolved != expected.resolve(strict=True) or campaign_resolved not in original_resolved.parents:
        raise T02Error("KILL_TARGET_ESCAPE")
    before = time.monotonic_ns()
    shutil.rmtree(ORIGINAL)
    elapsed = time.monotonic_ns() - before
    if ORIGINAL.exists() or not (CONTROL / "outside-kill-canary.txt").is_file():
        raise T02Error("KILL_OR_CANARY_VERIFICATION_FAILED")
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
                "version": "ev1-t02-failure-receipt-v1",
                "status": "EV1_T02_BLOCKED",
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
        raise T02Error("T02_EXECUTION_ALREADY_TERMINAL")
    captured = load_receipt(CAPTURE_RECEIPT)
    preflighted = load_receipt(PREFLIGHT_RECEIPT)
    if captured.get("status") != "EV1_T02_CAPTURE_GREEN_EXECUTION_NOT_STARTED":
        raise T02Error("CAPTURE_STATUS_INVALID")
    if preflighted.get("status") != "EV1_T02_EXECUTION_PREFLIGHT_GREEN_DELETION_NOT_STARTED":
        raise T02Error("EXECUTION_PREFLIGHT_STATUS_INVALID")
    if preflighted.get("capture_file_sha256") != digest(CAPTURE_RECEIPT):
        raise T02Error("PREFLIGHT_CAPTURE_DRIFT")
    if preflighted.get("runner_sha256") != digest(Path(__file__).resolve()):
        raise T02Error("RUNNER_DRIFT")
    if verify_work_state() != captured.get("declared_state"):
        raise T02Error("PRE_EXECUTION_STATE_DRIFT")
    if digest(REQUEST) != captured.get("request_sha256"):
        raise T02Error("REQUEST_DRIFT")
    if tree_hashes(REPRESENTATIONS) != captured.get("representation_hashes"):
        raise T02Error("REPRESENTATION_DRIFT")
    if EXECUTION_CAMPAIGN.exists() or DEPENDENCY_RUNTIME.exists():
        raise T02Error("EXECUTION_ROOT_PREEXISTS")

    r3 = load_r3()
    toolchain, venv, entrypoint = verify_product(r3)
    if digest(entrypoint) != captured.get("product_entrypoint_sha256"):
        raise T02Error("PRODUCT_ENTRYPOINT_DRIFT")
    for path in (EXECUTION_REPRESENTATIONS, EXECUTION_CUSTODY, EXECUTION_OUTPUT, EXECUTION_TEMP):
        path.mkdir(parents=True, mode=0o700)
    empty_home = EXECUTION_CAMPAIGN / "empty-home"
    empty_home.mkdir(mode=0o700)
    shutil.copytree(REPRESENTATIONS, EXECUTION_REPRESENTATIONS, dirs_exist_ok=True, copy_function=shutil.copy2)
    atomic_bytes(EXECUTION_REQUEST, REQUEST.read_bytes())
    if tree_hashes(EXECUTION_REPRESENTATIONS) != captured["representation_hashes"]:
        raise T02Error("EXECUTION_REPRESENTATION_COPY_MISMATCH")
    if digest(EXECUTION_REQUEST) != captured["request_sha256"]:
        raise T02Error("EXECUTION_REQUEST_COPY_MISMATCH")

    source_dependencies = ORIGINAL / "node_modules"
    if source_dependencies.is_symlink() or not source_dependencies.is_dir():
        raise T02Error("ORIGINAL_DEPENDENCY_RUNTIME_MISSING")
    DEPENDENCY_RUNTIME.mkdir(mode=0o700)
    shutil.move(str(source_dependencies), str(DEPENDENCY_RUNTIME / "node_modules"))
    dependency = dependency_shape(DEPENDENCY_RUNTIME / "node_modules")
    kill = guarded_destroy()

    baseline_files = T01.export_baseline(EXECUTION_SUCCESSOR, omit=set(DECLARED))
    if baseline_files != 75 or (EXECUTION_SUCCESSOR / ".git").exists():
        raise T02Error("SUCCESSOR_BASELINE_INVALID")
    successor_dependency = clone_dependencies(
        DEPENDENCY_RUNTIME / "node_modules", EXECUTION_SUCCESSOR / "node_modules"
    )
    if successor_dependency != dependency:
        raise T02Error("SUCCESSOR_DEPENDENCY_DRIFT")

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
        env=minimal_env(home=empty_home, tmpdir=EXECUTION_TEMP, path="/usr/bin:/bin"),
        timeout=120,
    )
    productive_ns = time.monotonic_ns() - invocation_start
    recovery_record = record_command("t02-recovery", recovered)
    if recovered.returncode != 0:
        raise T02Error(f"PRODUCT_RECOVERY_FAILED:{recovered.returncode}")
    summary = json.loads(recovered.stdout)
    if summary.get("verdict") != "PROMOTE" or summary.get("fresh_context_continued") is not True:
        raise T02Error("PRODUCT_RECOVERY_NOT_PROMOTED")
    if tree_hashes(EXECUTION_REPRESENTATIONS) != captured["representation_hashes"]:
        raise T02Error("EXECUTION_REPRESENTATION_MUTATED")
    if tree_hashes(REPRESENTATIONS) != captured["representation_hashes"]:
        raise T02Error("AUTHORITATIVE_REPRESENTATION_MUTATED")

    acceptance_env = minimal_env(
        home=empty_home,
        tmpdir=EXECUTION_TEMP,
        path=f"{EXECUTION_SUCCESSOR / 'node_modules' / '.bin'}:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
    )
    acceptance: dict[str, Any] = {}
    commands = (
        ("t02-successor-typecheck", ["/usr/local/bin/npm", "run", "typecheck"], 600),
        ("t02-successor-build", ["/usr/local/bin/npm", "run", "build"], 600),
        (
            "t02-successor-storage-contract",
            ["/usr/local/bin/npm", "run", "test:storage-contract"],
            180,
        ),
    )
    for name, argv, timeout in commands:
        completed = run(
            ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *argv],
            cwd=EXECUTION_SUCCESSOR,
            env=acceptance_env,
            timeout=timeout,
        )
        acceptance[name] = record_command(name, completed)
        if completed.returncode != 0:
            raise T02Error(f"SUCCESSOR_ACCEPTANCE_FAILED:{name}")
    acceptance_ns = time.monotonic_ns() - invocation_start

    restored = {relative: digest(safe_file(EXECUTION_SUCCESSOR, relative)) for relative in DECLARED}
    if restored != EXPECTED_HASHES:
        raise T02Error("SUCCESSOR_WORK_UNITS_MISMATCH")
    process_scan = run(["ps", "-axo", "pid=,command="], cwd=ROOT, timeout=30)
    if process_scan.returncode != 0:
        raise T02Error("PROCESS_RESIDUE_SCAN_FAILED")
    markers = (str(ORIGINAL), str(EXECUTION_RECOVERY))
    residue: list[str] = []
    for raw_line in process_scan.stdout.splitlines():
        line = raw_line.decode("utf-8", "replace").strip()
        fields = line.split(maxsplit=1)
        if len(fields) == 2 and fields[0].isdigit() and int(fields[0]) != os.getpid():
            if any(marker in fields[1] for marker in markers):
                residue.append(line)
    if residue:
        raise T02Error("TASK_PROCESS_RESIDUE")

    snapshot = CONTROL / "POST_RECOVERY_SNAPSHOT"
    if snapshot.exists():
        raise T02Error("POST_RECOVERY_SNAPSHOT_PREEXISTS")
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
        "project_class": "SMALL_SINGLE_PACKAGE",
        "capture_file_sha256": digest(CAPTURE_RECEIPT),
        "capture_receipt_sha256": captured["receipt_sha256"],
        "execution_preflight_file_sha256": digest(PREFLIGHT_RECEIPT),
        "execution_preflight_receipt_sha256": preflighted["receipt_sha256"],
        "capture_declaration": CAPTURE_DECLARATION,
        "capture_declaration_utc": CAPTURE_DECLARATION_UTC,
        "state_mix": {"committed": True, "uncommitted": True, "untracked": True, "human_edit": False},
        "declared_work_units_before_loss": 3,
        "usable_work_units_after_continuation": 3,
        "kill": kill,
        "empty_history_successor": True,
        "execution_root_class": "BOUNDED_PRIVATE_TMP",
        "recovery_home_root_class": "EMPTY_EXECUTION_TEMP",
        "baseline_files_recreated": baseline_files,
        "dependency_runtime": dependency,
        "successor_dependency_topology": "SUCCESSOR_ROOT/node_modules",
        "recovery": recovery_record,
        "recovery_summary": summary,
        "output_hashes": tree_hashes(EXECUTION_OUTPUT),
        "custody_hashes": tree_hashes(EXECUTION_CUSTODY),
        "post_recovery_snapshot_hashes": tree_hashes(snapshot),
        "restored_file_hashes": restored,
        "acceptance_command": "npm run typecheck && npm run build && npm run test:storage-contract",
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
    args = parser.parse_args()
    try:
        if args.phase == "capture":
            return capture()
        if args.phase == "preflight":
            return preflight()
        return execute()
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired, T02Error) as exc:
        reason = str(exc) or exc.__class__.__name__
        if args.phase == "execute":
            try:
                preserve_failure(reason)
            except OSError:
                pass
        print(canonical({"status": "EV1_T02_BLOCKED", "phase": args.phase, "reason": reason}).decode())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
