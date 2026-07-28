# Hardening Gate 7 Final Judge Packet R1

## Judge boundary

You are an independent, non-authoring judge. You have no shell, filesystem
write, deployment, credential, implementation, prioritization, or public-action
authority. Review only this sanitized packet. Do not propose code or direct the
builder. Return a verdict and findings only.

Every required Gate 7 condition is conjunctive. Do not average a failed bulk or
packaging condition against successful hidden/live evidence. Do not convert a
preserved blocker into GREEN because the remaining evidence is strong.

## Exact authority

- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `EXECUTION_PROMPT_SHA256`: `936c9ae62191e5d8daa0cbd7ef4287d77777e6c761694d6d6d8789842dcb454f`
- `EXPANDED_PLAN_SHA256`: `0f58b51c07d25d4643b98524e53f171d6e9c0d667c46e0718b07f40f27c1d7e7`
- `EXPANDED_PREFLIGHT_PACKET_SHA256`: `4fd89d699dccd0d3e15451fab40435ad2e9b3f7300061ff8791913dc4b7ecf44`
- `AWS_REFRESH_AMENDMENT_PACKET_SHA256`: `e3414df6b9df3a8e1126d494c8f542460cb38cb51386ac8ec9edfca7dd96c68d`
- `PREFLIGHT_JUDGES`: `GLM_5_2_GREEN; AGY_GEMINI_3_1_PRO_HIGH_GREEN; SAME_HASH; RECUSAL_CLEAR`
- `EXPECTED_FINAL_GATE`: `HARDENING_7_RUN2_GREEN only if every required track and closeout condition passes`

## Direct results

### Hidden benchmark: passed

- one CSPRNG seed, frozen before input generation;
- one execution, no tuning and no rerun;
- unprivileged `ckrunner`, capabilities zero, inherited seccomp network deny;
- oracle inaccessible to runner;
- 84/84 PASS;
- behavior failures 0, safety failures 0, false promotions 0, residue 0;
- remote aggregate SHA-256 and independent local rescore SHA-256 both
  `9428ae8cf6ce7857205dc718a3d2cd903463bf3f0331216b932c8e1cd74cfd8e`.

### One-hour live worker: passed

- 3613.026 measured seconds;
- 60/60 checkpoints;
- 12/12 safety replays;
- 12/12 summaries;
- 12/12 Lambda calls;
- 108/108 CockroachDB operations;
- status GREEN, failure null, interrupted false;
- worker final evidence hash
  `2f88d04363d10e5d41ab2c9948f01ce64dcc6da2345d29980f950f20bcf18e92`.

### AWS/guard/teardown: passed

- provider proof before start;
- post-final-exchange identity probe after at least 900 seconds: PASS;
- coordinator GREEN, bridge GREEN, coordinator guard GREEN;
- exact Pod ID absent after delete;
- active inventory `[]`, campaign-active inventory `[]`;
- lifecycle guard `TEARDOWN_GREEN`;
- no remaining campaign SSH, SCP, Screen, worker, coordinator, bridge, or guard
  process;
- 14,220.363 seconds paid lifetime at $0.06/hour, mathematical maximum
  $0.23700605, below the frozen $5.00 ceiling.

### Custody and scans: usable but prescribed helper failed

- all 318 production, 345 oracle, and 255 runner files arrived and verified
  against deterministic fallback manifests;
- gitleaks findings 0;
- exact private-path and credential-pattern hits 0;
- detect-secrets reported only 162 expected high-entropy SHA-256 receipt values,
  with no credential-type finding;
- the transferred payload did not contain the required
  `bundle/s3-soak/freeze_evidence_manifest.py` helper;
- no post-start upload or patch occurred;
- standard Linux `find` plus byte sort plus `sha256sum` was used solely to
  preserve custody, explicitly not as proof that the required helper path
  passed.

## Preserved hard blocker: bulk track

The required host-only 46,000-row bulk controller exited without its canonical
result receipt. Direct read-only counts immediately after exit were:

- tasks 2,000;
- trajectory events 20,000;
- receipts 4,000;
- vectors 0.

This proves partial execution and failure before the vector stage completed.
The controller process and its Screen session were absent. stdout/stderr was not
durably redirected, so the exact exception is unavailable. No cause beyond
`BULK_RESULT_MISSING_AFTER_PARTIAL_INSERT` is asserted.

The already frozen cleanup SQL removed all synthetic residue. Post-cleanup
counts were 0/0/0/0. No bulk rerun, continuation, hidden rerun, or worker rerun
occurred. The frozen one-run law forbids a measured retry.

## Required verdict logic

The final verdict must be `NOT_GREEN` or `BLOCKED` if either of these is a hard
failure under the frozen contract:

1. missing canonical bulk result after partial insert; or
2. missing packaged evidence-manifest helper and use of an explicitly labeled
   custody fallback.

Successful hidden, live-worker, AWS-margin, teardown, and cleanup evidence may
be recognized as valid sub-results but cannot close Gate 7.

Return exactly one JSON object.

For GLM:

```json
{
  "lane": "GLM",
  "model_identity": "<actual served model>",
  "packet_sha256": "<exact packet hash>",
  "verdict": "GREEN|NOT_GREEN|BLOCKED",
  "recusal_clear": true,
  "blocking_findings": [],
  "valid_sub_results": [],
  "summary": ""
}
```

For AGY, return the wrapper-validated heading form:

```text
PACKET_SHA256: <exact packet hash>
AGY_VERDICT: GREEN | NOT_GREEN | BLOCKED
BLOCKERS:
- <blocking finding or NONE>
NON_BLOCKING_RISKS:
- <risk or NONE>
EVIDENCE_GAPS:
- <gap or NONE>
RECUSAL_CHECK: clear | recusal_required
REQUIRED_RERUNS:
- <required rerun or NONE>
```

AGY may recognize the passed hidden benchmark, live worker, AWS probe, custody
verification, cleanup, and teardown as valid sub-results inside its findings,
but must not omit either conjunctive blocker.
