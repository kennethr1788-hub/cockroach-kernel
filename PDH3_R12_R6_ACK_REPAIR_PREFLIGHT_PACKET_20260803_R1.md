# PDH-3 R12 R6 ACK-Repair Preflight Packet R1

`PACKET_STATUS: FROZEN`

## Scope and authorization

This packet authorizes one new full-cardinality RunPod preflight campaign only:
up to three sequential Secure Cloud L40S creation attempts, one worker at a
time, no replacement after the main bundle is uploaded, a maximum ten-hour
successful worker lifetime, and a `$12` aggregate campaign ceiling. It does not
authorize the 24-hour measured campaign or any later phase.

The prior campaign remains immutable failed evidence. Its exact failure was
`OFFPOD_ACK_MISSING`; its worker was deleted and campaign inventory was proven
empty.

## Candidate binding

- `CURRENT_COMMIT: 8b13100b6404a392f5038626cb5b91dc2cab2620`
- `TRANSFER_ARCHIVE: .pdh3-runtime/r12-preflight/r6-repair-sampler-20260803-r4/transfer-r4.tgz`
- `TRANSFER_SHA256: 46fcf22b92e69e197274d9249e2404a55f51c29ed271f14cc015726554cb67f5`
- `BUNDLE_RECEIPT_SHA256: 17674780a738e8955ca193fdf1949f741a9dd1d4c7f409bcaeac9a3777d2ee56`
- `EXTRACTED_SMOKE_RECEIPT_SHA256: 492da92384214db1dc800dc87bf3898db1dae55ee06ef574e33ad5c149cc6c41`
- `RUNPODCTL_SHA256: 67cc575f518d05258f35c4334422f6f730446b7b88864933ed65a05e990ea1f2`

The candidate changes are limited to two repairs: the host checkpoint
supervisor now persists ACK-attempt events and retries each checkpoint fetch
and ACK promotion up to three times; and teardown accepts only explicit,
campaign-bound runtime parents in addition to the temporary-directory rule.
Persistent transfer, hash, or ACK errors remain fail-closed. The relevant
R6 test suite passes (`78 tests`, `OK`). The extracted-bundle smoke is GREEN
but does not claim full-cardinality or 24-hour evidence.

## Required remote gates

1. Verify no active worker and freeze this packet hash.
2. Obtain independent GLM 5.2 GREEN on this exact packet hash.
3. Create and verify one Secure Cloud L40S worker; delete and prove absence for
   each failed pre-upload attempt before retrying.
4. Transfer only the hash-bound archive and verify its hash remotely.
5. Run the full-cardinality R6 PF2/PF7 preflight with the frozen thresholds,
   sampler, network proof, checkpoint chain, ACK retry state machine, affinity,
   and teardown contracts.
6. Retrieve and hash all evidence before deletion; prove exact-ID absence and
   empty campaign inventory; reconcile exact provider billing.
7. Obtain independent GLM GREEN on the final evidence packet.

Any missing evidence, sampler exception, missing ACK after bounded retries,
hash mismatch, threshold breach, uncertain billing, or teardown failure is
`CK_R6_BLOCKED`; it is never converted to GREEN by assertion.

## Absolute lifecycle envelope

- `campaign_id: ck-pdh3-r12-preflight-r6-ack-repair-20260803`
- `launch window: 2026-08-03T21:00:00Z — 2026-08-03T21:30:00Z`
- `provider stop-after: 2026-08-04T06:55:00Z`
- `provider terminate-after: 2026-08-04T07:00:00Z`
- `max attempts: 3`, sequential, one worker at a time
- `max successful lifetime: 10 hours`
- `aggregate cost ceiling: $12`

`PACKET_SHA256: DETACHED`

`HASH_RULE: The packet SHA is carried out-of-band in the config and judge
receipt. The literal DETACHED marker is part of the hashed packet bytes; it is
not replaced after hashing.`
