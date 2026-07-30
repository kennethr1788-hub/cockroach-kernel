#!/usr/bin/env python3
"""Run public, non-measured EV0 mechanics canaries.

These canaries do not count toward EV1, EV2, or EV3. The connection canary uses
a project-pinned local CockroachDB binary only to prove harness mechanics; EV2
requires the real cloud services.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time

import pg8000.dbapi

from ev_common import chained_receipt, sha256, write_atomic


CAMPAIGN_ID = "ck-ev0-public-canaries-r1"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", 0))
        return int(handle.getsockname()[1])


def _wait_port(port: int, timeout: float = 20.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
            handle.settimeout(0.25)
            if handle.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise RuntimeError("LOCAL_COCKROACH_READINESS_TIMEOUT")


def _assert_port_closed(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.settimeout(0.25)
        if handle.connect_ex(("127.0.0.1", port)) == 0:
            raise RuntimeError("LOCAL_COCKROACH_RESIDUE")


def genuine_task_rehearsal(output: Path) -> dict:
    # Import the public-interface fixture only as a canary input builder. The
    # actual invocation below is the packaged public CLI, not an in-process test.
    from cockroach_kernel.test_recovery_surface import Scenario, tree

    files = {
        "notes/intent.md": b"Implement a deterministic invoice subtotal helper.\n",
        "src/subtotal.py": (
            b"def subtotal(values):\n"
            b"    return sum(values)\n"
        ),
        "tests/test_subtotal.txt": b"subtotal([125, 75]) == 200\n",
    }
    scenario = Scenario(files=files)
    try:
        expected = {path: sha256(raw) for path, raw in sorted(files.items())}
        command = scenario.cli(scenario.output)
        completed = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            check=False, timeout=30,
        )
        summary = json.loads(completed.stdout)
        observed = tree(scenario.workspace)
        if completed.returncode != 0 or summary.get("verdict") != "PROMOTE":
            raise RuntimeError("PUBLIC_RECOVERY_CANARY_FAILED")
        if observed != expected or not summary.get("fresh_context_continued"):
            raise RuntimeError("PUBLIC_RECOVERY_CANARY_MISMATCH")
        details = {
            "interface": "cockroach-kernel recover",
            "input_class": "public_disposable_task_rehearsal",
            "command_sha256": sha256(command),
            "stdout_sha256": sha256(completed.stdout),
            "expected_tree_hash": sha256(expected),
            "observed_tree_hash": sha256(observed),
            "verdict": summary["verdict"],
            "fresh_context_continued": True,
            "measured_campaign_credit": False,
        }
        write_atomic(output / "genuine-task-canary.json", details)
        return details
    finally:
        scenario.cleanup()


def connection_interruption_rehearsal(cockroach: Path, output: Path) -> dict:
    port, http_port = _free_port(), _free_port()
    root = Path(tempfile.mkdtemp(prefix="ck-ev0-crdb-"))
    store = root / "store"
    command = [
        str(cockroach.resolve()), "start-single-node", "--insecure",
        f"--listen-addr=127.0.0.1:{port}",
        f"--http-addr=127.0.0.1:{http_port}",
        f"--store={store}", "--cache=64MiB", "--max-sql-memory=64MiB",
        "--logtostderr=WARNING",
    ]
    process = subprocess.Popen(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        _wait_port(port)
        connection = pg8000.dbapi.connect(
            user="root", host="127.0.0.1", port=port,
            database="defaultdb", ssl_context=False, timeout=5,
        )
        cursor = connection.cursor()
        cursor.execute(
            "CREATE TABLE ev0_receipts (id STRING PRIMARY KEY, payload STRING NOT NULL)"
        )
        connection.commit()
        cursor.execute("INSERT INTO ev0_receipts VALUES ('before-commit','x')")
        # A client disconnect before COMMIT must leave no durable row.
        connection.close()

        verify = pg8000.dbapi.connect(
            user="root", host="127.0.0.1", port=port,
            database="defaultdb", ssl_context=False, timeout=5,
        )
        check = verify.cursor()
        check.execute("SELECT count(*) FROM ev0_receipts WHERE id='before-commit'")
        absent = int(check.fetchone()[0]) == 0
        check.execute(
            "INSERT INTO ev0_receipts VALUES ('after-reconnect','y') "
            "ON CONFLICT (id) DO NOTHING"
        )
        verify.commit()
        check.execute("SELECT count(*) FROM ev0_receipts WHERE id='after-reconnect'")
        once = int(check.fetchone()[0]) == 1
        verify.close()
        if not absent or not once:
            raise RuntimeError("CONNECTION_INTERRUPTION_CANARY_FAILED")
        details = {
            "engine": "project_pinned_local_cockroachdb",
            "precommit_row_absent": absent,
            "reconnect_idempotent_row_count": 1,
            "local_only": True,
            "measured_campaign_credit": False,
            "command_sha256": sha256(command),
        }
        write_atomic(output / "connection-interruption-canary.json", details)
        return details
    finally:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        shutil.rmtree(root, ignore_errors=True)
        _assert_port_closed(port)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cockroach-bin", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("OUTPUT_ROOT_EXISTS")
    args.output.mkdir(parents=True, mode=0o700)
    previous = "0" * 64
    results = []
    for sequence, (kind, call) in enumerate((
        ("genuine_task_rehearsal", lambda: genuine_task_rehearsal(args.output)),
        ("connection_interruption_rehearsal", lambda: connection_interruption_rehearsal(args.cockroach_bin, args.output)),
    ), start=1):
        details = call()
        receipt = chained_receipt(
            campaign_id=CAMPAIGN_ID, sequence=sequence, kind=kind,
            result="PASS", details=details, previous_hash=previous,
        )
        previous = receipt["receipt_hash"]
        write_atomic(args.output / f"receipt-{sequence:02d}.json", receipt)
        results.append(receipt)
    final = {
        "version": "ck-ev0-public-canaries-v1",
        "campaign_id": CAMPAIGN_ID,
        "status": "PASS",
        "canaries": len(results),
        "final_receipt_hash": previous,
        "hidden_seed_exists": False,
        "measured_campaign_credit": False,
    }
    write_atomic(args.output / "final.json", final)
    print(json.dumps(final, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
