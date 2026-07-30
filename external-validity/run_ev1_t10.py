#!/usr/bin/env python3
"""Capture and execute the frozen EV1-T10 release-note recovery task."""
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
TASK_ID = "EV1-T10"
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
DEPENDENCY_RUNTIME = CAMPAIGN / "dependency-runtime" / "node_modules"
PREPARATION_RECEIPT = CONTROL / "PREPARATION_RECEIPT.json"
WORK_RECEIPT = CONTROL / "WORK_RECEIPT.json"
CAPTURE_RECEIPT = CONTROL / "CAPTURE_RECEIPT.json"
PREFLIGHT_RECEIPT = CONTROL / "EXECUTION_PREFLIGHT_RECEIPT.json"
TASK_RECEIPT = CONTROL / "TASK_EXECUTION_RECEIPT.json"
FAILURE_RECEIPT = CONTROL / "TASK_FAILURE_RECEIPT.json"
FAILURE_SNAPSHOT = CONTROL / "FAILURE_SNAPSHOT"
PREFLIGHT_CAMPAIGN = Path("/private/tmp/ck-ev1-t10-preflight-r1")
EXECUTION_CAMPAIGN = Path("/private/tmp/ck-ev1-t10-r1")
EXECUTION_RECOVERY = EXECUTION_CAMPAIGN / "recovery"
EXECUTION_SUCCESSOR = EXECUTION_RECOVERY / "workspace"
EXECUTION_REPRESENTATIONS = EXECUTION_RECOVERY / "representations"
EXECUTION_CUSTODY = EXECUTION_RECOVERY / "custody"
EXECUTION_OUTPUT = EXECUTION_RECOVERY / "output"
EXECUTION_TEMP = EXECUTION_RECOVERY / "tmp"
EXECUTION_REQUEST = EXECUTION_RECOVERY / "request.json"
SOURCE_COMMIT = "ee6862f7d65d24d4de11eda8306d29356873b529"
SOURCE_MANIFEST_SHA256 = "6f81e7e81ad100b53163a13b11c5e7abcd437fe658f817e34905c02cbe0e7182"
BASELINE_COMMIT = "9d775362d58f3c8061953c2955f1289b6f1518a4"
BASELINE_FILE_COUNT = 410
BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
GLOBAL_PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
BASE_RUNNER = ROOT / "external-validity" / "run_ev1_t06.py"
BASE_RUNNER_SHA256 = "9158451861ba0febc6691b6320543eddc01953836f729b8077937ee2e28f5abe"
AUTHORIZATION = ROOT / "EXTERNAL_VALIDITY_EV1_T10_CAPTURE_AUTHORIZATION_R1.md"
AUTHORIZATION_SHA256 = "447c5b79ff6ac428f7b978a9d003aee4e568d85a0fa5d92291928a44d79d2383"
PREPARATION_FILE_SHA256 = "9f0d51f0546d491b593744688cba86f99582c815efb8aaeccae3f1a6c46a56e5"
PREPARATION_INTERNAL_SHA256 = "ade77d1383dd8b7c5c12afd1d4e96b4a765d37f1c6f51d826ecaf9521d1e03cf"
WORK_FILE_SHA256 = "d07d850130d7a2539c251cce53aa35ff02fbc3a6d3bcc9e5e129b8387a4eb691"
WORK_INTERNAL_SHA256 = "b77916c6cbb6b2594b114a718ee34fd9aa745013d5924185e75ab6396c7bce5f"
TASK_COMMIT = "5c671337842dc3ece20aa969f4bdec95eacc4203"
CAPTURE_DECLARATION = (
    "I, Kenneth, explicitly declare the exact current EV1-T10 state—committed "
    "scripts/validate-release-notes.mjs at task commit "
    "5c671337842dc3ece20aa969f4bdec95eacc4203, modified docs/RELEASE.md, "
    "and untracked .github/release-notes-template.md—permitted for capture, "
    "guarded disposable-workspace deletion, and fresh-process recovery under "
    "the frozen EV1 protocol."
)
CAPTURE_DECLARATION_UTC = "2026-07-30T22:26:55Z"
DECLARED = (
    ".github/release-notes-template.md",
    "docs/RELEASE.md",
    "scripts/validate-release-notes.mjs",
)
EXPECTED_STATUS = [" M docs/RELEASE.md", "?? .github/release-notes-template.md"]
EXPECTED_HASHES = {
    ".github/release-notes-template.md": "5588692402cabf72e89da0fa6d791d8bfacfbe6d33920e1d3135deb3158053f2",
    "docs/RELEASE.md": "e412093cd49a28724fd9d4c218031d8850961afd4ff6507253228d1bcf07f4b8",
    "scripts/validate-release-notes.mjs": "1320a79ab991e04055ec9f24ee60f25028cec86b10bf8dc8dfab7d1a1dcc17e8",
}
EXPECTED_LOGS = {
    "t10-prettier.log": "17aa973d3f004560237d9a95171210b0671deff23d61628eecf7322ff5938f20",
    "t10-validator-r1.log": "966293b8f766c9d0e7bce1c265dbca31f2e83e58a08a41820372f73a65fda6bb",
    "t10-validator-r2.log": "966293b8f766c9d0e7bce1c265dbca31f2e83e58a08a41820372f73a65fda6bb",
    "t10-validator-r3.log": "966293b8f766c9d0e7bce1c265dbca31f2e83e58a08a41820372f73a65fda6bb",
    "t10-validator-r4.log": "966293b8f766c9d0e7bce1c265dbca31f2e83e58a08a41820372f73a65fda6bb",
    "t10-validator-r5.log": "966293b8f766c9d0e7bce1c265dbca31f2e83e58a08a41820372f73a65fda6bb",
}
PNPM = CONTROL / "pnpm-runtime" / "node_modules" / "pnpm" / "bin" / "pnpm.cjs"
PNPM_SHA256 = "b276da51dc8ca5b0d3ee3371695b50fc8b3244b281b091c63a3f082a88dadeb9"
PRETTIER = DEPENDENCY_RUNTIME / "prettier" / "bin" / "prettier.cjs"
PRETTIER_SHA256 = "ac5523cd57e7e9d8eac71caef7e022a8a8489bcdc19ca8a778b7e728ec103b93"
OFFLINE_PROFILE_SHA256 = "5c358b8d847211333e7ba22df82d84f796b5f30a41a2682209a949d783adbd08"


