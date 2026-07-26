CREATE TABLE IF NOT EXISTS p8_policies (
  policy_id STRING PRIMARY KEY,
  policy_json JSONB NOT NULL,
  policy_hash BYTES NOT NULL UNIQUE CHECK (length(policy_hash) = 32),
  status STRING NOT NULL CHECK (status IN ('GOLDEN', 'SUPERSEDED'))
);

CREATE TABLE IF NOT EXISTS p8_incident_sets (
  incident_set_hash BYTES PRIMARY KEY CHECK (length(incident_set_hash) = 32),
  incidents_json JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS p8_proposals (
  proposal_id STRING PRIMARY KEY,
  proposal_json JSONB NOT NULL,
  proposal_hash BYTES NOT NULL UNIQUE CHECK (length(proposal_hash) = 32),
  outcome STRING NOT NULL CHECK (outcome IN ('PROMOTE', 'REJECT')),
  reason STRING NOT NULL
);

CREATE TABLE IF NOT EXISTS p8_promotions (
  proposal_id STRING PRIMARY KEY REFERENCES p8_proposals (proposal_id),
  previous_policy_id STRING NOT NULL REFERENCES p8_policies (policy_id),
  promoted_policy_id STRING NOT NULL REFERENCES p8_policies (policy_id),
  replay_hash BYTES NOT NULL CHECK (length(replay_hash) = 32),
  golden_pair_json JSONB NOT NULL,
  receipt_json JSONB NOT NULL,
  receipt_hash BYTES NOT NULL UNIQUE CHECK (length(receipt_hash) = 32)
);

CREATE TABLE IF NOT EXISTS p8_rollbacks (
  rollback_id STRING PRIMARY KEY,
  promotion_receipt_hash BYTES NOT NULL CHECK (length(promotion_receipt_hash) = 32),
  from_policy_id STRING NOT NULL REFERENCES p8_policies (policy_id),
  to_policy_id STRING NOT NULL REFERENCES p8_policies (policy_id),
  receipt_json JSONB NOT NULL,
  receipt_hash BYTES NOT NULL UNIQUE CHECK (length(receipt_hash) = 32)
);
