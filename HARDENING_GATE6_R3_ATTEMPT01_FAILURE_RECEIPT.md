# Hardening Gate 6 R3 — Attempt 01 Failure and Teardown Receipt

- `STATUS`: `FAILED_BEFORE_MEASURED_ROW_1; TEARDOWN_GREEN`
- `POD_ID`: `e5bvtk4s4y7yc0`
- `POD_NAME`: `ck-gate6-20260727-r3-a01`
- `CREATED_UTC`: `2026-07-28T02:16:57Z`
- `TEARDOWN_GREEN_UTC`: `2026-07-28T02:24:43Z`
- `WORKER`: `CPU; 2_VCPU; 4_GIB; 0_GPU; 0_VOLUME; 20_GIB_CONTAINER_DISK`
- `IMAGE`: `runpod/base:1.0.2-ubuntu2204`
- `RATE_USD_PER_HOUR`: `0.06`
- `KNOWN_LIFETIME_SECONDS_MAX`: `466`
- `BOUNDED_COST_AT_ACTIVE_RATE_CEILING_USD_MAX`: `0.012945`
- `EXACT_PROVIDER_CHARGE`: `PENDING; BILLING_QUERY_RETURNED_EMPTY_AFTER_DELETION`
- `CAPABILITY_CANARY`: `GREEN`
- `CANARY_RECORD_SHA256`: `8940387642d55e1fa43e70e193417cedf2ac94fb713abad7bc2141004e16744d`
- `CANARY_FILE_SHA256`: `7e8e1a83bb372e47278d4bed76d786bcd9f7b698ae7ab314202119761d3a9191`
- `PAYLOAD_ARCHIVE_SHA256`: `fd4449d7e7fb5ca4b3d1d149dfc7cec5e7b0bf29122324805dfeb1f78d827766`
- `PAYLOAD_TREE_SHA256`: `5ef2a108c83cfcb996019512a139d81464b747fbcd6175a25684c7f846ee54bc`
- `NON_MEASURED_SMOKE`: `GREEN`
- `MEASURED_EXECUTIONS`: `0`
- `FAILURE`: `ISOLATION_ATTESTATION_BINDING_INVALID`
- `ROOT_CAUSE`: `R3_VALIDATOR_COMPARED_WHOLE_FILE_SHA256_TO_EMBEDDED_CANONICAL_RECORD_SHA256`
- `FAILED_EVIDENCE_ARCHIVE_SHA256`: `8a8a09c78b762cb752eca81da6a8937bf869011d71dc6fdf1aa442b7ad10d126`
- `LIFECYCLE_CHAIN_SHA256`: `b96cd442b098f727030fe2e411c26c169808909211acb90497fd8bf6f914f044`
- `MEASURED_STDERR_SHA256`: `8dcdaf53789b82edf07559cd692e2f1c19da5af015bb3842d42388abddef070a`
- `STOP_RESULT`: `success`
- `DELETE_RESULT`: `success`
- `EXACT_ID_LOOKUP_AFTER_DELETE`: `not_found`
- `RUNNING_INVENTORY_AFTER_DELETE`: `[]`
- `DETACHED_GUARD_AFTER_DELETE`: `stopped`
- `GATE7`: `FORBIDDEN`

The live canary and non-measured smoke proved the seccomp boundary itself. The
measured orchestrator then rejected its fresh isolation record before creating
the output campaign or executing a row. This receipt does not claim measured
evidence. The whole-file hash and embedded canonical-record hash are different
integrity domains; the corrected validator now requires canonical bytes and
binds the embedded record hash exported by the launcher. A replacement worker
requires a new scanner-clean packet and fresh GLM plus AGY same-hash GREEN.
