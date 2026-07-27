# Hardening Gate 3 GLM Judge Receipt R1

- `STATUS`: `VALID_GREEN`
- `JUDGE_ROLE`: `independent non-authoring Gate 3 evidence judge`
- `JUDGE_ROUTE`: `direct glm-zai`
- `WRAPPER_VERIFIED_SERVED_MODEL`: `glm-4.7`
- `JUDGE_REPORTED_MODEL_TEXT`: `GLM-4`
- `MODEL_IDENTITY_INTERPRETATION`: wrapper enforcement is authoritative; the judge's shortened self-label is preserved as output drift
- `PACKET`: `HARDENING_GATE3_FINAL_GLM_PACKET_R1.md`
- `PACKET_SHA256`: `7ce89c16bed4c6fef8a442df401e564c140bc0eb5ad03b0d8bb87c780f7f4614`
- `RAW_OUTPUT`: `HARDENING_GATE3_GLM_JUDGE_RAW_R1.txt`
- `RAW_OUTPUT_SHA256`: `b3ffff82a23b88e7aa6185d8d67d5494bdb226ea9d5416d73ba137c6edb31411`
- `VERDICT`: `GREEN`
- `BLOCKERS`: `none`
- `UTC_RECORDED`: `2026-07-27T19:53:57Z`

## Availability and identity proof

Before the judge call, the direct exact-model smoke ran with fallback disabled,
requested `glm-4.7`, required the upstream response model to equal `glm-4.7`,
and returned:

```text
glm-zai: served by glm-4.7
READY_GLM_47_DIRECT
```

The final wrapper call used the same exact-model enforcement and exited `0`
with `glm-zai: served by glm-4.7`. The model-generated verdict text shortened
the label to `GLM-4`; that text is not corrected or hidden in the raw output.

## Verdict validation

The judge echoed the exact canonical packet SHA-256, returned `GREEN`, and
listed `BLOCKERS: none`. Its two non-blocking risks are preserved unchanged:

1. the resolved macOS `/tmp` cleanup-path fragility;
2. file-content reconstruction without recreating disposable Git branch and
   commit-history metadata.

Neither risk contradicts the narrow Gate 3 claim, and both were already
disclosed in the frozen packet.

