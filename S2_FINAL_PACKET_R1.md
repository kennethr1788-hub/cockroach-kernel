# S2 Final Evidence Packet R1

- `PHASE`: `S2`
- `TARGET_GATE`: `CK_S2_RECOVERY_SOAK_GREEN`
- `PACKET_STATUS`: `FROZEN_FOR_INDEPENDENT_REVIEW`
- `IMPLEMENTATION_COMMIT`: `fde4da6c1330f147b0e13bb39346c1fad604b6e5`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `AUTHORIZATION_SHA256`: `7661fd8de8284cfd69dfcf584f05e6b0584bb736047e626d594a4595047e486e`
- `REPLACEMENT_PREFLIGHT_PACKET_SHA256`: `b072143dd3ba99250b4abccc171a6640efd644819fd46afb383a007ff6a81a53`
- `P8_STATUS`: `NOT_STARTED`
- `BAND_B_STATUS`: `OPEN`

## Judge boundary

This packet is sanitized evidence. Judges are independent, non-authoring, and
deny-all-tool. They may return a verdict and findings only. They may not write
code, edit files, direct implementation, use shell/browser/network/credentials,
or authorize P8. Each judge must echo the exact packet SHA-256 supplied outside
these bytes, state its served model, and clear recusal.

Roles:

1. GLM: routing, schema, transactions, spend, and evidence completeness.
2. Claude Opus 4.8 via `claude-judge`: runtime, lifecycle, recovery, race,
   timeout, and cleanup semantics.
3. AGY via `agy-judge`: Wall-7 injection, egress, memory, and authority.

## Preconditions and frozen implementation

P3 through P7 were independently GREEN before S2. Replacement preflight GLM
5.2 and Claude Opus 4.8 returned valid exact-hash GREEN on packet
`b072143dd3ba99250b4abccc171a6640efd644819fd46afb383a007ff6a81a53`.
The frozen runtime custody JSON SHA-256 is
`5cbd3a2174ab19d1a33ab21546e7fc4fe0bbc896cbc75f7b2b32f26823588e7c`.
The returned worker was CPU-only, 2 vCPU, 4 GiB RAM, zero GPU, zero volume,
20 GB disposable disk, image `runpod/base:1.0.2-ubuntu2204`, and `$0.06/hour`
compute. Transfer, all 61 manifest entries, runtime archive, runtime binary,
Linux AMD64 identity, detached guard, and 68.085-second on-target smoke passed
before production. Production used a separate fresh output root.

## Six-hour result

The immutable workload ran once. It was never restarted or replaced after its
timer began.

```json
{"actual_counts":{"checkpoints":72,"hourly-summaries":6,"named-events":96,"safety-replays":24},"campaign_id":"CK-S2-20260726-ORCHESTRATION-R2","duration_requirement_met":true,"expected_counts":{"checkpoints":72,"hourly-summaries":6,"safety-replays":24},"failure":null,"final_evidence_hash":"2fc40ba096bfdf9b1e9f4956c55620751514cb04633f562a4b494f945c4aad16","finished_utc":"2026-07-26T09:25:37Z","interrupted":false,"manifest_hash":"9ab3ccaae79f7e56b005ac6607c3630c75a9b39663bd6ee21e07884d378e63f1","measured_test_seconds":21607.859,"runtime_residue":[],"schema_version":"s2-v1","started_utc":"2026-07-26T03:25:29Z","status":"GREEN","stream_requirements_met":true}
```

- `FINAL_JSON_SHA256`: `d0c9d7b20b6a53a38121bf44485be6f5fc69678d7df48619a1835bf23373270d`
- `MANIFEST_JSON_SHA256`: `7e6bbb53e9b4ba5e6bea25d107e8ea20b887559e37e747d083fe03f71b1ab6a0`
- `ASSERTION_RECEIPTS`: `198`
- `FAILED_ASSERTIONS`: `0`
- `MAX_RSS_BYTES`: `836284416` / `2147483648`
- `MAX_OPEN_FILES`: `60` / `512`
- `MAX_DATABASE_GROWTH_BYTES`: `147601628` / `536870912`
- `MAX_EVIDENCE_GROWTH_BYTES`: `461601` / `134217728`
- `NON_LOOPBACK_CONNECTION_OBSERVATIONS`: `0`

Hourly receipt SHA-256 values, in order:

1. `bde53576599233d673517bc3ebeea7e8edda337687a83e86099ab906f1c05a8c`
2. `2a4333791ab9b3c263a1f489246eef3293cf8a478c085b2697438ff995910601`
3. `3c4383d41f4e047af93064d71f66e57a333c54a7425dcba79fc3098f09cc6a8e`
4. `76b09f0030b96ac775d30233f985ef7e9b4c818ab41b02ed0bdc633bb95d4bf9`
5. `a1897abe667276c393ebc72638d5114aa7322d4d98d4ed66265ae3d132eda398`
6. `9941d868bb9296b6f11ab59e74ca520c8e9fcc3a549cc3ef421262aed2db7662`

