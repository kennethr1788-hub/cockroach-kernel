from __future__ import annotations

import importlib.util
import inspect
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

    def test_projection_batches_are_idempotent_and_content_reconciled(self) -> None:
        statement = plan_ab.projection_seed_statement("pf2-10000", 0, 5000)
        reconciliation = plan_ab.projection_reconciliation_statement(
            "pf2-10000", 0, 5000
        )
        self.assertIn("ON CONFLICT (projection_id) DO NOTHING", statement)
        self.assertIn("generate_series(0,4999)", statement)
        self.assertIn(
            "actual not in (0, stop - start)",
            inspect.getsource(plan_ab.seed_plan_specific_batches),
        )
        self.assertIn("projected_json IS DISTINCT FROM", reconciliation)
        self.assertIn("projection_hash IS DISTINCT FROM", reconciliation)

    def test_secondary_receipt_preserves_one_event_two_receipt_shape(self) -> None:
        statement = plan_ab.secondary_receipt_seed_statement("pf2-10000", 0, 5000)
        reconciliation = plan_ab.secondary_receipt_reconciliation_statement(
            "pf2-10000", 0, 5000
        )
        self.assertIn("'-receipt-' || i::STRING || '-1'", statement)
        self.assertIn("'-event-' || i::STRING || '-0'", statement)
        self.assertIn("ON CONFLICT (receipt_hash) DO NOTHING", statement)
        self.assertIn("receipt_json IS DISTINCT FROM", reconciliation)

    def test_pf2_seed_operations_are_individually_bounded(self) -> None:
        self.assertEqual(plan_ab.SEED_BATCH_TASKS, 5000)
        self.assertEqual(plan_ab.PROJECTION_BATCH_TASKS, 5000)
        self.assertLess(plan_ab.SEED_TAIL_RESERVE_SECONDS, plan_ab.SCALE_DEADLINE_SECONDS)
        self.assertLess(
            plan_ab.PROJECTION_TAIL_RESERVE_SECONDS,
            plan_ab.SEED_TAIL_RESERVE_SECONDS,
        )

    def test_ann_quality_remains_deferred_to_full_cardinality_gate(self) -> None:
        source = inspect.getsource(plan_ab.scale_trial)
        self.assertNotIn("prove_seeded_vector_index", source)
        self.assertIn("vector_index_metadata", source)
        self.assertIn("ann_quality_deferred_to_full_cardinality_pf5", source)

    def test_post_seed_operations_share_the_scale_deadline(self) -> None:
        source = inspect.getsource(plan_ab.scale_trial)
        self.assertIn("timeout=remaining_timeout(600)", source)
        self.assertGreaterEqual(source.count("deadline=scale_deadline"), 4)

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
