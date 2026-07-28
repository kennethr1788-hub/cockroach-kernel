# Fresh-Context Black-Box R3 — Public-Fixture Preflight Report

- `STATUS`: `PUBLIC_FIXTURE_PREFLIGHT_GREEN_PENDING_INDEPENDENT_REVIEW`
- `UTC_EXECUTED`: `2026-07-28T07:05:32Z`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PREFLIGHT_IMPLEMENTATION_COMMIT`: `18f400ae4ba09a62a4a8aa7d338eeb3886f11208`
- `R3_PLAN_SHA256`: `92f17ed947e874538b991f6281a3e4b67818a5a28820f07f7a12fbf3f5269adf`
- `RAW_RECEIPT`: `FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_RAW_R3.json`
- `RAW_RECEIPT_SHA256`: `34e9fcd9c2f2efe113c0657eb4c5097e44b9726e645c6be3c8b40e3c27f1d9d4`
- `UNIT_TESTS`: `5 PASS / 0 FAIL`
- `UNIT_TEST_RAW_SHA256`: `8dad7f13b9c035e5c23fcb3f1d8db0bbbe8f4e37c471b1161e95063c4b501134`
- `SURFACE_PROBE_R3_SHA256`: `20eaa5a88028911f04614a6635f573addc8371ebe653f619864adc4880fb84af`
- `SANDBOX_EXEC_SHA256`: `8857d087219f0f39d3e3c163e5d0a0aed690cc22f34b50c7eee3d74f93e69688`
- `SEATBELT_PROFILE_SHA256`: `6358a9beae8361105578231b64ca638a99cbf780e1c8f5d24f9ff71891f0bc2b`
- `HIDDEN_SEED_CREATED`: `NO`
- `HIDDEN_EXECUTIONS`: `0`
- `MODEL_ACTOR_CALLS`: `0`
- `PAID_RESOURCES`: `0`
- `GATE7_EFFECT`: `NONE`

## Direct outcomes

- Scenario binding: two identical alpha fixtures produced identical semantic
  hashes, while the omega fixture produced distinct request, decision, receipt,
  and summary hashes. The representation roots were unchanged.
- Allow canaries: `5/5` — installed help, public docs, workspace write, bounded
  output, and in-sandbox acceptance check.
- Deny canaries: `12/12` — outside read/write, scorer, generator, answer key,
  cross-session root, policy/monitor mutation, IPv4, IPv6, DNS, and unapproved
  child execution all returned OS-enforced denial plus a ledger event.
- Live telemetry: `22/22` ordered hash-chained events validate, and the event
  bytes recompute to the recorded telemetry hash.
- Telemetry calibration: `8/8` injected faults reject with their specific
  reason codes; the clean control passes.
- Residue calibration: all nine required mutations are detected — file,
  directory, symlink, living child, open descriptor, open socket, stale marker,
  cross-session artifact, and modified file — while the clean control passes.
- Scorer calibration: all ten required fault classes reject; documented help,
  version, which, runtime-internal reads, and incidental paths pass.
- Exact archived candidate installation, installed module hashes, profile and
  helper hashes, cleanup, secret scans, private-path scan, and zero product
  drift all pass.

## Isolation qualification

The fixed profile begins with `(deny default)`, denies network, constrains
execution to the staged Python and installed entrypoint, removes user,
mounted-volume, application, optional-software, and general temporary
namespaces, and reopens only the copied runtime/package and declared public
fixture roots. It does not modify the firewall. `/usr/bin/sandbox-exec` is
deprecated by macOS but is the exact mechanism required by the frozen target
contract and loaded successfully on this machine.

## Claim boundary

This is public-fixture preflight evidence, not black-box campaign evidence. It
does not establish independent human testing, production scale, hidden-case
generalization, or recovery of uncaptured bytes. No hidden seed or actor session
was created. A separate authorization and frozen packet are required next.