class T10Error(RuntimeError):
    pass


def digest(value: bytes | Path | Any) -> str:
    if isinstance(value, Path):
        raw = value.read_bytes()
    elif isinstance(value, bytes):
        raw = value
    else:
        raw = canonical(value)
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def load_base() -> Any:
    if digest(BASE_RUNNER) != BASE_RUNNER_SHA256:
        raise T10Error("BASE_RUNNER_DRIFT")
    spec = importlib.util.spec_from_file_location("ev1_t06_frozen_base", BASE_RUNNER)
    if spec is None or spec.loader is None:
        raise T10Error("BASE_RUNNER_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base()
atomic_bytes = BASE.atomic_bytes
atomic_record = BASE.atomic_record
run = BASE.run
tree_hashes = BASE.tree_hashes
safe_file = BASE.safe_file


def load_receipt(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if not raw.endswith(b"\n"):
        raise T10Error(f"RECEIPT_NOT_CANONICAL:{path.name}")
    value = json.loads(raw[:-1])
    if canonical(value) + b"\n" != raw:
        raise T10Error(f"RECEIPT_NOT_CANONICAL:{path.name}")
    body = {key: value[key] for key in value if key != "receipt_sha256"}
    if value.get("receipt_sha256") != digest(body):
        raise T10Error(f"RECEIPT_HASH_MISMATCH:{path.name}")
    return value


def git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return run(["git", *arguments], cwd=ORIGINAL, timeout=180)


def minimal_env(tmpdir: Path, path: str) -> dict[str, str]:
    fake_home = CONTROL / "fake-home"
    fake_home.mkdir(exist_ok=True)
    for target in (
        tmpdir,
        CONTROL / "xdg-cache",
        CONTROL / "xdg-config",
        CONTROL / "xdg-state",
        CONTROL / "npm-cache",
    ):
        target.mkdir(parents=True, exist_ok=True)
    return {
        "CI": "1",
        "HOME": str(fake_home),
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
        "npm_config_update_notifier": "false",
    }


def record_command(name: str, completed: subprocess.CompletedProcess[bytes]) -> dict[str, Any]:
    raw = completed.stdout + completed.stderr
    atomic_bytes(CONTROL / f"{name}.log", raw)
    return {
        "exit": completed.returncode,
        "log_bytes": len(raw),
        "log_sha256": digest(raw),
        "network_mode": "DENIED_SEATBELT",
    }


def verify_product(r3: Any) -> tuple[Path, Path, Path]:
    try:
        return BASE.verify_product(r3)
    except RuntimeError as exc:
        raise T10Error(f"PRODUCT_RUNTIME_INVALID:{exc}") from exc


def verify_work_state() -> dict[str, Any]:
    if digest(PREPARATION_RECEIPT) != PREPARATION_FILE_SHA256:
        raise T10Error("PREPARATION_FILE_DRIFT")
    preparation = load_receipt(PREPARATION_RECEIPT)
    if preparation.get("receipt_sha256") != PREPARATION_INTERNAL_SHA256:
        raise T10Error("PREPARATION_INTERNAL_DRIFT")
    if digest(WORK_RECEIPT) != WORK_FILE_SHA256:
        raise T10Error("WORK_RECEIPT_FILE_DRIFT")
    work = load_receipt(WORK_RECEIPT)
    if work.get("receipt_sha256") != WORK_INTERNAL_SHA256:
        raise T10Error("WORK_RECEIPT_INTERNAL_DRIFT")
    if work.get("status") != "EV1_T10_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED":
        raise T10Error("WORK_RECEIPT_STATUS_INVALID")
    if digest(AUTHORIZATION) != AUTHORIZATION_SHA256:
        raise T10Error("AUTHORIZATION_DRIFT")
    head = git("rev-parse", "HEAD")
    status = git("status", "--porcelain=v1", "-uall")
    if head.returncode != 0 or head.stdout.decode().strip() != TASK_COMMIT:
        raise T10Error("TASK_COMMIT_DRIFT")
    if status.returncode != 0 or status.stdout.decode().splitlines() != EXPECTED_STATUS:
        raise T10Error("TASK_STATUS_DRIFT")
    hashes = {relative: digest(safe_file(ORIGINAL, relative)) for relative in DECLARED}
    if hashes != EXPECTED_HASHES or work.get("declared_file_hashes") != EXPECTED_HASHES:
        raise T10Error("TASK_FILE_HASH_DRIFT")
    for name, expected in EXPECTED_LOGS.items():
        if digest(CONTROL / name) != expected:
            raise T10Error(f"PRE_LOSS_LOG_DRIFT:{name}")
    if work.get("human_edit_required") is not False:
        raise T10Error("HUMAN_EDIT_REQUIREMENT_DRIFT")
    if digest(PNPM) != PNPM_SHA256 or digest(PRETTIER) != PRETTIER_SHA256:
        raise T10Error("PINNED_TOOL_DRIFT")
    if digest(CONTROL / "offline.sb") != OFFLINE_PROFILE_SHA256:
        raise T10Error("OFFLINE_PROFILE_DRIFT")
    return {
        "file_hashes": hashes,
        "git_status": EXPECTED_STATUS,
        "task_commit": TASK_COMMIT,
        "human_edit_required": False,
        "independent_human_edit": "NOT_APPLICABLE",
    }


def make_request(r3: Any, file_hashes: dict[str, str]) -> dict[str, Any]:
    p7 = r3.p7
    paths = sorted(file_hashes)
    manifest = {
        "version": p7.VERSION,
        "manifest_id": "manifest-ev1-t10-r1",
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
        "COMMITTED_RELEASE_NOTES_VALIDATOR_PRESENT",
        "UNCOMMITTED_RELEASE_DOCUMENTATION_PRESENT",
        "UNTRACKED_RELEASE_NOTES_TEMPLATE_PRESENT",
        "PRIVATE_PACKAGE_SAFEGUARD_PRESENT",
        "OFFLINE_FORMAT_AND_RELEASE_NOTES_ACCEPTANCE_GREEN",
        "HUMAN_EDIT_NOT_REQUIRED_BY_FROZEN_TASK",
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
        "receipt_id": "trajectory-ev1-t10-r1",
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
        "candidate_id": "candidate-ev1-t10-r1",
        "task_id": TASK_ID,
        "provenance": {"source": "operator-declared-hash-bound-representation"},
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
            "test_id": "test-ev1-t10-release-notes-r1",
            "path": ".github/release-notes-template.md",
            "feature_hash": file_hashes[".github/release-notes-template.md"],
            "passed": True,
        },
    }
    decision = p7.select_candidate([candidate], context)
    if decision.get("decision") != "PROMOTE":
        raise T10Error("PREPARED_CANDIDATE_NOT_ADMITTED")
    warrant = p7.make_warrant("warrant-ev1-t10-r1", TASK_ID, candidate["candidate_id"], decision)
    loss = {
        "version": p7.VERSION,
        "receipt_id": "loss-ev1-t10-r1",
        "task_id": TASK_ID,
        "manifest_hash": p7.sha256_hex(manifest),
        "lost_paths": paths,
        "absence_hash": p7.sha256_hex({"lost_paths": paths, "observed": "absent"}),
    }
    request = {
        "version": r3.surface.REQUEST_VERSION,
        "request_id": "request-ev1-t10-r1",
        "context": context,
        "loss_receipt": loss,
        "candidates": [candidate],
        "warrant": warrant,
    }
    r3.surface.canonical_json(request)
    return request


def export_baseline_snapshot() -> dict[str, str]:
    if BASELINE_SNAPSHOT.exists() or BASELINE_SNAPSHOT.is_symlink():
        raise T10Error("BASELINE_SNAPSHOT_PREEXISTS")
    listed = git("ls-tree", "-r", "-z", BASELINE_COMMIT)
    if listed.returncode != 0:
        raise T10Error("BASELINE_TREE_LIST_FAILED")
    count = 0
    for record in listed.stdout.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split()
        relative = raw_path.decode("utf-8")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or "\x00" in relative:
            raise T10Error("BASELINE_PATH_UNSAFE")
        if object_type != "blob" or mode == "120000":
            raise T10Error("BASELINE_ENTRY_NOT_REGULAR_FILE")
        blob = git("cat-file", "blob", object_id)
        if blob.returncode != 0:
            raise T10Error("BASELINE_BLOB_READ_FAILED")
        target = BASELINE_SNAPSHOT.joinpath(*pure.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, blob.stdout, 0o600)
        count += 1
    if count != BASELINE_FILE_COUNT:
        raise T10Error("BASELINE_FILE_COUNT_MISMATCH")
    return tree_hashes(BASELINE_SNAPSHOT)


def verify_existing_baseline_snapshot() -> dict[str, str]:
    if BASELINE_SNAPSHOT.is_symlink() or not BASELINE_SNAPSHOT.is_dir():
        raise T10Error("BASELINE_SNAPSHOT_INVALID")
    actual = tree_hashes(BASELINE_SNAPSHOT)
    listed = git("ls-tree", "-r", "-z", BASELINE_COMMIT)
    if listed.returncode != 0:
        raise T10Error("BASELINE_TREE_LIST_FAILED")
    expected: dict[str, str] = {}
    for record in listed.stdout.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split()
        relative = raw_path.decode("utf-8")
        if object_type != "blob" or mode == "120000":
            raise T10Error("BASELINE_ENTRY_NOT_REGULAR_FILE")
        blob = git("cat-file", "blob", object_id)
        if blob.returncode != 0:
            raise T10Error("BASELINE_BLOB_READ_FAILED")
        expected[relative] = digest(blob.stdout)
    if len(expected) != BASELINE_FILE_COUNT or actual != expected:
        raise T10Error("PRESERVED_BASELINE_SNAPSHOT_DRIFT")
    return actual


def restore_baseline(destination: Path, omit: set[str]) -> int:
    if destination.exists() or destination.is_symlink():
        raise T10Error("SUCCESSOR_BASELINE_DESTINATION_PREEXISTS")
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
    candidate = REPRESENTATIONS / "candidate-ev1-t10-r1"
    for relative in DECLARED:
        source = safe_file(candidate, relative)
        target = destination.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, source.read_bytes(), 0o600)


