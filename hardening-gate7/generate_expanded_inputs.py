#!/usr/bin/env python3
"""Generate hidden Gate 7 inputs and a separately sealed oracle.

The hidden master seed is supplied by the controller only after preflight GREEN.
The measured runner receives case files and the input manifest, never the oracle.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("MODULE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


contract = load_module("gate7_expanded_contract", HERE / "expanded_contract.py")
legacy = load_module("gate7_legacy_generator", HERE / "make_vectors.py")


def canonical(value: Any) -> bytes:
    return contract.canonical(value)


def digest(value: bytes | Any) -> str:
    return contract.digest(value)


def atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    if temporary.exists():
        raise RuntimeError("TEMPORARY_PATH_EXISTS")
    with temporary.open("xb") as handle:
        handle.write(raw)
        handle.flush()
    temporary.replace(path)


def derive(master: bytes, campaign_id: str, block: str, slot_id: str) -> bytes:
    domain = f"gate7-r2\x00{campaign_id}\x00{block}\x00{slot_id}".encode("utf-8")
    return hmac.new(master, domain, hashlib.sha256).digest()


def _legacy_maps(master: bytes) -> tuple[dict[tuple[str, int], dict[str, Any]], dict[tuple[str, int], dict[str, Any]]]:
    # The preserved generator requires one 32-byte salt. Domain separation binds
    # this derivation to the original semantic block without exposing the master.
    salt = hmac.new(master, b"gate7-r2-original-43", hashlib.sha256).digest()
    record = legacy.build(contract.CANDIDATE, salt)
    failures = {(row["class"], row["variant"]): row for row in record["failure_vectors"]}
    controls = {
        (row["class"].removeprefix("valid-control-"), row["variant"]): row
        for row in record["valid_controls"]
    }
    return failures, controls


def _strip_legacy(vector: dict[str, Any]) -> dict[str, Any]:
    body = {
        "class": vector["class"],
        "variant": vector["variant"],
        "seed_hash": vector["seed_hash"],
        "input": vector["input"],
    }
    return dict(body, legacy_input_sha256=digest(body))


def _legacy_for_slot(
    row: dict[str, Any],
    failures: dict[tuple[str, int], dict[str, Any]],
    controls: dict[tuple[str, int], dict[str, Any]],
) -> tuple[dict[str, Any], str, str]:
    parts = row["operation"].split(":")
    if parts[0] == "legacy-failure":
        vector = failures[(parts[1], int(parts[2]))]
    elif parts[0] == "legacy-control":
        vector = controls[(parts[1], int(parts[2]))]
    elif parts[0] == "legacy-determinism":
        verdict = parts[1]
        candidates = [*failures.values(), *controls.values()]
        vector = next(item for item in candidates if item["expected_verdict"] == verdict)
    else:
        raise ValueError("LEGACY_OPERATION_INVALID")
    return _strip_legacy(vector), vector["expected_verdict"], vector["expected_reason"]


def build_records(master: bytes, campaign_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if len(master) != 32:
        raise ValueError("MASTER_SEED_LENGTH_INVALID")
    rows = contract.slots()
    contract.validate_slots(rows)
    failures, controls = _legacy_maps(master)
    inputs: list[dict[str, Any]] = []
    oracle: list[dict[str, Any]] = []
    for row in rows:
        case_seed = derive(master, campaign_id, row["block"], row["slot_id"])
        case_seed_hash = digest(case_seed)
        expected_verdict = row["expected_verdict"]
        expected_reason = row["expected_reason"]
        body: dict[str, Any] = {
            "version": "hardening-gate7-case-input-v1",
            "campaign_id": campaign_id,
            "candidate_commit": contract.CANDIDATE,
            "slot_id": row["slot_id"],
            "block": row["block"],
            "mode": "legacy" if row["block"].startswith("A_") else "surface",
            "operation": row["operation"],
            "topology": row["topology"],
            "workflow": row["workflow"],
            "factors": row["factors"],
            "boundary": row["boundary"],
            "temporal": row["temporal"],
            "case_seed_hex": case_seed.hex(),
            "case_seed_sha256": case_seed_hash,
        }
        if body["mode"] == "legacy":
            legacy_input, expected_verdict, expected_reason = _legacy_for_slot(
                row, failures, controls
            )
            body["legacy_input"] = legacy_input
        case_input = dict(body, input_sha256=digest(body))
        inputs.append(case_input)
        oracle_body = {
            "version": "hardening-gate7-case-oracle-v1",
            "campaign_id": campaign_id,
            "slot_id": row["slot_id"],
            "input_sha256": case_input["input_sha256"],
            "case_seed_sha256": case_seed_hash,
            "expected_verdict": expected_verdict,
            "expected_reason": expected_reason,
            "topology": row["topology"],
            "workflow": row["workflow"],
            "block": row["block"],
            "boundary": row["boundary"],
            "temporal": row["temporal"],
        }
        oracle.append(dict(oracle_body, oracle_sha256=digest(oracle_body)))
    return inputs, oracle


def order_cases(inputs: list[dict[str, Any]], oracle: list[dict[str, Any]], master: bytes) -> list[str]:
    oracle_by_id = {row["slot_id"]: row for row in oracle}
    deterministic = [row for row in inputs if row["block"] == "A_ORIGINAL_DETERMINISM"]
    remaining = [row for row in inputs if row["block"] != "A_ORIGINAL_DETERMINISM"]

    def ranking(row: dict[str, Any]) -> str:
        return digest(master + row["slot_id"].encode("utf-8"))

    pending = sorted(remaining, key=ranking)
    interleaved: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    while pending:
        choices = sorted(
            pending,
            key=lambda row: (
                1 if previous and oracle_by_id[row["slot_id"]]["expected_verdict"]
                == oracle_by_id[previous["slot_id"]]["expected_verdict"] else 0,
                1 if previous and row["topology"] == previous["topology"]
                and row["topology"] != "NONE" else 0,
                1 if previous and row["workflow"] == previous["workflow"]
                and row["workflow"] != "NONE" else 0,
                ranking(row),
            ),
        )
        selected = choices[0]
        pending.remove(selected)
        interleaved.append(selected)
        previous = selected

    # Five repetitions per verdict are intentionally distributed from early to
    # late campaign positions. Ordering inside each band remains seed-derived.
    det_by_rep: dict[int, list[dict[str, Any]]] = {}
    for row in deterministic:
        repetition = int(row["slot_id"].rsplit("-", 1)[1])
        det_by_rep.setdefault(repetition, []).append(row)
    targets = (4, 20, 40, 60, 78)
    offset = 0
    for repetition, target in enumerate(targets, start=1):
        batch = sorted(det_by_rep[repetition], key=ranking)
        position = min(target + offset, len(interleaved))
        interleaved[position:position] = batch
        offset += len(batch)
    order = [row["slot_id"] for row in interleaved]
    if len(order) != 84 or len(set(order)) != 84:
        raise RuntimeError("PERMUTATION_INVALID")
    thirds = (set(order[:28]), set(order[28:56]), set(order[56:]))
    for verdict in ("promote", "refuse", "invalid"):
        ids = {row["slot_id"] for row in deterministic if f"-{verdict}-" in row["slot_id"]}
        if any(not (ids & third) for third in thirds):
            raise RuntimeError("DETERMINISM_STRATIFICATION_INVALID")
    return order


def write_campaign(master: bytes, campaign_id: str, output: Path) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError("OUTPUT_ROOT_EXISTS")
    inputs, oracle = build_records(master, campaign_id)
    order = order_cases(inputs, oracle, master)
    input_root = output / "inputs"
    oracle_root = output / "sealed-oracle"
    input_root.mkdir(parents=True)
    oracle_root.mkdir()
    input_by_id = {row["slot_id"]: row for row in inputs}
    for slot_id in order:
        atomic_write(input_root / f"{slot_id}.json", canonical(input_by_id[slot_id]))
    input_body = {
        "version": "hardening-gate7-input-manifest-v1",
        "campaign_id": campaign_id,
        "candidate_commit": contract.CANDIDATE,
        "execution_order": order,
        "case_files": {
            f"{slot_id}.json": digest((input_root / f"{slot_id}.json").read_bytes())
            for slot_id in order
        },
        "case_count": len(order),
        "oracle_included": False,
    }
    input_manifest = dict(input_body, manifest_sha256=digest(input_body))
    atomic_write(output / "input-manifest.json", canonical(input_manifest))
    oracle_body = {
        "version": "hardening-gate7-oracle-manifest-v1",
        "campaign_id": campaign_id,
        "candidate_commit": contract.CANDIDATE,
        "input_manifest_sha256": input_manifest["manifest_sha256"],
        "entries": sorted(oracle, key=lambda row: row["slot_id"]),
    }
    oracle_manifest = dict(oracle_body, oracle_manifest_sha256=digest(oracle_body))
    atomic_write(oracle_root / "oracle.json", canonical(oracle_manifest))
    commitment_body = {
        "version": "hardening-gate7-seed-commitment-v1",
        "campaign_id": campaign_id,
        "master_seed_sha256": digest(master),
        "input_manifest_sha256": input_manifest["manifest_sha256"],
        "oracle_manifest_sha256": oracle_manifest["oracle_manifest_sha256"],
        "seed_revealed": False,
    }
    commitment = dict(commitment_body, commitment_sha256=digest(commitment_body))
    atomic_write(output / "seed-commitment.json", canonical(commitment))
    return {
        "input_manifest": input_manifest,
        "oracle_manifest": oracle_manifest,
        "commitment": commitment,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-file", required=True, type=Path)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    seed_raw = args.seed_file.read_bytes()
    seed_text = seed_raw.strip()
    if len(seed_text) == 64:
        try:
            master = bytes.fromhex(seed_text.decode("ascii"))
        except (UnicodeDecodeError, ValueError) as error:
            raise ValueError("MASTER_SEED_HEX_INVALID") from error
    elif len(seed_raw) == 32:
        master = seed_raw
    else:
        raise ValueError("MASTER_SEED_FILE_INVALID")
    write_campaign(master, args.campaign_id, args.output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
