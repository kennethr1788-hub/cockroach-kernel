-- Synthetic CockroachDB contract fixture. No credentials or live connection.
CREATE TABLE trajectory_events (
  event_id STRING PRIMARY KEY,
  task_id STRING NOT NULL,
  sequence INT8 NOT NULL,
  state_hash BYTES NOT NULL,
  receipt_hash BYTES NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  UNIQUE (task_id, sequence)
);

CREATE TABLE recovery_receipts (
  receipt_id STRING PRIMARY KEY,
  task_id STRING NOT NULL,
  event_id STRING NOT NULL,
  verdict STRING NOT NULL,
  receipt_hash BYTES NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  CONSTRAINT verdict_allowed CHECK (verdict IN ('PROMOTE', 'REFUSE', 'INVALID'))
);
