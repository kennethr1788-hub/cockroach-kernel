# PDH-3 R12 R6 PF-4-only operator authorization R1

Status: `PF4_ONLY_PAID_LIFECYCLE_AUTHORIZED_PENDING_SAME_HASH_PREFLIGHT`

UTC recorded: `2026-08-02T09:53:00Z`

## Exact operator statement

> I authorize a new pf 4

## Bounded interpretation

This statement authorizes exactly one new paid PF-4 capability attempt under
the already approved PDH-3 R12 R6 outer envelope. It does not authorize a main
campaign, a measured 24-hour clock, PF-2R through PF-7, a replacement after
upload, a different provider, billing-setting changes, credential transfer, or
any public action.

The authorized attempt is bounded as follows:

- one RunPod Secure Cloud L40S worker;
- one creation attempt;
- compute price no greater than `$0.99/hour`;
- total active rate, including 250 GB disposable container storage, bounded in
  the frozen packet;
- aggregate PF-4 exposure no greater than `$12.00`;
- paid lifetime shorter than 10 hours and further tightened by fresh absolute
  stop and terminate deadlines;
- 250 GB disposable container disk;
- zero persistent volume and zero network volume;
- synthetic, sanitized PF-4 probe material only;
- the main target-scale bundle is never uploaded;
- mandatory evidence retrieval and worker deletion after PF-4 success or
  failure;
- exact-Pod-ID absence and empty campaign inventory are required before any
  result can be considered complete.

The prior affinity-design review is not provider evidence. Before creation, a
new lifecycle packet must bind current inventory, pricing, code, payload,
deadlines, cost math, teardown commands, and this authorization, and an
independent GLM 5.2 judge must return GREEN over that exact packet hash.

The existing RunPod credential may be read only from the operator-authorized
local configuration and injected into the local controller process environment.
It must not be printed, persisted into project artifacts, logged, committed, or
transferred to the worker.

Any shape, price, image, cloud, disk, volume, affinity, evidence, judge, or
teardown mismatch stops fail-closed before main upload. No routine confirmation
is required inside this exact envelope.
