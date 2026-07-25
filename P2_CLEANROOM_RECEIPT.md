# P2 Clean-Room Receipt

- `SANDBOX_ID`: `CK-P2-20260725-CLEANROOM`
- `GOAL`: establish an isolated synthetic CockroachDB clean-room boundary
- `OWNER`: Codex / Kenneth-controlled workspace
- `INPUTS`: P1 packet hash `2f50e043b0348545cabd19f7cb29270cc3a32225cbd463a1db9a111a8a5b0c72`
- `ALLOWED_SCOPE`: this repository and `p2-cleanroom/`; synthetic fixtures only
- `FORBIDDEN_SCOPE`: HOME runtime, live memory, credentials, client data, live
  clusters, AWS, RunPod, public remotes, and unrelated repositories
- `RESULT`: `OPEN`
- `EVIDENCE`: `P2_STATUS.md`, `p2-cleanroom/`
- `NEXT_GATE`: `CK_P2_CLEANROOM_GREEN`
- `TEARDOWN`: not yet executed; no external resources created
- `UTC_CREATED`: `2026-07-25T20:14:09Z`
