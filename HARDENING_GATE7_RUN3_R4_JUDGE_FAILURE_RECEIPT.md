# Hardening Gate 7 Run 3 R4 Judge Failure Receipt

- UTC: `2026-07-29T02:55:19Z`
- packet: `HARDENING_GATE7_RUN3_PREFLIGHT_PACKET_R4.md`
- packet SHA-256: `3ecea696fc214331c9e46256fc4c80c74652e7c4925fd7555d3d7e4d8f8e8274`
- packet bytes: `107608`
- worker created: `NO`
- RunPod boundary: `CLOSED`

## GLM 5.2

- route: canonical direct `glm-zai`
- served-model evidence: `glm-5.2`
- exit status: `1`
- admissible verdict: `NO`
- exact result: `HTTP 200: empty response content (finish_reason=length)`
- classification: `JUDGE_OUTPUT_UNAVAILABLE`

## AGY 1.1.8

- route: canonical `agy-judge`
- pinned model: `Gemini 3.1 Pro (High)`
- exit status: `65`
- admissible verdict: `NO`
- exact result: `child or verdict validation failed (exit=0)`
- stdout emitted by wrapper: empty
- classification: `JUDGE_OUTPUT_SCHEMA_REJECTED`

## Controlling decision

Neither failure is converted into a verdict. Preserve R4 unchanged. Build a
smaller R5 judge packet that retains the authorization, immutable source and
artifact hashes, R3 split-verdict history, exact regression closure, critical
source excerpts, gate criteria, and failure-custody requirements while removing
redundant full-file embeddings. Obtain fresh same-hash GLM 5.2 and AGY verdicts
before any worker creation.
