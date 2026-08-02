from __future__ import annotations

import json
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest

from run_pdh3_traced import (
    TraceFailure,
    TraceStreamState,
    build_child_environment,
    build_strace_invocation,
    canonical,
    classify_line,
    digest,
    observe_process,
    scan_incremental,
    sha256_file,
    terminate_group,
    write_progress_receipt,
)


class FakeProcess:
    def __init__(self, pid: int = 4242) -> None:
        self.pid = pid
        self.returncode: int | None = None

    def poll(self) -> int | None:
        return self.returncode

    def wait(self, timeout: float | None = None) -> int:
        del timeout
        if self.returncode is None:
            self.returncode = -signal.SIGTERM
        return self.returncode


class TraceClassifierTests(unittest.TestCase):
    def test_permits_ipv4_loopback(self) -> None:
        line = (
            'connect(3, {sa_family=AF_INET, sin_port=htons(26257), '
            'sin_addr=inet_addr("127.0.0.1")}, 16) = 0'
        )
        self.assertEqual(classify_line(line), ("PERMITTED_LOOPBACK", "connect"))

    def test_permits_ipv6_loopback(self) -> None:
        line = (
            'connect(3, {sa_family=AF_INET6, sin6_port=htons(26257), '
            'inet_pton(AF_INET6, "::1", &sin6_addr)}, 28) = 0'
        )
        self.assertEqual(classify_line(line), ("PERMITTED_LOOPBACK", "connect"))

    def test_permits_unix_and_netlink(self) -> None:
        self.assertEqual(
            classify_line('connect(3, {sa_family=AF_UNIX, sun_path="/x"}, 4) = 0'),
            ("PERMITTED_LOCAL_KERNEL", "connect"),
        )
        self.assertEqual(
            classify_line("sendto(3, \"x\", 1, 0, {sa_family=AF_NETLINK}, 12) = 1"),
            ("PERMITTED_LOCAL_KERNEL", "sendto"),
        )

    def test_sendmsg_destination_is_classified(self) -> None:
        self.assertEqual(
            classify_line(
                'sendmsg(3, {msg_name={sa_family=AF_INET, '
                'sin_port=htons(26257), sin_addr=inet_addr("127.0.0.1")}, '
                'msg_namelen=16, msg_iov=[], msg_iovlen=0}, 0) = 0'
            ),
            ("PERMITTED_LOOPBACK", "sendmsg"),
        )
        self.assertEqual(
            classify_line(
                'sendmsg(3, {msg_name={sa_family=AF_INET, '
                'sin_port=htons(443), sin_addr=inet_addr("198.51.100.7")}, '
                'msg_namelen=16, msg_iov=[], msg_iovlen=0}, 0) = 0'
            ),
            ("BLOCK_EXTERNAL", "sendmsg"),
        )
        self.assertEqual(
            classify_line(
                'sendmsg(3, {msg_name=NULL, msg_namelen=0, msg_iov=[], '
                'msg_iovlen=0}, 0) = 0'
            ),
            ("PERMITTED_CONNECTED_NO_DESTINATION", "sendmsg"),
        )

    def test_blocks_external_addresses(self) -> None:
        line = (
            'connect(3, {sa_family=AF_INET, sin_port=htons(443), '
            'sin_addr=inet_addr("198.51.100.12")}, 16) = -1'
        )
        self.assertEqual(classify_line(line), ("BLOCK_EXTERNAL", "connect"))

    def test_blocks_unparseable_network_destination(self) -> None:
        self.assertEqual(
            classify_line("connect(3, 0x7fff0000, 16) = -1"),
            ("BLOCK_UNPARSEABLE_FAMILY", "connect"),
        )

    def test_permits_destinationless_send_on_connected_socket(self) -> None:
        line = 'sendto(4, "x", 1, MSG_NOSIGNAL, NULL, 0) = 1'
        self.assertEqual(
            classify_line(line),
            ("PERMITTED_CONNECTED_NO_DESTINATION", "sendto"),
        )

    def test_permits_unfinished_destinationless_send(self) -> None:
        line = '1234 sendto(4, "x", 1, MSG_NOSIGNAL, NULL, 0 <unfinished ...>'
        self.assertEqual(
            classify_line(line),
            ("PERMITTED_CONNECTED_NO_DESTINATION", "sendto"),
        )

    def test_still_blocks_sendto_with_external_destination(self) -> None:
        line = (
            'sendto(4, "x", 1, 0, {sa_family=AF_INET, '
            'sin_addr=inet_addr("198.51.100.12")}, 16) = 1'
        )
        self.assertEqual(classify_line(line), ("BLOCK_EXTERNAL", "sendto"))

    def test_payload_af_unix_cannot_mask_external_ipv4_destination(self) -> None:
        line = (
            'sendto(4, "payload AF_UNIX, {sa_family=AF_UNIX}", 38, 0, '
            '{sa_family=AF_INET, sin_port=htons(443), '
            'sin_addr=inet_addr("198.51.100.12")}, 16) = 38'
        )
        self.assertEqual(classify_line(line), ("BLOCK_EXTERNAL", "sendto"))

    def test_payload_af_unix_cannot_mask_external_ipv6_destination(self) -> None:
        line = (
            'sendto(4, "AF_UNIX", 7, 0, {sa_family=AF_INET6, '
            'sin6_port=htons(443), inet_pton(AF_INET6, "2001:db8::1", '
            '&sin6_addr)}, 28) = 7'
        )
        self.assertEqual(classify_line(line), ("BLOCK_EXTERNAL", "sendto"))

    def test_payload_network_tokens_do_not_override_unix_destination(self) -> None:
        line = (
            'sendto(4, "AF_INET inet_addr(\\"198.51.100.12\\")", 36, 0, '
            '{sa_family=AF_UNIX, sun_path="/tmp/pdh3.sock"}, 18) = 36'
        )
        self.assertEqual(
            classify_line(line),
            ("PERMITTED_LOCAL_KERNEL", "sendto"),
        )

    def test_payload_external_address_does_not_override_loopback(self) -> None:
        line = (
            'sendto(4, "inet_addr(\\"198.51.100.12\\")", 30, 0, '
            '{sa_family=AF_INET, sin_port=htons(26257), '
            'sin_addr=inet_addr("127.0.0.1")}, 16) = 30'
        )
        self.assertEqual(classify_line(line), ("PERMITTED_LOOPBACK", "sendto"))

    def test_ignores_non_network_lines(self) -> None:
        self.assertIsNone(classify_line("+++ exited with 0 +++"))


