---
name: cockroach-memory-inspection
description: Read-only inspection of hash-bound CockroachDB receipt and vector snapshots.
---

# Cockroach memory inspection

Use this skill after an approved read-only CockroachDB MCP query and vector
retrieval. The adapter accepts only the bounded `ck-memory-snapshot-v1` shape
and returns a hash-bound advisory report.

## Inputs

```json
{"version":"ck-memory-snapshot-v1","receipts":[],"vectors":[]}
```

Receipt rows contain only `task_id`, `receipt_hash`, `event_hash`, and `status`.
Vector rows contain `task_id`, `event_hash`, `namespace`, `vector_digest`, and
non-negative finite `distance`.

## Output and guardrails

The implementation is `cockroach_kernel.memory_skill.inspect_snapshot`.
It reports linkage, orphan vectors, conflicting receipt identities, counts,
and a SHA-256 evidence hash. It never emits `PROMOTE`, `REFUSE`, or `INVALID`,
never writes to CockroachDB, never invokes AWS, and never selects a recovery
candidate. Any unknown field, invalid hash, oversized input, or malformed row
fails closed.

The deterministic local verifier remains the only authority for recovery.
