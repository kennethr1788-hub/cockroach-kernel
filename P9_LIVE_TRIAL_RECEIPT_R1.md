# P9 Two-Live-Trial Receipt R1

- `RESULT`: `P9_TWO_LIVE_TRIALS_GREEN`
- `LAST_GREEN_GATE`: `CK_P8_GOLDEN_GREEN`
- `CONTRACT_SHA256`: `a36ad159c6b353afd1e13a2705882e7e8541bd05f2ed37da1f5d4f5bbeee4be4`
- `CAMPAIGN`: `ck-p9-completion-r1`
- `UTC_CLOSED`: `2026-07-26T22:08:00Z`
- `EVIDENCE_ROOT`: `evidence/p9-completion-live-r1/`

## Distinct live traces

The valid trace used task `ck-p9-live-promote-r1`, request hash
`3c7d6d1bb56f5a3901dbfab9e83a0c1c5fb3d2e9fc8702986f0d5c10daae15ec`,
and sealed receipt hash
`2f30d74734954eab00ceee936c9996bc8a0881b55ee7027b2decccd4a0d6a8bc`.
The local verifier returned `PROMOTE / VERIFIED` five times.

The unsafe trace used task `ck-p9-live-refuse-r1`, request hash
`07e049a9e3552aa5ead493cd728a81d190ddda26c35b77a22d99b3e78665e779`,
and sealed receipt hash
`b6d0fe2e5b004d67c3eea7ebc2ffb45d4defcd6184ec670f068915792aa884d8`.
The local verifier returned `REFUSE / HASH_MISMATCH` five times.

The two Lambda calls returned HTTP 200 with no function error and distinct
AWS request-ID hashes. Both responses were strict-schema validated and remained
`ADVISORY`; neither selected the verdict. Their response hashes are
`d67f70944096a79c427e2086ed3bac723bef071ae3f5d21e70dcaa3eaeeb51f2`
and `4212a2cc26fe4fd7623ba80b8c9d2444d261c4d252d9be673e065b43ceac35ad`.

Each trace atomically committed its task, trajectory event, sealed receipt,
and deterministic context vector. The bounded vector query returned the exact
linked vector with distance zero. Each worker result and projection then
committed successfully.

## Changefeed and fresh-context proof

The primary sinkless changefeed and the resumed changefeed both emitted the
two distinct request IDs plus a resolved cursor. Inspection hashes are
`1add3dd865363cd9c4a1e8aaa909e0c05fde04820d1085a3a0c5f33b4da8239c`
and `49c3e23996a74043ef8f8b8cc625e22753ffae63e6e89d4323a162617ae415c2`.
No changefeed process remained after capture.

Two separate clean-environment Python processes then consumed only the frozen
prepared and reconciled records. The valid capsule continued with
`FRESH_CONTEXT_PASS`; the refused capsule did not continue and returned
`CAPSULE_NOT_PROMOTED`. Both were labeled `KEYLESS_LOCAL_REPLAY`, used no
network or credential, and preserved five-repeat semantic parity. The first
isolated attempt used Python isolated mode and failed before evidence creation
because that mode excludes the script-local modules; the corrected clean
environment disabled user-site imports instead. Both temporary roots were
empty and removed.

## Preserved limitations and non-claims

- One initial read-only linked-row query used `encode()` on already encoded
  view strings and failed with SQLSTATE `42883`; the corrected exact view
  query succeeded. No mutation depended on the failed query.
- One initial sinkless-changefeed readiness probe required exact-PID local
  termination because the shell timeout did not stop the client. The three
  exact processes were stopped and no process residue remained before the
  evidence run.
- One Lambda console editor attempt appended to the default example and failed
  local JSON validation before invocation. It did not call Lambda.
- This receipt proves the bounded synthetic build-time traces. It does not
  claim that cloud output has authority, that the judge path needs cloud
  credentials, or that P9 is GREEN before independent final review.

## Evidence anchors

- reconciled manifest hash:
  `a8c7979dd4710d68cf158b334b94efc2fec8d5569fb69de74b53194a4f91c13c`
- live linked rows SHA-256:
  `b82b35ec123e1592fd7ec69fa9b33c8fabc98a9b530ac89b9e4c75742771ccdf`
- MCP-view rows SHA-256:
  `ff4c50fb8d130dce83462474cdc128828e4643de08b63399496a5c0563b39c39`
- valid fresh-process evidence SHA-256:
  `2194435da7eeeff4b16d31b97afb80a19f19f73d7525fa0d15ac8d08e72dcf39`
- refusal fresh-process evidence SHA-256:
  `cde1a72cb2ab5c47f2c1790c788cc44461be9b3b18f476afe9cd5e8953495521`
