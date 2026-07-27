# Hardening Gate 6 — Blocked Checkpoint R1

- `STATUS`: `HARDENING_6_RUN1_BLOCKED`
- `BLOCKER`: `EVIDENCE_CANDIDATE_INVALIDATED`
- `LAST_GREEN_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_GREEN`
- `CANDIDATE_IMPLEMENTATION_COMMIT`: `bd29bd23e831175aa54526b9e3c48bd04e8af3ed`
- `STARTING_COMMIT`: `e7d179f9668977e093337db404b90972e6ed898f`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `HARDENING_PLAN_SHA256`: `1ce953127138a35bd9588d686bbefefc0b012e8f2188a8fea736842030d57310`
- `GATE6_EXECUTION_PROMPT_SHA256`: `635c4c457e9f2393ec6be9b71289f0887185c21ef517b3d2be00da4eb705489a`
- `PREFLIGHT_PACKET_SHA256`: `f648e8433928053649ffe4e515a2fae824b2cdeb34afd3403c2fdf4f56e0aed1`
- `RAW_DIAGNOSTIC_SHA256`: `aa79e4bbdecb908d6ab68bcac8e7b4007aad8402da37abfa54dea398a2abbb9b`
- `MEASURED_EXECUTIONS`: `0`
- `RUNPOD_ATTEMPTS`: `0`
- `RUNPOD_ACTIVE_INVENTORY`: `[]`
- `COST_STATE`: `EXACT_$0.00`
- `UTC_RECORDED`: `2026-07-27T22:04:15Z`

The official Linux Restic binary is hash-valid, but the frozen candidate
rejects it and emits Darwin-only tool provenance and preflight-only receipt
labels. Repair requires reopening the frozen candidate contract. No paid
resource or measured evidence was created.
