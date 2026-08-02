from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


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

    def test_command_receipt_persists_exact_observer_streams(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            stdout = root / "observer.stdout"
            stderr = root / "observer.stderr"
            receipt = capability.command_receipt(
                [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr)"],
                stdout_path=stdout,
                stderr_path=stderr,
            )
            self.assertEqual(stdout.read_bytes(), b"out\n")
            self.assertEqual(stderr.read_bytes(), b"err\n")
            self.assertEqual(receipt["stdout_sha256"], capability.digest(b"out\n"))
            self.assertEqual(receipt["stderr_sha256"], capability.digest(b"err\n"))

    def test_cpuset_parser_counts_ranges_without_host_leakage(self) -> None:
        self.assertEqual(capability.parse_cpuset("0-3,8,10-11\n"), 7)
        with self.assertRaisesRegex(capability.CapabilityError, "CPUSET_INVALID"):
            capability.parse_cpuset("4-2")

    def test_effective_resources_bind_provider_and_cgroup_limits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "cpuset.cpus.effective").write_text("0-31\n")
            (root / "cpu.max").write_text("1600000 100000\n")
            (root / "memory.max").write_text(str(96 * 1024**3) + "\n")
            with (
                mock.patch.object(
                    capability.os,
                    "sched_getaffinity",
                    return_value=set(range(64)),
                    create=True,
                ),
                mock.patch.object(capability.os, "cpu_count", return_value=256),
                mock.patch.object(capability, "memory_total_bytes", return_value=1024 * 1024**3),
            ):
                values = capability.effective_resources(32, 125, root)
        self.assertEqual(values["effective_vcpus"], 16)
        self.assertEqual(values["effective_memory_bytes"], 96 * 1024**3)
        self.assertEqual(values["cpu"]["host_logical"], 256)

    def test_provider_allocation_remains_a_hard_upper_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "cpu.max").write_text("max 100000\n")
            (root / "memory.max").write_text("max\n")
            with (
                mock.patch.object(
                    capability.os,
                    "sched_getaffinity",
                    return_value=set(range(256)),
                    create=True,
                ),
                mock.patch.object(capability.os, "cpu_count", return_value=256),
                mock.patch.object(capability, "memory_total_bytes", return_value=1024 * 1024**3),
            ):
                values = capability.effective_resources(16, 125, root)
        self.assertEqual(values["effective_vcpus"], 16)
        self.assertEqual(values["effective_memory_bytes"], 125 * 1024**3)

    def test_effective_cpu_cap_preserves_four_gib_per_vcpu(self) -> None:
        plan = capability.cpu_affinity.effective_vcpu_plan(32, 125)
        self.assertEqual(plan["effective_vcpu_limit"], 31)
        self.assertTrue(plan["ratio_preserved"])

    def test_resource_accounting_prefers_complete_cgroup_v2(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            proc = root / "proc"
            cgroup = root / "cgroup"
            cgroup.mkdir()
            for name in ("cpu.stat", "memory.current", "memory.events", "io.stat", "pids.current"):
                (cgroup / name).write_text("0\n")
            values = capability.resource_accounting_backend(cgroup, proc)
        self.assertEqual(values["backend"], "CGROUP_V2")
        self.assertTrue(values["cgroup_isolation_observed"])

    def test_resource_accounting_accepts_complete_cgroup_v1(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            proc = root / "proc"
            cgroup = root / "cgroup"
            for relative in (
                "cpuacct/cpuacct.usage",
                "memory/memory.usage_in_bytes",
                "memory/memory.limit_in_bytes",
                "blkio/blkio.throttle.io_service_bytes",
                "pids/pids.current",
            ):
                path = cgroup / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("0\n")
            values = capability.resource_accounting_backend(cgroup, proc)
        self.assertEqual(values["backend"], "CGROUP_V1")
        self.assertTrue(values["cgroup_isolation_observed"])

    def test_resource_accounting_uses_declared_procfs_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            proc = root / "proc"
            cgroup = root / "cgroup"
            cgroup.mkdir()
            for relative in ("self/status", "self/io", "stat", "meminfo", "net/dev"):
                path = proc / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("0\n")
            with mock.patch.object(
                capability.os, "sched_getaffinity", return_value={0}, create=True
            ):
                values = capability.resource_accounting_backend(cgroup, proc)
        self.assertEqual(values["backend"], "PROCFS_PROCESS_TREE_PROVIDER_BOUND")
        self.assertFalse(values["cgroup_isolation_observed"])
        self.assertEqual(values["scope"], "PROCESS_TREE_PLUS_PROVIDER_ALLOCATION")


if __name__ == "__main__":
    unittest.main()
