# S3 Preflight Judge Receipt R3

- `STATUS`: `S3_PREFLIGHT_GREEN`
- `PACKET`: `S3_PREFLIGHT_PACKET_R3.md`
- `PACKET_SHA256`: `098cf186e1e8da56f1e6731f21e09e2833c3b7eea4c3df0cd88e4d18fb2cb2c9`
- `PACKET_COMMIT`: `08807f3baa49d6d98f56acd0c8ab5ecdd6172139`
- `PACKET_TAG`: `ck-s3-preflight-packet-r3`
- `GLM_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RAW_SHA256`: `6cb376a6e2ec7f2f1201848b976750f488a0e80a73cdc1a6d394463c8f37576c`
- `CLAUDE_MODEL`: `claude-opus-4-8`
- `CLAUDE_VERDICT`: `GREEN`
- `CLAUDE_RAW_SHA256`: `b5d3fb1fa9867011f42937bf1e9dae5ecf79f9c4a2fcd8a16f4c9d65205a693f`
- `RECUSAL`: `CLEAR_BOTH_LANES`
- `RUNPOD_ATTEMPTS_AT_GATE`: `0`
- `RUNPOD_EXPOSURE_AT_GATE`: `$0.00`
- `UTC_RECORDED`: `2026-07-27T00:10:31Z`

Both independent judges reviewed the exact same frozen R3 packet hash. GLM's
first length-exhausted attempt and second role-conflicted attempt were rejected;
only the third exact-model response counts. Claude's first R3 response passed
the wrapper's exact served-model and structured-output validation.

The preflight gate authorizes only the bounded sequential RunPod creation and
campaign-ready workflow already frozen in R3. It does not prove the 43,200
second campaign, authorize a second production attempt, or authorize P10.

Claude's R1 timestamp/version-hygiene finding is preserved as a non-blocking
final-sign-off item. Historical timestamps will not be rewritten; final S3
receipts must distinguish original evidence time from later amendment time.
