# PDH-3 R6 failure and R7 repair receipt

UTC_CREATED: 2026-08-01T07:23:04Z
STATUS: REPAIR_LOCALLY_GREEN_REMOTE_PROOF_OPEN
PRIOR_CAMPAIGN: ck-pdh3-scale-r8-relaunch-r6
PRIOR_POD_ID: xnlp690a3j3xum
PRIOR_TERMINAL_STATE: BLOCKED_COMPLETE
PRIOR_RESOURCE_STATE: DELETED
MEASURED_24_HOUR_CLOCK_STARTED: false

## Verified R6 facts

- Full setup seed completed: 500,000 tasks, 5,000,000 events, 1,000,000 receipts, and 250,000 vectors.
- The failure occurred during vector-index metadata verification after a nonempty-table `CREATE VECTOR INDEX` backfill destabilized the three-node cluster.
- The terminal SQL error reported unavailable replicas and loss of quorum with nodes 1 and 3 down.
- The exact initial process-death cause is not proved. OOM is not claimed.
- The final evidence archive SHA-256 is `d6a7da76b9641443380052d7f55bf546b8ca28f9ab656326a6abfca79e4a5a6f`.
- The worker was deleted; exact-ID lookup returned absence and matching active inventory was empty.

## Minimal repair

1. Preserve the vector index created by the migration on the empty table.
2. Prove visible index metadata and zero vector rows before seed.
3. Insert vectors independently in batches of at most 250 rows while CockroachDB maintains the existing index.
4. Prove exact post-seed metadata and full forced-index coverage.
5. Remove the obsolete drop/recreate/backfill implementation and its tests.
6. Continuously inspect all three node processes during gateway recovery, restart nodes that die after recovery begins, cap restart attempts, and require two consecutive all-node SQL-ready polls.
7. Update supervisor validation to accept only the new setup-v4 preseed/postseed evidence.

## Direct local evidence

- Active campaign tests: 40/40 GREEN.
- Supervisor archive tests: 11/11 GREEN.
- Three-node real CockroachDB smoke: GREEN for 60.004 seconds.
- Smoke cardinality: 600 tasks, 1,800 events, 600 receipts, 501 vectors.
- Vector insertion batches: 250, 250, and 1.
- Forced-index coverage: 501 returned rows and 501 distinct vector IDs.
- Generated root removed, all node processes stopped, and open ports empty.

Evidence hashes:

- `post-dogfood/run_pdh3_scale_campaign.py`: `2ea43605c757814af995a681aa80a0a384bf6bb4fd459ddea3b5574284120c04`
- `post-dogfood/supervise_pdh3_scale_campaign.py`: `b139e53ada4ca871d0bb546785d237a4560a6d940d07c1834f2880b0c85beeb3`
- Local setup receipt: `81d040641495e6eeb700139f0093bf8a354684985b13889af38e81cec68aa5b3`
- Local result receipt: `2365e041d31dade6a76443547f70395c33bf180c53ae2d067fcc1920851362ed`
- Local teardown receipt: `4944ecf7a82a73f0cc8a6305107cfcf6411258c80e6d829b80db8ba939dc8803`

## Authorization and remaining gate

Kenneth explicitly approved another policy-bounded RunPod run in the current conversation. This authorization permits the replacement lifecycle only after a fresh bundle, extracted-bundle smoke, provider/cost recheck, and identical-packet GLM 5.2 plus AGY preflight GREEN.

The local smoke is fault-detection evidence only. It does not prove the full-cardinality setup or the 24-hour measured campaign. Remote GREEN remains open until the replacement worker completes, evidence is retrieved and hash-verified, teardown is proved, and final independent review passes.
