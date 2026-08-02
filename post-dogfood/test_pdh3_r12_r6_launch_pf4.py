from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_r6_launch_tested", HERE / "pdh3_r12_r6_launch_pf4.py"
)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class R6LaunchTests(unittest.TestCase):
    def worker(self, *, vcpus: int = 16, memory: int = 94) -> dict[str, object]:
        return {
            "id": "pod-1", "name": "ck-pdh3-r12-preflight-r6-test-01",
            "gpuCount": 1,
            "imageName": "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            "containerDiskInGb": 250, "volumeInGb": 0, "costPerHr": 0.99,
            "vcpuCount": vcpus, "memoryInGb": memory,
            "machine": {"secureCloud": True, "gpuId": "NVIDIA L40S"},
        }

    def test_official_shape_is_accepted(self) -> None:
        self.assertTrue(module.exact_shape(
            self.worker(), name="ck-pdh3-r12-preflight-r6-test-01",
            image="runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            ceiling=0.99,
        ))

    def test_r5_shape_is_rejected_without_relabeling_cpu(self) -> None:
        self.assertFalse(module.exact_shape(
            self.worker(vcpus=32, memory=125),
            name="ck-pdh3-r12-preflight-r6-test-01",
            image="runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            ceiling=0.99,
        ))

    def test_nonzero_volume_and_rate_drift_are_rejected(self) -> None:
        worker = self.worker()
        worker["volumeInGb"] = 1
        worker["costPerHr"] = 1.00
        self.assertFalse(module.exact_shape(
            worker, name="ck-pdh3-r12-preflight-r6-test-01",
            image="runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            ceiling=0.99,
        ))


if __name__ == "__main__":
    unittest.main()
