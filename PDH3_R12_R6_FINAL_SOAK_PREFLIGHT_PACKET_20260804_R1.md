# PDH-3 R12 R6 Final Soak Preflight Packet R1

PACKET_STATUS: FROZEN_CANDIDATE
VERSION: PDH3_R12_R6_FINAL_SOAK_PREFLIGHT_R1
IMPLEMENTATION_COMMIT: 50e99ac
HOST_CANARY_AMENDMENT: PDH3_R12_R6_DURABLE_HOST_CANARY_AMENDMENT_20260804_R1.md
HOST_CANARY_AMENDMENT_SHA256: 5be286acbef96b487680ef02be35f3557b7549e786c6af859be71a88aaefa67e
R2_CANARY_PACKET_SHA256: d87ebb182555613ccae5e67a5e61db08477c9a3d575e413ff83905c4a8614738
R2_EVIDENCE_ARCHIVE_SHA256: f0989e6000c84f59ae173ae28fdaf6cc8dd37212592d2ffdcf4fd6d09bacfd1a
MEASURED_24H_AUTHORIZED: false

## Scope

This packet prepares one possible final 24-hour campaign. It does not launch a
worker, authorize spending, or start the measured clock. The R2 canary remains
immutable evidence; its acceptance amendment distinguishes a cosmetic launcher
status from authoritative detached-session, evidence, and teardown proof.

## Required implementation binding

The final candidate is commit `50e99ac`. It contains the durable supervisor
repair and 85 passing R6 tests. The supervisor rejects a pre-existing session,
waits for bounded registration, recognizes macOS `screen -ls` status 1 when the
exact detached session is present, and records launcher stdout/stderr hashes.
No final campaign may run the older `ba0f520` candidate.

## Provider and worker envelope

- One Secure Cloud NVIDIA L40S worker at the cheapest currently verified price.
- CPU/RAM, image, region, and deadlines are selected mechanically at live
  preflight; no stale hardware default is permitted.
- Container disk ceiling: **250 GB maximum**, because R2 returned 250 GB and the
  final packet must account for it explicitly.
- Persistent/network volume: 0 GB.
- Compute ceiling: $0.99/hour; container-disk rate must be included in the
  active-rate calculation.
- One worker at a time; retries only before main-bundle upload.
- Maximum paid lifetime and aggregate cost must be frozen from live pricing;
  the prior approved envelope was 28 hours and $35, but live revalidation is
  mandatory.
- No AWS/OAuth dependency is allowed during measurement. AWS authentication,
  if needed for setup, must be completed before worker creation and must not be
  required for the measured path.

## Exact-charge requirement

The final closeout must retrieve and preserve the provider's exact charge for
every attempt and the successful worker. Balance deltas and hourly estimates are
not substitutes. If exact billing is unavailable, the campaign remains
`BLOCKED_BILLING_RECONCILIATION_MISSING`, even if all workload assertions pass.

## Measured-start gate

The 86,400-second clock may start only after all of the following are directly
receipted on the same packet hash:

1. PF-4 and extracted smoke are GREEN.
2. PF-2R, PF-5, PF-6, and PF-7 are GREEN at the frozen cardinality.
3. Three complete c500 epochs pass named and aggregate latency gates.
4. Network and evidence-growth projections are below their frozen limits with
   safety margin; continuous observers and real store logs are live.
5. All hashes, source bindings, worker properties, deadlines, and cost bounds
   agree.
6. Lifecycle guard heartbeat, retrieval reserve, and teardown path are live.

Any missing predicate blocks the measured clock; it cannot be inferred from a
successful command or a model summary.

## Preserved workload and claims

The campaign retains exact cardinalities of 500,000 tasks, 5,000,000 events,
1,000,000 receipts, and 250,000 vectors; the fixed concurrency/fault schedule;
named histograms; evidence limits; 24 fault/restart cycles; and 9,976 verifier
executions. No threshold, seed, query, or failure rule may be tuned after
execution begins.

Claims remain bounded: three logical CockroachDB processes on one worker are one
physical failure domain; the network observer detects and fail-closes on
observed egress but is not a preventive firewall; synthetic bounded evidence is
not production-scale evidence; and recovery claims concern surviving captured
representations, not arbitrary deleted bytes from nothing.

## Final closeout gate

Retrieve and hash all raw evidence before deletion. Stop/delete the worker,
prove exact-ID absence and empty campaign inventory, verify no child, SSH,
watchdog, database, or paid process remains, and attach the exact-charge receipt.
Only then may an independent GLM 5.2 review classify the final packet GREEN.

## Kill lines

Any hash mismatch, worker or disk mismatch, missing observer, unbounded growth,
latency breach, exactness failure, fault/recovery failure, undeclared egress,
missing raw evidence, teardown ambiguity, billing uncertainty, AWS-auth renewal
requirement during measurement, or absent independent verdict is BLOCKED.
