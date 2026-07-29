-- P9 offline cloud foundation schema (P9_OFFLINE_CONTRACT_R1).
--
-- Target: database cockroach_kernel, schema ck, CockroachDB v26.2. This file
-- declares only the schema objects named in the contract: tasks,
-- trajectory_events, receipts, context_vectors, worker_results,
-- projection_events, and the mcp_receipt_view query surface. It is applied
-- inside database cockroach_kernel by the separately bounded owner session.
--
-- Deliberately absent: database creation, privilege, ownership, identity, and
-- cluster-wide statements of any kind. Runtime access boundaries for the
-- ck_runtime identity (read/write on mutable tables, insert-only posture on
-- immutable tables, no update/delete on receipts, trajectory_events, or
-- projection_events) are applied outside this file by the owner session and
-- are not part of the offline artifact.

CREATE SCHEMA IF NOT EXISTS ck;

-- Declared synthetic task and its declared-state hash, namespaced by campaign.
CREATE TABLE IF NOT EXISTS ck.tasks (
  task_id STRING PRIMARY KEY,
  campaign_id STRING NOT NULL,
  task_json JSONB NOT NULL,
  task_hash BYTES NOT NULL UNIQUE CHECK (length(task_hash) = 32),
  state_hash BYTES NOT NULL CHECK (length(state_hash) = 32)
);

-- Ordered event chain: each event binds its parent event hash and the state
-- hash after application. (task_id, sequence) is unique so replay order is
-- authoritative. Genesis events bind a declared all-zero parent hash.
CREATE TABLE IF NOT EXISTS ck.trajectory_events (
  event_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES ck.tasks (task_id),
  sequence INT8 NOT NULL CHECK (sequence >= 0),
  parent_event_hash BYTES NOT NULL CHECK (length(parent_event_hash) = 32),
  state_hash BYTES NOT NULL CHECK (length(state_hash) = 32),
  event_json JSONB NOT NULL,
  event_hash BYTES NOT NULL UNIQUE CHECK (length(event_hash) = 32),
  UNIQUE (task_id, sequence)
);

-- Immutable canonical receipt bytes and their SHA-256. receipt_hash is the
-- primary key; the event linkage is a hard reference and cannot be rewritten
-- once sealed (no update path exists for the runtime identity).
CREATE TABLE IF NOT EXISTS ck.receipts (
  receipt_hash BYTES PRIMARY KEY CHECK (length(receipt_hash) = 32),
  task_id STRING NOT NULL REFERENCES ck.tasks (task_id),
  event_hash BYTES NOT NULL REFERENCES ck.trajectory_events (event_hash),
  status STRING NOT NULL CHECK (status IN ('DECLARED', 'SEALED', 'ADVISORY')),
  receipt_json JSONB NOT NULL
);

-- Authoritative event linkage plus the deterministic VECTOR(64) context
-- projection. vector_digest binds the exact stored vector bytes and is
-- intentionally non-unique: a many-to-one projection can produce the same
-- vector for distinct authoritative events. vector_id and the unique
-- (task, event, namespace) tuple provide row identity and linkage.
CREATE TABLE IF NOT EXISTS ck.context_vectors (
  vector_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES ck.tasks (task_id),
  event_hash BYTES NOT NULL REFERENCES ck.trajectory_events (event_hash),
  namespace STRING NOT NULL,
  vector VECTOR(64) NOT NULL,
  vector_digest BYTES NOT NULL CHECK (length(vector_digest) = 32),
  UNIQUE (task_id, event_hash, namespace)
);

CREATE INDEX IF NOT EXISTS context_vectors_vector_digest_idx
  ON ck.context_vectors (vector_digest);

-- CockroachDB vector index over the deterministic context projection.
-- Requires the vector index feature available in the declared v26.2 target;
-- enabling any prerequisite feature flag is an owner-session action outside
-- this file.
CREATE VECTOR INDEX IF NOT EXISTS context_vectors_vector_idx
  ON ck.context_vectors (vector);

-- Lambda request/response hashes, stable provenance, and retry lineage.
-- request_id is the idempotency key: duplicate request IDs are replayed, not
-- re-recorded. supersedes links a successor request to the stale request it
-- replaces. result_json is the canonical ADVISORY-only result bytes; the
-- Lambda never emits a promotion, refusal, or invalid verdict.
CREATE TABLE IF NOT EXISTS ck.worker_results (
  request_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES ck.tasks (task_id),
  candidate_id STRING NOT NULL,
  request_hash BYTES NOT NULL CHECK (length(request_hash) = 32),
  response_hash BYTES NOT NULL CHECK (length(response_hash) = 32),
  attempt INT8 NOT NULL CHECK (attempt >= 1),
  supersedes STRING NULL REFERENCES ck.worker_results (request_id),
  status STRING NOT NULL CHECK (status IN ('ADVISORY', 'TIMEOUT', 'THROTTLED', 'MALFORMED', 'STALE')),
  result_json JSONB NOT NULL,
  result_hash BYTES NOT NULL UNIQUE CHECK (length(result_hash) = 32)
);

-- Bounded downstream sinkless-changefeed projection. Each row carries exact
-- authoritative-row linkage (source_table + source_key) and immutable receipt
-- linkage. Projection rows are append-only; the changefeed cannot write back
-- to the authoritative tables.
CREATE TABLE IF NOT EXISTS ck.projection_events (
  projection_id STRING PRIMARY KEY,
  source_table STRING NOT NULL CHECK (source_table IN ('tasks', 'trajectory_events', 'receipts', 'context_vectors', 'worker_results')),
  source_key STRING NOT NULL,
  receipt_hash BYTES NOT NULL REFERENCES ck.receipts (receipt_hash),
  sequence INT8 NOT NULL CHECK (sequence >= 0),
  projected_json JSONB NOT NULL,
  projection_hash BYTES NOT NULL UNIQUE CHECK (length(projection_hash) = 32),
  UNIQUE (source_table, source_key, sequence)
);

-- Minimal read-only query surface for Managed MCP: synthetic IDs, stable
-- hashes (hex-encoded), status, and event linkage only. Payload columns
-- (receipt_json and every other table) are never exposed here.
CREATE OR REPLACE VIEW ck.mcp_receipt_view AS
SELECT
  task_id,
  encode(receipt_hash, 'hex') AS receipt_hash,
  status,
  encode(event_hash, 'hex') AS event_hash
FROM ck.receipts;
