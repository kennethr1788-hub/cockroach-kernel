# P9 Completion Contract R1

- `STATUS`: `P9_COMPLETION_CONTRACT_FROZEN`
- `PARENT_COMMIT`: `10b1a40a48b8d0e2543a532e8e2d9d9de3036c30`
- `LAST_GREEN_GATE`: `CK_P8_GOLDEN_GREEN`
- `TARGET_GATE`: `CK_P9_INTEGRATION_GREEN`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `P8_PACKET_SHA256`: `c7de73f394151f5cc850cf085a32140e74887bf2873a37448a056966cc8f2378`
- `P9_S3_R2_SHA256`: `cb46e382f98d9a4d52a882a3d35f1b0ae4db9047e07f713d2212196dc3204214`
- `EXECUTION_PROMPT_SHA256`: `51cdae6c688dafa0715a3120b74fb6ec162a34b5d25c4680268e4450f463394b`
- `PRIOR_MCP_PROOF_SHA256`: `07db27442a49f49941dda9158d7ddb57839fc99e8a52ead5c2881d42e260552d`
- `PRIOR_AWS_LIVE_RECEIPT_SHA256`: `06f9cd68a6053db1c09afcd1f9525a983042d6be5b83c36a97339cdb7cfea115`
- `PERSONA_RECEIPT_SHA256`: `7627c7e9f128c857b0ba8ba951844cf6047ae870ee8d57086b967838edffd1d5`
- `UTC_FROZEN`: `2026-07-26T21:10:26Z`

## Exact missing evidence

P9 has a GREEN offline architecture and a GREEN bounded AWS lifecycle, but it
does not yet have two distinct complete live vertical slices. The prior two
Lambda calls repeated one byte-identical request, and the prior read-only MCP
query returned zero linked rows. Neither fact is promoted by this contract.

## Fixed identities

- campaign: `ck-p9-completion-r1`
- valid trial: `ck-p9-live-promote-r1`
- unsafe trial: `ck-p9-live-refuse-r1`
- valid request: `ck-p9-live-promote-request-r1`
- unsafe request: `ck-p9-live-refuse-request-r1`
- valid candidate: `ck-p9-live-promote-candidate-r1`
- unsafe candidate: `ck-p9-live-refuse-candidate-r1`

Every task, event, receipt, vector, request, worker result, projection, and
evidence root is distinct across the two trials. Trial A must end in local
deterministic `PROMOTE`. Trial B must end in local deterministic `REFUSE` after
one declared unsafe/tampered successor. Cloud output remains advisory.

## Finite coordinator operations

The only accepted operation names are:

1. `COMMIT_DECLARATION`
2. `STORE_CONTEXT_VECTOR`
3. `QUERY_CONTEXT_VECTOR`
4. `INVOKE_LAMBDA`
5. `COMMIT_WORKER_RESULT`
6. `STREAM_WORKER_RESULT`
7. `RESUME_STREAM`
8. `VERIFY_CANDIDATE`
9. `RECONSTRUCT_FRESH`
10. `REPLAY_LOCAL`
11. `QUERY_MCP_LINKAGE`
12. `CLEANUP_TRIAL`

The coordinator maps these enums to prewritten code. It rejects unknown
fields, noncanonical JSON, invalid identifiers, oversize payloads, duplicate or
out-of-order sequences, stale parents, replayed one-use identities, and hash
mismatches. It never executes model, worker, Lambda, MCP, or changefeed supplied
SQL, shell, URL, ARN, path, command, destination, or credentials.

## Fixed live resource allowlist

- CockroachDB cluster: `cockroach-kernel`
- database/schema: `cockroach_kernel.ck`
- tables: `tasks`, `trajectory_events`, `receipts`, `context_vectors`,
  `worker_results`, `projection_events`
- view: `ck.mcp_receipt_view`
- vector index: `context_vectors_vector_idx`
- runtime identity: `ck_runtime`
- AWS region/function: `us-west-2` / `ck-p9-evaluator`
- IAM role: `ck-p9-lambda-exec`
- log group: `/aws/lambda/ck-p9-evaluator`
- alarm: `ck-p9-invocations-1000`

