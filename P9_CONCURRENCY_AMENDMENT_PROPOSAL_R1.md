# P9 Lambda Concurrency Amendment Proposal R1

- `UTC`: `2026-07-26T19:11:59Z`
- `STATUS`: `PROPOSED_NOT_ACTIVE`
- `REASON`: `AWS_APPLIED_CONCURRENCY_QUOTA_10`
- `CURRENT_DEPLOYMENT_MANIFEST_SHA256`: `f2337df1010ea5afcee737515d198a6ebae0485d1e5a17cb66667732af8df82f`

## Contradiction

The offline contract specifies reserved concurrency 1. The authenticated AWS
Service Quotas page shows an applied account-level concurrent-executions quota
of 10 in `us-west-2`. AWS documentation requires at least 100 executions to
remain unreserved. Therefore a nonzero per-function reserved concurrency cannot
be configured in this account. Applying the old manifest would fail.

## Smallest safe amendment

Replace only the concurrency control:

- `reserved_concurrency`: from `1` to `null` / not configured;
- `effective_account_concurrency_ceiling`: `10`, read back from Service Quotas;
- `max_coordinator_in_flight`: `1`;
- `max_invocations`: unchanged at `1,000`;
- `provisioned_concurrency`: unchanged at `0`;
- function URL, event sources, public policy, async destinations, and triggers:
  all forbidden;
- invocation authority: exact project function only, from the authenticated
  project operator/coordinator path;
- handler timeout: unchanged at 3 seconds;
- memory: unchanged at 128 MiB;
- CloudWatch log retention: unchanged at one day;
- campaign counter and request IDs: locally bounded, hash-bound, idempotent,
  and fail closed after 1,000 attempted invocations.

The account quota of 10 is a finite provider-enforced upper bound. The
coordinator permits only one request in flight, while the absence of public
URLs, triggers, event sources, and cross-account invocation removes an
untrusted traffic path. The handler still has no network client and no verdict
authority.

## Rejection conditions

The amendment is invalid if:

- the applied account quota changes above 10 without a new packet;
- any public endpoint, trigger, event source, async destination, or wildcard
  invoke policy is added;
- coordinator serialization or the 1,000-invocation campaign counter is absent;
- the function can invoke another service or access a network client;
- the live IAM simulation does not match the exact role/function/log resources;
- cost cannot be bounded below the existing `$5.00` ceiling;
- an independent judge does not return GREEN over the exact pre-mutation packet
  hash.

No cloud mutation may occur from this proposal alone.
