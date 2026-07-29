# Gate 7 Run 5 Threshold Amendment Judge Receipt R1

- `STATUS`: `GREEN`
- `UTC_CREATED`: `2026-07-29T21:08:12Z`
- `PACKET`: `HARDENING_GATE7_RUN5_THRESHOLD_AMENDMENT_PACKET_R1.md`
- `PACKET_SHA256`: `72e89d90f93e8d8b49a7deeb33168956715127fca5365761d2a96aa4e9e83213`
- `GLM_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RECUSAL`: `clear`
- `AGY_MODEL`: `Gemini 3.1 Pro (High)`
- `AGY_VERDICT`: `GREEN`
- `AGY_RECUSAL`: `clear`
- `SAME_HASH`: `YES`
- `AUTHORITY`: `ONE_NON_HIDDEN_PUBLIC_CANARY_R5_ONLY`

## Preserved invalid attempt

The first AGY transport completed a provider call but its wrapper rejected the
model output because the packet requested `VERDICT` instead of the required
`AGY_VERDICT` field. That result is invalid and never counted. The packet was
revised, its hash changed, the earlier GLM GREEN was invalidated, and both lanes
were rerun on the current exact hash.

## Raw evidence

- GLM raw SHA-256:
  `8cb0367aee9a7c3f32ba7a5fafaa01cea2ca2a20e59dbd156963a8a6ab3f5725`;
- AGY raw SHA-256:
  `14120c735babe34ab2c5838e1ef0e3ce42cc170b5115f7be1ba7a6084c9e11d0`;
- invalid AGY transport SHA-256:
  `6fdbab705b0e72d99a8199b3274e09ff8066cafbc408e683e324381baf33c760`.

GLM noted two non-blocking risks: the seven-minute ceiling may mask later
latency regressions, and the total-time check cannot interrupt an individual
slow SQL batch. These remain visible limitations. Actual measured latency is
mandatory evidence, each SQL batch retains its own 120/300-second timeout, and
R5 remains blocking if total insert time exceeds 420,000 ms.

This receipt does not authorize a RunPod worker, hidden seed, ordinary Run 5
worker preflight, Gate 7 GREEN, or Gate 8.
