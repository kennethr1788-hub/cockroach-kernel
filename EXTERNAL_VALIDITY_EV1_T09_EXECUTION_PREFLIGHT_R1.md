# EV1-T09 Guarded Execution Preflight R1

- `STATUS`: `EV1_T09_EXECUTION_PREFLIGHT_GREEN_DELETION_NOT_STARTED`
- `TASK_ID`: `EV1-T09`
- `UTC_RECORDED`: `2026-07-30T22:02:13Z`
- `RUNNER_SHA256`: `8dbc406d8760315c202ee01d10660c345465646dc38f40d52f49935aa172a6d6`
- `CAPTURE_FILE_SHA256`: `7dd764814845659a757d34ee89ee567ff2951a4e170f2903862379c2564e5d6f`
- `CAPTURE_RECEIPT_SHA256`: `131bc484b34d5fe95b213d7f7eb0015cbd19bc4cafddff12a208c249b355297a`
- `LOCAL_PREFLIGHT_FILE_SHA256`: `da9ddb2d8951c6d4d4f9d16a4baf2e8ddff33a60fb99b1e1bd1d90e214e8b168`
- `LOCAL_PREFLIGHT_RECEIPT_SHA256`: `f0afea5e9be7014232d050fd9cc8f1765447a023f4388aab837164051e996408`
- `REVIEW_CONTENT_SHA256`: `3e8bea049a0197eb3757526e2208e543fd9847a55bf2cf66cbcc5a9a44d6ca3d`
- `PACKET_SHA256`: `341a54c7528213f76896237b2387dd1dfdf2845fb472ebac2929a7fdea1b6f50`
- `GLM_5_2_VERDICT`: `GREEN; RECUSAL_CLEAR; NO_BLOCKERS; NO_EVIDENCE_GAPS`
- `AGY_VERDICT`: `GREEN; RECUSAL_CLEAR; NO_BLOCKERS; NO_EVIDENCE_GAPS`
- `EDIT_CLASSIFICATION`: `MODEL_ASSISTED`
- `INDEPENDENT_HUMAN_EDIT_CLAIM`: `PERMANENTLY_EXCLUDED_FOR_EV1_T09`
- `ORIGINAL_PRESENT`: `TRUE`
- `EXECUTION_ROOT_PRESENT`: `FALSE`
- `DELETION_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`

## Independent results

- GLM R1 was an invalid no-verdict transport response and remains preserved
  byte-exact at SHA-256
  `fe590c1b1c98947e0c4331ea877ef623c98a631974c0775f7ac9031d03b816b1`.
- GLM R2 returned substantive GREEN from served model `glm-5.2`, with recusal
  clear, no blockers, and no evidence gaps over review-content SHA-256
  `3e8bea049a0197eb3757526e2208e543fd9847a55bf2cf66cbcc5a9a44d6ca3d`.
  Its output remains byte-exact at SHA-256
  `e05b962186fadbef8d5657065f0bbd1b0c071b689443f45e729d936ded15883b`.
  The local validator initially rejected its underscore-separated hash label;
  both parser-repair commits are preserved and no GLM result was rewritten.
- AGY returned GREEN, recusal clear, no blockers, and no evidence gaps over the
  same packet SHA-256. Its provider-bound output SHA-256 is
  `933556521848d8dccd29b0d7a175c4c4475b9913a3e930cfa92e710a62d147a6`.

Kenneth's exact-state declaration is recorded. Capture and local preflight are
GREEN. The original workspace still contains only the declared modified and
untracked task state, the execution root is absent, and both independent judges
are GREEN over one frozen packet. The one authorized guarded execution may
begin. No second execution is authorized. T09 cannot support an independently
human-edited evidence claim.
