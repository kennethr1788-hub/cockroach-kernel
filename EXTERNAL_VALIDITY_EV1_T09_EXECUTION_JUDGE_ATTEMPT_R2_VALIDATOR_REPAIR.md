# EV1-T09 Execution Judge Attempt R2 Validator Repair

- `STATUS`: `VALID_GREEN_OUTPUT_REJECTED_BY_LOCAL_VALIDATOR`
- `PACKET_SHA256`: `341a54c7528213f76896237b2387dd1dfdf2845fb472ebac2929a7fdea1b6f50`
- `REVIEW_CONTENT_SHA256`: `3e8bea049a0197eb3757526e2208e543fd9847a55bf2cf66cbcc5a9a44d6ca3d`
- `JUDGE_ROUTE`: `DIRECT_GLM_5_2`
- `SERVED_MODEL`: `glm-5.2`
- `GLM_RAW_SHA256`: `e05b962186fadbef8d5657065f0bbd1b0c071b689443f45e729d936ded15883b`
- `GLM_VERDICT`: `GREEN`
- `RECUSAL_STATUS`: `NOT_RECUSED`
- `BLOCKERS`: `NONE`
- `EVIDENCE_GAPS`: `NONE`
- `AGY_INVOKED_BEFORE_REPAIR`: `FALSE`
- `PACKET_CHANGED`: `FALSE`
- `DELETION_STARTED`: `FALSE`

The local validator expected a space or hyphen between `REVIEW` and `CONTENT`,
and initially still expected whitespace before `SHA-256`, while the valid GLM
response used `REVIEW_CONTENT_SHA-256`. The completed repair permits underscore
separators in both positions, binds the preserved R2 output by SHA-256, and
resumes at AGY without rerunning or rewriting the GLM result. The incomplete
first parser edit is preserved in commit
`7eec77bbad56aa51882304eac6c143dfabe96d78`. No product, packet, task,
threshold, evidence, or verdict content changed.
