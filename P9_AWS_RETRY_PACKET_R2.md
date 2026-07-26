# P9 AWS Retry Packet R2

## Identity

- `LAST_GREEN_EXECUTION_GATE`: `CK_P8_GOLDEN_GREEN`
- `P9_AWS_RETRY_PACKET_R1_SHA256`: `17077cf3913e88bab2b02440cd256814253f4544555310b46a2b39928fab4de2`
- `P9_AWS_RETRY_R1_JUDGE`: `GLM_5_2_GREEN`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `AUTHORIZATION_SHA256`: `cb46e382f98d9a4d52a882a3d35f1b0ae4db9047e07f713d2212196dc3204214`
- `FAILED_LIFECYCLE_R2`: `P9_AWS_FAILED_LIFECYCLE_RECEIPT_R2.md`
- `CONSISTENCY_AMENDMENT`: `P9_AWS_EVENTUAL_CONSISTENCY_AMENDMENT_R1.md`
- `RUNPOD_MUTATIONS`: `0`

## Proven current state

- CockroachDB migration, vector index, view, and exact runtime grants remain
  live and verified.
- The second AWS lifecycle proved exact IAM behavior and two deterministic live
  Lambda responses, then rolled back because the first log-stream inventory was
  empty.
- Post-rollback role and function absence and zero exact log-group/alarm counts
  are preserved in the raw evidence.
- No AWS function, role, log group, alarm, URL, trigger, event source, or
  provisioned concurrency currently remains.

## One additional bounded lifecycle

Recreate only the exact four approved AWS resources using the already-GREEN
IAM template. Repeat configuration readback and the two sequential synthetic
invocations. After the second invocation, poll only the exact log-group stream
inventory every five seconds for at most 90 seconds. Make no invocation during
that poll. Continue only after a nonzero stream count.

Then retrieve and hash the raw request, both byte-identical responses, invoke
metadata, sanitized configuration, simulation results, and evidence manifest.
Preserve the four AWS resources through S3 only if every gate passes. Stop at
Managed MCP OAuth; Kenneth alone may authorize read-only access restricted to
`cockroach-kernel`.

Any existing resource, broader permission, unexpected state, non-identical
response, missing log stream after 90 seconds, retrieval mismatch, credential
exposure, or rollback ambiguity blocks P9. No RunPod or S3 action is allowed.

## Verdict request

Judge only whether this bounded observation amendment preserves the already
approved authority, cost, reversibility, and P8-to-P9 boundary. Do not author
code or implementation direction. Return exactly:

`VERDICT: GREEN|NOT_GREEN`

`PACKET_SHA256: <exact supplied hash>`

`FINDING: <one sentence>`

`BOUNDARY: <one sentence>`
