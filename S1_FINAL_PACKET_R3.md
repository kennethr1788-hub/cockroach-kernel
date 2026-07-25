# Cockroach Kernel S1 Completed Final Packet R3

- `CLAIMED_GATE`: `CK_S1_FOUNDATION_SOAK_GREEN`
- `CLAIMED_BUNDLE_GATE`: `CK_BUNDLE_A_GREEN`
- `LAST_GREEN_GATE`: `CK_P4_VERIFIER_GREEN`
- `IMPLEMENTATION_AND_EVIDENCE_COMMIT`:
  `d70385db7c9f8b1f10bee6cd82e2220f90edea21`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `PREFLIGHT_PACKET_SHA256`: `82fc0dcdd38a814e40a39f85c57b1f35948d46792575c7fdd2db24283768ef87`
- `CAMPAIGN_ID`: `CK-S1-20260725-FOUNDATION-R3`
- `FROZEN_UTC`: `2026-07-25T22:51:08Z`

## Independent preflight

GLM 5.2 returned GREEN on the exact R3 preflight packet before any R3 worker
creation. The receipt SHA-256 is
`7b283b2410b67a583d75497b200d44711cb71567b7d8a6f96fa03a520dd67aae`.

## Worker and workload

One attempt created Pod `wo1iq5wtk04q49`, an authorized CPU worker with 2
vCPU, 4 GB RAM, $0.06/hour compute, exact
`runpod/base:1.0.2-ubuntu2204` image, 20 GB disposable disk, zero volume, and
zero GPUs. The active rate was $0.064/hour including storage, below the
$0.085/hour ceiling.

The immutable transfer archive, Linux CockroachDB archive and binary, S1
driver, and migration all matched the independently reviewed hashes before
execution. No retry or replacement occurred after verification.

The workload ran from `2026-07-25T21:43:22Z` through
`2026-07-25T22:43:32Z` and produced:

- 61/61 canonical checkpoints;
- 61/61 canonical receipt hashes independently recomputed valid;
- 61/61 telemetry-file links valid;
- SQLSTATE 40001 retry handling PASS at every checkpoint;
- duplicate-receipt idempotency PASS at every checkpoint;
- restart recovery PASS at every checkpoint;
- five-repeat deterministic verdicts PASS at every checkpoint;
- real quarantine exclusion PASS at every checkpoint;
- rollback PASS at every checkpoint;
- maximum database growth 35,598,311 bytes of 268,435,456 allowed;
- final evidence 59,861 bytes of 67,108,864 allowed;
- failure null, interrupted false, runtime residue empty;
- final status GREEN.

Final evidence identifiers:

- final evidence hash:
  `7e712179b9b4e6204cfd9a8142cb7b37c4334342221eaca4ece2d060df8b98ef`;
- final JSON SHA-256:
  `fe8cade647209f656253e16de0f21337781097f29563e7228d7059fe31b39ba3`;
- manifest hash:
  `5ea87e8075339e36e25fc0d944b3849082b7a650172f6ad1445f77e6c02b8479`.

## Evidence retrieval and teardown

The remote evidence archive SHA-256 was
`72fb147adc9a61b8f6d0fe24539579599928994c1fac1514cb6a754f96d56865`.
The per-file remote manifest SHA-256 was
`f92452cfcdeeb97f052e36bd45f1e5ff9bc6f810773f7dff336a65986fccf50c`.
Local retrieval matched both; all 126 manifest checks passed with zero
failures. The preserved 131-file evidence-tree digest is
`dc2cda67c3297c6a52ad00a25412b6621cff32b7fec78098cf027f786ae9e5b4`.

The Pod was stopped and deleted after retrieval. Scoped running and all-status
inventories are empty; Pod get returns provider 404. No S1 SSH, transfer,
monitor, watchdog, workload, CockroachDB, or paid background process remains.
Private-path scan, gitleaks, and detect-secrets returned no findings.

## Billing disclosure and revised operator gate

The CLI Pod billing endpoint returned `[]` for the prior failed Pod and the R3
Pod through six bounded closeout retries. The authenticated Cloud CPU explorer
stated that billing data is one hour behind and did not yet expose a July 25
itemized CPU row. The recorded rate and lifecycle produce an estimated
aggregate upper charge of $0.070116249, below the $0.30 envelope, but this is
not represented as an exact provider line item.

Kenneth explicitly stated that he can see and accepts the account-side charge
and directed that delayed itemization not block S1. The operator-acceptance
receipt SHA-256 is
`d4ae10012d2d6b22706be3f648556395687b3989f3e75a2b9418a3127487dfdd`.
No charge is fabricated, and no billing setting or account state was changed.

## Artifact hashes

- execution report:
  `d215f7e76667ac6c7bd981e4f17c3ebb54b095a3de67b0e2cd34101f3c42ffc4`;
- lifecycle receipt:
  `54412128036cd688e722c9fa7e5e6ba843fcc7df037e39b3ca10fd6e828ed389`;
- billing receipt:
  `fcc79e51aec8e5fedcdbe2aa418fdd2a2bc8caf4a556a83b744b263da45d0f40`;
- local manifest check:
  `feddba5675c35bf40ade67d68fd8fbd685d89455606cc5657cba778820c05e0f`.

## Judge question

Return GREEN only if the completed evidence supports S1 technical success,
payload and verdict integrity, bounded spend, clean teardown, no forbidden data
access, and honest treatment of delayed billing under Kenneth's explicit gate
revision. Otherwise identify the exact blocking contradiction. This packet does
not authorize P5 or any later phase.
