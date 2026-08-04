-- Applied only by the separately bounded owner session after ck_runtime exists.
-- This file creates no identity, role, database, schema, or cluster setting.

GRANT USAGE ON SCHEMA ck TO ck_runtime;

GRANT SELECT, INSERT ON TABLE
  ck.tasks,
  ck.trajectory_events,
  ck.receipts,
  ck.context_vectors,
  ck.worker_results,
  ck.projection_events,
  ck.recovery_checkpoints
TO ck_runtime;

GRANT SELECT ON TABLE ck.mcp_receipt_view TO ck_runtime;
GRANT CHANGEFEED ON TABLE ck.worker_results TO ck_runtime;
