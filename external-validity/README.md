# External-validity evidence harness

This directory is an evidence-only campaign layer rooted in product candidate
`1c483b1930e629c9ecb6d73418b9554897dc08ad`. It does not alter the product
authority model, verifier, schemas, thresholds, or public claims.

The first execution tranche is deliberately limited to:

1. EV0 protocol freeze, public mechanical canaries, and same-packet GLM/AGY
   preflight; then
2. EV2's 24 measured live CockroachDB Cloud and AWS Lambda fault executions.

EV1 genuine-use measurement and EV3 cross-model hidden measurement are outside
this tranche. Their protocol fields remain frozen, but their hidden inputs do
not yet exist and their measured campaigns must not start here.

All outputs are canonical JSON or newline-delimited canonical JSON. Credential
bytes remain process-local. Generated cloud/database resources are campaign
scoped and must be removed before EV2 can close.
