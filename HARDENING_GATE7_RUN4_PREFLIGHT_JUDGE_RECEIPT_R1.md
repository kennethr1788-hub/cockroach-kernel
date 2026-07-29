# Hardening Gate 7 Run 4 Preflight Judge Receipt R1

- `STATUS`: `RUN4_PREFLIGHT_GREEN`
- `UTC_CLOSED`: `2026-07-29T06:07:11Z`
- `PACKET`: `HARDENING_GATE7_RUN4_PREFLIGHT_PACKET_R1.md`
- `PACKET_SHA256`: `e7f4d8723b49f422bf31e0f264d49432c5735054ed7d45fdb48666a78e55a7e4`
- `PACKET_BYTES`: `32041`
- `PACKET_COMMIT`: `a587528fc6fe62bdf452447ed57e1539613f393e`
- `RUN3_STATE`: `IMMUTABLE_BLOCKED`
- `RUN4_HIDDEN_SEED`: `ABSENT`
- `RUN4_WORKER_BEFORE_PREFLIGHT`: `NONE`
- `DECISION`: `SAME_HASH_GLM_5_2_AND_AGY_GREEN`

## GLM 5.2

- canonical direct route: `/Users/kennethruedas/.local/bin/glm-zai`
- route SHA-256: `0b94755754de89557ffb9d00b45b8d8fef6578614d00563db2320e940f83748f`
- exact-model mode: fallback disabled; required served model `glm-5.2`
- transport result: `served by glm-5.2`
- admissible output SHA-256: `4b390e6964c466dba6a6506188c6636486687363898518dfb53aade45875bc3f`
- stderr SHA-256: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`
- verdict: `GREEN`
- recusal: `clear`

The first response was substantively GREEN and hash-matched but used an
unapproved JSON schema. The second response exhausted its output budget and
contained no verdict. Both are preserved as inadmissible raw evidence. The
third unchanged-packet attempt returned the required schema:

```text
PACKET_SHA256: e7f4d8723b49f422bf31e0f264d49432c5735054ed7d45fdb48666a78e55a7e4
GLM_MODEL: glm-5.2
GLM_VERDICT: GREEN
BLOCKERS:
- NONE
NON_BLOCKING_RISKS:
- AWS readiness must be revalidated live at CAMPAIGN_READY; delayed provider invoicing recorded honestly
EVIDENCE_GAPS:
- Run 4 measured worker evidence absent, correctly classified as work to authorize, mandatory until Gate 7 completion
RECUSAL_CHECK: clear
REQUIRED_RERUNS:
- NONE
```

## AGY

- canonical route: `/Users/kennethruedas/.local/bin/agy-judge`
- route SHA-256: `e90a7eca1526dd31b522fdbcb1b52e0083c93a0984e4d2f4edf8bde9eb0dd716`
- pinned model: `Gemini 3.1 Pro (High)`
- provider binding: authenticated inventory to exact backend override to provider response
- output SHA-256: `67bbc1fe2e8e51b8aa9f5368cbc8467410cde401ba949faca19f4fc9fb54c804`
- stderr SHA-256: `bf32ab8c082fa1aff618ee172c412b767bf7f636479cf49543749f2ba6ad30ee`
- verdict: `GREEN`
- recusal: `clear`

```text
PACKET_SHA256: e7f4d8723b49f422bf31e0f264d49432c5735054ed7d45fdb48666a78e55a7e4
AGY_VERDICT: GREEN
BLOCKERS:
- NONE
NON_BLOCKING_RISKS:
- NONE
EVIDENCE_GAPS:
- NONE
RECUSAL_CHECK: clear
REQUIRED_RERUNS:
- NONE
```

## Gate decision

The exact same packet is independently GREEN. Worker creation may begin only
inside the packet's bounded RunPod envelope and only after live inventory,
price, transfer archive, secret scan, extracted-bundle, lifecycle, AWS, and
CockroachDB readiness checks pass. This receipt does not mark Gate 7 GREEN.
