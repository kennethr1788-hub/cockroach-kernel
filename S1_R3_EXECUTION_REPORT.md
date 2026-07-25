# S1 R3 Foundation Soak Execution Report

- `TECHNICAL_RESULT`: `GREEN`
- `S1_GATE`: `CK_S1_PENDING_FINAL_JUDGE`
- `BLOCKER`: `NONE`; delayed itemization explicitly accepted by Kenneth
- `LAST_GREEN_GATE`: `CK_P4_VERIFIER_GREEN`
- `CAMPAIGN_ID`: `CK-S1-20260725-FOUNDATION-R3`
- `PACKET_SHA256`: `82fc0dcdd38a814e40a39f85c57b1f35948d46792575c7fdd2db24283768ef87`
- `POD_ID`: `wo1iq5wtk04q49`
- `ATTEMPTS_USED`: `1`
- `UTC_REPORTED`: `2026-07-25T22:47:48Z`

## Workload result

The single authorized worker ran the complete frozen 3,600-second S1 workload
from `2026-07-25T21:43:22Z` through `2026-07-25T22:43:32Z`.

- required checkpoints: 61;
- observed checkpoints: 61;
- telemetry records: 61;
- canonical receipt hashes valid: 61/61;
- telemetry links valid: 61/61;
- SQLSTATE 40001 retry handling: PASS at every checkpoint;
- duplicate-receipt idempotency: PASS at every checkpoint;
- restart recovery: PASS at every checkpoint;
- five-repeat deterministic verdicts: PASS at every checkpoint;
- real quarantine exclusion: PASS at every checkpoint;
- rollback: PASS at every checkpoint;
- maximum database growth: 35,598,311 bytes of 268,435,456 allowed;
- final evidence bytes: 59,861 of 67,108,864 allowed;
- workload failure: null;
- interrupted: false;
- runtime residue: empty;
- final status: GREEN.

The final record's canonical hash and manifest linkage recompute exactly:

- `FINAL_EVIDENCE_HASH`:
  `7e712179b9b4e6204cfd9a8142cb7b37c4334342221eaca4ece2d060df8b98ef`;
- `FINAL_JSON_SHA256`:
  `fe8cade647209f656253e16de0f21337781097f29563e7228d7059fe31b39ba3`;
- `MANIFEST_HASH`:
  `5ea87e8075339e36e25fc0d944b3849082b7a650172f6ad1445f77e6c02b8479`.

## Evidence custody

Remote evidence was frozen before teardown. The remote archive SHA-256 is
`72fb147adc9a61b8f6d0fe24539579599928994c1fac1514cb6a754f96d56865`;
the remote per-file manifest SHA-256 is
`f92452cfcdeeb97f052e36bd45f1e5ff9bc6f810773f7dff336a65986fccf50c`.
Local retrieval matched both hashes, and all 126 remote manifest entries passed
`sha256sum -c` with zero failures.

The preserved local evidence tree is `s1-evidence-r3/`, 131 files including the
archive, extracted raw evidence, local verification output, and scanner
reports. Its sorted file-hash digest is
`dc2cda67c3297c6a52ad00a25412b6621cff32b7fec78098cf027f786ae9e5b4`.

## Teardown and scans

The workload and CockroachDB processes were stopped before packaging. The Pod
was stopped at `2026-07-25T22:45:34Z`, deleted at
`2026-07-25T22:45:35Z`, and absent from running and all-status scoped inventory
at `2026-07-25T22:45:37Z`; Pod get returns provider 404. No S1 SSH, transfer,
monitor, watchdog, workload, database, or paid background process remains.

Private-path scan, gitleaks, and detect-secrets all returned no findings. No
forbidden HOME, Qdrant, StateV2, launchd, client, production, or unrelated
project state was read into or written by the workload.

## Billing disclosure and operator decision

The provider billing endpoint returned `[]` for both the earlier failed Pod and
the successful R3 Pod across the immediate query plus six bounded closeout
queries. The aggregate estimated upper charge is approximately $0.070116249,
well below $0.30, but it is not an exact provider charge. The authenticated
Cloud CPU explorer stated that billing data is one hour behind.

Kenneth explicitly confirmed that he can see and accepts the account-side
charge and directed that delayed itemization not block S1. This operator
revision is recorded without fabricating an exact per-Pod value. S1 now awaits
only final independent review of the exact completed packet.
