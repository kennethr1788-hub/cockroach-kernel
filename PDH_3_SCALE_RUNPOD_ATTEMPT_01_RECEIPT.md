# PDH-3 RunPod Attempt 01 Receipt

- `ATTEMPT`: `1`
- `POD_ID`: `xc0teveqftq5dr`
- `POD_NAME`: `ck-pdh3-scale-r1-a01`
- `CREATE_UTC`: `2026-07-31T04:00:06Z`
- `CLASSIFICATION`: `RETURNED_HOST_MEMORY_OUTSIDE_EXACT_R3_CONTRACT`
- `UPLOAD_OCCURRED`: `NO`
- `WORKLOAD_OCCURRED`: `NO`
- `RETURNED_CLOUD/GPU`: `Secure Cloud / NVIDIA L40S`
- `RETURNED_VCPU`: `16`
- `RETURNED_RAM_GB`: `188`
- `RETURNED_GPU_COUNT`: `1`
- `RETURNED_IMAGE`:
  `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`
- `RETURNED_CONTAINER_DISK_GB`: `250`
- `RETURNED_VOLUME_GB`: `0`
- `RETURNED_COMPUTE_RATE_USD_HOUR`: `$0.99`
- `DELETE_RESULT`: `GREEN`
- `EXACT_ID_POST_DELETE`: `404 pod not found`
- `ACTIVE_INVENTORY_POST_DELETE`: `[]`

Attempt 01 satisfied every provider and economic property except the R3
packet's exact `94 GB` RAM assertion. The provider returned `188 GB` at the
same rate. The worker was deleted immediately before SSH readiness, upload,
namespace work, or workload execution.

The raw creation response is retained locally because it contains the
operator's public SSH-key material. It is not copied into this packet.

- `RAW_CREATE_RESPONSE_SHA256`:
  `7f287f989f7d342f2a380ae71688bd01952eba60fa773a534facc19780c5811c`
- `RAW_DELETE_RESPONSE_SHA256`:
  `fe442e5df00f39b43edb79d73c0b535415d0a999a55fd0576fde6f5404b67eef`
- `POST_DELETE_GET_SHA256`:
  `abb343a1a20364080e68a3fa77e863e71c3dc444e3f06cb1467cdf87df479556`
- `POST_DELETE_ACTIVE_INVENTORY_SHA256`:
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`

R4 accepts the observed current provider range of 94 through 188 GB only;
it does not relax the GPU, vCPU, image, storage, rate, duration, volume,
credential, evidence, retry, or teardown boundary.
