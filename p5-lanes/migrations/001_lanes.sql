-- P5 advisory evaluator persistence. These rows are evidence, never authority.
CREATE TABLE IF NOT EXISTS p5_lane_manifests (
  manifest_id STRING PRIMARY KEY,
  lane_id STRING NOT NULL CHECK (lane_id IN (
    'syntax_structure', 'security_policy', 'logic_coherence',
    'contextual_fit', 'trajectory_alignment'
  )),
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  candidate_id STRING NOT NULL REFERENCES candidates (candidate_id),
  policy_version STRING NOT NULL,
  manifest_json JSONB NOT NULL,
  manifest_hash BYTES NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  UNIQUE (candidate_id, lane_id)
);

CREATE TABLE IF NOT EXISTS p5_lane_results (
  result_id STRING PRIMARY KEY,
  manifest_id STRING NOT NULL REFERENCES p5_lane_manifests (manifest_id),
  lane_id STRING NOT NULL CHECK (lane_id IN (
    'syntax_structure', 'security_policy', 'logic_coherence',
    'contextual_fit', 'trajectory_alignment'
  )),
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  candidate_id STRING NOT NULL REFERENCES candidates (candidate_id),
  trajectory_hash BYTES NOT NULL,
  policy_version STRING NOT NULL,
  prompt_hash BYTES NOT NULL,
  route STRING NOT NULL,
  served_model STRING NOT NULL,
  output_json JSONB NOT NULL,
  output_hash BYTES NOT NULL,
  retry_count INT8 NOT NULL CHECK (retry_count >= 0),
  timeout_ms INT8 NOT NULL CHECK (timeout_ms > 0),
  dissent_json JSONB NOT NULL,
  receipt_hash BYTES NOT NULL,
  advisory_verdict STRING NOT NULL CHECK (advisory_verdict = 'ADVISORY'),
  result_json JSONB NOT NULL,
  result_hash BYTES NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  UNIQUE (candidate_id, lane_id),
  UNIQUE (candidate_id, result_hash)
);

CREATE INDEX IF NOT EXISTS p5_results_candidate_lane
  ON p5_lane_results (candidate_id, lane_id);
