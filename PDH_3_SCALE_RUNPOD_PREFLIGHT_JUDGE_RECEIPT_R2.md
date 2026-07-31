# PDH-3 RunPod Preflight Judge Receipt R2

- `UTC_CREATED`: `2026-07-31T03:53:03Z`
- `JUDGE`: `GLM 5.2`
- `ROLE`: `independent non-authoring preflight judge`
- `SERVED_MODEL_VERIFIED`: `glm-5.2`
- `PACKET`:
  `PDH_3_SCALE_RUNPOD_PREFLIGHT_PACKET_R2.md`
- `PACKET_SHA256`:
  `86af89489086a4da69f35fe14f81b85806b9ee54bd4ffba86464a11aad2b75e6`
- `RAW_RESPONSE_SHA256`:
  `f591811902768f4c69d6f8b6256614ee6da1b5ef829aed7ef156b82745901546`
- `CANONICAL_RESPONSE_SHA256`:
  `02618b4b25cd2067a35d9633b9c196cd18ca718ba5bb950b87fe6fdde8114eec`
- `VERDICT`: `GREEN`
- `candidate_immutability`: `GREEN`
- `workload_and_thresholds`: `GREEN`
- `credential_and_data_boundary`: `GREEN`
- `lifecycle_and_cost`: `GREEN`
- `evidence_and_teardown`: `GREEN`
- `BLOCKERS`: `[]`

The response used the single JSON Markdown fence explicitly allowed by R2.
The fence was mechanically removed; the enclosed object parsed with the exact
required key set, every verdict dimension was GREEN, and `blockers` was empty.

The judge retained one expected limitation: the paid worker, 24-hour result,
retrieved evidence, teardown, and final independent audit do not yet exist.
Those are final-gate requirements and are not preflight evidence.

The two earlier R1 responses are preserved as format-noncompliant evidence.
They did not authorize provider mutation.
