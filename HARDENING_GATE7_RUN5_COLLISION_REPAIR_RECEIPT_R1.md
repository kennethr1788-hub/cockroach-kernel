# Gate 7 Run 5 Collision-Safe Repair Receipt R1

- `UTC_VERIFIED`: `2026-07-29T19:03:15Z`
- `PARENT_COMMIT`: `c35ecae65b1d13789ee629b78c174ffd68bfa691`
- `RUN4_FAILURE_PRESERVED`: `VECTOR_DIGEST_COLLISION`
- `REPAIR_SCOPE`: `DIGEST_SCHEMA_AND_GATE7_HARNESS_ONLY`
- `POST_REVEAL_TUNING_AGAINST_RUN4_INPUTS`: `0`
- `GATE7_TESTS`: `22/22 GREEN; 33.235 seconds`
- `P9_CONTRACT_TESTS`: `8/8 GREEN`
- `PYTHON_COMPILE`: `GREEN`
- `MIGRATION_PROOF`: `GREEN`
- `MIGRATION_OLD_UNIQUE_CONSTRAINT`: `1`
- `MIGRATION_NEW_UNIQUE_CONSTRAINT`: `0`
- `MIGRATION_DIGEST_LOOKUP_INDEX`: `1`
- `MIGRATION_ROWS`: `2`
- `MIGRATION_UNIQUE_VECTOR_IDS`: `2`
- `MIGRATION_UNIQUE_LINKAGES`: `2`
- `MIGRATION_UNIQUE_VECTOR_DIGESTS`: `1`
- `MIGRATION_STORE`: `MEMORY_ONLY`
- `MIGRATION_NETWORK`: `LOOPBACK_ONLY`
- `LOCAL_COCKROACH_PROCESS_AFTER_PROOF`: `ABSENT`

## Exact repaired source bindings

| Path | SHA-256 |
|---|---|
| `hardening-gate7/live_bulk_controller.py` | `834a0c16e524ed13a704c7eaec5859fd642a5e08a895762168115d6972e9d6e8` |
| `hardening-gate7/test_expanded_gate7.py` | `d6aa381d635e9af5b2f50912dfd8d55738d10d15dc3d955ad67c0b30fcae9fd6` |
| `hardening-gate7/run4_evidence_custody.py` | `4990f41a7f9e4522ee9a8c32fe6f47815cb8da1e4130c7b240fada4a17fd3dee` |
| `hardening-gate7/run4_track_gate.py` | `5c8abdf600475826317d1fecfeef66dcaa8a423f99e1bcdb9d7522bef3e072c7` |
| `hardening-gate7/build_expanded_bundle.py` | `f547eff8c79286c46330426f86b0c3b597f0ac487c41dd03b583b1c1ec578bed` |
| `hardening-gate7/freeze_expanded_preflight.py` | `a78d7f79e9dd2654ff0a99c8984f0c13f83225777c6d5e69cf29e02bfd4e4ad7` |
| `hardening-gate7/local_collision_migration_proof.sh` | `1d5a1bae6547c332fc71ec0a3c642e5ee9c9e9761bfec68943130fbe88f6842a` |
| `p9-cloud/migrations/001_cloud.sql` | `b17d93fe6c7236c4498f85cc0c5012f9967ddd8c384ed61c853b901dba539f59` |
| `p9-cloud/migrations/003_collision_safe_vector_digest.sql` | `d4696b355525454158818d29c4c8d6f3fa317e549a5bd32fb184eb008119d660` |
| `p9-cloud/test_contract_artifacts.py` | `14e2cc6ac4a7cc4b1c5e3738f24a2461181e4d8d8e81c1fc77ef21d42ba6b2d3` |

## Finding

The failed Run 4 invariant conflated a content digest with row identity. The
repair removes only that invalid global uniqueness requirement. It retains
unique row IDs and unique task/event/namespace linkage, adds explicit digest
collision accounting, and fails closed on identity or linkage duplication.

This receipt proves the local repair only. It is not public-live canary evidence,
RunPod evidence, Gate 7 GREEN, or Gate 8 GREEN.
