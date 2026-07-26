# Cockroach Kernel P9 Final Integration Packet R1

## Review target and authority boundary

This packet asks for an independent verdict on only
`CK_P9_INTEGRATION_GREEN`. It does not ask the reviewer to judge S3, P10,
release, video, public repository, or submission readiness.

- implementation branch: `main`
- packet parent commit: `61d77d1704a3f074427f9f82b300abaaa201f79c`
- implementation commit exercised by both clean clones:
  `cbd58b3af9e1ce5c4ddf8885866b88e7e7c1ca0f`
- last inherited GREEN gate: `CK_P8_GOLDEN_GREEN`
- target: `CK_P9_INTEGRATION_GREEN`
- plan SHA-256:
  `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- completion contract SHA-256:
  `a36ad159c6b353afd1e13a2705882e7e8541bd05f2ed37da1f5d4f5bbeee4be4`
- execution prompt SHA-256:
  `51cdae6c688dafa0715a3120b74fb6ec162a34b5d25c4680268e4450f463394b`

The reviewer is non-authoring. It may return a verdict and findings only. It
has no shell, filesystem write, code, browser, cloud, credential, deployment,
public-action, or implementation-direction authority. Cloud, MCP, builder,
persona, and reviewer outputs never select the product verdict.

## Current official rules and platform recheck

The official rules and current provider pages were re-read at
`2026-07-26T22:13:07Z`.

- official rules URL: `https://cockroachdb-ai.devpost.com/rules`
- current fetched rules bytes SHA-256:
  `b0c24cd83cd3ef5e869a110edf3b4bb41e6bd4e3506c1c884e3449600c132677`
- current Managed MCP page SHA-256:
  `b37744ad6e08054e020f69b26cdba383982f80e4176de81bfe66388a670c8b78`
- current AWS Lambda pricing page SHA-256:
  `91dff369b297f657a99cd86450db2458a69194b6b1cb301642751f7836c2ede5`

Relevant rule content remains unchanged: new work during the submission
period; an agentic application using CockroachDB as persistent memory and
deployed on AWS; meaningful use of at least two listed CockroachDB tools and
at least one AWS service; consistent functionality; later public open-source
repository, functional demo URL, sub-three-minute functional video, and free
judge access. P9 proves the build-time integration and keyless replay path. It
does not claim the later public/submission obligations are complete.

## Frozen architecture

The P9 host coordinator accepts exactly twelve versioned operations:

`COMMIT_DECLARATION`, `STORE_CONTEXT_VECTOR`, `QUERY_CONTEXT_VECTOR`,
`INVOKE_LAMBDA`, `COMMIT_WORKER_RESULT`, `STREAM_WORKER_RESULT`,
`RESUME_STREAM`, `VERIFY_CANDIDATE`, `RECONSTRUCT_FRESH`, `REPLAY_LOCAL`,
`QUERY_MCP_LINKAGE`, and `CLEANUP_TRIAL`.

Every command is canonical JSON with strict fields, bounded sizes, stable IDs,
sequence and parent hashes, replay rejection, and a fixed operation plan. No
model-, worker-, Lambda-, MCP-, or changefeed-supplied SQL, shell, URL, ARN,
path, command, destination, credential, or dynamic operation reaches
execution. SQL is prewritten and parameterized. Lambda output is strict-schema
validated and `ADVISORY` only. The local P4 verifier is the sole authority for
`PROMOTE`, `REFUSE`, and `INVALID`.

The live allowlist was limited to:

- CockroachDB database/schema `cockroach_kernel.ck`;
- six declared tables, one receipt view, and the distributed vector index;
- one runtime identity with 15 exact grants and no ownership/admin/DDL role;
- AWS Lambda `ck-p9-evaluator` in `us-west-2`, its exact execution role, log
  group, and invocation alarm;
- one temporary read-only Managed MCP grant bound to the declared cluster.

## Two distinct live vertical slices

| Property | Valid trace | Unsafe trace |
|---|---|---|
| Task | `ck-p9-live-promote-r1` | `ck-p9-live-refuse-r1` |
| Request hash | `3c7d6d1bb56f5a3901dbfab9e83a0c1c5fb3d2e9fc8702986f0d5c10daae15ec` | `07e049a9e3552aa5ead493cd728a81d190ddda26c35b77a22d99b3e78665e779` |
| Receipt hash | `2f30d74734954eab00ceee936c9996bc8a0881b55ee7027b2decccd4a0d6a8bc` | `b6d0fe2e5b004d67c3eea7ebc2ffb45d4defcd6184ec670f068915792aa884d8` |
| Lambda response hash | `d67f70944096a79c427e2086ed3bac723bef071ae3f5d21e70dcaa3eaeeb51f2` | `4212a2cc26fe4fd7623ba80b8c9d2444d261c4d252d9be673e065b43ceac35ad` |
| Worker result hash | `0489b0249c3eaa6081cdfa0576d460d583f9c71d9639a65d44cd55cb4438c979` | `c84d932b66ca0dc749029e8c7970efa626940b447f85ed9f7c57dfb77462bfe3` |
| Projection hash | `05038784019e86388554f94e4f6757de96cdc82256d1937f7dc2dc63bd3682d8` | `ca7529e66618773d5d12594b8e14304183c4db85da2f76891c04d9d0379102ac` |
| Local verdict | `PROMOTE / VERIFIED` x5 | `REFUSE / HASH_MISMATCH` x5 |
| Fresh context | continued | blocked: `CAPSULE_NOT_PROMOTED` |

