# P9 Pre-Mutation Packet R1

## Packet identity

- `PACKET_REVISION`: `R1`
- `UTC_FROZEN`: `2026-07-26T19:11:59Z`
- `LAST_GREEN_GATE`: `CK_P8_GOLDEN_GREEN`
- `CURRENT_COMMIT`: `bcc03a371d86587bdc00d1805742294fbcb012bd`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `AUTHORIZATION_SHA256`: `cb46e382f98d9a4d52a882a3d35f1b0ae4db9047e07f713d2212196dc3204214`
- `P8_PACKET_SHA256`: `c7de73f394151f5cc850cf085a32140e74887bf2873a37448a056966cc8f2378`
- `P9_OFFLINE_PACKET_SHA256`: `725f8edf8487a9a34572b2315eab795318a74a7ee0ebf0849e5f982be4468e7d`
- `P9_OFFLINE_ARCHITECTURE_GATE`: `GREEN`
- `AWS_MUTATIONS_BEFORE_PACKET`: `0`
- `COCKROACHDB_MUTATIONS_BEFORE_PACKET`: `0`
- `RUNPOD_ATTEMPTS`: `0`

## Exact supporting artifact hashes

| Artifact | SHA-256 |
|---|---|
| `P9_AWS_ACCOUNT_SETUP_RESOLUTION_RECEIPT_R2.md` | `dd1c7142fa3447aa5a9eab2f3b7f33c860a81a3a8e666b376c412f819f311a2e` |
| `P9_LIVE_PLATFORM_PREFLIGHT_R1.md` | `b7c0e1b3a00f59735119fc1ac7810cc80d7409142e45825d31cba9f0277dcd6f` |
| `P9_CONCURRENCY_AMENDMENT_PROPOSAL_R1.md` | `de68fd7b8e72a9db3624ed684e9cf02c75fb4188cee5cda3f7d99ff215b72cc1` |
| `P9_IAM_AMENDMENT_PROPOSAL_R1.md` | `df4d2c32f75f14c9ca4ec91dcc18a5706bfddf200bb6b4a47a9a206b1b5d6912` |
| `P9_IAM_AMENDMENT_JUDGE_RECEIPT_R1.md` | `81502b831f2412da9b78c74bb6ff3ce109224a1009c7fdf0143c6d18734ea3ac` |
| `p9-cloud/deployment_manifest.json` | `f2337df1010ea5afcee737515d198a6ebae0485d1e5a17cb66667732af8df82f` |
| `p9-cloud/iam_execution_role_template.json` | `d7d2ca0c04606b542728f6ac025f79827091ba37fa3c2d4aedb4bedd1a943a1f` |
| `p9-cloud/lambda_trust_policy.json` | `f780f9375d77b18c97f136bb9feb5c34bc5493829eefd381206688aeaa27beb5` |
| `p9-cloud/lambda_handler.py` | `8d6d02e8225d17fb7999f042e85413d72f918784b9c51d3516f8308395758833` |
| `p9-cloud/migrations/001_cloud.sql` | `cb2cb3774dce539a9f67c25e1a64f6f65e514ce54b8b2cdf5a0a46328763a240` |
| `p9-cloud/migrations/002_runtime_grants.sql` | `ee91ba6e53d7fe3cd8523cbb0de6f447e46b86b68854b320cf6a7ed8c9173c17` |

## Rules and availability facts

The re-read official rules still require a newly built agentic application
using CockroachDB as persistent memory, meaningful use of at least two named
CockroachDB tools, deployment on AWS using at least one AWS service, a public
open-source repository, a functional demo URL, a sub-three-minute video, and
free testing access through September 15, 2026.

Visible authenticated evidence, deliberately excluding account identifiers and
credentials, establishes:

- AWS Lambda is service-ready in `us-west-2`.
- Applied Lambda concurrent executions are 10; utilization is 0.
- CockroachDB cluster `cockroach-kernel` is Basic, AWS `us-west-2`, v26.2.1,
  Available.
