# Hardening Gate 7 Run 5 — Final Independent Review Packet R1

## Judge boundary

You are an independent, non-authoring judge. You have no shell, filesystem
write, deployment, credential, implementation, prioritization, or public-action
authority. Review only this sanitized packet. Return a verdict and findings;
do not propose code or direct implementation.

Every Gate 7 condition is conjunctive. Do not convert strong partial evidence
into GREEN. The packet hash supplied by the caller must match these exact bytes.

## Bound authority

- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PLAN_SHA256`: `0f58b51c07d25d4643b98524e53f171d6e9c0d667c46e0718b07f40f27c1d7e7`
- `PREFLIGHT_PACKET_SHA256`: `2b1af0712b00b373ae62b53365abc7268399bffc56f7196ba3c71801859cbe02`
- `PREFLIGHT_JUDGES`: `GLM_5_2_GREEN; AGY_GREEN; SAME_HASH; RECUSAL_CLEAR`
- `RUN5_CLOSEOUT`: `HARDENING_GATE7_RUN5_BLOCKED_CLOSEOUT_R1.md`
- `RUN5_MANIFEST`: `HARDENING_GATE7_RUN5_BLOCKED_EVIDENCE_MANIFEST_R1.json`

## Required facts

Track 1 produced an aggregate `84/84 PASS` with zero safety failures, but its
sealed raw archive was not retrieved before worker deletion. Track 3 completed
the 46,000-row live workload, 200 vector queries, cleanup 107/107, and zero
residue. Track 2 completed ten of twelve cloud exchanges: 10 Lambda calls and
90 CockroachDB operations. Request 11 reached the host, then the coordinator
emitted `COORDINATOR_BLOCKED` with error hash
`a0fe27d29e544bb052dbc74dd324e9f0ab0cbfd9b7985c5fa3610ae782fafa85`
before a call directory or result existed.

The guard immediately stopped and deleted exact Pod `9jizvy2igfeipj`.
Lifecycle evidence ends in `TEARDOWN_GREEN`; exact-ID lookup is absent,
campaign inventory is empty, and no campaign process remains.

The historical cause is not directly recoverable and is not attributed. The
worker final receipt, remote Track 2 evidence, post-exchange margin probe, and
Track 1 raw archive are missing. No measured rerun occurred.

## Required decision

Gate 7 can be GREEN only if all required hidden, live worker, cloud margin,
custody, teardown, and final-evidence conditions pass. Determine whether this
packet must be `BLOCKED` or `NOT_GREEN`. Recognize valid sub-results separately
without treating them as phase completion.

GLM must return exactly one JSON object:

```json
{"lane":"GLM","model_identity":"<actual served model>","packet_sha256":"<exact packet hash>","verdict":"GREEN|NOT_GREEN|BLOCKED","recusal_clear":true,"blocking_findings":[],"valid_sub_results":[],"summary":""}
```

AGY must return the wrapper-compatible heading form:

```text
PACKET_SHA256: <exact packet hash>
AGY_VERDICT: GREEN | NOT_GREEN | BLOCKED
BLOCKERS:
- <finding or NONE>
NON_BLOCKING_RISKS:
- <risk or NONE>
EVIDENCE_GAPS:
- <gap or NONE>
RECUSAL_CHECK: clear | recusal_required
REQUIRED_RERUNS:
- <rerun or NONE>
```
