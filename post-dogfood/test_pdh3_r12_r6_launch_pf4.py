from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock


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
            "machine": {
                "secureCloud": True, "gpuId": "NVIDIA L40S",
                "dataCenterId": "US-MO-1",
            },
        }

    def test_official_shape_is_accepted(self) -> None:
        self.assertTrue(module.exact_shape(
            self.worker(), name="ck-pdh3-r12-preflight-r6-test-01",
            image="runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            ceiling=0.99,
        ))

    def test_32_vcpu_125_gib_shape_gets_prospective_31_cpu_cap(self) -> None:
        worker = self.worker(vcpus=32, memory=125)
        self.assertTrue(module.exact_shape(
            worker,
            name="ck-pdh3-r12-preflight-r6-test-01",
            image="runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            ceiling=0.99,
        ))
        plan = module.shape_plan(
            worker,
            name="ck-pdh3-r12-preflight-r6-test-01",
            image="runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            ceiling=0.99,
        )
        self.assertIsNotNone(plan)
        self.assertEqual(plan["effective_vcpu_limit"], 31)

    def test_shape_below_frozen_memory_minimum_is_rejected(self) -> None:
        self.assertFalse(module.exact_shape(
            self.worker(vcpus=32, memory=93),
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

    def test_frozen_datacenter_is_enforced(self) -> None:
        worker = self.worker(vcpus=32, memory=125)
        self.assertTrue(module.exact_shape(
            worker,
            name="ck-pdh3-r12-preflight-r6-test-01",
            image="runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            ceiling=0.99,
            data_center_ids=("US-MO-1",),
        ))
        worker["machine"]["dataCenterId"] = "US-NC-1"
        self.assertFalse(module.exact_shape(
            worker,
            name="ck-pdh3-r12-preflight-r6-test-01",
            image="runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            ceiling=0.99,
            data_center_ids=("US-MO-1",),
        ))

    def test_creation_argv_places_datacenter_after_subcommand(self) -> None:
        config = {
            "image": "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            "stop_utc": "2026-08-02T15:00:00Z",
            "terminate_utc": "2026-08-02T15:15:00Z",
            "data_center_ids": ["US-MO-1"],
        }
        argv = module.creation_argv(
            Path("/tmp/runpodctl"), pod_name="campaign-01", config=config
        )
        self.assertEqual(argv[:3], ["/tmp/runpodctl", "pod", "create"])
        index = argv.index("--data-center-ids")
        self.assertEqual(argv[index + 1], "US-MO-1")
        self.assertEqual(argv[-2:], ["--output", "json"])

    def test_graphql_payload_binds_minimum_cpu_and_provider_deadlines(self) -> None:
        config = {
            "image": "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            "stop_utc": "2026-08-02T15:00:00Z",
            "terminate_utc": "2026-08-02T15:15:00Z",
            "min_vcpu_count": 24,
        }
        payload = module.graphql_creation_payload(
            pod_name="campaign-01", config=config
        )
        request = payload["variables"]["input"]
        self.assertEqual(request["minVcpuCount"], 24)
        self.assertEqual(request["minMemoryInGb"], 94)
        self.assertEqual(request["stopAfter"], config["stop_utc"])
        self.assertEqual(request["terminateAfter"], config["terminate_utc"])
        self.assertEqual(request["gpuTypeId"], "NVIDIA L40S")
        self.assertNotIn("dataCenterId", request)
        self.assertNotIn("RUNPOD_API_KEY", module.canonical(payload).decode())

    def test_graphql_worker_below_requested_provider_cpu_is_rejected(self) -> None:
        worker = self.worker(vcpus=16, memory=125)
        self.assertFalse(module.exact_shape(
            worker,
            name="ck-pdh3-r12-preflight-r6-test-01",
            image="runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            ceiling=0.99,
            min_provider_vcpus=24,
        ))

    def test_graphql_create_keeps_credential_out_of_url_and_body(self) -> None:
        config = {
            "graphql_url": "https://api.runpod.io/graphql",
            "image": "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            "stop_utc": "2026-08-02T15:00:00Z",
            "terminate_utc": "2026-08-02T15:15:00Z",
            "min_vcpu_count": 24,
        }
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({
            "data": {"podFindAndDeployOnDemand": {"id": "pod-1"}}
        }).encode()

        def inspect(request, timeout):
            self.assertEqual(request.full_url, config["graphql_url"])
            self.assertNotIn("secret", request.full_url)
            self.assertNotIn(b"secret", request.data)
            self.assertEqual(request.get_header("Authorization"), "Bearer secret")
            self.assertEqual(timeout, 180)
            return response

        with mock.patch.dict(os.environ, {"RUNPOD_API_KEY": "secret"}), \
                mock.patch.object(module.urllib.request, "urlopen", side_effect=inspect):
            result = module.create_via_graphql(
                pod_name="campaign-01", config=config
            )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["id"], "pod-1")
        self.assertNotIn(b"secret", result.stdout + result.stderr)

    def test_graphql_create_without_credential_fails_closed(self) -> None:
        config = {
            "graphql_url": "https://api.runpod.io/graphql",
            "image": "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
            "stop_utc": "2026-08-02T15:00:00Z",
            "terminate_utc": "2026-08-02T15:15:00Z",
            "min_vcpu_count": 24,
        }
        with mock.patch.dict(os.environ, {}, clear=True):
            result = module.create_via_graphql(
                pod_name="campaign-01", config=config
            )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, b"GRAPHQL_CREDENTIAL_UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
