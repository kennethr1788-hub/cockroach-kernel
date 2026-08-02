from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_checkpoint_tested", HERE / "pdh3_r12_checkpoint.py"
)
assert SPEC is not None and SPEC.loader is not None
checkpoint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checkpoint)


PACKET = "a" * 64


class CheckpointTests(unittest.TestCase):
    def test_publish_verify_and_acknowledge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            export = root / "export"
            source.mkdir()
            (source / "a.json").write_bytes(b"{}")
            (source / "b.log").write_bytes(b"evidence\n")
            manifest = checkpoint.publish(
                source_root=source,
                export_root=export,
                sequence=1,
                previous_manifest_sha256=checkpoint.ZERO_HASH,
                packet_sha256=PACKET,
                files=["b.log", "a.json"],
            )
            verified = checkpoint.verify_download(
                manifest_path=export / "checkpoint-0001.json",
                archive_path=export / "checkpoint-0001.tgz",
                expected_packet_sha256=PACKET,
                expected_sequence=1,
                expected_previous_manifest_sha256=checkpoint.ZERO_HASH,
            )
            self.assertEqual(verified, manifest)
            ack = checkpoint.acknowledge(
                output=root / "ack.json",
                manifest=manifest,
                local_archive=export / "checkpoint-0001.tgz",
                acknowledged_utc="2026-08-02T00:00:00Z",
            )
            self.assertTrue(ack["independent_local_copy"])

    def test_partial_archive_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            export = root / "export"
            source.mkdir()
            (source / "a").write_bytes(b"data")
            checkpoint.publish(
                source_root=source,
                export_root=export,
                sequence=1,
                previous_manifest_sha256=checkpoint.ZERO_HASH,
                packet_sha256=PACKET,
                files=["a"],
            )
            archive = export / "checkpoint-0001.tgz"
            archive.write_bytes(archive.read_bytes()[:-4])
            with self.assertRaises(checkpoint.CheckpointError):
                checkpoint.verify_download(
                    manifest_path=export / "checkpoint-0001.json",
                    archive_path=archive,
                    expected_packet_sha256=PACKET,
                )

    def test_sequence_chain_rules(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.mkdir(exist_ok=True)
            (root / "a").write_bytes(b"x")
            with self.assertRaisesRegex(checkpoint.CheckpointError, "GENESIS"):
                checkpoint.publish(
                    source_root=root,
                    export_root=root / "out",
                    sequence=1,
                    previous_manifest_sha256="b" * 64,
                    packet_sha256=PACKET,
                    files=["a"],
                )

    def test_unsafe_paths_rejected(self) -> None:
        for value in ("/absolute", "../escape", "a/../b", "a\\b"):
            with self.subTest(value=value):
                with self.assertRaises(checkpoint.CheckpointError):
                    checkpoint.validate_relative(value)


if __name__ == "__main__":
    unittest.main()
