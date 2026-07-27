# S3 Preflight Judge Receipt R7

- `STATUS`: `S3_PREFLIGHT_GREEN`
- `PACKET_SHA256`: `94b449510eecbdb7f6a6d961375412950cdcd566196e004290b9fb62149125f2`
- `PACKET_COMMIT`: `dd3cfd90215aa8b9ec6ff2dfa5928393cc3d8651`
- `PACKET_TAG`: `ck-s3-preflight-packet-r7`
- `GLM_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_NORMALIZED_VERDICT_SHA256`: `59e2e73eeae0ced2c631bf704ae177ed691898e7330fb7d7e6df25e1c33c3195`
- `CLAUDE_MODEL`: `claude-opus-4-8`
- `CLAUDE_VERDICT`: `GREEN`
- `CLAUDE_NORMALIZED_VERDICT_SHA256`: `65cd76e6a298679942b88a6251fa47fa606ac0641c613261f21dffc468288ee4`
- `RECUSAL`: `CLEAR_BOTH_LANES`
- `RUNPOD_ATTEMPTS_AT_GATE`: `0`
- `RUNPOD_EXPOSURE_AT_GATE`: `$0.00`
- `UTC_RECORDED`: `2026-07-27T00:59:08Z`

Both independent judges returned GREEN over the exact same R7 packet hash.
The receipt files are normalized verdict records; wrapper output also bound the
served models to exact GLM 5.2 and Claude Opus 4.8. This gate authorizes only
the already frozen pre-start retry and campaign-ready workflow.
