#!/usr/bin/env python3
"""Strict host-only configuration contract for the PDH-3 R12 R6 preflight."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any


class R6ConfigError(RuntimeError):
    """Stable R6 configuration failure."""


HEX64 = re.compile(r"[0-9a-f]{64}")
CAMPAIGN = re.compile(r"ck-pdh3-r12-preflight-r6-[a-z0-9-]{1,32}")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _require_hex(value: Any, label: str) -> str:
    if not isinstance(value, str) or HEX64.fullmatch(value) is None:
        raise R6ConfigError(label + "_INVALID")
    return value


def _require_path(value: Any, label: str, *, file: bool = True) -> Path:
    if not isinstance(value, str) or not value.startswith("/") or "\x00" in value:
        raise R6ConfigError(label + "_PATH_INVALID")
    supplied = Path(value)
    if supplied.is_symlink():
        raise R6ConfigError(label + ("_FILE_INVALID" if file else "_DIRECTORY_INVALID"))
    path = supplied.resolve()
    if file and not path.is_file():
        raise R6ConfigError(label + "_FILE_INVALID")
    if not file and not path.is_dir():
        raise R6ConfigError(label + "_DIRECTORY_INVALID")
    return path


def require_runtime_file(runtime: Path, value: Any, label: str) -> Path:
    """Resolve one receipt-bound file and require containment in the runtime."""
    runtime = runtime.resolve()
    path = _require_path(value, label)
    if runtime not in path.parents:
        raise R6ConfigError(label + "_OUTSIDE_RUNTIME")
    return path


def _utc(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise R6ConfigError(label + "_INVALID")
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise R6ConfigError(label + "_INVALID") from exc
    if parsed.tzinfo != timezone.utc or parsed.microsecond:
        raise R6ConfigError(label + "_INVALID")
    return parsed


def load(path: Path | None = None) -> dict[str, Any]:
    selected = path
    if selected is None:
        raw_path = os.environ.get("PDH3_R12_R6_CONFIG", "")
        if not raw_path:
            raise R6ConfigError("CONFIG_ENV_MISSING")
        selected = Path(raw_path)
    selected = selected.resolve()
    if not selected.is_file() or selected.is_symlink():
        raise R6ConfigError("CONFIG_FILE_INVALID")
    raw = selected.read_bytes()
    try:
        config = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise R6ConfigError("CONFIG_JSON_INVALID") from exc
    if not isinstance(config, dict):
        raise R6ConfigError("CONFIG_ROOT_INVALID")
    required = {
        "version", "root", "runtime", "runpodctl", "runpodctl_sha256",
        "packet", "packet_sha256", "platform_amendment",
        "platform_amendment_sha256", "authorization_envelope",
        "authorization_envelope_sha256", "judge_raw", "judge_raw_sha256", "campaign_id",
        "image", "launch_start_utc", "launch_end_utc", "stop_utc",
        "terminate_utc", "max_attempts", "rate_ceiling_usd_per_hour",
        "aggregate_cost_ceiling_usd", "archive", "archive_sha256",
        "bundle_receipt", "bundle_receipt_sha256", "tracer_binary_sha256",
    }
    version = config.get("version")
    if version in {
        "ck-pdh3-r12-r6-config-v3", "ck-pdh3-r12-r6-config-v4"
    }:
        required.add("data_center_ids")
    if version == "ck-pdh3-r12-r6-config-v4":
        required.update({"graphql_url", "min_vcpu_count"})
    if set(config) != required:
        raise R6ConfigError("CONFIG_FIELDS_INVALID")
    if version not in {
        "ck-pdh3-r12-r6-config-v2", "ck-pdh3-r12-r6-config-v3",
        "ck-pdh3-r12-r6-config-v4",
    }:
        raise R6ConfigError("CONFIG_VERSION_INVALID")
    root = _require_path(config["root"], "ROOT", file=False)
    runtime = Path(config["runtime"]).resolve()
    if (root not in runtime.parents or runtime == root
            or (runtime.exists() and (not runtime.is_dir() or runtime.is_symlink()))):
        raise R6ConfigError("RUNTIME_PATH_INVALID")
    for key in (
        "runpodctl", "packet", "platform_amendment", "authorization_envelope",
        "judge_raw", "archive", "bundle_receipt",
    ):
        resolved = _require_path(config[key], key.upper())
        if key != "runpodctl" and root not in resolved.parents:
            raise R6ConfigError(key.upper() + "_OUTSIDE_ROOT")
    bindings = {
        "runpodctl": "runpodctl_sha256",
        "packet": "packet_sha256",
        "platform_amendment": "platform_amendment_sha256",
        "authorization_envelope": "authorization_envelope_sha256",
        "judge_raw": "judge_raw_sha256",
        "archive": "archive_sha256",
        "bundle_receipt": "bundle_receipt_sha256",
    }
    for path_key, hash_key in bindings.items():
        expected = _require_hex(config[hash_key], hash_key.upper())
        if sha256(Path(config[path_key]).resolve()) != expected:
            raise R6ConfigError(hash_key.upper() + "_MISMATCH")
    _require_hex(config["tracer_binary_sha256"], "TRACER_BINARY_SHA256")
    if not isinstance(config["campaign_id"], str) or CAMPAIGN.fullmatch(config["campaign_id"]) is None:
        raise R6ConfigError("CAMPAIGN_ID_INVALID")
    if config["image"] != "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404":
        raise R6ConfigError("IMAGE_INVALID")
    launch_start = _utc(config["launch_start_utc"], "LAUNCH_START")
    launch_end = _utc(config["launch_end_utc"], "LAUNCH_END")
    stop = _utc(config["stop_utc"], "STOP")
    terminate = _utc(config["terminate_utc"], "TERMINATE")
    if not launch_start < launch_end <= stop < terminate:
        raise R6ConfigError("DEADLINE_ORDER_INVALID")
    if (launch_end - launch_start).total_seconds() > 2700:
        raise R6ConfigError("LAUNCH_WINDOW_TOO_LONG")
    if (terminate - launch_start).total_seconds() > 36_000:
        raise R6ConfigError("PAID_LIFETIME_TOO_LONG")
    maximum_attempts = config["max_attempts"]
    if (
        isinstance(maximum_attempts, bool)
        or not isinstance(maximum_attempts, int)
        or maximum_attempts < 1
        or maximum_attempts > (3 if version in {
            "ck-pdh3-r12-r6-config-v3", "ck-pdh3-r12-r6-config-v4"
        } else 1)
    ):
        raise R6ConfigError("MAX_ATTEMPTS_INVALID")
    if version.endswith("v3") and config["data_center_ids"] != ["US-MO-1"]:
        raise R6ConfigError("DATA_CENTER_IDS_INVALID")
    if version.endswith("v4"):
        allowed = [
            "EU-NL-1", "EUR-IS-2", "US-IL-1", "US-MO-1", "US-NC-1",
            "US-TX-3", "US-TX-4",
        ]
        if config["data_center_ids"] != allowed:
            raise R6ConfigError("DATA_CENTER_IDS_INVALID")
        if config["graphql_url"] != "https://api.runpod.io/graphql":
            raise R6ConfigError("GRAPHQL_URL_INVALID")
        if config["min_vcpu_count"] != 24:
            raise R6ConfigError("MIN_VCPU_COUNT_INVALID")
    if config["rate_ceiling_usd_per_hour"] != 0.99:
        raise R6ConfigError("RATE_CEILING_INVALID")
    if config["aggregate_cost_ceiling_usd"] != 12.0:
        raise R6ConfigError("COST_CEILING_INVALID")
    config["_config_path"] = selected
    config["_config_sha256"] = hashlib.sha256(raw).hexdigest()
    return config
