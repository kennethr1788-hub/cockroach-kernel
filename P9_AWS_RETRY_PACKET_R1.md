# P9 AWS Retry Packet R1

## Identity

- `LAST_GREEN_EXECUTION_GATE`: `CK_P8_GOLDEN_GREEN`
- `P9_PREMUTATION_PACKET_R2_SHA256`: `8b36c7a3f0e10d7ce7654656a8288a4a5763d1dae330fe5eeeff4658079c3b62`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `AUTHORIZATION_SHA256`: `cb46e382f98d9a4d52a882a3d35f1b0ae4db9047e07f713d2212196dc3204214`
- `AWS_FAILED_LIFECYCLE`: `P9_AWS_FAILED_LIFECYCLE_RECEIPT_R1.md`
- `IAM_AMENDMENT`: `P9_IAM_AMENDMENT_PROPOSAL_R2.md`
- `RUNPOD_MUTATIONS`: `0`

## Current live state

CockroachDB Cloud now contains only the approved P9 database state:

- database `cockroach_kernel`;
- schema `ck`;
- six expected tables and one expected view;
- vector index `context_vectors_vector_idx`;
- 15 exact `ck_runtime` grants and zero `UPDATE`, `DELETE`, `DROP`, `CREATE`,
  or `ALL` grants.

The SQL Shell blocks `SET ROLE`, so runtime denial is currently proved by the
authoritative grant inventory, not by an impersonated DML attempt. This
limitation must remain explicit.

AWS rollback is complete: the exact role, function, log group, and alarm are
absent. No invocation occurred. No RunPod resource exists for P9/S3.

## Exact retry amendment

Replace only:

`arn:aws:logs:us-west-2:${AWS_ACCOUNT_ID}:log-group:/aws/lambda/ck-p9-evaluator:log-stream:*`

with:

`arn:aws:logs:us-west-2:${AWS_ACCOUNT_ID}:log-group:/aws/lambda/ck-p9-evaluator:*`

AWS's simulator returned `allowed` for both `logs:CreateLogStream` and
`logs:PutLogEvents` on the corrected resource. The wildcard is still confined
to dynamically named streams under the exact project log group. No broader
permission is added.

## Authorized retry sequence

1. Rerun all tests and scanners over the amended local artifacts.
2. Re-simulate the custom policy and require two `allowed` results plus
   `implicitDeny` for every forbidden action.
3. Recreate only the exact role, function, log group, and alarm.
4. Read back memory, timeout, runtime, handler, concurrency, URL, trigger,
   resource-policy, log-retention, alarm, and role-policy state.
5. Invoke the strict handler twice with the frozen synthetic request and require
   byte-identical canonical output and matching hashes.
6. Preserve the four exact AWS resources only after all readbacks pass.
7. Stop at Managed MCP OAuth. Kenneth alone may authorize read-only access to
   only `cockroach-kernel`.

Any widened IAM scope, unexpected resource, failed simulation, failed
invocation, mismatch, credential exposure, paid-plan change, or rollback
ambiguity blocks P9. S3 remains forbidden.

## Verdict request

Judge coherence, least privilege, reversibility, evidence sufficiency, and the
P8-to-P9 phase boundary. Do not author code or implementation direction.
Return exactly:

`VERDICT: GREEN|NOT_GREEN`

`PACKET_SHA256: <exact supplied hash>`

`FINDING: <one sentence>`

`BOUNDARY: <one sentence>`
