# P9 Offline Feature Preflight R1

- `UTC`: `2026-07-26T12:49:23Z`
- `RESULT`: `OFFLINE_PREP_ELIGIBLE`
- `LIVE_P9_RESULT`: `BLOCKED`
- `LIVE_BLOCKER`: `AWS_ACCOUNT_SETUP_HUMAN_GATE`
- `LAST_GREEN_GATE`: `CK_P8_GOLDEN_GREEN`
- `PARENT_COMMIT`: `bd1e8160912f28cf009d99d0554c1eab34cbfb24`
- `AWS_MUTATIONS`: `0`
- `COCKROACHDB_MUTATIONS`: `0`

## Official-source custody

Raw HTML source hashes are execution metadata, not standalone version
identifiers because both Devpost and vendor pages contain request-variant
telemetry and session material.

| Source | SHA-256 |
|---|---|
| Devpost official rules | `df39b842018d4b36f552ef65e46c403f9428c0ec07ae90ea1e97308c0ef2b053` |
| CockroachDB Managed MCP | `cd475f8fd53d952820bebcf18978eb6b9fc07ebc25f667fe57e033a285fd9caf` |
| CockroachDB v26.2 vector indexes | `280982d1b03e07d0d0fe3446778aa564e785f6e9f31e7b63ba563f91c88c08fb` |
| CockroachDB Cloud costs | `01572ed107442f30b50a62c5090845160a75fea95d7c6f54f2bdf38ca887aa69` |
| CockroachDB changefeeds | `9db572912b45b8686eb102cd23b9fe53b28b292735828d30e5198cd403a35a38` |
| AWS Lambda pricing | `410ecf74f4e99123a5242be459541de8a96b8cc36c7d112d569c7084b244dc40` |
| AWS Lambda region support | `0f8b4becd1d40b0a456132546fc440d35b1fa6a9bd8b4e68ad3a0512c65471b7` |

## Visible account and cluster evidence

- CockroachDB cluster: `cockroach-kernel`.
- CockroachDB plan: Basic.
- CockroachDB provider and region: AWS, `us-west-2` (Oregon).
- CockroachDB version: `v26.2.1`.
- AWS target region: `us-west-2`, selected to match the database region.
- AWS Lambda account availability: unverified; service navigation redirects to
  `Complete your account setup`.

No account number, credential, token, cookie, payment detail, or private
identifier was recorded.

## Feature eligibility matrix

| Capability | Official support | Account evidence | Offline disposition | Live gate |
|---|---|---|---|---|
| CockroachDB serializable SQL | Supported | Cluster visible | Design and local test | Read-only connection then migration receipt |
| Distributed Vector Indexing | Supported in v26.2; cluster is v26.2.1 | Version visible | Implement deterministic 64-dimensional context vectors and local vector-index proof | Cluster-setting and `CREATE VECTOR INDEX` proof without plan change |
| Changefeed | All Cloud plans; Basic is RU-metered | Basic visible | Implement bounded sinkless projection and restart/duplicate tests | Live sinkless event, lag, restart, and cleanup receipt |
| Managed MCP | Managed service supports OAuth/API-key access and optional single-cluster scope | Account surface not yet verified | Freeze strict query allowlist and mock only | Human grants read-only only; single-cluster scope; query and audit trace; no write grant |
| AWS Lambda | `us-west-2` supported; free tier includes one million requests and 400,000 GB-seconds monthly | Account setup incomplete | Implement pure standard-library handler, local adapter, IAM/config templates, and tests | Account activation, quota/price check, deployment, two live invocations |

## Material correction to the planning language

Current CockroachDB documentation states that Managed MCP can receive read and
write permissions and can access all clusters visible to the authorizing
identity unless it is explicitly scoped. Therefore, `read-only and audited`
is an acceptance condition, not a default fact. P9 must fail closed unless the
actual authorization is read-only and restricted to the declared cluster.

## Non-claims

- No selected feature is yet proven live for this implementation.
- No AWS quota, free-tier balance, or service readiness is established.
- No live vector index, changefeed, MCP query, Lambda deployment, or Lambda
  invocation has occurred.
- This preflight authorizes offline work only and cannot close P9.

