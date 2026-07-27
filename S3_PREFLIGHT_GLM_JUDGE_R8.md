# VERDICT: GREEN

PACKET_SHA256: 318f5fcadf4d30df11261ede0beb2b816fe7ba0b688b3a6e550b621bb175246a

## Recusal
Clear. The packet names Codex as principal author/integrator of the S3-only harness, with Kimi K3 / Vibe / Devstral as bounded contributors; the Claude lane is designated solely as a judge. No authoring or material shaping by this family.

## Blockers
None identified.

## Grounded safety review

**R8 correction scope (S3_PREFLIGHT_REPAIR_RECEIPT_R8.md, S3_PREFLIGHT_CHECKPOINT_R8.md):** The only R8 change broadens accepted worker memory from 8 GiB only to the two shapes already listed in the controlling authorization (4 GiB at ≤ \$0.06/hr or 8 GiB at ≤ \$0.08/hr). The receipt states no source, bundle, threshold, schema, cloud boundary, campaign ID, attempt name, or deadline changed. R7 verdicts are explicitly invalidated; A02 is gated on fresh GLM + Claude GREEN over the R8 bytes.

**4-GiB sufficiency (S3_PREFLIGHT_REPAIR_RECEIPT_R8.md, S3_LOCAL_PREFLIGHT_RECEIPT_R1.md):** Backed by the completed S2 six-hour peak RSS of 836,284,416 bytes against the unchanged frozen S3 RSS ceiling of 1,610,612,736 bytes; 4 GiB exceeds both without relaxing any threshold.

**Credential separation (S3_CONTRACT_R1.md, S3_RESOURCE_ALLOWLIST_R1.json, s3-soak/protocol.py, s3-soak/worker.py, s3-soak/cloud_adapter.py):** Worker has no AWS/CockroachDB client; forbidden worker fields enumerate arn/command/credential/destination/path/shell/sql/url. Coordinator-side task IDs are validated against a fixed two-element set in `_cleanup_sql`; cockroach host is regex-locked to `*.cockroachlabs.cloud`; AWS pinned to `us-west-2` / profile `ck-s3`. Protocol is canonical, size-bounded (16 KiB), sequence/hash-bound, and rejects unknown fields and operation/sequence mismatch.

**Cost/lifecycle bounds (S3_EXECUTION_SCHEDULE_R1.json, S3_THRESHOLDS_R1.json, S3_CONTRACT_R1.md):** Active rate ≤ \$0.10/hr, aggregate ≤ \$3.00, successful-worker lifetime ≤ 14 hr, production exactly 43,200 s, max 8 creation attempts, 1 simultaneous worker, 1 production attempt. Cumulative RunPod exposure after A01 recorded as \$0.001667; 7 creation attempts remain in the 90-minute window.

**Call ceilings (S3_EXECUTION_WIRING_R1.md, s3-soak/host_coordinator.py, s3-soak/cloud_adapter.py):** Lambda ceiling 12 and Cockroach ceiling 108 match expected 12 requests × 9 operations exactly; enforced live by the coordinator and independently by the coordinator guard.

**P9 parent (P9_FINAL_JUDGE_RECEIPT_R1.md):** `CK_P9_INTEGRATION_GREEN` from GLM + AGY on packet `9f1e007d…`; S3 parent commit `fc296743…` consistent across freeze receipt, contract, status, and runtime hashes.

**Guards and teardown (s2-soak/lifecycle_guard.py, s3-soak/coordinator_guard.py, S3_EXECUTION_WIRING_R1.md):** Detached exact-ID lifecycle guard and coordinator guard are mandatory, hash-pinned, fail-stop, and require exact-ID absence plus empty scoped inventory before teardown GREEN. Bridge-terminal-tail exemption is tested and bounded.

## Non-blocking risks (grounded in packet)
- S3_CONTRACT_R1.md / S3_EXECUTION_WIRING_R1.md: provider exposes no cryptographic image-digest readback for CPU Pods; image pinned by name plus preserved registry/manifest digests and post-start runtime hashes only.
- S3_EXECUTION_WIRING_R1.md: SSH boundary is two-scan first-use pinning, explicitly not provider-signed host-key attestation.
- s3-soak/worker.py delegates RSS/open-files enforcement to the foundation run_soak.py, whose `process_metrics` monitors the CockroachDB process; the worker/coordinator Python processes themselves are not independently RSS-bounded during production.

## Evidence gaps (grounded in packet)
- S3_LOCAL_PREFLIGHT_RECEIPT_R1.md: receipt bears `LAST_AMENDED_UTC` after `UTC_RECORDED` with note `CURRENT_R3_FIELDS_ADDED_AFTER_ORIGINAL_EVIDENCE_TIME`; amendment is disclosed but post-hoc.
- S3_EXECUTION_WIRING_R1.md: the bundle upload and pre/post-extraction hash-verification commands (required by S3_CONTRACT_R1.md and the authorization) are not enumerated in the exact wiring; only their downstream worker invocation is shown.
- S3_LOCAL_PREFLIGHT_RECEIPT_R1.md: trials r3/r4 are accelerated 6/4/2 fresh-root smokes, not full-duration production evidence (by design).

## Authorization status
This verdict supplies the Claude leg required by S3_CONTRACT_R1.md, S3_PREFLIGHT_REPAIR_RECEIPT_R8.md, and S3_PREFLIGHT_CHECKPOINT_R8.md. Per the packet's own contract, A02 remains forbidden until the GLM leg also returns GREEN over the identical R8 packet hash.