All five bounded lanes, ordinary 3-of-5 and critical 4-of-5 quorum, dissent,
tie, split, timeout, failed lane, correlated outputs, missing quorum, policy
veto, SQLSTATE 40001 handling, duplicate idempotency, deterministic recovery,
real quarantine exclusion, surviving-representation comparison, valid
promotion, tampered/unsafe refusal, one-use warrant consumption, replay refusal,
fail-closed interruption, fresh-context reconstruction, rollback, and restart
were exercised. Every scheduled assertion receipt returned `PASS`.

## Retrieval and hash reconciliation

- `REMOTE_ARCHIVE_SHA256`: `d52fdbaa0b4e2335ebae66b4bb27ea56787465921b4b9311663a260be93f13fa`
- `REMOTE_RETRIEVAL_MANIFEST_SHA256`: `db544d29e8ad6c7551a447c3a777bd33799017958f8753bc10010d711fbace07`
- `REMOTE_MANIFEST_FILES`: `273`
- `LOCAL_FILES_VERIFIED`: `273/273`
- `HASH_MISMATCHES`: `0`
- `LOCAL_EXTRACTED_TREE_FILES`: `274`, including the retrieval manifest
- `LOCAL_EXTRACTED_TREE_DIGEST`: `0ebf87b079e3d7067af9ad41642854677067cb4f68a5807596abde7cd88c39a0`

Evidence was retrieved and verified before worker deletion.

## Teardown and spend

- `POD_ID`: `m6sj0mkio2yc4y`
- `PROVIDER_STOP_UTC`: `2026-07-26T09:27:55Z`
- `EXACT_ID_LOOKUP`: `404`
- `S2_SCOPED_INVENTORY`: `[]`
- `GUARD_TERMINAL_EVENT`: `TEARDOWN_GREEN`
- `GUARD_TERMINAL_UTC`: `2026-07-26T09:28:32Z`
- `GUARD_TERMINAL_HASH`: `71bbdd52dfc87a9b477713b102c163a88d4465d62dbada76a03a9f8f9e5a43a9`
- `S2_PROCESS_OR_SCREEN_RESIDUE`: `NONE`
- `PERSISTENT_OR_NETWORK_VOLUME`: `NONE_CREATED`
- `UNRELATED_RESOURCE_TOUCHED`: `NO`

Provider itemization returned `[]` at closeout. Under the explicit delayed
itemization clause, the evidence uses a conservative `CALCULATED_MAXIMUM`, not
an exact charge. It covers the whole interval from provider creation through
the later guard teardown proof at the frozen maximum active rate:

- prior attempt maximum: `$0.003825000`;
- replacement maximum: `$0.521492756`;
- aggregate maximum: `$0.525317756`;
- authorized ceiling: `$2.000000000`.

No residual paid resource exists. No billing/account setting changed.

## Residue and safety scans

- symlink scan: zero entries;
- private-path scan: zero entries;
- gitleaks: exit 0, zero findings;
- detect-secrets: exit 0, zero findings;
- runtime residue: `[]`;
- undeclared egress: none observed.

No HOME runtime, live memory, Qdrant, StateV2, launchd, cron, AWS, client data,
production data, credential, public action, P8 action, or unrelated private
source was used.

## Evidence anchors

- `S2_EXECUTION_REPORT_R2.md`: `11aa92bd291549b9314fdbcf30e071e9543c78de26d318a6de5703d54fecfa4f`
- `S2_REMOTE_LOCAL_HASH_RECEIPT_R2.md`: `6b3f664f358ed3a6cc7ae39db5cdc8595a254e9bf5bf3d439ce5d4e9b4abb837`
- `S2_TEARDOWN_RECEIPT_R2.md`: `669f5d0caf92aa4ee8ce380bdc6477fdd67ab56fee3cdf7f3f790657c532655f`
- `S2_BILLING_RECEIPT_R2.md`: `7c4dece6c97ec3ba681e200506676d9a93ce62b27626e50cb1b194281cc6e936`
- `S2_RESIDUE_SCAN_RECEIPT_R2.md`: `6b0e7240d5c80368a392b28bce68885649fae86a5cabff01b27e341646105017`
- `S2_REPLACEMENT_ATTEMPT_LEDGER_R2.md`: `c86ec5bc9d5ec461a5dbfed8e6000301dca15446205c8c9f38ef13511ead5479`

## Required response

Return a structured top-level `GREEN` or `NOT_GREEN`. Echo the exact packet
SHA-256 supplied with this packet and the served model. State the independently
checked role dimensions, blockers if any, non-blocking limitations, and
`RECUSAL_CHECK`. Do not propose or author implementation. GREEN means only that
this packet supports `CK_S2_RECOVERY_SOAK_GREEN`; it does not authorize P8 or
mark Band B GREEN.
