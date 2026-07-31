#!/usr/bin/env python3
"""Build a deterministic credential-free PDH-3 RunPod transfer bundle."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import tarfile
from typing import Any


BASE = Path(__file__).resolve().parents[1]
FILES = (
    "post-dogfood/pdh3_scale_contract.py",
    "post-dogfood/run_pdh3_scale_campaign.py",
    "post-dogfood/run_pdh3_local_canary.py",
    "hardening-gate7/make_vectors.py",
    "hardening-gate7/run_campaign.py",
    "hardening-gate7/run_trial.py",
    "hardening-gate5/heldout_contract.py",
    "p4-verifier/verifier.py",
    "p7-recovery/records.py",
    "p9-cloud/migrations/001_cloud.sql",
    "p9-cloud/migrations/003_collision_safe_vector_digest.sql",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/cockroach",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/LICENSE",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/THIRD-PARTY-NOTICES.txt",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/lib/libgeos.so",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/lib/libgeos_c.so",
)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validate_relative(name: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\x00" in name:
        raise ValueError("BUNDLE_PATH_UNSAFE")


def build(output: Path, manifest_path: Path) -> dict[str, Any]:
    if output.exists() or manifest_path.exists():
        raise ValueError("OUTPUT_EXISTS")
    entries: list[dict[str, Any]] = []
    for relative in FILES:
        validate_relative(relative)
        path = BASE / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError("SOURCE_INVALID:" + relative)
        raw = path.read_bytes()
        entries.append(
            {
                "path": relative,
                "bytes": len(raw),
                "sha256": digest(raw),
                "mode": 0o755 if os.access(path, os.X_OK) else 0o644,
            }
        )
    manifest_body = {
        "version": "ck-pdh3-scale-bundle-manifest-v1",
        "credential_free": True,
        "synthetic_only": True,
        "files": entries,
        "file_count": len(entries),
        "source_set_sha256": digest(canonical(entries)),
    }
    manifest = {
        **manifest_body,
        "manifest_sha256": digest(canonical(manifest_body)),
    }
    manifest_raw = canonical(manifest)
    stream = io.BytesIO()
    with gzip.GzipFile(fileobj=stream, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w") as archive:
            for row in entries:
                raw = (BASE / row["path"]).read_bytes()
                info = tarfile.TarInfo(row["path"])
                info.size = len(raw)
                info.mode = row["mode"]
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                archive.addfile(info, io.BytesIO(raw))
            info = tarfile.TarInfo("PDH3_BUNDLE_MANIFEST.json")
            info.size = len(manifest_raw)
            info.mode = 0o644
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            archive.addfile(info, io.BytesIO(manifest_raw))
    archive_raw = stream.getvalue()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(archive_raw)
    receipt_body = {
        "version": "ck-pdh3-scale-bundle-receipt-v1",
        "archive": output.name,
        "archive_bytes": len(archive_raw),
        "archive_sha256": digest(archive_raw),
        "manifest": manifest,
    }
    receipt = {
        **receipt_body,
        "receipt_sha256": digest(canonical(receipt_body)),
    }
    manifest_path.write_bytes(canonical(receipt))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    arguments = parser.parse_args()
    print(
        canonical(build(arguments.output.resolve(), arguments.receipt.resolve())).decode()
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
