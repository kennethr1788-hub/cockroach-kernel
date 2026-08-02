from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_lifecycle_launch_tested", HERE / "pdh3_r12_lifecycle_launch.py"
)
assert SPEC is not None and SPEC.loader is not None
launch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launch)


def record(sequence: int, previous: str, event: str, details: object) -> dict[str, object]:
    core = {
        "schema_version": "s2-guard-v1",
        "sequence": sequence,
        "utc": "2026-08-02T00:00:00Z",
        "monotonic_seconds": float(sequence),
        "previous_hash": previous,
        "event": event,
        "details": details,
    }
    return {**core, "event_hash": hashlib.sha256(launch.canonical(core)).hexdigest()}


class LifecycleLaunchTests(unittest.TestCase):
    def test_environment_passes_only_local_guard_credential_and_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            environment = launch.guard_environment(
                Path(temporary) / "home",
                {"RUNPOD_API_KEY": "secret", "OTHER_SECRET": "no", "HOME": "/real"},
            )
        self.assertEqual(environment["RUNPOD_API_KEY"], "secret")
        self.assertNotIn("OTHER_SECRET", environment)
        self.assertNotEqual(environment["HOME"], "/real")

    def test_missing_guard_credential_fails_before_fork(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                launch.LifecycleLaunchError, "RUNPOD_API_KEY_UNAVAILABLE"
            ):
                launch.guard_environment(Path(temporary) / "home", {})

    def test_wait_requires_hash_valid_identity_bound_event(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "guard.ndjson"
            bound = record(
                1,
                "0" * 64,
                "BOUND",
                {"pod_id": "pod", "name": "campaign-01", "campaign_prefix": "campaign"},
            )
            path.write_text(json.dumps(bound, sort_keys=True, separators=(",", ":")) + "\n")
            with mock.patch.object(launch.os, "kill"):
                observed = launch.wait_for_bound(
                    log=path,
                    pid=123,
                    pod_id="pod",
                    pod_name="campaign-01",
                    campaign_prefix="campaign",
                    timeout_seconds=1,
                )
        self.assertEqual(observed["event"], "BOUND")

    def test_blocked_event_is_not_accepted_as_startup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "guard.ndjson"
            blocked = record(1, "0" * 64, "GUARD_BLOCKED", {"error": "x"})
            path.write_text(json.dumps(blocked, sort_keys=True, separators=(",", ":")) + "\n")
            with (
                mock.patch.object(launch.os, "kill"),
                self.assertRaisesRegex(launch.LifecycleLaunchError, "GUARD_REPORTED_BLOCKED"),
            ):
                launch.wait_for_bound(
                    log=path,
                    pid=123,
                    pod_id="pod",
                    pod_name="campaign-01",
                    campaign_prefix="campaign",
                    timeout_seconds=1,
                )

    def test_chain_tamper_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "guard.ndjson"
            bound = record(1, "0" * 64, "BOUND", {})
            bound["event_hash"] = "f" * 64
            path.write_text(json.dumps(bound) + "\n")
            with self.assertRaisesRegex(
                launch.LifecycleLaunchError, "GUARD_CHAIN_EVENT_HASH_INVALID"
            ):
                launch.read_chain(path)


if __name__ == "__main__":
    unittest.main()
