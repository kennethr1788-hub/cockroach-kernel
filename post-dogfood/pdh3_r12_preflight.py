#!/usr/bin/env python3
"""Deterministic custody and host-resource gates for PDH-3 R12 preflight."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import time
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
PLAN = "PDH3_R12_EXTENSIVE_PREFLIGHT_PLAN_20260802_R1.md"
PLAN_SHA256 = "a1214b4779fe1495de219ed0033421ac810390641cd97742deb61cd3957df3d9"
AMENDMENT = "PDH3_R12_PREFLIGHT_RESOURCE_BOUNDARY_AMENDMENT_20260802_R2.md"
AMENDMENT_SHA256 = "4bf4e47b79a66c672208cbd90f18ad31ff4f23400e833c728a189507dbb0e0b9"
PF2_AMENDMENT = "PDH3_R12_PREFLIGHT_PF2_RESOURCE_AMENDMENT_20260802_R3.md"
PF2_AMENDMENT_SHA256 = "0068c17d1c2e515181f209848bd383da08c33893b1e0fb738acefab49070a41e"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"

SOURCE_FILES = (
    PLAN,
    AMENDMENT,
    PF2_AMENDMENT,
    "PDH3_R12_PF2_LOCAL_RESOURCE_BLOCKER_RECEIPT_20260802.json",
    "PDH3_R12_PF2_AMENDMENT_REVIEW_RECEIPT_20260802_R2.json",
    "PDH3_PROVIDER_DOCUMENTATION_COMPLIANCE_AUDIT_20260802.md",
    "PDH_3_CONSECUTIVE_FAILURE_DEEP_AUDIT_20260802.md",
    "post-dogfood/pdh3_scale_contract.py",
    "post-dogfood/run_pdh3_scale_campaign.py",
    "post-dogfood/run_pdh3_traced.py",
    "post-dogfood/run_pdh3_local_canary.py",
    "post-dogfood/build_pdh3_scale_bundle.py",
    "post-dogfood/supervise_pdh3_scale_campaign.py",
    "post-dogfood/pdh3_r12_preflight.py",
    "post-dogfood/pdh3_r12_plan_ab.py",
    "post-dogfood/pdh3_r12_network_observer.py",
    "post-dogfood/pdh3_r12_checkpoint.py",
    "post-dogfood/pdh3_r12_preflight_supervisor.py",
    "post-dogfood/pdh3_r12_remote_preflight.py",
    "p9-cloud/migrations/001_cloud.sql",
)

CAMPAIGN_DIRS = (
    "ck-pdh3-scale-r8-relaunch-r3",
    "ck-pdh3-scale-r8-relaunch-r4",
    "ck-pdh3-scale-r8-relaunch-r5",
    "ck-pdh3-scale-r8-relaunch-r6",
    "ck-pdh3-scale-r8-relaunch-r7",
    "ck-pdh3-scale-r8-relaunch-r8",
    "ck-pdh3-scale-r9-relaunch-r1",
    "ck-pdh3-scale-r10-relaunch-r1",
    "ck-pdh3-scale-r11b-relaunch-r1",
)

EXPECTED_CONTRACT = {
    "MEASURED_SECONDS": 86_400,
    "CHECKPOINT_SECONDS": 300,
    "REQUIRED_CHECKPOINTS": 288,
    "QUERY_DURATION_SECONDS": 120,
    "TASKS": 500_000,
    "EVENTS_PER_TASK": 10,
    "RECEIPTS_PER_TASK": 2,
    "VECTORS": 250_000,
    "VERIFIER_EXECUTIONS": 9_976,
    "MAX_CONCURRENCY": 500,
    "P99_LIMIT_MS": 5_000.0,
    "PMAX_LIMIT_MS": 10_000.0,
    "TRACE_BYTES_LIMIT": 2 * 1024**3,
}

REMOTE_MINIMUM_RAM_BYTES = 94 * 1024**3
REMOTE_CONTAINER_DISK_BYTES = 250 * 1000**3
NODE_DECLARED_BYTES = 3 * (8 * 1024**3 + 8 * 1024**3)


class PreflightError(RuntimeError):
    """A fail-closed R12 preflight contract error."""


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(raw: bytes | Any) -> str:
    return hashlib.sha256(raw if isinstance(raw, bytes) else canonical(raw)).hexdigest()


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def validate_relative(relative: str) -> None:
    path = PurePosixPath(relative)
    if (
        not relative
        or "\x00" in relative
        or "\\" in relative
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
        or str(path) != relative
    ):
        raise PreflightError("UNSAFE_RELATIVE_PATH:" + digest(relative.encode()))


def binding(relative: str, *, root: Path = ROOT) -> dict[str, Any]:
    validate_relative(relative)
    path = root / relative
    if not path.is_file() or path.is_symlink():
        raise PreflightError("BOUND_FILE_INVALID:" + relative)
    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": file_sha256(path),
    }


def load_contract(root: Path = ROOT) -> Any:
    path = root / "post-dogfood/pdh3_scale_contract.py"
    spec = importlib.util.spec_from_file_location("pdh3_r12_contract", path)
    if spec is None or spec.loader is None:
        raise PreflightError("CONTRACT_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_contract(contract: Any) -> dict[str, Any]:
    observed = {key: getattr(contract, key, None) for key in EXPECTED_CONTRACT}
    mismatches = {
        key: {"expected": value, "observed": observed[key]}
        for key, value in EXPECTED_CONTRACT.items()
        if observed[key] != value
    }
    if mismatches:
        raise PreflightError("CONTRACT_DRIFT:" + digest(mismatches))
    return observed


def git_head(root: Path = ROOT) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    value = completed.stdout.strip()
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise PreflightError("GIT_HEAD_INVALID")
    return value


def campaign_file_bindings(root: Path = ROOT) -> list[dict[str, Any]]:
    base = root / ".pdh3-runtime/r8-campaigns"
    rows: list[dict[str, Any]] = []
    for campaign in CAMPAIGN_DIRS:
        directory = base / campaign
        if not directory.is_dir() or directory.is_symlink():
            raise PreflightError("CAMPAIGN_CUSTODY_MISSING:" + campaign)
        files: list[dict[str, Any]] = []
        for path in sorted(directory.rglob("*")):
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise PreflightError("CAMPAIGN_SYMLINK_FORBIDDEN:" + relative)
            if path.is_file():
                files.append(binding(relative, root=root))
            elif not path.is_dir():
                raise PreflightError("CAMPAIGN_SPECIAL_FILE_FORBIDDEN:" + relative)
        if not files:
            raise PreflightError("CAMPAIGN_CUSTODY_EMPTY:" + campaign)
        row = {
            "campaign_id": campaign,
            "files": files,
            "file_count": len(files),
            "file_set_sha256": digest(files),
        }
        rows.append({**row, "campaign_sha256": digest(row)})
    return rows


def freeze_manifest(root: Path = ROOT) -> dict[str, Any]:
    if file_sha256(root / PLAN) != PLAN_SHA256:
        raise PreflightError("PLAN_HASH_MISMATCH")
    if file_sha256(root / AMENDMENT) != AMENDMENT_SHA256:
        raise PreflightError("AMENDMENT_HASH_MISMATCH")
    if file_sha256(root / PF2_AMENDMENT) != PF2_AMENDMENT_SHA256:
        raise PreflightError("PF2_AMENDMENT_HASH_MISMATCH")
    contract = validate_contract(load_contract(root))
    sources = [binding(relative, root=root) for relative in SOURCE_FILES]
    campaigns = campaign_file_bindings(root)
    body = {
        "version": "pdh3-r12-pf0-custody-manifest-v1",
        "parent_commit": git_head(root),
        "product_candidate": PRODUCT_CANDIDATE,
        "plan_sha256": PLAN_SHA256,
        "amendment_sha256": AMENDMENT_SHA256,
        "pf2_amendment_sha256": PF2_AMENDMENT_SHA256,
        "contract": contract,
        "sources": sources,
        "source_set_sha256": digest(sources),
        "campaigns": campaigns,
        "campaign_set_sha256": digest(campaigns),
        "private_or_secret_payload_included": False,
        "raw_campaign_evidence_remote_transfer_allowed": False,
    }
    return {**body, "manifest_sha256": digest(body)}


def host_memory_bytes() -> int:
    if sys.platform == "darwin":
        completed = subprocess.run(
            ["sysctl", "-n", "hw.memsize"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return int(completed.stdout.strip())
    pages = os.sysconf("SC_PHYS_PAGES")
    page_size = os.sysconf("SC_PAGE_SIZE")
    return int(pages * page_size)


def resource_receipt(root: Path = ROOT) -> dict[str, Any]:
    memory = host_memory_bytes()
    disk = shutil.disk_usage(root)
    branch = (
        "PF3_LOCAL_FULL_CARDINALITY_ELIGIBLE"
        if memory >= REMOTE_MINIMUM_RAM_BYTES
        and disk.free >= REMOTE_CONTAINER_DISK_BYTES
        and memory > NODE_DECLARED_BYTES
        else "PF3_LOCAL_RESOURCE_BOUNDARY_GREEN"
    )
    body = {
        "version": "pdh3-r12-pf3-resource-receipt-v1",
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "plan_sha256": PLAN_SHA256,
        "amendment_sha256": AMENDMENT_SHA256,
        "host": {
            "physical_memory_bytes": memory,
            "logical_cpu_count": os.cpu_count(),
            "filesystem_total_bytes": disk.total,
            "filesystem_used_bytes": disk.used,
            "filesystem_free_bytes": disk.free,
        },
        "target": {
            "minimum_ram_bytes": REMOTE_MINIMUM_RAM_BYTES,
            "container_disk_bytes": REMOTE_CONTAINER_DISK_BYTES,
            "three_process_declared_cache_plus_sql_bytes": NODE_DECLARED_BYTES,
        },
        "branch": branch,
        "full_cardinality_attempted": False,
        "reduced_scale_treated_as_equivalent": False,
        "first_mandatory_full_cardinality_stage": "PF-5",
    }
    return {**body, "receipt_sha256": digest(body)}


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
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


def write_record(path: Path, value: dict[str, Any]) -> None:
    atomic_write(path, canonical(value))


def verify_record(path: Path, hash_field: str) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or canonical(value) != raw:
        raise PreflightError("RECORD_NON_CANONICAL")
    expected = value.get(hash_field)
    body = {key: item for key, item in value.items() if key != hash_field}
    if expected != digest(body):
        raise PreflightError("RECORD_HASH_INVALID")
    return value


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    subparsers = value.add_subparsers(dest="command", required=True)
    freeze = subparsers.add_parser("freeze")
    freeze.add_argument("--output", type=Path, required=True)
    resource = subparsers.add_parser("resource")
    resource.add_argument("--output", type=Path, required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--record", type=Path, required=True)
    verify.add_argument(
        "--hash-field",
        choices=("manifest_sha256", "receipt_sha256"),
        required=True,
    )
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    if args.command == "freeze":
        value = freeze_manifest()
        write_record(args.output, value)
    elif args.command == "resource":
        value = resource_receipt()
        write_record(args.output, value)
    else:
        value = verify_record(args.record, args.hash_field)
    print(canonical(value).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
