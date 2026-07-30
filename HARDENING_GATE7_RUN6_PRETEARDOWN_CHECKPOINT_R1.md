# Hardening Gate 7 Run 6 — Pre-Teardown Checkpoint R1

- `UTC_CREATED`: `2026-07-30T06:17:14Z`
- `CURRENT_PHASE`: `HARDENING_7_RUN6_PRETEARDOWN`
- `LAST_GREEN_GATE`: `RUN6_TRACK2_AND_MARGIN_GREEN`
- `CURRENT_COMMIT`: `d465c53cde4d885a5e80cdbaf164e2ff137b9632`
- `RUN6_CONTRACT_FILE_SHA256`: `918f876b7fe53ffe2e5055407d92df60cc6b915e64f8af9e627b357bb7707f86`
- `PREFLIGHT_PACKET_SHA256`: `49deb473ad40c892ee8cf396843e1a20f1486bb81d1af634c3895f22b7c01007`
- `POD_ID`: `71rhohlh4fb02f`
- `POD_NAME`: `ck-g7r6-20260730-a01`
- `POD_STATE`: `RUNNING`

## Directly verified completed evidence

- Track 1: 84/84 PASS; behavior failures 0; safety failures 0; false promotions 0; residue 0; sealed host-custody archive SHA-256 `8d991b27e9d5ea9c14b84d69390ae266fd2ba685b27019ab8a36b443618b3dbc`.
- Track 3: exact counts 2,000 / 20,000 / 4,000 / 20,000; 200 vector queries; cleanup 107/107; residue 0; canonical result receipt hash `3061ab71d20c01f0f29001977f378af9dc2bf7e1d26c00d3ed2cc1859f3d4863`.
- Track 2: 3,613.497 measured seconds; 60 checkpoints; 12 safety replays; 12 summaries; 12 Lambda invocations; 108 CockroachDB operations; runtime residue empty; retrieved archive SHA-256 `f6dea043ced007319cf19805dad8ddd430ca8cadf1a8f9028e2997b1a204dc6b`.
- AWS margin: PASS after 901 seconds against a 900-second requirement; credential bytes recorded false; canonical receipt hash `f46ecca5e1abee978c86d6fe9292c749091bc85322308948b9d38ab7a20cc880`; file SHA-256 `0fae224c0895daf6aeaa8c1deacf3b93091abdbf54b72bae8a4eb5db5ca217e6`.

## Next allowed action

Write one hash-bound completion marker. Require `COORDINATOR_GREEN` and
`COORDINATOR_GUARD_GREEN`, then perform the detached exact-ID teardown. Gate 7
does not become GREEN until provider absence, campaign inventory, process and
residue scans, a complete final packet, and same-hash GLM 5.2 plus AGY GREEN are
all directly proved.

Gate 8 remains forbidden until that final independent state exists.
