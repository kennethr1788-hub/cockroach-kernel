from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "lifecycle_guard_tested", HERE / "lifecycle_guard.py"
)
assert SPEC is not None and SPEC.loader is not None
guard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = guard
SPEC.loader.exec_module(guard)


class FakeClock:
    def __init__(self, now: float) -> None:
        self.now = now

    def time(self) -> float:
        return self.now

    def pause(self, seconds: float, _: float) -> None:
        self.now += seconds


def arguments(root: Path) -> argparse.Namespace:
    return argparse.Namespace(
        runpodctl=root / "runpodctl",
        runpodctl_sha256="a" * 64,
        pod_id="pod-123",
        pod_name="ck-pdh3-scale-r1-worker",
        campaign_prefix="ck-pdh3-scale-r1",
        stop_epoch=110,
        delete_epoch=120,
        heartbeat_seconds=10,
        command_timeout_seconds=5,
        bind_timeout_seconds=10,
        delete_grace_seconds=30,
        log=root / "guard.ndjson",
    )


def present() -> tuple[bool, dict[str, str], str]:
    value = {
        "id": "pod-123",
        "name": "ck-pdh3-scale-r1-worker",
        "desiredStatus": "RUNNING",
    }
    return True, value, '{"desiredStatus":"RUNNING"}'


