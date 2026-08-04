#!/usr/bin/env python3
"""Build a deterministic Lambda zip for the Cockroach-backed canary.

Dependencies are supplied by a caller-owned temporary vendor directory.  This
builder never downloads packages, reads credentials, follows symlinks, or
includes VCS/private runtime state.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import zipfile


SOURCE_FILES = (
    ("live_lambda_handler.py", "live_lambda_handler.py"),
    ("cockroach_kernel", "cockroach_kernel"),
    ("p7-recovery", "p7_runtime"),
    ("p9-cloud", "p9_runtime"),
    ("p4-verifier", "verifier_runtime"),
)
DEPENDENCY_TOP_LEVEL = {
    "pg8000", "scramp", "asn1crypto", "dateutil", "six.py",
    "boto3", "botocore", "jmespath", "s3transfer", "urllib3.py",
}
DEPENDENCY_DIST_PREFIXES = (
    "pg8000-", "scramp-", "asn1crypto-", "python_dateutil-", "six-",
    "boto3-", "botocore-", "jmespath-", "s3transfer-", "urllib3-"
)


def _files(root: Path, relative: str, destination: str) -> list[tuple[str, Path]]:
    source = root / relative
    if source.is_file():
        return [(destination, source)]
    if not source.is_dir() or source.is_symlink():
        raise RuntimeError(f"SOURCE_ROOT_INVALID:{relative}")
    result = []
    for path in sorted(source.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        if "__pycache__" in path.parts or path.name.startswith("test_"):
            continue
        source_name = path.relative_to(root).as_posix()
        relative_name = path.relative_to(source).as_posix()
        result.append(((Path(destination) / relative_name).as_posix(), path))
    return result


def _dependency_files(vendor: Path) -> list[tuple[str, Path]]:
    if not vendor.is_dir() or vendor.is_symlink():
        raise RuntimeError("VENDOR_ROOT_INVALID")
    result = []
    for path in sorted(vendor.rglob("*")):
        if path.is_symlink() or not path.is_file() or "__pycache__" in path.parts:
            continue
        top = path.relative_to(vendor).parts[0]
        if top in DEPENDENCY_TOP_LEVEL or (
            top.endswith(".dist-info") and top.startswith(DEPENDENCY_DIST_PREFIXES)
        ):
            result.append((path.relative_to(vendor).as_posix(), path))
    if not any(name == "pg8000/__init__.py" for name, _ in result):
        raise RuntimeError("PG8000_MISSING")
    return result


def build(source_root: Path, vendor_root: Path, output: Path) -> dict[str, object]:
    entries: dict[str, Path] = {}
    for relative, destination in SOURCE_FILES:
        for name, path in _files(source_root, relative, destination):
            if name in entries:
                raise RuntimeError(f"PACKAGE_PATH_COLLISION:{name}")
            entries[name] = path
    for name, path in _dependency_files(vendor_root):
        if name in entries:
            raise RuntimeError(f"PACKAGE_PATH_COLLISION:{name}")
        entries[name] = path

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise RuntimeError("OUTPUT_ALREADY_EXISTS")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, entries[name].read_bytes())
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return {"path": output.as_posix(), "bytes": output.stat().st_size, "sha256": digest, "files": len(entries)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--vendor-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(build(args.source_root.resolve(), args.vendor_root.resolve(), args.output.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
