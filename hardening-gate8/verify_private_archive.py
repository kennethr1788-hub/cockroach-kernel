#!/usr/bin/env python3
"""Verify every member of the local-only Gate 8 private archive."""

from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / ".hardening-runtime" / "gate8-private" / "cockroach-kernel-private-raw-evidence-r1.tar"
MANIFEST = ROOT / ".hardening-runtime" / "gate8-private" / "source-manifest-r1.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_by_path = {item["path"]: item for item in expected["files"]}
    verified = 0
    with tarfile.open(ARCHIVE, "r") as archive:
        names = archive.getnames()
        if len(names) != len(set(names)):
            raise SystemExit("DUPLICATE_ARCHIVE_MEMBER")
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts:
                raise SystemExit(f"UNSAFE_ARCHIVE_MEMBER:{name}")
        embedded = archive.extractfile("_archive/source-manifest-r1.json")
        if embedded is None or embedded.read() != MANIFEST.read_bytes():
            raise SystemExit("EMBEDDED_MANIFEST_MISMATCH")
        actual_sources = set(names) - {"_archive/source-manifest-r1.json"}
        if actual_sources != set(expected_by_path):
            raise SystemExit("ARCHIVE_MEMBER_SET_MISMATCH")
        for name, record in expected_by_path.items():
            handle = archive.extractfile(name)
            if handle is None:
                raise SystemExit(f"MISSING_ARCHIVE_MEMBER:{name}")
            data = handle.read()
            if len(data) != record["bytes"] or sha256(data) != record["sha256"]:
                raise SystemExit(f"ARCHIVE_MEMBER_HASH_MISMATCH:{name}")
            verified += 1
    print(json.dumps({
        "archive_sha256": sha256(ARCHIVE.read_bytes()),
        "file_count": verified,
        "source_manifest_sha256": sha256(MANIFEST.read_bytes()),
        "status": "GREEN",
        "version": "hardening-gate8-private-archive-verification-v1",
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
