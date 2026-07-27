# S3 Failed Closeout Receipt R1

- `S3_RESULT`: `CK_S3_BLOCKED`
- `BLOCKER`: `AWS_AUTH_SESSION_EXPIRED_DURING_EXCHANGE_12`
- `LAST_GREEN_GATE`: `CK_P9_INTEGRATION_GREEN`
- `PRODUCTION_ATTEMPT`: `A04_OF_8`
- `POD_ID`: `he6sw2nz0w3jtk`
- `PRODUCTION_START_UTC`: `2026-07-27T03:40:35Z`
- `COORDINATOR_BLOCKED_UTC`: `2026-07-27T14:40:44Z`
- `RUNPOD_TEARDOWN_GREEN_UTC`: `2026-07-27T14:41:19Z`
- `LOCAL_BRIDGE_STOPPED_UTC`: `2026-07-27T16:22:21Z`
- `RUNPOD_ACTIVE_INVENTORY`: `[]`
- `EXACT_POD_LOOKUP`: `404_NOT_FOUND`
- `DATABASE_RESIDUE_BEFORE_CLEANUP`: `4`
- `DATABASE_RESIDUE_AFTER_CLEANUP`: `0`
- `FORBIDDEN_STATE_TOUCHED`: `NO`
- `RAW_EVIDENCE_REWRITTEN`: `NO`
- `PARTIAL_EVIDENCE_MANIFEST`: `S3_PARTIAL_EVIDENCE_MANIFEST_R1.md`
- `UTC_CLOSED`: `2026-07-27T16:23:59Z`

The coordinator completed eleven live exchanges and accepted request 12 before
an external command failed. The coordinator guard observed the fail-closed
event, wrote the stop marker, stopped and deleted the exact RunPod worker, and
the independent lifecycle guard later recorded `TEARDOWN_GREEN`.

The remote worker evidence tree was not retrieved before deletion and cannot be
reconstructed or claimed. The local bridge remained alive after worker deletion
because the R1 guard terminated the coordinator but not the bridge. It was
stopped by exact PID after all preserved local chain hashes and state had been
inspected. No paid worker was active at that time.

The interrupted exchange left exactly one synthetic task, one trajectory event,
one receipt, and one context vector for `ck-p9-live-refuse-r1`. An exact-ID,
transactional cleanup removed those four declared rows. A read-only post-cleanup
query returned zero matching rows. No unrelated task or production record was
deleted.

This closeout makes the failed campaign safe and usable as Hardening Run input. It
does not make S3 GREEN and does not authorize a replacement S3 worker.
