from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_remote_capability_tested", HERE / "pdh3_r12_remote_capability.py"
)
assert SPEC is not None and SPEC.loader is not None
capability = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capability)


class CapabilityTests(unittest.TestCase):
    def test_thresholds_are_fixed_and_resource_sufficient(self) -> None:
        values = capability.thresholds()
        self.assertEqual(values["min_vcpus"], 16)
        self.assertEqual(values["min_ram_bytes"], 64 * 1024**3)
        self.assertEqual(values["sustained_bytes"], 8 * 1024**3)
        self.assertEqual(values["max_fsync_p99_ms"], 50.0)

    def test_percentile_uses_nearest_rank(self) -> None:
        self.assertEqual(capability.percentile([1.0, 2.0, 3.0, 4.0], 0.99), 4.0)
        self.assertEqual(capability.percentile([4.0, 1.0, 3.0, 2.0], 0.50), 2.0)

    def test_atomic_write_is_canonical_and_exclusive_temp(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "receipt.json"
            raw = capability.canonical({"b": 2, "a": 1})
            capability.atomic_write(path, raw)
            self.assertEqual(path.read_bytes(), b'{"a":1,"b":2}')
            self.assertFalse((path.parent / ".receipt.json.part").exists())

    def test_invalid_percentile_is_rejected(self) -> None:
        with self.assertRaises(capability.CapabilityError):
            capability.percentile([], 0.99)
        with self.assertRaises(capability.CapabilityError):
            capability.percentile([1.0], 0.0)


if __name__ == "__main__":
    unittest.main()
