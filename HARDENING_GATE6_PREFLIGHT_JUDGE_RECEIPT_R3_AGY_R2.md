# Hardening Gate 6 R3 — GLM plus AGY Same-Hash Preflight Receipt

- `STATUS`: `PREFLIGHT_GREEN`
- `PACKET`: `HARDENING_GATE6_PREFLIGHT_PACKET_R3_AGY_R2.md`
- `PACKET_SHA256`: `4f598020da961385056d9a6a3f22d03b849624cfa8458fcc48f56bddb3c4620d`
- `PACKET_BYTES`: `99617`
- `GLM_ROUTE`: `glm-zai`
- `GLM_SERVED_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RECUSAL`: `clear`
- `GLM_RAW_SHA256`: `29ae2c61807def174a198031673af59e99c258b07ebc049cd8ecd9bd6c206dbb`
- `AGY_ROUTE`: `agy-judge`
- `AGY_MODEL`: `Gemini 3.1 Pro (High)`
- `AGY_VERDICT`: `GREEN`
- `AGY_RECUSAL`: `clear`
- `AGY_RAW_SHA256`: `46fcf268af6d3009984eb1a8671dde2695c7ee0147a1afb31284a493a7736d7e`
- `CLAUDE`: `RECUSAL_REQUIRED_PRESERVED_NOT_COUNTED`
- `RUNPOD_CREATED`: `no`
- `MEASURED_EXECUTIONS`: `0`
- `UTC_RECORDED`: `2026-07-28T02:10:02Z`

GLM's first review of R2 correctly refused to bind a digest that was not in its
outer call. No packet bytes changed. Both lanes were then rerun from scratch on
the same packet. GLM received a non-recursive envelope stating the SHA-256
computed from the exact packet file bytes; `agy-judge` independently computed
that same digest from its packet copy. Both outputs bind the exact digest above,
return GREEN, and report recusal clear. This authorizes only sequential worker
creation and the pre-payload capability canary under the frozen R3 envelope.
It does not predict the canary, authorize payload upload before canary GREEN,
approve Gate 7, or count as final review.
