# Hardening Gate 6 Status

- `STATUS`: `HARDENING_6_RUN1_BLOCKED`
- `BLOCKER`: `EVIDENCE_CANDIDATE_INVALIDATED`
- `LAST_GREEN_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_GREEN`
- `CANDIDATE_IMPLEMENTATION_COMMIT`: `bd29bd23e831175aa54526b9e3c48bd04e8af3ed`
- `PREFLIGHT_PACKET_SHA256`: `f648e8433928053649ffe4e515a2fae824b2cdeb34afd3403c2fdf4f56e0aed1`
- `MEASURED_EXECUTIONS_COMPLETED`: `0`
- `RUNPOD_ATTEMPTS`: `0`
- `RUNPOD_ACTIVE_INVENTORY`: `[]`
- `COST_STATE`: `EXACT_$0.00`
- `JUDGE_STATE`: `NOT_INVOKED_MECHANICAL_PREFLIGHT_BLOCKER`
- `UTC_RECORDED`: `2026-07-27T22:04:15Z`

The frozen candidate is Darwin-bound in its Restic acceptance, Git/Restic tool
provenance, receipt limitations, and scenario executable path. The official
Linux Restic binary is present and hash-valid but is rejected by the immutable
adapter. Repair would change behaviorally relevant candidate and evidence
semantics after freeze, which the Gate 6 contract forbids.

No worker was created and no measured campaign began.
