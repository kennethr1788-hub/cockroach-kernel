# Hardening Gate 7 Run 5 — Final Independent Judge Receipt R1

- `UTC_RECORDED`: `2026-07-29T23:57:31Z`
- `PACKET`: `HARDENING_GATE7_RUN5_FINAL_PACKET_R1.md`
- `PACKET_SHA256`: `8325637d019f5dcb33adb46be4f13fac2c218240b60dd47c587b14cdaacdffd8`
- `CLOSEOUT_SHA256`: `2bed0e4071c132bcecc81801626589bd82b3c9e0551cacc168ddc07de56bd392`
- `MANIFEST_SHA256`: `aa45709013112c23f6a5d820be6023ca1ae9c3d320b659c6eb1b0d0ba1cf9279`
- `RECUSAL_STATE`: `CLEAR_BOTH_LANES`
- `GATE7`: `BLOCKED`
- `GATE8`: `FORBIDDEN`

## GLM lane

- `ROUTE`: direct `glm-zai`
- `SERVED_MODEL_VERIFICATION`: `glm-zai: served by glm-5.2`
- `MODEL_IDENTITY`: `glm-5.2`
- `VERDICT`: `BLOCKED`
- `PACKET_HASH_MATCH`: `YES`
- `RECUSAL_CLEAR`: `YES`
- `RAW_OUTPUT`: `evidence/hardening-gate7-run5-final-r1/glm-final.txt`
- `RAW_SHA256`: `3c0e65183e129371646b42b7214d6763bb59d04fb9b40ff6fe37d959b17db35c`

The first same-packet response mislabeled its JSON `model_identity` as `GLM-4`
despite the wrapper independently verifying the provider response as
`glm-5.2`. That malformed attempt is preserved at
`evidence/hardening-gate7-run5-final-r1/glm-attempt1-invalid-identity.txt`
with SHA-256
`b62083d128e2dadf2b49477b0e3d253741f51d566a315ce16991bcc9cfbc35d4`.
It is not counted as the authoritative GLM result. No packet bytes or evidence
changed before the schema-compliant exact-model rerun.

## AGY lane

- `ROUTE`: `agy-judge`
- `OPERATIONAL_MODEL_BINDING`: `Gemini 3.1 Pro (High)`
- `RESPONSE_LEVEL_MODEL_METADATA`: `UNAVAILABLE_IN_CLI_1_1_8`
- `VERDICT`: `BLOCKED`
- `PACKET_HASH_MATCH`: `YES`
- `RECUSAL_CLEAR`: `YES`
- `RAW_OUTPUT`: `evidence/hardening-gate7-run5-final-r1/agy-final.txt`
- `RAW_SHA256`: `34aeeecf136e3205de1fcb6644c6992e565f0a2d6b3996d45eb9c8805d12b2c5`

## Controlling decision

Both independent lanes reviewed the same exact packet and independently
returned `BLOCKED`. They recognized the valid Track 1 aggregate, Track 3
completion, ten completed Track 2 exchanges, and successful teardown as narrow
sub-results. They did not convert those sub-results into Gate 7 completion.

The controlling blockers are incomplete Track 2 execution, missing remote
Track 2/final evidence, missing post-exchange AWS margin probe, and the missing
Track 1 raw archive. Gate 8 cannot start unless a separately authorized and
independently preflighted replacement campaign produces a new complete Gate 7
candidate.

## Post-review live revalidation

- `AWS_PROJECT_LOCAL_AUTH`: `GREEN_READ_ONLY_STS_IDENTITY`
- `RUNPOD_EXACT_ID_9jizvy2igfeipj`: `ABSENT`
- `RUNPOD_RUN5_CAMPAIGN_ACTIVE`: `[]`
- `RUNPOD_ALL_NON_EXITED_COUNT`: `0`

The AWS identity value is intentionally not copied into this sanitized receipt.
