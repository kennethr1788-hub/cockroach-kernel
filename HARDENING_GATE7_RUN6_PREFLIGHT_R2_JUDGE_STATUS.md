# Hardening Gate 7 Run 6 — R2 Judge Status

- `PACKET_SHA256`: `4171695e8ec4738812417bf70596a807920a76200c93578d769b1350146f53b4`
- `GLM_5_2`: `GREEN; SERVED_MODEL_VERIFIED`
- `AGY`: `INVALID; CHILD_EXIT_0; VERDICT_SCHEMA_REJECTED`
- `R2_PREFLIGHT`: `NOT_GREEN`
- `WORKER_CREATED`: `NO`
- `HIDDEN_SEED_CREATED`: `NO`

The R2 packet asked AGY for `JUDGE: AGY` plus `VERDICT`, while the reviewed
wrapper requires the canonical `AGY_VERDICT` field. The wrapper correctly
withheld the malformed provider response. R2 is preserved and cannot authorize
worker creation. R3 must correct only the output schema and rerun both judges
on one new hash.
