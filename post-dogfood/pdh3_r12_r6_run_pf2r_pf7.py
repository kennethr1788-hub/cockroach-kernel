#!/usr/bin/env python3
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

import pdh3_r12_cpu_affinity as cpu_affinity
import pdh3_r12_r6_config as r6_config


CONFIG = r6_config.load()
ROOT = Path(CONFIG["root"])
RUNTIME = Path(CONFIG["runtime"])
RUNPODCTL = Path(CONFIG["runpodctl"])
CAMPAIGN = CONFIG["campaign_id"]
RUNNING = json.loads((RUNTIME / "running-worker-receipt.json").read_bytes())
POD_NAME = str(RUNNING["pod_name"])
PACKET_SHA256 = CONFIG["packet_sha256"]
ARCHIVE = Path(CONFIG["archive"])
ARCHIVE_SHA256 = CONFIG["archive_sha256"]
BUNDLE_RECEIPT = Path(CONFIG["bundle_receipt"])
PACKET = Path(CONFIG["packet"])
REMOTE = "/workspace/" + CAMPAIGN
REMOTE_APP = REMOTE + "/app"
REMOTE_EXPORT = REMOTE + "/export"
REMOTE_ACK = REMOTE + "/acks"
LOCAL_CHECKPOINTS = RUNTIME / "checkpoints"
CLOSEOUT_DEADLINE = (
    datetime.fromisoformat(CONFIG["stop_utc"].replace("Z", "+00:00")).timestamp()
    - 900
)


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_name("." + path.name + ".part")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def run(argv: list[str], timeout: int = 90) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(argv, cwd=ROOT, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=timeout, check=False, shell=False)


