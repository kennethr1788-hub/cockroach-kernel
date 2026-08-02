#!/usr/bin/env python3
"""Canonical interruption-survivable checkpoint archives for PDH-3 R12.

Remote writers publish immutable sequence-numbered archives and manifests.  A
small canonical ``latest.json`` pointer is replaced only after both immutable
objects are fsynced.  The host copies to ``.part`` files, verifies every hash,
and writes its own canonical acknowledgement.  No partial or newer file can be
accepted as a complete earlier checkpoint.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile
from typing import Any, Iterable


ZERO_HASH = "0" * 64


class CheckpointError(RuntimeError):
    """Stable checkpoint failure."""


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


def validate_relative(value: str) -> None:
    path = PurePosixPath(value)
    if (
        not value
        or "\x00" in value
        or "\\" in value
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
        or str(path) != value
    ):
        raise CheckpointError("UNSAFE_RELATIVE_PATH")


def validate_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise CheckpointError(label + "_SHA256_INVALID")
    return value


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


def write_hashed(path: Path, body: dict[str, Any], hash_field: str) -> dict[str, Any]:
    value = {**body, hash_field: digest(body)}
    atomic_write(path, canonical(value))
    return value


def verify_hashed(path: Path, hash_field: str) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise CheckpointError("RECORD_JSON_INVALID") from exc
    if not isinstance(value, dict) or canonical(value) != raw:
        raise CheckpointError("RECORD_NON_CANONICAL")
    expected = validate_sha256(value.get(hash_field), hash_field.upper())
    body = {key: item for key, item in value.items() if key != hash_field}
    if digest(body) != expected:
        raise CheckpointError("RECORD_HASH_MISMATCH")
    return value


def collect_files(root: Path, relatives: Iterable[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for relative in sorted(set(relatives)):
        validate_relative(relative)
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise CheckpointError("CHECKPOINT_SOURCE_INVALID:" + relative)
        entries.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
        )
    if not entries:
        raise CheckpointError("CHECKPOINT_FILE_SET_EMPTY")
    return entries


def build_archive(root: Path, entries: list[dict[str, Any]]) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz", format=tarfile.PAX_FORMAT) as archive:
        for entry in entries:
            path = root / entry["path"]
            info = tarfile.TarInfo(entry["path"])
            info.size = entry["bytes"]
            info.mode = 0o600
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            with path.open("rb") as handle:
                archive.addfile(info, handle)
    return output.getvalue()


def publish(
    *,
    source_root: Path,
    export_root: Path,
    sequence: int,
    previous_manifest_sha256: str,
    packet_sha256: str,
    files: list[str],
) -> dict[str, Any]:
    if sequence < 1:
        raise CheckpointError("SEQUENCE_INVALID")
    validate_sha256(previous_manifest_sha256, "PREVIOUS_MANIFEST")
    validate_sha256(packet_sha256, "PACKET")
    if sequence == 1 and previous_manifest_sha256 != ZERO_HASH:
        raise CheckpointError("GENESIS_PREVIOUS_HASH_INVALID")
    if sequence > 1 and previous_manifest_sha256 == ZERO_HASH:
        raise CheckpointError("NON_GENESIS_PREVIOUS_HASH_INVALID")
    export_root.mkdir(parents=True, exist_ok=True)
    archive_name = f"checkpoint-{sequence:04d}.tgz"
    manifest_name = f"checkpoint-{sequence:04d}.json"
    archive_path = export_root / archive_name
    manifest_path = export_root / manifest_name
    if archive_path.exists() or manifest_path.exists():
        raise CheckpointError("CHECKPOINT_SEQUENCE_ALREADY_EXISTS")
    entries = collect_files(source_root, files)
    archive_raw = build_archive(source_root, entries)
    atomic_write(archive_path, archive_raw)
    body = {
        "version": "ck-pdh3-r12-checkpoint-manifest-v1",
        "sequence": sequence,
        "previous_manifest_sha256": previous_manifest_sha256,
        "packet_sha256": packet_sha256,
        "archive": archive_name,
        "archive_bytes": len(archive_raw),
        "archive_sha256": digest(archive_raw),
        "files": entries,
        "file_set_sha256": digest(entries),
    }
    manifest = write_hashed(manifest_path, body, "manifest_sha256")
    latest_body = {
        "version": "ck-pdh3-r12-checkpoint-latest-v1",
        "sequence": sequence,
        "manifest": manifest_name,
        "manifest_sha256": manifest["manifest_sha256"],
    }
    write_hashed(export_root / "latest.json", latest_body, "pointer_sha256")
    return manifest


def safe_archive_index(archive: tarfile.TarFile) -> dict[str, tarfile.TarInfo]:
    members = archive.getmembers()
    index: dict[str, tarfile.TarInfo] = {}
    for member in members:
        if not member.isfile():
            raise CheckpointError("ARCHIVE_MEMBER_NOT_REGULAR")
        validate_relative(member.name)
        if member.name in index:
            raise CheckpointError("ARCHIVE_MEMBER_DUPLICATE")
        index[member.name] = member
    return index


def verify_download(
    *,
    manifest_path: Path,
    archive_path: Path,
    expected_packet_sha256: str,
    expected_sequence: int | None = None,
    expected_previous_manifest_sha256: str | None = None,
) -> dict[str, Any]:
    manifest = verify_hashed(manifest_path, "manifest_sha256")
    if manifest.get("version") != "ck-pdh3-r12-checkpoint-manifest-v1":
        raise CheckpointError("MANIFEST_VERSION_INVALID")
    if manifest.get("packet_sha256") != expected_packet_sha256:
        raise CheckpointError("PACKET_BINDING_MISMATCH")
    if expected_sequence is not None and manifest.get("sequence") != expected_sequence:
        raise CheckpointError("SEQUENCE_MISMATCH")
    if (
        expected_previous_manifest_sha256 is not None
        and manifest.get("previous_manifest_sha256")
        != expected_previous_manifest_sha256
    ):
        raise CheckpointError("PREVIOUS_MANIFEST_MISMATCH")
    if manifest.get("archive") != archive_path.name:
        raise CheckpointError("ARCHIVE_NAME_MISMATCH")
    if manifest.get("archive_bytes") != archive_path.stat().st_size:
        raise CheckpointError("ARCHIVE_SIZE_MISMATCH")
    if manifest.get("archive_sha256") != file_sha256(archive_path):
        raise CheckpointError("ARCHIVE_HASH_MISMATCH")
    entries = manifest.get("files")
    if not isinstance(entries, list) or not entries or manifest.get("file_set_sha256") != digest(entries):
        raise CheckpointError("MANIFEST_FILE_SET_INVALID")
    expected = {entry.get("path"): entry for entry in entries if isinstance(entry, dict)}
    if len(expected) != len(entries):
        raise CheckpointError("MANIFEST_FILE_ENTRY_INVALID")
    with tarfile.open(archive_path, "r:gz") as archive:
        index = safe_archive_index(archive)
        if set(index) != set(expected):
            raise CheckpointError("ARCHIVE_FILE_SET_MISMATCH")
        for name, entry in expected.items():
            validate_relative(str(name))
            member = index[str(name)]
            handle = archive.extractfile(member)
            if handle is None:
                raise CheckpointError("ARCHIVE_MEMBER_UNREADABLE")
            raw = handle.read()
            if entry != {"path": name, "bytes": len(raw), "sha256": digest(raw)}:
                raise CheckpointError("ARCHIVE_MEMBER_HASH_MISMATCH")
    return manifest


def acknowledge(
    *,
    output: Path,
    manifest: dict[str, Any],
    local_archive: Path,
    acknowledged_utc: str,
) -> dict[str, Any]:
    body = {
        "version": "ck-pdh3-r12-checkpoint-ack-v1",
        "sequence": manifest["sequence"],
        "manifest_sha256": manifest["manifest_sha256"],
        "archive_sha256": file_sha256(local_archive),
        "local_bytes": local_archive.stat().st_size,
        "acknowledged_utc": acknowledged_utc,
        "independent_local_copy": True,
    }
    return write_hashed(output, body, "ack_sha256")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    subparsers = value.add_subparsers(dest="command", required=True)
    publish_parser = subparsers.add_parser("publish")
    publish_parser.add_argument("--source-root", type=Path, required=True)
    publish_parser.add_argument("--export-root", type=Path, required=True)
    publish_parser.add_argument("--sequence", type=int, required=True)
    publish_parser.add_argument("--previous-manifest-sha256", required=True)
    publish_parser.add_argument("--packet-sha256", required=True)
    publish_parser.add_argument("--file", action="append", required=True)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--manifest", type=Path, required=True)
    verify_parser.add_argument("--archive", type=Path, required=True)
    verify_parser.add_argument("--packet-sha256", required=True)
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "publish":
            value = publish(
                source_root=args.source_root,
                export_root=args.export_root,
                sequence=args.sequence,
                previous_manifest_sha256=args.previous_manifest_sha256,
                packet_sha256=args.packet_sha256,
                files=args.file,
            )
        else:
            value = verify_download(
                manifest_path=args.manifest,
                archive_path=args.archive,
                expected_packet_sha256=args.packet_sha256,
            )
    except (CheckpointError, OSError, tarfile.TarError) as exc:
        print(f"PDH3_R12_CHECKPOINT_BLOCKED:{type(exc).__name__}:{exc}", file=os.sys.stderr)
        return 2
    print(canonical(value).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
