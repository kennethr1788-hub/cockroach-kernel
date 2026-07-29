#!/usr/bin/env python3
"""Run and freeze Gate 7B local mechanical evidence before judge preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


BASE = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
PUBLIC_SEED_HEX = "0123456789abcdef" * 4

HARNESS_FILES = (
    "hardening-gate5/heldout_contract.py",
    "hardening-gate7/expanded_contract.py",
    "hardening-gate7/generate_expanded_inputs.py",
    "hardening-gate7/run_expanded_campaign.py",
    "hardening-gate7/run_expanded_case.py",
    "hardening-gate7/run4_evidence_custody.py",
    "hardening-gate7/run4_track_gate.py",
    "hardening-gate7/local_collision_migration_proof.sh",
    "hardening-gate7/score_expanded_campaign.py",
    "hardening-gate7/surface_cases.py",
    "hardening-gate7/prepare_hidden_campaign.py",
    "hardening-gate7/live_bulk_controller.py",
    "hardening-gate7/preflight_live_check.py",
    "hardening-gate7/build_expanded_bundle.py",
    "hardening-gate7/freeze_expanded_preflight.py",
    "hardening-gate7/build_expanded_preflight_packet.py",
    "hardening-gate7/profile_memory.py",
    "hardening-gate7/make_vectors.py",
    "hardening-gate7/run_campaign.py",
    "hardening-gate7/run_trial.py",
    "hardening-gate7/test_expanded_gate7.py",
    "hardening-gate7/test_gate7.py",
    "p9-cloud/migrations/001_cloud.sql",
    "p9-cloud/migrations/003_collision_safe_vector_digest.sql",
    "p9-cloud/test_contract_artifacts.py",
    "hardening-gate6/seccomp_exec.py",
    "s2-soak/lifecycle_guard.py",
    "s2-soak/run_soak.py",
    "s3-soak/protocol.py",
    "s3-soak/worker.py",
    "s3-soak/host_coordinator.py",
    "s3-soak/cloud_adapter.py",
    "s3-soak/remote_bridge.py",
    "s3-soak/coordinator_guard.py",
    "HARDENING_GATE7_EXPANDED_THRESHOLDS_R1.json",
    "HARDENING_GATE7_RUN5_SCHEDULE_R1.json",
    "HARDENING_GATE7_EXPANDED_EXECUTION_WIRING_R1.md",
)
PRODUCT_FILES = (
    "cockroach_kernel/recovery_surface.py",
    "p4-verifier/verifier.py",
    "p7-recovery/fresh_context.py",
    "p7-recovery/records.py",
    "p9-cloud/live_completion.py",
    "p9-cloud/records.py",
)


class FreezeError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def run(command: list[str], *, timeout: int = 180, allowed: set[int] | None = None) -> dict[str, Any]:
    result = subprocess.run(
        command, cwd=BASE, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        check=False, timeout=timeout,
    )
    accepted = allowed if allowed is not None else {0}
    if result.returncode not in accepted:
        raise FreezeError(
            "COMMAND_FAILED:" + command[0] + ":" + str(result.returncode) + ":" + digest(result.stdout)
        )
    return {
        "command": command,
        "exit": result.returncode,
        "output_sha256": digest(result.stdout),
        "output_bytes": len(result.stdout),
    }


def file_record(relative: str) -> dict[str, Any]:
    path = BASE / relative
    raw = path.read_bytes()
    return {"path": relative, "sha256": digest(raw), "bytes": len(raw)}


def contract_hash(plan: Path, prompt: Path) -> str:
    rows = [
        {"label": "plan", "sha256": digest(plan.read_bytes())},
        {"label": "prompt", "sha256": digest(prompt.read_bytes())},
        file_record("HARDENING_GATE7_EXPANDED_THRESHOLDS_R1.json"),
        file_record("HARDENING_GATE7_RUN5_SCHEDULE_R1.json"),
    ]
    return digest(canonical(rows))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--source-bindings", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--runpodctl", type=Path, required=True)
    parser.add_argument("--runpodctl-sha256", required=True)
    args = parser.parse_args()
    output = args.output_root.resolve()
    if output.exists():
        raise FreezeError("OUTPUT_ROOT_EXISTS")
    output.mkdir(parents=True)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=BASE, text=True).strip()
    if subprocess.run(["git", "merge-base", "--is-ancestor", CANDIDATE, head], cwd=BASE).returncode:
        raise FreezeError("CANDIDATE_NOT_ANCESTOR")
    changed_product = subprocess.check_output(
        ["git", "diff", "--name-only", CANDIDATE, "--", *PRODUCT_FILES],
        cwd=BASE, text=True,
    ).splitlines()
    if changed_product:
        raise FreezeError("FROZEN_PRODUCT_CHANGED")
    current_campaign_root = BASE / ".hardening-runtime/gate7-r5"
    if current_campaign_root.exists() and list(current_campaign_root.rglob("master-seed.bin")):
        raise FreezeError("PREMATURE_HIDDEN_SEED_PRESENT")
    plan = args.plan.resolve()
    prompt = args.prompt.resolve()
    frozen_contract = contract_hash(plan, prompt)
    source_body = {
        "version": "hardening-gate7-expanded-source-bindings-v1",
        "candidate_commit": CANDIDATE,
        "orchestration_head": head,
        "preflight_contract_sha256": frozen_contract,
        "product_files": [file_record(name) for name in PRODUCT_FILES],
        "harness_files": [file_record(name) for name in HARNESS_FILES],
    }
    source = dict(source_body, source_bindings_sha256=digest(canonical(source_body)))
    atomic_write(args.source_bindings.resolve(), canonical(source))

    tests = run([
        sys.executable, "-m", "unittest", "discover", "-s", "hardening-gate7",
        "-p", "test*.py", "-v",
    ], timeout=180)
    atomic_write(output / "unit-tests-receipt.json", canonical(tests))

    p9_tests = run([
        sys.executable, "-m", "unittest", "p9-cloud/test_contract_artifacts.py", "-v",
    ], timeout=120)
    atomic_write(output / "p9-contract-tests-receipt.json", canonical(p9_tests))

    migration_proof = run([
        "/bin/bash", str(HERE / "local_collision_migration_proof.sh"),
    ], timeout=180)
    atomic_write(output / "collision-migration-proof-receipt.json", canonical(migration_proof))

    with tempfile.TemporaryDirectory(prefix="ck-g7-preflight-") as temporary:
        temporary_root = Path(temporary)
        seed = temporary_root / "public-seed.hex"
        atomic_write(seed, (PUBLIC_SEED_HEX + "\n").encode("ascii"))
        generated = temporary_root / "generated"
        raw = temporary_root / "raw"
        scored = temporary_root / "scored"
        canary_packet = "2" * 64
        run([
            sys.executable, str(HERE / "generate_expanded_inputs.py"),
            "--seed-file", str(seed), "--campaign-id", "ck-g7-public-preflight-r1",
            "--output-root", str(generated),
        ])
        run([
            "/usr/bin/python3", str(HERE / "run_expanded_campaign.py"),
            "--input-manifest", str(generated / "input-manifest.json"),
            "--input-root", str(generated / "inputs"),
            "--python-bin", "/usr/bin/python3", "--output-root", str(raw),
            "--packet-sha256", canary_packet,
            "--source-bindings-sha256", source["source_bindings_sha256"],
        ], timeout=180)
        run([
            "/usr/bin/python3", str(HERE / "score_expanded_campaign.py"),
            "--campaign-root", str(raw),
            "--oracle", str(generated / "sealed-oracle/oracle.json"),
            "--input-manifest", str(generated / "input-manifest.json"),
            "--output-root", str(scored),
        ])
        aggregate = json.loads((scored / "aggregate.json").read_bytes())
        if not aggregate.get("green") or aggregate.get("pass_count") != 84:
            raise FreezeError("PUBLIC_CANARY_NOT_GREEN")
        atomic_write(output / "public-canary-aggregate.json", canonical(aggregate))

    profile_path = output / "memory-profile.json"
    run([
        "/usr/bin/python3", str(HERE / "profile_memory.py"),
        "--tasks", "2000", "--events-per-task", "10",
        "--receipts-per-task", "2", "--vectors-per-task", "10",
        "--query-samples", "200", "--end-to-end-calls", "12",
        "--concurrency", "4", "--output", str(profile_path),
    ])
    bulk_root = output / "bulk-sql-public"
    run([
        sys.executable, str(HERE / "live_bulk_controller.py"),
        "--campaign-id", "ck-g7r5-public-preflight",
        "--generated-root", str(bulk_root), "--generate-only",
    ])

    bundle_root = output / "bundle"
    bundle = run([
        sys.executable, str(HERE / "build_expanded_bundle.py"),
        "--output-root", str(bundle_root),
        "--contract-sha256", frozen_contract,
    ], timeout=300)
    atomic_write(output / "bundle-build-receipt.json", canonical(bundle))
    scan_root = output / "bundle-scan"
    scan_root.mkdir()
    run(["/usr/bin/tar", "-xzf", str(bundle_root / "gate7-worker-bundle.tgz"),
         "-C", str(scan_root)], timeout=300)
    with tempfile.TemporaryDirectory(prefix="ck-g7-extracted-smoke-") as temporary:
        smoke_root = Path(temporary)
        extracted = scan_root / "bundle"
        seed = smoke_root / "public-seed.hex"
        atomic_write(seed, (PUBLIC_SEED_HEX + "\n").encode("ascii"))
        generated = smoke_root / "generated"
        run([
            sys.executable,
            str(extracted / "hardening-gate7/generate_expanded_inputs.py"),
            "--seed-file", str(seed),
            "--campaign-id", "ck-g7-extracted-bundle-smoke-r1",
            "--output-root", str(generated),
        ], timeout=120)
        observations: dict[str, dict[str, Any]] = {}
        for order, slot_id in enumerate(("B-1-2", "D-FILE-LP1"), start=1):
            observation = smoke_root / f"{slot_id}.json"
            run([
                sys.executable,
                str(extracted / "hardening-gate7/run_expanded_case.py"),
                "--case", str(generated / "inputs" / f"{slot_id}.json"),
                "--trial-root", str(smoke_root / f"trial-{order}"),
                "--output", str(observation),
                "--packet-sha256", "2" * 64,
                "--execution-order", str(order),
                "--source-bindings-sha256", source["source_bindings_sha256"],
            ], timeout=120)
            observations[slot_id] = json.loads(observation.read_bytes())["observation"]
        expected = {
            "B-1-2": ("PROMOTE", "MAX_PROVEN_PREFIX"),
            "D-FILE-LP1": ("INVALID", "AGGREGATE_LIMIT_EXCEEDED"),
        }
        for slot_id, pair in expected.items():
            observed = observations[slot_id]
            if (observed["observed_verdict"], observed["observed_reason"]) != pair:
                raise FreezeError("EXTRACTED_BUNDLE_CANARY_MISMATCH:" + slot_id)
        smoke_body = {
            "version": "hardening-gate7-extracted-bundle-smoke-v1",
            "archive_sha256": digest((bundle_root / "gate7-worker-bundle.tgz").read_bytes()),
            "required_dependency": "hardening-gate5/heldout_contract.py",
            "required_dependency_sha256": digest(
                (extracted / "hardening-gate5/heldout_contract.py").read_bytes()
            ),
            "generator_from_extracted_bundle": True,
            "known_canaries_measured": False,
            "results": {
                slot_id: {
                    "verdict": observations[slot_id]["observed_verdict"],
                    "reason": observations[slot_id]["observed_reason"],
                }
                for slot_id in sorted(observations)
            },
        }
        smoke_receipt = dict(
            smoke_body,
            receipt_sha256=digest(canonical(smoke_body)),
        )
        atomic_write(output / "extracted-bundle-smoke-receipt.json", canonical(smoke_receipt))
    gitleaks = run([
        str(Path("/Users/kennethruedas/.local/bin/gitleaks")), "detect",
        "--source", str(scan_root), "--no-git", "--redact", "--exit-code", "1",
    ], timeout=300)
    detect = run([
        str(Path("/Users/kennethruedas/.local/bin/detect-secrets")), "scan",
        str(scan_root / "bundle"), "--all-files",
    ], timeout=300)
    atomic_write(output / "gitleaks-receipt.json", canonical(gitleaks))
    atomic_write(output / "detect-secrets-receipt.json", canonical(detect))
    shutil.rmtree(scan_root)

    guard = run([sys.executable, "s2-soak/prove_guard.py"], timeout=60)
    coordinator_guard = run([sys.executable, "s3-soak/prove_coordinator_guard.py"], timeout=60)
    atomic_write(output / "lifecycle-guard-receipt.json", canonical(guard))
    atomic_write(output / "coordinator-guard-receipt.json", canonical(coordinator_guard))

    runpodctl = args.runpodctl.resolve()
    if digest(runpodctl.read_bytes()) != args.runpodctl_sha256:
        raise FreezeError("RUNPODCTL_HASH_INVALID")
    inventory = run([str(runpodctl), "pod", "list"], timeout=60)
    if inventory["output_sha256"] != digest(b"[]\n"):
        raise FreezeError("RUNPOD_ACTIVE_INVENTORY_NOT_EMPTY")
    atomic_write(output / "runpod-inventory-receipt.json", canonical(inventory))

    # Preserve the read-only cloud readiness receipt. An expired AWS session is
    # a launch-time human action, not permission to weaken or skip the live track.
    live_readiness = BASE / ".hardening-runtime/gate7-r5/live-readiness-freeze.json"
    live_readiness.parent.mkdir(parents=True, exist_ok=True)
    live = run([
        sys.executable, str(HERE / "preflight_live_check.py"),
        "--config", str(BASE / ".s3-runtime/live-config.json"),
        "--output", str(live_readiness),
    ], timeout=90, allowed={0, 3})
    readiness_record = json.loads(live_readiness.read_bytes())
    atomic_write(output / "live-readiness-redacted.json", canonical(readiness_record))

    files = {
        str(path.relative_to(output)): digest(path.read_bytes())
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name != "gate7-worker-bundle.tgz"
    }
    receipt_body = {
        "version": "hardening-gate7-expanded-local-preflight-v1",
        "candidate_commit": CANDIDATE,
        "orchestration_head": head,
        "preflight_contract_sha256": frozen_contract,
        "source_bindings_sha256": source["source_bindings_sha256"],
        "hidden_seed_exists": False,
        "runpod_created": False,
        "active_runpod_inventory": [],
        "unit_tests_green": True,
        "public_canary_passes": aggregate["pass_count"],
        "public_canary_false_promotions": aggregate["false_promotions"],
        "public_canary_mutation_after_refusal_or_invalid": aggregate[
            "mutation_after_refusal_or_invalid"
        ],
        "transfer_scan_green": True,
        "extracted_bundle_canaries_green": True,
        "lifecycle_guard_green": True,
        "coordinator_guard_green": True,
        "cockroach_readiness": readiness_record.get("cockroach_reachable"),
        "aws_readiness": readiness_record.get("status"),
        "aws_login_required_before_campaign_ready": readiness_record.get("status") != "GREEN",
        "files": files,
    }
    receipt = dict(receipt_body, receipt_sha256=digest(canonical(receipt_body)))
    atomic_write(args.receipt.resolve(), canonical(receipt))
    print(canonical({
        "status": "GATE7B_LOCAL_GREEN_AWS_LOGIN_PENDING",
        "receipt_sha256": receipt["receipt_sha256"],
        "source_bindings_sha256": source["source_bindings_sha256"],
        "preflight_contract_sha256": frozen_contract,
        "live_check_exit": live["exit"],
    }).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
