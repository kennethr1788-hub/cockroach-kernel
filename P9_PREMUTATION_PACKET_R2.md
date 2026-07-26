# P9 Pre-Mutation Packet R2

## Identity

- `LAST_GREEN_GATE`: `CK_P8_GOLDEN_GREEN`
- `COMMIT`: `bcc03a371d86587bdc00d1805742294fbcb012bd`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `AUTHORIZATION_SHA256`: `cb46e382f98d9a4d52a882a3d35f1b0ae4db9047e07f713d2212196dc3204214`
- `OFFLINE_PACKET_SHA256`: `725f8edf8487a9a34572b2315eab795318a74a7ee0ebf0849e5f982be4468e7d`
- `PREVIOUS_JUDGE_ATTEMPT`: invalid, no verdict, preserved separately
- `MUTATIONS`: AWS 0; CockroachDB 0; RunPod 0

## Verified facts

- Official rules still require meaningful CockroachDB memory, at least two
  named CockroachDB tools, AWS deployment, free judge testing, public source,
  functional demo URL, and access through September 15, 2026.
- AWS Lambda is authenticated and available in `us-west-2`.
- AWS applied concurrent-executions quota is 10; utilization is 0.
- CockroachDB `cockroach-kernel` is Basic, AWS `us-west-2`, v26.2.1, Available.
- Live read-only SQL proved vector indexes enabled and rangefeeds enabled.
- The cluster UI exposes Managed MCP OAuth with selectable read-only/write
  scope. Human read-only, single-cluster authorization remains a later gate.
- Cockroach trial credits visibly expire August 25. Judges receive the proven
  keyless local replay, not private cloud credentials. P10 still must prove the
  public demo URL and judge-period access.

## Required amendment

Offline template reserved concurrency 1 is impossible: AWS requires 100
executions to stay unreserved but this account's total quota is 10.

Approve only this substitution:

- no per-function reserved or provisioned concurrency;
- provider-enforced account ceiling 10;
- coordinator maximum one in-flight request and 1,000 total attempts;
- 128 MiB, three-second timeout, one-day logs;
- no URL, trigger, event source, async destination, public/cross-account policy,
  wildcard invocation, VPC, layer, network client, or model verdict authority;
- exact function invocation only through the authenticated project path;
- strict schemas, 16 KiB request/response, hashes, idempotency, and local verdict.

At 1,000 maximum invocations, compute is 375 GB-seconds and about `$0.00625`
before free credits. Aggregate P9/S3 AWS ceiling remains `$5.00`.

The already-reviewed IAM exception permits only a dynamic log-stream suffix
under the exact project log group; no wildcard action or broader resource.

## Authorized sequence after GREEN

1. Encode this amendment locally; rerun all tests/scanners.
2. Apply exact CockroachDB migration/grants; prove runtime DDL/DML denial.
3. Create exact least-privilege Lambda role, function, log retention, and alarm.
4. Read back and hash all effective configuration; run negative tests.
5. Stop at Managed MCP OAuth. Kenneth alone grants read-only access to only
   `cockroach-kernel`; no model handles the challenge.

Stop on any credential exposure, quota/name/region/price drift, public endpoint,
trigger, unexpected permission, write-capable MCP, paid plan/resource increase,
migration mismatch, readback failure, cleanup ambiguity, or non-GREEN verdict.
S3 remains forbidden until final P9 GREEN.

## Verdict request

Judge only coherence, reversibility, least privilege, cost bounds, rules fit,
and safety through the next human gate. Do not code or direct implementation.
Return exactly four short lines:

`VERDICT: GREEN|NOT_GREEN`

`PACKET_SHA256: <exact supplied hash>`

`FINDING: <one sentence>`

`BOUNDARY: <one sentence>`
