#!/usr/bin/env python3
"""Host-side R12 preflight checkpoint puller and terminal-state law.

This program is host-only.  It copies immutable checkpoint artifacts from one
exact worker, verifies their canonical hash chain locally, and records a local
acknowledgement.  Its terminal classifier is deliberately exhaustive: absent,
partial, corrupt, transport, observer, deadline, and teardown failures are
mutually exclusive and none can become GREEN.
"""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
CHECKPOINT_SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_checkpoint_for_supervisor", HERE / "pdh3_r12_checkpoint.py"
)
if CHECKPOINT_SPEC is None or CHECKPOINT_SPEC.loader is None:
    raise RuntimeError("CHECKPOINT_IMPORT_FAILED")
checkpoint = importlib.util.module_from_spec(CHECKPOINT_SPEC)
CHECKPOINT_SPEC.loader.exec_module(checkpoint)


GREEN_PENDING_FINAL_GATE = "GREEN_PENDING_FINAL_GATE"
SEMANTIC_FAILURE = "SEMANTIC_FAILURE"
ABSENT_RESULT = "ABSENT_RESULT"
PARTIAL_ARCHIVE = "PARTIAL_ARCHIVE"
CORRUPT_ARCHIVE = "CORRUPT_ARCHIVE"
TRANSPORT_FAILURE = "TRANSPORT_FAILURE"
OBSERVER_LOSS = "OBSERVER_LOSS"
DEADLINE_EXCEEDED = "DEADLINE_EXCEEDED"
TEARDOWN_UNPROVEN = "TEARDOWN_UNPROVEN"

EXIT_CODES = {
    GREEN_PENDING_FINAL_GATE: 0,
    SEMANTIC_FAILURE: 2,
    ABSENT_RESULT: 3,
    PARTIAL_ARCHIVE: 4,
    CORRUPT_ARCHIVE: 5,
    TRANSPORT_FAILURE: 6,
    OBSERVER_LOSS: 7,
    DEADLINE_EXCEEDED: 8,
    TEARDOWN_UNPROVEN: 9,
}


class SupervisorError(RuntimeError):
    """Stable R12 supervisor error."""


class TransportError(SupervisorError):
    """Bounded transport error."""


@dataclass(frozen=True)
class PullConfig:
    ssh_config: Path
    ssh_alias: str
    remote_export_root: str
    local_root: Path
    packet_sha256: str
    deadline_epoch: float
    transfer_timeout_seconds: int = 900
    closeout_reserve_seconds: int = 300


@dataclass(frozen=True)
class TerminalObservation:
    teardown_proven: bool
    deadline_exceeded: bool = False
    transport_failed: bool = False
    observer_alive: bool = True
    workload_alive: bool = False
    terminal_result_present: bool = False
    archive_present: bool = False
    archive_complete: bool = False
    archive_valid: bool = False
    semantic_green: bool = False


def classify_terminal(value: TerminalObservation) -> str:
    """Return exactly one terminal state using fixed precedence."""
    if not value.teardown_proven:
        return TEARDOWN_UNPROVEN
    if value.transport_failed:
        return TRANSPORT_FAILURE
    if value.deadline_exceeded:
        return DEADLINE_EXCEEDED
    if not value.observer_alive and (value.workload_alive or not value.terminal_result_present):
        return OBSERVER_LOSS
    if not value.terminal_result_present:
        return ABSENT_RESULT
    if not value.archive_present or not value.archive_complete:
        return PARTIAL_ARCHIVE
    if not value.archive_valid:
        return CORRUPT_ARCHIVE
    if not value.semantic_green:
        return SEMANTIC_FAILURE
    return GREEN_PENDING_FINAL_GATE


def validate_config(config: PullConfig) -> None:
    if re.fullmatch(r"[0-9a-f]{64}", config.packet_sha256) is None:
        raise SupervisorError("PACKET_SHA256_INVALID")
    if re.fullmatch(r"[A-Za-z0-9_.-]+", config.ssh_alias) is None:
        raise SupervisorError("SSH_ALIAS_INVALID")
    remote = PurePosixPath(config.remote_export_root)
    if not remote.is_absolute() or ".." in remote.parts or "\x00" in config.remote_export_root:
        raise SupervisorError("REMOTE_EXPORT_ROOT_INVALID")
    if config.deadline_epoch <= time.time():
        raise SupervisorError("DEADLINE_INVALID")
    if not 1 <= config.transfer_timeout_seconds <= 3600:
        raise SupervisorError("TRANSFER_TIMEOUT_INVALID")
    if not 1 <= config.closeout_reserve_seconds <= 1800:
        raise SupervisorError("CLOSEOUT_RESERVE_INVALID")


def bounded_timeout(config: PullConfig) -> float:
    remaining = config.deadline_epoch - time.time() - config.closeout_reserve_seconds
    if remaining <= 0:
        raise TransportError("CLOSEOUT_DEADLINE_EXCEEDED")
    return max(0.1, min(config.transfer_timeout_seconds, remaining))


