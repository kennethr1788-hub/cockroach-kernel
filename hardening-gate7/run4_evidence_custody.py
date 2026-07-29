#!/usr/bin/env python3
"""Seal Track 1 evidence before later Run 4 tracks can begin."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import time
from typing import Any


CAMPAIGN_RE = re.compile(r"^ck-g7r4-[A-Za-z0-9-]+$")


class CustodyError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(raw: bytes | Any) -> str:
    return hashlib.sha256(raw if isinstance(raw, bytes) else canonical(raw)).hexdigest()


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise CustodyError("OUTPUT_EXISTS")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(canonical(value))
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


def validate_receipt(receipt: dict[str, Any]) -> None:
    body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if receipt.get("receipt_sha256") != digest(body):
        raise CustodyError("RECEIPT_HASH_INVALID")


def seal(archive: Path, receipt_path: Path, campaign_id: str) -> dict[str, Any]:
    if not CAMPAIGN_RE.fullmatch(campaign_id):
        raise CustodyError("CAMPAIGN_ID_INVALID")
    archive = archive.resolve()
    receipt_path = receipt_path.resolve()
    if archive.is_symlink() or not archive.is_file():
        raise CustodyError("ARCHIVE_INVALID")
    if archive.parent != receipt_path.parent:
        raise CustodyError("CUSTODY_ROOT_MISMATCH")
    raw = archive.read_bytes()
    body = {
        "version": "hardening-gate7-run4-track1-custody-v1",
        "campaign_id": campaign_id,
        "archive_name": archive.name,
        "archive_bytes": len(raw),
        "archive_sha256": digest(raw),
        "archive_mode_after": "0000",
        "extracted_before_track2": False,
        "status": "SEALED",
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    receipt = dict(body, receipt_sha256=digest(body))
    atomic_write(receipt_path, receipt)
    os.chmod(archive, 0)
    if stat.S_IMODE(archive.stat().st_mode) != 0:
        raise CustodyError("ARCHIVE_SEAL_FAILED")
    return receipt


def unseal(archive: Path, receipt_path: Path, output: Path) -> dict[str, Any]:
    archive = archive.resolve()
    receipt_path = receipt_path.resolve()
    output = output.resolve()
    receipt = json.loads(receipt_path.read_bytes())
    validate_receipt(receipt)
    if receipt.get("status") != "SEALED" or receipt.get("archive_name") != archive.name:
        raise CustodyError("CUSTODY_LINK_INVALID")
    if archive.parent != receipt_path.parent or stat.S_IMODE(archive.stat().st_mode) != 0:
        raise CustodyError("ARCHIVE_NOT_SEALED")
    os.chmod(archive, stat.S_IRUSR)
    raw = archive.read_bytes()
    if len(raw) != receipt["archive_bytes"] or digest(raw) != receipt["archive_sha256"]:
        raise CustodyError("ARCHIVE_HASH_MISMATCH")
    body = {
        "version": "hardening-gate7-run4-track1-unseal-v1",
        "campaign_id": receipt["campaign_id"],
        "custody_receipt_sha256": receipt["receipt_sha256"],
        "archive_sha256": receipt["archive_sha256"],
        "archive_bytes": receipt["archive_bytes"],
        "status": "UNSEALED_HASH_VERIFIED",
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    result = dict(body, receipt_sha256=digest(body))
    atomic_write(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    seal_parser = subparsers.add_parser("seal")
    seal_parser.add_argument("--archive", type=Path, required=True)
    seal_parser.add_argument("--receipt", type=Path, required=True)
    seal_parser.add_argument("--campaign-id", required=True)
    unseal_parser = subparsers.add_parser("unseal")
    unseal_parser.add_argument("--archive", type=Path, required=True)
    unseal_parser.add_argument("--receipt", type=Path, required=True)
    unseal_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = (seal(args.archive, args.receipt, args.campaign_id)
             if args.command == "seal"
             else unseal(args.archive, args.receipt, args.output))
    print(canonical(value).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
