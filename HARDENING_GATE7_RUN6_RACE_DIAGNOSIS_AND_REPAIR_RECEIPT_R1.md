# Hardening Gate 7 Run 6 — Request-Staging Race Diagnosis and Repair R1

- `STATUS`: `LOCAL_REPAIR_GREEN`
- `RUN5_ERROR_HASH`: `a0fe27d29e544bb052dbc74dd324e9f0ab0cbfd9b7985c5fa3610ae782fafa85`
- `HASHED_ERROR_TEXT`: `REQUEST_ENTRY_UNSAFE`
- `HASH_MATCH`: `YES`
- `RUN5_FAILURE_CLASS`: `HOST_BRIDGE_COORDINATOR_STAGING_RACE`
- `PRODUCT_CANDIDATE_CHANGED`: `NO`
- `HIDDEN_SCORER_OR_THRESHOLD_CHANGED`: `NO`
- `RUN5_HIDDEN_INPUT_READ_OR_REUSE`: `NO`

## Direct mechanism

Run 5's bridge downloaded each remote request to
`requests/request-NNNN.json.tmp`, decoded it, then atomically renamed it to the
final `.json` path. The coordinator simultaneously enumerated that same watched
directory and called `entry.is_file()` before checking whether the entry was the
allowed current temporary name. If the bridge renamed the temporary path after
enumeration but before `is_file()`, the stale directory entry no longer existed;
`is_file()` returned false and the coordinator raised `REQUEST_ENTRY_UNSAFE`.

The exact SHA-256 of `REQUEST_ENTRY_UNSAFE` is the recorded Run 5 error hash.
This establishes the historical cause without inspecting or reusing the Run 5
hidden request content.

## Repair

The bridge now downloads to a sibling `staging/` directory outside the watched
`requests/` directory. Only a fully transferred, decoded, campaign-bound,
sequence-bound, parent-bound request is atomically promoted into `requests/`.
The coordinator no longer permits any temporary name in its watched directory;
unknown entries remain fail-closed.

- `REMOTE_BRIDGE_BEFORE_SHA256`: `f96168781fe453eae52db953ebafdb7a710b8ffc0894629b9405f0816ac07685`
- `REMOTE_BRIDGE_AFTER_SHA256`: `c0ea21658213ae5da6936083dace18755ca5d69821ca46147350bc73b595ba83`
- `HOST_COORDINATOR_BEFORE_SHA256`: `b4c258189c2619815c81fed52732071db49404e30350e2c37057b438d1234fb1`
- `HOST_COORDINATOR_AFTER_SHA256`: `4112182c98c0088eb22df38f08bf7d744ddcb5da999aa4afb509bfaa96518a8b`
- `TEST_SOURCE_SHA256`: `1fe638f273cb979bd65614f74f30ea5a76915c2dbefd39add53430403d54fe56`

## Regression proof

The topology test executes all twelve chained requests. Every request is written
in two pieces with a delay while the watched directory is inspected. The
watched directory contains only previously committed `.json` files, never a
temporary transfer. All twelve fixture results return, the coordinator reaches
`COORDINATOR_GREEN`, and the bridge reaches `BRIDGE_GREEN`.

- `TESTS`: `19_OF_19_PASS`
- `TEST_TRANSCRIPT`: `evidence/hardening-gate7-run6-preflight-r1/local-tests.txt`
- `TEST_TRANSCRIPT_SHA256`: `a8eb9a36cfc41976f28863c6c8194bfb57febf55d174733d19229dfc8b8e2cf2`
- `RUNPOD_NON_EXITED_INVENTORY`: `[]`
- `RUN5_EXACT_ID`: `ABSENT`

This proof authorizes packet construction only. It is not Run 6 preflight,
campaign readiness, measured evidence, Gate 7 GREEN, or Gate 8 authority.
