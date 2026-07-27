# Hardening Gate 2 Public Demo Authorization Packet R1

## Gate state

- `STATUS`: `HUMAN_AUTHORIZATION_REQUIRED`
- `TARGET_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `LAST_GREEN_GATE`: `HARDENING_1_CLI_GREEN`
- `LOCAL_ADAPTER_COMMIT`: `ea4d3764dc6fd778af98f23788ba9871729cd99e`
- `PUBLIC_DEPLOYMENT_PERFORMED`: `no`
- `AWS_MUTATION_PERFORMED_BY_THIS_PACKET`: `no`
- `COCKROACHDB_MUTATION_PERFORMED_BY_THIS_PACKET`: `no`
- `RUNPOD_REQUIRED`: `no`
- `AWS_SESSION_STATE`: `expired; visible project-local login required`
- `UTC_FROZEN`: `2026-07-27T16:49:36Z`

## Current rules and source snapshots

- official rules URL: `https://cockroachdb-ai.devpost.com/rules`;
- official rules SHA-256: `8b5f15ed0a313bf18e56ae0145a17b103d6ae5b240ae8b084644903edb39aeeb`;
- submission deadline: `2026-08-18 17:00 EDT`;
- judging ends: `2026-09-15 17:00 EDT` / `2026-09-15T21:00:00Z`;
- AWS Lambda pricing SHA-256:
  `761496d27478515ddb3c69284dfd657b7e5a5624fd17ebbef26b54c66e1e1cb5`;
- AWS API Gateway pricing SHA-256:
  `fcd2c02c1c8a9150be49ddd1086eec50c1672f2fd54416a27b603d15071e4e53`;
- API Gateway throttling documentation SHA-256:
  `711cd281966bbea445214d1cafea2b36f712e78ee0c167fa3463c1955bdbf580`;
- AWS Secrets Manager pricing SHA-256:
  `9e01a402556b3e5cc54370908c27845874231b613f8378cd16072bbdd452030d`;
- CockroachDB Basic planning documentation SHA-256:
  `5cf8ce1c2445d26e9e0a25a6f17e0852b98925f3487bdd9551acdc61c0f84e47`.

The current rules require a functional demo URL, free and unrestricted judge
access through the judging period, meaningful CockroachDB persistent memory,
at least two listed CockroachDB tools, and deployment on AWS. This packet does
not claim those obligations are complete.

## Exact bounded architecture

Region: `us-west-2`.

New resources:

1. one API Gateway HTTP API named `ck-hardening-demo`;
2. exactly two anonymous `GET` routes: `/demo/promote` and `/demo/refuse`;
3. one Lambda function named `ck-hardening-demo`, Python 3.12, 256 MiB,
   eight-second timeout, zero provisioned concurrency, no VPC, no layer except
   the deployment bundle, no event source, and no async destination;
4. one exact Lambda execution role with only exact log-stream writes and
   `secretsmanager:GetSecretValue` on one exact secret;
5. one secret named `ck-hardening-demo-db`, encrypted by the free AWS-managed
   Secrets Manager key, with no rotation function;
6. one separate CockroachDB SQL identity with `USAGE` on schema `ck` and
   `SELECT` only on `ck.tasks`, `ck.receipts`, `ck.context_vectors`, and
   `ck.worker_results`; no insert, update, delete, DDL, changefeed, MCP, admin,
   or ownership authority;
7. one one-day-retention log group and invocation/error alarms;
8. no custom domain, WAF, cache, S3 bucket, DynamoDB table, paid instance,
   persistent volume, or RunPod resource.

The HTTP handler accepts no request body, query parameters, user SQL, path,
code, model output, URL, tool, destination, or arbitrary identifier. API
Gateway payload format is fixed at `2.0`. The only accepted routes map to two
frozen synthetic cases.

Each successful request performs:

- one parameterized CockroachDB transaction-linkage query joining task,
  immutable receipt, deterministic vector, and advisory worker-result state;
- one task-bound distributed vector-index query whose expected distance is
  zero;
- strict hash/linkage validation;
- one five-repeat P4 deterministic-verifier check;
- a bounded canonical response showing `PROMOTE / VERIFIED` or
  `REFUSE / HASH_MISMATCH`.

CockroachDB and Lambda output remain untrusted and advisory. Only the packaged
P4 verifier selects the verdict. The Lambda is read-only with respect to
CockroachDB and never mutates a workspace.

## Local implementation and dependency boundary

- `pyproject.toml` SHA-256:
  `ca8d0a873ddfa1d628f54ef5ca989b88e087b967f7d366bca66d8b59249b6dbd`;
- HTTP adapter SHA-256:
  `5d25d417ddaefa6f8490ca5486f0a3dbd91461ce1fc3c4f8e861fc7d406e30bb`;
