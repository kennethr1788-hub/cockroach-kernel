# EV1-T05 Guarded Execution Preflight R1

- `STATUS`: `EV1_T05_EXECUTION_PREFLIGHT_GREEN_DELETION_NOT_STARTED`
- `TASK_ID`: `EV1-T05`
- `RUNNER_SHA256`: `45d584d4f1c3756470d08b5cf33abeecf697cc9df6f1cf75427f9edfb53c52b8`
- `CAPTURE_FILE_SHA256`: `0e4cfd10d8a05c1e9685675551e256eb3d5ccbafc795fc3e6e8369654da8b798`
- `CAPTURE_RECEIPT_SHA256`: `7d83d3f4924612528b0c97ce41374f03d3594d9c82defcdc8b6bc6b05c9cb847`
- `LOCAL_PREFLIGHT_FILE_SHA256`: `7d30c7cab63a6aa2e31e8cecb790080d0639aa0b1aa950f9b7046dca192fa087`
- `LOCAL_PREFLIGHT_RECEIPT_SHA256`: `5e9de43e7c0543a6e1560a5bdddef737a6d1ab56c36eb44efc1f0ed16a03ee09`
- `REVIEW_CONTENT_SHA256`: `2434edde6426a4480af036909255c1e95002f1566b9b30ac2594daa9f7c7ce20`
- `PACKET_SHA256`: `3f86313756baec3dc09dc0eb4dcb26338d7a4b7298d924acf5275bd694f80d17`
- `GLM_5_2_VERDICT`: `GREEN; RECUSAL_CLEAR; NO_BLOCKERS; NO_EVIDENCE_GAPS`
- `AGY_VERDICT`: `GREEN; RECUSAL_CLEAR; NO_BLOCKERS; NO_EVIDENCE_GAPS`
- `DELETION_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`

## Independent results

- GLM attempts 1 and 2 returned no verdict because the served GLM 5.2 response
  ended at its 4096-token response ceiling with `finish_reason=length`. Both
  invalid outputs are preserved byte-exact with SHA-256
  `fe590c1b1c98947e0c4331ea877ef623c98a631974c0775f7ac9031d03b816b1`.
  A mechanism-specific retry raised the documented wrapper response ceiling to
  8192 without changing the packet. Direct served GLM 5.2 then returned GREEN,
  recusal clear, no blockers, and no evidence gaps over review-content SHA-256
  `2434edde6426a4480af036909255c1e95002f1566b9b30ac2594daa9f7c7ce20`.
  Its raw output SHA-256 is
  `685bbb1c7cd0162cab6dcc1c3028fa82e1a905127e2c24d826394ee10f18758e`.
- AGY returned GREEN, recusal clear, no blockers, and no evidence gaps over the
  same packet SHA-256. Its wrapper bound the authenticated inventory, exact
  Gemini 3.1 Pro High backend override, and provider response. Raw output
  SHA-256 is
  `13ec0b998d085fdb67e2d4fee2de481f9bc26cdc639f559add7d5cbe0a39d9ae`.

The first local preflight attempt's expected fixture-directory collision is
preserved separately. The corrected local preflight passed the product canary,
the complete reconstructed dependency topology, strict schema suite, typecheck,
production build, representation immutability, baseline attribution, and temp
teardown. The outbound packet's direct private-marker scan and gitleaks scan are
clean. The exact-state declaration is recorded; capture is complete; the
original workspace remains present; and both required independent lanes are
GREEN over one frozen packet. The one authorized guarded execution may begin.
No second execution is authorized.
