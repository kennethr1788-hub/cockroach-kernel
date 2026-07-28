#!/usr/bin/env python3
"""Gate 6 R2 process-isolated measured campaign and evidence aggregator."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import statistics
import subprocess
import sys
import time
from typing import Any


EXPECTED_CANDIDATE = "8718fbecc2b145ff36ce8c3ed655e92b5906aeab"
EXPECTED_PROTOCOL = "a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52"
EXPECTED_RESTIC = "ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c"
SCENARIOS = (
    "committed-only", "committed-plus-uncommitted", "complete-loss",
    "partial-loss", "conflicting-stale", "clean-control",
)
METHODS = ("ordinary-git", "git-plus-restic-0.19.0", "product")
ZERO_HASH = "0" * 64


class CampaignError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if isinstance(value, bytes) else canonical(value)
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
        if temporary.exists():
            temporary.unlink()


def file_hash(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def load_comparative(path: Path):
    spec = importlib.util.spec_from_file_location("gate6_comparative", path)
    if spec is None or spec.loader is None:
        raise CampaignError("COMPARATIVE_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_manifest(manifest: Any) -> list[dict[str, Any]]:
    if not isinstance(manifest, dict):
        raise CampaignError("MANIFEST_TYPE_INVALID")
    claimed = manifest.get("manifest_sha256")
    body = {key: value for key, value in manifest.items()
            if key != "manifest_sha256"}
    if claimed != digest(body):
        raise CampaignError("MANIFEST_HASH_MISMATCH")
    if (manifest.get("version") != "hardening-gate6-execution-manifest-v1" or
            manifest.get("execution_revision") != "R2" or
            manifest.get("candidate_commit") != EXPECTED_CANDIDATE or
            manifest.get("evidence_mode") != "MEASURED_GATE6" or
            not str(manifest.get("campaign_id", "")).startswith("ck-gate6-") or
            manifest.get("row_count") != 54 or
            tuple(manifest.get("scenario_classes", [])) != SCENARIOS or
            tuple(manifest.get("methods", [])) != METHODS or
            manifest.get("repetitions") != [1, 2, 3] or
            manifest.get("recovery_budget_seconds") != 180):
        raise CampaignError("MANIFEST_CONTROL_INVALID")
    rows = manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != 54:
        raise CampaignError("MANIFEST_ROWS_INVALID")
    combinations: set[tuple[str, int, str]] = set()
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise CampaignError("MANIFEST_ROW_TYPE_INVALID")
        claimed_row = row.get("row_sha256")
        row_body = {key: value for key, value in row.items()
                    if key != "row_sha256"}
        if claimed_row != digest(row_body) or row.get("sequence") != index:
            raise CampaignError("MANIFEST_ROW_HASH_INVALID")
        key = (row.get("scenario_class"), row.get("repetition"),
               row.get("method"))
        if (key[0] not in SCENARIOS or key[1] not in (1, 2, 3) or
                key[2] not in METHODS or key in combinations or
                row.get("execution_order") not in (1, 2, 3) or
                not re.fullmatch(r"[0-9]{3}--[a-z0-9.-]+--r[123]--[a-z0-9.+-]+\.json",
                                 str(row.get("receipt_name", "")))):
            raise CampaignError("MANIFEST_ROW_INVALID")
        combinations.add(key)
    expected = {(scenario, repetition, method)
                for scenario in SCENARIOS for repetition in (1, 2, 3)
                for method in METHODS}
    if combinations != expected:
        raise CampaignError("MANIFEST_COVERAGE_INVALID")
    for scenario_index, scenario in enumerate(SCENARIOS):
        rotation = scenario_index % 3
        expected_order = METHODS[rotation:] + METHODS[:rotation]
        for repetition in (1, 2, 3):
            actual = tuple(row["method"] for row in rows
                           if row["scenario_class"] == scenario and
                           row["repetition"] == repetition)
            if actual != expected_order:
                raise CampaignError("MANIFEST_ROTATION_INVALID")
    return rows


def validate_tools(tools: Any, git: Path, restic: Path, python: Path) -> None:
    expected = {
        "platform": "Linux",
        "architecture": "x86_64",
        "git": {"path": str(git), "sha256": file_hash(git)},
        "restic": {"path": str(restic), "sha256": file_hash(restic)},
        "python": {"path": str(python), "sha256": file_hash(python)},
    }
    for key in ("platform", "architecture"):
        if tools.get(key) != expected[key]:
            raise CampaignError("TOOL_PLATFORM_DRIFT")
    for name in ("git", "restic", "python"):
        item = tools.get(name)
        if not isinstance(item, dict):
            raise CampaignError("TOOL_RECORD_INVALID")
        if item.get("path") != expected[name]["path"] or item.get("sha256") != expected[name]["sha256"]:
            raise CampaignError(f"{name.upper()}_PROVENANCE_DRIFT")
    if tools["restic"].get("sha256") != EXPECTED_RESTIC:
        raise CampaignError("RESTIC_HASH_INVALID")


def append_checkpoint(path: Path, sequence: int, row: dict[str, Any],
                      receipt: dict[str, Any], prior_hash: str) -> str:
    event = {
        "version": "hardening-gate6-checkpoint-v1",
        "sequence": sequence,
        "row_sha256": row["row_sha256"],
        "receipt_sha256": receipt["receipt_sha256"],
        "previous_event_sha256": prior_hash,
    }
    event["event_sha256"] = digest(event)
    raw = canonical(event) + b"\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(descriptor, "ab", closefd=True) as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    return event["event_sha256"]


def median(values: list[int | float]) -> int | float:
    return statistics.median(values)


def aggregate(receipts: list[dict[str, Any]], raw_sizes: dict[str, int],
              manifest: dict[str, Any], final_checkpoint: str) -> dict[str, Any]:
    if len(receipts) != 54:
        raise CampaignError("RECEIPT_COUNT_INVALID")
    pairs: list[dict[str, Any]] = []
    pair_match_counts = {name: 0 for name in
                         ("source", "event", "loss", "allowed_information")}
    retention_outcomes = {method: {"wins": 0, "ties": 0, "losses": 0}
                          for method in METHODS}
    for scenario in SCENARIOS:
        for repetition in (1, 2, 3):
            group = [item for item in receipts
                     if item["scenario_class"] == scenario and
                     item["repetition"] == repetition]
            if len(group) != 3 or {item["method"] for item in group} != set(METHODS):
                raise CampaignError("PAIR_COVERAGE_INVALID")
            hash_fields = {
                "source": "source_manifest_sha256",
                "event": "event_stream_sha256",
                "loss": "loss_receipt_sha256",
                "allowed_information": "allowed_information_sha256",
            }
            for label, field in hash_fields.items():
                if len({item[field] for item in group}) != 1:
                    raise CampaignError(f"PAIR_{label.upper()}_HASH_MISMATCH")
                pair_match_counts[label] += 1
            ratios = {item["method"]: item["declared_work_units_retained"] /
                      item["declared_work_units_total"] for item in group}
            best = max(ratios.values())
            winners = {method for method, value in ratios.items() if value == best}
            for method in METHODS:
                if method in winners and len(winners) == 1:
                    retention_outcomes[method]["wins"] += 1
                elif method in winners:
                    retention_outcomes[method]["ties"] += 1
                else:
                    retention_outcomes[method]["losses"] += 1
            pairs.append({
                "scenario_class": scenario,
                "repetition": repetition,
                "hashes": {label: group[0][field]
                           for label, field in hash_fields.items()},
                "methods": {item["method"]: {
                    "receipt_sha256": item["receipt_sha256"],
                    "operation_status": item["operation_status"],
                    "retention_ratio": ratios[item["method"]],
                    "manifest_exact_match": item["manifest_exact_match"],
                    "executable_continuation_pass": item["executable_continuation_pass"],
                    "unsafe_acceptance": item["unsafe_acceptance"],
                } for item in group},
            })
    method_summary: dict[str, Any] = {}
    for method in METHODS:
        items = [item for item in receipts if item["method"] == method]
        ratios = [item["declared_work_units_retained"] /
                  item["declared_work_units_total"] for item in items]
        method_summary[method] = {
            "execution_count": len(items),
            "operation_status_counts": {status: sum(item["operation_status"] == status
                                                     for item in items)
                                         for status in sorted({item["operation_status"]
                                                               for item in items})},
            "manifest_exact_match": [sum(item["manifest_exact_match"] for item in items), len(items)],
            "executable_continuation_pass": [sum(item["executable_continuation_pass"] for item in items), len(items)],
            "unsafe_acceptance": [sum(item["unsafe_acceptance"] for item in items), len(items)],
            "retention_ratio_raw": ratios,
            "retention_ratio_median": median(ratios),
            "retention_ratio_min": min(ratios),
            "retention_ratio_max": max(ratios),
            "recovery_ms_raw": [item["wall_clock_recovery_ms"] for item in items],
            "recovery_ms_median": median([item["wall_clock_recovery_ms"] for item in items]),
            "capture_overhead_ms_raw": [item["capture_overhead_ms"] for item in items],
            "capture_overhead_ms_median": median([item["capture_overhead_ms"] for item in items]),
            "storage_bytes_raw": [item["storage_bytes_pre_loss"] for item in items],
            "storage_bytes_median": median([item["storage_bytes_pre_loss"] for item in items]),
            "canonical_receipt_bytes_raw": [raw_sizes[item["receipt_sha256"]] for item in items],
            "canonical_receipt_bytes_median": median([raw_sizes[item["receipt_sha256"]] for item in items]),
            "retention_pair_outcomes": retention_outcomes[method],
        }
    result: dict[str, Any] = {
        "version": "hardening-gate6-aggregate-v1",
        "execution_revision": "R2",
        "status": "GREEN",
        "campaign_id": manifest["campaign_id"],
        "candidate_commit": EXPECTED_CANDIDATE,
        "manifest_sha256": manifest["manifest_sha256"],
        "measured_executions": len(receipts),
        "unique_combinations": len({(item["scenario_class"], item["repetition"], item["method"])
                                    for item in receipts}),
        "pair_count": len(pairs),
        "pair_hash_match_counts": pair_match_counts,
        "canonical_receipts_valid": sum(1 for _ in receipts),
        "cleanup_pass": sum(item["cleanup_pass"] for item in receipts),
        "residue_bytes": sum(item["residue_bytes_after_teardown"] for item in receipts),
        "unsafe_acceptance_count": sum(item["unsafe_acceptance"] for item in receipts),
        "original_workspace_mutation_count": sum(item["original_workspace_mutated_after_loss"] for item in receipts),
        "final_checkpoint_sha256": final_checkpoint,
        "method_summary": method_summary,
        "pairs": pairs,
        "limitations": [
            "SYNTHETIC_PAIRED_COMPARATIVE", "NOT_LIVE_AWS",
            "NOT_PRODUCT_SCALE", "RUNPOD_GENERIC_COMPUTE",
            "N_EQUALS_THREE_PER_CLASS_METHOD", "NO_POPULATION_INFERENCE",
            "PRODUCT_TEAM_AUTHORED_SCENARIOS_AND_SUCCESS_RULES",
            "RECEIPT_EVIDENCE_BYTES_FIELD_IS_PRE_RECEIPT_AND_ZERO; ACTUAL_CANONICAL_RECEIPT_BYTES_REPORTED_SEPARATELY",
        ],
    }
    if (result["unique_combinations"] != 54 or result["pair_count"] != 18 or
            set(pair_match_counts.values()) != {18} or
            result["canonical_receipts_valid"] != 54 or
            result["cleanup_pass"] != 54 or result["residue_bytes"] != 0 or
            result["unsafe_acceptance_count"] != 0 or
            result["original_workspace_mutation_count"] != 0):
        raise CampaignError("CAMPAIGN_INTEGRITY_INVALID")
    result["aggregate_sha256"] = digest(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--comparative", required=True, type=Path)
    parser.add_argument("--tools", required=True, type=Path)
    parser.add_argument("--git", required=True, type=Path)
    parser.add_argument("--restic", required=True, type=Path)
    parser.add_argument("--python", required=True, type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_bytes())
    rows = validate_manifest(manifest)
    comparative = load_comparative(args.comparative.resolve())
    if comparative.PROTOCOL_SHA256 != EXPECTED_PROTOCOL:
        raise CampaignError("PROTOCOL_HASH_DRIFT")
    if file_hash(args.comparative) != "f9fa1d5ce7076c8fa96a1b5d9053f50c58902c557f1d6fbf340c0c356d12a1ec":
        raise CampaignError("COMPARATIVE_HASH_DRIFT")
    if args.validate_only:
        print(canonical({"status": "GREEN", "rows": len(rows),
                         "manifest_sha256": manifest["manifest_sha256"]}).decode())
        return 0
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise CampaignError("MEASURED_PLATFORM_INVALID")
    if os.geteuid() == 0:
        raise CampaignError("HOST_USER_MUST_BE_UNPRIVILEGED")
    unshare = shutil.which("unshare")
    if unshare is None:
        raise CampaignError("NETWORK_DENY_RUNTIME_MISSING")
    for path in (args.git, args.restic, args.python):
        if not path.resolve().is_file():
            raise CampaignError("TOOL_PATH_INVALID")
    tools = json.loads(args.tools.read_bytes())
    validate_tools(tools, args.git.resolve(), args.restic.resolve(), args.python.resolve())
    output = args.output_root.resolve()
    output.mkdir(parents=True, exist_ok=False)
    receipts_root = output / "receipts"
    receipts_root.mkdir()
    checkpoints = output / "checkpoints.ndjson"
    child_env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "CK_GATE5_GIT": str(args.git.resolve()),
        "CK_GATE5_RESTIC": str(args.restic.resolve()),
    }
    receipts: list[dict[str, Any]] = []
    raw_sizes: dict[str, int] = {}
    prior_hash = ZERO_HASH
    started = time.monotonic()
    for row in rows:
        destination = receipts_root / row["receipt_name"]
        command = [
            unshare, "--user", "--map-root-user", "--net", "--mount-proc",
            str(args.python.resolve()), str(args.comparative.resolve()),
            row["scenario_class"], str(row["repetition"]), row["method"],
            str(destination), "--campaign-id", manifest["campaign_id"],
            "--candidate-commit", EXPECTED_CANDIDATE,
            "--execution-order", str(row["execution_order"]),
            "--evidence-mode", "MEASURED_GATE6",
        ]
        result = subprocess.run(command, cwd=args.comparative.resolve().parents[1],
                                env=child_env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, check=False, timeout=240)
        if result.returncode != 0:
            raise CampaignError(f"ROW_EXECUTION_FAILED:{row['sequence']}:{digest(result.stdout)}")
        raw = destination.read_bytes()
        receipt = comparative.validate_receipt(json.loads(raw), raw)
        if (receipt["campaign_id"] != manifest["campaign_id"] or
                receipt["candidate_commit"] != EXPECTED_CANDIDATE or
                receipt["evidence_mode"] != "MEASURED_GATE6" or
                receipt["runtime_platform"] != "Linux" or
                receipt["scenario_class"] != row["scenario_class"] or
                receipt["repetition"] != row["repetition"] or
                receipt["method"] != row["method"] or
                receipt["execution_order"] != row["execution_order"] or
                not receipt["cleanup_pass"] or
                receipt["residue_bytes_after_teardown"] != 0):
            raise CampaignError("RECEIPT_CONTEXT_INVALID")
        for name, item_hash in receipt["tool_binary_sha256"].items():
            if item_hash != tools[name]["sha256"]:
                raise CampaignError(f"RECEIPT_{name.upper()}_PROVENANCE_DRIFT")
            if receipt["tool_versions"][name] != tools[name]["version"]:
                raise CampaignError(f"RECEIPT_{name.upper()}_VERSION_DRIFT")
        receipts.append(receipt)
        raw_sizes[receipt["receipt_sha256"]] = len(raw)
        prior_hash = append_checkpoint(checkpoints, row["sequence"], row,
                                       receipt, prior_hash)
    result = aggregate(receipts, raw_sizes, manifest, prior_hash)
    result["elapsed_seconds"] = time.monotonic() - started
    result["aggregate_sha256"] = digest({key: value for key, value in result.items()
                                         if key != "aggregate_sha256"})
    atomic_write(output / "aggregate.json", result)
    evidence_files = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "evidence-manifest.json":
            evidence_files.append({
                "path": path.relative_to(output).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": file_hash(path),
            })
    evidence_manifest = {
        "version": "hardening-gate6-evidence-manifest-v1",
        "campaign_id": manifest["campaign_id"],
        "candidate_commit": EXPECTED_CANDIDATE,
        "files": evidence_files,
    }
    evidence_manifest["manifest_sha256"] = digest(evidence_manifest)
    atomic_write(output / "evidence-manifest.json", evidence_manifest)
    print(canonical({"status": "GREEN", "measured_executions": 54,
                     "aggregate_sha256": result["aggregate_sha256"],
                     "evidence_manifest_sha256": evidence_manifest["manifest_sha256"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
