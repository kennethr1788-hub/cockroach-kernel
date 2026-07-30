#!/usr/bin/env python3
"""Verify and freeze EV1-T10 task work before any capture or deletion."""
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
CAMPAIGN = ROOT / ".ev1-runtime" / "EV1-T10"
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
PREPARATION = CONTROL / "PREPARATION_RECEIPT.json"
RECEIPT = CONTROL / "WORK_RECEIPT.json"
PREPARATION_FILE_SHA256 = "9f0d51f0546d491b593744688cba86f99582c815efb8aaeccae3f1a6c46a56e5"
PREPARATION_RECEIPT_SHA256 = "ade77d1383dd8b7c5c12afd1d4e96b4a765d37f1c6f51d826ecaf9521d1e03cf"
BASELINE_COMMIT = "9d775362d58f3c8061953c2955f1289b6f1518a4"
TASK_COMMIT = "5c671337842dc3ece20aa969f4bdec95eacc4203"
EXPECTED_STATUS = [" M docs/RELEASE.md", "?? .github/release-notes-template.md"]
DECLARED = [
    ".github/release-notes-template.md",
    "docs/RELEASE.md",
    "scripts/validate-release-notes.mjs",
]
PNPM = CONTROL / "pnpm-runtime" / "node_modules" / "pnpm" / "bin" / "pnpm.cjs"
PRETTIER = CAMPAIGN / "dependency-runtime" / "node_modules" / "prettier" / "bin" / "prettier.cjs"
PNPM_SHA256 = "b276da51dc8ca5b0d3ee3371695b50fc8b3244b281b091c63a3f082a88dadeb9"
PRETTIER_SHA256 = "ac5523cd57e7e9d8eac71caef7e022a8a8489bcdc19ca8a778b7e728ec103b93"
PRIVATE = re.compile(rb"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY")


class WorkError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: bytes | Path | Any) -> str:
    raw = value.read_bytes() if isinstance(value, Path) else value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def atomic(path: Path, raw: bytes) -> None:
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


