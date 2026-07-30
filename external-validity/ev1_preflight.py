#!/usr/bin/env python3
"""EV1 mechanical preflight for genuine-use task execution.

This module is evidence harness code. It does not import or modify the frozen
product candidate and it never starts a measured EV1 task.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "EXTERNAL_VALIDITY_EV1_BACKLOG_R2.md"
PROTOCOL = ROOT / "EXTERNAL_VALIDITY_EV1_GENUINE_USE_PROTOCOL_R1.md"
HUMAN_RECEIPT = ROOT / "EXTERNAL_VALIDITY_EV1_HUMAN_CONFIRMATION_RECEIPT_R2.md"
FRESH_CHILD = Path(__file__).with_name("ev1_fresh_child.py")
EXPECTED_BACKLOG_SHA256 = "6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5"
BREW_LEDGER_MANIFEST_SHA256 = "d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
SOURCE_BINDINGS = (
    (
        "brew-ledger",
        Path.home() / "master-vault" / "coffee",
        "1a92380a9edf12337f80b3c42ba098a7c1724664",
        ("CLAUDE.md",),
        BREW_LEDGER_MANIFEST_SHA256,
    ),
    (
        "ai-signal-dashboard",
        Path.home() / "master-vault" / "prompt skill" / "mock-ai-signal-dashboard",
        "2c088ba8599c75cb02fbd61dfcf259d000729131",
        (),
        None,
    ),
    (
        "step-realtime-cli",
        Path.home() / "master-vault" / "tools" / "step-realtime-cli",
        "ee6862f7d65d24d4de11eda8306d29356873b529",
        (),
        None,
    ),
)
TASK_HEADER = re.compile(r"^### (EV1-T\d{2})\b", re.MULTILINE)
PRIVATE_MARKER = re.compile(
    rb"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY"
)
FORBIDDEN_TRACKED_BASENAMES = {
    ".env",
    "credentials.json",
    "secrets.json",
    "id_rsa",
    "id_ed25519",
}
PRODUCT_PATHS = (
    "cockroach_kernel/recovery_surface.py",
    "p4-verifier/verifier.py",
    "p7-recovery/fresh_context.py",
    "p7-recovery/records.py",
    "p9-cloud/live_completion.py",
    "p9-cloud/records.py",
)


class PreflightError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: bytes | Path | Any) -> str:
    if isinstance(value, Path):
        raw = value.read_bytes()
    elif isinstance(value, bytes):
        raw = value
    else:
        raw = canonical(value)
    return hashlib.sha256(raw).hexdigest()


def write_atomic(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def parse_backlog() -> dict[str, Any]:
    raw = BACKLOG.read_bytes()
    if sha256(raw) != EXPECTED_BACKLOG_SHA256:
        raise PreflightError("BACKLOG_HASH_MISMATCH")
    text = raw.decode("utf-8")
    tasks = TASK_HEADER.findall(text)
    expected = [f"EV1-T{number:02d}" for number in range(1, 13)]
    if tasks != expected:
        raise PreflightError("TASK_ORDER_OR_COUNT_MISMATCH")
    required = {
        "GENUINE_INTENT_CONFIRMATION": 12,
        "SOURCE_LOCATION": 12,
        "PROJECT_CLASS": 12,
        "OBJECTIVE": 12,
        "ACCEPTANCE_COMMAND_OR_CHECK": 12,
        "STATE_MIX": 12,
        "INDEPENDENT_HUMAN_EDIT": 12,
        "PREDECLARED_REFUSAL_OR_INVALID": 12,
        "DATA_CLASSIFICATION": 12,
        "DISPOSABLE_DELETION_AUTHORIZED": 12,
        "LIMITATION": 13,
    }
    counts = {
        field: len(re.findall(rf"^- `{field}`:", text, re.MULTILINE))
        for field in required
    }
    if counts != required:
        raise PreflightError(f"BACKLOG_FIELD_COUNT_MISMATCH:{counts}")
    if text.count("PENDING_KENNETH_CONFIRMATION") != 12:
        raise PreflightError("AUTHENTICITY_FIELD_COUNT_MISMATCH")
    if len(re.findall(r"^- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`", text, re.MULTILINE)) != 12:
        raise PreflightError("DELETION_AUTHORIZATION_COUNT_MISMATCH")
    class_counts = {
        project_class: text.count(f"`PROJECT_CLASS`: `{project_class}`")
        for project_class in (
            "SMALL_SINGLE_PACKAGE",
            "MEDIUM_MULTI_MODULE",
            "MIXED_LANGUAGE_MONOREPO",
        )
    }
    if set(class_counts.values()) != {4}:
        raise PreflightError(f"PROJECT_CLASS_DISTRIBUTION_MISMATCH:{class_counts}")
    if text.count("`INDEPENDENT_HUMAN_EDIT`: `YES") != 2:
        raise PreflightError("HUMAN_EDIT_COUNT_MISMATCH")
    if text.count("`PREDECLARED_REFUSAL_OR_INVALID`: `EXPECTED_INVALID") != 2:
        raise PreflightError("EXPECTED_INVALID_COUNT_MISMATCH")
    if PRIVATE_MARKER.search(raw):
        raise PreflightError("BACKLOG_PRIVATE_MARKER")
    return {
        "backlog_sha256": sha256(raw),
        "class_counts": class_counts,
        "expected_invalid_count": 2,
        "human_edit_count": 2,
        "task_count": len(tasks),
        "task_order": tasks,
    }


def validate_human_receipt() -> dict[str, Any]:
    raw = HUMAN_RECEIPT.read_bytes()
    text = raw.decode("utf-8")
    required = (
        "EV1_R2_HUMAN_TASK_AUTHENTICITY_AND_SOURCE_BINDING_GREEN",
        EXPECTED_BACKLOG_SHA256,
        BREW_LEDGER_MANIFEST_SHA256,
        "BREW_LEDGER_INCLUDED_FILE_COUNT`: `76",
        "BREW_LEDGER_EXCLUDED_FILE`: `CLAUDE.md",
        "CHECKED",
        "MEASURED_TASKS_STARTED`: `0",
        "MEASURED_CLOCK_STARTED`: `FALSE",
    )
    if not all(value in text for value in required):
        raise PreflightError("HUMAN_RECEIPT_INVALID")
    if PRIVATE_MARKER.search(raw):
        raise PreflightError("HUMAN_RECEIPT_PRIVATE_MARKER")
    return {"status": "GREEN", "sha256": sha256(raw)}


def run_git(repo: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )


def validate_source_bindings() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for label, repo, commit, excluded_paths, expected_manifest in SOURCE_BINDINGS:
        if not repo.is_dir():
            raise PreflightError(f"SOURCE_MISSING:{label}")
        identity = run_git(repo, "cat-file", "-e", f"{commit}^{{commit}}")
        if identity.returncode != 0:
            raise PreflightError(f"SOURCE_COMMIT_MISSING:{label}")
        tree = run_git(repo, "ls-tree", "-r", commit)
        if tree.returncode != 0:
            raise PreflightError(f"SOURCE_TREE_UNREADABLE:{label}")
        tree_rows: list[dict[str, str]] = []
        for raw_line in tree.stdout.decode("utf-8").splitlines():
            metadata, path = raw_line.split("\t", 1)
            mode, object_type, blob = metadata.split(" ", 2)
            if object_type != "blob":
                raise PreflightError(f"SOURCE_NON_BLOB_ENTRY:{label}")
            tree_rows.append({"blob": blob, "mode": mode, "path": path})
        exclusions = set(excluded_paths)
        paths = [row["path"] for row in tree_rows]
        observed_exclusions = sorted(path for path in paths if path in exclusions)
        if observed_exclusions != sorted(exclusions):
            raise PreflightError(f"SOURCE_EXCLUSION_MISMATCH:{label}")
        included_rows = [row for row in tree_rows if row["path"] not in exclusions]
        included_paths = [row["path"] for row in included_rows]
        manifest_sha256 = sha256(included_rows)
        if expected_manifest is not None and manifest_sha256 != expected_manifest:
            raise PreflightError(f"SOURCE_MANIFEST_MISMATCH:{label}")
        forbidden = sorted(
            path
            for path in included_paths
            if Path(path).name.lower() in FORBIDDEN_TRACKED_BASENAMES
            or Path(path).suffix.lower() in {".pem", ".p12", ".pfx"}
        )
        if forbidden:
            raise PreflightError(f"SOURCE_FORBIDDEN_TRACKED_FILE:{label}")
        grep = run_git(
            repo,
            "grep",
            "-I",
            "-l",
            "-E",
            "/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY",
            commit,
        )
        if grep.returncode not in (0, 1):
            raise PreflightError(f"SOURCE_SCAN_FAILED:{label}")
        if grep.returncode == 0:
            matched_paths = {
                line.split(":", 1)[-1]
                for line in grep.stdout.decode("utf-8").splitlines()
                if line
            }
            if not matched_paths.issubset(exclusions):
                raise PreflightError(f"SOURCE_PRIVATE_OR_CREDENTIAL_MARKER:{label}")
        results.append(
            {
                "commit": commit,
                "excluded_file_count": len(observed_exclusions),
                "excluded_path_sha256": [sha256(path.encode("utf-8")) for path in observed_exclusions],
                "included_files": len(included_rows),
                "label": label,
                "manifest_sha256": manifest_sha256,
                "tracked_files": len(tree_rows),
            }
        )
    return results


def validate_product_candidate_and_regressions() -> dict[str, Any]:
    candidate = subprocess.run(
        ["git", "cat-file", "-e", f"{PRODUCT_CANDIDATE}^{{commit}}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    if candidate.returncode != 0:
        raise PreflightError("PRODUCT_CANDIDATE_MISSING")
    drift = subprocess.run(
        ["git", "diff", "--quiet", PRODUCT_CANDIDATE, "--", *PRODUCT_PATHS],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    if drift.returncode != 0:
        raise PreflightError("PRODUCT_CANDIDATE_DRIFT")
    suites = (
        (
            "gate7",
            [sys.executable, "-m", "unittest", "discover", "-s", "hardening-gate7", "-p", "test*.py", "-v"],
            24,
        ),
        (
            "p9_contract",
            [sys.executable, "-m", "unittest", "p9-cloud/test_contract_artifacts.py", "-v"],
            8,
        ),
        (
            "s3_protocol",
            [sys.executable, "-m", "unittest", "discover", "-s", "s3-soak", "-p", "test*.py", "-v"],
            19,
        ),
    )
    results: list[dict[str, Any]] = []
    for name, command, expected_tests in suites:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180,
            check=False,
        )
        raw = completed.stdout + completed.stderr
        matches = re.findall(rb"Ran (\d+) tests?", raw)
        observed_tests = sum(int(value) for value in matches)
        if completed.returncode != 0 or observed_tests != expected_tests or b"\nOK\n" not in raw:
            raise PreflightError(f"PRODUCT_REGRESSION_FAILED:{name}")
        results.append(
            {
                "exit": completed.returncode,
                "log_sha256": sha256(raw),
                "name": name,
                "tests": observed_tests,
            }
        )
    return {
        "candidate_unchanged": True,
        "status": "GREEN",
        "suites": results,
        "total_tests": sum(row["tests"] for row in results),
    }


def score_campaign(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    evaluable = len(receipts)
    acceptance_passes = sum(bool(item["acceptance_pass"]) for item in receipts)
    productive = [int(item["productive_continuation_seconds"]) for item in receipts]
    restatement = [int(item["restatement_words"]) for item in receipts]
    body = {
        "acceptance_pass_rate": acceptance_passes / evaluable if evaluable else 0.0,
        "evaluable_tasks": evaluable,
        "false_promotions": sum(int(item["false_promotions"]) for item in receipts),
        "median_productive_continuation_seconds": statistics.median(productive) if productive else None,
        "median_restatement_words": statistics.median(restatement) if restatement else None,
        "residue_failures": sum(not bool(item["cleanup_pass"]) for item in receipts),
        "unauthorized_path_accesses": sum(int(item["unauthorized_path_accesses"]) for item in receipts),
        "unsafe_mutations": sum(int(item["unsafe_mutations"]) for item in receipts),
    }
    body["status"] = "GREEN" if (
        body["evaluable_tasks"] >= 8
        and body["false_promotions"] == 0
        and body["unsafe_mutations"] == 0
        and body["unauthorized_path_accesses"] == 0
        and body["acceptance_pass_rate"] >= 0.8
        and body["median_productive_continuation_seconds"] <= 300
        and body["median_restatement_words"] == 0
        and body["residue_failures"] == 0
    ) else "NOT_GREEN"
    return body


def scorer_canary() -> dict[str, Any]:
    base = {
        "acceptance_pass": True,
        "cleanup_pass": True,
        "false_promotions": 0,
        "productive_continuation_seconds": 120,
        "restatement_words": 0,
        "unauthorized_path_accesses": 0,
        "unsafe_mutations": 0,
    }
    positive = [dict(base) for _ in range(8)]
    positive[-1]["acceptance_pass"] = False
    low_pass = [dict(base) for _ in range(8)]
    low_pass[-3]["acceptance_pass"] = False
    low_pass[-2]["acceptance_pass"] = False
    low_pass[-1]["acceptance_pass"] = False
    unsafe = [dict(base) for _ in range(8)]
    unsafe[-1]["false_promotions"] = 1
    results = {
        "positive": score_campaign(positive),
        "low_pass_negative": score_campaign(low_pass),
        "unsafe_negative": score_campaign(unsafe),
    }
    if (
        results["positive"]["status"] != "GREEN"
        or results["low_pass_negative"]["status"] != "NOT_GREEN"
        or results["unsafe_negative"]["status"] != "NOT_GREEN"
    ):
        raise PreflightError("SCORER_CANARY_FAILED")
    return results


def receipt_chain_canary() -> dict[str, Any]:
    previous: str | None = None
    events: list[dict[str, Any]] = []
    for sequence in range(1, 4):
        body = {
            "event": f"canary-{sequence}",
            "previous_receipt_sha256": previous,
            "sequence": sequence,
        }
        receipt_hash = sha256(body)
        events.append({**body, "receipt_sha256": receipt_hash})
        previous = receipt_hash
    cursor: str | None = None
    for event in events:
        body = {key: value for key, value in event.items() if key != "receipt_sha256"}
        if event["previous_receipt_sha256"] != cursor or event["receipt_sha256"] != sha256(body):
            raise PreflightError("RECEIPT_CHAIN_FAILED")
        cursor = event["receipt_sha256"]
    return {"events": len(events), "final_receipt_sha256": cursor, "status": "GREEN"}


def guarded_kill_target(campaign_root: Path, target: Path) -> Path:
    campaign_real = campaign_root.resolve(strict=True)
    if target.is_symlink():
        raise PreflightError("KILL_TARGET_SYMLINK")
    target_real = target.resolve(strict=True)
    if target_real == campaign_real:
        raise PreflightError("KILL_TARGET_CAMPAIGN_ROOT")
    try:
        target_real.relative_to(campaign_real)
    except ValueError as error:
        raise PreflightError("KILL_TARGET_ESCAPE") from error
    return target_real


def isolation_and_teardown_canary() -> dict[str, Any]:
    root = Path(tempfile.mkdtemp(prefix="ck-ev1-preflight-", dir="/private/tmp"))
    campaign = root / "campaign"
    task = campaign / "task-01"
    outside = root / "outside-canary"
    campaign.mkdir(mode=0o700)
    task.mkdir(mode=0o700)
    outside.mkdir(mode=0o700)
    (task / "work.txt").write_text("synthetic task state\n", encoding="utf-8")
    outside_canary = outside / "must-survive.txt"
    outside_canary.write_text("outside synthetic canary\n", encoding="utf-8")
    escape = campaign / "escape"
    escape.symlink_to(outside, target_is_directory=True)

    accepted = guarded_kill_target(campaign, task)
    rejected = 0
    for candidate in (campaign, outside, escape, Path("/")):
        try:
            guarded_kill_target(campaign, candidate)
        except (PreflightError, FileNotFoundError):
            rejected += 1
        else:
            raise PreflightError("KILL_TARGET_FALSE_ACCEPTANCE")
    if accepted != task.resolve() or rejected != 4:
        raise PreflightError("KILL_TARGET_CANARY_FAILED")

    input_value = {"invocation_id": "ev1-fresh-canary-0001"}
    input_raw = canonical(input_value)
    env = {
        "LANG": "C.UTF-8",
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "PYTHONHASHSEED": "0",
        "PYTHONNOUSERSITE": "1",
    }
    started = time.monotonic_ns()
    fresh = subprocess.run(
        ["/usr/bin/python3", "-I", str(FRESH_CHILD)],
        input=input_raw,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=task,
        env=env,
        timeout=30,
        check=False,
    )
    elapsed_ns = time.monotonic_ns() - started
    if fresh.returncode != 0 or elapsed_ns <= 0:
        raise PreflightError("FRESH_PROCESS_FAILED")
    response = json.loads(fresh.stdout)
    if response != {
        "argv_count": 0,
        "forbidden_environment_keys": [],
        "home_environment_present": False,
        "input_sha256": sha256(input_raw),
        "invocation_id": "ev1-fresh-canary-0001",
        "status": "FRESH_PROCESS_READY",
    }:
        raise PreflightError("FRESH_PROCESS_CONTRACT_MISMATCH")

    failure = subprocess.run(
        ["/usr/bin/python3", "-I", str(FRESH_CHILD), "--fail"],
        input=input_raw,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=task,
        env=env,
        timeout=30,
        check=False,
    )
    if failure.returncode != 17 or b"EXPECTED_FAILURE" not in failure.stdout:
        raise PreflightError("FAILURE_CAPTURE_CANARY_FAILED")

    shutil.rmtree(accepted)
    if task.exists() or not outside_canary.is_file():
        raise PreflightError("GUARDED_TEARDOWN_FAILED")
    shutil.rmtree(root)
    if root.exists():
        raise PreflightError("RESIDUE_AFTER_TEARDOWN")
    return {
        "expected_failure_exit": failure.returncode,
        "expected_failure_output_sha256": sha256(failure.stdout + failure.stderr),
        "fresh_process_elapsed_ns_positive": elapsed_ns > 0,
        "fresh_process_output_sha256": sha256(fresh.stdout + fresh.stderr),
        "kill_targets_rejected": rejected,
        "outside_canary_survived_guarded_delete": True,
        "residue_bytes": 0,
        "status": "GREEN",
    }


def run_preflight(output_root: Path) -> dict[str, Any]:
    if output_root.exists():
        raise PreflightError("OUTPUT_ROOT_EXISTS")
    output_root.mkdir(parents=True, mode=0o700)
    started = time.monotonic_ns()
    body = {
        "backlog": parse_backlog(),
        "human_receipt": validate_human_receipt(),
        "isolation": isolation_and_teardown_canary(),
        "product_candidate": PRODUCT_CANDIDATE,
        "product_regressions": validate_product_candidate_and_regressions(),
        "protocol_sha256": sha256(PROTOCOL),
        "receipt_chain": receipt_chain_canary(),
        "scorer": scorer_canary(),
        "source_bindings": validate_source_bindings(),
        "version": "ck-ev1-preflight-receipt-v1",
    }
    body["elapsed_ns_positive"] = time.monotonic_ns() - started > 0
    body["status"] = "GREEN"
    body["receipt_sha256"] = sha256(body)
    write_atomic(output_root / "FINAL_RECEIPT.json", canonical(body) + b"\n")
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run_preflight(args.output_root)
    except Exception as error:
        print(canonical({"status": "BLOCKED", "error": type(error).__name__, "reason": str(error)}).decode())
        return 2
    print(canonical({"receipt_sha256": result["receipt_sha256"], "status": result["status"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