For each trace, the live database atomically committed the task, trajectory
event, sealed immutable receipt, and deterministic 64-dimensional context
vector. The exact bounded vector query returned the linked row with distance
zero. Two distinct canonical Lambda requests returned HTTP 200, no function
error, distinct AWS request-ID hashes, and distinct response hashes. The
coordinator validated both responses as untrusted data before committing the
worker result and projection.

The primary sinkless changefeed and its restart from the captured cursor both
emitted both request IDs plus a resolved cursor. Inspection hashes:

- primary:
  `1add3dd865363cd9c4a1e8aaa909e0c05fde04820d1085a3a0c5f33b4da8239c`
- resumed:
  `49c3e23996a74043ef8f8b8cc625e22753ffae63e6e89d4323a162617ae415c2`

No changefeed write-back authority exists. No changefeed/client process
remained after capture.

## Fresh-process and keyless replay evidence

Two separate empty-root processes consumed only the canonical prepared and
reconciled files. User-site imports, network use, credentials, hidden session
state, and bytecode writes were absent.

- valid result SHA-256:
  `2194435da7eeeff4b16d31b97afb80a19f19f73d7525fa0d15ac8d08e72dcf39`
- refusal result SHA-256:
  `cde1a72cb2ab5c47f2c1790c788cc44461be9b3b18f476afe9cd5e8953495521`
- replay label: `KEYLESS_LOCAL_REPLAY`

The valid capsule reconstructed and continued without restating the task. The
unsafe capsule preserved the deterministic refusal and did not continue. This
is a deterministic replay of the genuine build-time trace, not a live cloud or
model call.

## Distributed Vector Index and Managed MCP evidence

Both live vector queries returned the exact task/event-bound vector and
deterministic digest. The application stores state, events, immutable receipts,
vectors, worker provenance, and projections in one transactional memory layer;
the vector path is not a detached toy database.

After nonempty rows existed, the visible OAuth consent state showed `Read Data`
checked and disabled and `Write Data` unchecked. Exactly one bounded
`cockroachdb-cloud/select_query` call returned the two declared rows from
`ck.mcp_receipt_view`, each with the exact distinct sealed receipt/event
linkage. No other MCP tool or server was used. The grant was revoked; scoped
status became `Not logged in`; the global Codex config remained at SHA-256
`932bb0c065f5c7807698375847f185793f58bb5ace653bb2997863172c8ad863`.
No OAuth, cookie, callback, account, organization, cluster, or connection
identifier is stored in the final evidence.

## Mechanical and adversarial verification

The current P9 suite passed 113/113 tests. The inherited P3-P8 suites also
passed at the current tree: 5 + 6 + 20 + 41 + 29 + 15 tests. Total current
mechanical executions: 229/229.

The tests preserve the required fault classes: SQLSTATE 40001 retry/exhaustion,
duplicates and idempotency conflicts, timeout/throttle/unavailable/malformed/
stale/hash-mismatched Lambda results, bounded deterministic vectors and
namespace isolation, MCP unknown/oversized/write/multi-statement refusal,
changefeed duplicate/lag/restart/projection mismatch, quorum and policy-veto
refusal, tamper, warrant replay, interrupted recovery/rollback, injection,
egress/import restrictions, IAM negatives, invocation/byte ceilings, cleanup,
and residue.

Two final no-hardlink clones of implementation commit
`cbd58b3af9e1ce5c4ddf8885866b88e7e7c1ca0f` independently passed 113/113 P9
tests and reproduced identical replay/promote/refuse hashes. Both clone roots
were removed; special-file and process counts were zero.

Gitleaks reported zero findings over the staged completion delta. The 26
`detect-secrets` candidates were classified individually as expected SHA-256
evidence hashes. Exact credential/private-path/host/cluster-ID patterns returned
zero matches.

## Cleanup, resources, and cost

