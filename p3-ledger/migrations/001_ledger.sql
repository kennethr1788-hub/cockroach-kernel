-- Cockroach Kernel P3 durable trajectory/evidence ledger.
-- All authoritative timestamps are supplied by the caller; verdict logic is
-- outside SQL and deterministic.
CREATE TABLE IF NOT EXISTS tasks (
  task_id STRING PRIMARY KEY,
  schema_version STRING NOT NULL,
  declared_state_hash BYTES NOT NULL,
  task_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS trajectory_events (
  event_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  sequence INT8 NOT NULL,
  parent_event_id STRING NULL,
  state_hash BYTES NOT NULL,
  event_json JSONB NOT NULL,
  event_hash BYTES NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  UNIQUE (task_id, sequence),
  UNIQUE (task_id, event_hash)
);

CREATE TABLE IF NOT EXISTS causal_links (
  link_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  from_event_id STRING NOT NULL,
  to_event_id STRING NOT NULL,
  relation STRING NOT NULL,
  link_hash BYTES NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS context_records (
  context_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  source_event_id STRING NOT NULL,
  context_json JSONB NOT NULL,
  context_hash BYTES NOT NULL,
  retention_class STRING NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS persona_manifests (
  manifest_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  persona_ids JSONB NOT NULL,
  source_hash BYTES NOT NULL,
  prompt_hash BYTES NOT NULL,
  route STRING NOT NULL,
  manifest_hash BYTES NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS policy_versions (
  policy_id STRING PRIMARY KEY,
  version STRING NOT NULL UNIQUE,
  policy_json JSONB NOT NULL,
  policy_hash BYTES NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS candidates (
  candidate_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  source_event_id STRING NOT NULL,
  candidate_prefix JSONB NOT NULL,
  state_hash BYTES NOT NULL,
  receipt_hash BYTES NOT NULL,
  policy_version STRING NOT NULL,
  verdict STRING NOT NULL CHECK (verdict IN ('PROMOTE', 'REFUSE', 'INVALID')),
  reason_code STRING NOT NULL,
  retention_class STRING NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS evaluator_votes (
  vote_id STRING PRIMARY KEY,
  candidate_id STRING NOT NULL REFERENCES candidates (candidate_id),
  evaluator_id STRING NOT NULL,
  vote STRING NOT NULL CHECK (vote IN ('APPROVE', 'REFUSE', 'INVALID')),
  output_hash BYTES NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  UNIQUE (candidate_id, evaluator_id)
);

CREATE TABLE IF NOT EXISTS dissent_records (
  dissent_id STRING PRIMARY KEY,
  candidate_id STRING NOT NULL REFERENCES candidates (candidate_id),
  evaluator_id STRING NOT NULL,
  dissent_json JSONB NOT NULL,
  dissent_hash BYTES NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS recovery_capsules (
  capsule_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  source_receipt_hash BYTES NOT NULL,
  candidate_id STRING NOT NULL REFERENCES candidates (candidate_id),
  capsule_json JSONB NOT NULL,
  capsule_hash BYTES NOT NULL,
  warrant_id STRING NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS one_use_warrants (
  warrant_id STRING PRIMARY KEY,
  capsule_id STRING NOT NULL REFERENCES recovery_capsules (capsule_id),
  state STRING NOT NULL CHECK (state IN ('ISSUED', 'CONSUMED', 'INVALID')),
  warrant_hash BYTES NOT NULL,
  consumed_at TIMESTAMPTZ NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS immutable_receipts (
  receipt_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  transition STRING NOT NULL CHECK (transition IN ('DECLARE', 'RECORD', 'EVALUATE', 'PROMOTE', 'REFUSE', 'INVALID')),
  subject_id STRING NOT NULL,
  receipt_json JSONB NOT NULL,
  receipt_hash BYTES NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  UNIQUE (task_id, transition, subject_id)
);

CREATE TABLE IF NOT EXISTS evidence_budget (
  budget_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  workload_bytes INT8 NOT NULL,
  telemetry_bytes INT8 NOT NULL,
  receipt_bytes INT8 NOT NULL,
  manifest_bytes INT8 NOT NULL,
  database_bytes INT8 NOT NULL,
  measurement_hash BYTES NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS trajectory_task_sequence ON trajectory_events (task_id, sequence);
CREATE INDEX IF NOT EXISTS receipts_task_created ON immutable_receipts (task_id, created_at);
