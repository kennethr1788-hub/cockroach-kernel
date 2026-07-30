#!/usr/bin/env python3
"""Build the deterministic, local-only Gate 8 raw-evidence archive."""

from __future__ import annotations

import hashlib
import io
import json
import os
import tarfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".hardening-runtime" / "gate8-private"

SOURCES = (
    "HARDENING_GATE3_REAL_WORKFLOW_REPORT_R1.md",
    "HARDENING_GATE3_GLM_JUDGE_RECEIPT_R1.md",
    "HARDENING_GATE3_GREEN_CHECKPOINT_R1.md",
    "P9_FINAL_PACKET_R1.md",
    "P9_FINAL_JUDGE_RECEIPT_R1.md",
    "P9_STATUS.md",
    "FRESH_CONTEXT_BLACK_BOX_R4_HIDDEN_REPORT_R1.md",
    "FRESH_CONTEXT_BLACK_BOX_R4_HIDDEN_FINAL_GLM_RECEIPT_R1.md",
    "HARDENING_GATE6_R3_AGGREGATE.json",
    "HARDENING_GATE6_R3_MEASURED_EVIDENCE_INDEX.json",
    "HARDENING_GATE6_FINAL_JUDGE_RECEIPT_R3_AGY_R2.md",
    "HARDENING_GATE7_RUN3_BLOCKED_CLOSEOUT_R1.md",
    "HARDENING_GATE7_RUN3_BLOCKED_EVIDENCE_MANIFEST_R1.json",
    "HARDENING_GATE7_RUN4_BLOCKED_CLOSEOUT_R1.md",
    "HARDENING_GATE7_RUN4_BLOCKED_EVIDENCE_MANIFEST_R1.json",
    "HARDENING_GATE7_RUN5_BLOCKED_CLOSEOUT_R1.md",
    "HARDENING_GATE7_RUN5_BLOCKED_EVIDENCE_MANIFEST_R1.json",
    "HARDENING_GATE7_RUN5_FINAL_JUDGE_RECEIPT_R1.md",
    "HARDENING_GATE7_RUN6_CLOSEOUT_REPORT_R1.md",
    "HARDENING_GATE7_RUN6_EVIDENCE_MANIFEST_R1.json",
    "HARDENING_GATE7_RUN6_FINAL_PACKET_R1.md",
    "HARDENING_GATE7_RUN6_FINAL_JUDGE_RECEIPT_R1.md",
    "HARDENING_GATE7_RUN6_TEARDOWN_RECEIPT_R1.md",
    "HARDENING_GATE7_RUN6_GREEN_CHECKPOINT_R1.md",
    "evidence/p9-completion-live-r1",
    "evidence/p9-mcp-linked-r2",
    "evidence/p9-final-judges-r1",
    "evidence/black-box-r4-hidden",
    ".hardening-runtime/gate3-real-workflow",
    ".hardening-runtime/gate7-r6/attempt-a01/lifecycle-events.jsonl",
    ".hardening-runtime/gate7-r6/attempt-a01/live",
    ".hardening-runtime/gate7-r6/attempt-a01/readiness",
    ".hardening-runtime/gate7-r6/attempt-a01/track1-custody",
    ".hardening-runtime/gate7-r6/attempt-a01/track1-rescore",
    ".hardening-runtime/gate7-r6/attempt-a01/track2-remote",
    ".hardening-runtime/gate7-r6/attempt-a01/track2-start-gate.json",
    ".hardening-runtime/gate7-r6/attempt-a01/track3/evidence",
    ".hardening-runtime/gate7-r6/live-readiness-freeze.json",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


def selected_files() -> list[Path]:
    files: set[Path] = set()
    for raw in SOURCES:
        path = ROOT / raw
        if not path.exists():
            raise SystemExit(f"MISSING_SOURCE:{raw}")
        if path.is_symlink():
            raise SystemExit(f"SYMLINK_SOURCE_FORBIDDEN:{raw}")
        if path.is_file():
            files.add(path)
            continue
        for child in path.rglob("*"):
            if child.is_symlink():
                raise SystemExit(f"SYMLINK_SOURCE_FORBIDDEN:{child.relative_to(ROOT)}")
            if child.is_file():
                files.add(child)
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix())


def tar_info(name: str, size: int) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.size = size
    info.mtime = 0
    info.mode = 0o644
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    return info


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    files = selected_files()
    records = []
    total_bytes = 0
    for path in files:
        data = path.read_bytes()
        relative = path.relative_to(ROOT).as_posix()
        records.append({"bytes": len(data), "path": relative, "sha256": sha256(data)})
        total_bytes += len(data)

    source_manifest = {
        "file_count": len(records),
        "files": records,
        "source_bytes": total_bytes,
        "version": "hardening-gate8-private-source-manifest-v1",
    }
    source_manifest_bytes = canonical(source_manifest)
    source_manifest_path = OUTPUT / "source-manifest-r1.json"
    source_manifest_path.write_bytes(source_manifest_bytes)

    archive_path = OUTPUT / "cockroach-kernel-private-raw-evidence-r1.tar"
    with tarfile.open(archive_path, "w", format=tarfile.PAX_FORMAT) as archive:
        archive.addfile(
            tar_info("_archive/source-manifest-r1.json", len(source_manifest_bytes)),
            io.BytesIO(source_manifest_bytes),
        )
        if len(records) != len(files):
            raise SystemExit("SOURCE_RECORD_LENGTH_MISMATCH")
        for record, path in zip(records, files):
            data = path.read_bytes()
            archive.addfile(tar_info(record["path"], len(data)), io.BytesIO(data))

    archive_bytes = archive_path.read_bytes()
    receipt = {
        "archive_bytes": len(archive_bytes),
        "archive_file": archive_path.name,
        "archive_sha256": sha256(archive_bytes),
        "contains_hidden_or_private_evidence": True,
        "file_count": len(records),
        "git_tracked": False,
        "public_release_authorized": False,
        "source_bytes": total_bytes,
        "source_manifest_file": source_manifest_path.name,
        "source_manifest_sha256": sha256(source_manifest_bytes),
        "utc_created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "version": "hardening-gate8-private-archive-receipt-v1",
    }
    receipt_path = OUTPUT / "archive-receipt-r1.json"
    receipt_path.write_bytes(canonical(receipt))
    os.chmod(archive_path, 0o600)
    os.chmod(source_manifest_path, 0o600)
    os.chmod(receipt_path, 0o600)
    print(canonical(receipt).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
