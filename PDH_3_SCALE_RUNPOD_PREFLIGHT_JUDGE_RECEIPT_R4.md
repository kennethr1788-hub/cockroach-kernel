# PDH-3 RunPod Preflight Judge Receipt R4

- `UTC_CREATED`: `2026-07-31T04:04:50Z`
- `JUDGE`: `GLM 5.2`
- `ROLE`: `independent non-authoring preflight judge`
- `SERVED_MODEL_VERIFIED`: `glm-5.2`
- `PACKET`:
  `PDH_3_SCALE_RUNPOD_PREFLIGHT_PACKET_R4.md`
- `PACKET_SHA256`:
  `68ad4e5608d13d47ffc0c12aebe4ab6f1ce4a75b6705f525fadaa26581ceb919`
- `RAW_RESPONSE_SHA256`:
  `180a057a938dfb3868f7c276a3cf3e482534bde243d3a62c1dcfadd668d93038`
- `CANONICAL_RESPONSE_SHA256`:
  `5a3b9d951d1c187c37c6fd1cc26e3c3369f77d1ac3eef8d648cdda09992de4f9`
- `VERDICT`: `GREEN`
- `candidate_immutability`: `GREEN`
- `workload_and_thresholds`: `GREEN`
- `credential_and_data_boundary`: `GREEN`
- `lifecycle_and_cost`: `GREEN`
- `evidence_and_teardown`: `GREEN`
- `BLOCKERS`: `[]`
- `LIMITATIONS`: `[]`

R4 preserves Attempt 01 as a deleted, no-upload failure and accepts only the
observed same-price Secure L40S RAM range of 94–188 GB. The single allowed JSON
fence was mechanically removed; the exact object parsed and every required
dimension is GREEN.
