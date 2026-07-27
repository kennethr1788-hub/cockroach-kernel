#!/usr/bin/env python3
"""Fail-closed S3 hardening primitives.

This module deliberately stores only stable classifications and hashes of
external-command output.  Raw command output, credentials, and environment
contents are never written to evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import signal
import time
from typing import Any

import protocol


AWS_AUTHENTICATION = "AWS_AUTHENTICATION"
AWS_AUTHORIZATION_OR_THROTTLING = "AWS_AUTHORIZATION_OR_THROTTLING"
COCKROACH_CONNECTIVITY = "COCKROACH_CONNECTIVITY"
UNKNOWN_EXTERNAL_COMMAND = "UNKNOWN_EXTERNAL_COMMAND"
SESSION_MARGIN_SECONDS = 900

_AWS_AUTH_MARKERS = (
    b"expiredtoken", b"expired token", b"token has expired",
    b"unauthorizedssotoken", b"sso session", b"login session",
    b"invalidclienttokenid", b"unrecognizedclientexception",
)
_AWS_AUTHZ_MARKERS = (
    b"accessdenied", b"not authorized", b"unauthorizedoperation",
    b"throttl", b"too many requests", b"requestlimitexceeded",
)
_COCKROACH_CONNECTIVITY_MARKERS = (
    b"connection refused", b"connection reset", b"connection timed out",
    b"no such host", b"could not connect", b"failed to connect",
    b"server closed the connection", b"tls handshake", b"x509:",
    b"certificate", b"dial tcp", b"network is unreachable",
)


@dataclass(frozen=True)
class ExternalCommandFailure(RuntimeError):
    command_family: str
    return_code: int
    output_hash: str
    failure_class: str

    def __str__(self) -> str:
        return f"{self.failure_class}:{self.command_family}:{self.return_code}"


def classify_external_failure(command_family: str, output: bytes) -> str:
    """Classify bounded command output without returning or retaining it."""
    lowered = bytes(output[:1_048_576]).lower()
    if command_family == "aws":
        if any(marker in lowered for marker in _AWS_AUTH_MARKERS):
            return AWS_AUTHENTICATION
        if any(marker in lowered for marker in _AWS_AUTHZ_MARKERS):
            return AWS_AUTHORIZATION_OR_THROTTLING
    if command_family == "cockroach" and any(
            marker in lowered for marker in _COCKROACH_CONNECTIVITY_MARKERS):
        return COCKROACH_CONNECTIVITY
    return UNKNOWN_EXTERNAL_COMMAND


def command_failure(command_family: str, return_code: int,
                    output: bytes) -> ExternalCommandFailure:
    return ExternalCommandFailure(
        command_family=command_family,
        return_code=return_code,
        output_hash=protocol.sha256(output),
        failure_class=classify_external_failure(command_family, output),
    )


def write_atomic(path: Path, value: dict[str, Any]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink() or (path.exists() and path.is_symlink()):
        raise RuntimeError("EVIDENCE_PATH_UNSAFE")
    raw = protocol.canonical(value) + b"\n"
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


def failure_receipt(*, campaign_id: str, sequence: int, stage: str,
                    request_hash: str, failure: ExternalCommandFailure,
                    utc: str | None = None) -> dict[str, Any]:
    core = {
        "version": "s3-stage-failure-v1",
        "campaign_id": campaign_id,
        "sequence": sequence,
        "stage": stage,
        "request_hash": request_hash,
        "failure_class": failure.failure_class,
        "command_family": failure.command_family,
        "return_code": failure.return_code,
        "sanitized_output_sha256": failure.output_hash,
        "raw_output_stored": False,
        "utc": utc or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    return {**core, "receipt_hash": protocol.sha256(core)}


def session_window_receipt(*, expires_epoch: int, final_exchange_epoch: int,
                           margin_seconds: int = SESSION_MARGIN_SECONDS) -> dict[str, Any]:
    if any(isinstance(item, bool) or not isinstance(item, int)
           for item in (expires_epoch, final_exchange_epoch, margin_seconds)):
        raise RuntimeError("AWS_SESSION_WINDOW_INVALID")
    if margin_seconds < SESSION_MARGIN_SECONDS:
        raise RuntimeError("AWS_SESSION_MARGIN_TOO_SMALL")
    required_expiry = final_exchange_epoch + margin_seconds
    status = "PASS" if expires_epoch >= required_expiry else "BLOCKED"
    core = {
        "version": "s3-aws-session-window-v1",
        "expires_epoch": expires_epoch,
        "final_exchange_epoch": final_exchange_epoch,
        "margin_seconds": margin_seconds,
        "required_expiry_epoch": required_expiry,
        "status": status,
        "stable_reason_code": (
            "AWS_SESSION_MARGIN_VERIFIED" if status == "PASS"
            else "AWS_SESSION_MARGIN_INSUFFICIENT"
        ),
    }
    return {**core, "receipt_hash": protocol.sha256(core)}


def validate_session_window(*, expires_epoch: int, final_exchange_epoch: int,
                            margin_seconds: int = SESSION_MARGIN_SECONDS) -> dict[str, Any]:
    receipt = session_window_receipt(
        expires_epoch=expires_epoch,
        final_exchange_epoch=final_exchange_epoch,
        margin_seconds=margin_seconds,
    )
    if receipt["status"] != "PASS":
        raise RuntimeError("AWS_SESSION_MARGIN_INSUFFICIENT")
    return receipt


def cleanup_trial_exact(trial_root: Path, evidence_root: Path) -> dict[str, Any]:
    """Remove exactly one generated trial root and prove zero path residue."""
    trial = trial_root.resolve(strict=False)
    evidence = evidence_root.resolve()
    if trial.parent != evidence or trial == evidence or trial.is_symlink():
        raise RuntimeError("TRIAL_CLEANUP_SCOPE_INVALID")
    existed = trial.exists()
    if existed:
        shutil.rmtree(trial)
    residue = trial.exists() or trial.is_symlink()
    core = {
        "version": "s3-trial-cleanup-v1",
        "trial_name": trial.name,
        "existed_before_cleanup": existed,
        "residue_entries": 1 if residue else 0,
        "status": "BLOCKED" if residue else "PASS",
        "stable_reason_code": "TRIAL_RESIDUE" if residue else "ZERO_TRIAL_RESIDUE",
    }
    receipt = {**core, "receipt_hash": protocol.sha256(core)}
    if residue:
        raise RuntimeError("TRIAL_RESIDUE")
    return receipt


class CheckpointCustody:
    """Append-only, per-exchange custody outside the disposable trial root."""

    def __init__(self, root: Path, campaign_id: str) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=False)
        self.campaign_id = campaign_id
        self.previous = protocol.GENESIS_HASH
        self.sequence = 0

    def capture(self, request: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        protocol.validate_request(request)
        protocol.validate_result(result, request)
        expected = self.sequence + 1
        if request["campaign_id"] != self.campaign_id or request["sequence"] != expected:
            raise RuntimeError("CUSTODY_SEQUENCE_INVALID")
        core = {
            "version": "s3-checkpoint-custody-v1",
            "campaign_id": self.campaign_id,
            "sequence": expected,
            "previous_receipt_hash": self.previous,
            "request_hash": request["request_hash"],
            "result_hash": result["result_hash"],
            "request_bytes_sha256": protocol.sha256(protocol.canonical(request)),
            "result_bytes_sha256": protocol.sha256(protocol.canonical(result)),
        }
        receipt = {**core, "receipt_hash": protocol.sha256(core)}
        write_atomic(self.root / f"exchange-{expected:04d}.json", receipt)
        self.previous = receipt["receipt_hash"]
        self.sequence = expected
        return receipt


def coordinated_local_shutdown(processes: list[tuple[str, int]],
                               timeout_seconds: float = 5.0) -> dict[str, Any]:
    """Terminate exact local coordinator/bridge PIDs and prove their absence."""
    if timeout_seconds <= 0:
        raise RuntimeError("SHUTDOWN_TIMEOUT_INVALID")
    ordered = []
    for role, pid in processes:
        if role not in {"worker", "bridge", "coordinator"} or pid <= 1 or pid == os.getpid():
            raise RuntimeError("SHUTDOWN_TARGET_INVALID")
        ordered.append((role, pid))
    for _role, pid in ordered:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + timeout_seconds
    remaining: list[tuple[str, int]] = []
    while time.monotonic() < deadline:
        remaining = []
        for role, pid in ordered:
            try:
                waited, _status = os.waitpid(pid, os.WNOHANG)
                if waited == pid:
                    continue
            except ChildProcessError:
                pass
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                continue
            remaining.append((role, pid))
        if not remaining:
            break
        time.sleep(0.05)
    if remaining:
        for _role, pid in remaining:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        time.sleep(0.05)
    live = []
    for role, pid in ordered:
        try:
            waited, _status = os.waitpid(pid, os.WNOHANG)
            if waited == pid:
                continue
        except ChildProcessError:
            pass
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            continue
        live.append(role)
    core = {
        "version": "s3-coordinated-shutdown-v1",
        "requested_roles": [role for role, _pid in ordered],
        "live_roles_after_shutdown": live,
        "status": "PASS" if not live else "BLOCKED",
    }
    receipt = {**core, "receipt_hash": protocol.sha256(core)}
    if live:
        raise RuntimeError("COORDINATED_SHUTDOWN_INCOMPLETE")
    return receipt
