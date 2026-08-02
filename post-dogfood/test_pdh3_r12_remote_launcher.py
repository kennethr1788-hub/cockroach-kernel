from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_remote_launcher_tested", HERE / "pdh3_r12_remote_launcher.py"
)
assert SPEC is not None and SPEC.loader is not None
launcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def arguments(self) -> argparse.Namespace:
        root = Path("/remote/ck-r12")
        return argparse.Namespace(
            observer=root / "post-dogfood/pdh3_r12_network_observer.py",
            runner=root / "post-dogfood/pdh3_r12_remote_preflight.py",
            binary=root / "cockroach",
            packet=root / "packet.md",
            packet_sha256="a" * 64,
            tracer=root / "tracer/usr/bin/strace",
            tracer_sha256="b" * 64,
            tracer_root=root / "tracer",
            tracer_library_path=str(root / "tracer/usr/lib/x86_64-linux-gnu"),
            campaign_id="ck-pdh3-r12-preflight-r1",
            workdir=root,
            empty_home=root / "empty-home",
            output=root / "evidence",
            export_root=root / "export",
            remote_ack_root=root / "export",
            network_output=root / "network",
            runtime_parent=root / "runtime",
            pf2_runtime_parent=root / "pf2-runtime",
            setup_timeout_seconds=10_800,
            host_ack_timeout_seconds=900,
            provider_vcpus=32,
            provider_memory_gib=125,
            effective_vcpu_limit=31,
            receipt=root / "launch.json",
            log=root / "launch.log",
        )

    def test_argv_is_preflight_only_and_packet_bound(self) -> None:
        argv = launcher.launch_argv(self.arguments())
        self.assertEqual(argv[0], sys.executable)
        self.assertIn("pdh3_r12_network_observer.py", " ".join(argv))
        self.assertIn("pdh3_r12_remote_preflight.py", " ".join(argv))
        self.assertEqual(argv.count("a" * 64), 2)
        self.assertIn(str(self.arguments().tracer), argv)
        self.assertIn("b" * 64, argv)
        self.assertNotIn("86400", argv)
        self.assertNotIn("--production", argv)

    def test_exact_setup_and_host_ack_timeouts_are_bound(self) -> None:
        argv = launcher.launch_argv(self.arguments())
        self.assertEqual(argv[argv.index("--setup-timeout-seconds") + 1], "10800")
        self.assertEqual(argv[argv.index("--host-ack-timeout-seconds") + 1], "900")
        self.assertEqual(argv[argv.index("--effective-vcpu-limit") + 1], "31")

    def test_runtime_environment_is_allowlisted_and_keeps_ubuntu_sbin(self) -> None:
        environment = launcher.runtime_environment(self.arguments())
        self.assertEqual(
            set(environment),
            {"HOME", "LANG", "LC_ALL", "LD_LIBRARY_PATH", "PATH", "PDH3_PACKET_SHA256",
             "PDH3_EFFECTIVE_VCPU_LIMIT", "PDH3_PROVIDER_VCPUS",
             "PDH3_PROVIDER_MEMORY_GIB", "PYTHONDONTWRITEBYTECODE",
             "PYTHONHASHSEED", "TZ"},
        )
        self.assertEqual(
            environment["PATH"],
            "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        )
        self.assertEqual(environment["PDH3_PACKET_SHA256"], "a" * 64)
        self.assertEqual(environment["PDH3_EFFECTIVE_VCPU_LIMIT"], "31")
        self.assertEqual(environment["PDH3_PROVIDER_VCPUS"], "32")
        self.assertEqual(environment["PDH3_PROVIDER_MEMORY_GIB"], "125")
        self.assertEqual(
            environment["LD_LIBRARY_PATH"],
            self.arguments().tracer_library_path,
        )
        self.assertEqual(
            environment["LD_LIBRARY_PATH"],
            "/remote/ck-r12/tracer/usr/lib/x86_64-linux-gnu",
        )


if __name__ == "__main__":
    unittest.main()
