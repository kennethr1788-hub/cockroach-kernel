-- Collision-safe transition for clusters created before the clean schema
-- stopped treating a deterministic projection digest as global row identity.
-- The digest still binds the exact VECTOR(64) bytes. Distinct authoritative
-- events may legitimately share it; vector_id and (task_id,event_hash,namespace)
-- remain the identity/linkage constraints.

ALTER TABLE ck.context_vectors
  DROP CONSTRAINT IF EXISTS context_vectors_vector_digest_key;

CREATE INDEX IF NOT EXISTS context_vectors_vector_digest_idx
  ON ck.context_vectors (vector_digest);