The first web-shell cleanup batch was rejected before mutation because its
first statement was `BEGIN`, a disallowed web-shell statement. The same six
exact ID-scoped deletes then succeeded individually in dependency-safe order.
Independent readback returned zero tasks, events, receipts, vectors, worker
results, and projections for both trial IDs. The local cleanup receipt hash is
`0ce271c9dc2805289cbe31d5f8ffb52ef04d88c80d794827a577f4ad9c5dc72f`.

The temporary CA certificate/root was removed, OAuth was revoked, no child or
changefeed remained, and no RunPod worker exists. The reviewed P9 AWS function,
role, one-day log group, and invocation alarm intentionally remain for S3.
Total known P9 Lambda evidence calls are four, far below the 1,000-call ceiling;
the current bounded incremental AWS exposure remains below `$0.01` and the
existing CockroachDB Basic/free-trial boundary was not upgraded.

## Builder/persona provenance

The required Kimi, Vibe, and Devstral contribution attempts are preserved in
`P9_COMPLETION_BUILDER_CONTRIBUTIONS_R1.md` (SHA-256
`7436bad1be6b43151ee9fd3ba21786a88c3f4ec1f0671c165c61723c3f93dcc3`).
Kimi's bounded coordinator design/test contribution was independently
reconciled; Vibe's unavailable-API suggestions were rejected; Devstral's
checklist was accepted only where encoded in mechanical tests. No contributor
received credentials or live authority and none judges this packet.

The 15 inert persona-source hashes were revalidated in
`P9_COMPLETION_PERSONA_SOURCE_RECEIPT_R1.md` (SHA-256
`87669796f4b3b9f7a29cdab3e112b4a233e18c453055c1e05a2b54818709b7a8`).
Personas grant no tool, credential, memory, cloud, public-action, or judge
authority.

## Evidence anchors

- P9 source-tree aggregate:
  `7579d87883ac3e7b685cda9c767ce0439ecc994f03919d2951f426a9f75dcd39`
- live-evidence-tree aggregate:
  `07e68ba6771166a7c682dbee3ac279da2232e472ae874a57ef858af9f6f0e5df`
- linked-MCP-evidence-tree aggregate:
  `ef7a0cc6a8a9ea0852d9d9f447992d3e48eef03b44bd8b7849852b17d8ef3c14`
- live trial receipt SHA-256:
  `00583a7e0f44857075ccdd9a86720c7cc41ac7798a3354a50ae98537327d5b69`
- MCP linked receipt SHA-256:
  `528878fe2afea8587bf92df991cdc72e2c35eecb27d293681214921f0ff61cad`
- cleanup receipt SHA-256:
  `75891ae42c6b8f5637d2554167a1c7e0e43f066c1f75887e7919a737fe260c45`
- clean-clone receipt SHA-256:
  `d5b1faf5f85a6e3f1698a5274f3002343a893eb94adc96db66b260bffbc058bd`
- prior AWS live receipt SHA-256:
  `06f9cd68a6053db1c09afcd1f9525a983042d6be5b83c36a97339cdb7cfea115`

Aggregate commands hash the sorted `shasum -a 256` output for every tracked
file in the named tree. Raw completion evidence totals 63,636 bytes.

## Preserved failures and limitations

No failure was rewritten into a pass:

- one initial SQL view query used `encode()` on string fields and failed;
- one initial sinkless-feed readiness process required exact-PID termination;
- one Lambda editor attempt failed local JSON validation before invocation;
- one isolated Python attempt failed before evidence because isolated mode
  excluded the script-local modules;
- one transaction-wrapped cleanup attempt was rejected before execution;
- the live CockroachDB SQL-shell role-switch negative remains grant-derived
  because the console blocks role switching;
- the cloud build path depends on authenticated owner sessions, but the final
  judge path is explicitly keyless local replay;
- P9 does not prove the 12-hour S3 soak or any public/submission gate.

## Required reviewer verdict

Return `GREEN` only if this packet directly supports all of the following:

1. two distinct end-to-end live traces with exact transactional, vector,
   Lambda, changefeed, local-verdict, and receipt linkage;
2. deterministic promotion/refusal authority remains local and cloud output is
   advisory only;
3. fresh-process continuation succeeds only for the valid capsule and keyless
   replay honestly matches the live semantics;
4. the final Managed MCP call is nonempty, read-only, single-cluster scoped,
   revoked, and sanitized;
5. cleanup, credentials, costs, resource boundaries, and known limitations are
   honest and fail-closed;
6. current tests, clean clones, hashes, and provenance are sufficient for
   `CK_P9_INTEGRATION_GREEN` without implying S3 or submission completion.

Otherwise return `NOT_GREEN`, `BLOCKED`, or `INSUFFICIENT_EVIDENCE` with the
exact failed criterion and evidence gap. Do not prescribe code or direct a
repair.
