# S3 Preflight Repair Receipt R4

- `R3_PACKET_SHA256`: `098cf186e1e8da56f1e6731f21e09e2833c3b7eea4c3df0cd88e4d18fb2cb2c9`
- `R3_GLM_VERDICT`: `GREEN_INVALIDATED_BY_PACKET_CHANGE`
- `R3_CLAUDE_VERDICT`: `GREEN_INVALIDATED_BY_PACKET_CHANGE`
- `STATUS`: `R4_SCHEDULE_AND_RETRIEVAL_REPAIR_LOCAL_GREEN`
- `UTC_RECORDED`: `2026-07-27T00:13:02Z`

R3 did not authorize a RunPod creation. After both judges returned GREEN,
Codex's final mechanical gate found that the packet described the campaign ID,
attempt names, and lifecycle dates as placeholders. The controlling execution
prompt requires those values to be frozen before creation. Judge approval does
not override that mechanical defect.

R4 corrections:

1. `S3_EXECUTION_SCHEDULE_R1.json` freezes one campaign ID, one campaign
   prefix, all eight permitted attempt names, the 90-minute retry window,
   campaign-ready deadline, provider stop and terminate epochs, accepted worker
   shape, template/image, disk/volume/GPU limits, and spend ceilings.
2. `S3_EXECUTION_WIRING_R1.md` binds every placeholder to that schedule and
   adds exact pre-retrieval remote-manifest, transfer, and local verification
   command families.
3. The local preflight receipt now distinguishes its original evidence time
   from its R3 amendment time instead of implying that later proof existed at
   the original timestamp.

No P9 feature, threshold, allowlist, or cloud contract changed. The worker
bundle changed only to add the hash-pinned atomic evidence-manifest helper and
its local test required by the retrieval correction. No RunPod worker has been
created.
