# PDH-3 R8 Isolated Local Smoke Packet R6

- UTC frozen: `2026-07-31T18:22:23Z`
- repository HEAD before R8 repair: `8bbdb9166c716054b1186168abcd1d22c794edeb`
- candidate commit: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- plan SHA-256: `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- repaired-source diff SHA-256: `7e91d5151a1b23699a85a95048b9d64abbe1acd3b0e0f1099acd171c92894410`

## Exact repaired sources

- `post-dogfood/pdh3_scale_contract.py`: `f90ee40dddd78da92bc68b74d739c18ef67818335948765ab5ff5e2e823821be`
- `post-dogfood/run_pdh3_scale_campaign.py`: `c970bf0888c68f3a8eee8d48457c478da029aa407305b1aa3c6de3c43b7a6541`
- `post-dogfood/run_pdh3_local_canary.py`: `e7e6abe76787c721fa38e612aa05c8e3b4bd1a4d01b5575ab4d3b81778d9b4dd`
- `post-dogfood/run_pdh3_traced.py`: `79ef6f334812a9c63aac87f4b6ec05bf1834bf37b904ac82d30158cd891e2a71`
- `post-dogfood/build_pdh3_scale_bundle.py`: `7143b7992112f626a1358bc47d141158526d3622a7460da2759126ec30c4aa67`
- `post-dogfood/supervise_pdh3_scale_campaign.py`: `6935824053933a2d85f4fbb07c7e50ab56c83fc133269e92b46dece856f83993`
- `s2-soak/lifecycle_guard.py`: `b50833c71dcbdfa73415cc31f36eb5571e6eb824f116fbb7077ffa88ee8eab5d`

## Reduced local contract

Run the repaired controller once against the pinned local CockroachDB v26.2.3
binary in a fresh generated root with an isolated HOME and diagnostic reporting
disabled. Use 100 tasks, 300 events, 100 receipts, 50 vectors, one 60-second
checkpoint, one fault cycle, and 43 verifier executions. Require exact seed
reconciliation, full vector-index coverage, six-digit query targets, batch-bound
verifier inputs, deterministic receipts, teardown, port closure, and residue
removal.

This is deliberately reduced local evidence. It is not RunPod evidence, target
scale, production traffic, the three-epoch remote premeasurement, or the 24-hour
campaign. A GREEN result must use reduced-local versioning and must not claim a
Secure Cloud RunPod topology.

The exploratory `cockroach demo` action disclosed in
`PDH_3_R8_VALIDATION_BOUNDARY_DISCLOSURE.md` is excluded. This R6 run may use
only its generated disposable root and isolated environment.
