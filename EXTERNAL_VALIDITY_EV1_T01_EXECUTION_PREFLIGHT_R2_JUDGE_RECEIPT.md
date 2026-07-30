# EV1-T01 Execution Preflight R2 Judge Receipt

- `STATUS`: `INDEPENDENT_GREEN; DELETION_NOT_STARTED`
- `TASK_ID`: `EV1-T01`
- `UTC_RECORDED`: `2026-07-30T15:03:09Z`
- `RUNNER_COMMIT`: `8de593cea6b7a8a1ca53354ef9f77778e8f2a75c`
- `RUNNER_SHA256`: `daf88b6029cfb44bd183ab1af87dcd22c0213fc4ea27bbe90d62994086bc5271`
- `CAPTURE_PREPARE_R2_FILE_SHA256`: `558d42488b10c6b313690d87f443b21169af33fb13fedbfb40c8ce02b62b83de`
- `CAPTURE_PREPARE_R2_INTERNAL_RECEIPT_SHA256`: `ad775d81f194add64ff3762dbd679b4ea8a48097e0097e13f68fe1c6ae2605e5`
- `STRICT_R2_CANARY`: `GREEN; PROMOTE; FRESH_CONTEXT_PASS; REPRESENTATION_UNCHANGED; TEARDOWN_GREEN`
- `CLAUDE_PACKET_SHA256`: `c193243c9570e7274e8b9aabcb0b39661f84a7f551c95a06b2369d76e185e0ad`
- `CLAUDE_RAW_SHA256`: `dab5def2c3d023566c8fec2585f09a3da6fcab946fa882d150115c010ca05dc7`
- `CLAUDE_MODEL`: `claude-opus-4-8; initialized and served identity wrapper-verified`
- `CLAUDE_VERDICT`: `GREEN`
- `CLAUDE_RECUSAL`: `CLEAR`
- `BLOCKERS`: `NONE`
- `DELETION_STARTED`: `FALSE`

## Invalid or unavailable prior attempts

- GLM R1 reached verified GLM 5.2 but emitted no content with
  `finish_reason=length`; it is not a verdict.
- GLM R2 transport verified GLM 5.2, but the returned block falsely labeled the
  served model as Claude. The identity contradiction invalidates that result.
  Its raw SHA-256 is
  `08835fb51772f2ce20367e214bb3fa1fd8c9afe2f0c26dd93268dcb792aff9d1`.
- AGY R3 exited `65` after child/verdict validation and emitted no verdict.
  Its empty raw SHA-256 is
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Preserved non-blocking residuals

The valid judge noted that execution-time strict-profile and harness parity
must be mechanically rechecked immediately before execution; the captured
representation is the authoritative project-local copy; the post-recovery
snapshot requires later scanning; and the exact deletion is guarded by the
runner rather than Seatbelt. These do not waive any runtime stop condition.
