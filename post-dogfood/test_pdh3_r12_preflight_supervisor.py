from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_preflight_supervisor_tested",
    HERE / "pdh3_r12_preflight_supervisor.py",
)
assert SPEC is not None and SPEC.loader is not None
supervisor = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = supervisor
SPEC.loader.exec_module(supervisor)


class SupervisorTests(unittest.TestCase):
    def test_terminal_matrix_is_mutually_exclusive(self) -> None:
        base = dict(
            teardown_proven=True,
            observer_alive=True,
            workload_alive=False,
            terminal_result_present=True,
            archive_present=True,
            archive_complete=True,
            archive_valid=True,
            semantic_green=True,
        )
        cases = [
            ({}, supervisor.GREEN_PENDING_FINAL_GATE),
            ({"semantic_green": False}, supervisor.SEMANTIC_FAILURE),
            ({"terminal_result_present": False}, supervisor.ABSENT_RESULT),
            ({"archive_present": False}, supervisor.PARTIAL_ARCHIVE),
            ({"archive_complete": False}, supervisor.PARTIAL_ARCHIVE),
            ({"archive_valid": False}, supervisor.CORRUPT_ARCHIVE),
            ({"transport_failed": True}, supervisor.TRANSPORT_FAILURE),
            (
                {"observer_alive": False, "terminal_result_present": False},
                supervisor.OBSERVER_LOSS,
            ),
            ({"deadline_exceeded": True}, supervisor.DEADLINE_EXCEEDED),
            ({"teardown_proven": False}, supervisor.TEARDOWN_UNPROVEN),
        ]
        for changes, expected in cases:
            with self.subTest(expected=expected):
                value = supervisor.TerminalObservation(**{**base, **changes})
                self.assertEqual(supervisor.classify_terminal(value), expected)
                self.assertEqual(supervisor.EXIT_CODES[expected] == 0, expected == supervisor.GREEN_PENDING_FINAL_GATE)

    def test_pull_latest_verifies_chain_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            remote = root / "remote"
            local = root / "local"
            source.mkdir()
            (source / "a").write_bytes(b"evidence")
            manifest = supervisor.checkpoint.publish(
                source_root=source,
                export_root=remote,
                sequence=1,
                previous_manifest_sha256=supervisor.checkpoint.ZERO_HASH,
                packet_sha256="a" * 64,
                files=["a"],
            )
            del manifest

            def fake_scp(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                remote_name = command[-2].rsplit("/", 1)[-1]
                shutil.copyfile(remote / remote_name, Path(command[-1]))
                return subprocess.CompletedProcess(command, 0, "", "")

            config = supervisor.PullConfig(
                ssh_config=root / "ssh-config",
                ssh_alias="worker",
                remote_export_root="/remote/export",
                local_root=local,
                packet_sha256="a" * 64,
                deadline_epoch=time.time() + 3600,
            )
            first = supervisor.pull_latest(
                config, runner=fake_scp, acknowledged_utc="2026-08-02T00:00:00Z"
            )
            self.assertIsNotNone(first)
            self.assertIsNone(supervisor.pull_latest(config, runner=fake_scp))

    def test_sequence_gap_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            remote = root / "remote"
            source.mkdir()
            (source / "a").write_bytes(b"x")
            supervisor.checkpoint.publish(
                source_root=source,
                export_root=remote,
                sequence=2,
                previous_manifest_sha256="b" * 64,
                packet_sha256="a" * 64,
                files=["a"],
            )

            def fake_scp(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                remote_name = command[-2].rsplit("/", 1)[-1]
                shutil.copyfile(remote / remote_name, Path(command[-1]))
                return subprocess.CompletedProcess(command, 0, "", "")

            config = supervisor.PullConfig(
                ssh_config=root / "ssh-config",
                ssh_alias="worker",
                remote_export_root="/remote/export",
                local_root=root / "local",
                packet_sha256="a" * 64,
                deadline_epoch=time.time() + 3600,
            )
            with self.assertRaisesRegex(supervisor.SupervisorError, "SEQUENCE_GAP"):
                supervisor.pull_latest(config, runner=fake_scp)

    def test_push_remote_ack_is_packet_and_manifest_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            local = root / "local"
            local.mkdir()
            calls: list[list[str]] = []

            def fake_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                calls.append(command)
                return subprocess.CompletedProcess(command, 0, "", "")

            config = supervisor.PullConfig(
                ssh_config=root / "ssh-config",
                ssh_alias="worker",
                remote_export_root="/remote/export",
                local_root=local,
                packet_sha256="a" * 64,
                deadline_epoch=time.time() + 3600,
            )
            pulled = {
                "manifest": {"sequence": 4, "manifest_sha256": "b" * 64},
                "ack": {"ack_sha256": "c" * 64},
            }
            receipt = supervisor.push_remote_ack(config, pulled, runner=fake_runner)
            self.assertTrue(receipt["verified"])
            self.assertEqual(receipt["packet_sha256"], "a" * 64)
            self.assertEqual(receipt["manifest_sha256"], "b" * 64)
            self.assertEqual([call[0] for call in calls], ["scp", "ssh"])


if __name__ == "__main__":
    unittest.main()