def clone_dependencies(destination: Path) -> dict[str, Any]:
    if destination.exists() or destination.is_symlink():
        raise T10Error("DEPENDENCY_DESTINATION_PREEXISTS")
    source_shape = dependency_shape(DEPENDENCY_RUNTIME)
    completed = run(["cp", "-cR", str(DEPENDENCY_RUNTIME), str(destination)], cwd=ROOT, timeout=600)
    if completed.returncode != 0:
        raise T10Error("DEPENDENCY_CLONE_FAILED")
    destination_shape = dependency_shape(destination)
    if destination_shape != source_shape:
        raise T10Error("DEPENDENCY_CLONE_SHAPE_MISMATCH")
    return source_shape


def dependency_shape(root: Path) -> dict[str, Any]:
    if root.is_symlink() or not root.is_dir():
        raise T10Error("DEPENDENCY_ROOT_INVALID")
    resolved_root = root.resolve(strict=True)
    files = [path for path in root.rglob("*") if path.is_file() and not path.is_symlink()]
    directories = [path for path in root.rglob("*") if path.is_dir() and not path.is_symlink()]
    symlinks: list[dict[str, str]] = []
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_symlink()):
        raw_target = os.readlink(path)
        if Path(raw_target).is_absolute():
            raise T10Error("DEPENDENCY_ABSOLUTE_SYMLINK")
        try:
            resolved_target = path.resolve(strict=True)
        except OSError as exc:
            raise T10Error("DEPENDENCY_BROKEN_SYMLINK") from exc
        if resolved_target != resolved_root and resolved_root not in resolved_target.parents:
            raise T10Error("DEPENDENCY_SYMLINK_ESCAPE")
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
        raise T10Error("DEPENDENCY_SPECIAL_FILE")
    prettier = root / "prettier" / "bin" / "prettier.cjs"
    if not prettier.is_file() or digest(prettier) != PRETTIER_SHA256:
        raise T10Error("DEPENDENCY_PRETTIER_DRIFT")
    return {
        "file_count": len(files),
        "directory_count": len(directories),
        "file_bytes": sum(path.stat().st_size for path in files),
        "symlinks": symlinks,
        "prettier_sha256": digest(prettier),
    }


