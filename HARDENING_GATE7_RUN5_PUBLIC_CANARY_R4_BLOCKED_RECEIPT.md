# Gate 7 Run 5 Public Canary R4 Blocked Receipt

- `STATUS`: `BLOCKED`
- `UTC_CLOSED`: `2026-07-29T20:58:34Z`
- `CAMPAIGN_ID`: `ck-g7r5-public-collision-r4`
- `SOURCE_COMMIT`: `c6d5a19cf8f513e2c9f9d2cb720c9019d420b807`
- `HIDDEN_CAMPAIGN`: `NO`
- `RUNPOD_WORKER_CREATED`: `NO`
- `BLOCKER`: `FROZEN_INSERT_TIME_THRESHOLD_BREACHED_BY_316_MS`

## Direct result

R4 began only after dropped-index schema GC job `1196957847833706497`
reached terminal status `succeeded`. It retained the exact R3 source, workload,
scale, retry count, timeouts, and thresholds. All 184 insertion batches
completed, but their measured successful SQL time was `300316 ms`, exceeding
the frozen `300000 ms` ceiling by `316 ms`. R4 therefore remains BLOCKED and
is never counted as a passing canary.

The stage measurements were:

- tasks: `5149 ms` across 8 batches;
- events: `53687 ms` across 80 batches;
- receipts: `9983 ms` across 16 batches;
- vectors: `231497 ms` across 80 batches;
- serialization retries: `26` total;
- vector batch p50/p95/p99/max: `2365/5130/6930/10393 ms`.

The monitoring lane sent SIGTERM through the reviewed interruption path as soon
as the cumulative breach was observed. The controller was already entering its
ordinary cleanup stage; interruption caused it to restart the complete
fail-closed cleanup contract. The canonical cleanup receipt records all
`107/107` required batches, zero cleanup retries, and residue `[0,0,0,0]`.

## Canonical evidence

- generated manifest SHA-256:
  `fe0cfb0fee07e1e928496fb11e9f0ee1500373854749ec03189544e91e46c64a`;
- cleanup manifest SHA-256:
  `ab3aa0fa51db0634fdb2bca90a0aef12e159cab2cb6731ce5702cffd51f56719`;
- failure file SHA-256:
  `e8c8e5fbaf843c34d3d0ab3408d10427ac2fb52ba956b67ac536f3887334cdf3`;
- cleanup file SHA-256:
  `5ec563cbc733b8905412d61704a11f5ef361788410b9d05b6d2fd1eeed7a0202`;
- terminal file SHA-256:
  `d0ff193f254bc10b3b54e026f70d89bf75cfa9d6099018e17de4dd00aa8a1c5a`;
- failure receipt SHA-256:
  `7bd7b4a194caa41b766444520bf83348d278e03bf59d2180fc0c85432be147ad`;
- cleanup receipt SHA-256:
  `39cc99c83a577a6957bc5c7b229c2f24083d2ee22c1ef614b839332608e96119`;
- terminal receipt SHA-256:
  `9c661ee2fe4b3b732c52d557346ce2a947c72dde3dce6a1b67d7b6f39c57aff5`;
- direct residue output SHA-256:
  `58d9fffe639ec31e34a1032bd727a05a5b7d6983881706d28a39c24cd03a31bb`.

No child process, RunPod worker, or hidden seed remains.

## Next safe action

Create a new pre-hidden threshold candidate without changing product behavior,
scale, correctness rules, safety rules, row counts, or evidence requirements.
Require fresh same-hash GLM 5.2 and AGY GREEN before one new public canary.
