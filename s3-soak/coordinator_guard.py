#!/usr/bin/env python3
"""Detached guard for the S3 coordinator, bridge, and exact RunPod identity."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any

import protocol
import hardening


class GuardFailure(RuntimeError):
    pass


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, check=False, timeout=30)


class ChainLog:
    def __init__(self, path: Path, campaign: str) -> None:
        if path.exists():
            raise GuardFailure("LOG_EXISTS")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.campaign = campaign
        self.previous = protocol.GENESIS_HASH
        self.sequence = 0

    def emit(self, event: str, details: Any) -> None:
        self.sequence += 1
        core = {
            "version": "s3-coordinator-guard-log-v1",
            "campaign_id": self.campaign, "sequence": self.sequence,
            "previous_hash": self.previous, "event": event, "details": details,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "monotonic_ns": time.monotonic_ns(),
        }
        value = {**core, "event_hash": protocol.sha256(core)}
        with self.path.open("ab") as handle:
            handle.write(protocol.canonical(value) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous = value["event_hash"]


def read_chain(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if len(raw) > 16 * 1024 * 1024:
        raise GuardFailure("CHAIN_LOG_OVERSIZED")
    if raw and not raw.endswith(b"\n"):
        complete, separator, _partial = raw.rpartition(b"\n")
        raw = complete + separator
    previous = protocol.GENESIS_HASH
    records = []
    for expected, line in enumerate(raw.splitlines(), 1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise GuardFailure("CHAIN_JSON_INVALID") from exc
        if protocol.canonical(value) != line:
            raise GuardFailure("CHAIN_NON_CANONICAL")
        if value.get("sequence") != expected or value.get("previous_hash") != previous:
            raise GuardFailure("CHAIN_SEQUENCE_INVALID")
        event_hash = value.get("event_hash")
        core = {key: item for key, item in value.items() if key != "event_hash"}
        if event_hash != protocol.sha256(core):
            raise GuardFailure("CHAIN_HASH_INVALID")
        previous = event_hash
        records.append(value)
    if not records:
        raise GuardFailure("CHAIN_EMPTY")
    return records


def pod_get(cli: Path, pod_id: str) -> dict[str, Any] | None:
    result = run([str(cli), "pod", "get", pod_id, "--output", "json"])
    if result.returncode != 0:
        lowered = result.stdout.lower()
        if "404" in lowered or "not found" in lowered or "does not exist" in lowered:
            return None
        raise GuardFailure("POD_GET_FAILED")
    value = json.loads(result.stdout)
    if not isinstance(value, dict):
        raise GuardFailure("POD_GET_INVALID")
    return value


def verify_pod(value: dict[str, Any], pod_id: str, name: str,
               campaign_prefix: str) -> None:
    if value.get("id") != pod_id or value.get("name") != name:
        raise GuardFailure("POD_IDENTITY_MISMATCH")
    if not name.startswith(campaign_prefix):
        raise GuardFailure("POD_CAMPAIGN_MISMATCH")


def teardown(cli: Path, pod_id: str, log: ChainLog) -> None:
    for action in ("stop", "delete"):
        succeeded = False
        for attempt, delay in enumerate((0, 2, 5), 1):
            if delay:
                time.sleep(delay)
            result = run([str(cli), "pod", action, pod_id, "--output", "json"])
            log.emit(action.upper() + "_ATTEMPT", {
                "attempt": attempt, "exit": result.returncode,
                "output_hash": protocol.sha256(result.stdout.encode()),
            })
            lowered = result.stdout.lower()
            if result.returncode == 0 or (action == "delete" and
                                           ("404" in lowered or "not found" in lowered)):
                succeeded = True
                break
        if not succeeded:
            raise GuardFailure(action.upper() + "_FAILED")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coordinator-pid", type=int, required=True)
    parser.add_argument("--bridge-pid", type=int, required=True)
    parser.add_argument("--runpod-guard-pid", type=int, required=True)
    parser.add_argument("--coordinator-log", type=Path, required=True)
    parser.add_argument("--bridge-log", type=Path, required=True)
    parser.add_argument("--runpod-guard-log", type=Path, required=True)
    parser.add_argument("--completion-marker", type=Path, required=True)
    parser.add_argument("--protocol-file", type=Path, required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--resource-allowlist", type=Path, required=True)
    parser.add_argument("--resource-allowlist-sha256", required=True)
    parser.add_argument("--lambda-call-ceiling", type=int, required=True)
    parser.add_argument("--cockroach-operation-ceiling", type=int, required=True)
    parser.add_argument("--runpodctl", type=Path, required=True)
    parser.add_argument("--runpodctl-sha256", required=True)
    parser.add_argument("--pod-id", required=True)
    parser.add_argument("--pod-name", required=True)
    parser.add_argument("--campaign-prefix", required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--stale-seconds", type=int, default=90)
    parser.add_argument("--startup-grace-seconds", type=int, default=60)
    parser.add_argument("--heartbeat-seconds", type=int, default=5)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--stop-marker", type=Path, required=True)
    args = parser.parse_args()
    if (min(args.coordinator_pid, args.bridge_pid, args.runpod_guard_pid) <= 1 or
            args.deadline_epoch <= int(time.time()) or
            not 1 <= args.heartbeat_seconds <= 30):
        raise GuardFailure("ARGUMENT_INVALID")
    protocol_file = args.protocol_file.resolve()
    allowlist = args.resource_allowlist.resolve()
    cli = args.runpodctl.resolve()
    if (file_hash(protocol_file) != args.protocol_sha256 or
            file_hash(allowlist) != args.resource_allowlist_sha256 or
            file_hash(cli) != args.runpodctl_sha256):
        raise GuardFailure("PINNED_HASH_MISMATCH")
    pod = pod_get(cli, args.pod_id)
    if pod is None:
        raise GuardFailure("POD_ABSENT_AT_BIND")
    verify_pod(pod, args.pod_id, args.pod_name, args.campaign_prefix)
    log = ChainLog(args.log.resolve(), args.campaign_prefix.rstrip("-"))
    started = time.monotonic()
    last_sizes: dict[Path, tuple[int, float]] = {}
    paths = [args.coordinator_log.resolve(), args.bridge_log.resolve(),
             args.runpod_guard_log.resolve()]
    log.emit("BOUND", {
        "coordinator_pid": args.coordinator_pid,
        "bridge_pid": args.bridge_pid,
        "runpod_guard_pid": args.runpod_guard_pid,
        "pod_id": args.pod_id, "pod_name": args.pod_name,
        "protocol_sha256": args.protocol_sha256,
        "resource_allowlist_sha256": args.resource_allowlist_sha256,
        "lambda_call_ceiling": args.lambda_call_ceiling,
        "cockroach_operation_ceiling": args.cockroach_operation_ceiling,
        "deadline_epoch": args.deadline_epoch,
        "request_chain_root": protocol.GENESIS_HASH,
    })
    try:
        while int(time.time()) < args.deadline_epoch:
            if file_hash(protocol_file) != args.protocol_sha256:
                raise GuardFailure("PROTOCOL_HASH_DRIFT")
            if file_hash(allowlist) != args.resource_allowlist_sha256:
                raise GuardFailure("ALLOWLIST_HASH_DRIFT")
            if file_hash(cli) != args.runpodctl_sha256:
                raise GuardFailure("CLI_HASH_DRIFT")
            now = time.monotonic()
            parsed: dict[Path, list[dict[str, Any]]] = {}
            for path in paths:
                if not path.exists():
                    if now - started > args.startup_grace_seconds:
                        raise GuardFailure("GUARDED_LOG_MISSING")
                    continue
                guarded_records = read_chain(path)
                parsed[path] = guarded_records
                terminal_event = {
                    args.coordinator_log.resolve(): "COORDINATOR_GREEN",
                    args.bridge_log.resolve(): "BRIDGE_GREEN",
                    args.runpod_guard_log.resolve(): "TEARDOWN_GREEN",
                }[path]
                terminal_green = guarded_records[-1].get("event") == terminal_event
                size = path.stat().st_size
                prior_size, prior_time = last_sizes.get(path, (-1, now))
                if size != prior_size:
                    prior_time = now
                elif not terminal_green and now - prior_time > args.stale_seconds:
                    raise GuardFailure("GUARDED_LOG_STALE")
                last_sizes[path] = (size, prior_time)
            coordinator_records = parsed.get(args.coordinator_log.resolve(), [])
            bridge_records = parsed.get(args.bridge_log.resolve(), [])
            runpod_records = parsed.get(args.runpod_guard_log.resolve(), [])
            if coordinator_records:
                latest = coordinator_records[-1]
                if latest.get("event") == "COORDINATOR_BLOCKED":
                    raise GuardFailure("COORDINATOR_REPORTED_BLOCKED")
                details = latest.get("details", {})
                if isinstance(details, dict):
                    if int(details.get("lambda_calls", 0)) > args.lambda_call_ceiling:
                        raise GuardFailure("LAMBDA_CEILING_BREACH")
                    if int(details.get("cockroach_operations", 0)) > args.cockroach_operation_ceiling:
                        raise GuardFailure("COCKROACH_CEILING_BREACH")
            for guarded_records in parsed.values():
                if str(guarded_records[-1].get("event", "")).endswith("BLOCKED"):
                    raise GuardFailure("GUARDED_PROCESS_BLOCKED")
            if args.completion_marker.resolve().exists():
                if (coordinator_records and
                        coordinator_records[-1].get("event") == "COORDINATOR_GREEN" and
                        bridge_records and
                        bridge_records[-1].get("event") == "BRIDGE_GREEN"):
                    log.emit("COORDINATOR_GUARD_GREEN", {"completion_marker": True})
                    return 0
            process_states = (
                (args.coordinator_pid, "COORDINATOR_PROCESS_EXITED", False),
                (args.bridge_pid, "BRIDGE_PROCESS_EXITED",
                 bool(bridge_records and bridge_records[-1].get("event") == "BRIDGE_GREEN")),
                (args.runpod_guard_pid, "RUNPOD_GUARD_PROCESS_EXITED",
                 bool(runpod_records and runpod_records[-1].get("event") == "TEARDOWN_GREEN")),
            )
            for process_id, reason, allowed_exit in process_states:
                if allowed_exit:
                    continue
                try:
                    os.kill(process_id, 0)
                except ProcessLookupError as exc:
                    raise GuardFailure(reason) from exc
            log.emit("HEARTBEAT", {"guarded_logs": len(parsed),
                                    "completion_marker": False})
            time.sleep(args.heartbeat_seconds)
        raise GuardFailure("GUARD_DEADLINE")
    except Exception as exc:
        shutdown_receipt: dict[str, Any] | None = None
        try:
            shutdown_receipt = hardening.coordinated_local_shutdown([
                ("bridge", args.bridge_pid),
                ("coordinator", args.coordinator_pid),
            ])
        except Exception as shutdown_exc:
            # Preserve the primary failure and still proceed to exact worker
            # teardown. The shutdown failure is hash-bound, never hidden.
            log.emit("LOCAL_SHUTDOWN_BLOCKED", {
                "type": type(shutdown_exc).__name__,
                "reason_hash": protocol.sha256(str(shutdown_exc).encode()),
            })
        marker = args.stop_marker.resolve()
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_bytes(protocol.canonical({
            "version": "s3-stop-marker-v1", "pod_id": args.pod_id,
            "reason_hash": protocol.sha256(str(exc).encode()),
        }) + b"\n")
        log.emit("COORDINATOR_GUARD_BLOCKED", {
            "type": type(exc).__name__,
            "reason_hash": protocol.sha256(str(exc).encode()),
            "stop_marker": True,
            "local_shutdown_receipt_hash": (
                shutdown_receipt["receipt_hash"] if shutdown_receipt else None
            ),
            "worker_shutdown": "EXACT_POD_STOP_DELETE",
        })
        teardown(cli, args.pod_id, log)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
