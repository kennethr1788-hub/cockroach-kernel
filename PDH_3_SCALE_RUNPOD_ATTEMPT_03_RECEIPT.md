# PDH-3 RunPod Attempt 03 Receipt

- `ATTEMPT`: `3`
- `POD_ID`: `7h1f0w824dlm2r`
- `POD_NAME`: `ck-pdh3-scale-r1-a03`
- `CREATE_UTC`: `2026-07-31T04:16:28Z`
- `CLASSIFICATION`: `STRACE_UNAVAILABLE_IN_BASE_IMAGE`
- `UPLOAD_OCCURRED`: `NO`
- `WORKLOAD_OCCURRED`: `NO`
- `RETURNED_CLOUD/GPU`: `Secure Cloud / NVIDIA L40S`
- `RETURNED_VCPU`: `16`
- `RETURNED_RAM_GB`: `125`
- `RETURNED_GPU_COUNT`: `1`
- `RETURNED_IMAGE`:
  `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`
- `RETURNED_CONTAINER_DISK_GB`: `250`
- `RETURNED_VOLUME_GB`: `0`
- `RETURNED_COMPUTE_RATE_USD_HOUR`: `$0.99`
- `SSH_READINESS`: `GREEN`
- `STRACE_IN_IMAGE`: `NO`
- `DELETE_RESULT`: `GREEN`
- `EXACT_ID_POST_DELETE`: `404 pod not found`
- `ACTIVE_INVENTORY_POST_DELETE`: `[]`
- `DETACHED_GUARD_TERMINAL_EVENT`: `TEARDOWN_GREEN`

Attempt 03 passed the provider, shape, price, SSH, and detached-guard boundary.
The image did not contain `strace`, so it was deleted without package
installation, payload upload, or workload execution.

R6 vendors the exact Ubuntu Noble `strace` and `libunwind8` packages inside the
credential-free deterministic archive. They are extracted under the disposable
campaign root without installing or mutating the image. Their official package
index, package bytes, and extracted tracer binary are all SHA-256 bound.

- `RAW_CREATE_RESPONSE_SHA256`:
  `b2f0a2ddc459e8889c42899040a97bc02f47b5e313d046ab125ed4fbc8f75ab6`
- `RAW_PROVIDER_DETAIL_SHA256`:
  `ec3f947e75ea08ad9c9fa0a524af4e17077c24357998658ecb308887878c787f`
- `READINESS_OUTPUT_SHA256`:
  `3dfa3fb239f56c778a1e9b33eb31328349edd155a95806dac4378904e88527e5`
- `RAW_DELETE_RESPONSE_SHA256`:
  `5af628221bebce27e5e62b3991f78271a9bac1f6025fd84af327b5ca9ee8442b`
- `POST_DELETE_GET_SHA256`:
  `abb343a1a20364080e68a3fa77e863e71c3dc444e3f06cb1467cdf87df479556`
- `POST_DELETE_ACTIVE_INVENTORY_SHA256`:
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`
- `LIFECYCLE_GUARD_LOG_SHA256`:
  `9f3b20850eb97a7f3aa9095eba889c20bf87edb5318511ed5533558c44a3414d`
