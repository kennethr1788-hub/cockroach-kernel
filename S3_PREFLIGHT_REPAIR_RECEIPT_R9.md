# S3 Preflight Repair Receipt R9

- `PARENT_PACKET`: `S3_PREFLIGHT_PACKET_R8.md`
- `PARENT_PACKET_SHA256`: `318f5fcadf4d30df11261ede0beb2b816fe7ba0b688b3a6e550b621bb175246a`
- `R8_GLM_VERDICT`: `GREEN_INVALIDATED_BY_R9_PACKET_CHANGE`
- `R8_CLAUDE_VERDICT`: `GREEN_INVALIDATED_BY_R9_PACKET_CHANGE`
- `STATUS`: `R9_DELETE_EPOCH_FIELD_REPAIRED_JUDGES_PENDING`
- `ATTEMPT_A02_RESULT`: `PREUPLOAD_LIFECYCLE_SCHEDULE_FIELD_MISSING_DELETED`
- `UPLOAD_STARTED`: `NO`
- `WORKLOAD_STARTED`: `NO`
- `UTC_RECORDED`: `2026-07-27T01:27:34Z`

## Finding

The R8 wiring requires `DELETE_EPOCH` for the lifecycle guard, host
coordinator, bridge, and coordinator guard, and says the execution schedule is
its authority. The R8 schedule contained the provider termination epoch but no
field named `delete_epoch`. Inferring the missing value at runtime would have
violated the frozen no-recomputation rule. A02 was therefore deleted unused.

## Correction

R9 adds one explicit schedule field:

```text
delete_epoch = provider_terminate_epoch = 1785162300
```

This binds all host-local deletion/cleanup guards to the already frozen final
provider termination deadline. It changes no timestamp, campaign ID, attempt
name, worker shape, rate, bundle, source, threshold, credential boundary,
cloud call, or production duration. The field is parse-gated and its new
schedule hash is propagated into the runtime-hash record. R8 verdicts are
historical after this byte change. A03 is forbidden until fresh GLM and Claude
GREEN verdicts exist over one R9 packet hash.
