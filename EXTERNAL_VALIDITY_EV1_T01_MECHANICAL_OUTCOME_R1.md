# EV1-T01 Mechanical Outcome R1

- `STATUS`: `INFRASTRUCTURE_INVALID_PRESERVED; OPERATOR_OBSERVATIONS_REQUIRED`
- `TASK_ID`: `EV1-T01`
- `UTC_RECORDED`: `2026-07-30T15:06:40Z`
- `PRODUCT_VERDICT`: `PROMOTE`
- `PRODUCT_REASON`: `MAX_PROVEN_PREFIX`
- `FRESH_CONTEXT`: `FRESH_CONTEXT_PASS`
- `RECOVERY_LOG_SHA256`: `66313857e46c7a33c5b86a542e4ca275c5379a9e6b8a34891b09e4a2e1912615`
- `RESTORED_PAGE_SHA256`: `4e58758472be64bb40458e4f201340d8ef98b7c848dc5ae7cd3323145cbc643e`
- `RESTORED_VERIFIER_SHA256`: `ef03dd17029435a469b80cb683ce6f2d5c64b2454940863e9ff78abeab6aa431`
- `STANDALONE_RESTORED_VERIFIER`: `EXIT_0; TAGLINE_SEMANTIC_AND_UNIQUE`
- `STANDALONE_VERIFIER_LOG_SHA256`: `823994e1443f06d130d5b7475572a36f790c685f8f4e04d91508487dd6ae55b3`
- `FROZEN_FULL_ACCEPTANCE`: `NOT_GREEN`
- `FIRST_FAILED_COMMAND`: `npm run typecheck`
- `TYPECHECK_FAILURE_LOG_SHA256`: `f0255770ab810ed0cc911c7998c88c75d6cf3805508fe8660bfa8874bfc0ac7d`
- `FAILURE_CLASS`: `INFRASTRUCTURE_INVALID_DEPENDENCY_LAYOUT`
- `FAILURE_MECHANISM`: `The preserved node_modules tree was moved outside the temporary successor's Node/TypeScript module-resolution ancestry. TypeScript therefore could not resolve next, react, or their types. No recovered source file differed from the declared hashes.`
- `FAILURE_RECEIPT_FILE_SHA256`: `cd6b2b093f09e87ce4390e084ba26b622035451421e4a137e892da98c574f011`
- `FAILURE_RECEIPT_INTERNAL_SHA256`: `a52f1d199ed74af7397998512aeec29b5f25151ce7af31e4de747421b09c4261`
- `BLOCKED_SNAPSHOT_FILE_SHA256`: `e37c65e5d9b5b858bc75868ea2cf0f01301a9861e76a003b8f99d9500a9b57b5`
- `BLOCKED_SNAPSHOT_INTERNAL_SHA256`: `49f3eb2da4d2ed31bf53a4e791a72a74537f5a7c655e25b772c223a79f0aaca5`
- `ORIGINAL_WORKSPACE_ABSENT`: `TRUE`
- `AUTHORITATIVE_CAPTURE_UNCHANGED`: `TRUE`
- `EXECUTION_REPRESENTATION_UNCHANGED`: `TRUE`
- `TASK_PROCESS_RESIDUE`: `0`
- `PRODUCT_CANDIDATE_CHANGED`: `FALSE`
- `SOURCE_EDIT_AFTER_RECOVERY`: `FALSE`
- `SECOND_RECOVERY_ATTEMPTED`: `FALSE`
- `TASK_COUNTED_AS_EVALUABLE_PASS`: `FALSE`
- `TEMPORARY_SUCCESSOR_TEARDOWN`: `GREEN; EXTERNAL_VALIDITY_EV1_T01_TEARDOWN_RECEIPT_R1.md; FILE_SHA256 6a5e724aceb634a5fa0b79b489850f17dfcd0794aaf8c9f25a8d21a417268dce`

The product recovered both declared work units byte-for-byte through the
one-use warrant and fresh-process path. The frozen three-command acceptance
sequence did not pass because the evidence runner placed dependencies outside
the successor's module-resolution ancestry. This result remains
infrastructure-invalid and non-scoring. It is not relabeled as product GREEN,
and no post-outcome recovery rerun or source change is authorized.

Kenneth's two operator observations were confirmed and preserved separately.
Independent direct GLM 5.2 review supported the conservative classification.
The exact temporary successor was then torn down with zero related processes,
zero root residue, and intact project-local snapshot custody.
