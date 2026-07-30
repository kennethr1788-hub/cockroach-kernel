# EV1-T02 Execution Preflight R1

- `STATUS`: `EV1_T02_EXECUTION_PREFLIGHT_GREEN`
- `TASK_ID`: `EV1-T02`
- `UTC_RECORDED`: `2026-07-30T16:54:28Z`
- `RUNNER_COMMIT`: `70b5bcbd75bec13f58b1a8e53cdfca996885ed4a`
- `RUNNER_SHA256`: `8db6767d881b5fd0d8e6c8a8b52e130d1f43b5fc232e7137d3106ee4143c784c`
- `CAPTURE_FILE_SHA256`: `680757925cf6e3e1d8f94e86fcdec8da10776e090ef488892603fd9d8d8f0acc`
- `CAPTURE_RECEIPT_SHA256`: `e4dc09bcb2007bba009ef2f45e75b847526ad92fa06af9e2066f8970ecd0ed78`
- `LOCAL_PREFLIGHT_FILE_SHA256`: `1c8c96413341fe4bb1b984b0df60154308d31b8773be24493e35b5454ed85e9a`
- `LOCAL_PREFLIGHT_RECEIPT_SHA256`: `25e305d6b118bbe745a990508dbfb5df43dfb822352faff50f6bbe197a775490`
- `REVIEW_CONTENT_SHA256`: `c0e39fcc32bd60b5b1f8c11ea2e3b217547e12172989426274b83506171c9324`
- `TRANSPORT_SHA256`: `1224261dac4359f18b3fc7171805c2b09fb766262d4807143563c257d2e61a1b`
- `DELETION_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`

## Mechanical preflight

The original disposable workspace remains present with the exact declared Git
state. Capture sealed all three representations. The frozen product canary
returned `PROMOTE`, did not mutate its representation root, and exited zero.
The fresh successor topology canary cloned `node_modules` into the successor
root, validated 16 relative in-root symlinks, and passed `npm run typecheck`.
Both temporary preflight and execution roots were absent after the canary.

## Independent review

Both independent lanes received the byte-identical 47,353-byte packet at
transport SHA-256
`1224261dac4359f18b3fc7171805c2b09fb766262d4807143563c257d2e61a1b`.

- GLM attempt 1 was invalid transport evidence: exact `glm-5.2` returned HTTP
  200 with empty content and `finish_reason=length` under a 4,096-token output
  allowance. It is preserved and does not count.
- GLM attempt 2 changed only the transport output allowance to 16,384 tokens;
  packet bytes were unchanged. Exact served model `glm-5.2` returned `GREEN`,
  matched review-content SHA-256, and reported no blockers, risks, or gaps.
- AGY's pinned judge wrapper returned `GREEN` on the exact transport SHA-256,
  with recusal clear and no blockers, risks, gaps, or reruns. The wrapper bound
  authenticated inventory, the exact `Gemini 3.1 Pro (High)` backend override,
  and a provider response. Response-level served-model metadata remains an
  explicitly disclosed CLI 1.1.8 limitation.

Raw evidence is preserved under the task control root:

- GLM invalid R1 SHA-256:
  `fe590c1b1c98947e0c4331ea877ef623c98a631974c0775f7ac9031d03b816b1`
- GLM GREEN R1 SHA-256:
  `c4a19b88e2c5df6fc37f9e38c68075f1800c27874d0c65cd91aa9e1bddaf450d`
- AGY GREEN R1 SHA-256:
  `000213c6aeb6660ac6bf9d63b49ac784c99b2c64e1e05fd4486d1f26c60aec7d`

Exactly one guarded T02 execution is now mechanically authorized. This receipt
does not predict its result and does not mark the task complete. The runner
must preserve any failure and stop for Kenneth's immediate observations after
mechanical execution.
