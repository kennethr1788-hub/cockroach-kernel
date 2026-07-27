#!/usr/bin/env python3
"""Hash-checked SSH bridge between one verified RunPod worker and host coordinator."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import time
from typing import Any

import protocol

REMOTE_ROOT_RE = re.compile(r"^/workspace/ck-s3-[A-Za-z0-9._-]{1,48}/bridge$")
HOST_RE = re.compile(r"^[A-Za-z0-9.-]{1,253}$")


class BridgeFailure(RuntimeError):
    pass


def run(command: list[str], timeout: int = 30) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          timeout=timeout, check=False)


class ChainLog:
    def __init__(self, path: Path, campaign: str) -> None:
        if path.exists():
            raise BridgeFailure("LOG_EXISTS")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.campaign = campaign
        self.previous = protocol.GENESIS_HASH
        self.sequence = 0

    def emit(self, event: str, details: Any) -> None:
        self.sequence += 1
        core = {
            "version": "s3-remote-bridge-log-v1", "campaign_id": self.campaign,
            "sequence": self.sequence, "previous_hash": self.previous,
            "event": event, "details": details,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "monotonic_ns": time.monotonic_ns(),
        }
        value = {**core, "event_hash": protocol.sha256(core)}
        with self.path.open("ab") as handle:
            handle.write(protocol.canonical(value) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous = value["event_hash"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--user", default="root")
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--known-hosts", type=Path, required=True)
    parser.add_argument("--remote-root", required=True)
    parser.add_argument("--local-root", type=Path, required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--expected-requests", type=int, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--heartbeat-seconds", type=int, default=30)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    if not HOST_RE.fullmatch(args.host) or not 1 <= args.port <= 65535:
        raise BridgeFailure("SSH_TARGET_INVALID")
    if args.user != "root" or not REMOTE_ROOT_RE.fullmatch(args.remote_root):
        raise BridgeFailure("REMOTE_SCOPE_INVALID")
    if not 1 <= args.expected_requests <= protocol.MAX_SEQUENCE:
        raise BridgeFailure("EXPECTED_REQUESTS_INVALID")
    if not 1 <= args.heartbeat_seconds <= 60:
        raise BridgeFailure("HEARTBEAT_INVALID")
    identity = args.identity.resolve()
    known_hosts = args.known_hosts.resolve()
    if not identity.is_file() or not known_hosts.is_file():
        raise BridgeFailure("SSH_MATERIAL_MISSING")
    if identity.stat().st_mode & 0o077:
        raise BridgeFailure("SSH_IDENTITY_PERMISSIONS")
    local = args.local_root.resolve()
    local_requests = local / "requests"
    local_results = local / "results"
    local_requests.mkdir(parents=True, exist_ok=True)
    local_results.mkdir(parents=True, exist_ok=True)
    log = ChainLog(args.log.resolve(), args.campaign_id)
    common = [
        "-i", str(identity), "-p", str(args.port),
        "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes",
        "-o", "StrictHostKeyChecking=yes",
        "-o", "UserKnownHostsFile=" + str(known_hosts),
        "-o", "ConnectTimeout=10",
    ]
    ssh = ["/usr/bin/ssh", *common, f"{args.user}@{args.host}"]
    scp_common = list(common)
    scp_common[scp_common.index("-p")] = "-P"
    scp = ["/usr/bin/scp", *scp_common]
    parent_hash = protocol.GENESIS_HASH
    log.emit("BRIDGE_START", {"expected_requests": args.expected_requests,
                               "deadline_epoch": args.deadline_epoch,
                               "heartbeat_seconds": args.heartbeat_seconds})
    try:
        for sequence in range(1, args.expected_requests + 1):
            request_name = f"request-{sequence:04d}.json"
            result_name = f"result-{sequence:04d}.json"
            remote_request = f"{args.remote_root}/requests/{request_name}"
            remote_result = f"{args.remote_root}/results/{result_name}"
            remote_temporary = remote_result + ".tmp"
            last_heartbeat = 0.0
            while int(time.time()) < args.deadline_epoch:
                probe = run([*ssh, "test", "-f", remote_request], timeout=15)
                if probe.returncode == 0:
                    break
                if probe.returncode not in {1, 255}:
                    raise BridgeFailure("REMOTE_PROBE_FAILED")
                now = time.monotonic()
                if now - last_heartbeat >= args.heartbeat_seconds:
                    log.emit("HEARTBEAT", {"sequence": sequence,
                                            "state": "AWAITING_REMOTE_REQUEST"})
                    last_heartbeat = now
                time.sleep(1)
            else:
                raise BridgeFailure("REMOTE_REQUEST_DEADLINE")
            # This name is a shared contract with host_coordinator's strict
            # directory validator. The coordinator permits only the current
            # sequence's `.json.tmp` while a transfer is incomplete.
            local_temporary = local_requests / (request_name + ".tmp")
            transfer = run([*scp, f"{args.user}@{args.host}:{remote_request}",
                            str(local_temporary)], timeout=60)
            if transfer.returncode != 0:
                raise BridgeFailure("REQUEST_TRANSFER_FAILED")
            request = protocol.decode_request(local_temporary.read_bytes())
            if request["campaign_id"] != args.campaign_id or request["sequence"] != sequence:
                raise BridgeFailure("REQUEST_LINKAGE_INVALID")
            if request["parent_hash"] != parent_hash:
                raise BridgeFailure("REQUEST_PARENT_INVALID")
            local_request = local_requests / request_name
            os.replace(local_temporary, local_request)
            log.emit("REQUEST_TRANSFERRED", {"sequence": sequence,
                                              "request_hash": request["request_hash"]})
            local_result = local_results / result_name
            while int(time.time()) < args.deadline_epoch and not local_result.exists():
                now = time.monotonic()
                if now - last_heartbeat >= args.heartbeat_seconds:
                    log.emit("HEARTBEAT", {"sequence": sequence,
                                            "state": "AWAITING_LOCAL_RESULT"})
                    last_heartbeat = now
                time.sleep(0.2)
            if not local_result.exists():
                raise BridgeFailure("LOCAL_RESULT_DEADLINE")
            result = protocol.decode_result(local_result.read_bytes(), request)
            upload = run([*scp, str(local_result),
                          f"{args.user}@{args.host}:{remote_temporary}"], timeout=60)
            if upload.returncode != 0:
                raise BridgeFailure("RESULT_TRANSFER_FAILED")
            commit = run([*ssh, "mv", remote_temporary, remote_result], timeout=30)
            if commit.returncode != 0:
                raise BridgeFailure("RESULT_COMMIT_FAILED")
            log.emit("RESULT_TRANSFERRED", {"sequence": sequence,
                                             "result_hash": result["result_hash"]})
            parent_hash = request["request_hash"]
        log.emit("BRIDGE_GREEN", {"requests": args.expected_requests})
        return 0
    except Exception as exc:
        log.emit("BRIDGE_BLOCKED", {"type": type(exc).__name__,
                                     "error_hash": protocol.sha256(str(exc).encode())})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
