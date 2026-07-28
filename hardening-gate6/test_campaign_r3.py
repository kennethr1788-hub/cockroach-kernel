#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
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
    @staticmethod
    def attestation() -> dict[str, object]:
        record: dict[str, object] = {
            "version": "hardening-gate6-isolation-attestation-v1",
            "uid": 10001,
            "euid": 10001,
            "gid": 10001,
            "egid": 10001,
            "cap_eff": "0000000000000000",
            "no_new_privs": 1,
            "seccomp_mode": 2,
            "seccomp_filters": 2,
            "network_socket_probe_errno": 1,
            "network_socket_probe_result": "DENIED_EPERM",
            "exec_canary": "PASS",
            "inherited_socket_fds": [],
            "filter_spec": {"architecture": "x86_64"},
            "filter_spec_sha256": "0" * 64,
        }
        record["attestation_sha256"] = runner.base.digest(record)
        return record

    def test_attestation_binds_canonical_record_hash_not_file_hash(self):
        record = self.attestation()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory).resolve() / "attestation.json"
            path.write_bytes(runner.base.canonical(record))
            self.assertNotEqual(runner.file_hash(path),
                                record["attestation_sha256"])
            self.assertEqual(
                runner.load_attestation(path, str(record["attestation_sha256"])),
                record,
            )

    def test_attestation_rejects_noncanonical_or_wrong_claim(self):
        record = self.attestation()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory).resolve() / "attestation.json"
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")
            with self.assertRaisesRegex(runner.base.CampaignError,
                                        "ISOLATION_ATTESTATION_BINDING_INVALID"):
                runner.load_attestation(path, str(record["attestation_sha256"]))
            path.write_bytes(runner.base.canonical(record))
            with self.assertRaisesRegex(runner.base.CampaignError,
                                        "ISOLATION_ATTESTATION_BINDING_INVALID"):
                runner.load_attestation(path, "f" * 64)

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
