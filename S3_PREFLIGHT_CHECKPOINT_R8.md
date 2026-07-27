# S3 Preflight Checkpoint R8

- `STATE`: `LOCAL_GREEN_INDEPENDENT_JUDGES_PENDING`
- `LAST_GREEN_GATE`: `CK_P9_INTEGRATION_GREEN`
- `S3_PREFLIGHT_R8_REPAIR_COMMIT`: `95408fb9386ced25b468c0957e86e8f73cb123e9`
- `R7_PACKET_SHA256_HISTORICAL`: `94b449510eecbdb7f6a6d961375412950cdcd566196e004290b9fb62149125f2`
- `R7_JUDGE_STATE`: `GREEN_BOTH_INVALIDATED_BY_R8_PACKET_CHANGE`
- `P9_PACKET_SHA256`: `9f1e007df3626f20ffdf98387ca03321ef0e2339279c9e03e58959f9dc55abbb`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `SCHEDULE_SHA256`: `f44ff1a4a1b19183f93735577a63fd5bdff3ea93ed49d592c9ca9382a0d34700`
- `S3_TESTS`: `12_OF_12_GREEN`
- `P9_CLOUD_REGRESSION_SUBSET`: `113_OF_113_GREEN`
- `WORKER_BUNDLE_SHA256`: `c0f0514c09d63da833361ec34ef2cbc2f0e96c210fca043cbc7d3c33a8e703d4`
- `HOST_BUNDLE_SHA256`: `97357e45e8eba6e7763c8f493cb30f228ecb5ad8a552b9c7f71c1e4bc567f8c8`
- `ATTEMPT_A01_RESULT`: `PREUPLOAD_WORKER_SHAPE_MISMATCH_DELETED`
- `ATTEMPT_A01_POD_ID`: `bre4wr6bkeoya1`
- `RUNPOD_S3_SCOPED_INVENTORY_AFTER_A01`: `[]`
- `RUNPOD_ATTEMPTS`: `1`
- `RUNPOD_EXPOSURE`: `CALCULATED_MAXIMUM_$0.001667`
- `UTC_RECORDED`: `2026-07-27T01:06:58Z`

R8 accepts only the two worker shapes already authorized by the controlling
prompt. The 4-GiB sufficiency finding is backed by the completed S2 six-hour
maximum RSS and the unchanged S3 RSS enforcement ceiling. No workload source,
bundle, threshold, cloud boundary, campaign ID, attempt name, or deadline
changed. No A02 worker may be created until GLM and Claude return GREEN on the
exact same R8 packet hash.