- HTTP adapter tests SHA-256:
  `31d927d799a9838e19bff5215b551fccfb5087b2d510ff3da4d0ee2ba2011620`;
- local CLI/HTTP tests: `12/12 PASS`;
- inherited P9 tests: `113/113 PASS`;
- inherited verifier tests: `6/6 PASS`;
- HTTP response determinism, fixed routes, memory-linkage tamper, refusal
  no-action, and sanitized dependency failures are directly tested;
- optional AWS demo dependency: `pg8000==1.31.5`, BSD-3-Clause;
- dependency smoke installed version `1.31.5` in a disposable local virtual
  environment and removed the environment afterward.

No dependency was installed globally and no HOME runtime was changed.

## Access, throttling, and denial-of-wallet boundary

- API Gateway stage target rate: `0.05 requests/second`;
- burst target: `2`;
- request body: forbidden;
- response cap: `16 KiB`;
- Lambda timeout: `8 seconds`;
- Lambda memory: `256 MiB`;
- log retention: `1 day`;
- access-preservation end: not before `2026-09-15T21:00:00Z`;
- planned teardown: after the judging-period access verification, beginning
  `2026-09-16` unless the official schedule changes;
- kill trigger: `5,000` invocations in a UTC day, a cumulative projected AWS
  charge of `$10.00`, credential/linkage failure, unexpected resource, or any
  false promotion;
- kill action: disable/delete the HTTP API first, then remove the demo Lambda,
  resource policy/integration, secret, read-only SQL identity, alarms, and log
  group after evidence retrieval.

The alarms are detection only. They do not automatically delete or disable the
endpoint. The kill decision and teardown are manual operator actions, so this
packet does not claim an automated or provider-enforced hard spend cap.

AWS explicitly describes HTTP API throttles as best-effort targets, not hard
ceilings. Therefore the `$12.00` envelope below is a permitted operational
ceiling with monitoring and a kill line, not a provider-guaranteed hard spend
cap. This residual denial-of-wallet risk requires Kenneth's informed approval.

## Cost envelope

For approximately `50.2` days from this packet freeze through the end of
judging, the `0.05 requests/second` target allows approximately `217,000`
requests before best-effort variance.

Conservative pre-free-tier estimate at that target:

- API Gateway HTTP API: about `$0.22` at `$1.00/million` requests;
- Lambda request charge: about `$0.04` at `$0.20/million` requests;
- Lambda duration upper calculation: about `$7.24` for 217,000 requests at the
  full eight-second timeout and 256 MiB using `$0.0000166667/GB-second`;
- one Secrets Manager secret: about `$0.67` prorated;
- worst-case secret API lookup on every request: about `$1.09`; warm-instance
  caching is expected to reduce this materially;
- bounded logging and small response transfer allowance: `$0.50`;
- planned AWS total below free-tier credits: about `$9.76`;
- `MAXIMUM_PERMITTED_INCREMENTAL_AWS_SPEND`: `$12.00`.

The CockroachDB path performs two bounded reads per request. At the official
typical `1-15 RU` per SELECT guidance, the full target is approximately
`0.43-6.51 million RUs`, below the advertised 50-million-RU monthly Basic
benefit. This is an estimate, not a billing guarantee.

## CockroachDB access blocker

The last verified CockroachDB free-trial expiry was `2026-08-25`, before the
judging period ends. Current Basic documentation says the recurring monthly
free resource benefit applies to pay-as-you-go organizations and that resource
limits may need to be configured. No model may accept billing terms, add a
payment method, or attest future availability for Kenneth.

Before public deployment Kenneth must confirm either:

1. the existing Basic cluster is already eligible and configured to remain
   active through `2026-09-15T21:00:00Z` within a reviewed RU/storage limit; or
2. he explicitly accepts the provider's required billing/resource-limit step.

No billing setting may be changed under this packet alone.

## Required explicit authorization

Deployment may begin only after Kenneth states all of the following in chat:

```text
I authorize the bounded Hardening Gate 2 public AWS demo described in
HARDENING_GATE2_PUBLIC_DEMO_AUTHORIZATION_PACKET_R1.md. I accept a maximum
permitted incremental AWS spend of $12.00, the documented best-effort
throttling residual risk, public anonymous access to only the two fixed GET
routes, one project-scoped Secrets Manager secret, and preservation of the
demo through 2026-09-15T21:00:00Z. I confirm the cockroach-kernel Basic cluster
is authorized and able to remain active through that time within its reviewed
resource limits. No billing-setting change is authorized unless I state it
separately. I will complete the visible project-local aws login if prompted.
```

After that statement, the visible project-local AWS login must be completed.
The implementation, IAM, SQL, cost, teardown, and same-hash independent review
gates still apply; authorization is not evidence of success.
