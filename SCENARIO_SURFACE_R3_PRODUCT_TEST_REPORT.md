# Scenario Surface R3 Product Test Report

- `STATUS`: `R3_PRODUCT_TESTS_PASS`
- `UTC_CREATED`: `2026-07-28T06:33:54Z`
- `CONTRACT_SHA256`: `52fbe37a309cebd3983692c58460fbb6dca64d13eaf6713a5d3c60e88af2fb78`
- `CONTRACT_AUDIT_PACKET_SHA256`: `d86c6433fd3df150490070fa734c49e27d76bcc55bff2f5d4c7084843ccc867d`
- `PYTHON`: `3.12.13`
- `TARGETED_AND_REGRESSION_TESTS`: `304 PASS; 0 FAIL; 0 ERROR`
- `COMPILEALL`: `PASS`
- `RAW_TEST_OUTPUT_SHA256`: `7dbcfcbdba96468a73b0f08f2b560c544421622936a38a4b66a44508be2deb84`
- `GITLEAKS_PRODUCT_DIFF`: `PASS; no leaks found`
- `DETECT_SECRETS_PRODUCT_DIFF`: `PASS; empty results; no network verification`
- `HIDDEN_SEED_CREATED`: `NO`
- `HIDDEN_EXECUTIONS`: `0`
- `PAID_OR_CLOUD_RESOURCE`: `NONE`

## Direct R3 coverage

The installed package passed complete declared loss, partial loss and strongest
candidate selection, clean no-loss, candidate and representation tamper,
fresh-process replay, after-consume interruption, partial-promotion
interruption, canonical encoding, unknown fields, unsupported schema, absolute
and traversal path classes, backslash, NUL, symlink, executable content, root
overlap, HOME rejection, request/root overlap, per-file and aggregate limits,
missing representation, deterministic fresh-root output, no-overwrite conflict,
public help, existing demo, and receipt inspection.

Every tested refusal/invalid/no-loss path compared the successor before and
after or directly proved no declared mutation. The interruption tests proved
the custody sidecar remained `CONSUMED` and a fresh invocation returned
`WARRANT_REPLAY`.

## Regression coverage

The source suites for P3 through P9, hardening Gates 5 through 7, S3 protocol,
and supplemental generalization all passed under their native source-tree test
entry points. The historical R1 surface probe was not rerun against changed
product bytes because it is intentionally candidate-pinned evidence; it remains
immutable and will be superseded by a separately named R3 probe.

## Product hashes before clean-clone proof

- `cockroach_kernel/cli.py`: `1f187a879a1946874b74bd043ff550a61963f6086076aed3c64a79bccd32b609`
- `cockroach_kernel/recovery_surface.py`: `bf13e0cdac3a846c48308ad79c89772e1b533a73dec340f13e25180500f69586`
- `cockroach_kernel/test_recovery_surface.py`: `d666969436776a3093e4b07f1cbbc251c9d7cff05f07db1fde7b7456785a8e07`
- `p7-recovery/records.py`: `97971f48852e94ada7ecabb7dd0390442b4bde11f38fbdb069b10d396355fd34`
- `p7-recovery/fresh_context.py`: `4fbe7ff002bcb26ceb649295a4a4e94d79f7aecbab10eff1e7a75d1c63c577f7`
- `pyproject.toml`: `5aec830e88570393e087b0b9f8b4d1217ef8879cb5c0c643e74a1a2e2e5625e7`
- `README.md`: `3ab7f36445f5790151c20a91d97b68037299933113ccfd8a7e4ac8bb41289fd7`

This report is local product evidence. It does not self-approve the final R3
gate and does not authorize hidden execution or Gate 7.
