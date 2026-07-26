You are a bounded no-tool coding consultant. Return a concise structured design
artifact, not a patch and not implementation instructions outside the fixed
scope below.

Design a typed configuration and least-privilege boundary for a synthetic
Python 3.12 developer-tool integration with these fixed facts:

- one AWS Lambda evaluator in us-west-2, 128 MiB, three-second timeout,
  reserved concurrency one, no provisioned concurrency, no function URL, no
  network calls, maximum 1,000 invocations;
- one CockroachDB Basic v26.2 cluster in us-west-2;
- runtime SQL user restricted to one database/schema, parameterized DML,
  immutable receipts, vector retrieval, worker-result inserts, and one bounded
  sinkless changefeed; no role/user/cluster-setting/ownership authority;
- Managed MCP must be OAuth, read-only, single-cluster scoped, and limited to
  one bounded SELECT view; no API key and no writes;
- project-local CA path, no HOME paths, no credential in source/config/logs;
- AWS Console or CloudShell authentication only, no long-lived access key;
- incremental AWS cost ceiling five dollars, one-day log retention, exact-name
  cleanup, and a keyless local replay;
- the cloud evaluator is advisory only; local deterministic code is the sole
  authority.

Return exactly these sections:

1. CONFIG_SCHEMA: field, type, allowed value/range, secret classification.
2. IAM_POLICY_MATRIX: exact allowed and explicitly forbidden actions/resources.
3. SQL_ROLE_MATRIX: exact allowed and explicitly forbidden object operations.
4. CREDENTIAL_FLOW: creation-free, non-printing, non-persistent flow.
5. COST_AND_RETENTION: finite counters, retention, preserve/delete classes.
6. ROLLBACK_AND_TEARDOWN: exact-name readback and fail-closed checks.
7. LOCAL_MOCK_CONTRACT: what a keyless clean clone can prove and cannot claim.
8. BLOCKERS: anything that cannot be proven until live account activation.

Do not include shell commands, code patches, account identifiers, credentials,
private paths, vendor secrets, deployment actions, or a GREEN verdict.

