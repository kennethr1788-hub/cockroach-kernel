# P9 AWS Live Receipt R1

- `RESULT`: `GREEN_THROUGH_MCP_HUMAN_GATE`
- `REGION`: `us-west-2`
- `FUNCTION`: `ck-p9-evaluator`
- `ROLE`: `ck-p9-lambda-exec`
- `LOG_GROUP`: `/aws/lambda/ck-p9-evaluator`
- `ALARM`: `ck-p9-invocations-1000`
- `PACKAGE_SHA256`: `29c1140b36c55aa7899f31866237ba91d0d02938f9af86079bee21f0cd6df220`
- `EVIDENCE_ARCHIVE_SHA256`: `68d7288acca74494f63d37db27d14a5073dd9ebebfef51cd708c874f082fcf6c`
- `EVIDENCE_DIRECTORY`: `evidence/p9-aws-live-green/`
- `UTC_RECORDED`: `2026-07-26T19:51:00Z`

## Configuration readback

- Python runtime: `python3.12`;
- handler: `lambda_handler.lambda_handler`;
- memory: 128 MiB;
- timeout: three seconds;
- function state: `Active`;
- last update: `Successful`;
- reserved concurrency: unset;
- provisioned concurrency count: zero;
- function URL count: zero;
- event-source mapping count: zero;
- resource policy: absent;
- exact log-group retention: one day;
- exact alarm: 1,000 invocations, one 3,600-second period,
  `notBreaching` missing-data treatment;
- attached managed policies: zero;
- inline policies: only `ck-p9-log-streams`.

## IAM and live behavior

- `logs:CreateLogStream` and `logs:PutLogEvents` on the exact project log-group
  stream suffix both simulated as `allowed`;
- `logs:CreateLogGroup`, `lambda:InvokeFunction`, `s3:GetObject`,
  `secretsmanager:GetSecretValue`, `dynamodb:GetItem`, and `iam:PassRole`
  all simulated as `implicitDeny`;
- two sequential invocations returned HTTP 200 with no `FunctionError`;
- both canonical responses were byte-identical, 618 bytes, and SHA-256
  `a6f2546b76632e3736646275e3595852c3da268cc9a25cad4ba408cae30d2f6c`;
- response status was `ADVISORY`, the only observation was
  `EVALUATION_COMPLETE`, and the response record hash was
  `abac3494602f1f01c2fe99766422945ce207c368ded0f0febc66fd294525bb1a`;
- the synthetic request was 625 bytes and SHA-256
  `2c401701b6b8bd6d33409c410f310722c5b96827a81a3540b1a455d8fcec2452`;
- the bounded consistency poll observed one stream in the exact log group.

## Preservation and remaining gate

The exact role, function, log group, and alarm are preserved through S3 as
authorized. No URL, trigger, public policy, event source, secret, VPC, layer,
database credential, or network client was created. No RunPod resource exists.

P9 is not GREEN. CockroachDB Managed MCP still requires Kenneth's human OAuth
approval restricted to read-only access on only `cockroach-kernel`. Final live
MCP queries, cleanup/readback, frozen packet, GLM review, and AGY review remain.

Gitleaks and detect-secrets reported zero findings across the imported evidence.
No account identifier, ARN, credential, token, cookie, password, or MFA value is
stored in the project evidence.
