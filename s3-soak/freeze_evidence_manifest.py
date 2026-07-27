#!/usr/bin/env python3
"""Freeze a deterministic SHA-256 manifest for one completed S3 evidence root."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re


ROOT_RE = re.compile(r"^/workspace/ck-s3-[A-Za-z0-9._-]{1,48}/production$")


class ManifestFailure(RuntimeError):
    pass


def file_sha256(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def atomic_write(path: Path, value: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise ManifestFailure("TEMP_OUTPUT_EXISTS")
    path.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open("xb") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def freeze(root: Path, output: Path) -> dict[str, int | str]:
    resolved_root = root.resolve(strict=True)
    resolved_output_parent = output.parent.resolve(strict=True)
    if not ROOT_RE.fullmatch(resolved_root.as_posix()):
        raise ManifestFailure("ROOT_OUTSIDE_CAMPAIGN")
    if resolved_output_parent != resolved_root.parent:
        raise ManifestFailure("OUTPUT_PARENT_INVALID")
    if output.name != "production-tree.sha256" or output.exists():
        raise ManifestFailure("OUTPUT_INVALID")
    records: list[bytes] = []
    total_bytes = 0
    file_count = 0
    for path in sorted(resolved_root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise ManifestFailure("SYMLINK_REJECTED")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ManifestFailure("NONREGULAR_FILE_REJECTED")
        relative = path.relative_to(resolved_root)
        if any(part in {"", ".", ".."} for part in relative.parts):
            raise ManifestFailure("RELATIVE_PATH_INVALID")
        digest, size = file_sha256(path)
        records.append(f"{digest}  production/{relative.as_posix()}\n".encode("utf-8"))
        total_bytes += size
        file_count += 1
    if file_count == 0:
        raise ManifestFailure("EVIDENCE_EMPTY")
    value = b"".join(records)
    atomic_write(output, value)
    return {
        "version": "s3-production-manifest-v1",
        "files": file_count,
        "bytes": total_bytes,
        "manifest_sha256": hashlib.sha256(value).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = freeze(args.root, args.output)
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED", "reason": type(exc).__name__},
                         sort_keys=True, separators=(",", ":")))
        return 1
    print(json.dumps({**result, "status": "GREEN"}, sort_keys=True,
                     separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
