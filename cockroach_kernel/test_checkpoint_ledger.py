import unittest

from cockroach_kernel.checkpoint_ledger import (CHECKPOINT_INSERT_SQL, CheckpointError,
                                                build_checkpoint, validate_checkpoint)


HASHES = {
    "parent_hash": "a" * 64,
    "request_hash": "b" * 64,
    "decision_hash": "c" * 64,
    "receipt_hash": "d" * 64,
    "preservation_hash": "e" * 64,
}


class CheckpointLedgerTests(unittest.TestCase):
    def test_checkpoint_is_hash_bound_and_append_only(self):
        checkpoint = build_checkpoint(
            request_id="request-1", task_id="task-1", verdict="PROMOTE",
            recovered_paths=["src/feature.py"], **HASHES
        )
        self.assertTrue(checkpoint["append_only"])
        self.assertEqual(validate_checkpoint(checkpoint), checkpoint)

    def test_tamper_and_unsafe_path_fail_closed(self):
        checkpoint = build_checkpoint(
            request_id="request-1", task_id="task-1", verdict="PROMOTE",
            recovered_paths=["src/feature.py"], **HASHES
        )
        checkpoint["verdict"] = "REFUSE"
        with self.assertRaisesRegex(CheckpointError, "CHECKPOINT_HASH_MISMATCH"):
            validate_checkpoint(checkpoint)
        with self.assertRaisesRegex(CheckpointError, "RECOVERED_PATHS_INVALID"):
            build_checkpoint(request_id="request-1", task_id="task-1", verdict="PROMOTE",
                             recovered_paths=["../escape"], **HASHES)

    def test_sql_is_parameterized_and_idempotent(self):
        self.assertIn("$1", CHECKPOINT_INSERT_SQL)
        self.assertIn("ON CONFLICT (checkpoint_id) DO NOTHING", CHECKPOINT_INSERT_SQL)
        self.assertNotIn("DROP", CHECKPOINT_INSERT_SQL.upper())


if __name__ == "__main__":
    unittest.main()
