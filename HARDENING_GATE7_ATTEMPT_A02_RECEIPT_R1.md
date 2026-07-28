# Hardening Gate 7 Attempt A02 Receipt R1

- `STATUS`: `NON_RETRYABLE_TRANSFER_BUNDLE_HARNESS_DEFECT_TEARDOWN_GREEN`
- `POD_ID`: `5rlcj1ublnt54k`
- `POD_NAME`: `ck-g7r2-20260728-a02`
- `CREATED_UTC`: `2026-07-28T16:10:53Z`
- `DELETED_UTC`: `2026-07-28T16:24:57Z`
- `RETURNED_SHAPE`: `CPU; 2 vCPU; 4 GiB RAM; 0 GPU`
- `IMAGE`: `runpod/base:1.0.2-ubuntu2204`
- `CONTAINER_DISK_GB`: `20`
- `VOLUME_GB`: `0`
- `COMPUTE_RATE_USD_PER_HOUR`: `0.06`
- `CANONICAL_HOST_KEY_SET_SHA256`: `515a5050b6dbce8c935b9658e8cbe07dc907d3247515bd44b55992897972ba92`
- `EXPECTED_ARCHIVE_BYTES`: `144518714`
- `OBSERVED_ARCHIVE_BYTES`: `144518714`
- `EXPECTED_ARCHIVE_SHA256`: `2503e7a848f555d20c6a73aacdeda8fe972873fd06c703a873ca300539a76b22`
- `OBSERVED_ARCHIVE_SHA256`: `2503e7a848f555d20c6a73aacdeda8fe972873fd06c703a873ca300539a76b22`
- `PAYLOAD_TREE_FILE_COUNT`: `86`
- `PAYLOAD_TREE_VERDICT`: `GREEN`
- `LINUX_ARCHIVE_SHA256`: `3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`
- `LINUX_BINARY_SHA256`: `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`
- `LINUX_RUNTIME`: `CockroachDB v26.2.3; linux amd64`
- `PAYLOAD_ACCEPTED`: `YES`
- `CAMPAIGN_READY`: `NO`
- `HIDDEN_SEED_CREATED`: `NO`
- `MEASURED_CAMPAIGN_STARTED`: `NO`
- `NON_MEASURED_CANARY_STARTED`: `NO; dependency failure occurred before generation`
- `FAILURE_CLASS`: `HARNESS_OR_TRANSFER_BUNDLE_DEFECT`
- `MISSING_REQUIRED_PATH`: `hardening-gate5/heldout_contract.py`
- `DEPENDENCY_CHAIN`: `prepare_hidden_campaign.py -> generate_expanded_inputs.py -> make_vectors.py -> hardening-gate5/heldout_contract.py`
- `TRANSFER_ALLOWLIST_DEFECT`: `build_expanded_bundle.py omitted the required dependency`
- `IN_PLACE_PATCH_PERFORMED`: `NO`
- `REPLACEMENT_WORKER_CREATED`: `NO`
- `EXACT_ID_ABSENT`: `YES; provider 404`
- `ACTIVE_CAMPAIGN_INVENTORY`: `[]`
- `GUARD_FINAL_EVENT`: `TEARDOWN_GREEN`
- `LIFECYCLE_LOG_SHA256`: `b53185d8761f11093a05ac006f6f117207cddda23047f9f250e31bb7300d0243`
- `PREDELETE_INVENTORY_SHA256`: `b1c6abef6269ed4010ed8782260b51d637019a4687eaf70a09f9b42bfd719d51`
- `POSTDELETE_POD_LIST_SHA256`: `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`
- `BILLING_ITEMIZATION`: `DELAYED_OR_NOT_RECONCILED`
- `MAXIMUM_MATHEMATICAL_CHARGE_USD`: `0.0141`
- `RETRY_ALLOWED_UNDER_CURRENT_PACKET`: `NO`

The exact archive and all 86 allowlisted files transferred and hash-verified.
The Linux archive and extracted binary also matched the exact frozen host bytes.
During `CAMPAIGN_READY` execution, the public non-measured canary generator
could not start because its transitive `hardening-gate5/heldout_contract.py`
dependency was absent from the frozen transfer bundle. The same omission would
prevent hidden input generation.

The approved payload was not altered after acceptance. No hidden seed was
created, no scored row ran, and no live measured campaign started. The worker
was stopped and deleted. Exact-ID absence, empty active inventory, and the
guard's hash-chained `TEARDOWN_GREEN` event were verified.

The governing authorization classifies a harness/schema/oracle defect as
non-retryable. Repair requires a new bundle revision, an extracted-bundle
campaign-ready smoke, refreshed hashes, a new frozen packet, and fresh
same-hash GLM/AGY GREEN before any replacement worker.
