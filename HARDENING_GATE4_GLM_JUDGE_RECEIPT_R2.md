# Hardening Gate 4 GLM Judge Receipt R2

- `STATUS`: `VALID_GREEN`
- `JUDGE_ROLE`: `fairness, statistics, schema, and construct-validity judge`
- `JUDGE_AUTHORITY`: `non-authoring verdict only`
- `JUDGE_ROUTE`: `direct glm-zai`
- `SERVED_MODEL`: `glm-4.7`
- `MODEL_FALLBACK`: disabled
- `PACKET`: `HARDENING_GATE4_JUDGE_PACKET_R1.md`
- `PACKET_SHA256`: `484686e1c02ef84c82a5433c6365559d1683502f9e92fb39d9a039a4b327429d`
- `RAW_OUTPUT`: `HARDENING_GATE4_GLM_JUDGE_RAW_R2.json`
- `RAW_OUTPUT_SHA256`: `2df987e6a3769b85981851aa25c99eb4d8e4bd9ed4d6b465d63f6473bb46c8d2`
- `STDERR_SHA256`: `3d6cc99569f37fabd00da60b0bb51340a75282320e786faae0a664290a857756`
- `VERDICT`: `GREEN`
- `BLOCKERS`: `none`
- `EVIDENCE_GAPS`: `none`
- `RECUSAL_CHECK`: `clear`
- `UTC_RECORDED`: `2026-07-27T20:30:50Z`

## Identity and schema validation

The direct route ran with exact `glm-4.7`, fallback disabled, and upstream
served-model verification required. Stderr records:

```text
glm-zai: served by glm-4.7
```

The raw stdout parses as one JSON object with exactly the required keys. It
echoes the canonical packet hash, returns GREEN, contains no blocker or evidence
gap, and reports recusal clear.

## Preserved invalid attempt

The first GLM attempt is preserved unchanged as:

- `HARDENING_GATE4_GLM_JUDGE_INVALID_ATTEMPT_R1.txt`
- SHA-256 `f907a088c3b96f42a8acc28a8733e3ed0359b348ad299fcc731202aa281939b3`
- stderr SHA-256
  `3d6cc99569f37fabd00da60b0bb51340a75282320e786faae0a664290a857756`

Its substantive verdict was GREEN, but it was invalid because it used Markdown
fences and an unapproved recusal value. No content was normalized or converted
into authority. R2 reviewed the unchanged packet hash and returned the valid
envelope.

## Non-blocking risks

The raw verdict identifies three limitations already disclosed by the packet:

1. local storage does not generalize to off-site/network disaster recovery;
2. one selected conventional baseline does not support broad comparisons to
   every other backup tool;
3. small synthetic scenarios may not represent large monorepos or
   database-heavy workloads.

These remain mandatory limitations for Gate 6 and public claims.

