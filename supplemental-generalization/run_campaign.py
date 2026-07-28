#!/usr/bin/env python3
"""Run and aggregate the frozen supplemental scale campaign."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import time
from typing import Any


ZERO_HASH = "0" * 64
EXPECTED_CANDIDATE = "8718fbecc2b145ff36ce8c3ed655e92b5906aeab"


class CampaignError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def file_hash(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if isinstance(value, bytes) else canonical(value)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
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
        if temporary.exists():
            temporary.unlink()


def validate_isolation() -> dict[str, Any]:
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise CampaignError("PLATFORM_INVALID")
    if os.getuid() == 0 or os.geteuid() == 0:
        raise CampaignError("UNPRIVILEGED_USER_REQUIRED")
    status = {}
    for line in Path("/proc/self/status").read_text().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            status[key] = value.strip()
    if (int(status.get("CapEff", "-1"), 16) != 0 or
            status.get("NoNewPrivs") != "1" or status.get("Seccomp") != "2"):
        raise CampaignError("KERNEL_ISOLATION_INVALID")
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError as error:
        if error.errno != 1:
            raise CampaignError("NETWORK_DENIAL_ERRNO_INVALID") from error
    else:
        raise CampaignError("NETWORK_DENIAL_NOT_ENFORCED")
    return {"uid": os.getuid(), "cap_eff": status["CapEff"],
            "no_new_privs": status["NoNewPrivs"], "seccomp": status["Seccomp"]}


def validate_manifest(manifest: Any) -> list[dict[str, Any]]:
    if not isinstance(manifest, dict):
        raise CampaignError("MANIFEST_INVALID")
    body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    if (manifest.get("manifest_sha256") != digest(body) or
            manifest.get("version") != "supplemental-generalization-manifest-v1" or
            manifest.get("candidate_commit") != EXPECTED_CANDIDATE or
            not str(manifest.get("campaign_id", "")).startswith("ck-supp-generalization-") or
            manifest.get("row_count") != 108):
        raise CampaignError("MANIFEST_CONTROL_INVALID")
    rows = manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != 108:
        raise CampaignError("MANIFEST_ROWS_INVALID")
    for index, row in enumerate(rows, 1):
        row_body = {key: value for key, value in row.items() if key != "row_sha256"}
        if row.get("sequence") != index or row.get("row_sha256") != digest(row_body):
            raise CampaignError("MANIFEST_ROW_INVALID")
    return rows


def append_checkpoint(path: Path, row: dict[str, Any], receipt_hash: str,
                      prior_hash: str) -> str:
    event = {"version": "supplemental-generalization-checkpoint-v1",
             "sequence": row["sequence"], "row_sha256": row["row_sha256"],
             "receipt_sha256": receipt_hash, "previous_event_sha256": prior_hash}
    event["event_sha256"] = digest(event)
    with path.open("ab") as handle:
        handle.write(canonical(event) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    return event["event_sha256"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--harness", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--git", required=True, type=Path)
    parser.add_argument("--restic", required=True, type=Path)
    parser.add_argument("--python", required=True, type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_bytes())
    rows = validate_manifest(manifest)
    if args.validate_only:
        print(canonical({"status": "GREEN", "rows": len(rows),
                         "manifest_sha256": manifest["manifest_sha256"]}).decode())
        return 0
    isolation = validate_isolation()
    for path in (args.harness, args.git, args.restic, args.python):
        if not path.resolve().is_file():
            raise CampaignError("TOOL_PATH_INVALID")
    output = args.output_root.resolve()
    output.mkdir(parents=True, exist_ok=False)
    receipts_dir = output / "receipts"
    receipts_dir.mkdir()
    checkpoints = output / "checkpoints.ndjson"
    checkpoints.touch(mode=0o600)
    env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
           "CK_GATE5_GIT": str(args.git.resolve()),
           "CK_GATE5_RESTIC": str(args.restic.resolve())}
    receipts = []
    prior = ZERO_HASH
    started = time.monotonic()
    for row in rows:
        destination = receipts_dir / row["receipt_name"]
        command = [str(args.python.resolve()), str(args.harness.resolve()),
                   row["profile"], row["scenario"], str(row["repetition"]),
                   row["method"], str(destination), "--campaign-id",
                   manifest["campaign_id"], "--execution-order",
                   str(row["execution_order"])]
        result = subprocess.run(command, cwd=args.harness.resolve().parents[1],
                                env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=600, check=False)
        if result.returncode != 0:
            raise CampaignError(f"ROW_FAILED:{row['sequence']}:{digest(result.stdout)}")
        raw = destination.read_bytes()
        wrapped = json.loads(raw)
        claimed = wrapped.get("receipt_sha256")
        if claimed != digest({key: value for key, value in wrapped.items()
                              if key != "receipt_sha256"}):
            raise CampaignError("RECEIPT_HASH_INVALID")
        receipt = wrapped["base_receipt"]
        if (receipt["candidate_commit"] != EXPECTED_CANDIDATE or
                receipt["campaign_id"] != manifest["campaign_id"] or
                receipt["evidence_mode"] != "SUPPLEMENTAL_GENERALIZATION" or
                receipt["runtime_platform"] != "Linux" or
                receipt["scenario_class"] != row["scenario"] or
                receipt["method"] != row["method"] or
                not receipt["cleanup_pass"] or receipt["unsafe_acceptance"]):
            raise CampaignError("RECEIPT_CONTEXT_INVALID")
        receipts.append(wrapped)
        prior = append_checkpoint(checkpoints, row, claimed, prior)
    profile_summary = {}
    for profile in manifest["profiles"]:
        items = [item for item in receipts if item["scale_profile"]["name"] == profile]
        profile_summary[profile] = {
            "execution_count": len(items),
            "generated_bytes": items[0]["scale_profile"]["total_generated_bytes"],
            "cleanup_pass": sum(item["base_receipt"]["cleanup_pass"] for item in items),
            "unsafe_acceptance_count": sum(item["base_receipt"]["unsafe_acceptance"] for item in items),
            "product_exact_match": [
                sum(item["base_receipt"]["manifest_exact_match"] for item in items
                    if item["base_receipt"]["method"] == "product"),
                sum(item["base_receipt"]["method"] == "product" for item in items),
            ],
            "product_continuation_pass": [
                sum(item["base_receipt"]["executable_continuation_pass"] for item in items
                    if item["base_receipt"]["method"] == "product"),
                sum(item["base_receipt"]["method"] == "product" for item in items),
            ],
        }
    aggregate = {"version": "supplemental-generalization-aggregate-v1",
                 "status": "GREEN_CANDIDATE_PENDING_INDEPENDENT_REVIEW",
                 "campaign_id": manifest["campaign_id"],
                 "candidate_commit": EXPECTED_CANDIDATE,
                 "manifest_sha256": manifest["manifest_sha256"],
                 "measured_executions": len(receipts),
                 "final_checkpoint_sha256": prior,
                 "elapsed_seconds": time.monotonic() - started,
                 "isolation": isolation, "profile_summary": profile_summary,
                 "cleanup_pass": sum(item["base_receipt"]["cleanup_pass"] for item in receipts),
                 "unsafe_acceptance_count": sum(item["base_receipt"]["unsafe_acceptance"] for item in receipts),
                 "limitations": ["SYNTHETIC_PRIVATE_GENERALIZATION",
                                 "NOT_INDEPENDENT_USER_EVIDENCE",
                                 "NO_POPULATION_INFERENCE", "NOT_PRODUCTION_SCALE"]}
    if (aggregate["measured_executions"] != 108 or
            aggregate["cleanup_pass"] != 108 or
            aggregate["unsafe_acceptance_count"] != 0 or
            any(value["product_exact_match"] != [12, 12] or
                value["product_continuation_pass"] != [12, 12]
                for value in profile_summary.values())):
        raise CampaignError("ACCEPTANCE_INVALID")
    aggregate["aggregate_sha256"] = digest(aggregate)
    atomic_write(output / "aggregate.json", aggregate)
    files = [{"path": path.relative_to(output).as_posix(), "bytes": path.stat().st_size,
              "sha256": file_hash(path)} for path in sorted(output.rglob("*")) if path.is_file()]
    evidence_manifest = {"version": "supplemental-generalization-evidence-v1",
                         "campaign_id": manifest["campaign_id"], "files": files}
    evidence_manifest["manifest_sha256"] = digest(evidence_manifest)
    atomic_write(output / "evidence-manifest.json", evidence_manifest)
    print(canonical({"status": "GREEN_CANDIDATE_PENDING_INDEPENDENT_REVIEW",
                     "aggregate_sha256": aggregate["aggregate_sha256"],
                     "evidence_manifest_sha256": evidence_manifest["manifest_sha256"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
