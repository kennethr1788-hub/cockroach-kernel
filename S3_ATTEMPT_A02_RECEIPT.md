# S3 Attempt A02 Receipt

- `ATTEMPT`: `2_OF_8`
- `POD_ID`: `9fsp8yrrfxraki`
- `POD_NAME`: `ck-s3-20260727-r1-a02`
- `CREATED_UTC`: `2026-07-27T01:25:28.622Z`
- `RESULT`: `PREUPLOAD_LIFECYCLE_SCHEDULE_FIELD_MISSING`
- `RETURNED_SHAPE`: `2_VCPU_4_GIB_CPU`
- `RETURNED_COMPUTE_RATE_USD_PER_HOUR`: `$0.06`
- `UPLOAD_STARTED`: `NO`
- `WORKLOAD_STARTED`: `NO`
- `CREATE_RESPONSE_SHA256`: `c52d863b4975a6d802fe5e5621f86923c1908c4fbaaef717f29c9a8d4dba98a1`
- `GET_RESPONSE_SHA256`: `d020b42ce9676b2090fa8efb637417ff6d0ad714877d9b03c5e36aa9f8e3f59a`
- `STOP_RESPONSE_SHA256`: `b78595fc67123d79ef2c31ed6a4e33ca36f2a3958e0519dd012c042c9db6022b`
- `DELETE_RESPONSE_SHA256`: `c683f859a6144f345cce3d43c1ded0970c3b89a25f8d4a42b120ec452af81f80`
- `STOPPED_AND_DELETED_UTC`: `2026-07-27T01:27:34Z`
- `EXACT_ID_LOOKUP_AFTER_DELETE`: `404_ABSENT`
- `S3_SCOPED_INVENTORY_AFTER_DELETE`: `[]`
- `CALCULATED_MAXIMUM_USD`: `$0.002222`
- `CUMULATIVE_CALCULATED_MAXIMUM_USD`: `$0.003889`
- `RETRY_CLASSIFICATION`: `EXACT_ID_GUARD_STARTUP_CONTRACT_DEFECT_RETRYABLE_PRESTART`

A02 matched the independently approved R8 worker shape and became SSH
addressable. Before upload, exact lifecycle-guard argument resolution exposed
that `S3_EXECUTION_WIRING_R1.md` names `DELETE_EPOCH` as a mandatory
schedule-owned value while `S3_EXECUTION_SCHEDULE_R1.json` omitted that field.
No deadline was inferred. A02 was stopped and deleted before guard start,
upload, extraction, coordinator start, smoke, or production. Exact-ID lookup
returned 404 and the S3-scoped inventory was empty.
