# S2 Evidence Manifest R2

## Frozen preflight and custody

- `S2_REPLACEMENT_PREFLIGHT_PACKET_R1.md`: `b072143dd3ba99250b4abccc171a6640efd644819fd46afb383a007ff6a81a53`
- `S2_RUNTIME_HASHES_R1.json`: `5cbd3a2174ab19d1a33ab21546e7fc4fe0bbc896cbc75f7b2b32f26823588e7c`
- `S2_REPLACEMENT_SCHEDULE_R1.json`: `dc766db950cd39fe81bc0bd6c39b63be07c72ade677b88f7ae7a489eaaea2e39`
- `S2_CAMPAIGN_READY_RECEIPT_R2.md`: `8e01dce2b7dd95953912220396d3d2f5a6aafd4efdcd13abe77514deca64b2e2`
- `S2_PRODUCTION_START_RECEIPT_R2.md`: `7d01129fce3c7ece7db0afab18975a92f40a7ab430e89f4ac5dc25d5143a1eb3`

## Completed execution and closeout

- `S2_EXECUTION_REPORT_R2.md`: `11aa92bd291549b9314fdbcf30e071e9543c78de26d318a6de5703d54fecfa4f`
- `S2_REMOTE_LOCAL_HASH_RECEIPT_R2.md`: `6b3f664f358ed3a6cc7ae39db5cdc8595a254e9bf5bf3d439ce5d4e9b4abb837`
- `S2_TEARDOWN_RECEIPT_R2.md`: `669f5d0caf92aa4ee8ce380bdc6477fdd67ab56fee3cdf7f3f790657c532655f`
- `S2_BILLING_RECEIPT_R2.md`: `7c4dece6c97ec3ba681e200506676d9a93ce62b27626e50cb1b194281cc6e936`
- `S2_RESIDUE_SCAN_RECEIPT_R2.md`: `6b0e7240d5c80368a392b28bce68885649fae86a5cabff01b27e341646105017`
- `S2_REPLACEMENT_ATTEMPT_LEDGER_R2.md`: `c86ec5bc9d5ec461a5dbfed8e6000301dca15446205c8c9f38ef13511ead5479`

## Raw retrieved evidence

- `s2-evidence/r2/ck-s2-r2-a01-evidence.tar.gz`: `d52fdbaa0b4e2335ebae66b4bb27ea56787465921b4b9311663a260be93f13fa`
- `s2-evidence/r2/ck-s2-r2-a01-retrieval-manifest.json`: `db544d29e8ad6c7551a447c3a777bd33799017958f8753bc10010d711fbace07`
- `s2-evidence/r2/lifecycle-guard.jsonl`: `45450ca57402a3a3f9a0608c010acac30aeb258726f01b4df6ac7f8dd6bd7332`
- `s2-evidence/r2/billing-query.json`: `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`
- `s2-evidence/r2/gitleaks.json`: `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`
- `s2-evidence/r2/detect-secrets.json`: `d1bd75517bf54453b215c5476067066a8a936c9a27bdeeb1caf91bfca6972a3e`
- `s2-evidence/r2/private-path-scan.txt`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `s2-evidence/r2/symlink-scan.txt`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

## Final same-hash panel

- `S2_FINAL_PACKET_R1.md`: `46e1135cd285f0023a12b10bd033808c3f628e577f737f905ef2a27789fdfb9f`
- `S2_FINAL_GLM_RECEIPT_R1.md`: `ca1a134ff86a10c16034f5879d31721cef39319ecabe2b8e3e8a7f607aa06734`
- `S2_FINAL_CLAUDE_INVALID_ATTEMPT_R1.md`: `0928ef75e1c9b79e7d8f5369ab37d2a89c8862a7d51b2c64ef3aa4f6c376ea93`
- `S2_FINAL_CLAUDE_RECEIPT_R1.md`: `b21e708b2a9db859a0655ecb935e07e07551658a90b13c9100c0bfff12a6149d`
- `S2_FINAL_AGY_RECEIPT_R1.md`: `8ee74d18cc8e410c4a2b86ff4f4c6bc8ce3f1541b18acdd37001a91da2b9f6b3`
- `S2_FINAL_JUDGE_PANEL_R1.md`: `eb93a9f556a042b52ebdb62370d488be4e83707648108bb6d939854a5c47d578`

The remote retrieval manifest contains 273 entries and every entry matched
locally. The extracted tree has 274 files because it also contains the remote
retrieval manifest itself. The invalid Claude attempt is preserved but excluded
from the panel; all three valid verdicts share the final packet hash.
