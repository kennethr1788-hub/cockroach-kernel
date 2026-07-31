#!/usr/bin/env python3
"""Capture, preflight, and execute the frozen EV1-T12 recovery task."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import time
from typing import Any

import prepare_ev1_t11 as PREP
import run_ev1_t11 as U


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "EV1-T12"
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
INDEPENDENT_GATE = CONTROL / "INDEPENDENT_EXECUTION_GATE.json"
TASK_RECEIPT = CONTROL / "TASK_EXECUTION_RECEIPT.json"
FAILURE_RECEIPT = CONTROL / "TASK_FAILURE_RECEIPT.json"
FAILURE_SNAPSHOT = CONTROL / "FAILURE_SNAPSHOT"
PREFLIGHT_ROOT = Path("/private/tmp/ck-ev1-t12-preflight-r1")
EXECUTION_ROOT = Path("/private/tmp/ck-ev1-t12-r1")
EXECUTION_RECOVERY = EXECUTION_ROOT / "recovery"
EXECUTION_SUCCESSOR = EXECUTION_RECOVERY / "workspace"
EXECUTION_REPRESENTATIONS = EXECUTION_RECOVERY / "representations"
EXECUTION_CUSTODY = EXECUTION_RECOVERY / "custody"
EXECUTION_OUTPUT = EXECUTION_RECOVERY / "output"
EXECUTION_TEMP = EXECUTION_RECOVERY / "tmp"
EXECUTION_REQUEST = EXECUTION_RECOVERY / "request.json"
SOURCE_COMMIT = "ee6862f7d65d24d4de11eda8306d29356873b529"
SOURCE_MANIFEST_SHA256 = "6f81e7e81ad100b53163a13b11c5e7abcd437fe658f817e34905c02cbe0e7182"
BASELINE_COMMIT = "98bd20e042851fd8368ddad7ed1ab37d24351152"
BASELINE_FILE_COUNT = 410
BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
GLOBAL_PREFLIGHT_PACKET_SHA256 = "a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
AUTHORIZATION = ROOT / "EXTERNAL_VALIDITY_EV1_T12_CAPTURE_AUTHORIZATION_R1.md"
AUTHORIZATION_SHA256 = "86d61453a73c736310d55e2be3b7609d01288088f8d517ad4464b00d7d912817"
PREPARATION_FILE_SHA256 = "494619b9ed72c9e2f96330a7fd7248f821b8828d471a4e155b4229731d63950b"
PREPARATION_INTERNAL_SHA256 = "d8dc81d40f634624dbf454b4232c9462f29ba139a7c0e562f9bd17ee50be7fb1"
WORK_FILE_SHA256 = "c20b9cfffa6a40cfb682a351184e13cb41bf404cc5f09ac630e6cde1db749df4"
WORK_INTERNAL_SHA256 = "69cc45764a10433bd9070b982c2378445fd36e095fba511e925cd1026d393359"
TASK_COMMIT = "62b3f01f00544ba618a04ea8935908de8b038bb4"
CAPTURE_DECLARATION_UTC = "2026-07-31T00:00:10Z"
DECLARED = (
    "docs/RELEASE.md",
    "scripts/build-release-manifest.mjs",
    "scripts/build-release-manifest.test.ts",
)
EXPECTED_STATUS = [" M docs/RELEASE.md", "?? scripts/build-release-manifest.test.ts"]
EXPECTED_HASHES = {
    "docs/RELEASE.md": "8ea051ff477c04d7becafb53fa970f9973875d67211ea2ae7c390ba4050d1fee",
    "scripts/build-release-manifest.mjs": "1aa1561692cba73683d00cb0991971e04a6ae9f70101c0b5093ee47eb2d9c40a",
    "scripts/build-release-manifest.test.ts": "01b0d4eaf0e0794e4b5d5224932a75186613e6f36f667681950255e9f9e69941",
}
PNPM = CONTROL / "pnpm-runtime" / "node_modules" / "pnpm" / "bin" / "pnpm.cjs"
PNPM_SHA256 = "b276da51dc8ca5b0d3ee3371695b50fc8b3244b281b091c63a3f082a88dadeb9"
DEPENDENCY_MANIFEST_SHA256 = "bda7fc8f96d452960e7174cc6b84f05708f763ebf2e10dbdd40a1eca87b06dbe"
DECLARED_LINKS_SHA256 = "aa1ad61037ef49847a9de65f3c92ce2d91f9fe989b202f25f88d720e0e6490b8"
DECLARED_LINK_COUNT = 36
OFFLINE_PROFILE_SHA256 = "5c358b8d847211333e7ba22df82d84f796b5f30a41a2682209a949d783adbd08"


class T12Error(RuntimeError):
    pass


canonical = U.canonical
digest = U.digest
atomic_bytes = U.atomic_bytes
atomic_record = U.atomic_record
run = U.run
tree_hashes = U.tree_hashes
safe_file = U.safe_file


def load_receipt(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if canonical(value) + b"\n" != raw:
        raise T12Error(f"RECEIPT_NOT_CANONICAL:{path.name}")
    body = {key: value[key] for key in value if key != "receipt_sha256"}
    if value.get("receipt_sha256") != digest(body):
        raise T12Error(f"RECEIPT_HASH_MISMATCH:{path.name}")
    return value


def git(*arguments: str):
    return run(["git", *arguments], cwd=ORIGINAL, timeout=180)


def minimal_env(tmpdir: Path, path_value: str) -> dict[str, str]:
    fake_home = CONTROL / "fake-home"
    for target in (fake_home, tmpdir, CONTROL / "xdg-cache", CONTROL / "xdg-config", CONTROL / "xdg-state"):
        target.mkdir(parents=True, exist_ok=True)
    return {
        "CI": "1",
        "HOME": str(fake_home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        "PATH": path_value,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "TMPDIR": str(tmpdir),
        "XDG_CACHE_HOME": str(CONTROL / "xdg-cache"),
        "XDG_CONFIG_HOME": str(CONTROL / "xdg-config"),
        "XDG_STATE_HOME": str(CONTROL / "xdg-state"),
    }


def record_command(name: str, completed: subprocess.CompletedProcess[bytes]) -> dict[str, Any]:
    raw = completed.stdout + completed.stderr
    atomic_bytes(CONTROL / f"{name}.log", raw)
    return {"exit": completed.returncode, "log_bytes": len(raw), "log_sha256": digest(raw), "network_mode": "DENIED_SEATBELT"}


def verify_runtime() -> dict[str, Any]:
    if DEPENDENCY_RUNTIME.is_symlink() or not DEPENDENCY_RUNTIME.is_dir():
        raise T12Error("DEPENDENCY_RUNTIME_UNSAFE")
    manifest = PREP.tree_manifest(DEPENDENCY_RUNTIME)
    if digest(manifest) != DEPENDENCY_MANIFEST_SHA256 or digest(PNPM) != PNPM_SHA256:
        raise T12Error("DEPENDENCY_RUNTIME_DRIFT")
    return {
        "manifest_sha256": DEPENDENCY_MANIFEST_SHA256,
        "manifest_entries": len(manifest),
        "declared_links_sha256": DECLARED_LINKS_SHA256,
        "declared_link_count": DECLARED_LINK_COUNT,
        "pnpm_sha256": PNPM_SHA256,
        "install_executed": False,
    }


def clone_dependencies(destination: Path) -> dict[str, Any]:
    if destination.exists() or destination.is_symlink():
        raise T12Error("DEPENDENCY_DESTINATION_PREEXISTS")
    expected = verify_runtime()
    copied = run(["/bin/cp", "-cR", str(DEPENDENCY_RUNTIME), str(destination)], cwd=ROOT, timeout=900)
    if copied.returncode != 0 or digest(PREP.tree_manifest(destination)) != DEPENDENCY_MANIFEST_SHA256:
        raise T12Error("DEPENDENCY_CLONE_DRIFT")
    links = PREP.declared_links(destination.parent)
    if len(links) != DECLARED_LINK_COUNT or digest(links) != DECLARED_LINKS_SHA256:
        raise T12Error("DECLARED_LINK_DRIFT")
    _count, broken, escapes = PREP.resolved_links(destination, destination.parent)
    if broken or escapes:
        raise T12Error("DEPENDENCY_LINK_ESCAPE")
    return expected


def verify_work_state() -> dict[str, Any]:
    if digest(PREPARATION_RECEIPT) != PREPARATION_FILE_SHA256 or load_receipt(PREPARATION_RECEIPT).get("receipt_sha256") != PREPARATION_INTERNAL_SHA256:
        raise T12Error("PREPARATION_DRIFT")
    work = load_receipt(WORK_RECEIPT)
    if digest(WORK_RECEIPT) != WORK_FILE_SHA256 or work.get("receipt_sha256") != WORK_INTERNAL_SHA256:
        raise T12Error("WORK_RECEIPT_DRIFT")
    if digest(AUTHORIZATION) != AUTHORIZATION_SHA256:
        raise T12Error("AUTHORIZATION_DRIFT")
    head = git("rev-parse", "HEAD")
    status = git("status", "--porcelain=v1", "-uall")
    if head.returncode != 0 or head.stdout.decode().strip() != TASK_COMMIT:
        raise T12Error("TASK_COMMIT_DRIFT")
    if status.returncode != 0 or status.stdout.decode().splitlines() != EXPECTED_STATUS:
        raise T12Error("TASK_STATUS_DRIFT")
    hashes = {relative: digest(safe_file(ORIGINAL, relative)) for relative in DECLARED}
    if hashes != EXPECTED_HASHES or work.get("declared_file_hashes") != EXPECTED_HASHES:
        raise T12Error("TASK_FILE_HASH_DRIFT")
    if digest(CONTROL / "offline.sb") != OFFLINE_PROFILE_SHA256:
        raise T12Error("OFFLINE_PROFILE_DRIFT")
    verify_runtime()
    return {"file_hashes": hashes, "git_status": EXPECTED_STATUS, "task_commit": TASK_COMMIT, "human_edit_required": False}


def make_request(r3: Any, file_hashes: dict[str, str]) -> dict[str, Any]:
    p7 = r3.p7
    paths = sorted(file_hashes)
    manifest = {"version": p7.VERSION, "manifest_id": "manifest-ev1-t12-r1", "task_id": TASK_ID, "files": [{"path": item, "content_hash": file_hashes[item], "executable": False, "is_symlink": False} for item in paths]}
    labels = ("SOURCE_AND_BASELINE_BOUND", "COMMITTED_MANIFEST_GENERATOR_PRESENT", "UNCOMMITTED_RELEASE_DOCUMENTATION_PRESENT", "UNTRACKED_SYNTHETIC_TEST_PRESENT", "FIVE_REPEAT_DETERMINISM_GREEN", "DUPLICATE_PLATFORM_REFUSAL_GREEN", "NO_EXTERNAL_RELEASE_ACTION")
    events = [{"sequence": index, "event": label, "event_hash": digest(label.encode())} for index, label in enumerate(labels)]
    previous = ""
    for event in events:
        previous = p7.sha256_hex({"previous": previous, "event": event})
    trajectory = {"version": p7.VERSION, "receipt_id": "trajectory-ev1-t12-r1", "task_id": TASK_ID, "manifest_hash": p7.sha256_hex(manifest), "events": events, "trajectory_hash": previous}
    quorum = {"decision": "PROMOTE"}
    context = {"manifest": manifest, "trajectory_receipt": trajectory, "policy_version": "ev1-frozen-r3", "quorum_decision_hash": p7.sha256_hex(quorum)}
    candidate = {"version": p7.VERSION, "candidate_id": "candidate-ev1-t12-r1", "task_id": TASK_ID, "provenance": {"source": "operator-declared-hash-bound-representation"}, "source_receipt_hash": p7.sha256_hex(trajectory), "policy_version": context["policy_version"], "policy_veto": False, "tampered": False, "quorum_decision": quorum, "prefix_length": len(events), "integrity_hash": p7.trajectory_integrity_hash(events, len(events)), "declared_paths": paths, "file_hashes": dict(sorted(file_hashes.items())), "executable_test": {"test_id": "test-ev1-t12-manifest-r1", "path": "scripts/build-release-manifest.test.ts", "feature_hash": file_hashes["scripts/build-release-manifest.test.ts"], "passed": True}}
    decision = p7.select_candidate([candidate], context)
    if decision.get("decision") != "PROMOTE":
        raise T12Error("CANDIDATE_NOT_ADMITTED")
    warrant = p7.make_warrant("warrant-ev1-t12-r1", TASK_ID, candidate["candidate_id"], decision)
    loss = {"version": p7.VERSION, "receipt_id": "loss-ev1-t12-r1", "task_id": TASK_ID, "manifest_hash": p7.sha256_hex(manifest), "lost_paths": paths, "absence_hash": p7.sha256_hex({"lost_paths": paths, "observed": "absent"})}
    request = {"version": r3.surface.REQUEST_VERSION, "request_id": "request-ev1-t12-r1", "context": context, "loss_receipt": loss, "candidates": [candidate], "warrant": warrant}
    r3.surface.canonical_json(request)
    return request


def export_baseline() -> dict[str, str]:
    if BASELINE_SNAPSHOT.exists():
        raise T12Error("BASELINE_PREEXISTS")
    listed = git("ls-tree", "-r", "-z", BASELINE_COMMIT)
    if listed.returncode != 0:
        raise T12Error("BASELINE_LIST_FAILED")
    count = 0
    for record in listed.stdout.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, object_id = metadata.decode().split()
        pure = PurePosixPath(raw_path.decode())
        if pure.is_absolute() or ".." in pure.parts or kind != "blob" or mode == "120000":
            raise T12Error("BASELINE_ENTRY_UNSAFE")
        blob = git("cat-file", "blob", object_id)
        if blob.returncode != 0:
            raise T12Error("BASELINE_BLOB_FAILED")
        target = BASELINE_SNAPSHOT.joinpath(*pure.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, blob.stdout)
        count += 1
    if count != BASELINE_FILE_COUNT:
        raise T12Error("BASELINE_COUNT_MISMATCH")
    return tree_hashes(BASELINE_SNAPSHOT)


def restore_baseline(destination: Path) -> int:
    if destination.exists():
        raise T12Error("SUCCESSOR_PREEXISTS")
    destination.mkdir(parents=True, mode=0o700)
    count = 0
    for relative in sorted(tree_hashes(BASELINE_SNAPSHOT)):
        if relative in DECLARED:
            continue
        source = safe_file(BASELINE_SNAPSHOT, relative)
        target = destination.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, source.read_bytes())
        count += 1
    return count


def copy_representations(destination: Path) -> None:
    candidate = REPRESENTATIONS / "candidate-ev1-t12-r1"
    for relative in DECLARED:
        source = safe_file(candidate, relative)
        target = destination.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, source.read_bytes())


def run_acceptance(workspace: Path, prefix: str, tmpdir: Path) -> dict[str, Any]:
    env = minimal_env(tmpdir, "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin")
    commands = (
        (f"{prefix}-prettier", ["/usr/local/bin/node", str(PNPM), "exec", "prettier", "--check", *DECLARED]),
        (f"{prefix}-tests", ["/usr/local/bin/node", str(PNPM), "vitest", "run", "scripts/build-release-manifest.test.ts"]),
    )
    results = {}
    for name, command in commands:
        completed = run(["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command], cwd=workspace, env=env, timeout=300)
        results[name] = record_command(name, completed)
        if completed.returncode != 0:
            raise T12Error(f"ACCEPTANCE_FAILED:{name}")
    return results


def capture() -> int:
    if any(path.exists() for path in (CAPTURE_RECEIPT, TASK_RECEIPT, FAILURE_RECEIPT, RECOVERY, EXECUTION_ROOT, PREFLIGHT_ROOT)):
        raise T12Error("CAPTURE_PRECONDITION_FAILED")
    state = verify_work_state()
    r3 = U.BASE.load_r3()
    toolchain, _venv, entrypoint = U.verify_product(r3)
    baseline = export_baseline()
    runtime = verify_runtime()
    for path in (REPRESENTATIONS, CUSTODY, OUTPUT, TEMP):
        path.mkdir(parents=True, mode=0o700)
    candidate = REPRESENTATIONS / "candidate-ev1-t12-r1"
    for relative in DECLARED:
        target = candidate.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, safe_file(ORIGINAL, relative).read_bytes())
    atomic_bytes(REQUEST, r3.surface.canonical_json(make_request(r3, state["file_hashes"])))
    outside = CONTROL / "outside-kill-canary.txt"
    atomic_bytes(outside, b"EV1-T12 outside kill canary\n")
    body = {"version": "ev1-t12-capture-v1", "status": "EV1_T12_CAPTURE_GREEN_EXECUTION_NOT_STARTED", "task_id": TASK_ID, "capture_declaration_utc": CAPTURE_DECLARATION_UTC, "authorization_sha256": AUTHORIZATION_SHA256, "backlog_sha256": BACKLOG_SHA256, "global_preflight_packet_sha256": GLOBAL_PREFLIGHT_PACKET_SHA256, "product_candidate": PRODUCT_CANDIDATE, "source_commit": SOURCE_COMMIT, "source_manifest_sha256": SOURCE_MANIFEST_SHA256, "baseline_commit": BASELINE_COMMIT, "baseline_snapshot_hashes": baseline, "baseline_snapshot_file_count": len(baseline), "baseline_attribution": "ORDINARY_GIT_EQUIVALENT_NOT_RECOVERED_TASK_WORK", "declared_state": state, "request_sha256": digest(REQUEST), "representation_hashes": tree_hashes(REPRESENTATIONS), "dependency_runtime": runtime, "offline_profile_sha256": OFFLINE_PROFILE_SHA256, "product_entrypoint_sha256": digest(entrypoint), "toolchain_sha256": digest(toolchain / "bin" / "python3.12"), "kill_target": ".ev1-runtime/EV1-T12/workspace", "outside_canary_sha256": digest(outside), "capture_complete": True, "deletion_started": False, "recovery_started": False}
    receipt_hash, file_hash = atomic_record(CAPTURE_RECEIPT, body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


def preflight() -> int:
    if PREFLIGHT_RECEIPT.exists() or TASK_RECEIPT.exists() or FAILURE_RECEIPT.exists():
        raise T12Error("PREFLIGHT_PRECONDITION_FAILED")
    captured = load_receipt(CAPTURE_RECEIPT)
    if verify_work_state() != captured.get("declared_state") or digest(REQUEST) != captured.get("request_sha256"):
        raise T12Error("POST_CAPTURE_DRIFT")
    if tree_hashes(REPRESENTATIONS) != captured.get("representation_hashes") or tree_hashes(BASELINE_SNAPSHOT) != captured.get("baseline_snapshot_hashes"):
        raise T12Error("CAPTURE_ARTIFACT_DRIFT")
    if PREFLIGHT_ROOT.exists() or EXECUTION_ROOT.exists():
        raise T12Error("TEMP_ROOT_PREEXISTS")
    r3 = U.BASE.load_r3()
    toolchain, venv, entrypoint = U.verify_product(r3)
    product_root = PREFLIGHT_ROOT / "product"
    product_root.mkdir(parents=True)
    r3.make_fixture(product_root, "ev1-t12-predelete")
    before = r3.tree(product_root / "representations")
    public = CONTROL / "public"
    public.mkdir(exist_ok=True)
    arguments = ["recover", "--request", str(product_root / "request.json"), "--sandbox-root", str(product_root), "--workspace", str(product_root / "workspace"), "--representation-root", str(product_root / "representations"), "--custody-root", str(product_root / "custody"), "--output-root", str(product_root / "output")]
    product = run(r3.seatbelt_command(entrypoint, toolchain, venv, public, product_root, arguments), cwd=ROOT, env=minimal_env(product_root / "tmp", "/usr/bin:/bin"), timeout=120)
    product_record = record_command("t12-product-preflight", product)
    summary = json.loads(product.stdout) if product.returncode == 0 else {}
    if summary.get("verdict") != "PROMOTE" or r3.tree(product_root / "representations") != before:
        raise T12Error("PRODUCT_CANARY_FAILED")
    workspace = PREFLIGHT_ROOT / "dependency" / "workspace"
    baseline_count = restore_baseline(workspace)
    if baseline_count != 409 or (workspace / ".git").exists():
        raise T12Error("PREFLIGHT_BASELINE_INVALID")
    copy_representations(workspace)
    runtime = clone_dependencies(workspace / "node_modules")
    acceptance = run_acceptance(workspace, "t12-dependency-preflight", PREFLIGHT_ROOT / "dependency" / "tmp")
    restored = {relative: digest(safe_file(workspace, relative)) for relative in DECLARED}
    if restored != EXPECTED_HASHES:
        raise T12Error("PREFLIGHT_RESTORED_HASH_DRIFT")
    shutil.rmtree(PREFLIGHT_ROOT)
    if PREFLIGHT_ROOT.exists():
        raise T12Error("PREFLIGHT_TEARDOWN_FAILED")
    body = {"version": "ev1-t12-preflight-v1", "status": "EV1_T12_EXECUTION_PREFLIGHT_GREEN_DELETION_NOT_STARTED", "task_id": TASK_ID, "capture_file_sha256": digest(CAPTURE_RECEIPT), "capture_receipt_sha256": captured["receipt_sha256"], "runner_sha256": digest(Path(__file__).resolve()), "execution_root": "/private/tmp/ck-ev1-t12-r1", "product_canary": {**product_record, "summary": summary, "representation_unchanged": True}, "dependency_canary": {"runtime": runtime, "acceptance": acceptance, "restored_hashes": restored}, "original_workspace_present": ORIGINAL.is_dir(), "preflight_root_absent": True, "execution_root_absent": not EXECUTION_ROOT.exists(), "deletion_started": False, "recovery_started": False}
    receipt_hash, file_hash = atomic_record(PREFLIGHT_RECEIPT, body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


def guarded_destroy() -> dict[str, Any]:
    expected = CAMPAIGN / "workspace"
    if ORIGINAL != expected or ORIGINAL.is_symlink() or not ORIGINAL.is_dir():
        raise T12Error("KILL_TARGET_MISMATCH")
    if ORIGINAL.resolve(strict=True) != expected.resolve(strict=True) or CAMPAIGN.resolve(strict=True) not in ORIGINAL.resolve(strict=True).parents:
        raise T12Error("KILL_TARGET_ESCAPE")
    started = time.monotonic_ns()
    shutil.rmtree(ORIGINAL)
    elapsed = time.monotonic_ns() - started
    if ORIGINAL.exists() or not (CONTROL / "outside-kill-canary.txt").is_file():
        raise T12Error("KILL_VERIFICATION_FAILED")
    return {"elapsed_monotonic_ns": elapsed, "original_absent": True, "outside_canary_survived": True}


def preserve_failure(reason: str) -> None:
    if not FAILURE_SNAPSHOT.exists():
        for name, source in (("output", EXECUTION_OUTPUT), ("custody", EXECUTION_CUSTODY)):
            if source.is_dir():
                shutil.copytree(source, FAILURE_SNAPSHOT / name, copy_function=shutil.copy2)
    if not FAILURE_RECEIPT.exists():
        atomic_record(FAILURE_RECEIPT, {"version": "ev1-t12-failure-v1", "status": "EV1_T12_BLOCKED", "reason": reason, "original_exists": ORIGINAL.exists(), "successor_exists": EXECUTION_SUCCESSOR.exists(), "failure_snapshot_hashes": tree_hashes(FAILURE_SNAPSHOT), "utc_recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})


def execute() -> int:
    if TASK_RECEIPT.exists() or FAILURE_RECEIPT.exists():
        raise T12Error("EXECUTION_ALREADY_TERMINAL")
    captured = load_receipt(CAPTURE_RECEIPT)
    preflighted = load_receipt(PREFLIGHT_RECEIPT)
    gate = load_receipt(INDEPENDENT_GATE)
    if gate.get("status") != "EV1_T12_INDEPENDENT_EXECUTION_GATE_GREEN" or gate.get("runner_sha256") != digest(Path(__file__).resolve()) or gate.get("capture_file_sha256") != digest(CAPTURE_RECEIPT) or gate.get("preflight_file_sha256") != digest(PREFLIGHT_RECEIPT):
        raise T12Error("INDEPENDENT_GATE_DRIFT")
    if verify_work_state() != captured.get("declared_state") or tree_hashes(REPRESENTATIONS) != captured.get("representation_hashes") or tree_hashes(BASELINE_SNAPSHOT) != captured.get("baseline_snapshot_hashes"):
        raise T12Error("PRE_EXECUTION_DRIFT")
    if EXECUTION_ROOT.exists():
        raise T12Error("EXECUTION_ROOT_PREEXISTS")
    r3 = U.BASE.load_r3()
    toolchain, venv, entrypoint = U.verify_product(r3)
    if digest(entrypoint) != captured.get("product_entrypoint_sha256"):
        raise T12Error("PRODUCT_DRIFT")
    for path in (EXECUTION_REPRESENTATIONS, EXECUTION_CUSTODY, EXECUTION_OUTPUT, EXECUTION_TEMP):
        path.mkdir(parents=True, mode=0o700)
    shutil.copytree(REPRESENTATIONS, EXECUTION_REPRESENTATIONS, dirs_exist_ok=True, copy_function=shutil.copy2)
    atomic_bytes(EXECUTION_REQUEST, REQUEST.read_bytes())
    if tree_hashes(EXECUTION_REPRESENTATIONS) != captured["representation_hashes"] or digest(EXECUTION_REQUEST) != captured["request_sha256"]:
        raise T12Error("EXECUTION_COPY_DRIFT")
    kill = guarded_destroy()
    baseline_count = restore_baseline(EXECUTION_SUCCESSOR)
    if baseline_count != 409 or (EXECUTION_SUCCESSOR / ".git").exists():
        raise T12Error("SUCCESSOR_BASELINE_INVALID")
    runtime = clone_dependencies(EXECUTION_SUCCESSOR / "node_modules")
    public = CONTROL / "public"
    public.mkdir(exist_ok=True)
    arguments = ["recover", "--request", str(EXECUTION_REQUEST), "--sandbox-root", str(EXECUTION_RECOVERY), "--workspace", str(EXECUTION_SUCCESSOR), "--representation-root", str(EXECUTION_REPRESENTATIONS), "--custody-root", str(EXECUTION_CUSTODY), "--output-root", str(EXECUTION_OUTPUT)]
    start = time.monotonic_ns()
    recovered = run(r3.seatbelt_command(entrypoint, toolchain, venv, public, EXECUTION_RECOVERY, arguments), cwd=ROOT, env=minimal_env(EXECUTION_TEMP, "/usr/bin:/bin"), timeout=120)
    productive_ns = time.monotonic_ns() - start
    recovery_record = record_command("t12-recovery", recovered)
    summary = json.loads(recovered.stdout) if recovered.returncode == 0 else {}
    if summary.get("verdict") != "PROMOTE" or summary.get("fresh_context_continued") is not True:
        raise T12Error("PRODUCT_RECOVERY_FAILED")
    if tree_hashes(EXECUTION_REPRESENTATIONS) != captured["representation_hashes"] or tree_hashes(REPRESENTATIONS) != captured["representation_hashes"]:
        raise T12Error("REPRESENTATION_MUTATED")
    acceptance = run_acceptance(EXECUTION_SUCCESSOR, "t12-successor", EXECUTION_TEMP)
    acceptance_ns = time.monotonic_ns() - start
    restored = {relative: digest(safe_file(EXECUTION_SUCCESSOR, relative)) for relative in DECLARED}
    if restored != EXPECTED_HASHES:
        raise T12Error("SUCCESSOR_FILE_DRIFT")
    process = run(["ps", "-axo", "pid=,command="], cwd=ROOT, timeout=30)
    residue = [line.decode("utf-8", "replace") for line in process.stdout.splitlines() if str(EXECUTION_ROOT) in line.decode("utf-8", "replace") and str(os.getpid()) not in line.decode("utf-8", "replace")]
    if process.returncode != 0 or residue:
        raise T12Error("PROCESS_RESIDUE")
    snapshot = CONTROL / "POST_RECOVERY_SNAPSHOT"
    if snapshot.exists():
        raise T12Error("SNAPSHOT_PREEXISTS")
    shutil.copytree(EXECUTION_OUTPUT, snapshot / "output", copy_function=shutil.copy2)
    shutil.copytree(EXECUTION_CUSTODY, snapshot / "custody", copy_function=shutil.copy2)
    for relative in DECLARED:
        target = snapshot / "restored" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_bytes(target, safe_file(EXECUTION_SUCCESSOR, relative).read_bytes())
    body = {"version": "ev1-task-execution-receipt-v1", "status": "MECHANICAL_TASK_COMPLETE_OPERATOR_OBSERVATION_REQUIRED", "task_id": TASK_ID, "backlog_sha256": BACKLOG_SHA256, "product_candidate": PRODUCT_CANDIDATE, "source_commit": SOURCE_COMMIT, "project_class": "MIXED_LANGUAGE_MONOREPO", "capture_file_sha256": digest(CAPTURE_RECEIPT), "capture_receipt_sha256": captured["receipt_sha256"], "execution_preflight_file_sha256": digest(PREFLIGHT_RECEIPT), "execution_preflight_receipt_sha256": preflighted["receipt_sha256"], "independent_gate_file_sha256": digest(INDEPENDENT_GATE), "state_mix": {"committed": True, "uncommitted": True, "untracked": True, "human_edit_required": False}, "declared_work_units_before_loss": 3, "usable_work_units_after_continuation": 3, "kill": kill, "empty_history_successor": True, "baseline_attribution": captured["baseline_attribution"], "baseline_files_recreated": baseline_count, "dependency_runtime": runtime, "recovery": recovery_record, "recovery_summary": summary, "output_hashes": tree_hashes(EXECUTION_OUTPUT), "custody_hashes": tree_hashes(EXECUTION_CUSTODY), "post_recovery_snapshot_hashes": tree_hashes(snapshot), "restored_file_hashes": restored, "acceptance_command": "pnpm exec prettier --check docs/RELEASE.md scripts/build-release-manifest.mjs scripts/build-release-manifest.test.ts && pnpm vitest run scripts/build-release-manifest.test.ts", "acceptance": acceptance, "invocation_to_productive_continuation_monotonic_ns": productive_ns, "invocation_to_acceptance_pass_monotonic_ns": acceptance_ns, "post_loss_task_restatement_words": 0, "manual_intervention_count_after_loss": 0, "expected_verdict": "PROMOTE", "observed_verdict": summary["verdict"], "stable_reason": summary["reason"], "false_promotion_count": 0, "false_refusal_count": 0, "invalid_count": 0, "unsafe_mutation_count": 0, "unauthorized_path_access_count": 0, "original_workspace_residue_bytes": 0, "task_process_residue_count": 0, "operator_qualitative_note": None, "operator_git_backup_counterfactual": None, "operator_observation_scoring": "PENDING_HUMAN_CONFIRMATION", "campaign_teardown_pending": True}
    receipt_hash, file_hash = atomic_record(TASK_RECEIPT, body)
    print(canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


def main() -> int:
    phase = argparse.ArgumentParser()
    phase.add_argument("phase", choices=("capture", "preflight", "execute"))
    selected = phase.parse_args().phase
    try:
        return {"capture": capture, "preflight": preflight, "execute": execute}[selected]()
    except Exception as exc:
        reason = f"{type(exc).__name__}:{exc}"
        if selected == "execute":
            preserve_failure(reason)
        print(canonical({"status": "EV1_T12_BLOCKED", "phase": selected, "reason": reason}).decode())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