def delete_and_prove(pod_id: str) -> None:
    deleted = run([RUNPODCTL.as_posix(), "pod", "delete", pod_id, "--output", "json"], 60)
    atomic_write(RUNTIME / "pf8-delete.stdout", deleted.stdout)
    atomic_write(RUNTIME / "pf8-delete.stderr", deleted.stderr)
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        if provider_absent(pod_id):
            atomic_write(RUNTIME / "pf8-inventory.json", b"[]")
            return
        time.sleep(5)
    raise RuntimeError("PF8_TEARDOWN_UNPROVEN")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("MODULE_LOAD_FAILED:" + name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SUPERVISOR = load_module(ROOT / "post-dogfood/pdh3_r12_preflight_supervisor.py", "pdh3_r12_host_supervisor")
CHECKPOINT = SUPERVISOR.checkpoint
GUARD = load_module(ROOT / "s2-soak/lifecycle_guard.py", "pdh3_r12_terminal_guard")


def provider_absent(pod_id: str) -> bool:
    try:
        present, _, _ = GUARD.pod_get(RUNPODCTL, pod_id, timeout_seconds=30)
        active = GUARD.campaign_active(RUNPODCTL, CAMPAIGN, timeout_seconds=30)
    except Exception:
        return False
    return not present and active == []


def scp_exact(config, remote_name: str, local: Path) -> Path:
    return SUPERVISOR.atomic_scp(config, remote_name, local)


def pull_and_ack(config, ssh_base: list[str], scp_base: list[str], target_sequence: int) -> int:
    previous_sequence, previous_hash = SUPERVISOR.previous_state(LOCAL_CHECKPOINTS)
    for sequence in range(previous_sequence + 1, target_sequence + 1):
        manifest_name = f"checkpoint-{sequence:04d}.json"
        archive_name = f"checkpoint-{sequence:04d}.tgz"
        manifest_path = scp_exact(config, manifest_name, LOCAL_CHECKPOINTS / manifest_name)
        archive_path = scp_exact(config, archive_name, LOCAL_CHECKPOINTS / archive_name)
        verified = CHECKPOINT.verify_download(
            manifest_path=manifest_path,
            archive_path=archive_path,
            expected_packet_sha256=PACKET_SHA256,
            expected_sequence=sequence,
            expected_previous_manifest_sha256=previous_hash,
        )
        ack = CHECKPOINT.acknowledge(
            output=LOCAL_CHECKPOINTS / f"checkpoint-{sequence:04d}.ack.json",
            manifest=verified,
            local_archive=archive_path,
            acknowledged_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        state = {
            "version": "ck-pdh3-r12-pull-state-v1",
            "last_sequence": sequence,
            "last_manifest_sha256": verified["manifest_sha256"],
            "last_ack_sha256": ack["ack_sha256"],
        }
        CHECKPOINT.write_hashed(LOCAL_CHECKPOINTS / "pull-state.json", state, "state_sha256")
        host_ack_body = {
            "version": "ck-pdh3-r12-host-ack-v1",
            "sequence": sequence,
            "packet_sha256": PACKET_SHA256,
            "manifest_sha256": verified["manifest_sha256"],
            "local_ack_sha256": ack["ack_sha256"],
            "verified": True,
        }
        host_ack = CHECKPOINT.write_hashed(
            LOCAL_CHECKPOINTS / f"host-ack-{sequence:04d}.json",
            host_ack_body, "host_ack_sha256",
        )
        local_ack = LOCAL_CHECKPOINTS / f"host-ack-{sequence:04d}.json"
        temporary = f"{REMOTE_ACK}/host-ack-{sequence:04d}.json.part"
        final = f"{REMOTE_ACK}/host-ack-{sequence:04d}.json"
        uploaded = run([*scp_base, str(local_ack), f"{POD_NAME}:{temporary}"], 300)
        promoted = run([*ssh_base, "mv", "--", temporary, final], 60) if uploaded.returncode == 0 else uploaded
        if uploaded.returncode != 0 or promoted.returncode != 0 or host_ack.get("verified") is not True:
            raise RuntimeError("REMOTE_ACK_FAILED")
        previous_hash = verified["manifest_sha256"]
    return target_sequence


def best_effort_retrieve(ssh_base: list[str], scp_base: list[str]) -> None:
    command = [*ssh_base, "tar", "-czf", f"{REMOTE}/final-evidence.tgz",
               "-C", REMOTE, "output", "network", "remote-launch.log",
               "remote-launch-receipt.json"]
    packed = run(command, 1800)
    atomic_write(RUNTIME / "pf8-pack.stdout", packed.stdout)
    atomic_write(RUNTIME / "pf8-pack.stderr", packed.stderr)
    if packed.returncode != 0:
        return
    sidecar = run([*ssh_base, "sha256sum", f"{REMOTE}/final-evidence.tgz"], 120)
    atomic_write(RUNTIME / "pf8-remote-sha256.txt", sidecar.stdout)
    retrieved = run([*scp_base, f"{POD_NAME}:{REMOTE}/final-evidence.tgz",
                     str(RUNTIME / "final-evidence.tgz")], 1800)
    atomic_write(RUNTIME / "pf8-retrieve.stderr", retrieved.stderr)
    if retrieved.returncode != 0 or sha256(RUNTIME / "final-evidence.tgz") not in sidecar.stdout.decode("utf-8", "replace"):
        raise RuntimeError("PF8_ARCHIVE_HASH_MISMATCH")


def main() -> int:
    pf4 = json.loads((RUNTIME / "PF4_HOST_RECEIPT.json").read_bytes())
    if pf4.get("status") != "PF4_GREEN" or pf4.get("packet_sha256") != PACKET_SHA256:
        raise RuntimeError("PF4_NOT_GREEN")
    pod_id = str(pf4.get("pod_id", ""))
    config_path = r6_config.require_runtime_file(
        RUNTIME, RUNNING.get("ssh_config"), "SSH_CONFIG"
    )
    ssh_base = ["/usr/bin/ssh", "-F", str(config_path), POD_NAME]
    scp_base = ["/usr/bin/scp", "-F", str(config_path)]
    workload_started = False
    final_green = False
    error: BaseException | None = None
    try:
        try:
            affinity_plan = cpu_affinity.effective_vcpu_plan(
                int(RUNNING["vcpu_count"]), int(RUNNING["memory_gib"])
            )
        except (KeyError, TypeError, ValueError, cpu_affinity.AffinityError) as exc:
            raise RuntimeError("RUNNING_AFFINITY_PLAN_INVALID") from exc
        if (
            RUNNING.get("effective_vcpu_limit")
            != affinity_plan["effective_vcpu_limit"]
            or RUNNING.get("cpu_affinity_plan") != affinity_plan
        ):
            raise RuntimeError("RUNNING_AFFINITY_PLAN_MISMATCH")
        # The remote launcher creates output/export/ack roots atomically and
        # rejects pre-existing roots. Only its parent may exist beforehand.
        create = run([*ssh_base, "mkdir", "-p", "--", REMOTE], 60)
        if create.returncode != 0:
            raise RuntimeError("REMOTE_STAGE_ROOT_CREATE_FAILED")
        transfers = (
            (ARCHIVE, REMOTE + "/pdh3-r12-bundle.tgz"),
            (BUNDLE_RECEIPT, REMOTE + "/bundle-receipt.json"),
            (PACKET, REMOTE + "/frozen-packet.md"),
        )
        atomic_write(RUNTIME / "main-bundle-upload-started.json", canonical({
            "version": "ck-pdh3-r12-r6-upload-marker-v1",
            "packet_sha256": PACKET_SHA256,
            "pod_id": pod_id,
            "replacement_forbidden": True,
        }))
        for local, remote in transfers:
            sent = run([*scp_base, str(local), f"{POD_NAME}:{remote}"], 1800)
            if sent.returncode != 0:
                raise RuntimeError("MAIN_TRANSFER_FAILED:" + local.name)
        hashes = run([*ssh_base, "sha256sum", REMOTE + "/pdh3-r12-bundle.tgz",
                      REMOTE + "/frozen-packet.md"], 120)
        remote_hash_text = hashes.stdout.decode("utf-8", "replace")
        if (hashes.returncode != 0 or ARCHIVE_SHA256 not in remote_hash_text
                or PACKET_SHA256 not in remote_hash_text):
            raise RuntimeError("REMOTE_MAIN_HASH_MISMATCH")
        staging = run([*ssh_base, "mkdir", "--", REMOTE + "/staging"], 60)
        if staging.returncode != 0:
            raise RuntimeError("REMOTE_STAGING_CREATE_FAILED")
        unpack = run([*ssh_base, "tar", "-xzf", REMOTE + "/pdh3-r12-bundle.tgz",
                      "-C", REMOTE + "/staging"], 1800)
        if unpack.returncode != 0:
            raise RuntimeError("REMOTE_STAGING_EXTRACT_FAILED")
        smoke = run([*ssh_base, "python3",
                     REMOTE + "/staging/post-dogfood/build_pdh3_scale_bundle.py",
                     "--verify-archive", REMOTE + "/pdh3-r12-bundle.tgz",
                     "--verify-receipt", REMOTE + "/bundle-receipt.json",
                     "--verify-root", REMOTE_APP,
                     "--verify-smoke-receipt", REMOTE + "/remote-smoke.json"], 3600)
        atomic_write(RUNTIME / "remote-smoke.stdout", smoke.stdout)
        atomic_write(RUNTIME / "remote-smoke.stderr", smoke.stderr)
        smoke_get = run([*scp_base, f"{POD_NAME}:{REMOTE}/remote-smoke.json",
                         str(RUNTIME / "remote-smoke.json")], 300)
        atomic_write(RUNTIME / "remote-smoke.retrieve.stderr", smoke_get.stderr)
        if smoke_get.returncode != 0:
            if smoke.returncode != 0:
                raise RuntimeError("REMOTE_SMOKE_FAILURE_RECEIPT_UNRETRIEVABLE")
            raise RuntimeError("REMOTE_SMOKE_RECEIPT_INVALID")
        try:
            smoke_receipt = r6_config.validate_remote_smoke_receipt(
                RUNTIME / "remote-smoke.json", ARCHIVE_SHA256
            )
        except r6_config.R6ConfigError as exc:
            raise RuntimeError("REMOTE_SMOKE_RECEIPT_INVALID") from exc
        diagnostic = {
            "version": "ck-pdh3-r12-r6-host-smoke-diagnostic-v1",
            "packet_sha256": PACKET_SHA256,
            "archive_sha256": ARCHIVE_SHA256,
            "remote_command_returncode": smoke.returncode,
            "remote_smoke_sha256": smoke_receipt["smoke_sha256"],
            "green": smoke_receipt.get("green") is True,
            "failed_checks": smoke_receipt["failed_checks"],
        }
        atomic_write(
            RUNTIME / "remote-smoke-host-diagnostic.json",
            canonical(diagnostic),
        )
        if smoke.returncode != 0 or smoke_receipt.get("green") is not True:
            raise RuntimeError("REMOTE_EXTRACTED_SMOKE_FAILED")
        tracer_root = REMOTE + "/tracer"
        tracer = tracer_root + "/usr/bin/strace"
        tracer_library_path = (
            tracer_root + "/usr/lib/x86_64-linux-gnu:"
            + tracer_root + "/lib/x86_64-linux-gnu"
        )
        strace_deb = (
            REMOTE_APP
            + "/p2-cleanroom/vendor/ubuntu-noble-strace/strace_6.8-0ubuntu2_amd64.deb"
        )
        unwind_deb = (
            REMOTE_APP
            + "/p2-cleanroom/vendor/ubuntu-noble-strace/libunwind8_1.6.2-3build1_amd64.deb"
        )
        for command in (
            [*ssh_base, "dpkg-deb", "--extract", unwind_deb, tracer_root],
            [*ssh_base, "dpkg-deb", "--extract", strace_deb, tracer_root],
        ):
            if run(command, 300).returncode != 0:
                raise RuntimeError("REMOTE_TRACER_EXTRACTION_FAILED")
        tracer_hash = run([*ssh_base, "sha256sum", tracer], 60)
        if (tracer_hash.returncode != 0
                or CONFIG["tracer_binary_sha256"]
                not in tracer_hash.stdout.decode("utf-8", "replace")):
            raise RuntimeError("REMOTE_TRACER_HASH_MISMATCH")
        setup = run([*ssh_base, "mkdir", "-p", "--", REMOTE + "/empty-home",
                     REMOTE + "/runtime-parent", REMOTE + "/pf2-parent"], 60)
        if setup.returncode != 0:
            raise RuntimeError("REMOTE_RUNTIME_ROOT_CREATE_FAILED")
        launched = run([
            *ssh_base, "python3", REMOTE_APP + "/post-dogfood/pdh3_r12_remote_launcher.py",
            "--observer", REMOTE_APP + "/post-dogfood/pdh3_r12_network_observer.py",
            "--runner", REMOTE_APP + "/post-dogfood/pdh3_r12_remote_preflight.py",
            "--binary", REMOTE_APP + "/p2-cleanroom/vendor/cockroach-v26.2.3-linux/cockroach-v26.2.3.linux-amd64/cockroach",
            "--packet", REMOTE + "/frozen-packet.md",
            "--packet-sha256", PACKET_SHA256, "--campaign-id", CAMPAIGN,
            "--tracer", tracer,
            "--tracer-sha256", CONFIG["tracer_binary_sha256"],
            "--tracer-root", tracer_root,
            "--tracer-library-path", tracer_library_path,
            "--workdir", REMOTE_APP, "--empty-home", REMOTE + "/empty-home",
            "--output", REMOTE + "/output", "--export-root", REMOTE_EXPORT,
            "--remote-ack-root", REMOTE_ACK, "--network-output", REMOTE + "/network",
            "--runtime-parent", REMOTE + "/runtime-parent",
            "--pf2-runtime-parent", REMOTE + "/pf2-parent",
            "--setup-timeout-seconds", "10800", "--host-ack-timeout-seconds", "900",
            "--provider-vcpus", str(RUNNING["vcpu_count"]),
            "--provider-memory-gib", str(RUNNING["memory_gib"]),
            "--effective-vcpu-limit", str(RUNNING["effective_vcpu_limit"]),
            "--receipt", REMOTE + "/remote-launch-receipt.json",
            "--log", REMOTE + "/remote-launch.log",
        ], 300)
        atomic_write(RUNTIME / "remote-launch.stdout", launched.stdout)
        atomic_write(RUNTIME / "remote-launch.stderr", launched.stderr)
        if launched.returncode != 0:
            raise RuntimeError("REMOTE_LAUNCH_FAILED")
        launch_receipt = json.loads(launched.stdout)
        remote_pid = int(launch_receipt["pid"])
        workload_started = True

        config = SUPERVISOR.PullConfig(
            ssh_config=config_path, ssh_alias=POD_NAME,
            remote_export_root=REMOTE_EXPORT, local_root=LOCAL_CHECKPOINTS,
            packet_sha256=PACKET_SHA256, deadline_epoch=CLOSEOUT_DEADLINE,
            transfer_timeout_seconds=900, closeout_reserve_seconds=900,
        )
        last_sequence = 0
        while time.time() < CLOSEOUT_DEADLINE - 900:
            latest = run([*ssh_base, "test", "-f", REMOTE_EXPORT + "/latest.json",
                          "&&", "cat", REMOTE_EXPORT + "/latest.json"], 60)
            if latest.returncode == 0 and latest.stdout:
                pointer = json.loads(latest.stdout)
                target = int(pointer["sequence"])
                if target > last_sequence:
                    last_sequence = pull_and_ack(config, ssh_base, scp_base, target)
            alive = run([*ssh_base, "kill", "-0", str(remote_pid)], 30)
            if alive.returncode != 0:
                time.sleep(3)
                latest = run([*ssh_base, "test", "-f", REMOTE_EXPORT + "/latest.json",
                              "&&", "cat", REMOTE_EXPORT + "/latest.json"], 60)
                if latest.returncode == 0 and latest.stdout:
                    target = int(json.loads(latest.stdout)["sequence"])
                    if target > last_sequence:
                        last_sequence = pull_and_ack(config, ssh_base, scp_base, target)
                break
            time.sleep(2)
        else:
            raise RuntimeError("REMOTE_PREFLIGHT_DEADLINE_EXCEEDED")
        result_get = run([*scp_base, f"{POD_NAME}:{REMOTE}/output/result.json",
                          str(RUNTIME / "remote-result.json")], 300)
        network_get = run([*scp_base, f"{POD_NAME}:{REMOTE}/network/network-receipt.json",
                           str(RUNTIME / "network-receipt.json")], 300)
        if result_get.returncode != 0 or network_get.returncode != 0:
            raise RuntimeError("TERMINAL_RECEIPT_RETRIEVAL_FAILED")
        result = json.loads((RUNTIME / "remote-result.json").read_bytes())
        network = json.loads((RUNTIME / "network-receipt.json").read_bytes())
        if (result.get("status") != "GREEN_PENDING_PF8" or result.get("green_pending_pf8") is not True
                or result.get("measured_24h_started") is not False or network.get("green") is not True):
            raise RuntimeError("REMOTE_PREFLIGHT_SEMANTIC_NON_GREEN")
        best_effort_retrieve(ssh_base, scp_base)
        final_green = True
    except BaseException as exc:
        error = exc
        try:
            if workload_started:
                best_effort_retrieve(ssh_base, scp_base)
        except BaseException as retrieval_error:
            atomic_write(RUNTIME / "pf8-retrieval-error.txt",
                         (type(retrieval_error).__name__ + ":" + str(retrieval_error)).encode())
    finally:
        delete_and_prove(pod_id)

    user = run([RUNPODCTL.as_posix(), "user", "--output", "json"], 30)
    account = json.loads(user.stdout) if user.returncode == 0 else {}
    terminal = {
        "version": "ck-pdh3-r12-pf8-host-terminal-v1",
        "campaign_id": CAMPAIGN, "pod_id": pod_id,
        "packet_sha256": PACKET_SHA256,
        "status": "GREEN_PENDING_FINAL_GLM" if final_green else "BLOCKED",
        "error_type": None if error is None else type(error).__name__,
        "error": None if error is None else str(error),
        "last_checkpoint_sequence": (SUPERVISOR.previous_state(LOCAL_CHECKPOINTS)[0]
                                     if (LOCAL_CHECKPOINTS / "pull-state.json").is_file() else 0),
        "worker_absent": provider_absent(pod_id),
        "campaign_inventory_empty": provider_absent(pod_id),
        "measured_24h_started": False,
        "account_balance_after": account.get("clientBalance"),
        "current_spend_per_hr_after": account.get("currentSpendPerHr"),
        "utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    atomic_write(RUNTIME / "PF8_HOST_TERMINAL.json", canonical(terminal))
    print(canonical(terminal).decode(), flush=True)
    if not final_green:
        raise RuntimeError("REMOTE_PREFLIGHT_BLOCKED:" + str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
