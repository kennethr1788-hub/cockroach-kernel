# Hardening Gate 8 — Final Independent Review Packet R1

## Judge boundary

You are an independent, non-authoring judge. You have no shell, filesystem
write, deployment, credential, implementation, prioritization, or public-action
authority. Review only this sanitized packet. Return a verdict and findings;
do not propose code or direct the builder.

Decide only whether this evidence package is internally complete, traceable,
honest, mechanically consistent, and safe to use as the source for later claim
work. Do not approve Gate 9, release, publication, video, or submission.

## Authority and target

- Parent gate: `HARDENING_7_EXPANDED_GREEN`
- Product candidate: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- Gate 7 packet SHA-256:
  `1f9fa31524fb857a37b444df4b5ff7f1aa79847e941c863ffd1a993566efa89a`
- Gate 7 final judges: GLM 5.2 GREEN and AGY GREEN on the same packet hash;
  both recusal checks clear.
- Target: `HARDENING_8_EVIDENCE_PACKAGE_GREEN`

The official Stage Two criteria are equally weighted: Agentic Memory Design,
Technological Implementation, Real-World Impact, Product Readiness, and
Creativity & Originality.

## Package inventory and hashes

| Artifact | SHA-256 |
|---|---|
| One-page scorecard | `7097cee62c72a548d3f7aa04a993cf27a9410b17085b9f58445e7944f96dddde` |
| Claim-to-evidence manifest | `11afb9f54906b625de82947cf27aebd0a548655c926a598bdca2921b17976921` |
| Architecture boundary diagram | `68020d80b2b0260a4ccd9f5b439c2262765810961331236f398931caabd4efc8` |
| Limitations | `b4a7cfdd9d640d404c930e691e2cd616bf6c7836e0b5c5022c5c7b011fa75add` |
| Public subset README | `71af3199652cb37cc8e4a7d00b2b8307cfad8e5a73db0b1575b1f3caca9bc059` |
| Mechanical receipt | `84fc994692c8df0ec5c66d0cd0b98e35b9b59e8aa0fad00028c8200e7f431e97` |
| Regression and scan receipt | `3ce9cf26d659f082a297e4bb87aede3e5f389a50291c67a42d32492606114a77` |
| Private archive index | `d7e020c152e06eea1eaa907e12790a2eb6a3c7e6bbaa210ca9378c0369ddb6fb` |
| Private archive verification | `2a36a3be5fc37c01b37a5f7ff3fca391fddbc6b9aa061cab8919f5aafdbe2478` |

The private raw archive is not in Git and is not authorized for public
release. Its SHA-256 is
`717636adba545315e13930e331b4024c44c787f0b130532ad3f827ba8388837d`.
Its embedded canonical manifest binds 613 files and 3,167,428 source bytes.
An independent read-only pass verified the exact member set, safe relative tar
paths, and every member byte count and SHA-256 with zero mismatch.

The archive contains the raw sources behind the public claims, including the
Gate 3 live workflow, P9 live CockroachDB/AWS/MCP evidence, R4 black-box
evidence, Gate 6 measured comparison, Gate 7 Run 6 hidden/workload/cloud
evidence, and the preserved blocked closeouts for Gate 7 Runs 3–5. Hidden
inputs, oracle material, provider endpoints, account details, and private
runtime evidence are absent from the public subset.

## Mechanical results

All seven required counters are zero:

- missing referenced artifacts: 0;
- hash mismatches: 0;
- displayed metrics without source receipts: 0;
- public claims without evidence: 0;
- contradictory metrics: 0;
- public credentials, private paths, or private evidence: 0;
- replay/live ambiguity: 0.

Gitleaks found no leak and detect-secrets found zero findings in the public
subset. Exact frozen regression suites passed: Gate 7 24/24, P9 cloud contract
8/8, and S3 protocol/hardening 19/19. An initial repository-wide test discovery
was rejected as an invalid harness because separate suites require their own
module roots; it is preserved as a diagnostic and is not counted as evidence.

## Official-criteria scorecard

| Criterion | Evidence | Boundary |
|---|---|---|
| Agentic Memory Design | Live CockroachDB transactions bind task, trajectory, immutable receipt, vector, worker result, and projection state. The bounded workload exercised 46,000 linked rows and 200 task-bound vector queries. Managed MCP was read-only. | Bounded single-region evidence, not production scale. |
| Technological Implementation | Two live P9 traces linked CockroachDB, distributed vectors, Lambda, changefeed evidence, deterministic verdicts, and cleanup. Gate 7 handled 24 serialization retries, 12/12 cloud exchanges, and 108/108 CockroachDB operations. | Lambda and models are untrusted advisory inputs. Local deterministic policy alone decides promotion or refusal. |
| Real-World Impact | One live operator workflow retained 3/3 declared work units in a fresh OS process without task restatement. Eighteen of eighteen fresh-context local-model cases passed. | One operator; model actors and hidden campaigns are synthetic. No population claim. |
| Product Readiness | Gate 6 completed 54 measured comparisons with 54/54 cleanup and zero residue. Gate 7 completed 84/84 hidden cases, a one-hour cloud path, zero false promotions, zero tuning, hash-chain verification, and teardown. Failed Runs 3–5 remain preserved. | Competition-scale evidence, not unlimited capacity or production longevity. |
| Creativity & Originality | Recovery is deterministic promotion of a captured, declared trajectory. CockroachDB persists operational and semantic memory together while cloud and agent layers remain non-authoritative. | Originality is a judge decision. No first-ever, only, perfect, or globally optimal claim. |

