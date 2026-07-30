# Hardening Gate 8 — Final Independent Review Packet R2

## Transport and judge boundary

This file, in its entirety, is the current Gate 8 packet. The invoker/wrapper
computes its SHA-256 and supplies that current hash separately. Do not copy the
parent Gate 7 hash into the verdict.

You are an independent, non-authoring judge. You have no shell, filesystem
write, deployment, credential, implementation, prioritization, or public-action
authority. Review only this sanitized packet. Return a verdict and findings;
do not propose code or direct the builder. Decide only whether Gate 8 is
complete, traceable, honest, consistent, and safely usable for later claims.
Do not approve Gate 9, release, publication, video, or submission.

## Authority and target

- Parent gate: `HARDENING_7_EXPANDED_GREEN`
- Product candidate: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PARENT_GATE7_PACKET_SHA256`:
  `1f9fa31524fb857a37b444df4b5ff7f1aa79847e941c863ffd1a993566efa89a`
- Parent Gate 7 final judges: exact GLM 5.2 GREEN and AGY GREEN on that same
  parent hash; recusal checks clear.
- Current target: `HARDENING_8_EVIDENCE_PACKAGE_GREEN`

The five equally weighted official Stage Two criteria are Agentic Memory
Design, Technological Implementation, Real-World Impact, Product Readiness,
and Creativity & Originality.

## Deliverables and integrity

All five required Gate 8 deliverables exist:

1. one-page official-criteria scorecard;
2. canonical machine-readable claim-to-evidence manifest;
3. complete local-only raw archive for all mapped claims and preserved Gate 7
   failures;
4. five-file sanitized public evidence subset;
5. architecture diagram covering AWS, CockroachDB, agent/advisory, and local
   deterministic authority.

| Artifact | SHA-256 |
|---|---|
| Scorecard | `7097cee62c72a548d3f7aa04a993cf27a9410b17085b9f58445e7944f96dddde` |
| Claim manifest | `11afb9f54906b625de82947cf27aebd0a548655c926a598bdca2921b17976921` |
| Architecture diagram | `68020d80b2b0260a4ccd9f5b439c2262765810961331236f398931caabd4efc8` |
| Limitations | `b4a7cfdd9d640d404c930e691e2cd616bf6c7836e0b5c5022c5c7b011fa75add` |
| Public subset README | `71af3199652cb37cc8e4a7d00b2b8307cfad8e5a73db0b1575b1f3caca9bc059` |
| Mechanical receipt | `84fc994692c8df0ec5c66d0cd0b98e35b9b59e8aa0fad00028c8200e7f431e97` |
| Regression/scan receipt | `3ce9cf26d659f082a297e4bb87aede3e5f389a50291c67a42d32492606114a77` |
| Private archive index | `d7e020c152e06eea1eaa907e12790a2eb6a3c7e6bbaa210ca9378c0369ddb6fb` |
| Private archive verification | `2a36a3be5fc37c01b37a5f7ff3fca391fddbc6b9aa061cab8919f5aafdbe2478` |

The local-only raw archive is not tracked and is not authorized for public
release. Archive SHA-256 is
`717636adba545315e13930e331b4024c44c787f0b130532ad3f827ba8388837d`.
Its embedded canonical manifest binds 613 files and 3,167,428 source bytes.
A separate read-only verifier confirmed the exact member set, safe relative
member paths, and every member byte count and hash with zero mismatch.

The archive covers the Gate 3 live workflow, P9 CockroachDB/AWS/MCP evidence,
R4 fresh-context black box, Gate 6 comparison, Gate 7 Run 6 hidden/workload/
cloud evidence, and immutable blocked closeouts for Gate 7 Runs 3–5. Hidden
inputs, raw oracle material, provider endpoints, account details, and private
runtime evidence are excluded from the public subset.

All required mechanical counters are zero:

- missing referenced artifacts;
- hash mismatches;
- displayed metrics without source receipts;
- public claims without evidence;
- contradictory metrics;
- public credentials, private paths, or private evidence;
- replay/live ambiguity.

Gitleaks found no leak and detect-secrets found zero findings in the public
subset. Exact frozen regressions passed: Gate 7 24/24, P9 cloud contract 8/8,
and S3 protocol/hardening 19/19. A broad repository discovery command was an
invalid harness because suites require separate module roots; it is disclosed
and not counted as passing or failing product evidence.

## Criteria scorecard

| Criterion | Direct evidence | Boundary |
|---|---|---|
| Agentic Memory Design | Live CockroachDB transactions bind tasks, events, receipts, vectors, worker results, and projections. The bounded workload exercised 46,000 linked rows and 200 task-bound vector queries. Managed MCP was read-only. | Bounded, single-region; not production scale. |
| Technological Implementation | Two live P9 traces linked CockroachDB, vector queries, Lambda, changefeed evidence, deterministic verdicts, and cleanup. Gate 7 handled 24 serialization retries, 12/12 cloud exchanges, and 108/108 CockroachDB operations. | Lambda/models are untrusted advisory inputs; local deterministic policy alone decides. |
| Real-World Impact | One live operator workflow retained 3/3 declared work units in a fresh OS process without task restatement. An 18/18 fresh-context local-model campaign covered six classes. | One operator; local-model and hidden campaigns are synthetic. No population claim. |
| Product Readiness | Gate 6 completed 54 measured comparisons with 54/54 cleanup and zero residue. Gate 7 completed 84/84 hidden cases, a one-hour cloud path, zero false promotions, zero tuning, chain verification, and teardown. Failed Runs 3–5 remain preserved. | Competition-scale, not unlimited capacity or production longevity. |
| Creativity & Originality | Recovery is deterministic promotion of a captured, declared trajectory. CockroachDB co-locates operational and semantic memory while cloud and agent layers remain non-authoritative. | Originality is for competition judges. No first-ever, only, perfect, safest, or global-optimality claim. |

## Eight canonical public mappings

1. CockroachDB is the persistent transactional/vector memory; Lambda is
   schema-validated advisory input; local deterministic policy is sole verdict
   authority. Metric: two bounded live P9 traces. Limitation: synthetic live
   evidence, not production traffic.
2. One live operator workflow retained 3/3 declared units in 23,981 ms, passed
   14/14 checks, and needed no task restatement. Limitation: one operator; the
   disposable workspace/local Git session was deleted but the parent
   orchestration conversation was not; captured representations only.
3. Fresh-context black box passed 18/18 across six classes with zero safety
   failures and verified teardown. Limitation: stateless local model actors and
   project-authored synthetic classes, not independent humans.
4. Paired comparison completed 54 measured executions, 54/54 cleanup, and zero
   residue bytes. Limitation: synthetic with three repetitions per class; no
   population inference; RunPod was generic compute, not the live AWS deploy.
5. Expanded hidden benchmark passed 84/84 with zero safety failures, false
   promotions, or post-reveal tuning across diverse repository, workflow,
   compound, boundary, and custody cases. Limitation: common synthetic
   generator/product provenance; not statistically independent or user proof.
6. CockroachDB workload: 46,000 linked rows, 200 vector queries, concurrency
   four, 24 serialization retries, 1,086 ms p99, 107/107 cleanup, zero residue.
   Limitation: one bounded single-region campaign.
7. Cloud path: 3,613.497 measured seconds, 60/60 checkpoints, 12/12 safety
   replays, 12/12 Lambda invocations, 108/108 CockroachDB operations, empty
   residue, verified teardown. Limitation: not production longevity; the AWS
   margin passed at 901 seconds against a 900-second minimum.
8. Recovery is limited to captured, declared representations. Unverifiable
   candidates are refused; arbitrary uncaptured bytes cannot be recovered from
   nothing.

The machine-readable manifest maps every clause to a metric, test,
repository-relative source receipt, source SHA-256, evidence mode, and explicit
limitation. Modes distinguish architecture, live synthetic, local synthetic,
measured synthetic, single-operator live, and limitation. No replay is called
live. Runs 3–5 are not pooled into the successful Run 6 result.

## Architecture and authority wall

- CockroachDB persists memory but does not decide pass/fail.
- AWS Lambda and advisory model fan-out supply untrusted proposals only and
  have no filesystem/verdict authority.
- Managed MCP is read-only and cannot mutate memory or recover files.
- Cloud/model output is schema-validated and hash-bound.
- The local deterministic verifier is the sole `PROMOTE`, `REFUSE`, or
  `INVALID` authority.
- Filesystem actions are limited to declared disposable roots; unsafe paths,
  tampering, unsupported state, and warrant replay fail closed.
- Fresh-process materialization is one-use and receipt-bound.

## Verdict law

GREEN requires all five deliverables, all seven zero mechanical counters,
public/private separation, exact traceability, honest evidence-mode labels,
preserved failed campaigns, and zero unsupported claim. Any missing,
contradictory, misleading, or boundary-violating element is NOT_GREEN or
BLOCKED.

### GLM output

Return exactly one JSON object. `model_identity` must be exactly `glm-5.2`.
`packet_sha256` must equal the current R2 file hash supplied by the transport;
it must not equal `PARENT_GATE7_PACKET_SHA256`.

```json
{
  "lane": "GLM",
  "model_identity": "glm-5.2",
  "packet_sha256": "<current R2 packet hash supplied by transport>",
  "verdict": "GREEN|NOT_GREEN|BLOCKED",
  "recusal_clear": true,
  "blocking_findings": [],
  "evidence_gaps": [],
  "non_blocking_risks": [],
  "summary": ""
}
```

### AGY wrapper output

Return exactly the wrapper contract below. `PACKET_SHA256` is the current R2
file hash supplied by the wrapper, not the parent Gate 7 hash.

```text
PACKET_SHA256: <current R2 packet hash supplied by wrapper>
AGY_VERDICT: GREEN | NOT_GREEN | BLOCKED | INSUFFICIENT_EVIDENCE | RECUSAL_REQUIRED
BLOCKERS:
- none
NON_BLOCKING_RISKS:
- none or bounded risks
EVIDENCE_GAPS:
- none
RECUSAL_CHECK: clear | recusal_required
REQUIRED_RERUNS:
- none
```
