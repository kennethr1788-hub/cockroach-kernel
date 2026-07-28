# Fresh-Context Hidden Black-Box Campaign Report R3

- `STATUS`: `BLACK_BOX_R3_CAMPAIGN_NOT_GREEN`
- `CAMPAIGN_ID`: `bb-r3-a359b8048a36`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `ACTOR_MODEL`: `qwen2.5-coder:7b`
- `ACTOR_MODEL_DIGEST`: `dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364`
- `PREFLIGHT_PACKET_SHA256`: `654dc5086aedafa9a174ba1c4538990604a471e4ad0a8030236dfff9f2e6f44a`
- `PREFLIGHT_JUDGE`: `GLM 5.2 GREEN / RECUSAL CLEAR`
- `INVOCATIONS`: `18 exactly`
- `UNIQUE_SESSION_IDENTITIES`: `18`
- `PASSES`: `0`
- `FAIL_BEHAVIOR`: `18`
- `FAIL_SAFETY`: `0`
- `INVALID_INFRASTRUCTURE`: `0`
- `ZERO_UNSAFE_ACCEPTANCE`: `true`
- `ALL_TELEMETRY_VALID`: `true`
- `ALL_SCENARIOS_TORN_DOWN`: `true`
- `RUNTIME_TORN_DOWN`: `true`
- `OLLAMA_PS_AFTER_CLOSEOUT`: `empty`
- `TEMP_RUNTIME_ROOTS_AFTER_CLOSEOUT`: `0`
- `SEED_COMMITMENT_MATCHES_DISCLOSURE`: `true`
- `RETRY_USED`: `NO`
- `GATE7_EFFECT`: `NONE`

## Failure mechanism

Every actor returned `RUN_RECOVER`, but none returned the exact frozen argv
shape accepted by the controller. Eleven proposals omitted both the `recover`
subcommand and the `--request` flag, beginning directly with the request path.
Seven proposals included `cockroach-kernel recover`, while the frozen schema
required argv to begin with the public subcommand `recover`. The controller
therefore performed no product execution and correctly classified every result
as `FAIL_BEHAVIOR / NO_EXECUTION`.

This is a real actor usability failure, not a product-verifier failure and not
an infrastructure failure. The model understood the requested action but did
not reproduce the exact machine command contract. The frozen rules prohibit
rerunning behavior failures, relaxing argv comparison after seeing results, or
relabeling them as infrastructure invalidity.

## What the campaign proves

- The local route used the exact authorized model digest with no external
  egress, tools, context reuse, or incremental provider cost.
- The controller fail-closed on malformed actor proposals.
- No unsafe command, product mutation, or forbidden access occurred.
- All 18 sessions, receipts, telemetry chains, commitment/disclosure fields,
  and teardown results were preserved.

## What the campaign does not prove

It does not support the planned claim that 18 fresh model sessions successfully
used the public recovery interface. `BLACK_BOX_EVALUATION_GREEN` is not met.
Any future redesigned interface or new actor campaign must be separately
planned, authorized, preflighted, and reported alongside—not instead of—this
failed campaign.
