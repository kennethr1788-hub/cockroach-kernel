-- P7 declared-loss, surviving-candidate, one-use warrant, and recovery ledger.
CREATE TABLE IF NOT EXISTS p7_manifests (
  manifest_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  manifest_json JSONB NOT NULL,
  manifest_hash BYTES NOT NULL CHECK (length(manifest_hash) = 32)
);

CREATE TABLE IF NOT EXISTS p7_loss_receipts (
  receipt_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  manifest_id STRING NOT NULL REFERENCES p7_manifests (manifest_id),
  receipt_json JSONB NOT NULL,
  receipt_hash BYTES NOT NULL CHECK (length(receipt_hash) = 32)
);

CREATE TABLE IF NOT EXISTS p7_recovery_candidates (
  candidate_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  loss_receipt_hash BYTES NOT NULL CHECK (length(loss_receipt_hash) = 32),
  candidate_json JSONB NOT NULL,
  candidate_hash BYTES NOT NULL CHECK (length(candidate_hash) = 32)
);

CREATE TABLE IF NOT EXISTS p7_warrants (
  warrant_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  candidate_id STRING NOT NULL REFERENCES p7_recovery_candidates (candidate_id),
  decision_hash BYTES NOT NULL CHECK (length(decision_hash) = 32),
  state STRING NOT NULL CHECK (state IN ('ISSUED', 'CONSUMED', 'INVALID')),
  warrant_json JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS p7_recoveries (
  recovery_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  candidate_id STRING NOT NULL REFERENCES p7_recovery_candidates (candidate_id),
  warrant_id STRING NOT NULL UNIQUE REFERENCES p7_warrants (warrant_id),
  decision_json JSONB NOT NULL,
  decision_hash BYTES NOT NULL CHECK (length(decision_hash) = 32)
);

CREATE TABLE IF NOT EXISTS p7_recovery_receipts (
  receipt_id STRING PRIMARY KEY,
  recovery_id STRING NOT NULL UNIQUE REFERENCES p7_recoveries (recovery_id),
  receipt_json JSONB NOT NULL,
  receipt_hash BYTES NOT NULL CHECK (length(receipt_hash) = 32)
);

CREATE TABLE IF NOT EXISTS p7_unrecovered_ledgers (
  ledger_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  ledger_json JSONB NOT NULL,
  ledger_hash BYTES NOT NULL CHECK (length(ledger_hash) = 32)
);
