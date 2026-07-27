# S3 Preflight Checkpoint R6

- `STATE`: `LOCAL_GREEN_INDEPENDENT_JUDGES_PENDING`
- `LAST_GREEN_GATE`: `CK_P9_INTEGRATION_GREEN`
- `S3_PREFLIGHT_R6_REPAIR_COMMIT`: `8b1d5bd1038588527bd994eb8fcb5467cac47eac`
- `R5_PACKET_SHA256`: `5254f701c3e2fe1d745592eb097ca5d25817afdf3a5b709ac2e95fe5d8db30ee`
- `R5_GLM_STATE`: `GREEN_INVALIDATED_BY_CLAUDE_BLOCKER_AND_PACKET_CHANGE`
- `R5_CLAUDE_STATE`: `BLOCKED`
- `P9_PACKET_SHA256`: `9f1e007df3626f20ffdf98387ca03321ef0e2339279c9e03e58959f9dc55abbb`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `SCHEDULE_SHA256`: `cbd8c1dc28314d0cf9d901701661ee9fa3388b71a3807159b142af95f11e3cff`
- `S3_TESTS`: `12_OF_12_GREEN`
- `P9_CLOUD_REGRESSION_SUBSET`: `113_OF_113_GREEN`
- `WORKER_BUNDLE_SHA256`: `c0f0514c09d63da833361ec34ef2cbc2f0e96c210fca043cbc7d3c33a8e703d4`
- `HOST_BUNDLE_SHA256`: `97357e45e8eba6e7763c8f493cb30f228ecb5ad8a552b9c7f71c1e4bc567f8c8`
- `RUNPOD_S3_SCOPED_INVENTORY`: `[]`
- `RUNPOD_ATTEMPTS`: `0`
- `RUNPOD_EXPOSURE`: `$0.00`
- `UTC_RECORDED`: `2026-07-27T00:37:25Z`

The bridge and coordinator now use one atomic request-staging convention, and
the direct topology test holds the partial stage file visible across multiple
coordinator scans. This checkpoint cannot authorize creation until GLM and
Claude return GREEN on the exact R6 packet.
