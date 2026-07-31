from __future__ import annotations

import unittest

from run_pdh3_traced import classify_line


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

    def test_ignores_non_network_lines(self) -> None:
        self.assertIsNone(classify_line("+++ exited with 0 +++"))


if __name__ == "__main__":
    unittest.main()