def environment() -> dict[str, str]:
    return {
        "CI": "1",
        "HOME": str(CONTROL / "fake-home"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        "PATH": f"{CONTROL / 'bin'}:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "TMPDIR": str(CONTROL / "tmp"),
        "XDG_CACHE_HOME": str(CONTROL / "xdg-cache"),
        "XDG_CONFIG_HOME": str(CONTROL / "xdg-config"),
        "XDG_STATE_HOME": str(CONTROL / "xdg-state"),
    }


def run(command: list[str], *, cwd: Path = WORKSPACE, timeout: int = 300) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["/usr/bin/sandbox-exec", "-f", str(CONTROL / "offline.sb"), *command],
        cwd=cwd,
        env=environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def logged(command: list[str], name: str, expected_exit: int) -> dict[str, Any]:
    completed = run(command)
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


def negative_case(path: Path, label: str) -> dict[str, Any]:
    relative = path.relative_to(WORKSPACE).as_posix()
    completed = run(["/usr/local/bin/node", "scripts/validate-release-notes.mjs", relative])
    raw = completed.stdout + completed.stderr
    atomic(CONTROL / f"t10-negative-{label}.log", raw)
    if completed.returncode != 1 or not raw.startswith(b"RELEASE_NOTES_INVALID:"):
        raise WorkError(f"NEGATIVE_CASE_FALSE_ACCEPT:{label}:{completed.returncode}")
    return {
        "case": label,
        "exit": completed.returncode,
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
    if committed_delta != ["scripts/validate-release-notes.mjs"]:
        raise WorkError("COMMITTED_SET_DRIFT")
    if digest(PNPM) != PNPM_SHA256 or digest(PRETTIER) != PRETTIER_SHA256:
        raise WorkError("PINNED_TOOL_DRIFT")
    package = json.loads((WORKSPACE / "package.json").read_text())
    if package.get("private") is not True:
        raise WorkError("PRIVATE_PACKAGE_SAFEGUARD_MISSING")

    hashes = {relative: digest(WORKSPACE / relative) for relative in DECLARED}
    if any(PRIVATE.search((WORKSPACE / relative).read_bytes()) for relative in DECLARED):
        raise WorkError("DECLARED_FILE_PRIVATE_MARKER")
    validator = (WORKSPACE / "scripts" / "validate-release-notes.mjs").read_text()
    forbidden = ("node:http", "node:https", "node:net", "fetch(", "child_process", "npm publish", "gh release")
    if any(token in validator for token in forbidden):
        raise WorkError("VALIDATOR_NETWORK_OR_PUBLISH_SURFACE")

    prettier = logged(
        [str(PNPM), "exec", "prettier", "--check", "docs/RELEASE.md", ".github/release-notes-template.md"],
        "t10-prettier",
        0,
    )
    validator_runs = []
    validator_outputs = []
    for index in range(1, 6):
        result = logged(
            ["/usr/local/bin/node", "scripts/validate-release-notes.mjs", ".github/release-notes-template.md"],
            f"t10-validator-r{index}",
            0,
        )
        validator_runs.append(result)
        validator_outputs.append((CONTROL / f"t10-validator-r{index}.log").read_bytes())
    if len({digest(raw) for raw in validator_outputs}) != 1:
        raise WorkError("VALIDATOR_NONDETERMINISTIC")

    template = (WORKSPACE / ".github" / "release-notes-template.md").read_text()
    temporary = Path(tempfile.mkdtemp(prefix=".ev1-t10-adversarial-", dir=WORKSPACE))
    try:
        missing = temporary / "missing.md"
        missing.write_text(template[: template.index("## Known limitations")])
        duplicate = temporary / "duplicate.md"
        duplicate.write_text(template + "\n## Highlights\n\n- duplicate\n")
        reordered = temporary / "reordered.md"
        reordered.write_text(
            template.replace("## Highlights", "## __swap__", 1)
            .replace("## Breaking changes", "## Highlights", 1)
            .replace("## __swap__", "## Breaking changes", 1)
        )
        oversized = temporary / "oversized.md"
        oversized.write_text(template + ("x" * (64 * 1024)))
        symlinked = temporary / "symlink.md"
        os.symlink(os.path.relpath(WORKSPACE / ".github" / "release-notes-template.md", temporary), symlinked)
        negative = [
            negative_case(missing, "missing"),
            negative_case(duplicate, "duplicate"),
            negative_case(reordered, "reordered"),
            negative_case(oversized, "oversized"),
            negative_case(symlinked, "symlink"),
        ]
    finally:
        shutil.rmtree(temporary)
    if temporary.exists():
        raise WorkError("ADVERSARIAL_TEMP_RESIDUE")
    if git("status", "--porcelain=v1", "-uall") != EXPECTED_STATUS:
        raise WorkError("POST_TEST_TASK_STATE_DRIFT")

    body = {
        "version": "ev1-t10-work-receipt-v1",
        "status": "EV1_T10_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED",
        "task_id": "EV1-T10",
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
            "committed": ["scripts/validate-release-notes.mjs"],
            "uncommitted": ["docs/RELEASE.md"],
            "untracked": [".github/release-notes-template.md"],
            "status": EXPECTED_STATUS,
        },
        "declared_file_hashes": hashes,
        "private_package_safeguard": True,
        "validator_network_or_publish_surface": False,
        "pinned_tools": {
            "pnpm_version": "10.17.0",
            "pnpm_entry_sha256": PNPM_SHA256,
            "prettier_version": "3.8.1",
            "prettier_entry_sha256": PRETTIER_SHA256,
        },
        "acceptance": {
            "prettier": prettier,
            "validator_runs": validator_runs,
            "validator_repeat_count": 5,
            "validator_outputs_identical": True,
            "negative_cases": negative,
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