def atomic_scp(
    config: PullConfig,
    remote_name: str,
    destination: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> Path:
    checkpoint.validate_relative(remote_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    partial.unlink(missing_ok=True)
    try:
        completed = runner(
            [
                "scp",
                "-F",
                str(config.ssh_config),
                f"{config.ssh_alias}:{config.remote_export_root}/{remote_name}",
                str(partial),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=bounded_timeout(config),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TransportError("SCP_TIMEOUT:" + remote_name) from exc
    if completed.returncode != 0 or not partial.is_file():
        partial.unlink(missing_ok=True)
        raise TransportError("SCP_FAILED:" + remote_name)
    with partial.open("rb") as handle:
        os.fsync(handle.fileno())
    os.replace(partial, destination)
    directory = os.open(destination.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return destination


def previous_state(local_root: Path) -> tuple[int, str]:
    path = local_root / "pull-state.json"
    if not path.exists():
        return 0, checkpoint.ZERO_HASH
    value = checkpoint.verify_hashed(path, "state_sha256")
    sequence = value.get("last_sequence")
    manifest_hash = value.get("last_manifest_sha256")
    if not isinstance(sequence, int) or sequence < 1:
        raise SupervisorError("PULL_STATE_SEQUENCE_INVALID")
    checkpoint.validate_sha256(manifest_hash, "PULL_STATE_MANIFEST")
    return sequence, manifest_hash


def pull_latest(
    config: PullConfig,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    acknowledged_utc: str | None = None,
) -> dict[str, Any] | None:
    validate_config(config)
    local = config.local_root.resolve()
    local.mkdir(parents=True, exist_ok=True)
    pointer_path = atomic_scp(config, "latest.json", local / "latest.json", runner=runner)
    pointer = checkpoint.verify_hashed(pointer_path, "pointer_sha256")
    if pointer.get("version") != "ck-pdh3-r12-checkpoint-latest-v1":
        raise SupervisorError("LATEST_VERSION_INVALID")
    sequence = pointer.get("sequence")
    manifest_name = pointer.get("manifest")
    manifest_hash = pointer.get("manifest_sha256")
    if (
        not isinstance(sequence, int)
        or sequence < 1
        or manifest_name != f"checkpoint-{sequence:04d}.json"
    ):
        raise SupervisorError("LATEST_POINTER_INVALID")
    checkpoint.validate_sha256(manifest_hash, "LATEST_MANIFEST")
    previous_sequence, previous_hash = previous_state(local)
    if sequence == previous_sequence:
        return None
    if sequence != previous_sequence + 1:
        raise SupervisorError("CHECKPOINT_SEQUENCE_GAP")

    manifest_path = atomic_scp(config, manifest_name, local / manifest_name, runner=runner)
    manifest = checkpoint.verify_hashed(manifest_path, "manifest_sha256")
    if manifest.get("manifest_sha256") != manifest_hash:
        raise SupervisorError("LATEST_MANIFEST_HASH_MISMATCH")
    archive_name = manifest.get("archive")
    if archive_name != f"checkpoint-{sequence:04d}.tgz":
        raise SupervisorError("CHECKPOINT_ARCHIVE_NAME_INVALID")
    archive_path = atomic_scp(config, archive_name, local / archive_name, runner=runner)
    verified = checkpoint.verify_download(
        manifest_path=manifest_path,
        archive_path=archive_path,
        expected_packet_sha256=config.packet_sha256,
        expected_sequence=sequence,
        expected_previous_manifest_sha256=previous_hash,
    )
    ack = checkpoint.acknowledge(
        output=local / f"checkpoint-{sequence:04d}.ack.json",
        manifest=verified,
        local_archive=archive_path,
        acknowledged_utc=acknowledged_utc
        or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    state_body = {
        "version": "ck-pdh3-r12-pull-state-v1",
        "last_sequence": sequence,
        "last_manifest_sha256": verified["manifest_sha256"],
        "last_ack_sha256": ack["ack_sha256"],
    }
    checkpoint.write_hashed(local / "pull-state.json", state_body, "state_sha256")
    return {"manifest": verified, "ack": ack}


def push_remote_ack(
    config: PullConfig,
    pulled: dict[str, Any],
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Publish a packet-bound acknowledgement back to the running worker.

    The remote workload may cross its interruption canary only after this
    exact local verification result exists.  Upload uses a temporary name and
    a bounded SSH rename so a partial acknowledgement is never accepted.
    """
    validate_config(config)
    manifest = pulled.get("manifest")
    ack = pulled.get("ack")
    if not isinstance(manifest, dict) or not isinstance(ack, dict):
        raise SupervisorError("REMOTE_ACK_INPUT_INVALID")
    sequence = manifest.get("sequence")
    if not isinstance(sequence, int) or sequence < 1:
        raise SupervisorError("REMOTE_ACK_SEQUENCE_INVALID")
    body = {
        "version": "ck-pdh3-r12-host-ack-v1",
        "sequence": sequence,
        "packet_sha256": config.packet_sha256,
        "manifest_sha256": manifest.get("manifest_sha256"),
        "local_ack_sha256": ack.get("ack_sha256"),
        "verified": True,
    }
    local_ack = checkpoint.write_hashed(
        config.local_root / f"host-ack-{sequence:04d}.json",
        body,
        "host_ack_sha256",
    )
    name = f"host-ack-{sequence:04d}.json"
    temporary = name + ".part"
    timeout = bounded_timeout(config)
    upload = runner(
        [
            "scp", "-F", str(config.ssh_config), str(config.local_root / name),
            f"{config.ssh_alias}:{config.remote_export_root}/{temporary}",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )
    if upload.returncode != 0:
        raise TransportError("REMOTE_ACK_UPLOAD_FAILED")
    promote = runner(
        [
            "ssh", "-F", str(config.ssh_config), config.ssh_alias,
            "mv", "--", f"{config.remote_export_root}/{temporary}",
            f"{config.remote_export_root}/{name}",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=bounded_timeout(config),
        check=False,
    )
    if promote.returncode != 0:
        raise TransportError("REMOTE_ACK_PROMOTE_FAILED")
    return local_ack


def main() -> int:
    print("PDH3_R12_PREFLIGHT_SUPERVISOR_LIBRARY_ONLY", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
