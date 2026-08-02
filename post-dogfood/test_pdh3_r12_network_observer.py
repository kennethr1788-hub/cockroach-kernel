from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_network_observer_tested", HERE / "pdh3_r12_network_observer.py"
)
assert SPEC is not None and SPEC.loader is not None
observer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(observer)


class NetworkObserverTests(unittest.TestCase):
    def test_net_dev_parser(self) -> None:
        raw = """Inter-| Receive | Transmit
 face |bytes packets errs drop fifo frame compressed multicast|bytes packets errs drop fifo colls carrier compressed
    lo: 10 2 0 0 0 0 0 0 20 3 0 0 0 0 0 0
"""
        self.assertEqual(
            observer.parse_net_dev(raw),
            {
                "lo": {
                    "rx_bytes": 10,
                    "rx_packets": 2,
                    "rx_errors": 0,
                    "rx_drops": 0,
                    "tx_bytes": 20,
                    "tx_packets": 3,
                    "tx_errors": 0,
                    "tx_drops": 0,
                }
            },
        )

    def test_interface_parsers(self) -> None:
        ipv4 = "Iface Destination Gateway Flags RefCnt Use Metric Mask MTU Window IRTT\nlo 0000007F 00000000 0001 0 0 0 000000FF 0 0 0\n"
        ipv6 = "0" * 96 + " 01 80 10 80 lo\n"
        self.assertEqual(observer.route_interfaces(ipv4), ["lo"])
        self.assertEqual(observer.ipv6_route_interfaces(ipv6), ["lo"])

    def test_chain_is_hash_linked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "chain.ndjson"
            chain = observer.ChainWriter(path)
            first = chain.emit("ONE", {"value": 1})
            second = chain.emit("TWO", {"value": 2})
            self.assertEqual(first["previous_hash"], observer.ZERO_HASH)
            self.assertEqual(second["previous_hash"], first["sample_sha256"])
            self.assertEqual(chain.previous_hash, second["sample_sha256"])

    def test_exact_unshare_command_has_required_namespaces(self) -> None:
        command = observer.exact_unshare_command(
            script=Path("/tmp/observer.py"),
            mode="_probe",
            forwarded=["--output", "/tmp/x"],
            unshare=Path("/usr/bin/unshare"),
        )
        for flag in ("--user", "--map-root-user", "--net", "--pid", "--fork", "--mount-proc"):
            self.assertIn(flag, command)

    def test_packet_hash_rejected(self) -> None:
        with self.assertRaisesRegex(observer.ObserverError, "PACKET_SHA256_INVALID"):
            observer.validate_packet_sha256("not-a-hash")


if __name__ == "__main__":
    unittest.main()
