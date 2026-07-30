# EV2 Replacement Campaign Final Judge Receipt R1

- `UTC_RECORDED`: `2026-07-30T11:58:41Z`
- `PACKET`: `EXTERNAL_VALIDITY_EV2_R2_FINAL_REVIEW_PACKET_R1.md`
- `PACKET_SHA256`: `f62463cf1f2cc7ec47f5877d1013dade4e300ab5a6d72dffaf1ee42d7cf3c8a7`
- `PACKET_COMMIT`: `03b3f068254067b042b472b394ab280d1850f9a0`
- `GLM_ROUTE`: `direct glm-zai`
- `GLM_SERVED_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RECUSAL`: `clear`
- `GLM_RAW_SHA256`: `29343d172c09c1e4e4c8a4107037514c233abc7f657787cd6cea93def0124c88`
- `GLM_STDERR_SHA256`: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`
- `AGY_ROUTE`: `agy-judge`
- `AGY_MODEL`: `Gemini 3.1 Pro (High)`
- `AGY_VERDICT`: `RECUSAL_REQUIRED`
- `AGY_RECUSAL`: `recusal_required`
- `AGY_RAW_SHA256`: `e4735534870780086138a60e16311d84554818dd293e7f0353fef7866451559f`
- `AGY_STDERR_SHA256`: `bf32ab8c082fa1aff618ee172c412b767bf7f636479cf49543749f2ba6ad30ee`
- `EV2_THRESHOLD_DECISION`: `SUPPORTED_BY_DIRECT_MECHANICAL_EVIDENCE_AND_ONE_INDEPENDENT_GREEN`
- `PROGRAM_FINAL_PANEL`: `NOT_GREEN_NOT_CLAIMED`

## GLM result

GLM bound the exact packet hash and returned `GREEN`, `RECUSAL_CHECK: clear`,
no blockers, no material evidence gaps, and no reruns. It retained bounded-scope
limitations and the absence of exact provider billing as non-blocking risks.

## AGY result

AGY bound the exact packet hash and returned `RECUSAL_REQUIRED`. Its blockers
are preserved verbatim in meaning:

1. it treated its earlier preflight verdict as material influence requiring
   recusal;
2. it found the inherited internal `campaign_id` ending in `r1` ambiguous
   against the separately preserved failed R1 attempt; and
3. it therefore considered the R2 final/teardown provenance insufficiently
   distinguished.

No packet was revised in response, no AGY result was converted to GREEN, and no
replacement judge was substituted. The campaign bytes and evidence remain
unchanged.

## Disposition

The EV2 behavior threshold itself does not require a two-judge final panel. Its
direct criteria are 24 completed executions, zero partial/duplicate/false
promotion/replay failures, passing linkage invariants, clean teardown, and
agreeing hashes. Those mechanical criteria pass, and one independent family
returned exact-hash GREEN.

The broader `EXTERNAL_VALIDITY_EVIDENCE_GREEN` gate explicitly requires GLM and
AGY after EV0 through EV3 complete. That overall gate is not claimed here. AGY's
recusal and provenance concern remain open inputs to the later composite EV4
package.
