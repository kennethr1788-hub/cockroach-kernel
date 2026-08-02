# PDH-3 R12 R6 PF-4 replacement retry authorization R1

Status: `PF4_REPLACEMENT_RETRIES_AUTHORIZED_PENDING_REPAIR_AND_PREFLIGHT`

UTC recorded: `2026-08-02T10:29:00Z`

## Exact operator statement

> I authorize another attempt and continuous retires until a successful run pod
> is launched after each failed attempt fixes should be made based on the
> failures prior to the next attempt

## Fail-closed bounded interpretation

This supersedes the prior one-attempt limit for PF-4 replacement attempts only.
It does not create unbounded spending authority. The existing `$12.00`
aggregate ceiling, `$0.99/hour` L40S compute ceiling, one-worker-at-a-time
limit, disposable-storage boundary, and mandatory teardown remain controlling.

Mechanical retry envelope:

- at most three additional sequential worker creation attempts;
- stop immediately when one worker completes PF-4 successfully;
- never more than one paid worker at a time;
- no replacement after main-bundle upload, which remains forbidden;
- no PF-2R through PF-7 and no measured 24-hour campaign;
- every failed worker must be deleted with exact-ID absence and empty campaign
  inventory proved before another creation;
- every attempt must preserve its raw failure evidence;
- provider/capacity failures may be retried only when the implementation and
  packet are unchanged;
- any deterministic implementation, contract, threshold, or evidence defect
  requires a local correction, new hashes, and fresh same-hash GLM 5.2 GREEN
  before the next provider mutation;
- three consecutive occurrences of the same failure stop blind retries even if
  the numeric envelope remains.

The first correction is evidence-driven: constrain L40S scheduling to
`US-MO-1`, where two preserved provider readbacks returned 32 vCPU / 125 GiB,
and require that exact datacenter in post-create readback. This historical
shape evidence is not a PF-4 pass. Real cgroup accounting must still show at
least 16 effective CPUs, and the 4-GiB-per-effective-CPU rule remains fixed.

The existing local RunPod credential may be read only to inject the key into
the local controller environment. It must not be printed, persisted, logged,
committed, or transferred to a worker.

No routine confirmation is required within this envelope. Unknown price,
aggregate-cost uncertainty, billing-setting changes, secret exposure,
undeleted resources, or evidence loss are terminal blockers.