## Canonical claim mappings

1. Architecture: CockroachDB is persistent transactional/vector memory; AWS
   Lambda is schema-validated advisory input; local deterministic policy is
   sole verdict authority. Evidence: two bounded live P9 traces. Limitation:
   synthetic live traces, not production traffic.
2. Single-operator workflow: 3 declared units, 3 retained units, 23,981 ms,
   14/14 checks, no task restatement. Limitation: one operator; disposable
   workspace/local Git session deleted, parent orchestration conversation not
   terminated; captured representations only.
3. Fresh-context black box: 18/18 across six classes with zero safety failures
   and verified teardown. Limitation: stateless local model actors and
   project-authored synthetic classes, not independent users.
4. Paired comparison: 54 measured executions, 54/54 cleanup, zero residue
   bytes. Limitation: synthetic, three repetitions per class, no population
   inference; generic RunPod compute was not the live AWS deployment.
5. Expanded hidden benchmark: 84/84, zero safety failures, zero false
   promotions, zero post-reveal tuning across small, medium, monorepo,
   mixed-language, conflicting-edit, partial-deletion, stale-evidence,
   missing-history, oversized-state, compound, and custody boundaries.
   Limitation: common synthetic generator/product provenance; not statistically
   independent or public-user evidence.
6. CockroachDB workload: 46,000 linked rows, 200 vector queries, concurrency
   four, 24 serialization retries, 1,086 ms p99 query latency, 107/107 cleanup,
   zero residue. Limitation: one bounded single-region campaign.
7. One-hour cloud path: 3,613.497 measured seconds, 60/60 checkpoints, 12/12
   safety replays, 12/12 Lambda invocations, 108/108 CockroachDB operations,
   empty runtime residue, verified teardown. Limitation: not production
   longevity; AWS margin passed at 901 seconds against a 900-second minimum.
8. Recovery boundary: only captured, declared representations can be
   reconstructed; unverifiable candidates are refused. Arbitrary uncaptured
   bytes cannot be recovered from nothing.

Every mapping in the machine-readable manifest names its exact repository
source artifact and SHA-256. The package labels each mapping as architecture,
live synthetic, local synthetic, measured synthetic, single-operator live, or
limitation. No replay is described as live.

## Architecture and authority wall

- CockroachDB persists tasks, trajectory events, receipts, vectors, results,
  and projections. It does not decide pass/fail.
- AWS Lambda and advisory model fan-out supply untrusted proposals only. They
  have no filesystem or verdict authority.
- Managed MCP is read-only inspection and cannot mutate memory or recover
  files.
- All cloud/model output is schema-validated and hash-bound.
- The deterministic local verifier is the sole `PROMOTE`, `REFUSE`, or
  `INVALID` authority.
- Filesystem actions are scoped to declared disposable roots; unsafe paths,
  tampering, unsupported state, and warrant replay fail closed.
- Fresh-process materialization is one-use and receipt-bound.

## Required verdict law

Return GREEN only if the package directly proves all five required artifacts,
all seven zero-count mechanical gates, public/private separation, exact claim
traceability, honest evidence-mode labels, preserved failed campaigns, and no
unsupported public claim. Return NOT_GREEN or BLOCKED for any missing,
contradictory, misleading, or boundary-violating element.

For GLM return exactly one JSON object:

```json
{
  "lane": "GLM",
  "model_identity": "<actual served model>",
  "packet_sha256": "<exact supplied packet hash>",
  "verdict": "GREEN|NOT_GREEN|BLOCKED",
  "recusal_clear": true,
  "blocking_findings": [],
  "evidence_gaps": [],
  "non_blocking_risks": [],
  "summary": ""
}
```

For AGY return exactly:

```text
AGY_MODEL_IDENTITY: <actual served model or unavailable>
AGY_PACKET_SHA256: <exact supplied packet hash>
AGY_VERDICT: GREEN | NOT_GREEN | BLOCKED
AGY_RECUSAL_CLEAR: true | false
AGY_BLOCKING_FINDINGS: <none or findings>
AGY_EVIDENCE_GAPS: <none or gaps>
AGY_NON_BLOCKING_RISKS: <none or risks>
AGY_SUMMARY: <concise summary>
```
