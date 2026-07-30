# EV1-T04 Guarded Execution Preflight R1

- `STATUS`: `EV1_T04_EXECUTION_PREFLIGHT_GREEN_DELETION_NOT_STARTED`
- `TASK_ID`: `EV1-T04`
- `UTC_RECORDED`: `2026-07-30T18:22:55Z`
- `RUNNER_SHA256`: `adf276cab76dc77e76e81fa5a33573c23d6192a5f719ee0ac1df96c882eca1fc`
- `CAPTURE_FILE_SHA256`: `8ce860815d1cb92f0701f59c96833bae6708aa14e5fc06cb82f4894bf489ba42`
- `CAPTURE_RECEIPT_SHA256`: `4b3264fc0d1e2c226a50409f831f7f2d5c9da8d7f0b8665f256c676065b0a23a`
- `LOCAL_PREFLIGHT_FILE_SHA256`: `a5793f59f83d3ba87d0a30590ce93e4208f2a66b15af2e1d96475f7a91cce81f`
- `LOCAL_PREFLIGHT_RECEIPT_SHA256`: `fc55a6a8754866011f77b45a9617e50526587dbd0b32dc9d96496cfc42a78add`
- `REVIEW_CONTENT_SHA256`: `932631487196807044f631270376219e00918394fcb320ea1c18c40ba87491a4`
- `PACKET_SHA256`: `4b7b673f43467eb85eb088bbfa3e5f72027fccc0ee10d4140f9051ed487081d6`
- `GLM_5_2_VERDICT`: `GREEN; RECUSAL_CLEAR; NO_BLOCKERS; NO_EVIDENCE_GAPS`
- `AGY_VERDICT`: `GREEN; RECUSAL_CLEAR; NO_BLOCKERS; NO_EVIDENCE_GAPS`
- `DELETION_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`

## Independent results

- GLM raw SHA-256: `21b704a952af7fa9dc6236fb80eabd450510826bf9661c3010becd01f7a03e89`.
  Direct transport reported `glm-5.2`; its verdict bound review-content SHA-256
  `932631487196807044f631270376219e00918394fcb320ea1c18c40ba87491a4`.
- AGY raw SHA-256: `3124a09e4e5eaa9f3bdbe6aef23e1310750438238de721333e9b9a108bdf606c`.
  The validated wrapper bound packet SHA-256
  `4b7b673f43467eb85eb088bbfa3e5f72027fccc0ee10d4140f9051ed487081d6`.

The exact-state declaration is recorded, capture is complete, the product and
dependency-topology canaries are green, the outbound packet's direct private
marker scan and gitleaks scan are clean, and both required independent lanes are
green over the same frozen packet. The one authorized guarded execution may
begin. No second execution is authorized.
