# P9 AWS Failed Lifecycle Receipt R1

- `UTC_WINDOW`: `2026-07-26T19:33Z` through `2026-07-26T19:38Z`
- `REGION`: `us-west-2`
- `FUNCTION`: `ck-p9-evaluator`
- `ROLE`: `ck-p9-lambda-exec`
- `LOG_GROUP`: `/aws/lambda/ck-p9-evaluator`
- `ALARM`: `ck-p9-invocations-1000`
- `PACKAGE_SHA256`: `29c1140b36c55aa7899f31866237ba91d0d02938f9af86079bee21f0cd6df220`
- `RESULT`: `KILLED`
- `BLOCKER`: `IAM_SIMULATION_RESOURCE_MISMATCH`

## What passed before the kill line

- Lambda became `Active` on Python 3.12 with handler
  `lambda_handler.lambda_handler`, 128 MiB memory, and a three-second timeout.
- Reserved concurrency was unset; provisioned concurrency, function URLs,
  event-source mappings, and resource policy counts were zero.
- The exact log group had one-day retention.
- The exact alarm had threshold 1,000, one 3,600-second evaluation period, and
  `notBreaching` missing-data handling.
- The role had zero attached managed policies and one inline project policy.

## Failure and rollback

The role simulation returned `implicitDeny` for the two required log actions
because the reviewed `:log-stream:*` policy ARN did not match AWS's effective
log-group resource representation. No Lambda invocation occurred. The failure
trap deleted the alarm, function, inline policy, role, and log group.

Post-rollback inventory:

- role absent: `true`;
- function absent: `true`;
- exact log-group count: `0`;
- exact alarm count: `0`.

No account identifier, ARN, credential, token, password, or secret is stored in
this receipt.
