import unittest

from cockroach_kernel.continuation_lineage import LINEAGE_SQL, LineageError, parse_lineage_row


def row():
    return {"task_id": "task-1", "task_hash": "a" * 64, "state_hash": "b" * 64,
            "event_id": "event-1", "sequence": 0, "parent_event_hash": "0" * 64,
            "event_hash": "c" * 64, "receipt_hash": "d" * 64, "receipt_status": "SEALED",
            "request_hash": "e" * 64, "response_hash": "f" * 64, "result_hash": "1" * 64,
            "worker_status": "ADVISORY", "projection_hash": "2" * 64}


class LineageTests(unittest.TestCase):
    def test_query_is_parameterized_and_read_only(self):
        self.assertIn(":task_id", LINEAGE_SQL)
        self.assertNotIn("INSERT", LINEAGE_SQL.upper())
        self.assertNotIn("UPDATE", LINEAGE_SQL.upper())
        self.assertNotIn("DELETE", LINEAGE_SQL.upper())

    def test_row_is_strictly_parsed(self):
        self.assertEqual(parse_lineage_row(row())["receipt_status"], "SEALED")
        bad = row()
        bad["worker_status"] = "PROMOTE"
        with self.assertRaises(LineageError):
            parse_lineage_row(bad)

    def test_optional_advisory_and_projection_are_explicit(self):
        value = row()
        value["worker_status"] = None
        value["projection_hash"] = None
        self.assertIsNone(parse_lineage_row(value)["projection_hash"])


if __name__ == "__main__":
    unittest.main()
