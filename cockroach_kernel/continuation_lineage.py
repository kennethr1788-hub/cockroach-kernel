"""Read-only CockroachDB lineage contract for continuation briefs.

The query is parameterized and returns only hash-bound lineage. This module
does not open a connection, call AWS, or decide a recovery verdict.
"""
from __future__ import annotations

import re
from typing import Any

HASH = re.compile(r"^[0-9a-f]{64}$")

LINEAGE_SQL = """
SELECT t.task_id,
       t.task_hash,
       t.state_hash,
       e.event_id,
       e.sequence,
       e.parent_event_hash,
       e.event_hash,
       r.receipt_hash,
       r.status AS receipt_status,
       w.request_hash,
       w.response_hash,
       w.result_hash,
       w.status AS worker_status,
       p.projection_hash
FROM ck.tasks AS t
JOIN ck.trajectory_events AS e ON e.task_id = t.task_id
JOIN ck.receipts AS r ON r.task_id = t.task_id AND r.event_hash = e.event_hash
LEFT JOIN ck.worker_results AS w ON w.task_id = t.task_id
LEFT JOIN ck.projection_events AS p
  ON p.source_table = 'receipts' AND p.source_key = encode(r.receipt_hash, 'hex')
WHERE t.task_id = :task_id
  AND r.status = 'SEALED'
ORDER BY e.sequence DESC
LIMIT 1
""".strip()


class LineageError(ValueError):
    pass


def _hex(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not HASH.fullmatch(value):
        raise LineageError(f"{field}_HASH_INVALID")
    return value


def parse_lineage_row(row: Any) -> dict[str, Any]:
    """Validate one normalized driver row; no SQL or verdict authority."""
    if isinstance(row, dict):
        required = {"task_id", "task_hash", "state_hash", "event_id", "sequence",
                    "parent_event_hash", "event_hash", "receipt_hash", "receipt_status",
                    "request_hash", "response_hash", "result_hash", "worker_status",
                    "projection_hash"}
        if set(row) != required:
            raise LineageError("LINEAGE_FIELDS_INVALID")
        value = row
    elif isinstance(row, (list, tuple)) and len(row) == 14:
        value = dict(zip(("task_id", "task_hash", "state_hash", "event_id", "sequence",
                          "parent_event_hash", "event_hash", "receipt_hash", "receipt_status",
                          "request_hash", "response_hash", "result_hash", "worker_status",
                          "projection_hash"), row))
    else:
        raise LineageError("LINEAGE_ROW_INVALID")
    for key in ("task_id", "event_id"):
        if not isinstance(value[key], str) or not value[key]:
            raise LineageError("LINEAGE_ID_INVALID")
    if isinstance(value["sequence"], bool) or not isinstance(value["sequence"], int) or value["sequence"] < 0:
        raise LineageError("LINEAGE_SEQUENCE_INVALID")
    for key in ("task_hash", "state_hash", "parent_event_hash", "event_hash", "receipt_hash",
                "request_hash", "response_hash", "result_hash", "projection_hash"):
        _hex(value[key], key)
    if value["receipt_status"] != "SEALED":
        raise LineageError("RECEIPT_NOT_SEALED")
    if value["worker_status"] not in {None, "ADVISORY"}:
        raise LineageError("WORKER_AUTHORITY_INVALID")
    return dict(value)

