-- P6 typed handoffs and atomic authority transition receipts.
CREATE TABLE IF NOT EXISTS p6_handoffs (
  handoff_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  stage STRING NOT NULL CHECK (stage IN ('THINKER_TO_WORKER', 'WORKER_TO_VERIFIER')),
  candidate_id STRING NOT NULL REFERENCES candidates (candidate_id),
  handoff_json JSONB NOT NULL,
  handoff_hash BYTES NOT NULL CHECK (length(handoff_hash) = 32),
  parent_handoff_hash BYTES NULL,
  parent_receipt_hash BYTES NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS p6_votes (
  vote_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  candidate_id STRING NOT NULL REFERENCES candidates (candidate_id),
  lane_id STRING NOT NULL,
  vote_json JSONB NOT NULL,
  vote_hash BYTES NOT NULL CHECK (length(vote_hash) = 32),
  created_at TIMESTAMPTZ NOT NULL,
  UNIQUE (candidate_id, lane_id)
);

CREATE TABLE IF NOT EXISTS p6_transitions (
  task_id STRING PRIMARY KEY REFERENCES tasks (task_id),
  intent_id STRING NOT NULL UNIQUE,
  candidate_id STRING NOT NULL REFERENCES candidates (candidate_id),
  decision STRING NOT NULL CHECK (decision IN ('PROMOTE', 'REFUSE', 'INVALID')),
  reason_code STRING NOT NULL,
  decision_hash BYTES NOT NULL CHECK (length(decision_hash) = 32),
  transition_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS p6_transition_receipts (
  intent_id STRING PRIMARY KEY REFERENCES p6_transitions (intent_id),
  task_id STRING NOT NULL UNIQUE REFERENCES p6_transitions (task_id),
  receipt_id STRING NOT NULL UNIQUE,
  receipt_json JSONB NOT NULL,
  receipt_hash BYTES NOT NULL CHECK (length(receipt_hash) = 32),
  created_at TIMESTAMPTZ NOT NULL
);
