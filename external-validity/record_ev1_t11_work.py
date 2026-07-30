#!/usr/bin/env python3
"""Verify and freeze EV1-T11 task work before any capture or deletion."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / ".ev1-runtime" / "EV1-T11"
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
PREPARATION = CONTROL / "PREPARATION_RECEIPT.json"
RECEIPT = CONTROL / "WORK_RECEIPT.json"
PREPARATION_FILE_SHA256 = "3d4e7dc29fb7e8eef17b4ebc13ece6ac9d056d523cb6677067c25a703edd2139"
PREPARATION_RECEIPT_SHA256 = "6098fad3ca259498bb35a8753aa6251bc64e125f28fddc554e345ae3b469171b"
BASELINE_COMMIT = "fadda411374331866368c3ee3edfa02e7f221d03"
TASK_COMMIT = "36790fe0c7c6badae07ae95e1383a051746f1a8c"
EXPECTED_STATUS = [" M docs/RELEASE.md", "?? scripts/release-readiness-cases.json"]
DECLARED = [
    "docs/RELEASE.md",
    "scripts/check-release-readiness.mjs",
    "scripts/release-readiness-cases.json",
]
PNPM = CONTROL / "pnpm-runtime" / "node_modules" / "pnpm" / "bin" / "pnpm.cjs"
PNPM_SHA256 = "b276da51dc8ca5b0d3ee3371695b50fc8b3244b281b091c63a3f082a88dadeb9"
PRIVATE = re.compile(rb"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY")
ALLOWED_NODE_IMPORTS = {"node:crypto", "node:fs", "node:path", "node:url"}


class WorkError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: bytes | Path | Any) -> str:
    raw = value.read_bytes() if isinstance(value, Path) else value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def atomic(path: Path, raw: bytes) -> None:
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


def environment(temp_root: Path | None = None) -> dict[str, str]:
    base = temp_root if temp_root is not None else CONTROL
    fake_home = base / "fake-home"
    tmp = base / "tmp"
    xdg_cache = base / "xdg-cache"
    xdg_config = base / "xdg-config"
    xdg_state = base / "xdg-state"
    for path in (fake_home, tmp, xdg_cache, xdg_config, xdg_state):
        path.mkdir(parents=True, exist_ok=True)
    return {
        "CI": "1",
        "HOME": str(fake_home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "TMPDIR": str(tmp),
        "XDG_CACHE_HOME": str(xdg_cache),
        "XDG_CONFIG_HOME": str(xdg_config),
        "XDG_STATE_HOME": str(xdg_state),
    }


def run(command: list[str], *, cwd: Path = WORKSPACE, timeout: int = 900, env_root: Path | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command],
        cwd=cwd,
        env=environment(env_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def logged(command: list[str], name: str, expected_exit: int, *, timeout: int = 900) -> dict[str, Any]:
    completed = run(command, timeout=timeout)
    raw = completed.stdout + completed.stderr
    atomic(CONTROL / f"{name}.log", raw)
    if completed.returncode != expected_exit:
        raise WorkError(f"COMMAND_EXIT_MISMATCH:{name}:{completed.returncode}")
    return {
        "command_label": name,
        "exit": completed.returncode,
        "log_bytes": len(raw),
        "log_sha256": digest(raw),
        "network_mode": "DENIED_SEATBELT",
    }


def git(*arguments: str) -> list[str]:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=WORKSPACE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        raise WorkError("GIT_INSPECTION_FAILED")
    return completed.stdout.decode().splitlines()


def mutate(root: Path, mutation: str) -> list[str]:
    if mutation == "arguments-empty":
        return []
    if mutation == "arguments-publish":
        return ["--publish"]
    package_path = root / "package.json"
    package = json.loads(package_path.read_text())
    if mutation == "root-private-false":
        package["private"] = False
    elif mutation == "root-version-invalid":
        package["version"] = "v1"
    elif mutation == "root-unresolved-workspace-reference":
        package.setdefault("dependencies", {})["missing-local-package"] = "workspace:*"
    elif mutation == "root-local-version-binding":
        package["dependencies"]["@step-cli/core"] = "1.0.0"
    elif mutation == "root-bin-target-missing":
        package["bin"]["step"] = "bin/missing-step-cli.js"
    elif mutation == "license-missing":
        (root / "LICENSE").unlink()
        return ["--offline-dry-run"]
    else:
        raise WorkError(f"UNKNOWN_MUTATION:{mutation}")
    atomic(package_path, canonical(package) + b"\n")
    return ["--offline-dry-run"]


def adversarial_case(case: dict[str, str], root: Path) -> dict[str, Any]:
    case_root = root / case["id"]
    shutil.copytree(
        WORKSPACE,
        case_root,
        symlinks=True,
        ignore=shutil.ignore_patterns(".git", "node_modules"),
    )
    arguments = mutate(case_root, case["mutation"])
    completed = run(
        ["/usr/local/bin/node", "scripts/check-release-readiness.mjs", *arguments],
        cwd=case_root,
        timeout=120,
        env_root=case_root / ".runtime",
    )
    raw = completed.stdout + completed.stderr
    atomic(CONTROL / f"t11-negative-{case['id']}.log", raw)
    expected = f"RELEASE_READINESS_INVALID:{case['expected']}\n".encode()
    if completed.returncode != 1 or raw != expected:
        raise WorkError(f"NEGATIVE_CASE_FALSE_ACCEPT:{case['id']}:{completed.returncode}")
    return {
        "case": case["id"],
        "exit": completed.returncode,
        "expected": case["expected"],
        "log_sha256": digest(raw),
        "rejected": True,
    }


def main() -> int:
    if RECEIPT.exists():
        raise WorkError("WORK_ALREADY_RECORDED")
    if digest(PREPARATION) != PREPARATION_FILE_SHA256:
        raise WorkError("PREPARATION_FILE_DRIFT")
    preparation = json.loads(PREPARATION.read_text())
    if preparation.get("receipt_sha256") != PREPARATION_RECEIPT_SHA256:
        raise WorkError("PREPARATION_RECEIPT_DRIFT")
    if git("rev-parse", "HEAD") != [TASK_COMMIT]:
        raise WorkError("TASK_COMMIT_DRIFT")
    if git("status", "--porcelain=v1", "-uall") != EXPECTED_STATUS:
        raise WorkError("TASK_STATE_DRIFT")
    committed_delta = git("diff", "--name-only", f"{BASELINE_COMMIT}..{TASK_COMMIT}")
    if committed_delta != ["scripts/check-release-readiness.mjs"]:
        raise WorkError("COMMITTED_SET_DRIFT")
    if digest(PNPM) != PNPM_SHA256:
        raise WorkError("PINNED_TOOL_DRIFT")
    package = json.loads((WORKSPACE / "package.json").read_text())
    if package.get("private") is not True:
        raise WorkError("PRIVATE_PACKAGE_SAFEGUARD_MISSING")

    hashes = {relative: digest(WORKSPACE / relative) for relative in DECLARED}
    if any(PRIVATE.search((WORKSPACE / relative).read_bytes()) for relative in DECLARED):
        raise WorkError("DECLARED_FILE_PRIVATE_MARKER")
    guard = (WORKSPACE / "scripts" / "check-release-readiness.mjs").read_text()
    imports = set(re.findall(r'from\s+["\']([^"\']+)["\']', guard))
    if imports != ALLOWED_NODE_IMPORTS:
        raise WorkError("GUARD_IMPORT_SURFACE_INVALID")
    forbidden_tokens = (
        "node:http",
        "node:https",
        "node:net",
        "node:dns",
        "node:tls",
        "node:dgram",
        "node:child_process",
        "fetch(",
        "XMLHttpRequest",
        "WebSocket",
        "process.env",
        "writeFile",
        "appendFile",
        "createWriteStream",
        "rmSync",
        "unlinkSync",
        "renameSync",
    )
    if any(token in guard for token in forbidden_tokens):
        raise WorkError("GUARD_NETWORK_PROCESS_OR_WRITE_SURFACE")

    prettier = logged(
        ["/usr/local/bin/node", str(PNPM), "exec", "prettier", "--check", "docs/RELEASE.md", "scripts/check-release-readiness.mjs"],
        "t11-prettier",
        0,
    )
    guard_runs = []
    guard_outputs = []
    for index in range(1, 6):
        result = logged(
            ["/usr/local/bin/node", "scripts/check-release-readiness.mjs", "--offline-dry-run"],
            f"t11-guard-r{index}",
            0,
            timeout=120,
        )
        guard_runs.append(result)
        raw = (CONTROL / f"t11-guard-r{index}.log").read_bytes()
        guard_outputs.append(raw)
        parsed = json.loads(raw)
        if parsed.get("status") != "RELEASE_READINESS_GREEN" or parsed.get("publish_action") != "REFUSED_ROOT_PRIVATE":
            raise WorkError("GUARD_POSITIVE_OUTPUT_INVALID")
    if len({digest(raw) for raw in guard_outputs}) != 1:
        raise WorkError("GUARD_NONDETERMINISTIC")
    tests = logged(["/usr/local/bin/node", str(PNPM), "test"], "t11-full-tests", 0, timeout=900)

    cases_body = json.loads((WORKSPACE / "scripts" / "release-readiness-cases.json").read_text())
    cases = cases_body.get("cases")
    expected_ids = [
        "missing-flag",
        "publish-like-flag",
        "root-not-private",
        "root-version-invalid",
        "unresolved-workspace-reference",
        "local-version-binding",
        "missing-bin-target",
        "missing-license",
    ]
    if not isinstance(cases, list) or [case.get("id") for case in cases] != expected_ids:
        raise WorkError("ADVERSARIAL_CASE_CONTRACT_INVALID")
    temporary = Path(tempfile.mkdtemp(prefix=".ev1-t11-adversarial-", dir=CONTROL))
    try:
        negative = [adversarial_case(case, temporary) for case in cases]
    finally:
        shutil.rmtree(temporary)
    if temporary.exists():
        raise WorkError("ADVERSARIAL_TEMP_RESIDUE")
    if git("status", "--porcelain=v1", "-uall") != EXPECTED_STATUS:
        raise WorkError("POST_TEST_TASK_STATE_DRIFT")

    body = {
        "version": "ev1-t11-work-receipt-v1",
        "status": "EV1_T11_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED",
        "task_id": "EV1-T11",
        "utc_recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "backlog_sha256": preparation["backlog_sha256"],
        "global_ev1_preflight_packet_sha256": preparation["global_ev1_preflight_packet_sha256"],
        "product_candidate": preparation["product_candidate"],
        "source_commit": preparation["source_commit"],
        "source_manifest_sha256": preparation["source_manifest_sha256"],
        "preparation_file_sha256": PREPARATION_FILE_SHA256,
        "preparation_receipt_sha256": PREPARATION_RECEIPT_SHA256,
        "baseline_commit": BASELINE_COMMIT,
        "task_commit": TASK_COMMIT,
        "state_mix": {
            "committed": ["scripts/check-release-readiness.mjs"],
            "uncommitted": ["docs/RELEASE.md"],
            "untracked": ["scripts/release-readiness-cases.json"],
            "status": EXPECTED_STATUS,
        },
        "declared_file_hashes": hashes,
        "private_package_safeguard": True,
        "guard_authority": "READ_ONLY_LOCAL_METADATA_VALIDATION_AND_PUBLISH_REFUSAL",
        "guard_allowed_imports": sorted(imports),
        "guard_network_process_or_write_surface": False,
        "runtime": preparation["runtime"],
        "acceptance": {
            "prettier": prettier,
            "guard_runs": guard_runs,
            "guard_repeat_count": 5,
            "guard_outputs_identical": True,
            "guard_output_sha256": digest(guard_outputs[0]),
            "full_tests": tests,
            "negative_cases": negative,
            "negative_case_count": len(negative),
        },
        "human_edit_required": False,
        "capture_started": False,
        "deletion_started": False,
        "recovery_started": False,
        "public_action": False,
        "adversarial_temp_residue_count": 0,
    }
    receipt_hash = digest(body)
    raw = canonical(dict(body, receipt_sha256=receipt_hash)) + b"\n"
    atomic(RECEIPT, raw)
    print(canonical({"file_sha256": digest(raw), "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