def run_acceptance(workspace: Path, prefix: str, tmpdir: Path) -> dict[str, Any]:
    environment = minimal_env(
        tmpdir,
        f"{workspace / 'node_modules' / '.bin'}:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
    )
    commands = (
        (
            f"{prefix}-prettier",
            [
                "/usr/local/bin/node",
                str(PNPM),
                "exec",
                "prettier",
                "--check",
                "docs/RELEASE.md",
                ".github/release-notes-template.md",
            ],
            300,
        ),
        (
            f"{prefix}-release-notes",
            [
                "/usr/local/bin/node",
                "scripts/validate-release-notes.mjs",
                ".github/release-notes-template.md",
            ],
            300,
        ),
    )
    results: dict[str, Any] = {}
    for name, command, timeout in commands:
        completed = run(
            ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command],
            cwd=workspace,
            env=environment,
            timeout=timeout,
        )
        results[name] = record_command(name, completed)
        if completed.returncode != 0:
            raise T10Error(f"SUCCESSOR_ACCEPTANCE_FAILED:{name}")
    validator_log = CONTROL / f"{prefix}-release-notes.log"
    validator = json.loads(validator_log.read_text())
    if validator != {
        "file": ".github/release-notes-template.md",
        "required_sections": 6,
        "status": "GREEN",
    }:
        raise T10Error("RELEASE_NOTES_ACCEPTANCE_OUTPUT_DRIFT")
    return results


