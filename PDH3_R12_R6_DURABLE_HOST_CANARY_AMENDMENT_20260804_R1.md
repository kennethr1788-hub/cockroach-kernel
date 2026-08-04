# PDH-3 R12 R6 Durable Host Canary — Acceptance Amendment R1

AMENDMENT_STATUS: FROZEN_CANDIDATE
VERSION: PDH3_R12_R6_DURABLE_HOST_CANARY_AMENDMENT_R1
PARENT_PACKET_SHA256: d87ebb182555613ccae5e67a5e61db08477c9a3d575e413ff83905c4a8614738
PARENT_IMPLEMENTATION_COMMIT: ba0f520
REPAIRED_IMPLEMENTATION_COMMIT: 50e99ac
R2_EVIDENCE_ARCHIVE_SHA256: f0989e6000c84f59ae173ae28fdaf6cc8dd37212592d2ffdcf4fd6d09bacfd1a
R2_FINAL_GLM_REVIEW_SHA256: 7f5b8947abcac324ff6e4a264a4e9c0925fb8ebef612f9968a6d13c6be194a0b

## Single acceptance-line amendment

Replace the launcher-status condition with:

> A nonzero `screen` launcher/listing status is diagnostic only; detached-session existence, exact command/session binding, terminal receipt, evidence hashes, and teardown are authoritative.

## Scope and non-retroactivity

This is a prospective interpretation amendment. It does not rewrite, delete, or
replace any R2 receipt, raw output, checkpoint, failure, or timestamp. R2's
false foreground startup status remains preserved as evidence. The amendment
recognizes the independently verified detached process and the completed
terminal/teardown evidence as the authoritative operational result.

No workload, cardinality, threshold, fault schedule, evidence schema, privacy
boundary, cost ceiling, or 24-hour authorization changes. The repaired
implementation at `50e99ac` additionally records the launcher return code and
stdout/stderr hashes, rejects pre-existing sessions, and has 85 passing R6
tests. It is required for any subsequent packet; it is not silently substituted
into R2's historical execution.

## Gate consequence

If an independent judge accepts this exact amendment and the R2 evidence, the
R2 canary may be classified as operationally GREEN for detached continuation,
evidence custody, and teardown. This does not start or authorize a 24-hour
measured soak. Any soak packet must bind the repaired implementation and this
amendment explicitly.

## Kill lines retained

Missing exact-session proof, command/session mismatch, missing terminal receipt,
hash mismatch, evidence loss, undeclared egress, worker residue, unknown cost,
or any measured-clock start remains a failure.
