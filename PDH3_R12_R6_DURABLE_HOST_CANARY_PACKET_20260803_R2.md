# PDH-3 R12 R6 Short Remote Canary — Durable Host Supervisor R2

PACKET_STATUS: FROZEN_CANDIDATE
PACKET_SHA256: DETACHED
VERSION: PDH3_R12_R6_DURABLE_HOST_CANARY_R2
PROJECT_ROOT: /Users/kennethruedas/sandbox/cockroach-kernel-build-20260725
IMPLEMENTATION_COMMIT: ba0f520

## Stated goal

Prove that the repaired host-side checkpoint/retrieval supervisor survives its
launcher terminal disappearing, continues ACK custody against one already-
verified worker, and performs evidence retrieval plus teardown without creating
a replacement or starting the 24-hour measured campaign.

## Repair under test

The supervisor now waits up to ten seconds for `/usr/bin/screen -ls` to register
the detached session after `screen -dmS` returns. This closes the startup race
that caused the R1 foreground command to report `HOST_SUPERVISOR_DETACH_FAILED`
while its detached stage continued. The wait is bounded and fail-closed.

## Launch rule

`IMMEDIATE_AFTER_GLM_GREEN`: obtain a fresh direct GLM 5.2 GREEN over these exact
bytes, then launch one bounded canary immediately. Absolute provider stop and
terminate deadlines remain mandatory safety bounds; there is no scheduled launch
time.

## Candidate and prior evidence

- Durable wrapper: `post-dogfood/pdh3_r12_r6_host_supervisor.py`
- Regression coverage: `post-dogfood/test_pdh3_r12_r6_host_supervisor.py`
- Orchestrator integration: `post-dogfood/pdh3_r12_r6_orchestrator.py`
- Repair commit: `ba0f520` (`fix detached screen startup race`)
- Local terminal-loss canary: GREEN
- Focused/R12 tests after repair: 82 PASS
- R1 worker `xbog4g7bh0uw94` completed detached execution and was deleted;
  R1 evidence remains immutable and is not reused as R2 proof.
- Synthetic transfer archive SHA-256:
  `46fcf22b92e69e197274d9249e2404a55f51c29ed271f14cc015726554cb67f5`

## Bounded canary envelope

- Campaign: `ck-pdh3-r12-preflight-r6-durable-host-canary-r2-20260804`
- One Secure Cloud L40S worker, one worker at a time, max 3 pre-upload attempts.
- Image: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`.
- Minimum 24 vCPU, minimum 94 GiB RAM, zero volume, max $0.99/hour.
- Aggregate ceiling: $12; no 24-hour measured clock.
- Launch admission is immediate after GLM review and expires only at the
  provider deadline recorded in the generated R2 config.
- No replacement after bundle upload; synthetic data only; no AWS login,
  production data, HOME state, Qdrant, StateV2, or unrelated repositories.

## Required proof

1. Verify the exact worker shape, price, deadlines, image, and empty inventory.
2. Start the repaired host wrapper under `screen` + `caffeinate`.
3. Terminate only the foreground launcher/session; do not terminate the
   detached supervisor or worker.
4. Confirm checkpoint ACKs continue after launcher loss and the terminal receipt
   is readable from a fresh process without a false startup BLOCKED result.
5. Retrieve and hash evidence before deletion; delete the worker and prove
   exact-ID absence plus empty campaign inventory.

## Kill lines

Missing GLM, stale hash, worker mismatch, missing ACK after supervisor recovery,
partial or corrupt evidence, undeclared egress, credential/private-data exposure,
supervisor loss without detached continuation, teardown failure, nonempty
inventory, unknown cost, or any measured-clock start.

## Success

`CK_R6_DURABLE_HOST_CANARY_GREEN` only if the repaired startup path, detached
continuation, ACK custody, terminal receipt, evidence hashing, and teardown all
pass, followed by final independent GLM review over the complete R2 evidence
packet. Otherwise return `CK_R6_BLOCKED` with the exact blocker. This packet
never authorizes a 24-hour run.
