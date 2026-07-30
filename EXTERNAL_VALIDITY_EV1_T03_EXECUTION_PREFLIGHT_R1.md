# EV1-T03 Guarded Execution Preflight R1

- `STATUS`: `EV1_T03_EXECUTION_PREFLIGHT_GREEN_DELETION_NOT_STARTED`
- `TASK_ID`: `EV1-T03`
- `UTC_RECORDED`: `2026-07-30T17:44:02Z`
- `RUNNER_SHA256`: `491b57a9bc354df1c91a01fef9f00975c8afe70b43d1e51650b0107051b26446`
- `CAPTURE_FILE_SHA256`: `5a19dd8583ce996b3798b3a00b479874157aebb729c25b1216fd92a52f3319a8`
- `CAPTURE_RECEIPT_SHA256`: `2ce830be3d804328ba09440ee66efc617fe9549b68def72dc0a097f24ca14297`
- `LOCAL_PREFLIGHT_FILE_SHA256`: `cc8ec816f95aca26c9f0f36a3625c35ed05e6ccee10fb1f795387b19691bf2bd`
- `LOCAL_PREFLIGHT_RECEIPT_SHA256`: `48de1415fa3507116fcd8f2b60b9e407770ca844437bd55a250a800259751c6f`
- `REVIEW_CONTENT_SHA256`: `f3d90cb7ffda9b77fa8448d9fcced1591f2710710ca99bf29c9d002a61e41f50`
- `PACKET_SHA256`: `325f413cdf6f7e31640b8512f39e911a9ef0cc9c184d8437cbb0189fda483f92`
- `GLM_5_2_VERDICT`: `GREEN; RECUSAL_CLEAR; NO_BLOCKERS; NO_MATERIAL_EVIDENCE_GAPS`
- `AGY_VERDICT`: `GREEN; RECUSAL_CLEAR; NO_BLOCKERS; NO_EVIDENCE_GAPS`
- `DELETION_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`

## Preserved invalid attempts

- GLM R1: invalid because provider returned HTTP 200 with empty response
  content and `finish_reason=length`; raw SHA-256
  `fe590c1b1c98947e0c4331ea877ef623c98a631974c0775f7ac9031d03b816b1`.
- AGY R1 and R2: invalid because the wrapper rejected the verdict shape;
  each raw wrapper-output SHA-256
  `6fdbab705b0e72d99a8199b3274e09ff8066cafbc408e683e324381baf33c760`.
- Packet R1 was superseded only to remove a conflict between its internal
  exact-output instruction and the AGY wrapper's authoritative output schema.
  No evidence, runner, gate, threshold, or decision criterion changed.

## Valid independent results

- GLM R3 raw SHA-256:
  `32a8375ed2e0120ceada939b28629e6a3ac4c2c25fb8549c5d11988bc7220310`.
  Direct transport reported `glm-5.2`; the response bound review-content hash
  `f3d90cb7ffda9b77fa8448d9fcced1591f2710710ca99bf29c9d002a61e41f50`.
- AGY R3 raw SHA-256:
  `36e9d42f814b807275f56df9ea9a5d3b3295e62a756f6a8be14e160c7f4dcfc7`.
  The validated wrapper result bound packet SHA-256
  `325f413cdf6f7e31640b8512f39e911a9ef0cc9c184d8437cbb0189fda483f92`.

The operator's exact-state declaration is recorded, capture is complete, the
product and dependency-topology canaries are green, both required independent
lanes are green over the same R2 packet, and the one authorized guarded
execution may now begin. No second execution is authorized.
