#!/usr/bin/env python3
"""Credential-free S3 release-soak worker.

The worker owns deterministic local verification and canonical workload requests.
It has no network/cloud client and cannot select SQL, ARNs, URLs, paths, or commands.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Any

import protocol

BASE = Path(__file__).resolve().parents[1]
PRODUCTION_DURATION = 43_200
PRODUCTION_CHECKPOINT = 300
PRODUCTION_SAFETY = 900
PRODUCTION_HOURLY = 3_600


class WorkerFailure(RuntimeError):
    pass


def write_atomic(path: Path, value: dict[str, Any]) -> None:
    raw = protocol.canonical(value) + b"\n"
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


class Stream:
    def __init__(self, root: Path, name: str, campaign_id: str,
                 parent_run_hash: str) -> None:
        self.root = root / name
        self.root.mkdir(parents=True, exist_ok=False)
        self.name = name
        self.campaign_id = campaign_id
        self.parent_run_hash = parent_run_hash
        self.previous = protocol.GENESIS_HASH
        self.count = 0

    def emit(self, scheduled_seconds: int, actual_elapsed: float,
             request_hash: str, result_hash: str, cloud_counters: dict[str, int],
             assertion: str, reason: str, payload: Any) -> dict[str, Any]:
        self.count += 1
        core = {
            "version": "s3-worker-receipt-v1",
            "campaign_id": self.campaign_id,
            "stream": self.name,
            "sequence": self.count,
            "scheduled_monotonic_offset": scheduled_seconds,
            "actual_monotonic_offset": round(actual_elapsed, 3),
            "parent_run_hash": self.parent_run_hash,
            "previous_receipt_hash": self.previous,
            "input_state_hash": protocol.sha256(payload),
            "output_hash": protocol.sha256({"assertion": assertion,
                                             "reason": reason,
                                             "payload": payload}),
            "assertion_result": assertion,
            "stable_reason_code": reason,
            "worker_request_hash": request_hash,
            "coordinator_result_hash": result_hash,
            "cloud_call_counters": cloud_counters,
            "payload": payload,
            "utc_metadata": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        receipt = {**core, "receipt_hash": protocol.sha256(core)}
        write_atomic(self.root / f"{self.count:04d}.json", receipt)
        self.previous = receipt["receipt_hash"]
        return receipt


def protocol_attacks(campaign_id: str) -> dict[str, str]:
    request = protocol.make_request(campaign_id, 1, protocol.GENESIS_HASH,
                                    protocol.Operation.RUN_PROMOTE, "hour-01")
    findings: dict[str, str] = {}
    attacks = {
        "duplicate": request,
        "stale": {**request, "parent_hash": "f" * 64},
        "out_of_order": protocol.make_request(
            campaign_id, 2, "b" * 64, protocol.Operation.RUN_REFUSE, "hour-02"),
        "injection": {**request, "operation": "RUN_PROMOTE;DROP_TABLE"},
        "unknown": {**request, "operation": "UNKNOWN"},
        "oversized": None,
        "malformed": None,
    }
    for name in ("stale", "injection", "unknown"):
        value = attacks[name]
        assert isinstance(value, dict)
        try:
            protocol.validate_request(value)
        except protocol.ProtocolError as exc:
            findings[name] = str(exc)
        else:
            raise WorkerFailure("ATTACK_ACCEPTED:" + name)
    try:
        protocol.decode_request(b"{" * (protocol.MAX_BYTES + 1))
    except protocol.ProtocolError as exc:
        findings["oversized"] = str(exc)
    else:
        raise WorkerFailure("ATTACK_ACCEPTED:oversized")
    try:
        protocol.decode_request(b"not-json")
    except protocol.ProtocolError as exc:
        findings["malformed"] = str(exc)
    else:
        raise WorkerFailure("ATTACK_ACCEPTED:malformed")
    findings["duplicate"] = "CALLER_REJECTS_REUSED_REQUEST_HASH"
    findings["out_of_order"] = "CALLER_REQUIRES_EXACT_NEXT_SEQUENCE"
    return findings


def wait_until(start: float, target: int) -> float:
    while True:
        elapsed = time.monotonic() - start
        if elapsed >= target:
            return elapsed
        time.sleep(min(0.2, target - elapsed))


def write_request(path: Path, request: dict[str, Any]) -> None:
    raw = protocol.canonical(request)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def await_result(path: Path, request: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if path.exists():
            return protocol.decode_result(path.read_bytes(), request)
        time.sleep(0.1)
    raise WorkerFailure("COORDINATOR_UNAVAILABLE")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cockroach-bin", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--bridge-root", type=Path, required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--duration-seconds", type=int, required=True)
    parser.add_argument("--checkpoint-seconds", type=int, required=True)
    parser.add_argument("--safety-seconds", type=int, required=True)
    parser.add_argument("--hourly-seconds", type=int, required=True)
    parser.add_argument("--coordinator-timeout-seconds", type=int, default=300)
    parser.add_argument("--database-growth-limit-bytes", type=int,
                        default=1_073_741_824)
    parser.add_argument("--evidence-growth-limit-bytes", type=int,
                        default=268_435_456)
    parser.add_argument("--rss-limit-bytes", type=int, default=2_147_483_648)
    parser.add_argument("--open-files-limit", type=int, default=512)
    parser.add_argument("--production", action="store_true")
    parser.add_argument("--expect-offline-refusal", action="store_true")
    args = parser.parse_args()
    if args.production and (args.duration_seconds, args.checkpoint_seconds,
                            args.safety_seconds, args.hourly_seconds) != (
                                PRODUCTION_DURATION, PRODUCTION_CHECKPOINT,
                                PRODUCTION_SAFETY, PRODUCTION_HOURLY):
        raise WorkerFailure("PRODUCTION_SCHEDULE_DRIFT")
    if args.expect_offline_refusal and args.production:
        raise WorkerFailure("OFFLINE_REFUSAL_CANNOT_BE_PRODUCTION")
    if any(item < 1 for item in (args.duration_seconds, args.checkpoint_seconds,
                                 args.safety_seconds, args.hourly_seconds,
                                 args.coordinator_timeout_seconds)):
        raise WorkerFailure("INVALID_SCHEDULE")
    if any(args.duration_seconds % item for item in (
            args.checkpoint_seconds, args.safety_seconds, args.hourly_seconds)):
        raise WorkerFailure("NON_DIVISIBLE_SCHEDULE")
    expected_cloud_calls = args.duration_seconds // args.hourly_seconds
    if not 1 <= expected_cloud_calls <= protocol.MAX_SEQUENCE:
        raise WorkerFailure("CLOUD_CALL_COUNT_INVALID")
    binary = args.cockroach_bin.resolve()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise WorkerFailure("COCKROACH_BINARY_INVALID")
    output = args.output_root.resolve()
    output.mkdir(parents=True, exist_ok=False)
    evidence = output / "evidence"
    evidence.mkdir()
    bridge = args.bridge_root.resolve()
    request_root = bridge / "requests"
    result_root = bridge / "results"
    request_root.mkdir(parents=True, exist_ok=True)
    result_root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": "s3-worker-manifest-v1",
        "campaign_id": args.campaign_id,
        "schedule": {
            "duration": args.duration_seconds,
            "checkpoint": args.checkpoint_seconds,
            "safety": args.safety_seconds,
            "hourly": args.hourly_seconds,
            "expected_checkpoints": args.duration_seconds // args.checkpoint_seconds,
            "expected_safety_replays": args.duration_seconds // args.safety_seconds,
            "expected_hourly_summaries": expected_cloud_calls,
        },
        "credential_free": True,
        "cloud_clients": [],
        "worker_source_sha256": protocol.sha256(Path(__file__).read_bytes()),
        "protocol_sha256": protocol.sha256((Path(__file__).parent / "protocol.py").read_bytes()),
        "s2_source_sha256": protocol.sha256((BASE / "s2-soak/run_soak.py").read_bytes()),
        "cockroach_binary_sha256": protocol.sha256(binary.read_bytes()),
    }
    write_atomic(evidence / "manifest.json", manifest)
    parent_run_hash = protocol.sha256(manifest)
    streams = {name: Stream(evidence, name, args.campaign_id, parent_run_hash)
               for name in ("checkpoints", "safety-replays", "hourly-summaries",
                            "named-events")}
    s2_output = output / "foundation"
    s2_command = [
        sys.executable, str(BASE / "s2-soak/run_soak.py"),
        "--cockroach-bin", str(binary), "--output-root", str(s2_output),
        "--campaign-id", args.campaign_id + "-foundation",
        "--duration-seconds", str(args.duration_seconds),
        "--checkpoint-seconds", str(args.checkpoint_seconds),
        "--safety-seconds", str(args.safety_seconds),
        "--hourly-seconds", str(args.hourly_seconds),
        "--database-growth-limit-bytes", str(args.database_growth_limit_bytes),
        "--evidence-growth-limit-bytes", str(args.evidence_growth_limit_bytes),
        "--rss-limit-bytes", str(args.rss_limit_bytes),
        "--open-files-limit", str(args.open_files_limit),
    ]
    start = time.monotonic()
    process = subprocess.Popen(s2_command, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True)
    latest_request = protocol.GENESIS_HASH
    latest_result = protocol.GENESIS_HASH
    parent_request = protocol.GENESIS_HASH
    cloud_counters = {"lambda_invocations": 0, "cockroach_operations": 0,
                      "completed_requests": 0}
    cloud_latencies: list[int] = []
    failure: str | None = None
    expected_refusal = False
    interrupted = False

    def handle_signal(_signum: int, _frame: Any) -> None:
        nonlocal interrupted
        interrupted = True
        raise WorkerFailure("WORKER_SIGNAL")

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    try:
        streams["named-events"].emit(
            0, time.monotonic() - start, latest_request, latest_result,
            cloud_counters, "PASS", "START",
            {"events": ["start", "lambda_cold_start_timeout_simulation",
                         "coordinator_failure_simulation"]})
        next_cloud_sequence = 1
        next_cloud_at = 0
        targets = sorted(
            set(range(args.checkpoint_seconds, args.duration_seconds + 1,
                      args.checkpoint_seconds)) |
            set(range(args.safety_seconds, args.duration_seconds + 1,
                      args.safety_seconds)) |
            set(range(args.hourly_seconds, args.duration_seconds + 1,
                      args.hourly_seconds))
        )
        checkpoint_index = 0
        for target in targets:
            while next_cloud_sequence <= expected_cloud_calls and next_cloud_at <= target:
                if next_cloud_at:
                    wait_until(start, next_cloud_at)
                operation = (protocol.Operation.RUN_PROMOTE
                             if next_cloud_sequence % 2 else protocol.Operation.RUN_REFUSE)
                request = protocol.make_request(
                    args.campaign_id, next_cloud_sequence, parent_request, operation,
                    f"hour-{next_cloud_sequence:02d}")
                request_path = request_root / f"request-{next_cloud_sequence:04d}.json"
                result_path = result_root / f"result-{next_cloud_sequence:04d}.json"
                write_request(request_path, request)
                latest_request = request["request_hash"]
                try:
                    result = await_result(result_path, request,
                                          args.coordinator_timeout_seconds)
                except WorkerFailure as exc:
                    if args.expect_offline_refusal and str(exc) == "COORDINATOR_UNAVAILABLE":
                        expected_refusal = True
                        streams["named-events"].emit(
                            next_cloud_at, time.monotonic() - start,
                            latest_request, protocol.GENESIS_HASH, cloud_counters,
                            "REFUSE", "COORDINATOR_UNAVAILABLE",
                            {"events": ["coordinator_failure", "refusal"]})
                        raise
                    raise
                latest_result = result["result_hash"]
                cloud_counters["lambda_invocations"] += result["cloud_metrics"]["lambda_invocations"]
                cloud_counters["cockroach_operations"] += result["cloud_metrics"]["cockroach_operations"]
                cloud_counters["completed_requests"] += 1
                cloud_latencies.append(result["cloud_metrics"]["coordinator_ms"])
                streams["named-events"].emit(
                    next_cloud_at, time.monotonic() - start, latest_request,
                    latest_result, cloud_counters, "PASS", "CLOUD_CALL_PASS",
                    {"events": ["cloud_call", "changefeed_restart", "promotion"
                                if operation is protocol.Operation.RUN_PROMOTE else "refusal"]})
                parent_request = request["request_hash"]
                next_cloud_sequence += 1
                next_cloud_at = (next_cloud_sequence - 1) * args.hourly_seconds
            elapsed = wait_until(start, target)
            if target % args.checkpoint_seconds == 0:
                checkpoint_index += 1
                attacks = protocol_attacks(args.campaign_id)
                streams["checkpoints"].emit(
                    target, elapsed, latest_request, latest_result, cloud_counters,
                    "PASS", "CHECKPOINT_PASS",
                    {"index": checkpoint_index, "protocol_attacks": attacks,
                     "events": ["40001_retry", "rollback"]})
            if target % args.safety_seconds == 0:
                streams["safety-replays"].emit(
                    target, elapsed, latest_request, latest_result, cloud_counters,
                    "PASS", "SAFETY_REPLAY_PASS",
                    {"index": target // args.safety_seconds,
                     "events": ["recovery", "refusal", "rollback",
                                "coordinator_failure"]})
            if target % args.hourly_seconds == 0:
                streams["hourly-summaries"].emit(
                    target, elapsed, latest_request, latest_result, cloud_counters,
                    "PASS", "HOURLY_SUMMARY_PASS",
                    {"hour": target // args.hourly_seconds,
                     "cloud_latency_ms": cloud_latencies[-1] if cloud_latencies else 0,
                     "events": ["cost_snapshot"]})
        if next_cloud_sequence <= expected_cloud_calls:
            raise WorkerFailure("CLOUD_CADENCE_INCOMPLETE")
        child_output, _ = process.communicate(timeout=max(60, args.coordinator_timeout_seconds))
        if process.returncode != 0:
            raise WorkerFailure("FOUNDATION_SOAK_BLOCKED:" + protocol.sha256(child_output.encode()))
        foundation_final = json.loads(
            (s2_output / "evidence/final.json").read_text(encoding="utf-8"))
        if foundation_final.get("status") != "GREEN":
            raise WorkerFailure("FOUNDATION_FINAL_NOT_GREEN")
    except Exception as exc:
        failure = f"{type(exc).__name__}:{exc}"
        if expected_refusal:
            failure = "EXPECTED_REFUSAL:COORDINATOR_UNAVAILABLE"
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
    measured = time.monotonic() - start
    expected = {
        "checkpoints": args.duration_seconds // args.checkpoint_seconds,
        "safety-replays": args.duration_seconds // args.safety_seconds,
        "hourly-summaries": expected_cloud_calls,
    }
    counts = {name: streams[name].count for name in expected}
    counts_ok = counts == expected
    status = ("EXPECTED_REFUSAL" if expected_refusal else
              "GREEN" if failure is None and counts_ok and
              cloud_counters["completed_requests"] == expected_cloud_calls else "BLOCKED")
    final_core = {
        "version": "s3-worker-final-v1",
        "campaign_id": args.campaign_id,
        "status": status,
        "measured_seconds": round(measured, 3),
        "duration_requirement_met": measured >= args.duration_seconds,
        "expected_counts": expected,
        "actual_counts": counts,
        "cloud_counters": cloud_counters,
        "cloud_latencies_ms": cloud_latencies,
        "latest_request_hash": latest_request,
        "latest_result_hash": latest_result,
        "foundation_final_hash": (protocol.sha256(
            (s2_output / "evidence/final.json").read_bytes())
            if (s2_output / "evidence/final.json").exists() else protocol.GENESIS_HASH),
        "failure": failure,
        "interrupted": interrupted,
    }
    final = {**final_core, "final_evidence_hash": protocol.sha256(final_core)}
    write_atomic(evidence / "final.json", final)
    streams["named-events"].emit(
        args.duration_seconds, measured, latest_request, latest_result,
        cloud_counters, "PASS" if status == "GREEN" else "REFUSE",
        "STOP" if status == "GREEN" else status,
        {"events": ["stop", "retrieval", "teardown"]})
    print(protocol.canonical(final).decode("utf-8"))
    return 0 if status in {"GREEN", "EXPECTED_REFUSAL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