class TraceStreamTests(unittest.TestCase):
    def test_single_stream_invocation_uses_f_not_ff(self) -> None:
        invocation = build_strace_invocation(
            Path("/usr/bin/strace"),
            Path("/tmp/trace.log"),
            ["python3", "campaign.py"],
        )
        self.assertIn("-f", invocation)
        self.assertNotIn("-ff", invocation)
        self.assertEqual(invocation[-2:], ["python3", "campaign.py"])

    def test_child_environment_exposes_progress_receipt(self) -> None:
        progress = Path("/tmp/trace-progress.json")
        environment = build_child_environment(
            progress,
            "a" * 64,
            "b" * 64,
            {"PRESERVED": "yes"},
        )
        self.assertEqual(environment["PRESERVED"], "yes")
        self.assertEqual(
            environment["PDH3_TRACE_PROGRESS_RECEIPT"], str(progress)
        )
        self.assertEqual(environment["PDH3_TRACE_PACKET_SHA256"], "a" * 64)
        self.assertEqual(
            environment["PDH3_TRACE_CHILD_COMMAND_SHA256"], "b" * 64
        )

    def test_partial_line_is_buffered_until_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            trace = Path(temporary) / "trace.log"
            trace.write_bytes(
                b'1234 connect(3, {sa_family=AF_INET, sin_addr=inet_addr("127.'
            )
            state = TraceStreamState()

            first_counts, first_violations, _ = scan_incremental(
                trace, state, 1 << 20
            )
            self.assertEqual(first_counts["connect"], 0)
            self.assertEqual(first_violations, [])
            self.assertGreater(len(state.pending), 0)

            with trace.open("ab") as handle:
                handle.write(b'0.0.1")}, 16) = 0\n')
            second_counts, second_violations, _ = scan_incremental(
                trace, state, 1 << 20
            )

            self.assertEqual(second_counts["connect"], 1)
            self.assertEqual(second_counts["permitted_loopback"], 1)
            self.assertEqual(second_violations, [])
            self.assertEqual(state.pending, b"")
            self.assertEqual(state.process_ids, {1234})

    def test_trace_cap_fails_before_reading_oversized_stream(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            trace = Path(temporary) / "trace.log"
            trace.write_bytes(b"x" * 1025)
            state = TraceStreamState()

            with self.assertRaisesRegex(
                TraceFailure, r"^TRACE_BYTES_LIMIT:1025:1024$"
            ):
                scan_incremental(trace, state, 1024)

            self.assertEqual(state.bytes_read, 0)
            self.assertEqual(state.read_calls, 0)

    def test_replaced_trace_stream_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trace = root / "trace.log"
            replacement = root / "replacement.log"
            trace.write_bytes(b"1234 +++ exited with 0 +++\n")
            state = TraceStreamState()
            scan_incremental(trace, state, 1 << 20)
            replacement.write_bytes(b"1234 +++ exited with 0 +++\n")
            replacement.replace(trace)

            with self.assertRaisesRegex(TraceFailure, "^TRACE_FILE_REPLACED$"):
                scan_incremental(trace, state, 1 << 20)

    def test_ten_thousand_process_equivalent_has_constant_empty_poll_io(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            trace = Path(temporary) / "trace.log"
            payload = b"".join(
                f"{pid} +++ exited with 0 +++\n".encode("ascii")
                for pid in range(10_000, 20_000)
            )
            trace.write_bytes(payload)
            state = TraceStreamState()

            scan_incremental(trace, state, 2 * 1024**3)
            initial_read_calls = state.read_calls
            for _ in range(250):
                scan_incremental(trace, state, 2 * 1024**3)

            self.assertEqual(len(state.process_ids), 10_000)
            self.assertEqual(state.bytes_read, len(payload))
            self.assertEqual(state.read_calls, initial_read_calls)
            self.assertEqual(state.poll_count, 251)

    def test_progress_receipt_is_atomic_non_authoritative_and_projected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trace = root / "trace.log"
            progress = root / "trace-progress.json"
            final = root / "trace-final.json"
            trace.write_bytes(b"x" * 100)
            state = TraceStreamState(
                poll_count=3,
                bytes_read=100,
                last_observed_size=100,
                scan_wall_seconds=1.25,
                scan_cpu_seconds=0.25,
            )

            first = write_progress_receipt(
                progress_receipt=progress,
                final_receipt=final,
                trace_prefix=trace,
                state=state,
                maximum_bytes=1_000_000,
                started_utc="2026-07-31T00:00:00Z",
                started_monotonic=100.0,
                observed_monotonic=110.0,
                observed_utc="2026-07-31T00:00:10Z",
                terminal_snapshot=False,
                packet_sha256="a" * 64,
                child_command_sha256="b" * 64,
                campaign_id="ck-pdh3-scale-test",
            )

            self.assertEqual(first["status"], "IN_PROGRESS")
            self.assertFalse(first["authoritative"])
            self.assertEqual(first["elapsed_seconds"], 10.0)
            self.assertEqual(first["trace_bytes"], 100)
            self.assertEqual(first["trace_stream_count"], 1)
            self.assertEqual(first["scan_count"], 3)
            self.assertEqual(first["scan_wall_seconds"], 1.25)
            self.assertEqual(first["scan_cpu_seconds"], 0.25)
            self.assertEqual(first["current_trace_bytes_per_second"], 10.0)
            self.assertEqual(
                first["projected_trace_bytes_24h_conservative"], 864_100
            )
            self.assertFalse(first["projected_cap_exceeded"])

            trace.write_bytes(b"x" * 200)
            state.poll_count = 4
            state.bytes_read = 200
            state.last_observed_size = 200
            second = write_progress_receipt(
                progress_receipt=progress,
                final_receipt=final,
                trace_prefix=trace,
                state=state,
                maximum_bytes=1_000_000,
                started_utc="2026-07-31T00:00:00Z",
                started_monotonic=100.0,
                observed_monotonic=120.0,
                observed_utc="2026-07-31T00:00:20Z",
                terminal_snapshot=True,
                packet_sha256="a" * 64,
                child_command_sha256="b" * 64,
                campaign_id="ck-pdh3-scale-test",
            )

            self.assertEqual(second["status"], "TERMINAL_SNAPSHOT_NON_AUTHORITATIVE")
            self.assertEqual(second["trace_bytes"], 200)
            self.assertEqual(second["current_trace_bytes_per_second"], 10.0)
            self.assertEqual(json.loads(progress.read_text("utf-8")), second)
            self.assertEqual(progress.read_bytes(), canonical(second))
            self.assertEqual(
                list(root.glob(f".{progress.name}.*.tmp")),
                [],
            )

    def test_terminate_group_escalates_through_injected_signal_function(self) -> None:
        class EscalatingProcess(FakeProcess):
            def __init__(self) -> None:
                super().__init__(pid=8765)
                self.wait_calls = 0

            def wait(self, timeout: float | None = None) -> int:
                self.wait_calls += 1
                if self.wait_calls == 1:
                    raise subprocess.TimeoutExpired(["fake"], timeout)
                self.returncode = -signal.SIGKILL
                return self.returncode

        process = EscalatingProcess()
        signals: list[tuple[int, int]] = []
        terminate_group(
            process,
            signal_group=lambda pid, signum: signals.append((pid, signum)),
        )

        self.assertEqual(
            signals,
            [(8765, signal.SIGTERM), (8765, signal.SIGKILL)],
        )
        self.assertEqual(process.returncode, -signal.SIGKILL)


class TraceReceiptTests(unittest.TestCase):
    def test_clean_terminal_scan_emits_authoritative_green_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trace = root / "trace.log"
            receipt = root / "trace-receipt.json"
            trace.write_bytes(
                b'1234 connect(3, {sa_family=AF_INET, sin_addr=inet_addr("127.0.0.1")}, 16) = 0\n'
            )
            process = FakeProcess()
            process.returncode = 0

            record = observe_process(
                process,
                trace_prefix=trace,
                receipt=receipt,
                packet_sha256="e" * 64,
                strace=Path("/usr/bin/strace"),
                strace_sha256="f" * 64,
                command=[
                    "python3", "campaign.py", "--campaign-id",
                    "ck-pdh3-scale-test",
                ],
                poll_seconds=0.5,
                maximum_bytes=2 * 1024**3,
                started_utc="2026-07-31T00:00:00Z",
            )

            self.assertEqual(record["status"], "GREEN")
            self.assertTrue(record["authoritative"])
            self.assertTrue(record["green"])
            self.assertEqual(
                record["tool_sha256"],
                sha256_file(Path(__file__).parent / "run_pdh3_traced.py"),
            )
            self.assertEqual(record["trace_file_count"], 1)
            self.assertEqual(record["trace_emitting_process_count"], 1)
            self.assertIsNone(record["observer_error"])

    def test_cap_emits_canonical_blocked_receipt_and_terminates_group(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trace = root / "trace.log"
            receipt = root / "trace-receipt.json"
            trace.write_bytes(b"x" * 2049)
            process = FakeProcess()
            terminated: list[int] = []

            def terminate(candidate: FakeProcess) -> None:
                terminated.append(candidate.pid)
                candidate.returncode = -signal.SIGTERM

            record = observe_process(
                process,
                trace_prefix=trace,
                receipt=receipt,
                packet_sha256="a" * 64,
                strace=Path("/usr/bin/strace"),
                strace_sha256="b" * 64,
                command=[
                    "python3", "campaign.py", "--campaign-id",
                    "ck-pdh3-scale-test",
                ],
                poll_seconds=0.5,
                maximum_bytes=2048,
                started_utc="2026-07-31T00:00:00Z",
                terminate_function=terminate,
                sleep_function=lambda _: None,
            )

            self.assertEqual(terminated, [4242])
            self.assertEqual(record["status"], "BLOCKED")
            self.assertFalse(record["green"])
            self.assertEqual(record["claim"], "PROCESS_TREE_OBSERVATION_BLOCKED")
            self.assertEqual(
                record["observer_error"]["reason"],
                "TRACE_BYTES_LIMIT:2049:2048",
            )
            self.assertEqual(record["trace_file_count"], 1)
            self.assertEqual(record["trace_bytes"], 2049)
            self.assertFalse(record["trace_files"][0]["hash_complete"])
            self.assertIsNone(record["trace_files"][0]["sha256"])
            progress = Path(record["progress_receipt_path"])
            progress_record = json.loads(progress.read_text("utf-8"))
            self.assertFalse(progress_record["authoritative"])
            self.assertEqual(
                record["progress_receipt_sha256"],
                progress_record["progress_receipt_sha256"],
            )
            body = {key: value for key, value in record.items() if key != "receipt_sha256"}
            self.assertEqual(record["receipt_sha256"], digest(canonical(body)))
            self.assertEqual(json.loads(receipt.read_text("utf-8")), record)
            self.assertEqual(receipt.read_bytes(), canonical(record))

    def test_arbitrary_observer_failure_still_emits_blocked_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trace = root / "trace.log"
            receipt = root / "trace-receipt.json"
            trace.write_bytes(b"")
            process = FakeProcess()

            def fail_scan(*args: object, **kwargs: object) -> object:
                del args, kwargs
                raise OSError("observer read failed")

            def terminate(candidate: FakeProcess) -> None:
                candidate.returncode = -signal.SIGTERM

            record = observe_process(
                process,
                trace_prefix=trace,
                receipt=receipt,
                packet_sha256="c" * 64,
                strace=Path("/usr/bin/strace"),
                strace_sha256="d" * 64,
                command=[
                    "python3", "campaign.py", "--campaign-id",
                    "ck-pdh3-scale-test",
                ],
                poll_seconds=0.5,
                maximum_bytes=2 * 1024**3,
                started_utc="2026-07-31T00:00:00Z",
                scan_function=fail_scan,
                terminate_function=terminate,
                sleep_function=lambda _: None,
            )

            self.assertEqual(record["status"], "BLOCKED")
            self.assertEqual(record["observer_error"]["type"], "OSError")
            self.assertEqual(record["observer_error"]["phase"], "scan")
            self.assertTrue(receipt.is_file())

    def test_progress_write_failure_blocks_and_terminates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trace = root / "trace.log"
            receipt = root / "trace-receipt.json"
            progress = root / "occupied-progress-path"
            trace.write_bytes(b"1234 +++ exited with 0 +++\n")
            progress.mkdir()
            process = FakeProcess()
            terminated: list[int] = []

            def terminate(candidate: FakeProcess) -> None:
                terminated.append(candidate.pid)
                candidate.returncode = -signal.SIGTERM

            record = observe_process(
                process,
                trace_prefix=trace,
                receipt=receipt,
                packet_sha256="1" * 64,
                strace=Path("/usr/bin/strace"),
                strace_sha256="2" * 64,
                command=[
                    "python3", "campaign.py", "--campaign-id",
                    "ck-pdh3-scale-test",
                ],
                poll_seconds=0.5,
                maximum_bytes=2 * 1024**3,
                started_utc="2026-07-31T00:00:00Z",
                progress_receipt=progress,
                terminate_function=terminate,
                sleep_function=lambda _: None,
            )

            self.assertEqual(terminated, [4242])
            self.assertEqual(record["status"], "BLOCKED")
            self.assertEqual(record["observer_error"]["phase"], "progress")
            self.assertIsNone(record["progress_receipt_sha256"])
            self.assertTrue(receipt.is_file())


if __name__ == "__main__":
    unittest.main()
