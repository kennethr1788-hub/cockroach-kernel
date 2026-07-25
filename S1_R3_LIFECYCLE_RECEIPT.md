# S1 R3 RunPod Lifecycle Receipt

- `CAMPAIGN_ID`: `CK-S1-20260725-FOUNDATION-R3`
- `ATTEMPT`: `1 of 8 allowed`
- `POD_ID`: `wo1iq5wtk04q49`
- `POD_NAME`: `ck-s1-20260725-r3-a01`
- `PACKET_SHA256`: `82fc0dcdd38a814e40a39f85c57b1f35948d46792575c7fdd2db24283768ef87`
- `CREATED_UTC`: `2026-07-25T21:40:03.961Z`
- `SSH_READY_UTC`: `2026-07-25T21:40:47Z`
- `WORKLOAD_STARTED_UTC`: `2026-07-25T21:43:22Z`
- `WORKLOAD_FINISHED_UTC`: `2026-07-25T22:43:32Z`
- `STOPPED_UTC`: `2026-07-25T22:45:34Z`
- `DELETED_UTC`: `2026-07-25T22:45:35Z`
- `DELETION_CONFIRMED_UTC`: `2026-07-25T22:45:37Z`
- `LIFECYCLE_RESULT`: `TEARDOWN_GREEN`

The worker was CPU-only, 2 vCPU / 4 GB, $0.06/hour compute,
`runpod/base:1.0.2-ubuntu2204`, 20 GB disposable container disk, zero volume,
and zero GPUs. The complete workload and evidence retrieval finished before
stop and deletion. Scoped running inventory and scoped all-status inventory
both returned `[]`; Pod get returned provider 404.

No retry or replacement occurred. No S1 local or remote process remains.
Unrelated provider resources were not modified.
