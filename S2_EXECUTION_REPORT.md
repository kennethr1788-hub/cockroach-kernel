# S2 Execution Report

- `UTC_CLOSED`: `2026-07-26T02:21:29Z`
- `RESULT`: `CK_S2_BLOCKED`
- `BLOCKER`: `EXECUTOR_USED_STALE_BINARY_HASH_AFTER_UPLOAD`
- `LAST_GREEN_GATE`: `CK_P7_RECOVERY_GREEN`
- `PREFLIGHT_PACKET_SHA256`: `f99a5deda6715fe50a186420594d5797820fe263e06e1b9d5c420a91a5abf6b8`
- `ATTEMPTS_USED`: `1`
- `POD_IDS`: `btdc8bhvws6cbs`
- `CAMPAIGN_READY`: `NO`
- `TEST_START_UTC`: `NOT_STARTED`
- `TEST_END_UTC`: `NOT_STARTED`
- `MEASURED_TEST_SECONDS`: `0`
- `TOTAL_PAID_LIFETIME_SECONDS`: `<=162`
- `OBSERVED_RATE`: `$0.06/hour compute; <=$0.085/hour frozen active-rate ceiling`
- `BILLING_EVIDENCE`: `CALCULATED_MAXIMUM <= $0.003825; provider query []`
- `TEARDOWN`: `GREEN`
- `ACTIVE_S2_INVENTORY`: `[]`
- `P8_STATUS`: `NOT_STARTED`
- `BAND_B_STATUS`: `OPEN`

## What passed

- P5, P6, and P7 remain independently GREEN.
- GLM 5.2 and Claude Opus 4.8 returned valid GREEN over the exact same S2
  preflight packet hash.
- Attempt 1 matched every approved worker property.
- The detached local exact-ID guard emitted a valid hash chain.
- The exact scanned bundle uploaded successfully and matched its remote hash.
- All 61 transfer-manifest entries passed.
- The runtime archive matched its frozen hash.
- The extracted CockroachDB binary matched the authoritative frozen binary
  hash and returned the expected v26.2.3 Linux AMD64 build identity.
- Teardown completed; exact-ID lookup is absent; S2 campaign inventory is
  empty; no S2 process or temporary transfer artifact remains.

## Why S2 did not run

The executor built the binary-verification command from stale resumed-summary
data rather than rereading the authoritative receipt. The false comparison
failed and triggered premature worker deletion. A subsequent reread proved the
remote binary was correct.

Payload upload had already begun, so the frozen no-replacement law controlled.
The executor did not create another worker and did not start the remote smoke or
six-hour campaign.

## Scanner closeout

The exact transferred bundle was clean under `rg`, `gitleaks`, and
`detect-secrets` before upload. The repository-wide closeout scan reports four
pre-existing gitleaks candidates: two generic-key-shaped evidence/control lines
and two third-party-notice strings in the vendored CockroachDB distributions.
The broader detect-secrets scan reports hash-shaped synthetic fixtures and
evidence receipts. No flagged value entered the exact transfer bundle, and no
credential or private key was transferred.

## Next safe action

Kenneth must explicitly authorize one replacement S2 campaign. The amended
packet must preserve attempt 1, freeze future deadlines, and require every
load-bearing verification hash to be read directly from the frozen local
receipt in the same command that performs the comparison. GLM and Claude must
return GREEN on that revised exact packet before creation.
