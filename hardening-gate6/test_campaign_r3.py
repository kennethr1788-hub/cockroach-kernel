#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


manifest_module = load("gate6_manifest_r3", ROOT / "make_manifest_r3.py")
runner = load("gate6_runner_r3", ROOT / "run_campaign_r3.py")
launcher = load("gate6_seccomp", ROOT / "seccomp_exec.py")


class Gate6R3Tests(unittest.TestCase):
    def test_manifest_is_exactly_54_r3_rows(self):
        manifest = manifest_module.build()
        rows = runner.validate_manifest_r3(manifest)
        self.assertEqual(manifest["execution_revision"], "R3")
        self.assertEqual(len(rows), 54)

    def test_manifest_revision_tamper_fails(self):
        manifest = manifest_module.build()
        manifest["execution_revision"] = "R2"
        with self.assertRaisesRegex(runner.base.CampaignError,
                                    "MANIFEST_REVISION_INVALID"):
            runner.validate_manifest_r3(manifest)

    def test_filter_denies_all_declared_network_paths(self):
        required = {
            "socket", "connect", "accept", "sendto", "recvfrom",
            "sendmsg", "recvmsg", "socketpair", "accept4", "recvmmsg",
            "sendmmsg", "io_uring_setup", "bpf", "pidfd_getfd",
        }
        self.assertTrue(required.issubset(launcher.DENIED_SYSCALLS))
        filters, program = launcher.build_filter()
        self.assertEqual(program.length, 7 + 2 * len(set(
            launcher.DENIED_SYSCALLS.values())))
        self.assertEqual(len(filters), program.length)

    def test_foreign_arch_is_killed_and_default_allows(self):
        filters, _ = launcher.build_filter()
        self.assertEqual(filters[2].k, launcher.SECCOMP_RET_KILL_PROCESS)
        self.assertEqual(filters[4].k, launcher.X32_SYSCALL_BIT)
        self.assertEqual(filters[5].k, launcher.SECCOMP_RET_KILL_PROCESS)
        self.assertEqual(filters[-1].k, launcher.SECCOMP_RET_ALLOW)


if __name__ == "__main__":
    unittest.main()
