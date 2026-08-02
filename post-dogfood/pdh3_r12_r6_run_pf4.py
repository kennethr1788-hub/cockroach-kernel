#!/usr/bin/env python3
"""Run the minimal, pre-main-upload R6 capability gate."""
from __future__ import annotations

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
import pdh3_r12_r6_config as r6_config


class PF4Error(RuntimeError):
    """Stable R6 PF4 failure."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def atomic_new(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb", closefd=True) as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def run(root: Path, argv: list[str], timeout: int = 90) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(argv, cwd=root, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=timeout, check=False, shell=False)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise PF4Error("MODULE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def provider_absent(guard: Any, cli: Path, campaign: str, pod_id: str) -> bool:
    try:
        present, _, _ = guard.pod_get(cli, pod_id, timeout_seconds=30)
        active = guard.campaign_active(cli, campaign, timeout_seconds=30)
    except Exception:
        return False
    return not present and active == []


def delete_and_prove(root: Path, runtime: Path, guard: Any, cli: Path,
                     campaign: str, pod_id: str) -> None:
    result = run(root, [str(cli), "pod", "delete", pod_id, "--output", "json"], 60)
    atomic_new(runtime / "pf4-delete.stdout", result.stdout)
    atomic_new(runtime / "pf4-delete.stderr", result.stderr)
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        if provider_absent(guard, cli, campaign, pod_id):
            atomic_new(runtime / "pf4-post-delete-inventory.json", b"[]")
            return
        time.sleep(5)
    raise PF4Error("PF4_TEARDOWN_UNPROVEN")


def main() -> int:
    config = r6_config.load()
    root = Path(config["root"])
    runtime = Path(config["runtime"])
    running = json.loads((runtime / "running-worker-receipt.json").read_bytes())
    if (running.get("status") != "PF4_WORKER_READY_PREUPLOAD"
            or running.get("version") != "ck-pdh3-r12-r6-running-worker-v2"
            or running.get("packet_sha256") != config["packet_sha256"]
            or running.get("main_bundle_uploaded") is not False):
        raise PF4Error("RUNNING_RECEIPT_INVALID")
    try:
        expected_affinity = cpu_affinity.effective_vcpu_plan(
            int(running["vcpu_count"]), int(running["memory_gib"])
        )
    except (KeyError, TypeError, ValueError, cpu_affinity.AffinityError) as exc:
        raise PF4Error("RUNNING_AFFINITY_PLAN_INVALID") from exc
    if (
        running.get("cpu_affinity_plan") != expected_affinity
        or running.get("effective_vcpu_limit")
        != expected_affinity["effective_vcpu_limit"]
    ):
        raise PF4Error("RUNNING_AFFINITY_PLAN_MISMATCH")
    pod_id = str(running.get("pod_id", ""))
    pod_name = str(running.get("pod_name", ""))
    cli = Path(config["runpodctl"])
    guard = load_module(root / "s2-soak/lifecycle_guard.py", "pdh3_r12_r6_pf4_guard")
    ssh_config = r6_config.require_runtime_file(
        runtime, running.get("ssh_config"), "SSH_CONFIG"
    )
    ssh = ["/usr/bin/ssh", "-F", str(ssh_config), pod_name]
    scp = ["/usr/bin/scp", "-F", str(ssh_config)]
    remote = f"/workspace/{config['campaign_id']}/pf4"
    observer = root / "post-dogfood/pdh3_r12_network_observer.py"
    trace_support = root / "post-dogfood/run_pdh3_traced.py"
    affinity_support = root / "post-dogfood/pdh3_r12_cpu_affinity.py"
    capability = root / "post-dogfood/pdh3_r12_remote_capability.py"
    strace_deb = root / "p2-cleanroom/vendor/ubuntu-noble-strace/strace_6.8-0ubuntu2_amd64.deb"
    unwind_deb = root / "p2-cleanroom/vendor/ubuntu-noble-strace/libunwind8_1.6.2-3build1_amd64.deb"
    tracer_root = remote + "/tracer"
    tracer = tracer_root + "/usr/bin/strace"
    library_path = tracer_root + "/usr/lib/x86_64-linux-gnu:" + tracer_root + "/lib/x86_64-linux-gnu"
    try:
        make = run(root, [*ssh, "mkdir", "-p", "--", remote], 60)
        if make.returncode != 0:
            raise PF4Error("REMOTE_ROOT_CREATE_FAILED")
        payload = (
            observer, trace_support, affinity_support, capability, strace_deb,
            unwind_deb,
        )
        for local in payload:
            transfer = run(root, [*scp, str(local), f"{pod_name}:{remote}/{local.name}"], 600)
            if transfer.returncode != 0:
                raise PF4Error("PF4_TRANSFER_FAILED:" + local.name)
        expected = {path.name: sha256(path) for path in payload}
        remote_hashes = run(root, [*ssh, "sha256sum", *[f"{remote}/{name}" for name in expected]], 120)
        text = remote_hashes.stdout.decode("utf-8", "replace")
        if remote_hashes.returncode != 0 or not all(value in text for value in expected.values()):
            raise PF4Error("PF4_REMOTE_HASH_MISMATCH")
        setup_commands = (
            [*ssh, "dpkg-deb", "--extract", f"{remote}/{unwind_deb.name}", tracer_root],
            [*ssh, "dpkg-deb", "--extract", f"{remote}/{strace_deb.name}", tracer_root],
        )
        for command in setup_commands:
            if run(root, command, 300).returncode != 0:
                raise PF4Error("TRACER_EXTRACTION_FAILED")
        tracer_hash = run(root, [*ssh, "sha256sum", tracer], 60)
        if (tracer_hash.returncode != 0
                or config["tracer_binary_sha256"] not in tracer_hash.stdout.decode("utf-8", "replace")):
            raise PF4Error("TRACER_BINARY_HASH_MISMATCH")
        output = remote + "/PF4_CAPABILITY_RECEIPT.json"
        observer_stdout = remote + "/PF4_NETWORK_OBSERVER.stdout"
        observer_stderr = remote + "/PF4_NETWORK_OBSERVER.stderr"
        command = [
            *ssh, "/usr/bin/env", "-i", "HOME=" + remote + "/empty-home",
            "LANG=C.UTF-8", "LC_ALL=C.UTF-8", "PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "LD_LIBRARY_PATH=" + library_path, "PYTHONDONTWRITEBYTECODE=1", "PYTHONHASHSEED=0", "TZ=UTC",
            "python3", remote + "/" + capability.name,
            "--workdir", remote + "/benchmark-root", "--output", output,
            "--observer", remote + "/" + observer.name,
            "--allocated-vcpus", str(running["vcpu_count"]),
            "--allocated-memory-gib", str(running["memory_gib"]),
            "--effective-vcpu-limit", str(running["effective_vcpu_limit"]),
            "--packet-sha256", config["packet_sha256"],
            "--tracer", tracer, "--tracer-sha256", config["tracer_binary_sha256"],
        ]
        result = run(root, command, 2400)
        atomic_new(runtime / "pf4-command.stdout", result.stdout)
        atomic_new(runtime / "pf4-command.stderr", result.stderr)
        for remote_path, local_name in (
            (observer_stdout, "PF4_NETWORK_OBSERVER.stdout"),
            (observer_stderr, "PF4_NETWORK_OBSERVER.stderr"),
        ):
            captured = run(root, [*scp, f"{pod_name}:{remote_path}", str(runtime / local_name)], 300)
            atomic_new(runtime / (local_name + ".retrieve.stderr"), captured.stderr)
        retrieve = run(root, [*scp, f"{pod_name}:{output}",
                              str(runtime / "PF4_CAPABILITY_RECEIPT.json")], 300)
        atomic_new(runtime / "pf4-retrieve.stderr", retrieve.stderr)
        if result.returncode != 0 or retrieve.returncode != 0:
            raise PF4Error("PF4_CAPABILITY_OR_RETRIEVAL_FAILED")
        receipt_path = runtime / "PF4_CAPABILITY_RECEIPT.json"
        receipt = json.loads(receipt_path.read_bytes())
        core = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        if (receipt.get("green") is not True
                or hashlib.sha256(canonical(core)).hexdigest() != receipt.get("receipt_sha256")):
            raise PF4Error("PF4_RECEIPT_INVALID")
        observer_record = receipt.get("observed", {}).get("streaming_network_observer", {})
        if (
            sha256(runtime / "PF4_NETWORK_OBSERVER.stdout")
            != observer_record.get("stdout_sha256")
            or sha256(runtime / "PF4_NETWORK_OBSERVER.stderr")
            != observer_record.get("stderr_sha256")
        ):
            raise PF4Error("PF4_OBSERVER_STREAM_HASH_MISMATCH")
        remote_hash = run(root, [*ssh, "sha256sum", output], 60)
        if (remote_hash.returncode != 0
                or sha256(receipt_path) not in remote_hash.stdout.decode("utf-8", "replace")):
            raise PF4Error("PF4_OFFWORKER_ROUNDTRIP_MISMATCH")
        cleanup = run(root, [*ssh, "rm", "-rf", "--", remote], 300)
        residue = run(root, [*ssh, "test", "!", "-e", remote], 60)
        if cleanup.returncode != 0 or residue.returncode != 0:
            raise PF4Error("PF4_REMOTE_RESIDUE")
        record = {
            "version": "ck-pdh3-r12-r6-pf4-host-v1",
            "status": "PF4_GREEN", "pod_id": pod_id, "pod_name": pod_name,
            "packet_sha256": config["packet_sha256"],
            "capability_receipt_sha256": sha256(receipt_path),
            "tracer_binary_sha256": config["tracer_binary_sha256"],
            "main_bundle_uploaded": False, "remote_residue": False,
        }
        atomic_new(runtime / "PF4_HOST_RECEIPT.json", canonical(record))
        print(canonical(record).decode("utf-8"), flush=True)
        return 0
    except BaseException:
        try:
            for remote_path, local_name in (
                (remote + "/PF4_CAPABILITY_RECEIPT.json", "PF4_FAILURE_RECEIPT.json"),
                (remote + "/PF4_NETWORK_OBSERVER.stdout", "PF4_FAILURE_NETWORK_OBSERVER.stdout"),
                (remote + "/PF4_NETWORK_OBSERVER.stderr", "PF4_FAILURE_NETWORK_OBSERVER.stderr"),
            ):
                local_path = runtime / local_name
                if not local_path.exists():
                    run(root, [*scp, f"{pod_name}:{remote_path}", str(local_path)], 300)
        finally:
            delete_and_prove(root, runtime, guard, cli, config["campaign_id"], pod_id)
        raise


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BaseException as exc:
        print(f"PDH3_R12_R6_PF4_BLOCKED:{type(exc).__name__}:{exc}", file=sys.stderr)
        raise
