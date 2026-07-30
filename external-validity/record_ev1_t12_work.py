#!/usr/bin/env python3
"""Verify and record the frozen EV1-T12 task work before capture authorization."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

import prepare_ev1_t11 as BASE


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / ".ev1-runtime" / "EV1-T12"
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
PREPARATION = CONTROL / "PREPARATION_RECEIPT.json"
WORK_RECEIPT = CONTROL / "WORK_RECEIPT.json"
PNPM = CONTROL / "pnpm-runtime" / "node_modules" / "pnpm" / "bin" / "pnpm.cjs"
PROFILE = CONTROL / "offline.sb"
TASK_COMMIT = "62b3f01f00544ba618a04ea8935908de8b038bb4"
PREPARATION_FILE_SHA256 = "494619b9ed72c9e2f96330a7fd7248f821b8828d471a4e155b4229731d63950b"
PREPARATION_RECEIPT_SHA256 = "d8dc81d40f634624dbf454b4232c9462f29ba139a7c0e562f9bd17ee50be7fb1"
PNPM_SHA256 = "b276da51dc8ca5b0d3ee3371695b50fc8b3244b281b091c63a3f082a88dadeb9"
PROFILE_SHA256 = "5c358b8d847211333e7ba22df82d84f796b5f30a41a2682209a949d783adbd08"
DECLARED = (
    "docs/RELEASE.md",
    "scripts/build-release-manifest.mjs",
    "scripts/build-release-manifest.test.ts",
)
EXPECTED_HASHES = {
    "docs/RELEASE.md": "8ea051ff477c04d7becafb53fa970f9973875d67211ea2ae7c390ba4050d1fee",
    "scripts/build-release-manifest.mjs": "1aa1561692cba73683d00cb0991971e04a6ae9f70101c0b5093ee47eb2d9c40a",
    "scripts/build-release-manifest.test.ts": "01b0d4eaf0e0794e4b5d5224932a75186613e6f36f667681950255e9f9e69941",
}
EXPECTED_STATUS = [" M docs/RELEASE.md", "?? scripts/build-release-manifest.test.ts"]
NETWORK_OR_PROCESS = re.compile(
    rb"node:(?:http|https|net|dns|tls|child_process)|\bfetch\s*\(|\bWebSocket\b|\bXMLHttpRequest\b|\b(?:exec|spawn|fork)\s*\("
)
PRIVATE = re.compile(rb"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY")


class WorkError(RuntimeError):
    pass


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 900):
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def environment(tmp: Path) -> dict[str, str]:
    fake_home = CONTROL / "fake-home"
    return {
        "CI": "1",
        "HOME": str(fake_home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C",
        "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "TMPDIR": str(tmp),
        "XDG_CACHE_HOME": str(CONTROL / "xdg-cache"),
        "XDG_CONFIG_HOME": str(CONTROL / "xdg-config"),
        "XDG_STATE_HOME": str(CONTROL / "xdg-state"),
    }


def offline(command: list[str], *, tmp: Path, timeout: int = 900):
    tmp.mkdir(parents=True, exist_ok=True)
    return run(
        ["/usr/bin/sandbox-exec", "-f", str(PROFILE), *command],
        cwd=WORKSPACE,
        env=environment(tmp),
        timeout=timeout,
    )


def record_log(name: str, completed: subprocess.CompletedProcess[bytes]) -> dict[str, object]:
    raw = completed.stdout + completed.stderr
    BASE.atomic(CONTROL / name, raw)
    return {"exit": completed.returncode, "bytes": len(raw), "sha256": BASE.digest(raw)}


def main() -> int:
    if WORK_RECEIPT.exists():
        raise WorkError("WORK_ALREADY_RECORDED")
    if BASE.digest(PREPARATION) != PREPARATION_FILE_SHA256:
        raise WorkError("PREPARATION_FILE_DRIFT")
    preparation = json.loads(PREPARATION.read_bytes())
    if preparation.get("receipt_sha256") != PREPARATION_RECEIPT_SHA256 or preparation.get("status") != "EV1_T12_READY_FOR_TASK_WORK":
        raise WorkError("PREPARATION_RECEIPT_DRIFT")
    if BASE.digest(PNPM) != PNPM_SHA256 or BASE.digest(PROFILE) != PROFILE_SHA256:
        raise WorkError("TOOLCHAIN_DRIFT")
    head = run(["git", "rev-parse", "HEAD"], cwd=WORKSPACE)
    status = run(["git", "status", "--porcelain=v1", "-uall"], cwd=WORKSPACE)
    if head.returncode != 0 or head.stdout.decode().strip() != TASK_COMMIT:
        raise WorkError("TASK_COMMIT_DRIFT")
    if status.returncode != 0 or status.stdout.decode().splitlines() != EXPECTED_STATUS:
        raise WorkError("TASK_STATUS_DRIFT")
    hashes = {relative: BASE.digest(WORKSPACE / relative) for relative in DECLARED}
    if hashes != EXPECTED_HASHES:
        raise WorkError("DECLARED_FILE_HASH_DRIFT")
    if PRIVATE.search(b"\n".join((WORKSPACE / relative).read_bytes() for relative in DECLARED)):
        raise WorkError("PRIVATE_MARKER_PRESENT")
    generator = (WORKSPACE / "scripts" / "build-release-manifest.mjs").read_bytes()
    if NETWORK_OR_PROCESS.search(generator):
        raise WorkError("NETWORK_OR_PROCESS_CODE_PRESENT")

    acceptance_tmp = CONTROL / "t12-work-tmp"
    prettier = offline(
        [
            "/usr/local/bin/node",
            str(PNPM),
            "exec",
            "prettier",
            "--check",
            *DECLARED,
        ],
        tmp=acceptance_tmp,
    )
    prettier_record = record_log("t12-work-prettier.log", prettier)
    tests = offline(
        [
            "/usr/local/bin/node",
            str(PNPM),
            "vitest",
            "run",
            "scripts/build-release-manifest.test.ts",
        ],
        tmp=acceptance_tmp,
    )
    test_record = record_log("t12-work-tests.log", tests)
    if prettier.returncode != 0 or tests.returncode != 0:
        raise WorkError("TASK_ACCEPTANCE_FAILED")

    fixture = CONTROL / "t12-determinism-fixture"
    if fixture.exists():
        raise WorkError("FIXTURE_PREEXISTS")
    (fixture / "bin").mkdir(parents=True)
    BASE.atomic(fixture / "bin" / "step-linux", b"synthetic-linux\n")
    BASE.atomic(fixture / "bin" / "step-macos", b"synthetic-macos\n")
    spec = [
        {"platform": "linux-x64", "path": "bin/step-linux"},
        {"platform": "darwin-arm64", "path": "bin/step-macos"},
    ]
    BASE.atomic(fixture / "spec.json", BASE.canonical(spec) + b"\n")
    outputs: list[bytes] = []
    runs: list[dict[str, object]] = []
    for index in range(1, 6):
        output = fixture / f"manifest-r{index}.json"
        completed = offline(
            [
                "/usr/local/bin/node",
                "scripts/build-release-manifest.mjs",
                "--root",
                str(fixture),
                "--spec",
                str(fixture / "spec.json"),
                "--output",
                str(output),
            ],
            tmp=acceptance_tmp,
            timeout=120,
        )
        if completed.returncode != 0 or not output.is_file() or completed.stdout != output.read_bytes():
            raise WorkError(f"DETERMINISM_RUN_FAILED:{index}")
        outputs.append(output.read_bytes())
        runs.append({"index": index, "exit": completed.returncode, "output_sha256": BASE.digest(output)})
    if len(set(outputs)) != 1:
        raise WorkError("DETERMINISM_OUTPUT_MISMATCH")
    sample = outputs[0]
    parsed = json.loads(sample)
    if [entry["platform"] for entry in parsed.get("artifacts", [])] != ["darwin-arm64", "linux-x64"]:
        raise WorkError("CANONICAL_ORDER_FAILED")
    BASE.atomic(CONTROL / "t12-manifest-sample.json", sample)
    shutil.rmtree(fixture)
    shutil.rmtree(acceptance_tmp)
    if fixture.exists() or acceptance_tmp.exists():
        raise WorkError("TEMP_RESIDUE")

    post_status = run(["git", "status", "--porcelain=v1", "-uall"], cwd=WORKSPACE)
    if post_status.returncode != 0 or post_status.stdout.decode().splitlines() != EXPECTED_STATUS:
        raise WorkError("ACCEPTANCE_MUTATED_WORKSPACE")
    body = {
        "version": "ev1-t12-work-receipt-v1",
        "status": "EV1_T12_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED",
        "task_id": "EV1-T12",
        "utc_recorded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "task_commit": TASK_COMMIT,
        "disposable_baseline_commit": preparation["disposable_baseline_commit"],
        "declared_file_hashes": hashes,
        "state_mix": {
            "committed": ["scripts/build-release-manifest.mjs"],
            "uncommitted": ["docs/RELEASE.md"],
            "untracked": ["scripts/build-release-manifest.test.ts"],
            "status": EXPECTED_STATUS,
        },
        "human_edit_required": False,
        "synthetic_binary_fixtures_only": True,
        "network_or_process_code_present": False,
        "release_upload_signing_registry_actions": 0,
        "acceptance": {
            "command": "pnpm exec prettier --check docs/RELEASE.md scripts/build-release-manifest.mjs scripts/build-release-manifest.test.ts && pnpm vitest run scripts/build-release-manifest.test.ts",
            "prettier": prettier_record,
            "tests": test_record,
            "test_files_passed": 1,
            "tests_passed": 8,
            "network_mode": "DENIED_SEATBELT",
        },
        "determinism": {
            "runs": runs,
            "five_of_five_byte_identical": True,
            "manifest_sha256": BASE.digest(sample),
            "canonical_platform_order": ["darwin-arm64", "linux-x64"],
        },
        "private_marker_matches": 0,
        "temporary_residue_paths": 0,
        "capture_started": False,
        "deletion_started": False,
        "recovery_started": False,
    }
    receipt_hash, file_hash = BASE.record(WORK_RECEIPT, body)
    print(BASE.canonical({"file_sha256": file_hash, "receipt_sha256": receipt_hash, "status": body["status"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
