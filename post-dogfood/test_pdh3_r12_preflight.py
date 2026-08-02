from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_preflight_tested", HERE / "pdh3_r12_preflight.py"
)
assert SPEC is not None and SPEC.loader is not None
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


class Contract:
    MEASURED_SECONDS = 86_400
    CHECKPOINT_SECONDS = 300
    REQUIRED_CHECKPOINTS = 288
    QUERY_DURATION_SECONDS = 120
    TASKS = 500_000
    EVENTS_PER_TASK = 10
    RECEIPTS_PER_TASK = 2
    VECTORS = 250_000
    VERIFIER_EXECUTIONS = 9_976
    MAX_CONCURRENCY = 500
    P99_LIMIT_MS = 5_000.0
    PMAX_LIMIT_MS = 10_000.0
    TRACE_BYTES_LIMIT = 2 * 1024**3


class R12PreflightTests(unittest.TestCase):
    def test_contract_drift_fails_closed(self) -> None:
        self.assertEqual(
            preflight.validate_contract(Contract()), preflight.EXPECTED_CONTRACT
        )
        changed = copy.copy(Contract())
        changed.MAX_CONCURRENCY = 499
        with self.assertRaisesRegex(preflight.PreflightError, "CONTRACT_DRIFT"):
            preflight.validate_contract(changed)

    def test_relative_path_validation(self) -> None:
        for value in ("/absolute", "../escape", "a/../b", "a\\b", "x\x00y"):
            with self.subTest(value=value):
                with self.assertRaises(preflight.PreflightError):
                    preflight.validate_relative(value)
        preflight.validate_relative("post-dogfood/file.py")

    def test_canonical_record_roundtrip_and_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "receipt.json"
            body = {"version": "test", "branch": "GREEN"}
            value = {**body, "receipt_sha256": preflight.digest(body)}
            preflight.write_record(path, value)
            self.assertEqual(
                preflight.verify_record(path, "receipt_sha256"), value
            )
            broken = dict(value)
            broken["branch"] = "BLOCKED"
            path.write_bytes(preflight.canonical(broken))
            with self.assertRaisesRegex(preflight.PreflightError, "HASH_INVALID"):
                preflight.verify_record(path, "receipt_sha256")

    def test_resource_boundary_is_green_without_target_attempt(self) -> None:
        usage = type("Usage", (), {"total": 100, "used": 95, "free": 5})()
        with mock.patch.object(
            preflight, "host_memory_bytes", return_value=18 * 1024**3
        ), mock.patch.object(
            preflight.shutil, "disk_usage", return_value=usage
        ), mock.patch.object(
            preflight.os, "cpu_count", return_value=11
        ):
            value = preflight.resource_receipt(Path("/tmp"))
        self.assertEqual(value["branch"], "PF3_LOCAL_RESOURCE_BOUNDARY_GREEN")
        self.assertFalse(value["full_cardinality_attempted"])
        self.assertFalse(value["reduced_scale_treated_as_equivalent"])
        self.assertEqual(value["first_mandatory_full_cardinality_stage"], "PF-5")

    def test_record_is_canonical(self) -> None:
        value = {"b": 2, "a": 1}
        self.assertEqual(preflight.canonical(value), b'{"a":1,"b":2}')


if __name__ == "__main__":
    unittest.main()
