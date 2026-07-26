# P9 Offline Implementation Contract R1

- `STATUS`: `FROZEN_FOR_OFFLINE_IMPLEMENTATION_ONLY`
- `LIVE_P9_STATUS`: `BLOCKED`
- `LIVE_BLOCKER`: `AWS_ACCOUNT_SETUP_HUMAN_GATE`
- `LAST_GREEN_GATE`: `CK_P8_GOLDEN_GREEN`
- `PARENT_COMMIT`: `bd1e8160912f28cf009d99d0554c1eab34cbfb24`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `AUTHORIZATION_SHA256`: `cb46e382f98d9a4d52a882a3d35f1b0ae4db9047e07f713d2212196dc3204214`

This contract freezes the local implementation surface while AWS activation is
pending. It does not authorize external mutation and is not the final P9
pre-mutation or final judge packet.

## Fixed vertical slice

The implementation must preserve the exact order declared in the P9 execution
prompt: synthetic task, CockroachDB event/receipt transaction, bounded vector
retrieval, Lambda evaluation, strict response validation, CockroachDB result
transaction, sinkless changefeed projection, read-only Managed MCP query,
tampered successor, local deterministic verdict, declared session loss,
maximum-provable continuation, and fresh-context resume.

Cloud, broker, MCP, vector, and model outputs remain untrusted evidence. Only
the existing local verifier and recovery machinery can produce `PROMOTE`,
`REFUSE`, or `INVALID`.

## Region and resource contract

- AWS region: `us-west-2`.
- CockroachDB region: `us-west-2`.
- Database: `cockroach_kernel`.
- Runtime SQL user: `ck_runtime`; no ownership, admin, role creation, cluster
  setting, user creation, or unrelated database access.
- Migration identity: a separately bounded owner session used only for frozen
  schema/grant application; never packaged or retained in runtime config.
- Lambda function: `ck-p9-evaluator`.
- Lambda execution role: `ck-p9-lambda-exec`.
- Lambda memory: 128 MiB.
- Lambda timeout: 3 seconds.
- Reserved concurrency: 1.
- Provisioned concurrency: forbidden.
- Function URL: forbidden.
- Network calls from Lambda: forbidden.
- Lambda log group: `/aws/lambda/ck-p9-evaluator`, one-day retention.
- Maximum combined P9/S3 invocations: 1,000.
- Maximum request and response: 16 KiB each.
- Maximum observations per response: 16.
- Maximum observation text: 256 UTF-8 bytes.
- CloudWatch invocation alarm threshold: 1,000 during the bounded campaign;
  creation is conditional on current price remaining inside the $5 envelope.

All live identifiers are re-read before mutation and recorded only in a
sanitized form that cannot expose account or credential material.

## Lambda authority contract

The Lambda handler is a pure, standard-library evaluator. It accepts one exact
canonical JSON schema with:

- `version`, `request_id`, `task_id`, `candidate_id`;
- `trajectory_hash`, `candidate_hash`, `policy_hash`;
- a bounded `features` object containing declared numeric/boolean evidence;
- `request_hash` over the body without `request_hash`.

It returns:

- `version`, `request_id`, `candidate_id`;
- echoed input hashes;
- `status: ADVISORY`;
- bounded structured observations with stable codes;
- `response_hash` over the body without `response_hash`.

It may not return a promotion/refusal decision, mutate policy, execute code,
invoke another agent/service, choose a resource, read a credential, or perform
network I/O. Unknown fields, wrong types, stale hashes, oversized values, and
non-canonical input fail closed.

## CockroachDB schema contract

All application objects live in database `cockroach_kernel`, schema `ck`:

- `tasks`: declared synthetic task and declared-state hash;
- `trajectory_events`: ordered event chain with parent and state hashes;
- `receipts`: immutable canonical receipt bytes and SHA-256;
- `context_vectors`: authoritative event linkage plus `VECTOR(64)` deterministic
  context vector and a CockroachDB vector index;
- `worker_results`: Lambda request/response hashes, stable provenance, retry
  lineage, and canonical result bytes;
