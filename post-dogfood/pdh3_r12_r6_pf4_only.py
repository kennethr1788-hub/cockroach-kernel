#!/usr/bin/env python3
"""Execute exactly PF-4, retrieve its evidence, and delete the paid worker."""
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

import pdh3_r12_r6_config as r6_config


class PF4OnlyError(RuntimeError):
    """Stable PF-4-only controller failure."""


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def atomic_new(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb", closefd=True) as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def run(
    root: Path, argv: list[str], timeout: int | None = None
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        argv, cwd=root, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, timeout=timeout, check=False, shell=False,
    )


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise PF4OnlyError("MODULE_LOAD_FAILED:" + name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def campaign_empty(guard: Any, cli: Path, campaign: str) -> bool:
    try:
        return guard.campaign_active(cli, campaign, timeout_seconds=30) == []
    except Exception:
        return False


def provider_absent(guard: Any, cli: Path, campaign: str, pod_id: str) -> bool:
    try:
        present, _, _ = guard.pod_get(cli, pod_id, timeout_seconds=30)
        return not present and campaign_empty(guard, cli, campaign)
    except Exception:
        return False


def wait_for_terminal_guard(
    lifecycle: Any, log: Path, *, timeout_seconds: int = 180
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        records = lifecycle.read_chain(log)
        if records:
            terminal = records[-1]
            if terminal.get("event") == "TEARDOWN_GREEN":
                return terminal
            if terminal.get("event") == "GUARD_BLOCKED":
                raise PF4OnlyError("LIFECYCLE_GUARD_BLOCKED")
        time.sleep(1)
    raise PF4OnlyError("LIFECYCLE_TERMINAL_MISSING")


def delete_and_prove(
    *, root: Path, runtime: Path, guard: Any, lifecycle: Any, cli: Path,
    campaign: str, pod_id: str, attempt: int,
) -> dict[str, Any]:
    if not provider_absent(guard, cli, campaign, pod_id):
        deleted = run(
            root, [str(cli), "pod", "delete", pod_id, "--output", "json"], 60
        )
        atomic_new(runtime / "pf4-only-delete.stdout", deleted.stdout)
        atomic_new(runtime / "pf4-only-delete.stderr", deleted.stderr)
        if deleted.returncode != 0:
            raise PF4OnlyError("PF4_ONLY_DELETE_COMMAND_FAILED")
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        if provider_absent(guard, cli, campaign, pod_id):
            break
        time.sleep(5)
    else:
        raise PF4OnlyError("PF4_ONLY_TEARDOWN_UNPROVEN")
    terminal = wait_for_terminal_guard(
        lifecycle, runtime / f"attempt-{attempt:02d}" / "lifecycle.ndjson"
    )
    body = {
        "version": "ck-pdh3-r12-r6-pf4-only-teardown-v1",
        "pod_id": pod_id,
        "campaign_id": campaign,
        "exact_id_absent": True,
        "campaign_inventory": [],
        "lifecycle_terminal_event_hash": terminal["event_hash"],
        "teardown_green": True,
    }
    return {**body, "receipt_sha256": digest(body)}


def terminal_green(
    *, create_returncode: int, pf4_returncode: int, teardown_green: bool,
    pf4_status: str | None,
) -> bool:
    return (
        create_returncode == 0
        and pf4_returncode == 0
        and teardown_green
        and pf4_status == "PF4_GREEN"
    )


def main() -> int:
    config = r6_config.load()
    root = Path(config["root"])
    runtime = Path(config["runtime"])
    cli = Path(config["runpodctl"])
    campaign = str(config["campaign_id"])
    guard = load_module(root / "s2-soak/lifecycle_guard.py", "pdh3_r12_pf4_only_guard")
    lifecycle = load_module(
        root / "post-dogfood/pdh3_r12_lifecycle_launch.py",
        "pdh3_r12_pf4_only_lifecycle",
    )
    launch_script = root / "post-dogfood/pdh3_r12_r6_launch_pf4.py"
    pf4_script = root / "post-dogfood/pdh3_r12_r6_run_pf4.py"
    launch = run(root, [sys.executable, str(launch_script)], None)
    if runtime.is_dir():
        atomic_new(runtime / "pf4-only-launch.stdout", launch.stdout)
        atomic_new(runtime / "pf4-only-launch.stderr", launch.stderr)
    if launch.returncode != 0:
        if runtime.is_dir():
            body = {
                "version": "ck-pdh3-r12-r6-pf4-only-terminal-v1",
                "status": "PF4_ONLY_BLOCKED",
                "stage": "CREATE",
                "launch_returncode": launch.returncode,
                "campaign_inventory_empty": campaign_empty(guard, cli, campaign),
                "measured_24h_started": False,
            }
            atomic_new(runtime / "PF4_ONLY_TERMINAL.json", canonical({
                **body, "receipt_sha256": digest(body),
            }))
        return launch.returncode

    running = json.loads((runtime / "running-worker-receipt.json").read_bytes())
    pod_id = str(running["pod_id"])
    attempt = int(running["attempt"])
    pf4 = run(root, [sys.executable, str(pf4_script)], None)
    atomic_new(runtime / "pf4-only-capability.stdout", pf4.stdout)
    atomic_new(runtime / "pf4-only-capability.stderr", pf4.stderr)
    teardown: dict[str, Any] | None = None
    teardown_error: BaseException | None = None
    try:
        teardown = delete_and_prove(
            root=root, runtime=runtime, guard=guard, lifecycle=lifecycle,
            cli=cli, campaign=campaign, pod_id=pod_id, attempt=attempt,
        )
    except BaseException as exc:
        teardown_error = exc
    pf4_receipt = (
        json.loads((runtime / "PF4_HOST_RECEIPT.json").read_bytes())
        if (runtime / "PF4_HOST_RECEIPT.json").is_file()
        else {}
    )
    green = terminal_green(
        create_returncode=launch.returncode,
        pf4_returncode=pf4.returncode,
        teardown_green=teardown is not None and teardown.get("teardown_green") is True,
        pf4_status=pf4_receipt.get("status"),
    )
    body = {
        "version": "ck-pdh3-r12-r6-pf4-only-terminal-v1",
        "status": "PF4_ONLY_GREEN" if green else "PF4_ONLY_BLOCKED",
        "campaign_id": campaign,
        "pod_id": pod_id,
        "packet_sha256": config["packet_sha256"],
        "launch_returncode": launch.returncode,
        "pf4_returncode": pf4.returncode,
        "pf4_host_receipt_sha256": (
            hashlib.sha256((runtime / "PF4_HOST_RECEIPT.json").read_bytes()).hexdigest()
            if (runtime / "PF4_HOST_RECEIPT.json").is_file()
            else None
        ),
        "teardown": teardown,
        "teardown_error": (
            None if teardown_error is None
            else type(teardown_error).__name__ + ":" + str(teardown_error)
        ),
        "main_bundle_uploaded": False,
        "measured_24h_started": False,
        "utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "green": green,
    }
    record = {**body, "receipt_sha256": digest(body)}
    atomic_new(runtime / "PF4_ONLY_TERMINAL.json", canonical(record))
    print(canonical(record).decode("utf-8"), flush=True)
    if not green:
        raise PF4OnlyError("PF4_ONLY_NOT_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
