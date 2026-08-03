# PDH-3 R12 R6 Preflight Packet — Immediate After GLM GREEN

PACKET_STATUS: FROZEN_CANDIDATE
PACKET_SHA256: DETACHED
VERSION: PDH3_R12_R6_IMMEDIATE_AFTER_GLM_R1
PROJECT_ROOT: /Users/kennethruedas/sandbox/cockroach-kernel-build-20260725
PARENT_COMMIT: 8b13100b6404a392f5038626cb5b91dc2cab2620

## Launch condition

`launch_mode=IMMEDIATE_AFTER_GLM_GREEN`. The host must verify a fresh same-hash
GLM 5.2 GREEN receipt and then invoke PF4 immediately in the same controlled
workflow. There is no scheduled launch time and no waiting for a clock window.
The packet retains an absolute launch-admission expiry solely as a bounded retry
kill line; provider stop/terminate deadlines are absolute and immutable.

## Independent gate

The exact bytes of this packet are sent to direct `glm-zai` with served-model
verification (`glm-5.2`, fallback disabled). Any verdict other than GREEN blocks
worker creation. The builder cannot self-approve.

## Candidate and repairs

- Candidate commit: `8b13100b6404a392f5038626cb5b91dc2cab2620`
- Repair: checkpoint retrieval/verification/host-ACK retries (three attempts),
  fsynced ACK event log, and explicit generated-root teardown parents.
- Prior failure preserved unchanged: `OFFPOD_ACK_MISSING` on R6 R3.
- Transfer archive:
  `.pdh3-runtime/r12-preflight/r6-repair-sampler-20260803-r4/transfer-r4.tgz`
  SHA-256 `46fcf22b92e69e197274d9249e2404a55f51c29ed271f14cc015726554cb67f5`
- Bundle receipt SHA-256:
  `17674780a738e8955ca193fdf1949f741a9dd1d4c7f409bcaeac9a3777d2ee56`

## Bounded envelope

- Campaign: `ck-pdh3-r12-preflight-r6-immediate-glm-20260803`
- Attempts: at most 3, sequential, one worker at a time, before upload only.
- Worker: Secure Cloud NVIDIA L40S, at least 24 vCPU, at least 94 GiB RAM,
  zero volume, image `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`.
- Current live inventory/pricing must be rechecked immediately before PF4.
- Rate ceiling: $0.99/hour; aggregate ceiling: $12.
- Admission expiry: 45 minutes after packet authorization/GLM verification.
- Provider `stopAfter` and `terminateAfter` are absolute deadlines recorded in
  the config and must be included in every creation request.
- No replacement after upload, no 24-hour measured clock, no AWS login, no
  credentials in the bundle, no HOME/Qdrant/StateV2/production data.

## Required sequence

1. Validate all bound hashes and the direct GLM receipt over this exact packet.
2. Immediately invoke PF4; do not wait for a fixed launch timestamp.
3. Before upload, verify CPU/GPU shape, image, disk, volume, rate, deadlines,
   campaign identity, SSH readiness, and empty prior inventory.
4. Upload the hash-verified synthetic bundle and run the bounded PF2R/PF7/PF8
   preflight. Preserve every checkpoint, ACK attempt, receipt, and raw failure.
5. Retrieve and hash evidence before deletion. Delete the worker, prove exact-ID
   absence and empty campaign inventory, and record billing honestly.

## Kill lines

Unknown price, missing GLM receipt, stale packet, mismatched worker, missing
checkpoint/ACK, hash mismatch, private or credential exposure, undeclared
egress, failed teardown, nonempty inventory, or any deadline/cost violation.

## Success

`CK_R6_PREFLIGHT_GREEN` only after full-cardinality PF2R/PF7/PF8 evidence,
complete ACK chain, clean teardown, exact hashes, and a fresh final independent
GLM 5.2 GREEN review. Otherwise return `CK_R6_BLOCKED` with the exact blocker.
