# P9 AWS Failed Lifecycle Receipt R2

- `RESULT`: `KILLED`
- `BLOCKER`: `LOG_STREAM_EVENTUAL_CONSISTENCY`
- `REGION`: `us-west-2`
- `FUNCTION`: `ck-p9-evaluator`
- `ROLE`: `ck-p9-lambda-exec`
- `LOG_GROUP`: `/aws/lambda/ck-p9-evaluator`
- `ALARM`: `ck-p9-invocations-1000`
- `PACKAGE_SHA256`: `29c1140b36c55aa7899f31866237ba91d0d02938f9af86079bee21f0cd6df220`
- `RAW_ARCHIVE_SHA256`: `9550cdea924586947419f8b0959a4c590bfb619e6c7f7f1fa0f32cb743529ca9`
- `EVIDENCE_DIRECTORY`: `evidence/p9-aws-failed-lifecycle-r2/`

## Passed evidence

- the corrected exact-log-group IAM resource returned `allowed` for
  `logs:CreateLogStream` and `logs:PutLogEvents`;
- every forbidden simulated action returned `implicitDeny`;
- function configuration, zero URL/trigger/provisioned/resource-policy state,
  one-day retention, alarm threshold, and role-policy inventory matched the
  contract;
- two sequential live invocations returned HTTP 200 without `FunctionError`;
- both response files were byte-identical, 618 bytes, and SHA-256
  `a6f2546b76632e3736646275e3595852c3da268cc9a25cad4ba408cae30d2f6c`;
- the validated response was `ADVISORY`, contained only
  `EVALUATION_COMPLETE`, and carried record hash
  `abac3494602f1f01c2fe99766422945ce207c368ded0f0febc66fd294525bb1a`;
- the synthetic request was 625 bytes and SHA-256
  `2c401701b6b8bd6d33409c410f310722c5b96827a81a3540b1a455d8fcec2452`.

## Kill line and teardown

The script checked for a log stream immediately after the second invocation.
CloudWatch had not yet exposed the stream, so the zero-count test triggered the
failure trap. This is an eventual-consistency observation defect, not a Lambda
or IAM failure. The exact alarm, function, role/policy, and log group were
deleted. Post-rollback inventory proved role and function absent and exact log
group and alarm counts both zero.

Raw evidence contains synthetic request/response and sanitized configuration
only. Gitleaks and detect-secrets both reported zero findings.
