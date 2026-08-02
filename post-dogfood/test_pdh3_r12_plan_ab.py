from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_plan_ab_tested", HERE / "pdh3_r12_plan_ab.py"
)
assert SPEC is not None and SPEC.loader is not None
plan_ab = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plan_ab)


class PlanABTests(unittest.TestCase):
    def test_plan_parser(self) -> None:
        self.assertTrue(plan_ab.full_scan("flags: FULL SCAN"))
        self.assertTrue(plan_ab.full_scan("spans: all"))
        self.assertFalse(plan_ab.full_scan("spans: /1-/2"))

    def test_exact_query_family_count(self) -> None:
        queries = plan_ab.query_definitions("campaign")
        self.assertEqual(len(queries), 27)
        self.assertEqual(sum(name.startswith("receipt-") for name in queries), 5)
        self.assertEqual(sum(name.startswith("vector-") for name in queries), 20)

    def test_index_definitions_are_narrow(self) -> None:
        self.assertEqual(
            plan_ab.RECEIPT_INDEX_DDL,
            "CREATE INDEX receipts_task_id_idx ON ck.receipts(task_id) STORING(status,event_hash)",
        )
        self.assertNotIn("IF NOT EXISTS", plan_ab.RECEIPT_INDEX_DDL)

    def test_teardown_preserves_and_hashes_database_log(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            root = parent / "runtime"
            output = parent / "evidence"
            root.mkdir()
            output.mkdir()
            raw = b"synthetic cockroach log\n"
            (root / "cockroach.log").write_bytes(raw)
            teardown: dict[str, object] = {}

            plan_ab.preserve_database_log(root, output, teardown)

            self.assertEqual((output / "cockroach.log").read_bytes(), raw)
            self.assertEqual(teardown["database_log_sha256"], plan_ab.digest(raw))


if __name__ == "__main__":
    unittest.main()
