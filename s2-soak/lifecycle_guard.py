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
import re
import subprocess
import time
from pathlib import Path
from typing import Any


class GuardFailure(RuntimeError):
    pass


class TransientProviderError(GuardFailure):
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


def run(command: list[str], *, timeout_seconds: float) -> subprocess.CompletedProcess[str]:
    if timeout_seconds <= 0:
        raise TransientProviderError("PROVIDER_COMMAND_DEADLINE_EXCEEDED")
    try:
        return subprocess.run(
            command,
            text=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TransientProviderError(
            "PROVIDER_COMMAND_TIMEOUT:" + Path(command[0]).name
        ) from exc


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
        raise TransientProviderError("MALFORMED_PROVIDER_JSON") from exc


def structured_pod_not_found(raw: str) -> bool:
    """Accept absence only from a JSON error envelope bound to a missing Pod.

    Provider command output is untrusted.  A log line, billing identifier, or
    arbitrary message that happens to contain ``404`` is not deletion proof.
    The accepted schemas are deliberately narrow: a flat JSON error object, or
    a JSON object whose ``error`` member is an error object.  The selected
    object must carry a numeric HTTP-style 404 code and a human-readable
    message that identifies a Pod as not found/nonexistent.
    """
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        # runpodctl v2.7.2 writes one valid JSON envelope, then Cobra usage
        # text and a second malformed rendering.  Accept only that exact
        # command-scoped prefix; arbitrary text after a valid 404 remains
        # insufficient proof.
        first, separator, remainder = raw.partition("\n")
        expected_remainder = (
            "Usage:\n"
            "  runpodctl pod get <pod-id> [flags]\n\n"
            "Flags:\n"
            "  -h, --help                     help for get\n"
            "      --include-machine          include machine info\n"
            "      --include-network-volume   include network volume info\n\n"
            "Global Flags:\n"
            "  -o, --output string   output format (json, yaml) (default \"json\")\n\n"
            '{"error":"failed to get pod: api error: {"error":"pod not found",'
            '"status":404}\n (status 404)"}\n'
        )
        if not separator or remainder != expected_remainder:
            return False
        try:
            value = json.loads(first)
        except json.JSONDecodeError:
            return False
    if not isinstance(value, dict):
        return False

    candidates = [value]
    nested = value.get("error")
    if isinstance(nested, dict):
        candidates.append(nested)
    elif isinstance(nested, str):
        matched = re.fullmatch(
            r"api error: (\{.*\})\n \(status 404\)", nested, re.DOTALL
        )
        if matched:
            try:
                decoded = json.loads(matched.group(1))
            except json.JSONDecodeError:
                decoded = None
            if isinstance(decoded, dict):
                candidates.append(decoded)

    for candidate in candidates:
        code_values = [
            candidate[key]
            for key in ("status", "statusCode", "code")
            if key in candidate
        ]
        if not code_values or any(
            isinstance(code, bool) or not isinstance(code, int) or code != 404
            for code in code_values
        ):
            continue
        messages = [
            candidate[key]
            for key in ("message", "detail", "error")
            if isinstance(candidate.get(key), str)
        ]
        for message in messages:
            normalized = " ".join(message.lower().split())
            pod_named = re.search(r"\bpods?\b", normalized) is not None
            absent = (
                re.search(r"\bnot[ -]?found\b", normalized) is not None
                or re.search(r"\bdoes not exist\b", normalized) is not None
            )
            if pod_named and absent:
                return True
    return False


def pod_get(
    cli: Path,
    pod_id: str,
    *,
    timeout_seconds: float,
) -> tuple[bool, dict[str, Any] | None, str]:
    result = run(
        [str(cli), "pod", "get", pod_id, "--output", "json"],
        timeout_seconds=timeout_seconds,
    )
    if result.returncode != 0:
        if structured_pod_not_found(result.stdout):
            return False, None, result.stdout.strip()
        raise TransientProviderError("POD_GET_FAILED:" + result.stdout[-500:])
    value = parse_json(result)
    if not isinstance(value, dict):
        raise TransientProviderError("MALFORMED_POD_GET")
    return True, value, result.stdout.strip()


def campaign_active(
    cli: Path,
    campaign_prefix: str,
    *,
    timeout_seconds: float,
) -> list[dict[str, Any]]:
    result = run(
        [str(cli), "pod", "list", "--all", "--output", "json"],
        timeout_seconds=timeout_seconds,
    )
    if result.returncode != 0:
        raise TransientProviderError("POD_LIST_FAILED:" + result.stdout[-500:])
    value = parse_json(result)
    if not isinstance(value, list):
        raise TransientProviderError("MALFORMED_POD_LIST")
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


def remaining_timeout(deadline_epoch: float, maximum_seconds: float) -> float:
    remaining = deadline_epoch - time.time()
    if remaining <= 0:
        raise TransientProviderError("GUARD_DEADLINE_EXCEEDED")
    return max(0.1, min(maximum_seconds, remaining))


def pause(seconds: float, deadline_epoch: float) -> None:
    remaining = deadline_epoch - time.time()
    if remaining > 0:
        time.sleep(min(seconds, remaining))


def bounded_action(
    cli: Path,
    action: str,
    pod_id: str,
    log: ChainLog,
    *,
    command_timeout_seconds: float,
    deadline_epoch: float,
) -> bool:
    delays = (0, 2, 5)
    for attempt, delay in enumerate(delays, 1):
        if delay:
            pause(delay, deadline_epoch)
        try:
            result = run(
                [str(cli), "pod", action, pod_id, "--output", "json"],
                timeout_seconds=remaining_timeout(
                    deadline_epoch, command_timeout_seconds
                ),
            )
        except TransientProviderError as exc:
            log.emit(
                action.upper() + "_ATTEMPT",
                {"attempt": attempt, "error": str(exc)},
            )
            continue
        log.emit(action.upper() + "_ATTEMPT",
                 {"attempt": attempt, "exit": result.returncode,
                  "output_hash": hashlib.sha256(result.stdout.encode()).hexdigest()})
        if result.returncode == 0:
            return True
        if action == "delete" and structured_pod_not_found(result.stdout):
            return True
    log.emit(action.upper() + "_RETRIES_EXHAUSTED", {})
    return False


def verify_cli(cli: Path, expected_sha256: str) -> None:
    if sha256_file(cli) != expected_sha256:
        raise GuardFailure("CLI_HASH_MISMATCH")


def guard_loop(args: argparse.Namespace, cli: Path, log: ChainLog) -> int:
    terminal_deadline = args.delete_epoch + args.delete_grace_seconds
    bind_deadline = min(terminal_deadline, time.time() + args.bind_timeout_seconds)
    while time.time() < bind_deadline:
        verify_cli(cli, args.runpodctl_sha256)
        try:
            present, value, _ = pod_get(
                cli,
                args.pod_id,
                timeout_seconds=remaining_timeout(
                    bind_deadline, args.command_timeout_seconds
                ),
            )
        except TransientProviderError as exc:
            log.emit("BIND_RETRY", {"reason": str(exc)})
            pause(args.heartbeat_seconds, bind_deadline)
            continue
        if not present or value is None:
            log.emit("BIND_RETRY", {"reason": "EXACT_ID_404"})
            pause(args.heartbeat_seconds, bind_deadline)
            continue
        verify_identity(value, args.pod_id, args.pod_name, args.campaign_prefix)
        log.emit(
            "BOUND",
            {
                "pod_id": args.pod_id,
                "name": args.pod_name,
                "campaign_prefix": args.campaign_prefix,
                "cli_sha256": args.runpodctl_sha256,
                "stop_epoch": args.stop_epoch,
                "delete_epoch": args.delete_epoch,
                "terminal_deadline_epoch": terminal_deadline,
            },
        )
        break
    else:
        raise GuardFailure("BIND_DEADLINE_EXCEEDED")

    stop_succeeded = False
    while time.time() < terminal_deadline:
        verify_cli(cli, args.runpodctl_sha256)
        now = time.time()
        timeout_seconds = remaining_timeout(
            terminal_deadline, args.command_timeout_seconds
        )
        try:
            present, value, raw = pod_get(
                cli, args.pod_id, timeout_seconds=timeout_seconds
            )
        except TransientProviderError as exc:
            log.emit("PROVIDER_RETRY", {"operation": "get", "reason": str(exc)})
            if now >= args.delete_epoch:
                bounded_action(
                    cli,
                    "delete",
                    args.pod_id,
                    log,
                    command_timeout_seconds=args.command_timeout_seconds,
                    deadline_epoch=terminal_deadline,
                )
            elif now >= args.stop_epoch and not stop_succeeded:
                stop_succeeded = bounded_action(
                    cli,
                    "stop",
                    args.pod_id,
                    log,
                    command_timeout_seconds=args.command_timeout_seconds,
                    deadline_epoch=min(args.delete_epoch, terminal_deadline),
                )
            pause(args.heartbeat_seconds, terminal_deadline)
            continue

        if not present:
            try:
                active = campaign_active(
                    cli,
                    args.campaign_prefix,
                    timeout_seconds=remaining_timeout(
                        terminal_deadline, args.command_timeout_seconds
                    ),
                )
            except TransientProviderError as exc:
                log.emit(
                    "PROVIDER_RETRY",
                    {"operation": "list_all", "reason": str(exc)},
                )
                pause(args.heartbeat_seconds, terminal_deadline)
                continue
            if active:
                log.emit(
                    "TEARDOWN_PENDING",
                    {
                        "exact_id_404": True,
                        "campaign_active_count": len(active),
                    },
                )
                pause(args.heartbeat_seconds, terminal_deadline)
                continue
            log.emit(
                "TEARDOWN_GREEN",
                {"exact_id_404": True, "campaign_active": []},
            )
            return 0

        assert value is not None
        verify_identity(value, args.pod_id, args.pod_name, args.campaign_prefix)
        log.emit(
            "HEARTBEAT",
            {
                "pod_id": args.pod_id,
                "provider_state": value.get("desiredStatus"),
                "provider_record_hash": hashlib.sha256(raw.encode()).hexdigest(),
                "seconds_to_stop": int(args.stop_epoch - now),
                "seconds_to_delete": int(args.delete_epoch - now),
            },
        )
        if now >= args.delete_epoch:
            bounded_action(
                cli,
                "delete",
                args.pod_id,
                log,
                command_timeout_seconds=args.command_timeout_seconds,
                deadline_epoch=terminal_deadline,
            )
        elif now >= args.stop_epoch and not stop_succeeded:
            stop_succeeded = bounded_action(
                cli,
                "stop",
                args.pod_id,
                log,
                command_timeout_seconds=args.command_timeout_seconds,
                deadline_epoch=min(args.delete_epoch, terminal_deadline),
            )
        pause(args.heartbeat_seconds, terminal_deadline)
    raise GuardFailure("GUARD_DEADLINE_EXCEEDED")


def execute(args: argparse.Namespace) -> int:
    if (
        args.heartbeat_seconds < 1
        or args.delete_epoch <= args.stop_epoch
        or args.command_timeout_seconds < 1
        or args.bind_timeout_seconds < 1
        or args.delete_grace_seconds < 1
    ):
        raise GuardFailure("INVALID_DEADLINE")
    cli = args.runpodctl.resolve()
    if not cli.is_file() or not os.access(cli, os.X_OK):
        raise GuardFailure("CLI_NOT_EXECUTABLE")
    log = ChainLog(args.log.resolve())
    try:
        return guard_loop(args, cli, log)
    except Exception as exc:
        log.emit("GUARD_BLOCKED", {"type": type(exc).__name__, "error": str(exc)})
        return 1


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
    parser.add_argument("--command-timeout-seconds", type=int, default=30)
    parser.add_argument("--bind-timeout-seconds", type=int, default=120)
    parser.add_argument("--delete-grace-seconds", type=int, default=900)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    return execute(args)


if __name__ == "__main__":
    raise SystemExit(main())
