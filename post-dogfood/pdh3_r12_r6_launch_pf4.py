#!/usr/bin/env python3
"""Create and pre-upload verify one R6 worker under a bounded retry envelope."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import pdh3_r12_cpu_affinity as cpu_affinity
import pdh3_r12_lifecycle_launch as lifecycle
import pdh3_r12_r6_config as r6_config


class R6LaunchError(RuntimeError):
    """Stable pre-upload creation failure."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def atomic_new(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb", closefd=True) as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def run(root: Path, argv: list[str], timeout: int = 90) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(argv, cwd=root, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=timeout, check=False, shell=False)


def parsed(result: subprocess.CompletedProcess[bytes], label: str) -> Any:
    if result.returncode != 0:
        raise R6LaunchError(label + "_COMMAND_FAILED")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise R6LaunchError(label + "_JSON_INVALID") from exc


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise R6LaunchError("MODULE_LOAD_FAILED:" + name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def provider_absent(guard: Any, cli: Path, campaign: str, pod_id: str) -> bool:
    try:
        present, _, _ = guard.pod_get(cli, pod_id, timeout_seconds=30)
        active = guard.campaign_active(cli, campaign, timeout_seconds=30)
    except Exception:
        return False
    return not present and active == []


def delete_and_prove(
    *, root: Path, runtime: Path, guard: Any, cli: Path, campaign: str,
    pod_id: str, attempt: int,
) -> None:
    attempt_root = runtime / f"attempt-{attempt:02d}"
    result = run(root, [str(cli), "pod", "delete", pod_id, "--output", "json"], 60)
    atomic_new(attempt_root / "delete.stdout", result.stdout)
    atomic_new(attempt_root / "delete.stderr", result.stderr)
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        if provider_absent(guard, cli, campaign, pod_id):
            atomic_new(attempt_root / "post-delete-inventory.json", b"[]")
            return
        time.sleep(5)
    raise R6LaunchError("TEARDOWN_UNPROVEN")


def shape_plan(
    body: dict[str, Any], *, name: str, image: str, ceiling: float,
    data_center_ids: tuple[str, ...] = (),
) -> dict[str, Any] | None:
    machine = body.get("machine") if isinstance(body.get("machine"), dict) else {}
    vcpus = int(body.get("vcpuCount", 0))
    memory = int(body.get("memoryInGb", 0))
    base_green = bool(
        body.get("id")
        and body.get("name") == name
        and body.get("gpuCount") == 1
        and body.get("imageName") == image
        and body.get("containerDiskInGb") == 250
        and body.get("volumeInGb") == 0
        and float(body.get("costPerHr", 999.0)) <= ceiling
        and vcpus >= 16
        and memory >= 94
        and machine.get("secureCloud") is True
        and (
            not data_center_ids
            or machine.get("dataCenterId") in data_center_ids
        )
        and (machine.get("gpuId") == "NVIDIA L40S"
             or "L40S" in str(machine.get("gpuDisplayName", "")))
    )
    if not base_green:
        return None
    try:
        return cpu_affinity.effective_vcpu_plan(vcpus, memory)
    except cpu_affinity.AffinityError:
        return None


def exact_shape(
    body: dict[str, Any], *, name: str, image: str, ceiling: float,
    data_center_ids: tuple[str, ...] = (),
) -> bool:
    return shape_plan(
        body, name=name, image=image, ceiling=ceiling,
        data_center_ids=data_center_ids,
    ) is not None


def creation_argv(
    cli: Path, *, pod_name: str, config: dict[str, Any]
) -> list[str]:
    argv = [
        str(cli), "pod", "create", "--cloud-type", "SECURE",
        "--compute-type", "GPU", "--gpu-id", "NVIDIA L40S",
        "--gpu-count", "1", "--image", config["image"], "--name", pod_name,
        "--container-disk-in-gb", "250", "--volume-in-gb", "0",
        "--ports", "22/tcp", "--stop-after", config["stop_utc"],
        "--terminate-after", config["terminate_utc"],
    ]
    if config.get("data_center_ids"):
        argv.extend([
            "--data-center-ids", ",".join(config["data_center_ids"])
        ])
    return [*argv, "--output", "json"]


def ssh_ready(
    *, root: Path, runtime: Path, cli: Path, pod_id: str, pod_name: str,
    attempt: int, deadline: float,
) -> Path:
    attempt_root = runtime / f"attempt-{attempt:02d}"
    detailed: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        result = run(root, [str(cli), "pod", "get", pod_id, "--include-machine",
                            "--output", "json"], 60)
        try:
            candidate = json.loads(result.stdout)
        except json.JSONDecodeError:
            candidate = {}
        ssh = candidate.get("ssh", {}) if isinstance(candidate, dict) else {}
        key = ssh.get("ssh_key", {}) if isinstance(ssh, dict) else {}
        if (result.returncode == 0 and ssh.get("ip") and ssh.get("port")
                and isinstance(key, dict) and key.get("path")):
            detailed = candidate
            break
        time.sleep(10)
    if detailed is None:
        raise R6LaunchError("SSH_METADATA_TIMEOUT")
    atomic_new(attempt_root / "pod-get.json", canonical(detailed))
    ssh = detailed["ssh"]
    host = str(ssh["ip"])
    port = int(ssh["port"])
    key = Path(str(ssh["ssh_key"]["path"])).resolve()
    if not 1 <= port <= 65535 or not key.is_file() or key.is_symlink():
        raise R6LaunchError("SSH_BINDING_INVALID")
    scan: bytes | None = None
    while time.monotonic() < deadline:
        candidate = run(root, ["/usr/bin/ssh-keyscan", "-p", str(port), "-T", "15", host], 30)
        if candidate.returncode == 0 and candidate.stdout.strip():
            scan = candidate.stdout
            break
        time.sleep(10)
    if scan is None:
        raise R6LaunchError("SSH_HOST_KEY_SCAN_TIMEOUT")
    known_hosts = attempt_root / "known_hosts"
    atomic_new(known_hosts, scan)
    config = attempt_root / "ssh-config"
    atomic_new(
        config,
        (
            f"Host {pod_name}\n  HostName {host}\n  Port {port}\n  User root\n"
            f"  IdentityFile {key}\n  UserKnownHostsFile {known_hosts}\n"
            "  StrictHostKeyChecking yes\n  IdentitiesOnly yes\n"
            "  BatchMode yes\n  ConnectTimeout 15\n"
        ).encode("utf-8"),
    )
    base = ["/usr/bin/ssh", "-F", str(config), pod_name]
    while time.monotonic() < deadline:
        probe = run(root, [*base, "true"], 30)
        if probe.returncode == 0:
            return config
        time.sleep(10)
    raise R6LaunchError("SSH_READINESS_TIMEOUT")


def verify_static_gate(config: dict[str, Any]) -> None:
    judge = Path(config["judge_raw"]).read_text(encoding="utf-8")
    required = (
        "SERVED_MODEL: glm-5.2",
        "TARGET_PACKET_SHA256: " + config["packet_sha256"],
        "VERDICT: GREEN",
    )
    if (not all(judge.count(item) == 1 for item in required)
            or judge.count("VERDICT:") != 1
            or any(value in judge for value in (
                "VERDICT: NOT_GREEN", "VERDICT: BLOCKED", "VERDICT: JUDGE_UNAVAILABLE"
            ))):
        raise R6LaunchError("JUDGE_GATE_NOT_GREEN")
    start = datetime.fromisoformat(config["launch_start_utc"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(config["launch_end_utc"].replace("Z", "+00:00"))
    if not start <= now_utc() <= end:
        raise R6LaunchError("LAUNCH_WINDOW_NOT_OPEN")


def main() -> int:
    config = r6_config.load()
    root = Path(config["root"])
    runtime = Path(config["runtime"])
    runtime.mkdir(parents=True, exist_ok=False, mode=0o700)
    cli = Path(config["runpodctl"])
    campaign = config["campaign_id"]
    guard = load_module(root / "s2-soak/lifecycle_guard.py", "pdh3_r12_r6_guard")
    verify_static_gate(config)
    # Prove the detached guard can receive its host-only credential before any
    # paid provider mutation.  Never read, print, persist, or hash the value.
    lifecycle.guard_environment(runtime / "credential-canary-home")
    inventory = parsed(run(root, [str(cli), "pod", "list", "--output", "json"], 30), "INVENTORY")
    if inventory != []:
        raise R6LaunchError("ACTIVE_INVENTORY_NOT_EMPTY")
    gpus = parsed(run(root, [str(cli), "gpu", "list", "--include-unavailable",
                              "--output", "json"], 30), "GPU_INVENTORY")
    if not any(isinstance(row, dict) and row.get("gpuId") == "NVIDIA L40S"
               and row.get("available") is True and row.get("secureCloud") is True
               for row in gpus):
        raise R6LaunchError("SECURE_L40S_UNAVAILABLE")
    account = parsed(run(root, [str(cli), "user", "--output", "json"], 30), "ACCOUNT")
    if float(account.get("clientBalance", 0)) < config["aggregate_cost_ceiling_usd"]:
        raise R6LaunchError("ACCOUNT_BALANCE_INSUFFICIENT")
    if float(account.get("currentSpendPerHr", 999)) > 0.01:
        raise R6LaunchError("UNEXPECTED_EXISTING_SPEND")
    atomic_new(runtime / "precreate-inventory.json", canonical(inventory))
    atomic_new(runtime / "precreate-account-sanitized.json", canonical({
        "clientBalance": account.get("clientBalance"),
        "currentSpendPerHr": account.get("currentSpendPerHr"),
        "spendLimit": account.get("spendLimit"),
    }))

    launch_deadline = datetime.fromisoformat(config["launch_end_utc"].replace("Z", "+00:00")).timestamp()
    stop_epoch = int(datetime.fromisoformat(config["stop_utc"].replace("Z", "+00:00")).timestamp())
    terminate_epoch = int(datetime.fromisoformat(config["terminate_utc"].replace("Z", "+00:00")).timestamp())
    total_attempt_seconds = 0.0
    attempt_ledger: list[dict[str, Any]] = []
    active_rate_bound = config["rate_ceiling_usd_per_hour"] + 250 * 0.10 / (30 * 24)
    for attempt in range(1, config["max_attempts"] + 1):
        if time.time() >= launch_deadline:
            break
        if active_rate_bound * (total_attempt_seconds / 3600 + 10) > config["aggregate_cost_ceiling_usd"]:
            raise R6LaunchError("AGGREGATE_COST_BOUND_EXCEEDED")
        if parsed(run(root, [str(cli), "pod", "list", "--output", "json"], 30), "RETRY_INVENTORY") != []:
            raise R6LaunchError("RETRY_INVENTORY_NOT_EMPTY")
        attempt_root = runtime / f"attempt-{attempt:02d}"
        attempt_root.mkdir(mode=0o700)
        pod_name = f"{campaign}-{attempt:02d}"
        create = creation_argv(cli, pod_name=pod_name, config=config)
        started = time.monotonic()
        created = run(root, create, 180)
        atomic_new(attempt_root / "create.stdout", created.stdout)
        atomic_new(attempt_root / "create.stderr", created.stderr)
        pod_id = ""
        try:
            body = parsed(created, "CREATE")
            if not isinstance(body, dict):
                raise R6LaunchError("CREATE_RESPONSE_INVALID")
            pod_id = str(body.get("id", ""))
            if not pod_id:
                raise R6LaunchError("CREATE_ID_MISSING")
            guard_argv = [
                sys.executable, str(root / "s2-soak/lifecycle_guard.py"),
                "--runpodctl", str(cli), "--runpodctl-sha256", config["runpodctl_sha256"],
                "--pod-id", pod_id, "--pod-name", pod_name,
                "--campaign-prefix", campaign, "--stop-epoch", str(stop_epoch),
                "--delete-epoch", str(terminate_epoch), "--heartbeat-seconds", "30",
                "--command-timeout-seconds", "30", "--bind-timeout-seconds", "120",
                "--delete-grace-seconds", "900", "--log", str(attempt_root / "lifecycle.ndjson"),
            ]
            guard_pid = lifecycle.launch_detached(
                argv=guard_argv, cwd=root,
                process_log=attempt_root / "lifecycle-process.log",
                empty_home=attempt_root / "guard-home",
            )
            bound = lifecycle.wait_for_bound(
                log=attempt_root / "lifecycle.ndjson", pid=guard_pid,
                pod_id=pod_id, pod_name=pod_name, campaign_prefix=campaign,
                timeout_seconds=150,
            )
            ssh_config = ssh_ready(
                root=root, runtime=runtime, cli=cli, pod_id=pod_id,
                pod_name=pod_name, attempt=attempt,
                deadline=min(time.monotonic() + 900, time.monotonic() + max(1, launch_deadline - time.time())),
            )
            detailed = json.loads((attempt_root / "pod-get.json").read_bytes())
            affinity_plan = shape_plan(
                detailed, name=pod_name, image=config["image"],
                ceiling=config["rate_ceiling_usd_per_hour"],
                data_center_ids=tuple(config.get("data_center_ids", ())),
            )
            if affinity_plan is None:
                raise R6LaunchError("RETURNED_WORKER_MISMATCH")
            record = {
                "version": "ck-pdh3-r12-r6-running-worker-v2",
                "attempt": attempt, "campaign_id": campaign,
                "pod_id": pod_id, "pod_name": pod_name,
                "packet_sha256": config["packet_sha256"],
                "config_sha256": config["_config_sha256"],
                "guard_pid": guard_pid, "guard_bound_event_hash": bound["event_hash"],
                "ssh_config": str(ssh_config), "cost_per_hr": detailed["costPerHr"],
                "vcpu_count": detailed["vcpuCount"], "memory_gib": detailed["memoryInGb"],
                "data_center_id": detailed["machine"]["dataCenterId"],
                "effective_vcpu_limit": affinity_plan["effective_vcpu_limit"],
                "cpu_affinity_plan": affinity_plan,
                "stop_utc": config["stop_utc"], "terminate_utc": config["terminate_utc"],
                "main_bundle_uploaded": False, "status": "PF4_WORKER_READY_PREUPLOAD",
                "utc": iso(now_utc()),
            }
            atomic_new(runtime / "running-worker-receipt.json", canonical(record))
            atomic_new(runtime / "attempt-ledger.json", canonical(attempt_ledger + [{
                "attempt": attempt, "pod_id": pod_id, "outcome": "READY_PREUPLOAD",
                "create_argv_sha256": hashlib.sha256(canonical(create)).hexdigest(),
            }]))
            print(canonical(record).decode("utf-8"), flush=True)
            return 0
        except BaseException as exc:
            elapsed = max(0.0, time.monotonic() - started)
            total_attempt_seconds += elapsed
            entry = {
                "attempt": attempt, "pod_id": pod_id or None,
                "error_type": type(exc).__name__, "error": str(exc),
                "elapsed_seconds": round(elapsed, 3),
                "main_bundle_uploaded": False,
            }
            attempt_ledger.append(entry)
            atomic_new(attempt_root / "attempt-result.json", canonical(entry))
            if pod_id:
                delete_and_prove(root=root, runtime=runtime, guard=guard, cli=cli,
                                 campaign=campaign, pod_id=pod_id, attempt=attempt)
            atomic_new(runtime / "attempt-ledger.part.json", canonical(attempt_ledger))
            retryable = str(exc).split(":", 1)[0] in {
                "CREATE_COMMAND_FAILED", "CREATE_ID_MISSING", "SSH_METADATA_TIMEOUT",
                "SSH_BINDING_INVALID", "SSH_HOST_KEY_SCAN_TIMEOUT", "SSH_READINESS_TIMEOUT",
                "RETURNED_WORKER_MISMATCH", "LifecycleLaunchError",
            }
            if not retryable:
                raise
            if attempt < config["max_attempts"]:
                time.sleep((15, 30)[min(attempt - 1, 1)])
    atomic_new(runtime / "attempt-ledger.json", canonical(attempt_ledger))
    raise R6LaunchError("RUNPOD_RETRY_ENVELOPE_EXHAUSTED")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BaseException as exc:
        print(f"PDH3_R12_R6_LAUNCH_BLOCKED:{type(exc).__name__}:{exc}", file=sys.stderr)
        raise
