from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "host_supervisor_tested", HERE / "pdh3_r12_r6_host_supervisor.py"
)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class HostSupervisorTests(unittest.TestCase):
    def config(self, root: Path) -> dict[str, object]:
        return {
            "runtime": str(root / "runtime"),
            "campaign_id": "ck-pdh3-r12-preflight-r6-test",
            "packet_sha256": "a" * 64,
            "_config_path": root / "config.json",
            "terminate_utc": "2099-01-01T00:00:00Z",
        }

    def test_session_name_is_bounded_and_safe(self) -> None:
        value = module.session_name(
            "ck-pdh3-r12-preflight-r6-test/with spaces/and-$symbols"
        )
        self.assertRegex(value, r"^ck-r6-host-[A-Za-z0-9_.-]+$")
        self.assertLessEqual(len(value), 80)

    def test_start_records_hash_bound_detached_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = root / "runtime"
            runtime.mkdir()
            config = self.config(root)
            calls: list[list[str]] = []

            def fake_run(argv, **kwargs):
                calls.append(argv)
                return mock.Mock(returncode=0, stdout=b"", stderr=b"")

            with mock.patch.object(module, "screen_alive", return_value=True), \
                 mock.patch.object(module.subprocess, "run", side_effect=fake_run):
                self.assertEqual(module.start(config), 0)
            receipt = json.loads((runtime / "HOST_SUPERVISOR_LAUNCH.json").read_bytes())
            self.assertEqual(receipt["packet_sha256"], "a" * 64)
            self.assertEqual(receipt["session"], module.session_name(config["campaign_id"]))
            self.assertTrue(receipt["command_sha256"])
            self.assertIn("/usr/bin/screen", calls[0])
            self.assertIn("/usr/bin/caffeinate", calls[0])

    def test_start_waits_for_delayed_screen_registration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = root / "runtime"
            runtime.mkdir()
            config = self.config(root)
            calls: list[list[str]] = []
            alive = iter((False, False, True))

            def fake_run(argv, **kwargs):
                calls.append(argv)
                return mock.Mock(returncode=0, stdout=b"", stderr=b"")

            with mock.patch.object(module, "screen_alive",
                                   side_effect=lambda _name: next(alive)), \
                 mock.patch.object(module.time, "sleep") as sleep, \
                 mock.patch.object(module.subprocess, "run", side_effect=fake_run):
                self.assertEqual(module.start(config), 0)
            self.assertEqual(len(calls), 1)
            self.assertEqual(sleep.call_count, 2)
            self.assertTrue((runtime / "HOST_SUPERVISOR_LAUNCH.json").is_file())

    def test_status_reads_terminal_without_relaunch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = root / "runtime"
            runtime.mkdir()
            config = self.config(root)
            terminal = {
                "status": "BLOCKED",
                "pod_id": "pod-1",
                "measured_24h_started": False,
            }
            (runtime / "PF8_HOST_TERMINAL.json").write_text(json.dumps(terminal))
            with mock.patch.object(module, "screen_alive") as alive:
                self.assertEqual(module.status(config), 1)
                alive.assert_not_called()


if __name__ == "__main__":
    unittest.main()
