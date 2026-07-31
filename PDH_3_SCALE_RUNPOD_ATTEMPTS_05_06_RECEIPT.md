# PDH-3 RunPod Attempts 05 and 06 Receipt

Both attempts were rejected before SSH, upload, or workload execution because
the provider returned 32 vCPU while the frozen R7 packet required exactly 16.
Both workers were deleted and exact-ID absence plus empty active inventory were
captured before the next worker was created.

## Attempt 05

- `POD_ID`: `05r61x5gskaa4m`
- `POD_NAME`: `ck-pdh3-scale-r1-a05`
- `RETURNED_SHAPE`: `32 vCPU / 125 GB RAM / 1x L40S`
- `RATE`: `$0.99/hour`
- `CLASSIFICATION`: `WORKER_SHAPE_MISMATCH`
- `UPLOAD_OCCURRED`: `NO`
- `WORKLOAD_OCCURRED`: `NO`
- `CREATE_RESPONSE_SHA256`:
  `9d64f02646649713bc9c2009379dfaa17dc35ec86dec0becbc63824efb98577c`
- `DELETE_RESPONSE_SHA256`:
  `a99d2bf66810f8d14aec0b64d1538a83fac26e92378a5851e501826a6cdc15b7`
- `POST_DELETE_GET_SHA256`:
  `abb343a1a20364080e68a3fa77e863e71c3dc444e3f06cb1467cdf87df479556`
- `EMPTY_ACTIVE_INVENTORY_SHA256`:
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`
- `GUARD_LOG_SHA256`:
  `93159f4c7d95d7c44816d08dc935547dd4345b5a8eedabcd2119ffc1778ed9a5`

## Attempt 06

- `POD_ID`: `qivnbqzlitxei1`
- `POD_NAME`: `ck-pdh3-scale-r1-a06`
- `RETURNED_SHAPE`: `32 vCPU / 125 GB RAM / 1x L40S`
- `RATE`: `$0.99/hour`
- `CLASSIFICATION`: `WORKER_SHAPE_MISMATCH`
- `UPLOAD_OCCURRED`: `NO`
- `WORKLOAD_OCCURRED`: `NO`
- `CREATE_RESPONSE_SHA256`:
  `d52bc237716d7666d3eee99fe667e2a2547274b207b86187fbc9cd1dedaafd64`
- `DELETE_RESPONSE_SHA256`:
  `7f4ce938d17b54f1d6d333d75d7ea6dbf65213259e179572d2c2b5937aed0d61`
- `POST_DELETE_GET_SHA256`:
  `abb343a1a20364080e68a3fa77e863e71c3dc444e3f06cb1467cdf87df479556`
- `EMPTY_ACTIVE_INVENTORY_SHA256`:
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`
- `GUARD_LOG_SHA256`:
  `d04af562cb6e7b481b6c6ce54cb61125469e8e6b149468178801d55287ab2b58`

The detached guards later emitted `EXACT_ID_ABSENT_CAMPAIGN_ACTIVE` after the
next attempt had already been created under the same campaign prefix. Those
late guard terminal events are not used as teardown proof. The controlling
proof is each exact-ID 404 plus the captured empty active inventory before its
replacement was created.
