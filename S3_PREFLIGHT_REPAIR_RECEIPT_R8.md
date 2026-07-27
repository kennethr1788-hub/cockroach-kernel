# S3 Preflight Repair Receipt R8

- `PARENT_PACKET`: `S3_PREFLIGHT_PACKET_R7.md`
- `PARENT_PACKET_SHA256`: `94b449510eecbdb7f6a6d961375412950cdcd566196e004290b9fb62149125f2`
- `STATUS`: `R8_WORKER_SHAPE_CONTRACT_REPAIRED_JUDGES_PENDING`
- `ATTEMPT_A01_POD_ID`: `bre4wr6bkeoya1`
- `ATTEMPT_A01_RESULT`: `PREUPLOAD_WORKER_SHAPE_MISMATCH`
- `ATTEMPT_A01_TEARDOWN`: `GREEN`
- `ATTEMPT_A01_REQUEST_SHA256`: `aff92d6a4c5169263a4e2612b7157c2f2a3798bd019681fba68238a717368929`
- `ATTEMPT_A01_SANITIZED_RESPONSE_SHA256`: `42a633b23209b47c353b3569e6a6e587a0f7d2430e258dd1aedb4243574fa43f`
- `UPLOAD_STARTED`: `NO`
- `WORKLOAD_STARTED`: `NO`
- `S2_SIX_HOUR_MAX_RSS_BYTES`: `836284416`
- `S3_FROZEN_RSS_LIMIT_BYTES`: `1610612736`
- `UTC_RECORDED`: `2026-07-27T01:05:14Z`

## Finding

The controlling authorization explicitly permits either exactly 2 vCPU with
4 GiB RAM or exactly 2 vCPU with 8 GiB RAM when sufficient. R7 unnecessarily
narrowed the independently reviewed execution contract to 8 GiB. RunPod then
returned the authorized 4-GiB class at `$0.06/hour` for A01. Because that did
not match R7, A01 was stopped and deleted before upload; exact-ID lookup was
absent and scoped inventory was empty.

## Evidence-backed correction

The completed S2 six-hour production run measured maximum RSS of `836284416`
bytes. S3 retains its pre-result worker RSS ceiling of `1610612736` bytes.
Four GiB therefore exceeds both the observed production requirement and the
frozen enforcement ceiling without relaxing any S3 threshold. R8 accepts only:

- exactly 2 vCPU / 4 GiB at no more than `$0.06/hour` compute; or
- exactly 2 vCPU / 8 GiB at no more than `$0.08/hour` compute.

Both remain subject to the unchanged `$0.10/hour` active-rate ceiling,
20-GiB disposable disk ceiling, zero GPU, zero persistent/network volume,
unchanged image/template, and all original security and lifecycle gates.

No source code, workload bundle, threshold, evidence schema, cloud boundary,
campaign identifier, attempt name, or provider deadline changed. R7 judge
verdicts are historical after this contract change. Attempt A02 is forbidden
until GLM and Claude independently return GREEN over the same R8 packet bytes.
