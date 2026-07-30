# Hardening Gate 7 Run 6 — Replacement Campaign Contract R1

## Objective

Execute exactly one new hidden Gate 7 campaign after repairing the host
request-staging race that blocked Run 5. Preserve Runs 3, 4, and 5 unchanged.
Advance to Gate 8 only if one complete retrieved Run 6 packet receives final
same-hash GLM 5.2 and AGY GREEN.

## Scope and kill line

Run 6 changes only orchestration and evidence custody. The product candidate,
hidden scenario classes, scorer, thresholds, row counts, cloud-call counts,
verdict law, and safety law remain frozen. Kill Run 6 before worker creation if
the twelve-request race regression, new-input exclusion, bundle custody, cloud
readiness, worker identity, price, lifecycle, or preflight judge gate fails.

After hidden input creation, any product, scorer, threshold, fixture, or
workload change blocks Run 6. Every failure is preserved. No measured rerun is
authorized after the first hidden Run 6 execution begins.

## Run 5 preservation and root-cause boundary

Run 5 remains `GATE7_RUN5_BLOCKED`. Its hidden seed and inputs cannot be read,
copied, replayed, summarized into Run 6 inputs, or used for tuning. The only
historical fact carried forward is the independently hash-matched infrastructure
error `REQUEST_ENTRY_UNSAFE` and its non-content timing mechanism.

The repaired bridge stages downloads outside the coordinator's watched
directory and atomically promotes only validated final files. The watched
directory accepts final request names only. The twelve-request fixture must pass
from fresh temporary roots before packet freeze and again from the extracted
host harness before `CAMPAIGN_READY`.

## Evidence custody

1. Track 1 runs 84 newly generated hidden executions. Its opaque archive,
   aggregate, and custody receipt are copied to the host and hash-verified before
   Track 3 begins. The archive remains mode `0000` and cannot be unsealed until
   worker teardown.
2. Track 3 runs the exact 46,000-row CockroachDB workload, 200 vector queries,
   bounded cleanup, and direct zero-residue proof. Its canonical result,
   terminal, cleanup, journal, and manifest are host-local before Track 2.
3. The Track 2 start gate binds the host-custodied Track 1 and Track 3 hashes.
4. Track 2 runs twelve cloud exchanges, 12 Lambda invocations, 108 CockroachDB
   operations, the full one-hour worker schedule, scheduled checkpoint/safety/
   summary streams, and a post-final-exchange 900-second AWS identity margin
   probe. Coordinator requests, results, per-call evidence, and custody receipts
   are host-local as they are committed.
5. Before worker deletion, retrieve the worker final evidence tree and verify
   its manifest. Only then write the completion marker and perform teardown.

No missing archive, final receipt, checkpoint stream, safety replay, summary,
margin probe, residue proof, or teardown receipt can be averaged away.

## RunPod boundary

- one official Ubuntu 22.04 CPU worker at a time;
- exactly 2 vCPU, 4 or 8 GiB RAM, zero GPU;
- exact image `runpod/base:1.0.2-ubuntu2204`;
- at most 20 GiB disposable container disk and zero persistent/network volume;
- compute at most `$0.10/hour`, total active rate at most `$0.12/hour`;
- aggregate Run 6 exposure at most `$5.00`;
- at most eight sequential pre-upload creation attempts in 120 minutes;
- provider stop and terminate offsets of 390 and 420 minutes;
- one detached exact-ID lifecycle guard; no idle or unguarded paid worker;
- synthetic/sanitized payload only; no cloud credential enters the worker;
- host AWS/Cockroach access remains project-local and least-scoped;
- no HOME, live memory, Qdrant, StateV2, launchd, client/private/production data,
  provider billing settings, or unrelated repository mutation.

Every failed creation/readiness attempt is deleted and proved absent before the
next. Three identical failures require bounded diagnosis and a fresh packet.
Upload ends creation retries. Hidden seed creation ends all replacement
authority for Run 6.

## Gates

1. `RUN6_LOCAL_REPAIR_GREEN`
2. `RUN6_PREFLIGHT_GREEN`: exact same packet, GLM 5.2 and AGY GREEN
3. `RUN6_CAMPAIGN_READY`: verified worker, bundle, extracted smoke, four guards,
   cloud readiness, no hidden seed yet
4. `RUN6_TRACK1_CUSTODY_GREEN`
5. `RUN6_TRACK3_GREEN`
6. `RUN6_TRACK2_START_GREEN`
7. `RUN6_TRACK2_AND_MARGIN_GREEN`
8. `RUN6_RETRIEVAL_AND_TEARDOWN_GREEN`
9. `HARDENING_7_EXPANDED_GREEN`: final same-hash GLM 5.2 and AGY GREEN
10. Gate 8 packaging and independent review

Gate 8 and every later public/release action remain forbidden until gate 9.
