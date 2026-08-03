# PDH-3 R12 R6 Sampler-Repair Preflight Packet R1

`PACKET_STATUS: FROZEN_CANDIDATE_PENDING_INDEPENDENT_REVIEW`

## Scope and authorization

This packet authorizes one new full-cardinality RunPod preflight campaign only:
up to three sequential Secure Cloud L40S creation attempts, one worker at a
time, no replacement after the main bundle is uploaded, a maximum ten-hour
successful worker lifetime, and a `$12` aggregate campaign ceiling. It does not
authorize the 24-hour measured campaign or any later phase.

The prior R6 run remains immutable failed evidence:
`CK_R6_BLOCKED:SAMPLER_FAILED:1ba550cdd03974b2321eec304d1d20b93db0bb2dd97fc3fa02f8b9f3b89deece`.
Its worker teardown was GREEN and no worker remains active.

## Candidate binding

- `CURRENT_COMMIT: 58ff09838c15d7831f8ccb31df4e844696207301`
- `TRANSFER_ARCHIVE: .pdh3-runtime/r12-preflight/r6-repair-sampler-20260803-r3/transfer-r3.tgz`
- `TRANSFER_SHA256: 9528c00af2bdb4b94ded89108995dd2df44b38a43e78af1f2ea3ac96127804d0`
- `BUNDLE_RECEIPT_SHA256: b28c5676000c666e9e9b66cea7f140d4ef11e74cbafd41aa3ddf6715253b6328`
- `EXTRACTED_SMOKE_RECEIPT_SHA256: 02f72290e29109d4c11e8bdfee643aa73d79fa3ed5a9dd3ab297499c470400e8`
- `RUNPODCTL_SHA256: 67cc575f518d05258f35c4334422f6f730446b7b88864933ed65a05e990ea1f2`

The candidate changes are limited to: retrying transient accounting-file
reads while keeping persistent failures fatal; validating nested generated
roots only when their resolved path remains below `/tmp` or `/private/tmp`
and contains the campaign identity; and binding the PF7 manifest to the
actual `growth-observer.ndjson.gz` artifact. Focused and complete R6 unit
tests pass (`78 tests`, `OK`). The extracted-bundle smoke is GREEN but does
not claim full-cardinality or 24-hour evidence.

## Independent advisory inputs

Kimi was queried through the managed OAuth coding lane as a non-authoring
advisory. Its usable conclusion was to separate genuine sampler exceptions
from clean stop, verify hash-chain finalization, and test successful and
failure stops without changing fail-closed behavior.

Grok was queried in the authenticated browser as a non-authoring advisory. It
identified the same two defects and recommended: bounded retry of ephemeral
resource files, preserving the evidence artifact and exception details, and a
resolved-path prefix guard for nested temporary roots. Neither model had
write, infrastructure, credential, or gate authority.

## Live provider preflight snapshot

- `CAPTURED_UTC: 2026-08-03T16:13:33Z`
- `ACTIVE_PODS: []`
- `POD_LIST_SHA256: a760ba1a9f93166d740aca8443e55a56c4526ed0d91e98338f787435d92f296f`
- `GPU_LIST_SHA256: 528c0fbb7a5b86e4b7ff78fd7f3d0906ba45c31b5a086116419b318735a180ee`
- `L40S: Secure Cloud available, 48 GB VRAM, observed secure price $0.99/hour, stock Low`
- `eligible observed data centers: EU-NL-1 (Low), US-MO-1 (Low)`
- `image: runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`
- `container disk: 250 GB; persistent/network volume: 0`

The exact provider response files are retained under
`.pdh3-runtime/r12-preflight/r6-repair-sampler-20260803-r3/provider/`.

## Absolute lifecycle envelope

- `campaign_id: ck-pdh3-r12-preflight-r6-sampler-repair-20260803`
- `launch window: 2026-08-03T16:20:00Z — 2026-08-03T16:50:00Z`
- `provider stop-after: 2026-08-04T02:10:00Z`
- `provider terminate-after: 2026-08-04T02:15:00Z`
- `max attempts: 3`, sequential, one worker at a time
- `max successful lifetime: 10 hours`
- `aggregate cost ceiling: $12`
- `retry cost is bounded and reconciled before every subsequent attempt`

No worker may be created if observed price, image, secure-cloud flag, GPU,
volume, disk, deadlines, or aggregate cost differs from this packet. No upload
or workload execution may begin until all returned properties pass exact
verification. Once upload begins, replacement creation is forbidden.

## Required remote gates

1. Verify no active worker and freeze the packet hash.
2. Obtain independent GLM 5.2 GREEN on this exact packet hash.
3. Create and verify one Secure Cloud L40S worker; delete and prove absence for
   each failed pre-upload attempt before retrying.
4. Transfer only the hash-bound archive and verify its hash remotely.
5. Run the full-cardinality R6 PF2/PF7 preflight with the frozen thresholds,
   sampler, network proof, checkpoint chain, affinity, and teardown contracts.
6. Retrieve and hash all evidence before deletion; prove exact-ID absence and
   empty campaign inventory; reconcile exact provider billing.
7. Obtain independent GLM GREEN on the final evidence packet.

Any missing evidence, sampler exception, hash mismatch, threshold breach,
uncertain billing, or teardown failure is `CK_R6_BLOCKED`; it is never
converted to GREEN by model summary or operator assertion.

`PACKET_SHA256: COMPUTE_AFTER_FREEZE`
