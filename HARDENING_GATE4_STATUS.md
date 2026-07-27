# Hardening Gate 4 Status

- `STATUS`: `HARDENING_4_BASELINE_PROTOCOL_R2_GREEN`
- `LAST_GREEN_GATE`: `HARDENING_4_BASELINE_PROTOCOL_R2_GREEN`
- `NEXT_TARGET`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `PARENT_GATE`: `HARDENING_3_REAL_WORKFLOW_GREEN`
- `QUALIFIED_METHODS`: `ORDINARY_GIT; GIT_PLUS_RESTIC_0_19_0; PRODUCT`
- `PROTOCOL_R1_SHA256`: `12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`
- `PROTOCOL_R2_SHA256`: `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`
- `RESEARCH_RECEIPT_SHA256`: `35536d9b7f3b43313e70672ac887c93b35eb38c7c73ef4f8f6e91eb89d7b2223`
- `FINAL_PACKET_SHA256`: `41efeb9270b76a0d4e1f711d5b1ab3270ecd92d32eccce93f07bef8a6ba036c0`
- `GLM_JUDGE`: `GLM_5_2_GREEN`
- `GLM_RAW_SHA256`: `aeb7368a182fd1ad4cdfc615e0e31828c1ec80a1e36418ca585b9c1b5d6cc644`
- `CLAUDE_JUDGE`: `CLAUDE_OPUS_4_8_GREEN_RECUSAL_CLEAR`
- `CLAUDE_RAW_SHA256`: `120f440b93e0ed0557910bda585bf2958dad5d12a377acb145cdd704766907b4`
- `BLOCKERS`: `none`
- `UTC_RECORDED`: `2026-07-27T22:57:33Z`

R2 incorporates the original fair-comparison protocol by hash and corrects
only platform-stable source bytes, runtime-attested tool provenance, the exact
Darwin/Linux Restic allowlist, and canonical preflight/measured evidence modes.
The protocol gives ordinary Git a durable bare remote, gives the conventional
Git-plus-Restic comparator a completed full-workspace snapshot at every common
checkpoint, gives all methods equal source/event/loss/test information and a
180-second recovery budget, separates unsupported capabilities from actual
failures, and forbids a composite winner score. Both required independent
families returned GREEN over the same exact packet hash.

Gate 5 R2 implements and freezes the corrected generator, scorer, adapters,
provenance, evidence-mode validation, isolation, receipt validation, and local
paired smoke before any benchmark or RunPod action.

This status does not claim Gate 5, a completed benchmark, a product win, a
baseline loss, any new RunPod worker, S3-R2, release, or submission readiness.
