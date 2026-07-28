# Hardening Gate 6 R3 — Attempt 02 Failure and Teardown Receipt

- `STATUS`: `FAILED_BEFORE_MEASURED_ROW_1; TEARDOWN_GREEN`
- `POD_ID`: `iyr2mi9jf9p6p7`
- `POD_NAME`: `ck-gate6-20260727-r3-a02`
- `CREATED_UTC`: `2026-07-28T02:35:14Z`
- `TEARDOWN_GREEN_UTC`: `2026-07-28T02:39:15Z`
- `WORKER`: `CPU; 2_VCPU; 4_GIB; 0_GPU; 0_VOLUME; 20_GIB_CONTAINER_DISK`
- `IMAGE`: `runpod/base:1.0.2-ubuntu2204`
- `RATE_USD_PER_HOUR`: `0.06`
- `KNOWN_LIFETIME_SECONDS_MAX`: `241`
- `BOUNDED_COST_AT_ACTIVE_RATE_CEILING_USD_MAX`: `0.006695`
- `EXACT_PROVIDER_CHARGE`: `PENDING`
- `CAPABILITY_CANARY`: `GREEN`
- `PAYLOAD_ARCHIVE_SHA256`: `88bbf3779d896dc488e76235429a3d9044a7f3c4ad5c2c4ab2d37a51c1eb4225`
- `PAYLOAD_TREE_SHA256`: `27e71d0f723fb8fa91ca9ce131f516b2cd281b63366c7fde350b67525ccb8cf5`
- `FIRST_SMOKE`: `INVALID_OPERATOR_INPUT; MALFORMED_CANDIDATE_ID; NOT_COUNTED`
- `CORRECTED_FRESH_ROOT_SMOKE`: `GREEN; EXACT_CANDIDATE_8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `MEASURED_EXECUTIONS`: `0`
- `FAILURE`: `PYTHON_PROVENANCE_DRIFT`
- `ROOT_CAUSE`: `PROVENANCE_BOUND_UNRESOLVED_/usr/bin/python3_WHILE_VALIDATOR_RESOLVED_/usr/bin/python3.10`
- `FAILED_EVIDENCE_ARCHIVE_SHA256`: `a9b2569801c5e42b9cbc0c0136db2d73a04cd37b5b6d2c52d8e0fb02741f0bc3`
- `LIFECYCLE_CHAIN_SHA256`: `1b58676694a6ae5094b3482922aaf63a6d87c2497cf4b4fc592a0c0b64ac56e5`
- `MEASURED_STDERR_SHA256`: `181871bb11c5b89a068b10851d245886f283b298794cac578be8dc9ea8cc65a0`
- `STOP_RESULT`: `success`
- `DELETE_RESULT`: `success`
- `EXACT_ID_LOOKUP_AFTER_DELETE`: `not_found`
- `RUNNING_INVENTORY_AFTER_DELETE`: `[]`
- `DETACHED_GUARD_AFTER_DELETE`: `stopped`

The corrected attestation binding passed and the orchestrator advanced to tool
validation, then stopped before output-root creation or row execution. The
Python binary hash and version matched, but `Path.resolve()` produced
`/usr/bin/python3.10` while the record named `/usr/bin/python3`. The first smoke
used an invalid operator-supplied candidate ID and is explicitly excluded; a
fresh-root corrected smoke passed before measurement. No measured evidence is
claimed from this attempt.
