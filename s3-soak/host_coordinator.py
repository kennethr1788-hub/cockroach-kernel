#!/usr/bin/env python3
"""Detached S3 host coordinator with strict sequence and call ceilings."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import time
from typing import Any

import cloud_adapter
import protocol


class CoordinatorFailure(RuntimeError):
    pass


def write_atomic(path: Path, value: dict[str, Any]) -> None:
    raw = protocol.canonical(value)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


class ChainLog:
    def __init__(self, path: Path, campaign_id: str) -> None:
        if path.exists():
            raise CoordinatorFailure("LOG_EXISTS")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.campaign_id = campaign_id
        self.previous = protocol.GENESIS_HASH
        self.sequence = 0

    def emit(self, event: str, details: Any) -> dict[str, Any]:
        self.sequence += 1
        core = {
            "version": "s3-coordinator-log-v1",
            "campaign_id": self.campaign_id,
            "sequence": self.sequence,
            "previous_hash": self.previous,
            "event": event,
            "details": details,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "monotonic_ns": time.monotonic_ns(),
        }
        record = {**core, "event_hash": protocol.sha256(core)}
        with self.path.open("ab") as handle:
            handle.write(protocol.canonical(record) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous = record["event_hash"]
        return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bridge-root", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--expected-requests", type=int, required=True)
    parser.add_argument("--lambda-call-ceiling", type=int, required=True)
    parser.add_argument("--cockroach-operation-ceiling", type=int, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--mode", choices=("live", "fixture", "offline-refusal"),
                        required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--heartbeat-seconds", type=int, default=5)
    parser.add_argument("--completion-marker", type=Path)
    args = parser.parse_args()
    if not 1 <= args.expected_requests <= protocol.MAX_SEQUENCE:
        raise CoordinatorFailure("EXPECTED_REQUESTS_INVALID")
    if args.mode == "live" and args.config is None:
        raise CoordinatorFailure("LIVE_CONFIG_REQUIRED")
    if args.deadline_epoch <= int(time.time()):
        raise CoordinatorFailure("DEADLINE_INVALID")
    if args.lambda_call_ceiling < args.expected_requests:
        raise CoordinatorFailure("LAMBDA_CEILING_TOO_LOW")
    if args.cockroach_operation_ceiling < args.expected_requests * 9:
        raise CoordinatorFailure("COCKROACH_CEILING_TOO_LOW")

    bridge = args.bridge_root.resolve()
    requests = bridge / "requests"
    results = bridge / "results"
    for path in (requests, results):
        path.mkdir(parents=True, exist_ok=True)
    evidence = args.evidence_root.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    log = ChainLog(evidence / "coordinator.ndjson", args.campaign_id)
    processed: set[str] = set()
    expected_sequence = 1
    parent_hash = protocol.GENESIS_HASH
    lambda_calls = 0
    cockroach_operations = 0
    stopped = False

    def stop(_signum: int, _frame: Any) -> None:
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    log.emit("COORDINATOR_START", {
        "mode": args.mode,
        "expected_requests": args.expected_requests,
        "lambda_call_ceiling": args.lambda_call_ceiling,
        "cockroach_operation_ceiling": args.cockroach_operation_ceiling,
        "deadline_epoch": args.deadline_epoch,
    })
    last_heartbeat = 0.0
    try:
        while expected_sequence <= args.expected_requests:
            if stopped:
                raise CoordinatorFailure("COORDINATOR_STOPPED")
            if int(time.time()) >= args.deadline_epoch:
                raise CoordinatorFailure("COORDINATOR_DEADLINE")
            now = time.monotonic()
            if now - last_heartbeat >= args.heartbeat_seconds:
                log.emit("HEARTBEAT", {
                    "next_sequence": expected_sequence,
                    "processed": len(processed),
                    "lambda_calls": lambda_calls,
                    "cockroach_operations": cockroach_operations,
                })
                last_heartbeat = now
            request_path = requests / f"request-{expected_sequence:04d}.json"
            if not request_path.exists():
                time.sleep(0.1)
                continue
            raw = request_path.read_bytes()
            request = protocol.decode_request(raw)
            if request["campaign_id"] != args.campaign_id:
                raise CoordinatorFailure("CAMPAIGN_MISMATCH")
            if request["sequence"] != expected_sequence:
                raise CoordinatorFailure("OUT_OF_ORDER_REQUEST")
            if request["parent_hash"] != parent_hash:
                raise CoordinatorFailure("PARENT_HASH_MISMATCH")
            if request["request_hash"] in processed:
                raise CoordinatorFailure("DUPLICATE_REQUEST")
            log.emit("REQUEST_ACCEPTED", {
                "sequence": expected_sequence,
                "request_hash": request["request_hash"],
                "operation": request["operation"],
            })
            if args.mode == "offline-refusal":
                log.emit("COORDINATOR_OFFLINE_REFUSAL", {
                    "sequence": expected_sequence,
                    "request_hash": request["request_hash"],
                    "stable_reason_code": "COORDINATOR_UNAVAILABLE",
                })
                return 73
            call_root = evidence / f"call-{expected_sequence:04d}"
            if args.mode == "live":
                metrics, hashes = cloud_adapter.run_live(request, args.config, call_root)
            else:
                metrics, hashes = cloud_adapter.run_fixture(request)
            lambda_calls += int(metrics["lambda_invocations"])
            cockroach_operations += int(metrics["cockroach_operations"])
            if lambda_calls > args.lambda_call_ceiling:
                raise CoordinatorFailure("LAMBDA_CALL_CEILING")
            if cockroach_operations > args.cockroach_operation_ceiling:
                raise CoordinatorFailure("COCKROACH_OPERATION_CEILING")
            result = protocol.make_result(request, metrics, hashes)
            result_path = results / f"result-{expected_sequence:04d}.json"
            write_atomic(result_path, result)
            log.emit("RESULT_COMMITTED", {
                "sequence": expected_sequence,
                "request_hash": request["request_hash"],
                "result_hash": result["result_hash"],
                "lambda_calls": lambda_calls,
                "cockroach_operations": cockroach_operations,
            })
            processed.add(request["request_hash"])
            parent_hash = request["request_hash"]
            expected_sequence += 1
        if args.completion_marker is not None:
            marker = args.completion_marker.resolve()
            while not marker.exists():
                if stopped:
                    raise CoordinatorFailure("COORDINATOR_STOPPED")
                if int(time.time()) >= args.deadline_epoch:
                    raise CoordinatorFailure("COMPLETION_MARKER_DEADLINE")
                now = time.monotonic()
                if now - last_heartbeat >= args.heartbeat_seconds:
                    log.emit("HEARTBEAT", {
                        "next_sequence": expected_sequence,
                        "processed": len(processed),
                        "lambda_calls": lambda_calls,
                        "cockroach_operations": cockroach_operations,
                        "awaiting_completion_marker": True,
                    })
                    last_heartbeat = now
                time.sleep(0.2)
        log.emit("COORDINATOR_GREEN", {
            "processed": len(processed),
            "lambda_calls": lambda_calls,
            "cockroach_operations": cockroach_operations,
        })
        return 0
    except Exception as exc:
        log.emit("COORDINATOR_BLOCKED", {
            "type": type(exc).__name__,
            "error_hash": protocol.sha256(str(exc).encode("utf-8")),
        })
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
