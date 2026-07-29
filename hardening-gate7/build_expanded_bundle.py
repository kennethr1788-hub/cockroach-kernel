#!/usr/bin/env python3
"""Build a deterministic, allowlisted, synthetic-only Gate 7 worker archive."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tarfile
from typing import Any


BASE = Path(__file__).resolve().parents[1]
CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
LINUX_ARCHIVE = Path(
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64.tgz"
)
LINUX_ARCHIVE_SHA256 = "3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3"

EXACT_FILES = (
    "cockroach_kernel/__init__.py",
    "cockroach_kernel/recovery_surface.py",
    "hardening-gate5/heldout_contract.py",
    "hardening-gate6/seccomp_exec.py",
    "hardening-gate7/expanded_contract.py",
    "hardening-gate7/generate_expanded_inputs.py",
    "hardening-gate7/live_bulk_controller.py",
    "hardening-gate7/make_vectors.py",
    "hardening-gate7/prepare_hidden_campaign.py",
    "hardening-gate7/run_expanded_campaign.py",
    "hardening-gate7/run_expanded_case.py",
    "hardening-gate7/run4_evidence_custody.py",
    "hardening-gate7/run4_track_gate.py",
    "hardening-gate7/run_trial.py",
    "hardening-gate7/score_expanded_campaign.py",
    "hardening-gate7/surface_cases.py",
    "HARDENING_GATE7_RUN5_THRESHOLDS_R2.json",
    "s2-soak/run_soak.py",
    "s3-soak/protocol.py",
    "s3-soak/hardening.py",
    "s3-soak/cloud_adapter.py",
    "s3-soak/freeze_evidence_manifest.py",
    "s3-soak/worker.py",
    "p9-cloud/context_vector.py",
    "p9-cloud/records.py",
    "p9-cloud/migrations/001_cloud.sql",
    "p9-cloud/migrations/003_collision_safe_vector_digest.sql",
    str(LINUX_ARCHIVE),
)
TREE_ROOTS = (
    "p3-ledger/migrations",
    "p4-verifier",
    "p5-lanes",
    "p6-quorum",
    "p7-recovery",
)
ALLOWED_SUFFIXES = {".py", ".sql", ".json", ".md", ".tgz"}
FORBIDDEN_PATTERNS = (
    re.compile(rb"/Users/kennethruedas(?:/|\\b)"),
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"(?i)(?:aws_secret_access_key|api[_-]?key|password)\s*[:=]\s*['\"]?[A-Za-z0-9+/=_-]{16,}"),
)


class BundleError(RuntimeError):
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


def collect() -> list[Path]:
    relative: set[Path] = {Path(name) for name in EXACT_FILES}
    for root_name in TREE_ROOTS:
        root = BASE / root_name
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in ALLOWED_SUFFIXES and "__pycache__" not in path.parts:
                relative.add(path.relative_to(BASE))
    paths = sorted(relative, key=lambda item: item.as_posix())
    for relative_path in paths:
        absolute = (BASE / relative_path).resolve()
        if not absolute.is_file() or not absolute.is_relative_to(BASE.resolve()):
            raise BundleError("ALLOWLIST_PATH_INVALID:" + relative_path.as_posix())
        if absolute.is_symlink():
            raise BundleError("ALLOWLIST_SYMLINK_FORBIDDEN")
    return paths


def scan(paths: list[Path]) -> list[dict[str, str]]:
    receipts: list[dict[str, str]] = []
    for relative in paths:
        raw = (BASE / relative).read_bytes()
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(raw):
                raise BundleError("FORBIDDEN_CONTENT:" + relative.as_posix())
        receipts.append({
            "path": relative.as_posix(),
            "sha256": digest(raw),
            "bytes": str(len(raw)),
            "mode": "0755" if relative.suffix == ".py" else "0644",
        })
    archive_row = next(row for row in receipts if row["path"] == LINUX_ARCHIVE.as_posix())
    if archive_row["sha256"] != LINUX_ARCHIVE_SHA256:
        raise BundleError("COCKROACH_ARCHIVE_HASH_INVALID")
    return receipts


def make_archive(paths: list[Path], output: Path) -> None:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for relative in paths:
            raw = (BASE / relative).read_bytes()
            info = tarfile.TarInfo("bundle/" + relative.as_posix())
            info.size = len(raw)
            info.mode = 0o755 if relative.suffix == ".py" else 0o644
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = "root"
            info.gname = "root"
            archive.addfile(info, io.BytesIO(raw))
    compressed = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=compressed, mtime=0, compresslevel=9) as handle:
        handle.write(buffer.getvalue())
    atomic_write(output, compressed.getvalue())


def validate_archive(output: Path, receipts: list[dict[str, str]]) -> dict[str, Any]:
    expected = {"bundle/" + row["path"]: row for row in receipts}
    observed: dict[str, dict[str, str]] = {}
    with tarfile.open(output, "r:gz") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)):
            raise BundleError("ARCHIVE_DUPLICATE_MEMBER")
        for member in members:
            if not member.isfile() or member.issym() or member.islnk():
                raise BundleError("ARCHIVE_NONREGULAR_MEMBER")
            if member.name not in expected:
                raise BundleError("ARCHIVE_UNEXPECTED_MEMBER")
            handle = archive.extractfile(member)
            if handle is None:
                raise BundleError("ARCHIVE_MEMBER_UNREADABLE")
            raw = handle.read()
            row = expected[member.name]
            mode = format(member.mode & 0o777, "04o")
            if (str(len(raw)) != row["bytes"] or digest(raw) != row["sha256"] or
                    mode != row["mode"]):
                raise BundleError("ARCHIVE_MEMBER_BINDING_INVALID")
            observed[member.name] = {
                "sha256": digest(raw), "bytes": str(len(raw)), "mode": mode,
            }
    if set(observed) != set(expected):
        raise BundleError("ARCHIVE_MEMBER_MISSING")
    helper = "bundle/s3-soak/freeze_evidence_manifest.py"
    if helper not in observed:
        raise BundleError("PACKAGED_MANIFEST_HELPER_MISSING")
    return {
        "file_count": len(observed),
        "tree_sha256": digest(canonical(observed)),
        "manifest_helper": observed[helper],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--contract-sha256", required=True)
    args = parser.parse_args()
    if len(args.contract_sha256) != 64:
        raise BundleError("CONTRACT_HASH_INVALID")
    output = args.output_root.resolve()
    if output.exists():
        raise BundleError("OUTPUT_ROOT_EXISTS")
    output.mkdir(parents=True)
    paths = collect()
    rows = scan(paths)
    tree_body = {
        "version": "hardening-gate7-transfer-tree-v1",
        "candidate_commit": CANDIDATE,
        "preflight_contract_sha256": args.contract_sha256,
        "synthetic_only": True,
        "credential_files": 0,
        "private_paths": 0,
        "files": rows,
    }
    tree = dict(tree_body, tree_sha256=digest(canonical(tree_body)))
    atomic_write(output / "PAYLOAD_TREE.json", canonical(tree))
    archive = output / "gate7-worker-bundle.tgz"
    make_archive(paths, archive)
    archive_validation = validate_archive(archive, rows)
    manifest_body = {
        "version": "hardening-gate7-transfer-manifest-v1",
        "candidate_commit": CANDIDATE,
        "preflight_contract_sha256": args.contract_sha256,
        "payload_tree_sha256": tree["tree_sha256"],
        "archive_sha256": digest(archive.read_bytes()),
        "archive_bytes": archive.stat().st_size,
        "file_count": len(rows),
        "archive_validation": archive_validation,
        "runtime_archive_sha256": LINUX_ARCHIVE_SHA256,
        "worker_credentials": False,
        "persistent_volume": False,
        "network_volume": False,
    }
    manifest = dict(manifest_body, manifest_sha256=digest(canonical(manifest_body)))
    atomic_write(output / "TRANSFER_MANIFEST.json", canonical(manifest))
    print(canonical(manifest).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
