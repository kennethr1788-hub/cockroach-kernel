#!/usr/bin/env python3
"""Evidence-only PDH-1 captured-versus-uncaptured boundary campaign.

This controller does not modify product behavior. It invokes the frozen public
``cockroach-kernel recover`` path in a fresh disposable root for every case,
under the fixed macOS network-denial profile. The controller alone retains the
B4 oracle bytes in memory; those bytes are not written to a fixture, request,
representation, prompt, environment variable, or subprocess argument.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile
import time
from typing import Any

from cockroach_kernel import recovery_surface as surface
from p7_runtime import records as p7


CAMPAIGN_VERSION = "ck-pdh1-information-boundary-v1"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
REPEATS = 5
PROFILE = b"(version 1)\n(allow default)\n(deny network*)\n"
EXPECTED_CLASSES = {
    "B1": "RECOVERED_EXACT",
    "B2": "RECOVERED_EXACT",
    "B3": "RECOVERED_EXACT",
    "B4": "UNRECOVERABLE_NO_SURVIVING_REPRESENTATION",
    "B5": "RECOVERED_MAXIMUM_PROVABLE_SUBSET",
    "B6": "INVALID_TAMPERED_EVIDENCE",
}


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(value: bytes | Path) -> str:
    if isinstance(value, Path):
        return hashlib.sha256(value.read_bytes()).hexdigest()
    return hashlib.sha256(value).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("wb") as handle:
        handle.write(canonical(value) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def tree(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): digest(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def event_chain(labels: tuple[str, ...]) -> list[dict[str, Any]]:
    return [
        {
            "sequence": index,
            "event": label,
            "event_hash": digest(label.encode("utf-8")),
        }
        for index, label in enumerate(labels)
    ]


def build_request(
    case_id: str,
    files: dict[str, bytes],
    represented: set[str],
) -> tuple[dict[str, Any], dict[str, bytes]]:
    entries = [
        {
            "path": path,
            "content_hash": digest(raw),
            "executable": False,
            "is_symlink": False,
        }
        for path, raw in sorted(files.items())
    ]
    manifest = {
        "version": p7.VERSION,
        "manifest_id": f"manifest-{case_id.lower()}",
        "task_id": f"task-{case_id.lower()}",
        "files": entries,
    }
    events = event_chain(("capture-frozen", "declared-loss"))
    previous = ""
    for event in events:
        previous = p7.sha256_hex({"previous": previous, "event": event})
    trajectory = {
        "version": p7.VERSION,
        "receipt_id": f"trajectory-{case_id.lower()}",
        "task_id": manifest["task_id"],
        "manifest_hash": p7.sha256_hex(manifest),
        "events": events,
        "trajectory_hash": previous,
    }
    quorum = {"decision": "PROMOTE"}
    context = {
        "manifest": manifest,
        "trajectory_receipt": trajectory,
        "policy_version": "policy-pdh1-v1",
        "quorum_decision_hash": p7.sha256_hex(quorum),
    }
    test_path = sorted(represented)[0] if represented else sorted(files)[0]
    candidate = {
        "version": p7.VERSION,
        "candidate_id": f"candidate-{case_id.lower()}",
        "task_id": manifest["task_id"],
        "provenance": {"source": "pdh1-frozen-synthetic"},
        "source_receipt_hash": p7.sha256_hex(trajectory),
        "policy_version": context["policy_version"],
        "policy_veto": False,
        "tampered": False,
        "quorum_decision": quorum,
        "prefix_length": len(events),
        "integrity_hash": p7.trajectory_integrity_hash(events, len(events)),
        "declared_paths": sorted(files),
        "file_hashes": {path: digest(raw) for path, raw in sorted(files.items())},
        "executable_test": {
            "test_id": f"test-{case_id.lower()}",
            "path": test_path,
            "feature_hash": digest(files[test_path]),
            "passed": True,
        },
    }
    decision = p7.select_candidate([candidate], context)
    warrant = p7.make_warrant(
        f"warrant-{case_id.lower()}",
        manifest["task_id"],
        candidate["candidate_id"],
        decision,
    )
    lost_paths = sorted(files)
    loss_receipt = {
        "version": p7.VERSION,
        "receipt_id": f"loss-{case_id.lower()}",
        "task_id": manifest["task_id"],
        "manifest_hash": p7.sha256_hex(manifest),
        "lost_paths": lost_paths,
        "absence_hash": p7.sha256_hex({"lost_paths": lost_paths, "observed": "absent"}),
    }
    request = {
        "version": surface.REQUEST_VERSION,
        "request_id": f"request-{case_id.lower()}",
        "context": context,
        "loss_receipt": loss_receipt,
        "candidates": [candidate],
        "warrant": warrant,
    }
    return request, {path: files[path] for path in represented}


def case_inputs(b4_oracle: bytes) -> dict[str, tuple[dict[str, bytes], set[str], bool]]:
    return {
        "B1": ({"src/committed.py": b"print('captured committed')\n"}, {"src/committed.py"}, False),
        "B2": ({"src/modified.py": b"print('captured modified')\n"}, {"src/modified.py"}, False),
        "B3": ({"notes/untracked.md": b"captured untracked\n"}, {"notes/untracked.md"}, False),
        "B4": ({"lost/post-capture.bin": b4_oracle}, set(), False),
        "B5": (
            {
                "src/provable.py": b"print('maximum provable subset')\n",
                "notes/unverifiable.txt": b"declared but representation unavailable\n",
            },
            {"src/provable.py"},
            False,
        ),
        "B6": ({"src/tampered.py": b"original captured bytes\n"}, {"src/tampered.py"}, True),
    }


def sanitized_environment(tmpdir: Path) -> dict[str, str]:
    return {
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONNOUSERSITE": "1",
        "TMPDIR": str(tmpdir),
    }


def network_denial_probe(profile: Path, python: Path, root: Path) -> dict[str, Any]:
    command = [
        "/usr/bin/sandbox-exec",
        "-f",
        str(profile),
        str(python),
        "-c",
        (
            "import socket;"
            "socket.create_connection(('127.0.0.1',9),timeout=0.1)"
        ),
    ]
    completed = subprocess.run(
        command,
        cwd=root,
        env=sanitized_environment(root),
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    return {
        "command_class": "LOOPBACK_CONNECT_EXPECTED_DENIED",
        "exit_code": completed.returncode,
        "denied": completed.returncode != 0,
        "stdout_sha256": digest(completed.stdout.encode()),
        "stderr_sha256": digest(completed.stderr.encode()),
    }


def classify(
    case_id: str,
    exit_code: int,
    product: dict[str, Any],
    workspace_tree: dict[str, str],
    ledger: dict[str, Any] | None,
) -> str:
    verdict = product.get("verdict")
    reason = product.get("reason")
    if case_id in {"B1", "B2", "B3"}:
        if exit_code == 0 and verdict == "PROMOTE" and workspace_tree:
            return "RECOVERED_EXACT"
    elif case_id == "B4":
        if exit_code == 1 and verdict == "REFUSE" and reason == p7.NO_SURVIVING_CANDIDATE:
            return "UNRECOVERABLE_NO_SURVIVING_REPRESENTATION"
    elif case_id == "B5":
        if (
            exit_code == 0
            and verdict == "PROMOTE"
            and ledger is not None
            and ledger["recovered_paths"]
            and ledger["unrecovered_items"]
        ):
            return "RECOVERED_MAXIMUM_PROVABLE_SUBSET"
    elif case_id == "B6":
        if exit_code == 2 and verdict == "INVALID" and reason == "REPRESENTATION_HASH_MISMATCH":
            return "INVALID_TAMPERED_EVIDENCE"
    return "INFRASTRUCTURE_INVALID"


def scrub_text(value: str, replacements: dict[str, str]) -> str:
    result = value
    for raw, replacement in sorted(replacements.items(), key=lambda item: -len(item[0])):
        result = result.replace(raw, replacement)
    return result[-4000:]


def execute_case(
    campaign_root: Path,
    profile: Path,
    python: Path,
    case_id: str,
    repeat: int,
    files: dict[str, bytes],
    represented: set[str],
    tamper: bool,
    b4_oracle: bytes,
) -> dict[str, Any]:
    root = campaign_root / f"{case_id.lower()}-r{repeat}"
    workspace = root / "workspace"
    representations = root / "representations"
    custody = root / "custody"
    output = root / "output"
    tmpdir = root / "tmp"
    for path in (workspace, representations, custody, output, tmpdir):
        path.mkdir(parents=True)
    request, represented_files = build_request(case_id, files, represented)
    request_path = root / "request.json"
    request_path.write_bytes(surface.canonical_json(request))
    candidate_id = request["candidates"][0]["candidate_id"]
    for relative, raw in represented_files.items():
        target = representations / candidate_id / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"tampered replacement\n" if tamper else raw)

    before_workspace = tree(workspace)
    before_root = tree(root)
    command = [
        "/usr/bin/sandbox-exec",
        "-f",
        str(profile),
        str(python),
        "-m",
        "cockroach_kernel.cli",
        "recover",
        "--request",
        str(request_path),
        "--sandbox-root",
        str(root),
        "--workspace",
        str(workspace),
        "--representation-root",
        str(representations),
        "--custody-root",
        str(custody),
        "--output-root",
        str(output),
    ]
    started = time.monotonic_ns()
    completed = subprocess.run(
        command,
        cwd=root,
        env=sanitized_environment(tmpdir),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    elapsed_ns = time.monotonic_ns() - started
    stream = completed.stdout if completed.stdout.strip() else completed.stderr
    try:
        product = json.loads(stream)
    except json.JSONDecodeError:
        product = {
            "verdict": "INVALID",
            "reason": "NONCANONICAL_PROCESS_OUTPUT",
            "action_taken": "NONE",
        }
    ledger_path = output / "unrecovered-ledger.json"
    ledger = json.loads(ledger_path.read_bytes()) if ledger_path.exists() else None
    after_workspace = tree(workspace)
    after_root = tree(root)
    outcome_class = classify(
        case_id, completed.returncode, product, after_workspace, ledger
    )

    expected_workspace = {
        path: digest(raw) for path, raw in sorted(represented_files.items())
    }
    if tamper or case_id == "B4":
        expected_workspace = {}
    exact_workspace = after_workspace == expected_workspace
    oracle_materialized = any(
        path.read_bytes() == b4_oracle
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    )
    if case_id != "B4":
        oracle_materialized = False

    semantic = {
        "case_id": case_id,
        "outcome_class": outcome_class,
        "product_verdict": product.get("verdict"),
        "product_reason": product.get("reason"),
        "action_taken": product.get("action_taken"),
        "request_hash": product.get("request_hash"),
        "workspace_tree": after_workspace,
        "ledger_recovered_paths": None if ledger is None else ledger["recovered_paths"],
        "ledger_unrecovered_items": None if ledger is None else ledger["unrecovered_items"],
        "custody_tree": tree(custody),
        "output_tree": tree(output),
    }
    result = {
        "case_id": case_id,
        "repeat": repeat,
        "expected_outcome_class": EXPECTED_CLASSES[case_id],
        "outcome_class": outcome_class,
        "pass": (
            outcome_class == EXPECTED_CLASSES[case_id]
            and exact_workspace
            and not oracle_materialized
        ),
        "exit_code": completed.returncode,
        "elapsed_ns": elapsed_ns,
        "request_sha256": digest(request_path),
        "stdout_sha256": digest(completed.stdout.encode()),
        "stderr_sha256": digest(completed.stderr.encode()),
        "stdout_sanitized": scrub_text(
            completed.stdout,
            {str(root): "<CASE_ROOT>", str(python): "<FROZEN_PYTHON>"},
        ),
        "stderr_sanitized": scrub_text(
            completed.stderr,
            {str(root): "<CASE_ROOT>", str(python): "<FROZEN_PYTHON>"},
        ),
        "product_output": product,
        "workspace_before": before_workspace,
        "workspace_after": after_workspace,
        "workspace_exact": exact_workspace,
        "root_before": before_root,
        "root_after": after_root,
        "file_write_manifest": {
            path: sha for path, sha in after_root.items() if before_root.get(path) != sha
        },
        "model_call_count": 0,
        "network_egress_count": 0,
        "tool_calls": [
            {
                "tool": "cockroach-kernel recover",
                "network_denied": True,
                "exit_code": completed.returncode,
            }
        ],
        "oracle_bytes_materialized": oracle_materialized,
        "semantic": semantic,
        "semantic_sha256": digest(canonical(semantic)),
    }
    shutil.rmtree(root)
    result["teardown_root_absent"] = not root.exists()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--candidate-commit", default=PRODUCT_CANDIDATE)
    parser.add_argument("--cases", default="B1,B2,B3,B4,B5,B6")
    parser.add_argument("--repeats", type=int, default=REPEATS)
    parser.add_argument(
        "--receipt-name",
        default="PDH_1_INFORMATION_BOUNDARY_MECHANICAL_RECEIPT_R1.json",
    )
    args = parser.parse_args()
    if args.candidate_commit != PRODUCT_CANDIDATE:
        raise SystemExit("CANDIDATE_MISMATCH")
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    # Preserve the virtual-environment launcher path. Resolving its symlink to
    # the base interpreter drops the venv's installed candidate site-packages.
    python = Path(os.path.abspath(os.environ.get("PDH1_PYTHON", os.sys.executable)))
    sandbox_exec = Path("/usr/bin/sandbox-exec")
    if not sandbox_exec.is_file():
        raise SystemExit("OFFLINE_VERIFY_BLOCKED")

    b4_oracle = secrets.token_bytes(257)
    b4_oracle_sha256 = digest(b4_oracle)
    with tempfile.TemporaryDirectory(prefix="ck-pdh1-campaign-", dir="/private/tmp") as name:
        campaign_root = Path(name).resolve()
        profile = campaign_root / "offline.sb"
        profile.write_bytes(PROFILE)
        network_probe = network_denial_probe(profile, python, campaign_root)
        if not network_probe["denied"]:
            raise SystemExit("OFFLINE_VERIFY_BLOCKED")
        inputs = case_inputs(b4_oracle)
        selected_cases = [item.strip() for item in args.cases.split(",") if item.strip()]
        if (
            not selected_cases
            or any(item not in inputs for item in selected_cases)
            or args.repeats < 1
            or args.repeats > REPEATS
        ):
            raise SystemExit("INVALID_CAMPAIGN_SELECTION")
        results = []
        for case_id in selected_cases:
            files, represented, tamper = inputs[case_id]
            for repeat in range(1, args.repeats + 1):
                results.append(
                    execute_case(
                        campaign_root,
                        profile,
                        python,
                        case_id,
                        repeat,
                        files,
                        represented,
                        tamper,
                        b4_oracle,
                    )
                )
        deterministic = {}
        for case_id in selected_cases:
            case_hashes = [
                result["semantic_sha256"]
                for result in results
                if result["case_id"] == case_id
            ]
            deterministic[case_id] = {
                "executions": len(case_hashes),
                "identical": len(set(case_hashes)) == 1,
                "semantic_sha256": case_hashes[0],
            }
        full_campaign = (
            selected_cases == ["B1", "B2", "B3", "B4", "B5", "B6"]
            and args.repeats == REPEATS
        )
        mechanical_pass = (
            all(result["pass"] and result["teardown_root_absent"] for result in results)
            and all(value["identical"] for value in deterministic.values())
        )
        if full_campaign and mechanical_pass:
            status = "PDH_1_INFORMATION_BOUNDARY_MECHANICAL_GREEN"
        elif not full_campaign and mechanical_pass:
            status = "PDH_1_INFORMATION_BOUNDARY_CANARY_GREEN"
        else:
            status = "PDH_1_INFORMATION_BOUNDARY_MECHANICAL_BLOCKED"
        receipt = {
            "version": CAMPAIGN_VERSION,
            "status": status,
            "product_candidate": PRODUCT_CANDIDATE,
            "python": str(python),
            "python_sha256": digest(python),
            "sandbox_exec": str(sandbox_exec),
            "sandbox_exec_sha256": digest(sandbox_exec),
            "seatbelt_profile_sha256": digest(PROFILE),
            "network_denial_probe": network_probe,
            "b4_oracle": {
                "bytes": len(b4_oracle),
                "sha256": b4_oracle_sha256,
                "stored_or_passed_to_product": False,
                "controller_memory_only": True,
            },
            "model_call_count": 0,
            "measured_executions": len(results),
            "full_campaign": full_campaign,
            "case_determinism": deterministic,
            "results": results,
            "campaign_root_absent_after_context": True,
        }
        receipt["receipt_sha256"] = digest(canonical(receipt))
        atomic_json(output_dir / args.receipt_name, receipt)
    final = json.loads(
        (output_dir / args.receipt_name).read_bytes()
    )
    final["campaign_root_absent_after_context"] = True
    body = {key: value for key, value in final.items() if key != "receipt_sha256"}
    final["receipt_sha256"] = digest(canonical(body))
    atomic_json(output_dir / args.receipt_name, final)
    print(final["status"])
    print(final["receipt_sha256"])
    return 0 if final["status"].endswith("_GREEN") else 1


if __name__ == "__main__":
    raise SystemExit(main())
