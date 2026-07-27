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
import re

import cloud_adapter
import hardening
import protocol


class CoordinatorFailure(RuntimeError):
    pass


REQUEST_NAME_RE = re.compile(r"^request-([0-9]{4})\.json$")


def verify_request_directory(requests: Path, expected_sequence: int,
                             processed: set[str]) -> None:
    expected_temporary = f"request-{expected_sequence:04d}.json.tmp"
    for entry in requests.iterdir():
        if entry.is_symlink() or not entry.is_file():
            raise CoordinatorFailure("REQUEST_ENTRY_UNSAFE")
        match = REQUEST_NAME_RE.fullmatch(entry.name)
        if match is None:
            if entry.name == expected_temporary:
                continue
            raise CoordinatorFailure("REQUEST_FILE_UNKNOWN")
        sequence = int(match.group(1))
        if sequence > expected_sequence:
            raise CoordinatorFailure("OUT_OF_ORDER_REQUEST")
        if sequence < expected_sequence:
            prior = protocol.decode_request(entry.read_bytes())
            if prior["sequence"] != sequence or prior["request_hash"] not in processed:
                raise CoordinatorFailure("STALE_REQUEST_MISMATCH")


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
    parser.add_argument("--custody-root", type=Path)
    parser.add_argument("--aws-session-expiry-epoch", type=int)
    parser.add_argument("--final-cloud-exchange-epoch", type=int)
    parser.add_argument("--session-margin-seconds", type=int, default=900)
    args = parser.parse_args()
    if not 1 <= args.expected_requests <= protocol.MAX_SEQUENCE:
        raise CoordinatorFailure("EXPECTED_REQUESTS_INVALID")
    if args.mode == "live" and args.config is None:
        raise CoordinatorFailure("LIVE_CONFIG_REQUIRED")
    if args.mode == "live" and any(value is None for value in (
            args.custody_root, args.aws_session_expiry_epoch,
            args.final_cloud_exchange_epoch)):
        raise CoordinatorFailure("LIVE_CUSTODY_OR_SESSION_GATE_REQUIRED")
    if (args.mode == "live" and
            (args.final_cloud_exchange_epoch < int(time.time()) or
             args.final_cloud_exchange_epoch > args.deadline_epoch)):
        raise CoordinatorFailure("FINAL_CLOUD_EXCHANGE_WINDOW_INVALID")
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
    custody = None
    if args.custody_root is not None:
        custody = hardening.CheckpointCustody(
            args.custody_root, args.campaign_id)
    if args.mode == "live":
        assert args.aws_session_expiry_epoch is not None
        assert args.final_cloud_exchange_epoch is not None
        session_receipt = hardening.validate_session_window(
            expires_epoch=args.aws_session_expiry_epoch,
            final_exchange_epoch=args.final_cloud_exchange_epoch,
            margin_seconds=args.session_margin_seconds,
        )
        hardening.write_atomic(evidence / "aws-session-window.json", session_receipt)
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
            verify_request_directory(requests, expected_sequence, processed)
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
            if custody is not None:
                custody_receipt = custody.capture(request, result)
                log.emit("CHECKPOINT_CUSTODY_COMMITTED", {
                    "sequence": expected_sequence,
                    "receipt_hash": custody_receipt["receipt_hash"],
                })
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
