# Hardening Gate 7 Final Judge Receipt R1

- `UTC_CREATED`: `2026-07-28T23:36:32Z`
- `PACKET`: `HARDENING_GATE7_FINAL_PACKET_R1.md`
- `PACKET_SHA256`: `a27866a084b09d5d4a1e3aaa7202040897150348344e98f3d57fd92e8d1c24fd`
- `PACKET_COMMIT`: `98b2d220e03030fa14b912523023fb5852b2d3f4`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `SAME_HASH`: `YES`
- `RECUSAL_STATE`: `GLM_CLEAR; AGY_CLEAR`
- `TERMINAL_RESULT`: `HARDENING_7_RUN2_BLOCKED`

## GLM lane

- `MODEL`: `glm-5.2`
- `MODEL_PROOF`: `wrapper-verified exact model; fallback disabled; stderr reports served by glm-5.2`
- `VERDICT`: `NOT_GREEN`
- `PACKET_SHA256_RETURNED`: `a27866a084b09d5d4a1e3aaa7202040897150348344e98f3d57fd92e8d1c24fd`
- `RECUSAL_CLEAR`: `true`
- `RAW_SHA256`: `935438b12498044af64c56095b433a87705aebaf1ef791fc653c6ffb8a871808`
- `STDERR_SHA256`: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`

Two earlier GLM attempts are preserved but invalidated. Attempt 1 returned the
old repaired-preflight packet hash. Attempt 2 returned the correct final packet
hash and blocker verdict but contradicted the wrapper's `glm-5.2` served-model
proof by self-labeling as `GLM-4`. Neither attempt is counted.

## AGY lane

- `MODEL_BINDING`: `Gemini 3.1 Pro (High); authenticated inventory to exact backend override to provider response`
- `VERDICT`: `BLOCKED`
- `PACKET_SHA256_RETURNED`: `a27866a084b09d5d4a1e3aaa7202040897150348344e98f3d57fd92e8d1c24fd`
- `RECUSAL_CHECK`: `clear`
- `RAW_SHA256`: `1302cd4e3fd907d67d617a73dab6d1a339134ad62fe2effb72f421b476babbc0`
- `STDERR_SHA256`: `704cd697e3c35f59e1936b327608c169e0648d6966e31ac5a99ade7b5816186e`

## Shared blocking findings

1. `BULK_RESULT_MISSING_AFTER_PARTIAL_INSERT`: the mandatory 46,000-row
   host-only bulk controller exited after 2,000 tasks, 20,000 trajectory
   events, and 4,000 receipts, with 0 vectors and no canonical result receipt.
2. `PACKAGED_EVIDENCE_MANIFEST_HELPER_MISSING`: the required
   `bundle/s3-soak/freeze_evidence_manifest.py` was absent from the accepted
   payload; the deterministic custody fallback does not satisfy that prescribed
   helper gate.

## Valid sub-results preserved

- hidden benchmark 84/84 PASS with zero behavior or safety failures, false
  promotions, or residue;
- one-hour worker GREEN with 3613.026 measured seconds, 60/60 checkpoints,
  12/12 safety replays, 12/12 Lambda calls, and 108/108 CockroachDB operations;
- 900-second post-final-exchange AWS identity probe PASS;
- transferred custody entries verified 318/318 production, 345/345 oracle,
  and 255/255 runner;
- bulk synthetic residue cleaned to 0/0/0/0;
- A03 teardown GREEN, exact Pod ID absent, and active inventories empty.

Both judges independently applied the conjunctive acceptance law. The passed
sub-results remain usable evidence, but neither judge permits them to offset
the two hard blockers.
