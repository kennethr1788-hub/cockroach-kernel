from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_r6_pf4_only_tested", HERE / "pdh3_r12_r6_pf4_only.py"
)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class PF4OnlyTests(unittest.TestCase):
    def test_terminal_green_requires_all_four_conditions(self) -> None:
        self.assertTrue(module.terminal_green(
            create_returncode=0, pf4_returncode=0, teardown_green=True,
            pf4_status="PF4_GREEN",
        ))
        for values in (
            (1, 0, True, "PF4_GREEN"),
            (0, 1, True, "PF4_GREEN"),
            (0, 0, False, "PF4_GREEN"),
            (0, 0, True, "PF4_BLOCKED"),
        ):
            self.assertFalse(module.terminal_green(
                create_returncode=values[0], pf4_returncode=values[1],
                teardown_green=values[2], pf4_status=values[3],
            ))

    def test_terminal_guard_requires_hash_valid_teardown_event(self) -> None:
        class Lifecycle:
            @staticmethod
            def read_chain(path: Path):
                return [{"event": "TEARDOWN_GREEN", "event_hash": "a" * 64}]

        with tempfile.TemporaryDirectory() as temporary:
            result = module.wait_for_terminal_guard(
                Lifecycle(), Path(temporary) / "lifecycle.ndjson",
                timeout_seconds=1,
            )
        self.assertEqual(result["event"], "TEARDOWN_GREEN")

    def test_guard_block_is_terminal(self) -> None:
        class Lifecycle:
            @staticmethod
            def read_chain(path: Path):
                return [{"event": "GUARD_BLOCKED", "event_hash": "b" * 64}]

        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(module.PF4OnlyError, "LIFECYCLE_GUARD_BLOCKED"):
                module.wait_for_terminal_guard(
                    Lifecycle(), Path(temporary) / "lifecycle.ndjson",
                    timeout_seconds=1,
                )


if __name__ == "__main__":
    unittest.main()
