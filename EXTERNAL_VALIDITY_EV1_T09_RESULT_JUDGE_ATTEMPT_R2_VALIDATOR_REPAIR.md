# EV1-T09 Result Judge Attempt R2 Validator Repair

- `STATUS`: `VALID_GREEN_OUTPUT_REJECTED_BY_LOCAL_VALIDATOR`
- `PACKET_SHA256`: `90a21e73653d37f48e6802458e8a6808a792c46ce548cf27bc2acb9ec3b2cc69`
- `REVIEW_CONTENT_SHA256`: `a2ad10b073ff7b800127ce9c078404d876d0e55cf07e3566858cb672e9489e27`
- `JUDGE_ROUTE`: `DIRECT_GLM_5_2`
- `SERVED_MODEL`: `glm-5.2`
- `GLM_RAW_SHA256`: `5809ced5e7a484124bd24acbfa5b218d8e38eaeaa0c29051228942babe8d5b75`
- `GLM_VERDICT`: `GREEN`
- `OBSERVATION_1_EVIDENCE`: `SUPPORTED`
- `OBSERVATION_2_EVIDENCE`: `SUPPORTED`
- `CLASSIFICATION_EVIDENCE`: `SUPPORTED`
- `RECUSAL`: `NONE`
- `BLOCKERS`: `NONE`
- `PACKET_CHANGED`: `FALSE`
- `TEARDOWN_STARTED`: `FALSE`

The R2 output explicitly supports both observations and the model-assisted,
non-independent-human-edit classification. The local validator nevertheless
required the phrase `model-assisted` to precede the exclusion phrase. GLM used
structured `independent_human_edit:false` and `PERMANENTLY_EXCLUDED` evidence,
then stated `model-assisted` elsewhere. The repaired validator accepts either
ordering within bounded context and binds the preserved R2 bytes by SHA-256.
No packet, evidence, verdict, product, threshold, or judge output changed.