- `projection_events`: bounded downstream changefeed projection with exact
  authoritative-row and receipt linkage;
- `mcp_receipt_view`: minimal query surface exposing only synthetic IDs, stable
  hashes, status, and linkage—never payloads or credentials.

Every write is parameterized and uses CockroachDB serializable retry handling.
Duplicate request IDs are idempotent. Immutable tables reject update/delete
for the runtime role. Changefeed output cannot write back.

The deterministic 64-dimensional context vector is produced locally from a
bounded token-feature hash projection. It is reproducible and keyless. It is
described honestly as deterministic context retrieval, not as a neural model
embedding or proof of semantic understanding.

## Managed MCP contract

- OAuth only; no API key or service-account secret for this build.
- Human authorization must grant read permission only and deny write.
- Connection must be restricted to cluster `cockroach-kernel`.
- Allowed SQL shape: one bounded `SELECT` against `ck.mcp_receipt_view` by
  declared synthetic task ID with a finite limit.
- No DDL, DML, comments-as-commands, dynamic SQL, arbitrary schema access,
  multi-statement query, or model-selected query.
- Preserve the visible authorization scope, query result hash, and available
  audit trace. If the service cannot prove read-only scope and audit linkage,
  Managed MCP is not counted and P9 is blocked.

## Credential and egress contract

- No credential is printed, copied to a prompt, passed on a command line,
  committed, packaged, uploaded, or transferred to RunPod.
- CockroachDB CA certificate is downloaded to a project-local ignored runtime
  directory and hash-verified; never `$HOME/.postgresql`.
- Runtime password may be retrieved from macOS Keychain only into a child
  process environment and must never enter logs or evidence.
- AWS operations use the visible authenticated console/CloudShell session; no
  long-lived access key is created.
- A CloudShell session requiring CockroachDB authentication must use a human
  hidden-input prompt. No script may echo, persist, or upload the value.
- Allowed external destinations after the live gate: the declared CockroachDB
  SQL endpoint, CockroachDB Managed MCP, and AWS Lambda control/invocation
  endpoints in `us-west-2` only.
- Local mock/replay performs no network I/O.

## Cost, retention, rollback, and cleanup

- Aggregate incremental AWS cost remains at or below $5.
- CockroachDB paid-plan changes, resource-limit increases, and billing changes
  are forbidden.
- P9 test rows are synthetic, namespaced by campaign, and preserved only until
  the P9 evidence packet is frozen; cleanup is an explicit transaction.
- Sinkless changefeeds are canceled by closing the client; no persistent sink
  or job is allowed for the offline or P9 proof path.
- Lambda code/config is preserved through S3 only after exact inventory and
  idle-cost verification; all temporary roles, alarms, logs, and rows receive
  a preserve/delete classification.
- Rollback deletes only exact project resources after identity readback.
- Any wildcard IAM action/resource, cross-account reference, public endpoint,
  unknown price, paid upgrade, credential prompt to a model, or teardown
  ambiguity blocks execution.

## Local acceptance tests

Required offline tests include:

1. two clean local vertical-slice mock/replay trials;
2. strict Lambda request/response schema and canonical hash tests;
3. unknown/oversized/malformed/stale/duplicate/timeout/throttle cases;
4. SQLSTATE 40001 retry and bounded exhaustion;
5. duplicate request/event idempotency;
6. deterministic context-vector equality and vector empty/stale/namespace
   cases against disposable CockroachDB v26.2;
7. sinkless changefeed duplicate, restart, lag, and no-write-back behavior in a
   disposable local cluster;
8. MCP write/DDL/multi-statement/unknown-field/oversized-result refusals in the
   local mock;
9. Lambda handler network-denial assertion and forbidden-import scan;
10. IAM policy negative tests, cost bound, retention, teardown, secret scan,
    private-path scan, and clean-root residue scan.

Offline completion may produce only `P9_OFFLINE_RUNWAY_READY`. It cannot produce
`CK_P9_INTEGRATION_GREEN`.

