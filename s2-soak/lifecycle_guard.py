#!/usr/bin/env python3
"""Detached local exact-ID RunPod lifecycle guard.

This process runs on the operator host only. It receives one exact Pod ID,
expected name/campaign prefix, a hash-pinned runpodctl path, and absolute stop
and delete deadlines. It never enters the Pod and never transfers credentials.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


class GuardFailure(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, check=False)


class ChainLog:
    def __init__(self, path: Path) -> None:
        if path.exists():
            raise GuardFailure("LOG_ALREADY_EXISTS")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.previous = "0" * 64
        self.sequence = 0

    def emit(self, event: str, details: Any) -> dict[str, Any]:
        self.sequence += 1
        core = {"schema_version": "s2-guard-v1", "sequence": self.sequence,
                "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "monotonic_seconds": round(time.monotonic(), 3),
                "previous_hash": self.previous, "event": event,
                "details": details}
        record = {**core, "event_hash": hashlib.sha256(canonical(core)).hexdigest()}
        with self.path.open("ab") as handle:
            handle.write(canonical(record) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous = record["event_hash"]
        return record


def parse_json(result: subprocess.CompletedProcess[str]) -> Any:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise GuardFailure("MALFORMED_PROVIDER_JSON") from exc


def pod_get(cli: Path, pod_id: str) -> tuple[bool, dict[str, Any] | None, str]:
    result = run([str(cli), "pod", "get", pod_id, "--output", "json"])
    if result.returncode != 0:
        lowered = result.stdout.lower()
        if "404" in lowered or "not found" in lowered or "does not exist" in lowered:
            return False, None, result.stdout.strip()
        raise GuardFailure("POD_GET_FAILED:" + result.stdout[-500:])
    value = parse_json(result)
    if not isinstance(value, dict):
        raise GuardFailure("MALFORMED_POD_GET")
    return True, value, result.stdout.strip()


def campaign_active(cli: Path, campaign_prefix: str) -> list[dict[str, Any]]:
    result = run([str(cli), "pod", "list", "--all", "--output", "json"])
    if result.returncode != 0:
        raise GuardFailure("POD_LIST_FAILED:" + result.stdout[-500:])
    value = parse_json(result)
    if not isinstance(value, list):
        raise GuardFailure("MALFORMED_POD_LIST")
    return [item for item in value if isinstance(item, dict)
            and str(item.get("name", "")).startswith(campaign_prefix)
            and str(item.get("desiredStatus", "")).upper() not in
            {"EXITED", "TERMINATED", "DELETED"}]


def verify_identity(value: dict[str, Any], pod_id: str, expected_name: str,
                    campaign_prefix: str) -> None:
    if value.get("id") != pod_id:
        raise GuardFailure("POD_ID_MISMATCH")
    if value.get("name") != expected_name:
        raise GuardFailure("POD_NAME_MISMATCH")
    if not expected_name.startswith(campaign_prefix):
        raise GuardFailure("CAMPAIGN_MISMATCH")


def bounded_action(cli: Path, action: str, pod_id: str,
                   log: ChainLog) -> None:
    delays = (0, 2, 5)
    for attempt, delay in enumerate(delays, 1):
        if delay:
            time.sleep(delay)
        result = run([str(cli), "pod", action, pod_id, "--output", "json"])
        log.emit(action.upper() + "_ATTEMPT",
                 {"attempt": attempt, "exit": result.returncode,
                  "output_hash": hashlib.sha256(result.stdout.encode()).hexdigest()})
        if result.returncode == 0:
            return
        lowered = result.stdout.lower()
        if action == "delete" and ("404" in lowered or "not found" in lowered):
            return
    raise GuardFailure(action.upper() + "_RETRIES_EXHAUSTED")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runpodctl", type=Path, required=True)
    parser.add_argument("--runpodctl-sha256", required=True)
    parser.add_argument("--pod-id", required=True)
    parser.add_argument("--pod-name", required=True)
    parser.add_argument("--campaign-prefix", required=True)
    parser.add_argument("--stop-epoch", type=int, required=True)
    parser.add_argument("--delete-epoch", type=int, required=True)
    parser.add_argument("--heartbeat-seconds", type=int, default=30)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    if args.heartbeat_seconds < 1 or args.delete_epoch <= args.stop_epoch:
        raise GuardFailure("INVALID_DEADLINE")
    cli = args.runpodctl.resolve()
    if not cli.is_file() or not os.access(cli, os.X_OK):
        raise GuardFailure("CLI_NOT_EXECUTABLE")
    log = ChainLog(args.log.resolve())
    stopped = False
    try:
        if sha256_file(cli) != args.runpodctl_sha256:
            raise GuardFailure("CLI_HASH_MISMATCH")
        present, value, _ = pod_get(cli, args.pod_id)
        if not present or value is None:
            raise GuardFailure("POD_ABSENT_AT_BIND")
        verify_identity(value, args.pod_id, args.pod_name, args.campaign_prefix)
        log.emit("BOUND", {"pod_id": args.pod_id, "name": args.pod_name,
                           "campaign_prefix": args.campaign_prefix,
                           "cli_sha256": args.runpodctl_sha256,
                           "stop_epoch": args.stop_epoch,
                           "delete_epoch": args.delete_epoch})
        while True:
            if sha256_file(cli) != args.runpodctl_sha256:
                raise GuardFailure("CLI_HASH_MISMATCH")
            present, value, raw = pod_get(cli, args.pod_id)
            if not present:
                active = campaign_active(cli, args.campaign_prefix)
                if active:
                    raise GuardFailure("EXACT_ID_ABSENT_CAMPAIGN_ACTIVE")
                log.emit("TEARDOWN_GREEN", {"exact_id_absent": True,
                                             "campaign_active": []})
                return 0
            assert value is not None
            verify_identity(value, args.pod_id, args.pod_name, args.campaign_prefix)
            now = int(time.time())
            log.emit("HEARTBEAT", {"pod_id": args.pod_id,
                                   "provider_state": value.get("desiredStatus"),
                                   "provider_record_hash": hashlib.sha256(raw.encode()).hexdigest(),
                                   "seconds_to_stop": args.stop_epoch - now,
                                   "seconds_to_delete": args.delete_epoch - now})
            if now >= args.delete_epoch:
                bounded_action(cli, "delete", args.pod_id, log)
            elif now >= args.stop_epoch and not stopped:
                bounded_action(cli, "stop", args.pod_id, log)
                stopped = True
            time.sleep(args.heartbeat_seconds)
    except Exception as exc:
        log.emit("GUARD_BLOCKED", {"type": type(exc).__name__, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
