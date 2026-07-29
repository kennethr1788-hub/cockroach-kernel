# Hardening Gate 7 Run 3 R5 Preflight Judge Receipt

- UTC closed: `2026-07-29T03:00:21Z`
- packet: `HARDENING_GATE7_RUN3_PREFLIGHT_PACKET_R5.md`
- packet SHA-256: `5274e5f8c35383ff26f283764ba64385c3e3e5d5711da07a9b20735c6ccba7c9`
- packet bytes: `64023`
- packet commit: `0aed8a277bd1331adc35720ea9de9bfafd025828`
- worker created before preflight: `NO`
- recusal state: `CLEAR` in both valid verdicts
- preflight result: `GREEN`

## GLM 5.2

- canonical route: `/Users/kennethruedas/.local/bin/glm`
- route SHA-256: `a0b0ce72f2275b1489c2a3e4c759aecd1c1c7dc1f1bc9143fa1045b7ca7505f9`
- direct backend SHA-256: `0b94755754de89557ffb9d00b45b8d8fef6578614d00563db2320e940f83748f`
- egress gateway SHA-256: `184400014c30de9e5d70e7453d0537717e87919165f8c9fbe743cd405c51f9f7`
- sanitized prompt SHA-256: `6880d288ad678a18cd4e49afd866eb5ed57a536bba675de42ea130149beef2fe`
- exact-model mode: `GLM_ZAI_DISABLE_FALLBACK=1`
- required served model: `glm-5.2`
- transport model verification: `served by glm-5.2`
- verdict: `GREEN`
- recusal: `clear`

The first otherwise-GREEN response body mislabeled its model as `GLM_4` even
though the transport verified `glm-5.2`. It was not counted. The same unchanged
packet was rerun in exact-model mode with a transport-bound identity field and
returned:

```text
PACKET_SHA256: 5274e5f8c35383ff26f283764ba64385c3e3e5d5711da07a9b20735c6ccba7c9
GLM_MODEL: glm-5.2
GLM_VERDICT: GREEN
BLOCKERS:
- None
NON_BLOCKING_RISKS:
- R4 exhausted output budget and AGY failed via malformed output; R5 mitigates this by summarizing files, but final verdict remains strictly bound by AGY's canonical operational stability during the final post-execution review.
- The eventual success of the Gate 7 campaign relies on flawless remote execution within bounded cost and safety limits, which carries inherent operational risk outside of preflight validation.
EVIDENCE_GAPS:
- Live measured execution evidence (Track 1: 84 hidden benchmark cases, Track 2: 3,600s live worker run, Track 3: 46,000-row remote bulk workload).
- Final independent re-verification of remote evidence and CockroachDB cleanup to zero rows.
RECUSAL_CHECK: clear
REQUIRED_RERUNS:
- None
```

## AGY 1.1.8

- canonical route SHA-256: `e90a7eca1526dd31b522fdbcb1b52e0083c93a0984e4d2f4edf8bde9eb0dd716`
- signed AGY binary SHA-256: `251662551657dd0955428dd31536e7adf84c1cb4d53f20b6dca8bf8714762ff9`
- egress gateway SHA-256: `184400014c30de9e5d70e7453d0537717e87919165f8c9fbe743cd405c51f9f7`
- pinned model: `Gemini 3.1 Pro (High)`
- provider-execution binding: authenticated inventory, exact backend override,
  provider response
- verdict: `GREEN`
- recusal: `clear`

```text
PACKET_SHA256: 5274e5f8c35383ff26f283764ba64385c3e3e5d5711da07a9b20735c6ccba7c9
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

The same-hash preflight quorum is GREEN. RunPod worker creation may begin only
inside the exact authorization and campaign envelope in R5. This does not mark
Gate 7 GREEN; all three measured tracks, teardown, cost accounting, and final
same-hash GLM 5.2 plus AGY review remain required.
