# PDH-3 RunPod Attempt 04 Receipt

- `ATTEMPT`: `4`
- `POD_ID`: `w7i7acjvco7jfr`
- `POD_NAME`: `ck-pdh3-scale-r1-a04`
- `CREATE_UTC`: `2026-07-31T04:30:53Z`
- `CLASSIFICATION`: `DESTINATIONLESS_SENDTO_FALSE_POSITIVE`
- `UPLOAD_OCCURRED`: `YES`
- `MEASURED_WORKLOAD_OCCURRED`: `NO`
- `RETURNED_CLOUD/GPU`: `Secure Cloud / NVIDIA L40S`
- `RETURNED_VCPU`: `16`
- `RETURNED_RAM_GB`: `188`
- `RETURNED_GPU_COUNT`: `1`
- `RETURNED_IMAGE`:
  `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`
- `RETURNED_CONTAINER_DISK_GB`: `250`
- `RETURNED_VOLUME_GB`: `0`
- `RETURNED_COMPUTE_RATE_USD_HOUR`: `$0.99`
- `SSH_READINESS`: `GREEN`
- `BUNDLE_AND_PACKET_HASHES`: `GREEN`
- `VENDORED_STRACE_PROVENANCE`: `GREEN`
- `CLASSIFIER_CANARY`: `GREEN`
- `REAL_TRACE_WRAPPER_CANARY`: `NOT_GREEN`
- `DELETE_RESULT`: `GREEN`
- `EXACT_ID_POST_DELETE`: `404 pod not found`
- `ACTIVE_INVENTORY_POST_DELETE`: `[]`
- `DETACHED_GUARD_TERMINAL_EVENT`: `TEARDOWN_GREEN`

The real wrapper canary observed a loopback `connect`, followed by a
destinationless `sendto(..., NULL, 0)` on that connected socket. R6 treated
the destinationless send as an unparseable destination even though its routing
authority was the preceding observed loopback connect. The wrapper returned
non-green, no 60-second controller canary or measured workload began, and the
worker was deleted.

R7 permits only the exact destinationless `sendto` form because tracing starts
before exec and follows every descendant: any external connected socket must
first produce an independently classified external `connect`, which remains a
hard stop. Explicit external `sendto` destinations and every other unparseable
destination remain blocked.

- `RAW_CREATE_RESPONSE_SHA256`:
  `ecd36e800f916be9b16450a469cda30b9871e6154f2d23236b3aee94ded16758`
- `RAW_PROVIDER_DETAIL_SHA256`:
  `26f5e4d6e0857544d68546c690975dfa7dd8fcd61456c1a86d6a88ff175bdd37`
- `READINESS_OUTPUT_SHA256`:
  `8905f879836dc29c3a5e56ef1e952886a3efa3237bf62fc9197b9bcedbc13350`
- `UPLOAD_HASHES_SHA256`:
  `d3bc96b979d9a9c453483cff718ec8637c72a57015da9a8ff391447a43106fdb`
- `STRACE_CANARY_SHA256`:
  `05baaf89173973ebb7a664884178b04cbc592e0010a82c3d56db105df51720d3`
- `REAL_TRACE_CANARY_DEBUG_SHA256`:
  `1c9580fd0a4fc47c571c2d0f837595e5fb2612ff759eea5fe9fcc61669812262`
- `RAW_DELETE_RESPONSE_SHA256`:
  `28075c53383d9f5c2eb29af2ccf6a716f45eb77d13ff38e011b51ae8c19e4328`
- `POST_DELETE_GET_SHA256`:
  `abb343a1a20364080e68a3fa77e863e71c3dc444e3f06cb1467cdf87df479556`
- `POST_DELETE_ACTIVE_INVENTORY_SHA256`:
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`
- `LIFECYCLE_GUARD_LOG_SHA256`:
  `948ad6f295e9abe0e78a87c7335f76762ce4659155eac29bb81cbb7892441904`
