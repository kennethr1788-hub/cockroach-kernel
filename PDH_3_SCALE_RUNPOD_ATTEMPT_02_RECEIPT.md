# PDH-3 RunPod Attempt 02 Receipt

- `ATTEMPT`: `2`
- `POD_ID`: `hjzz81j3gftatz`
- `POD_NAME`: `ck-pdh3-scale-r1-a02`
- `CREATE_UTC`: `2026-07-31T04:05:25Z`
- `CLASSIFICATION`: `NETWORK_NAMESPACE_UNAVAILABLE`
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
- `UNPRIVILEGED_NETWORK_NAMESPACE`: `BLOCKED`
- `EXACT_ERROR`: `unshare: unshare failed: Operation not permitted`
- `DELETE_RESULT`: `GREEN`
- `EXACT_ID_POST_DELETE`: `404 pod not found`
- `ACTIVE_INVENTORY_POST_DELETE`: `[]`
- `DETACHED_GUARD_TERMINAL_EVENT`: `TEARDOWN_GREEN`

Attempt 02 passed the complete provider, shape, price, SSH, and detached-guard
boundary. Before upload, its isolation canary proved this Secure GPU container
cannot create the reviewed user/network namespace. The worker was deleted
without payload transfer or workload execution.

R5 does not relabel that failure. It replaces the namespace claim with a
narrower process-tree syscall-observation contract. The full measured command
and every descendant are traced for `connect` and `sendto`; only loopback,
Unix, netlink, and AF_UNSPEC destinations are permitted by the fail-fast
observer. This is observation and termination, not a namespace or firewall.

- `RAW_PROVIDER_DETAIL_SHA256`:
  `34f1e327fe36898b48ad7d5a85a1605bcadbf3c2b6e90bec9366d000a770df81`
- `READINESS_OUTPUT_SHA256`:
  `1b73df4b864b076c4f259077e642bb62baf035acdcd8f5f4f066d51948c9d836`
- `RAW_DELETE_RESPONSE_SHA256`:
  `c38d3abbf7f4328bb398c2d5f2a1e566e73c70fb5f188f996dd4ed454d4c5751`
- `POST_DELETE_GET_SHA256`:
  `abb343a1a20364080e68a3fa77e863e71c3dc444e3f06cb1467cdf87df479556`
- `POST_DELETE_ACTIVE_INVENTORY_SHA256`:
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`
- `LIFECYCLE_GUARD_LOG_SHA256`:
  `146013cba146b197e2f710b25174f17ea87680de6fdebfaf1b303c33aaeeef88`
