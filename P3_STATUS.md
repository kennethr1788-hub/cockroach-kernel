# P3 Durable Trajectory and Evidence Ledger

**Status:** `CK_P3_LEDGER_GREEN`
**Parent gate:** `CK_P2_CLEANROOM_GREEN`
**Implementation commit:** `ad87584`
**Started/completed UTC:** `2026-07-25T20:46:11Z`
**Judge receipt UTC:** `2026-07-25T20:49:18Z`

The standard-library ledger primitives, CockroachDB migration, deterministic
verdict vectors, retry/idempotency checks, explicit CockroachDB reconstruction
query, and evidence
budget accounting are implemented. Two fresh-root integration trials passed
with matching results. The gate is closed by the independent GLM `GREEN`
receipt in `P3_JUDGE_RECEIPT.md`.

No P4, S1, AWS, RunPod, or release work was performed.