def capture() -> int:
    if any(path.exists() for path in (CAPTURE_RECEIPT, TASK_RECEIPT, FAILURE_RECEIPT)):
        raise T10Error("CAPTURE_ALREADY_STARTED")
    if any(path.exists() for path in (RECOVERY, EXECUTION_CAMPAIGN, PREFLIGHT_CAMPAIGN)):
        raise T10Error("PREEXISTING_CAMPAIGN_ROOT")
    state = verify_work_state()
    r3 = BASE.load_r3()
    toolchain, _venv, entrypoint = verify_product(r3)
    baseline_hashes = (
        verify_existing_baseline_snapshot()
        if BASELINE_SNAPSHOT.exists()
        else export_baseline_snapshot()
    )
    dependency = dependency_shape(DEPENDENCY_RUNTIME)
    for path in (REPRESENTATIONS, CUSTODY, OUTPUT, TEMP):
        path.mkdir(parents=True, mode=0o700)
    candidate = REPRESENTATIONS / "candidate-ev1-t10-r1"
    for relative in DECLARED:
        target = candidate.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, safe_file(ORIGINAL, relative).read_bytes(), 0o600)
    request = make_request(r3, state["file_hashes"])
    atomic_bytes(REQUEST, r3.surface.canonical_json(request), 0o600)
    outside = CONTROL / "outside-kill-canary.txt"
    atomic_bytes(outside, b"EV1-T10 outside kill canary\n")
    body = {
        "version": "ev1-t10-capture-receipt-v1",
        "status": "EV1_T10_CAPTURE_GREEN_EXECUTION_NOT_STARTED",
        "task_id": TASK_ID,
        "capture_declaration": CAPTURE_DECLARATION,
        "capture_declaration_utc": CAPTURE_DECLARATION_UTC,
        "authorization_file_sha256": AUTHORIZATION_SHA256,
        "human_edit_required": False,
        "independent_human_edit": "NOT_APPLICABLE",
        "independent_human_edit_claim": "NOT_REQUIRED_BY_FROZEN_TASK",
        "backlog_sha256": BACKLOG_SHA256,
        "global_preflight_packet_sha256": GLOBAL_PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "source_commit": SOURCE_COMMIT,
        "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
        "baseline_commit": BASELINE_COMMIT,
        "baseline_snapshot_hashes": baseline_hashes,
        "baseline_snapshot_file_count": len(baseline_hashes),
        "baseline_attribution": "ORDINARY_GIT_EQUIVALENT_NOT_RECOVERED_TASK_WORK",
        "work_receipt_file_sha256": WORK_FILE_SHA256,
        "work_receipt_internal_sha256": WORK_INTERNAL_SHA256,
        "declared_state": state,
        "request_sha256": digest(REQUEST),
        "representation_hashes": tree_hashes(REPRESENTATIONS),
        "representation_aggregate_bytes": sum(
            path.stat().st_size for path in REPRESENTATIONS.rglob("*") if path.is_file()
        ),
        "dependency_runtime": dependency,
        "offline_profile_sha256": OFFLINE_PROFILE_SHA256,
        "product_entrypoint_sha256": digest(entrypoint),
        "product_runtime": {
            "toolchain_sha256": digest(toolchain / "bin" / "python3.12"),
            "entrypoint_sha256": digest(entrypoint),
            "source": "hash-bound closed T01 project-local product runtime",
        },
        "kill_target": ".ev1-runtime/EV1-T10/workspace",
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
    if any(path.exists() for path in (PREFLIGHT_RECEIPT, TASK_RECEIPT, FAILURE_RECEIPT)):
        raise T10Error("PREFLIGHT_ALREADY_STARTED")
    captured = load_receipt(CAPTURE_RECEIPT)
    if captured.get("status") != "EV1_T10_CAPTURE_GREEN_EXECUTION_NOT_STARTED":
        raise T10Error("CAPTURE_STATUS_INVALID")
    if verify_work_state() != captured.get("declared_state"):
        raise T10Error("POST_CAPTURE_STATE_DRIFT")
    if digest(REQUEST) != captured.get("request_sha256"):
        raise T10Error("CAPTURE_REQUEST_DRIFT")
    if tree_hashes(REPRESENTATIONS) != captured.get("representation_hashes"):
        raise T10Error("CAPTURE_REPRESENTATION_DRIFT")
    if tree_hashes(BASELINE_SNAPSHOT) != captured.get("baseline_snapshot_hashes"):
        raise T10Error("CAPTURE_BASELINE_DRIFT")
    if PREFLIGHT_CAMPAIGN.exists() or EXECUTION_CAMPAIGN.exists():
        raise T10Error("TEMP_ROOT_PREEXISTS")

    r3 = BASE.load_r3()
    toolchain, venv, entrypoint = verify_product(r3)
    product_canary = PREFLIGHT_CAMPAIGN / "product-canary"
    product_canary.mkdir(parents=True, mode=0o700)
    r3.make_fixture(product_canary, "ev1-t10-predelete")
    representation_before = r3.tree(product_canary / "representations")
    public_root = CONTROL / "public"
    public_root.mkdir(exist_ok=True)
    product_tmp = product_canary / "tmp"
    product_tmp.mkdir(mode=0o700, exist_ok=True)
    arguments = [
        "recover",
        "--request", str(product_canary / "request.json"),
        "--sandbox-root", str(product_canary),
        "--workspace", str(product_canary / "workspace"),
        "--representation-root", str(product_canary / "representations"),
        "--custody-root", str(product_canary / "custody"),
        "--output-root", str(product_canary / "output"),
    ]
    product = run(
        r3.seatbelt_command(entrypoint, toolchain, venv, public_root, product_canary, arguments),
        cwd=ROOT,
        env=minimal_env(product_tmp, "/usr/bin:/bin"),
        timeout=120,
    )
    product_record = record_command("t10-product-preflight", product)
    if product.returncode != 0:
        raise T10Error("PRODUCT_PREFLIGHT_FAILED")
    summary = json.loads(product.stdout)
    if summary.get("verdict") != "PROMOTE" or summary.get("fresh_context_continued") is not True:
        raise T10Error("PRODUCT_PREFLIGHT_NOT_PROMOTED")
    if r3.tree(product_canary / "representations") != representation_before:
        raise T10Error("PRODUCT_PREFLIGHT_REPRESENTATION_MUTATED")

    dependency_workspace = PREFLIGHT_CAMPAIGN / "dependency-canary" / "workspace"
    baseline_files = restore_baseline(dependency_workspace, set(DECLARED))
    if baseline_files != 409 or (dependency_workspace / ".git").exists():
        raise T10Error("DEPENDENCY_CANARY_BASELINE_INVALID")
    copy_representations_into(dependency_workspace)
    dependency = clone_dependencies(dependency_workspace / "node_modules")
    dependency_tmp = PREFLIGHT_CAMPAIGN / "dependency-canary" / "tmp"
    dependency_tmp.mkdir(mode=0o700)
    acceptance = run_acceptance(dependency_workspace, "t10-dependency-preflight", dependency_tmp)
    hashes = {relative: digest(safe_file(dependency_workspace, relative)) for relative in DECLARED}
    if hashes != EXPECTED_HASHES:
        raise T10Error("DEPENDENCY_CANARY_WORK_UNITS_MISMATCH")

    shutil.rmtree(PREFLIGHT_CAMPAIGN)
    if PREFLIGHT_CAMPAIGN.exists():
        raise T10Error("PREFLIGHT_TEARDOWN_FAILED")
    body = {
        "version": "ev1-t10-execution-preflight-receipt-v1",
        "status": "EV1_T10_EXECUTION_PREFLIGHT_GREEN_DELETION_NOT_STARTED",
        "task_id": TASK_ID,
        "capture_file_sha256": digest(CAPTURE_RECEIPT),
        "capture_receipt_sha256": captured["receipt_sha256"],
        "runner_sha256": digest(Path(__file__).resolve()),
        "base_runner_sha256": BASE_RUNNER_SHA256,
        "execution_root": "/private/tmp/ck-ev1-t10-r1",
        "successor_dependency_topology": "SUCCESSOR_ROOT/node_modules",
        "baseline_attribution": captured["baseline_attribution"],
        "human_edit_required": False,
        "independent_human_edit": "NOT_APPLICABLE",
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
        raise T10Error("KILL_TARGET_MISMATCH")
    campaign_resolved = CAMPAIGN.resolve(strict=True)
    original_resolved = ORIGINAL.resolve(strict=True)
    if original_resolved != expected.resolve(strict=True) or campaign_resolved not in original_resolved.parents:
        raise T10Error("KILL_TARGET_ESCAPE")
    before = time.monotonic_ns()
    shutil.rmtree(ORIGINAL)
    elapsed = time.monotonic_ns() - before
    if ORIGINAL.exists() or not (CONTROL / "outside-kill-canary.txt").is_file():
        raise T10Error("KILL_OR_CANARY_VERIFICATION_FAILED")
    return {
        "elapsed_monotonic_ns": elapsed,
        "original_absent": True,
        "outside_canary_survived": True,
    }


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
                "version": "ev1-t10-failure-receipt-v1",
                "status": "EV1_T10_BLOCKED",
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
        raise T10Error("EXECUTION_ALREADY_TERMINAL")
    captured = load_receipt(CAPTURE_RECEIPT)
    preflighted = load_receipt(PREFLIGHT_RECEIPT)
    if captured.get("status") != "EV1_T10_CAPTURE_GREEN_EXECUTION_NOT_STARTED":
        raise T10Error("CAPTURE_STATUS_INVALID")
    if preflighted.get("status") != "EV1_T10_EXECUTION_PREFLIGHT_GREEN_DELETION_NOT_STARTED":
        raise T10Error("EXECUTION_PREFLIGHT_STATUS_INVALID")
    if preflighted.get("capture_file_sha256") != digest(CAPTURE_RECEIPT):
        raise T10Error("PREFLIGHT_CAPTURE_DRIFT")
    if preflighted.get("runner_sha256") != digest(Path(__file__).resolve()):
        raise T10Error("RUNNER_DRIFT")
    if verify_work_state() != captured.get("declared_state"):
        raise T10Error("PRE_EXECUTION_STATE_DRIFT")
    if digest(REQUEST) != captured.get("request_sha256"):
        raise T10Error("REQUEST_DRIFT")
    if tree_hashes(REPRESENTATIONS) != captured.get("representation_hashes"):
        raise T10Error("REPRESENTATION_DRIFT")
    if tree_hashes(BASELINE_SNAPSHOT) != captured.get("baseline_snapshot_hashes"):
        raise T10Error("BASELINE_SNAPSHOT_DRIFT")
    if EXECUTION_CAMPAIGN.exists():
        raise T10Error("EXECUTION_ROOT_PREEXISTS")

    r3 = BASE.load_r3()
    toolchain, venv, entrypoint = verify_product(r3)
    if digest(entrypoint) != captured.get("product_entrypoint_sha256"):
        raise T10Error("PRODUCT_ENTRYPOINT_DRIFT")
    for path in (EXECUTION_REPRESENTATIONS, EXECUTION_CUSTODY, EXECUTION_OUTPUT, EXECUTION_TEMP):
        path.mkdir(parents=True, mode=0o700)
    shutil.copytree(REPRESENTATIONS, EXECUTION_REPRESENTATIONS, dirs_exist_ok=True, copy_function=shutil.copy2)
    atomic_bytes(EXECUTION_REQUEST, REQUEST.read_bytes())
    if tree_hashes(EXECUTION_REPRESENTATIONS) != captured["representation_hashes"]:
        raise T10Error("EXECUTION_REPRESENTATION_COPY_MISMATCH")
    if digest(EXECUTION_REQUEST) != captured["request_sha256"]:
        raise T10Error("EXECUTION_REQUEST_COPY_MISMATCH")

    dependency = dependency_shape(DEPENDENCY_RUNTIME)
    if dependency != captured.get("dependency_runtime"):
        raise T10Error("DEPENDENCY_RUNTIME_DRIFT")
    kill = guarded_destroy()
    baseline_files = restore_baseline(EXECUTION_SUCCESSOR, set(DECLARED))
    if baseline_files != 409 or (EXECUTION_SUCCESSOR / ".git").exists():
        raise T10Error("SUCCESSOR_BASELINE_INVALID")
    successor_dependency = clone_dependencies(EXECUTION_SUCCESSOR / "node_modules")
    if successor_dependency != dependency:
        raise T10Error("SUCCESSOR_DEPENDENCY_DRIFT")

    public_root = CONTROL / "public"
    public_root.mkdir(exist_ok=True)
    arguments = [
        "recover",
        "--request", str(EXECUTION_REQUEST),
        "--sandbox-root", str(EXECUTION_RECOVERY),
        "--workspace", str(EXECUTION_SUCCESSOR),
        "--representation-root", str(EXECUTION_REPRESENTATIONS),
        "--custody-root", str(EXECUTION_CUSTODY),
        "--output-root", str(EXECUTION_OUTPUT),
    ]
    invocation_start = time.monotonic_ns()
    recovered = run(
        r3.seatbelt_command(entrypoint, toolchain, venv, public_root, EXECUTION_RECOVERY, arguments),
        cwd=ROOT,
        env=minimal_env(EXECUTION_TEMP, "/usr/bin:/bin"),
        timeout=120,
    )
    productive_ns = time.monotonic_ns() - invocation_start
    recovery_record = record_command("t10-recovery", recovered)
    if recovered.returncode != 0:
        raise T10Error(f"PRODUCT_RECOVERY_FAILED:{recovered.returncode}")
    summary = json.loads(recovered.stdout)
    if summary.get("verdict") != "PROMOTE" or summary.get("fresh_context_continued") is not True:
        raise T10Error("PRODUCT_RECOVERY_NOT_PROMOTED")
    if tree_hashes(EXECUTION_REPRESENTATIONS) != captured["representation_hashes"]:
        raise T10Error("EXECUTION_REPRESENTATION_MUTATED")
    if tree_hashes(REPRESENTATIONS) != captured["representation_hashes"]:
        raise T10Error("AUTHORITATIVE_REPRESENTATION_MUTATED")
    if tree_hashes(BASELINE_SNAPSHOT) != captured["baseline_snapshot_hashes"]:
        raise T10Error("AUTHORITATIVE_BASELINE_MUTATED")

    acceptance = run_acceptance(EXECUTION_SUCCESSOR, "t10-successor", EXECUTION_TEMP)
    acceptance_ns = time.monotonic_ns() - invocation_start
    restored = {relative: digest(safe_file(EXECUTION_SUCCESSOR, relative)) for relative in DECLARED}
    if restored != EXPECTED_HASHES:
        raise T10Error("SUCCESSOR_WORK_UNITS_MISMATCH")
    process_scan = run(["ps", "-axo", "pid=,command="], cwd=ROOT, timeout=30)
    if process_scan.returncode != 0:
        raise T10Error("PROCESS_RESIDUE_SCAN_FAILED")
    markers = (str(ORIGINAL), str(EXECUTION_RECOVERY))
    residue = []
    for raw_line in process_scan.stdout.splitlines():
        line = raw_line.decode("utf-8", "replace").strip()
        fields = line.split(maxsplit=1)
        if len(fields) == 2 and fields[0].isdigit() and int(fields[0]) != os.getpid():
            if any(marker in fields[1] for marker in markers):
                residue.append(line)
    if residue:
        raise T10Error("TASK_PROCESS_RESIDUE")

    snapshot = CONTROL / "POST_RECOVERY_SNAPSHOT"
    if snapshot.exists():
        raise T10Error("POST_RECOVERY_SNAPSHOT_PREEXISTS")
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
        "global_preflight_packet_sha256": GLOBAL_PREFLIGHT_PACKET_SHA256,
        "product_candidate": PRODUCT_CANDIDATE,
        "source_commit": SOURCE_COMMIT,
        "project_class": "LARGE_MONOREPO_RELEASE_OPERATIONS",
        "capture_file_sha256": digest(CAPTURE_RECEIPT),
        "capture_receipt_sha256": captured["receipt_sha256"],
        "execution_preflight_file_sha256": digest(PREFLIGHT_RECEIPT),
        "execution_preflight_receipt_sha256": preflighted["receipt_sha256"],
        "capture_declaration": CAPTURE_DECLARATION,
        "capture_declaration_utc": CAPTURE_DECLARATION_UTC,
        "state_mix": {
            "committed": True,
            "uncommitted": True,
            "untracked": True,
            "human_edit_required": False,
            "independent_human_edit": "NOT_APPLICABLE",
        },
        "independent_human_edit_claim": "NOT_REQUIRED_BY_FROZEN_TASK",
        "declared_work_units_before_loss": 3,
        "usable_work_units_after_continuation": 3,
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
        "acceptance_command": "pnpm exec prettier --check docs/RELEASE.md .github/release-notes-template.md && node scripts/validate-release-notes.mjs .github/release-notes-template.md",
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
        "operator_observation_scoring": "PENDING_HUMAN_CONFIRMATION",
        "campaign_teardown_pending": True,
    }
    receipt_hash, file_hash = atomic_record(TASK_RECEIPT, body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("capture", "preflight", "execute"))
    phase = parser.parse_args().phase
    try:
        if phase == "capture":
            return capture()
        if phase == "preflight":
            return preflight()
        return execute()
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired, T10Error) as exc:
        reason = str(exc) or exc.__class__.__name__
        if phase == "execute":
            try:
                preserve_failure(reason)
            except OSError:
                pass
        print(canonical({"status": "EV1_T10_BLOCKED", "phase": phase, "reason": reason}).decode())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