- `feature.vector_index.enabled = true`.
- `kv.rangefeed.enabled = true`.
- CockroachDB Cloud exposes Managed MCP for this cluster using OAuth with a
  human-selectable read-only or write scope.
- CockroachDB trial credits expire August 25, 2026, before judging ends. The
  judge path therefore cannot depend on private live credentials or assume the
  trial remains unrestricted. The proven keyless replay remains the free test
  path, and P10 retains the separate public-demo/access obligation.

## Required concurrency amendment

The offline template's reserved concurrency of 1 cannot be applied because AWS
requires at least 100 executions to remain unreserved and this account's total
applied quota is 10.

The packet proposes the smallest safe substitution:

- do not configure per-function reserved concurrency;
- treat the provider-enforced account quota of 10 as the hard cloud ceiling;
- serialize the project coordinator to one in-flight request;
- retain the 1,000-invocation campaign ceiling, 128 MiB memory, three-second
  timeout, one-day logs, and no provisioned concurrency;
- create no function URL, trigger, event source, async destination, public
  policy, cross-account policy, or wildcard invocation permission;
- permit invocation of only the exact project function from the authenticated
  project operator/coordinator path;
- retain strict request/response size limits, one-use IDs, idempotency,
  canonical hashes, local verdict authority, and fail-closed behavior.

At the declared maximum, Lambda compute is 375 GB-seconds and approximately
`$0.00625` before free-tier credits at the current published rate. Request cost
is within the published one-million-request monthly free tier. The existing
aggregate P9/S3 ceiling remains `$5.00`.

## IAM exception already reviewed

The only resource wildcard permitted is the dynamic CloudWatch log-stream
suffix below the exact project log group. AWS generates log stream names at
runtime; exact enumeration is impossible. No wildcard action, log-group,
function, role, region, account, or service resource is allowed. The prior
same-hash independent GLM receipt for this narrow amendment is included by
hash above.

## Exact intended mutation sequence

Only after this packet receives independent GREEN:

1. Update the local deployment manifest to encode the approved concurrency
   amendment and rerun all local tests and scanners.
2. Re-read the exact cluster/function/role/log names and region.
3. Apply the frozen CockroachDB migration with the bounded owner session.
4. Apply the runtime grants and prove negative DDL/DML privilege tests.
5. Create one exact Lambda execution role and inline least-privilege logging
   policy; read back the exact trust and permissions.
6. Create one Python Lambda function `ck-p9-evaluator` at 128 MiB and three
   seconds, with no URL, VPC, layer, event source, trigger, destination, or
   provisioned concurrency.
7. Set exact one-day log retention and the bounded invocation alarm only if the
   current price remains inside the packet.
8. Read back and hash the effective function, IAM, and logging configuration.
9. Run local and live negative tests before any claim.
10. Stop at the Managed MCP OAuth human gate. Kenneth must personally authorize
    read-only access restricted to `cockroach-kernel`; no model may approve the
    scope or handle the OAuth challenge.

No S3/RunPod action is permitted until final P9 GREEN.

## Stop conditions

Stop before or during mutation on any credential exposure, region/name drift,
account quota change, unknown price, public endpoint, trigger, unexpected IAM
permission, write-capable MCP scope, paid CockroachDB plan change, CockroachDB
resource-limit increase, migration mismatch, inability to read back exact
configuration, cleanup ambiguity, or judge verdict other than GREEN.

## Requested independent verdict

Review only whether this pre-mutation contract is internally coherent,
reversible, least privilege, cost bounded, rules compatible, and safe to execute
through the next explicit human gate. Do not write code or direct implementation.

Return exactly four lines:

1. `VERDICT: GREEN` or `VERDICT: NOT_GREEN`
2. `PACKET_SHA256: <exact supplied packet hash>`
3. `FINDING: <single concise finding>`
4. `BOUNDARY: <single concise boundary statement>`
