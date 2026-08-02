# PDH-3 R12 R6 CPU-affinity packet authorization R1

UTC recorded: `2026-08-02T09:35:32Z`

Operator statement, preserved verbatim:

> I give authorization for a new packet selecting a compliant shape or prospectively proving a workload CPU-affinity cap.

Interpretation and boundary:

- authorized: design, implement, locally test, package, freeze, and independently
  review one prospective CPU-affinity repair packet;
- selected path: preserve the existing resource invariant by applying a
  fail-closed Linux CPU-affinity cap derived from the returned provider vCPU
  and memory values;
- not authorized by this statement: creating, starting, retaining, replacing,
  or charging a RunPod worker;
- any future paid worker requires a fresh lifecycle authorization, current
  provider inventory and pricing, fresh absolute deadlines, and a packet-bound
  controller configuration;
- the prior failed worker and its evidence remain immutable.

This receipt does not mark PF-4, R6, or the 24-hour campaign GREEN.
