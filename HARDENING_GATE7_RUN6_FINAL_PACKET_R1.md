# Hardening Gate 7 Run 6 — Final Independent Judge Packet R1

## Judge boundary

You are an independent, non-authoring judge. You have no shell, filesystem
write, deployment, credential, implementation, prioritization, or public-action
authority. Review only this sanitized packet. Return a verdict and findings;
do not propose code or direct the builder.

Every Gate 7 condition is conjunctive. Do not average a failure against passed
tracks. Do not approve Gate 8; decide only whether Run 6 closes Gate 7.

## Exact authority and continuity

- Product candidate: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- Run 6 replacement contract file SHA-256:
  `918f876b7fe53ffe2e5055407d92df60cc6b915e64f8af9e627b357bb7707f86`
- Run 6 preflight packet SHA-256:
  `49deb473ad40c892ee8cf396843e1a20f1486bb81d1af634c3895f22b7c01007`
- Run 6 preflight judges: exact GLM 5.2 GREEN and AGY GREEN on that same
  packet hash; both recusal checks clear.
- Attempt request SHA-256:
  `4b6a9fbd8950ed0546c869035d65c9750caf5e005dcb8d2c52489c908df31b25`
- Worker: official Ubuntu 22.04 CPU image, 2 vCPU, 4 GiB RAM, 20 GiB
  disposable disk, zero GPU, zero persistent/network volume, observed
  `$0.06/hour` compute rate.

Runs 3, 4, and 5 remain immutable failed evidence. Run 6 used a new CSPRNG
seed and newly generated hidden inputs. No revealed Run 5 hidden input was
read, reused, or tuned against. Post-reveal tuning events are zero.

## Track 1 — new hidden benchmark

- 84/84 PASS;
- behavior failures 0, safety failures 0;
- false promotions 0;
- mutation after refusal or invalid 0;
- correct stable reason 84/84;
- cleanup GREEN 84/84, residue 0;
- original 43 semantics preserved;
- unprivileged runner, zero effective capabilities, `no_new_privs=1`, inherited
  seccomp network denial, oracle unavailable to the runner;
- retrieved archive SHA-256:
  `8d991b27e9d5ea9c14b84d69390ae266fd2ba685b27019ab8a36b443618b3dbc`;
- after verified worker teardown, custody unseal hash verification passed and a
  fresh independent local rescore reproduced the exact remote aggregate
  SHA-256:
  `e0b313d32cc2c9f552f17fe9fbd43d539eb5c84fd3c8fddc7972f5ecafd62694`.

## Track 3 — bounded CockroachDB workload

- exact rows: 2,000 tasks, 20,000 trajectory events, 4,000 receipts, 20,000
  vectors;
- 200 task-bound vector queries;
- concurrency configured 4 and observed 4;
- 24 serialization retries handled;
- insert total 234,977 ms;
- query latency p50 533 ms, p95 864 ms, p99 1,086 ms, max 1,196 ms;
- cleanup 107/107 and residue counts 0/0/0/0;
- credential bytes recorded false; worker received credentials false;
- canonical result hash:
  `3061ab71d20c01f0f29001977f378af9dc2bf7e1d26c00d3ed2cc1859f3d4863`.

## Track 2 — one-hour cloud path

- status GREEN, failure null, interrupted false;
- 3,613.497 measured seconds;
- 60/60 checkpoints;
- 12/12 safety replays;
- 12/12 hourly summaries;
- 12/12 completed requests and Lambda invocations;
- 108/108 CockroachDB operations;
- runtime residue empty;
- retrieved archive SHA-256:
  `f6dea043ced007319cf19805dad8ddd430ca8cadf1a8f9028e2997b1a204dc6b`;
- worker final evidence hash:
  `8e7302a0fa258287bad9277e8e52046b7f190342c0dd63c248cd488091d84506`;
- independently recomputed checkpoint, safety, summary, named-event, request,
  result, and parent-link chains all passed.

## AWS margin, custody, and teardown

- the required post-final-exchange identity probe passed after 901 seconds
  against a 900-second minimum;
- credential bytes recorded false;
- postcheck receipt hash:
  `f46ecca5e1abee978c86d6fe9292c749091bc85322308948b9d38ab7a20cc880`;
- terminal chains: `BRIDGE_GREEN`, `COORDINATOR_GREEN`,
  `COORDINATOR_GUARD_GREEN`, `TEARDOWN_GREEN`;
- completion marker was written only after measured evidence retrieval and hash
  verification;
- exact Pod ID absent, campaign inventory empty, no Screen session or campaign
  process remains;
- observed active lifetime 6,408.486 seconds; mathematical compute cost
  `$0.1068081`, below the `$5.00` ceiling; this is not claimed as an exact
  provider billing receipt.

## Final regressions

- Gate 7 tests: 24/24 PASS;
- P9 cloud-contract tests: 8/8 PASS;
- S3 protocol/hardening tests: 19/19 PASS.

## Honest limitations

- synthetic hidden scenarios and a common generator/product implementation;
- not statistically independent and not public-user evidence;
- bounded, single-region workload, not production-scale or universal capacity;
- reconstructs only captured, declared representations and cannot recover
  arbitrary uncaptured bytes from nothing.

## Required verdict law

Return `GREEN` only if the evidence directly supports every required Run 6
track, AWS margin, custody, cleanup, teardown, and no-tuning boundary. Return
`NOT_GREEN` or `BLOCKED` for any missing or contradictory conjunctive evidence.

For GLM, return exactly one JSON object:

```json
{
  "lane": "GLM",
  "model_identity": "<actual served model>",
  "packet_sha256": "<exact supplied packet hash>",
  "verdict": "GREEN|NOT_GREEN|BLOCKED",
  "recusal_clear": true,
  "blocking_findings": [],
  "non_blocking_risks": [],
  "summary": ""
}
```

For AGY, return exactly the wrapper-validated heading form:

```text
PACKET_SHA256: <exact supplied packet hash>
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
