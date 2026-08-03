from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest import mock


BASE = Path(__file__).resolve().parents[1]
MODULE = BASE / "post-dogfood/pdh3_r12_remote_preflight.py"
sys.path.insert(0, str(MODULE.parent))
SPEC = importlib.util.spec_from_file_location("pdh3_r12_remote_preflight_tested", MODULE)
assert SPEC is not None and SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


class R12RemotePreflightTests(unittest.TestCase):
    def test_named_family_partition_is_exact(self) -> None:
        names = [name for family in runner.NAMED_FAMILIES.values() for name in family]
        self.assertEqual(len(names), 27)
        self.assertEqual(len(set(names)), 27)

    def test_gateway_aggregate_preserves_literal_c500(self) -> None:
        rows = []
        for concurrency in runner.GATEWAY_ALLOCATION:
            rows.append(
                {
                    "concurrency": concurrency,
                    "summary": {
                        "operations": 100,
                        "errors": 0,
                        "latency_ms": {"p99": 10.0, "max": 20.0},
                    },
                }
            )
        value = runner.aggregate_gateway(rows)
        self.assertTrue(value["green"])
        self.assertEqual(value["logical_workers"], 500)

    def test_gateway_aggregate_fails_latency(self) -> None:
        rows = []
        for index, concurrency in enumerate(runner.GATEWAY_ALLOCATION):
            rows.append(
                {
                    "concurrency": concurrency,
                    "summary": {
                        "operations": 100,
                        "errors": 0,
                        "latency_ms": {
                            "p99": 6000.0 if index == 1 else 10.0,
                            "max": 7000.0,
                        },
                    },
                }
            )
        self.assertFalse(runner.aggregate_gateway(rows)["green"])

    def test_growth_projection_uses_observed_delta(self) -> None:
        value = runner.growth_projection(
            [
                {"database": 100, "evidence": 10, "network": 1},
                {"database": 200, "evidence": 30, "network": 3},
            ],
            100.0,
        )
        self.assertGreater(value["projected_24h"]["database"], 200)
        self.assertGreater(value["projected_24h"]["network"], 3)

    def test_resource_accounting_retries_transient_file_race(self) -> None:
        backend = {
            "available": True,
            "backend": "PROCFS_PROCESS_TREE_PROVIDER_BOUND",
            "files": {"cpu": "/proc/fake/cpu.stat"},
        }
        with mock.patch.object(
            runner.remote_capability,
            "resource_accounting_backend",
            return_value=backend,
        ), mock.patch.object(
            runner,
            "read_small",
            side_effect=[OSError("vanished"), b"usage 1\n"],
        ) as read:
            value = runner.resource_accounting_snapshot()
        self.assertEqual(value["values"]["cpu"]["read_attempts"], 2)
        self.assertEqual(read.call_count, 2)

    def test_resource_accounting_persistent_failure_is_fatal(self) -> None:
        backend = {"available": True, "backend": "PROC", "files": {"cpu": "/proc/fake/cpu"}}
        with mock.patch.object(
            runner.remote_capability, "resource_accounting_backend", return_value=backend
        ), mock.patch.object(runner, "read_small", side_effect=OSError("gone")):
            with self.assertRaisesRegex(runner.R12RemoteError, "RESOURCE_ACCOUNTING_READ_FAILED"):
                runner.resource_accounting_snapshot()

    def test_node_affinity_proof_covers_every_live_node(self) -> None:
        nodes = [
            SimpleNamespace(
                index=index,
                process=SimpleNamespace(pid=100 + index, poll=lambda: None),
            )
            for index in range(3)
        ]
        with mock.patch.object(
            runner.cpu_affinity,
            "verify_current_affinity",
            side_effect=lambda expected, pid: {
                "expected": expected,
                "pid": pid,
                "exact": True,
                "receipt_sha256": "a" * 64,
            },
        ):
            receipt = runner.verify_node_affinities(nodes, 31)
        self.assertTrue(receipt["exact"])
        self.assertEqual([row["affinity"]["pid"] for row in receipt["nodes"]], [100, 101, 102])

    def test_node_affinity_proof_rejects_dead_node(self) -> None:
        nodes = [
            SimpleNamespace(
                index=0,
                process=SimpleNamespace(pid=100, poll=lambda: 1),
            )
        ]
        with self.assertRaisesRegex(runner.R12RemoteError, "COCKROACH_NODE_NOT_ALIVE"):
            runner.verify_node_affinities(nodes, 31)


if __name__ == "__main__":
    unittest.main()