class LifecycleGuardTests(unittest.TestCase):
    def test_structured_pod_404_required_for_absence(self) -> None:
        vague = subprocess.CompletedProcess([], 1, "pod not found", None)
        exact = subprocess.CompletedProcess(
            [], 1, '{"status":404,"message":"Pod not found"}', None
        )
        with mock.patch.object(guard, "run", return_value=vague):
            with self.assertRaises(guard.TransientProviderError):
                guard.pod_get(Path("/tmp/cli"), "pod", timeout_seconds=1)
        with mock.patch.object(guard, "run", return_value=exact):
            observed, value, _ = guard.pod_get(
                Path("/tmp/cli"), "pod", timeout_seconds=1
            )
        self.assertFalse(observed)
        self.assertIsNone(value)

    def test_nested_structured_pod_404_is_accepted(self) -> None:
        result = subprocess.CompletedProcess(
            [],
            1,
            '{"error":{"code":404,"detail":"Requested pod does not exist"}}',
            None,
        )
        with mock.patch.object(guard, "run", return_value=result):
            observed, value, _ = guard.pod_get(
                Path("/tmp/cli"), "pod", timeout_seconds=1
            )
        self.assertFalse(observed)
        self.assertIsNone(value)

    def test_runpodctl_v280_symbolic_code_with_numeric_status_is_accepted(self) -> None:
        result = subprocess.CompletedProcess(
            [],
            1,
            '{"error":"failed to get pod: pod not found","code":"not_found","status":404}',
            None,
        )
        with mock.patch.object(guard, "run", return_value=result):
            observed, value, _ = guard.pod_get(
                Path("/tmp/cli"), "pod", timeout_seconds=1
            )
        self.assertFalse(observed)
        self.assertIsNone(value)

    def test_symbolic_code_cannot_replace_or_override_numeric_404(self) -> None:
        outputs = (
            '{"error":"Pod not found","code":"not_found"}',
            '{"error":"Pod not found","code":"not_found","status":500}',
            '{"error":"Pod not found","code":500,"status":404}',
        )
        for stdout in outputs:
            with self.subTest(stdout=stdout):
                failed = subprocess.CompletedProcess([], 1, stdout, None)
                with mock.patch.object(guard, "run", return_value=failed):
                    with self.assertRaises(guard.TransientProviderError):
                        guard.pod_get(Path("/tmp/cli"), "pod", timeout_seconds=1)

    def test_runpodctl_v272_wrapped_pod_404_is_accepted(self) -> None:
        output = (
            '{"error":"api error: {\\"error\\":\\"pod not found\\",'
            '\\"status\\":404}\\n (status 404)"}\n'
            "Usage:\n"
            "  runpodctl pod get <pod-id> [flags]\n\n"
            "Flags:\n"
            "  -h, --help                     help for get\n"
            "      --include-machine          include machine info\n"
            "      --include-network-volume   include network volume info\n\n"
            "Global Flags:\n"
            "  -o, --output string   output format (json, yaml) (default \"json\")\n\n"
            '{"error":"failed to get pod: api error: {"error":"pod not found",'
            '"status":404}\n (status 404)"}\n'
        )
        result = subprocess.CompletedProcess([], 1, output, None)
        with mock.patch.object(guard, "run", return_value=result):
            observed, value, _ = guard.pod_get(
                Path("/tmp/cli"), "pod", timeout_seconds=1
            )
        self.assertFalse(observed)
        self.assertIsNone(value)

    def test_json_404_followed_by_unscoped_text_is_rejected(self) -> None:
        output = '{"status":404,"message":"Pod not found"}\nprovider warning\n'
        failed = subprocess.CompletedProcess([], 1, output, None)
        with mock.patch.object(guard, "run", return_value=failed):
            with self.assertRaises(guard.TransientProviderError):
                guard.pod_get(Path("/tmp/cli"), "pod", timeout_seconds=1)

    def test_arbitrary_stdout_containing_404_is_not_absence_proof(self) -> None:
        outputs = (
            "upstream request 404; retry later",
            '{"status":404}',
            '{"status":404,"message":"Billing invoice not found"}',
            '{"status":"404","message":"Pod not found"}',
            '{"status":500,"message":"Pod not found; prior request was 404"}',
        )
        for stdout in outputs:
            with self.subTest(stdout=stdout):
                failed = subprocess.CompletedProcess([], 1, stdout, None)
                with mock.patch.object(guard, "run", return_value=failed):
                    with self.assertRaises(guard.TransientProviderError):
                        guard.pod_get(Path("/tmp/cli"), "pod", timeout_seconds=1)

    def test_delete_does_not_accept_unstructured_404(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lifecycle-guard-test.") as temporary:
            root = Path(temporary)
            log = guard.ChainLog(root / "guard.ndjson")
            failed = subprocess.CompletedProcess([], 1, "random 404 text", None)
            with (
                mock.patch.object(guard, "run", return_value=failed),
                mock.patch.object(guard, "pause"),
            ):
                succeeded = guard.bounded_action(
                    Path("/tmp/cli"),
                    "delete",
                    "pod-123",
                    log,
                    command_timeout_seconds=1,
                    deadline_epoch=guard.time.time() + 60,
                )
        self.assertFalse(succeeded)

    def test_delete_accepts_structured_pod_404(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lifecycle-guard-test.") as temporary:
            root = Path(temporary)
            log = guard.ChainLog(root / "guard.ndjson")
            absent = subprocess.CompletedProcess(
                [], 1, '{"statusCode":404,"message":"Pod not found"}', None
            )
            with mock.patch.object(guard, "run", return_value=absent):
                succeeded = guard.bounded_action(
                    Path("/tmp/cli"),
                    "delete",
                    "pod-123",
                    log,
                    command_timeout_seconds=1,
                    deadline_epoch=guard.time.time() + 60,
                )
        self.assertTrue(succeeded)

    def test_provider_timeout_is_transient(self) -> None:
        with mock.patch.object(
            guard.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["runpodctl"], 1),
        ):
            with self.assertRaises(guard.TransientProviderError):
                guard.run(["runpodctl"], timeout_seconds=1)

    def test_failed_action_is_retryable_not_fatal(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lifecycle-guard-test.") as temporary:
            root = Path(temporary)
            log = guard.ChainLog(root / "guard.ndjson")
            failed = subprocess.CompletedProcess([], 1, "provider unavailable", None)
            with (
                mock.patch.object(guard, "run", return_value=failed),
                mock.patch.object(guard, "pause"),
            ):
                succeeded = guard.bounded_action(
                    Path("/tmp/cli"),
                    "stop",
                    "pod-123",
                    log,
                    command_timeout_seconds=1,
                    deadline_epoch=guard.time.time() + 60,
                )
            self.assertFalse(succeeded)

    def test_transient_get_and_failed_stop_do_not_suppress_delete(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lifecycle-guard-test.") as temporary:
            root = Path(temporary)
            args = arguments(root)
            log = guard.ChainLog(args.log)
            clock = FakeClock(100)
            sequence: list[object] = [
                present(),
                guard.TransientProviderError("TEMPORARY_GET_FAILURE"),
                present(),
                present(),
                (False, None, '{"status":404,"message":"Pod not found"}'),
            ]

            def next_get(*_: object, **__: object) -> object:
                value = sequence.pop(0)
                if isinstance(value, Exception):
                    raise value
                return value

            actions: list[str] = []

            def action(*call_args: object, **_: object) -> bool:
                actions.append(str(call_args[1]))
                return len(actions) > 1

            with (
                mock.patch.object(guard, "verify_cli"),
                mock.patch.object(guard, "pod_get", side_effect=next_get),
                mock.patch.object(guard, "campaign_active", return_value=[]),
                mock.patch.object(guard, "bounded_action", side_effect=action),
                mock.patch.object(guard.time, "time", side_effect=clock.time),
                mock.patch.object(guard, "pause", side_effect=clock.pause),
            ):
                exit_code = guard.guard_loop(args, args.runpodctl, log)
            self.assertEqual(exit_code, 0)
            self.assertEqual(actions, ["stop", "delete"])
            events = [
                __import__("json").loads(line)["event"]
                for line in args.log.read_text().splitlines()
            ]
            self.assertIn("PROVIDER_RETRY", events)
            self.assertEqual(events[-1], "TEARDOWN_GREEN")

    def test_transient_list_retries_until_absence_is_proven(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lifecycle-guard-test.") as temporary:
            root = Path(temporary)
            args = arguments(root)
            log = guard.ChainLog(args.log)
            clock = FakeClock(100)
            get_sequence = [
                present(),
                (False, None, '{"status":404,"message":"Pod not found"}'),
                (False, None, '{"status":404,"message":"Pod not found"}'),
            ]
            list_sequence: list[object] = [
                guard.TransientProviderError("TEMPORARY_LIST_FAILURE"),
                [],
            ]

            def next_list(*_: object, **__: object) -> object:
                value = list_sequence.pop(0)
                if isinstance(value, Exception):
                    raise value
                return value

            with (
                mock.patch.object(guard, "verify_cli"),
                mock.patch.object(guard, "pod_get", side_effect=get_sequence),
                mock.patch.object(guard, "campaign_active", side_effect=next_list),
                mock.patch.object(guard.time, "time", side_effect=clock.time),
                mock.patch.object(guard, "pause", side_effect=clock.pause),
            ):
                exit_code = guard.guard_loop(args, args.runpodctl, log)
            self.assertEqual(exit_code, 0)
            events = [
                __import__("json").loads(line)["event"]
                for line in args.log.read_text().splitlines()
            ]
            self.assertIn("PROVIDER_RETRY", events)
            self.assertEqual(events[-1], "TEARDOWN_GREEN")

    def test_persistent_transient_failure_blocks_at_deadline(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lifecycle-guard-test.") as temporary:
            root = Path(temporary)
            args = arguments(root)
            args.delete_grace_seconds = 10
            log = guard.ChainLog(args.log)
            clock = FakeClock(100)
            sequence = [present()]

            def next_get(*_: object, **__: object) -> object:
                if sequence:
                    return sequence.pop(0)
                raise guard.TransientProviderError("PROVIDER_DOWN")

            with (
                mock.patch.object(guard, "verify_cli"),
                mock.patch.object(guard, "pod_get", side_effect=next_get),
                mock.patch.object(guard, "bounded_action", return_value=False),
                mock.patch.object(guard.time, "time", side_effect=clock.time),
                mock.patch.object(guard, "pause", side_effect=clock.pause),
            ):
                with self.assertRaisesRegex(guard.GuardFailure, "GUARD_DEADLINE_EXCEEDED"):
                    guard.guard_loop(args, args.runpodctl, log)


if __name__ == "__main__":
    unittest.main()
