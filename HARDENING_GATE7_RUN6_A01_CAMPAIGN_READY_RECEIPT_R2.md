# Gate 7 Run 6 A01 Campaign Ready Receipt R2

- `STATUS`: `CAMPAIGN_READY`
- `UTC_CORRECTED`: `2026-07-30T04:49:00Z`
- `SUPERSEDES`: `HARDENING_GATE7_RUN6_A01_CAMPAIGN_READY_RECEIPT_R1.md`
- `SUPERSEDED_FIELD`: `MEASURED_HIDDEN_CAMPAIGN_ID`
- `RUN6_TRACK_GATE_BASE_CAMPAIGN_ID`: `ck-g7r5-run6-20260730-a01`
- `MEASURED_HIDDEN_CAMPAIGN_ID`: `ck-g7r5-run6-20260730-a01-measured`
- `TRACK3_CAMPAIGN_ID`: `ck-g7r5-run6-20260730-a01-bulk`
- `TRACK2_LIVE_CAMPAIGN_ID`: `ck-s3-g7r6-a01`
- `HIDDEN_SEED_EXISTS_AT_CORRECTION`: `NO`
- `MEASURED_EXECUTION_STARTED_AT_CORRECTION`: `NO`
- `PREFLIGHT_PACKET_SHA256`: `49deb473ad40c892ee8cf396843e1a20f1486bb81d1af634c3895f22b7c01007`
- `SOURCE_BINDINGS_SHA256`: `44afd2b2d15626642ed22eec525e039ea8f305f243797cd686c12c16b3a52cc9`

The frozen `hardening-gate7/run4_track_gate.py` interface validates base
campaign identifiers against `^ck-g7r[45]-[A-Za-z0-9-]+$`. Its source bytes
and hash were independently approved and are already inside the immutable
worker bundle. Rewriting that source after approval and upload would create
packet and payload drift.

This receipt therefore uses the existing `ck-g7r5-` compatibility namespace
while explicitly embedding `run6` in the identifier. The namespace is a
frozen protocol-version compatibility label, not a claim that this is Run 5.
Run 5 remains immutable failed evidence; no Run 5 hidden input, seed, output,
or campaign artifact is read or reused.

No code, packet, source binding, uploaded payload, threshold, schedule, cloud
resource, or evidence requirement changed. Every other field and proof in R1
remains controlling. This correction was frozen before hidden-input generation
and before any measured execution.
