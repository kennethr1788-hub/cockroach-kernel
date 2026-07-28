#!/usr/bin/env python3
"""Create one committed hidden seed, then freeze Gate 7 inputs and oracle."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import sys
import time
from typing import Any


HERE = Path(__file__).resolve().parent


def load_generator():
    path = HERE / "generate_expanded_inputs.py"
    spec = importlib.util.spec_from_file_location("gate7_hidden_generator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("GENERATOR_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def atomic_write(path: Path, raw: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        os.chmod(path, mode)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--packet-sha256", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    if len(args.packet_sha256) != 64:
        raise ValueError("PACKET_HASH_INVALID")
    output = args.output_root.resolve()
    if output.exists():
        raise ValueError("OUTPUT_ROOT_EXISTS")
    output.mkdir(mode=0o700, parents=True)
    seed = secrets.token_bytes(32)
    seed_path = output / "master-seed.bin"
    atomic_write(seed_path, seed)
    commitment_body = {
        "version": "hardening-gate7-pre-generation-commitment-v1",
        "campaign_id": args.campaign_id,
        "packet_sha256": args.packet_sha256,
        "master_seed_sha256": digest(seed),
        "seed_bytes": 32,
        "generator_started": False,
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "monotonic_ns": time.monotonic_ns(),
    }
    commitment = dict(
        commitment_body,
        commitment_sha256=digest(canonical(commitment_body)),
    )
    commitment_path = output / "pre-generation-commitment.json"
    atomic_write(commitment_path, canonical(commitment))
    # The commitment must be durable before any concrete input exists.
    if not commitment_path.is_file() or any(
        name in {path.name for path in output.iterdir()}
        for name in ("inputs", "sealed-oracle", "input-manifest.json")
    ):
        raise RuntimeError("PRE_GENERATION_COMMITMENT_NOT_ISOLATED")
    generator = load_generator()
    generated = output / "generated"
    records = generator.write_campaign(seed, args.campaign_id, generated)
    generation_body = {
        "version": "hardening-gate7-hidden-generation-receipt-v1",
        "campaign_id": args.campaign_id,
        "packet_sha256": args.packet_sha256,
        "pre_generation_commitment_sha256": commitment["commitment_sha256"],
        "master_seed_sha256": digest(seed),
        "input_manifest_sha256": records["input_manifest"]["manifest_sha256"],
        "oracle_manifest_sha256": records["oracle_manifest"]["oracle_manifest_sha256"],
        "case_count": records["input_manifest"]["case_count"],
        "oracle_in_runner_manifest": records["input_manifest"]["oracle_included"],
        "post_reveal_tuning_events": 0,
    }
    generation = dict(
        generation_body,
        generation_receipt_sha256=digest(canonical(generation_body)),
    )
    atomic_write(output / "generation-receipt.json", canonical(generation))
    print(canonical({
        "status": "HIDDEN_INPUTS_FROZEN",
        "commitment_sha256": commitment["commitment_sha256"],
        "generation_receipt_sha256": generation["generation_receipt_sha256"],
    }).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
