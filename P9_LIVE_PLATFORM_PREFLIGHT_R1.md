# P9 Live Platform Preflight R1

- `UTC`: `2026-07-26T19:11:59Z`
- `RESULT`: `PREMUTATION_REVIEW_REQUIRED`
- `LAST_GREEN_GATE`: `CK_P8_GOLDEN_GREEN`
- `CURRENT_COMMIT`: `bcc03a371d86587bdc00d1805742294fbcb012bd`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `AUTHORIZATION_SHA256`: `cb46e382f98d9a4d52a882a3d35f1b0ae4db9047e07f713d2212196dc3204214`
- `P8_PACKET_SHA256`: `c7de73f394151f5cc850cf085a32140e74887bf2873a37448a056966cc8f2378`
- `P9_OFFLINE_PACKET_SHA256`: `725f8edf8487a9a34572b2315eab795318a74a7ee0ebf0849e5f982be4468e7d`
- `AWS_MUTATIONS`: `0`
- `COCKROACHDB_MUTATIONS`: `0`
- `RUNPOD_ATTEMPTS`: `0`

## Revalidated official sources

Raw HTML hashes are point-in-time execution metadata. Vendor and Devpost pages
contain request-variant material, so a changed raw hash is not by itself a
substantive rules or product change.

| Source | SHA-256 |
|---|---|
| Devpost official rules | `f42e7cb158fb7f8017dd9c928237937a203a1f7a362413b4fa5987ca38c85979` |
| CockroachDB Managed MCP | `b37744ad6e08054e020f69b26cdba383982f80e4176de81bfe66388a670c8b78` |
| CockroachDB vector indexes | `a78ed61f3969efd14b7c11068f9dd3a43a5c818b96fe2b1a110b3d6a2013ec2d` |
| CockroachDB changefeeds | `5314e68f45ee6843503df51f2d54b5264af192811babf14a8c32267f8ef0fc28` |
| CockroachDB free trial | `8cd0d2d1ddc64b0d46e767751379e5ead05f93eb62f7053452acf36febc22cb9` |
| CockroachDB pricing | `65fa7d1053c8f5c8247ed0b6b0d3e332ad899141ec885107730767cd190066d5` |
| AWS Lambda pricing | `f144beff7eb6341d1ec09a5617e31b857df54743d20df763b73bcd316ad42626` |
| AWS Lambda quotas | `06d9b5f5469e6c2d902fdeb9301b690fd4a8817292dc03265704ec7307b769bd` |
| AWS Lambda concurrency configuration | `60a46ab86720d784fe790ddc3441a20aab74dbb15512b12e86eb4c60c4ce995c` |

The official rules still require an agentic application using CockroachDB as
persistent memory, deployment on AWS, at least two named CockroachDB tools,
at least one AWS service, meaningful integration, a public open-source
repository, a functional demo URL, and free judging access through the end of
the judging period on September 15, 2026.

## AWS account evidence

- Authenticated Lambda console: available.
- Region: `us-west-2` / Oregon.
- Applied concurrent-executions quota: `10`.
- Default displayed quota: `1,000`.
- Utilization: `0`.
- Lambda Functions pricing remains request plus GB-second duration; the public
  free tier advertises one million requests and 400,000 GB-seconds monthly.
- No public endpoint, trigger, function, role, log group, alarm, access key, or
  other project resource exists yet.

At 128 MiB, three seconds, and 1,000 maximum controlled invocations, the
declared compute upper bound is 375 GB-seconds. The published on-demand rate
would make the compute component approximately `$0.00625` before any free-tier
credit, and 1,000 requests are below the published one-million-request monthly
free tier. Logging remains separately bounded by one-day retention.

## CockroachDB account evidence

- Cluster: `cockroach-kernel`.
- Plan: `Basic`.
- Provider and region: AWS, `us-west-2` / Oregon.
- Version: `v26.2.1`.
- State: `Available`.
- Database visible before P9 migration: `defaultdb`.
- Runtime SQL user visible: `ck_runtime`.
- Current request-unit usage: approximately 46.09 thousand.
- Current storage usage: approximately 1.94 MiB.
- Free-trial credits: `$400` remaining; visible expiry: `2026-08-25`.
- Basic public pricing advertises 50 million RUs and 10 GiB free monthly, but
  the vendor documentation says continued monthly Basic credits require a
  payment method. No payment details were inspected or changed.

## Live capability matrix

| Capability | Live evidence | Disposition |
|---|---|---|
| Serializable SQL authority | Authenticated SQL Shell executed read-only statements successfully | Available for reviewed migration |
| Distributed Vector Indexing | `SHOW CLUSTER SETTING feature.vector_index.enabled` returned `true` | Available |
| Changefeed foundation | `SHOW CLUSTER SETTING kv.rangefeed.enabled` returned `true`; official cost docs state all Cloud plans support CDC and Basic meters it as RUs | Available inside RU/cost cap |
| Managed MCP | Cluster Connect modal exposes the CockroachDB Cloud MCP endpoint and OAuth flow with selectable read-only/write scope | Available; human read-only OAuth authorization remains required |
| AWS Lambda | Authenticated Lambda Functions console and Service Quotas are accessible in `us-west-2` | Available, subject to concurrency amendment |

## Free judge path

The live vendor accounts are build-time evidence surfaces, not judge
credentials. The free unrestricted judge path remains the keyless deterministic
local replay and clean-clone path already proven in the P9 offline packet. It
must be labeled as replay. P10 must still prove a public functional demo URL and
access through the full judging period; this preflight does not close P10.

## Open gates

1. The account-level Lambda quota of 10 prevents the planned reserved
   concurrency of 1 under AWS's mandatory 100-unreserved rule.
2. Managed MCP still needs a human-controlled OAuth authorization that grants
   read-only access to only the declared cluster.
3. Live IAM simulation, exact resource readback, two live trials, and cleanup
   receipts do not exist yet.
4. CockroachDB free-trial expiry precedes the end of judging. The keyless replay
   avoids a judge credential dependency, but P10 must separately prove the
   public demo and judge-period access plan.

No external mutation is authorized by this receipt.
