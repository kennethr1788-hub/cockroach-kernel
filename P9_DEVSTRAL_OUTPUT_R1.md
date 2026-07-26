# P9 Devstral Output R1

## Provenance

- ROUTE: `devstral` wrapper V14.0.0
- REQUESTED_MODEL: `mistral-medium-3-5`
- SERVED_MODEL: `mistral-medium-3-5`
- LIVE_SENTINEL: `DEVSTRAL_SENTINEL_READY`
- HIGH_REASONING_ATTEMPT: `BLOCKED_EMPTY_FINAL_TEXT`
- STANDARD_REASONING_RETRY: `COMPLETE`
- AUTHORITY: advisory only; no tools, files, shell, cloud, or verdict authority

## Raw advisory output

```text
CONFIG_SCHEMA:
- field: lambda_arn, type: str, allowed: arn:aws:lambda:us-west-2:<acct>:function:eval-*, secret: none
- field: db_host, type: str, allowed: <cluster>--<id>.us-west-2.crdb.io:26257, secret: none
- field: db_name, type: str, allowed: [a-z0-9_]{1,30}, secret: none
- field: db_user, type: str, allowed: [a-z0-9_]{1,30}, secret: none
- field: db_ssl_root, type: str, allowed: /project/ca/*.crt, secret: none
- field: mcp_view, type: str, allowed: [a-z0-9_]{1,30}, secret: none
- field: log_group, type: str, allowed: /aws/lambda/eval-*, secret: none

IAM_POLICY_MATRIX:
- allowed: lambda:InvokeFunction on arn:aws:lambda:us-west-2:<acct>:function:eval-*
- allowed: logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents on /aws/lambda/eval-*
- forbidden: * on * except above

SQL_ROLE_MATRIX:
- allowed: SELECT on mcp_view
- allowed: INSERT on worker_results
- allowed: parameterized DML on receipts, vector_retrieval
- allowed: CHANGEFEED on bounded_sinkless_feed
- forbidden: CREATE, ALTER, DROP, GRANT, REVOKE, SET, SHOW on *
- forbidden: SELECT on * except mcp_view
- forbidden: INSERT, UPDATE, DELETE on * except worker_results, receipts, vector_retrieval

CREDENTIAL_FLOW:
- AWS Console/CloudShell STS AssumeRole with session token, max 1h, never printed or persisted
- CockroachDB password fetched via AWS Secrets Manager once per Lambda cold start, in-memory only

COST_AND_RETENTION:
- counters: Lambda invocations <=1000, duration <=3s, memory 128 MiB
- retention: CloudWatch logs 1 day, exact-name cleanup
- preserve: none
- delete: all resources on teardown

ROLLBACK_AND_TEARDOWN:
- exact-name readback: Lambda function name, DB cluster name, log group name
- fail-closed checks: Lambda concurrency=1, no provisioned, no function URL, no network calls, DB role restrictions

LOCAL_MOCK_CONTRACT:
- can prove: deterministic logic, SQL schema compliance, IAM policy shape, cost counters
- cannot claim: AWS account identity, real network latency, real DB performance, real MCP OAuth flow

BLOCKERS:
- live account activation required to verify AWS region, Lambda runtime, CockroachDB cluster existence, OAuth MCP endpoint reachability
```

## Codex disposition

Useful: bounded names, explicit deny posture, finite counters, exact-name teardown,
and a clean separation between local proof and live proof.

Rejected as written: the suggestion to fetch a database password from AWS Secrets
Manager creates a network call and additional service dependency that conflicts with
the frozen no-network evaluator contract. The SQL operation matrix is also too coarse
to apply directly. Codex must translate the useful constraints into exact local files;
this output is not implementation evidence.
