# S3 Preflight History R1

- `STATUS`: `PRESERVED_WITH_CORRECTIONS`
- `UTC_RECORDED`: `2026-07-26T23:12:11Z`

1. `s3-local-smoke-fixture-r1` was BLOCKED: only two of four safety replays
   were emitted because cadence evaluation occurred only on checkpoint targets.
   This finding caused a union-of-cadence-targets correction. It is not GREEN
   evidence. Aggregate raw hash:
   `3ea543eda2f85d5e86b38a2d541dffe06785b2d74b43b2e0daf60f50c7c7605a`.
2. `s3-local-smoke-fixture-r2` passed 6 checkpoints, 4 safety replays, and 2
   hourly summaries. Aggregate raw hash:
   `63e976d3dab9b6fa5409d2bff624c04630716ea7e40c99edd06da4fec745ca65`.
3. Early live smokes r1/r2 passed their then-current contract but performed one
   changefeed scan per call. They were rejected as insufficient restart proof.
4. The coordinator was corrected to require two bounded initial-scan executions
   with identical request identities and nine exact Cockroach operations per
   cloud call.
5. Final fresh-root live smokes r3/r4 both passed on the corrected cloud path.
6. A forced coordinator-offline trial returned expected refusal
   `COORDINATOR_UNAVAILABLE` with zero cloud calls.
7. A later adversarial inspection found that the coordinator guard would treat
   a legitimately idle bridge log as stale between hourly requests. Before any
   RunPod creation, the bridge gained bounded heartbeats and the guard gained
   explicit coordinator, bridge, and lifecycle-guard PID bindings. The updated
   normal/fail-stop proof is GREEN.

No historical failure was deleted or converted to GREEN.
