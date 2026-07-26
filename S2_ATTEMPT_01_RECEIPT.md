# S2 RunPod Attempt 01 Receipt

- `CAMPAIGN_ID`: `CK-S2-20260726-ORCHESTRATION-R1`
- `ATTEMPT`: `1`
- `POD_ID`: `btdc8bhvws6cbs`
- `POD_NAME`: `ck-s2-20260726-r1-a1`
- `CREATED_UTC`: `2026-07-26T02:12:25.816Z`
- `TEARDOWN_GREEN_UTC`: `2026-07-26T02:15:07Z`
- `RETURNED_SHAPE`: `2 vCPU / 4 GiB / 0 GPU`
- `IMAGE`: `runpod/base:1.0.2-ubuntu2204`
- `CONTAINER_DISK_GB`: `20`
- `PERSISTENT_OR_NETWORK_VOLUME_GB`: `0`
- `COMPUTE_RATE_USD_PER_HOUR`: `0.06`
- `MAXIMUM_ACTIVE_RATE_USD_PER_HOUR`: `0.085`
- `CALCULATED_MAXIMUM_USD`: `0.003825`
- `PROVIDER_BILLING_QUERY`: `[]` (delayed/unavailable itemization)
- `CAMPAIGN_READY`: `NO`
- `WORKLOAD_STARTED`: `NO`
- `RESULT`: `BLOCKED`
- `BLOCKER`: `EXECUTOR_USED_STALE_BINARY_HASH_AFTER_UPLOAD`

## Custody and verification

The exact scanned archive was uploaded after worker and guard verification.
Remote archive SHA-256 matched
`a35a6786b5d88393ee13cad83ad742759062c0b7b567062aa9bfbbbd3c725273`.
The 61-file transfer manifest passed in full. The Linux runtime archive matched
`3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`.

The authoritative frozen binary SHA-256 in
`S2_TRANSFER_AND_INVENTORY_RECEIPT.md` and `S2_PREFLIGHT_PACKET_R3.md` is:

`97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`

The extracted remote binary produced exactly that hash and identified itself as
CockroachDB v26.2.3, linux amd64, build commit
`90d3b6080727dc810224a99903cb2e88b81e91ae`.

The executor instead checked it against stale resumed-summary data:

`97a8836b5b659caeae1b8f3cc1971c6e459e0ab23fa8e71dee10842c6d890068`

That comparison failed, and the executor deleted the worker before rereading
the authoritative receipt. This was not a runtime or product failure. It was a
control-plane execution error caused by trusting recalled summary data over the
frozen local source.

Because payload upload had already occurred, the prompt's retry authority had
expired permanently. No replacement worker or second campaign is authorized.

## Lifecycle guard terminal chain

```jsonl
{"details":{"campaign_prefix":"ck-s2-20260726-r1-","cli_sha256":"a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037","delete_epoch":1785060600,"name":"ck-s2-20260726-r1-a1","pod_id":"btdc8bhvws6cbs","stop_epoch":1785060000},"event":"BOUND","event_hash":"ae675c46e880e540634b097e6fd9f4e08027f6966c5baf67638f46b9c407d143","monotonic_seconds":3.669,"previous_hash":"0000000000000000000000000000000000000000000000000000000000000000","schema_version":"s2-guard-v1","sequence":1,"utc":"2026-07-26T02:12:49Z"}
{"details":{"pod_id":"btdc8bhvws6cbs","provider_record_hash":"3552927bb3d81a4709cf1c7eb468ee6081486aa6109c62a978eb3515bfcc4c6f","provider_state":"RUNNING","seconds_to_delete":28627,"seconds_to_stop":28027},"event":"HEARTBEAT","event_hash":"a8dd3182cfad2128905b4df6a4609c6130a03f3c64f94b70dd04c48819dba93a","monotonic_seconds":7.196,"previous_hash":"ae675c46e880e540634b097e6fd9f4e08027f6966c5baf67638f46b9c407d143","schema_version":"s2-guard-v1","sequence":2,"utc":"2026-07-26T02:12:53Z"}
{"details":{"pod_id":"btdc8bhvws6cbs","provider_record_hash":"6e7f704c47af0b72efd3c95d25122661611ea1e4c5d44c56ec1911f2e16ce70d","provider_state":"RUNNING","seconds_to_delete":28594,"seconds_to_stop":27994},"event":"HEARTBEAT","event_hash":"21b27cc4db07fc2e430f35adfe5a6f99d79e13a2a648630b21a58479904d7b4a","monotonic_seconds":40.792,"previous_hash":"a8dd3182cfad2128905b4df6a4609c6130a03f3c64f94b70dd04c48819dba93a","schema_version":"s2-guard-v1","sequence":3,"utc":"2026-07-26T02:13:26Z"}
{"details":{"pod_id":"btdc8bhvws6cbs","provider_record_hash":"6e7f704c47af0b72efd3c95d25122661611ea1e4c5d44c56ec1911f2e16ce70d","provider_state":"RUNNING","seconds_to_delete":28560,"seconds_to_stop":27960},"event":"HEARTBEAT","event_hash":"6a2b052bd16ea71657fc1c047a5c128ba275a203cdac842b3bb779669aed8ff8","monotonic_seconds":74.388,"previous_hash":"21b27cc4db07fc2e430f35adfe5a6f99d79e13a2a648630b21a58479904d7b4a","schema_version":"s2-guard-v1","sequence":4,"utc":"2026-07-26T02:14:00Z"}
{"details":{"pod_id":"btdc8bhvws6cbs","provider_record_hash":"6e7f704c47af0b72efd3c95d25122661611ea1e4c5d44c56ec1911f2e16ce70d","provider_state":"RUNNING","seconds_to_delete":28527,"seconds_to_stop":27927},"event":"HEARTBEAT","event_hash":"6b87d97452d841e0234c5a3e8a144180409e8e191a047399c63b1f8f676850af","monotonic_seconds":107.778,"previous_hash":"6a2b052bd16ea71657fc1c047a5c128ba275a203cdac842b3bb779669aed8ff8","schema_version":"s2-guard-v1","sequence":5,"utc":"2026-07-26T02:14:33Z"}
{"details":{"campaign_active":[],"exact_id_absent":true},"event":"TEARDOWN_GREEN","event_hash":"56e78604b1e63f7d111604bc6efc6ae046010e119a62b04057c180c794429540","monotonic_seconds":141.093,"previous_hash":"6b87d97452d841e0234c5a3e8a144180409e8e191a047399c63b1f8f676850af","schema_version":"s2-guard-v1","sequence":6,"utc":"2026-07-26T02:15:07Z"}
```

- `GUARD_LOG_SHA256`: `672ee8ef37d6bbb5e08c21d68eb7482f5f0ee20b96b11e781c168ea0e2493868`
- `EXACT_ID_LOOKUP`: `404 pod not found`
- `CAMPAIGN_ALL_STATUS_INVENTORY`: `[]`
- `S2_GUARD_PROCESS_REMAINS`: `NO`
- `UNRELATED_RESOURCE_TOUCHED`: `NO`

## Billing

The provider billing query for this exact Pod and interval returned `[]`.
Using 162 seconds as a conservative paid-lifetime ceiling and the frozen
$0.085/hour maximum active rate yields a deterministic `CALCULATED_MAXIMUM` of
$0.003825. This is not an exact provider charge.

## Resume gate

Fresh explicit authorization is required for a replacement campaign. Any new
authorization must freeze corrected future lifecycle deadlines, preserve this
failed attempt, prohibit use of recalled hashes, and require verification
values to be read directly from the frozen receipt at command construction.
