# PDH-3 R12 R6 Short Remote Canary — Durable Host Supervisor

PACKET_STATUS: FROZEN_CANDIDATE
PACKET_SHA256: DETACHED
VERSION: PDH3_R12_R6_DURABLE_HOST_CANARY_R1
PROJECT_ROOT: /Users/kennethruedas/sandbox/cockroach-kernel-build-20260725
IMPLEMENTATION_COMMIT: 0d0b46b339f7a6a88bb52185a64cf48269fb9a46

## Stated goal

Prove that the host-side checkpoint/retrieval supervisor survives its launcher
terminal disappearing, continues ACK custody against one already-verified worker,
and performs evidence retrieval plus teardown without creating a replacement or
starting the 24-hour measured campaign.

## Launch rule

`IMMEDIATE_AFTER_GLM_GREEN`: obtain a fresh direct GLM 5.2 GREEN over these exact
bytes, then launch one bounded canary immediately. Absolute provider stop and
terminate deadlines remain mandatory safety bounds; there is no scheduled launch
time.

## Candidate and prior evidence

- Durable wrapper: `post-dogfood/pdh3_r12_r6_host_supervisor.py`
- Orchestrator integration: `post-dogfood/pdh3_r12_r6_orchestrator.py`
- Local terminal-loss canary: GREEN
- Focused/R12 tests: 81 PASS
- Prior R6 worker `kdsdbywxma9vvy` was deleted after host supervision loss;
  its partial evidence remains immutable failure evidence.
- Synthetic transfer archive SHA-256:
  `46fcf22b92e69e197274d9249e2404a55f51c29ed271f14cc015726554cb67f5`

## Bounded canary envelope

- Campaign: `ck-pdh3-r12-preflight-r6-durable-host-canary-20260803`
- One Secure Cloud L40S worker, one worker at a time, max 3 pre-upload attempts.
- Image: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`.
- Minimum 24 vCPU, minimum 94 GiB RAM, zero volume, max $0.99/hour.
- Aggregate ceiling: $12; no 24-hour measured clock.
- Launch admission expires 45 minutes after packet authorization/GLM review.
- No replacement after bundle upload; synthetic data only; no AWS login,
  production data, HOME state, Qdrant, StateV2, or unrelated repositories.

## Required proof

1. Verify the exact worker shape, price, deadlines, image, and empty inventory.
2. Start the durable host wrapper under `screen` + `caffeinate`.
3. Terminate only the foreground launcher/session; do not terminate the detached
   supervisor or worker.
4. Confirm checkpoint ACKs continue after launcher loss and the terminal receipt
   is readable from a fresh process.
5. Retrieve and hash evidence before deletion; delete the worker and prove exact-ID
   absence plus empty campaign inventory.

## Kill lines

Missing GLM, stale hash, worker mismatch, missing ACK after supervisor recovery,
partial or corrupt evidence, undeclared egress, credential/private-data exposure,
supervisor loss without detached continuation, teardown failure, nonempty
inventory, unknown cost, or any measured-clock start.

## Success

`CK_R6_DURABLE_HOST_CANARY_GREEN` only if detached continuation, ACK custody,
terminal receipt, evidence hashing, and teardown all pass. Otherwise return
`CK_R6_BLOCKED` with the exact blocker. This packet never authorizes a 24-hour run.
