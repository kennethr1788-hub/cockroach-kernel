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
    def test_net_dev_parser_and_counter_delta(self) -> None:
        raw = """Inter-| Receive | Transmit
 face |bytes packets errs drop fifo frame compressed multicast|bytes packets errs drop fifo colls carrier compressed
    lo: 10 2 0 0 0 0 0 0 20 3 0 0 0 0 0 0
"""
        first = observer.parse_net_dev(raw)
        last = {"lo": {**first["lo"], "rx_bytes": 15, "tx_packets": 5}}
        delta, continuous = observer.counter_delta(first, last)
        self.assertTrue(continuous)
        self.assertEqual(delta["lo"]["rx_bytes"], 5)
        self.assertEqual(delta["lo"]["tx_packets"], 2)

    def test_counter_discontinuity_is_detected(self) -> None:
        first = {"lo": {"rx_bytes": 10}}
        last = {"lo": {"rx_bytes": 9}}
        _, continuous = observer.counter_delta(first, last)
        self.assertFalse(continuous)

    def test_summary_chain_is_hash_linked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "chain.ndjson"
            chain = observer.ChainWriter(path)
            first = chain.emit("ONE", {"value": 1})
            second = chain.emit("TWO", {"value": 2})
        self.assertEqual(first["previous_hash"], observer.ZERO_HASH)
        self.assertEqual(second["previous_hash"], first["sample_sha256"])

    def test_tracer_argv_streams_to_inherited_pipe_and_guards_child(self) -> None:
        argv = observer.tracer_invocation(
            Path("/opt/strace"),
            9,
            Path("/opt/observer.py"),
            ["python3", "work.py"],
        )
        self.assertIn("trace=connect,sendto,sendmsg", argv)
        self.assertIn("/proc/self/fd/9", argv)
        self.assertIn("_guard_exec", argv)
        self.assertNotIn("--user", argv)
        self.assertNotIn("--net", argv)

    def test_packet_hash_rejected(self) -> None:
        with self.assertRaisesRegex(observer.ObserverError, "PACKET_SHA256_INVALID"):
            observer.validate_hash("not-a-hash", "PACKET_SHA256")


if __name__ == "__main__":
    unittest.main()
