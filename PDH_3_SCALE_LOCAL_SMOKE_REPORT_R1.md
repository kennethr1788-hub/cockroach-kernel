# PDH-3 Scale Controller Local Smoke Report R1

## Result

`PDH_3_SCALE_LOCAL_SMOKE_GREEN`

- `CAMPAIGN`: `ck-pdh3-scale-local-r4`
- `PRODUCT_CANDIDATE`:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PACKET_SHA256`:
  `c0cd692e3fb630fba54aabf8dcff40125a3d8c8636e0120afe3b7b337f15d49a`
- `RESULT_SHA256`:
  `14895d952dec265a3348b9a5320fc4e48a7931dfce10a3a1efad3c0ed64f2688`
- `EVIDENCE_MANIFEST_SHA256`:
  `19feefd9ce5d8371a1a3af3b44b6fee7aa45951b5576e81231c15c2e40b80f00`
- `TEARDOWN_RECEIPT_SHA256`:
  `41c8ec39e13a46bc13e774b2559e29e1f5a32f621fb9faa305b1498e1ec133a0`

## Measured behavior

- three CockroachDB v26.2.3 nodes on isolated loopback ports;
- 60.001039084 measured seconds;
- 25,455 measured operations;
- 43 fresh-process verifier executions;
- one rotating-node `SIGKILL`, surviving-node query, restart, and exact-count
  reconciliation;
- 100 tasks, 300 trajectory events, 100 receipts, and 50 task-bound vectors;
- zero cross-task vector links;
- five synthetic dependency-advice outcome states;
- one concurrent create/delete cleanup probe with zero residue;
- maximum p99 218.1 ms and maximum observed latency 453.0 ms;
- every final green check true.

## Failed attempts preserved

- R1 and R2 exposed that CockroachDB's `sha256` SQL result required explicit
  hex decoding into `BYTES`.
- R3 exposed that a remote-container disk-occupancy ceiling cannot be
  interpreted against unrelated existing Mac host occupancy.
- R4 preserves the remote production ceiling at exactly 70% while recording,
  but not misclassifying, pre-existing local host disk occupancy.

No failed attempt was pooled into the R4 pass.

## Teardown

- database dropped;
- three database processes stopped;
- all six SQL/HTTP ports closed;
- generated root removed;
- no credential, AWS call, CockroachDB Cloud call, GitHub call, external model
  call, persistent volume, or paid resource used.

This report proves controller-path readiness only. It is not paid cloud,
production-scale, multi-region, or production-traffic evidence.