SQL is limited to parameterized inserts/selects over those exact objects, one
fixed vector nearest-neighbor query scoped by `task_id` and namespace, the
approved sinkless changefeed over `ck.worker_results`, one fixed bounded MCP
SELECT over `ck.mcp_receipt_view`, and exact campaign cleanup. Dynamic object
names, multi-statements, comments-as-commands, arbitrary DDL/DCL, and model-
selected SQL are forbidden.

## Bounds

- request/response: at most 16 KiB each
- observations: at most 16, each at most 256 UTF-8 bytes
- one in-flight Lambda call; at most 1,000 P9/S3 invocations total
- Lambda timeout: three seconds; 128 MiB; no URL, trigger, VPC, layer, or model
- transaction retries: bounded SQLSTATE `40001` only, with original and
  committed attempts preserved
- MCP: one temporary project-local OAuth configuration, read-only, one cluster,
  two task IDs, finite limit, followed by logout and configuration deletion
- aggregate P9/S3 AWS incremental charge: at most $5.00
- credentials and OAuth bytes: never printed, logged, committed, packaged, or
  transferred

## Test and evidence matrix

Before live execution: the existing P9 suite plus coordinator unit,
integration, adversarial, idempotency, stale/out-of-order, injection,
denial-of-wallet, fresh-root, replay, residue, secret, and private-path tests;
two fresh mock roots; and canonical source/config hashes.

Each live trial must emit linked canonical receipts for transaction, vector,
Lambda request/AWS request ID/response, worker commit, changefeed projection and
restart cursor, local verdict, declared session loss, fresh-root continuation,
keyless replay parity, cost, and cleanup. The two trials must differ on every
declared identity and receipt root.

Required preserved fault classes: 40001 retry, duplicate, Lambda timeout,
throttle, malformed, stale, hash mismatch and unavailable, vector empty/stale/
unauthorized/linkage failure, MCP unknown/oversized/write refusal, changefeed
duplicate/lag/restart/projection mismatch, tamper, policy veto, quorum failure,
warrant replay, interrupted commit, rollback, injection, egress, IAM negatives,
denial-of-wallet, cleanup, and residue.

## Stop conditions and kill line

Stop fail-closed on false acceptance, nondeterminism, missing linkage, hidden
credential, credential prompt, MFA/CAPTCHA/terms/payment, write-capable MCP,
unexpected cluster/resource/region, dynamic operation, unbounded cost, hash or
schema mismatch, incomplete cleanup, test failure, or evidence loss.

Kill line: no S3 packet, judge, RunPod inventory mutation, worker creation, or
campaign action until the two live trials, linked MCP read plus revocation, and
same-packet GLM plus AGY P9 final reviews are all GREEN.

## Builder and judge boundary

The completion delta uses the separately frozen builder and persona receipts.
Kimi K3, Vibe, and Devstral contribute sanitized bounded artifacts only;
Codex reconciles them and owns the live coordinator. P9 final judges are GLM
and AGY over identical sanitized packet bytes. Contributors never judge their
own work and no model output can close this gate.

## Current official-source snapshots

- Devpost rules URL: `https://cockroachdb-ai.devpost.com/rules`
- retrieved-byte SHA-256: `7683efa323843010982320df18d8ffba5988750401518d70cf1323f0147ab0f9`
- CockroachDB vector-index docs SHA-256: `a78ed61f3969efd14b7c11068f9dd3a43a5c818b96fe2b1a110b3d6a2013ec2d`
- CockroachDB CDC overview SHA-256: `5e0415e7dbbc21d16bdaf6d906149726ae7ae8c0d77270a4fc20d3d148718886`
- AWS Lambda Python handler docs SHA-256: `7a2644371c59a2d389e834657a8b6952e76f54713e0af4871750ad1d8f741447`

The current rules still require a new agentic application with CockroachDB as
the persistent memory layer, meaningful CockroachDB and AWS integration, at
least two listed CockroachDB tools, at least one AWS service, consistent
functionality, public open-source code, a functional demo URL, a sub-three-
minute functional video, and free unrestricted judging access. This contract
does not claim the later public or submission gates.
