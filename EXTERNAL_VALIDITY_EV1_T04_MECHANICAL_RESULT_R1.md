# EV1-T04 Mechanical Result R1

- `STATUS`: `MECHANICAL_TASK_COMPLETE_OPERATOR_OBSERVATION_REQUIRED`
- `TASK_ID`: `EV1-T04`
- `UTC_RECORDED`: `2026-07-30T18:24:38Z`
- `TASK_EXECUTION_FILE_SHA256`: `61f78eb3c4d2b43fc9ec4f08382c2c2712c8661892946bba805f433781f89fc4`
- `TASK_EXECUTION_RECEIPT_SHA256`: `12f186dfa6f1d2d70372fa80b1ea82b0b03a713edf2faf155b5c7a6ba2a5a7e5`
- `OBSERVED_VERDICT`: `PROMOTE`
- `STABLE_REASON`: `MAX_PROVEN_PREFIX`
- `FRESH_CONTEXT_CONTINUED`: `TRUE`
- `NETWORK_USED`: `FALSE`
- `CREDENTIALS_USED`: `FALSE`

## Recovery result

- original disposable workspace absent: `TRUE`
- outside deletion canary survived: `TRUE`
- empty-history successor: `TRUE`
- baseline files recreated independently: `74`
- declared work units before loss: `5`
- usable work units after continuation: `5`
- all five restored files byte-exact: `TRUE`
- original workspace residue bytes: `0`
- related process residue: `0`
- unsafe mutations: `0`
- unauthorized path accesses: `0`
- task restatement after loss: `0 words`
- manual intervention after loss: `0`

## Successor acceptance

- Pacific 12-case dashboard-date suite: `PASS`, SHA-256 `6a49b3300432981db63192f716d657b1c0be0e349741eca2abda50a6c5f0a518`
- UTC 12-case dashboard-date suite: `PASS`, SHA-256 `89dca994eb91dabf30dc51461087037c89841ac0319ae55cb100b736120cb40c`
- typecheck: `PASS`, SHA-256 `7ad5370190f3f13153e8329d717ccdfec065241392cd850b68579e68731ca022`
- production build: `PASS`, SHA-256 `b3c7fa47e7f1cf1578e83cabe28aed26d3cb81f10fccfbfa166e0e9e28716225`

The test output directly shows the same explicit late-Pacific instant assigned
to May 13 under `America/Los_Angeles` and May 14 under `UTC`, included on the
reference local day in both environments, with deterministic selection,
invalid-timestamp rejection, input immutability, and zero wall-clock reads
inside the verdict helper.

This is mechanical evidence only. Kenneth must provide the immediate operator
observations before any evaluable-pass label or final objective-evidence audit.
The execution root and preserved dependency runtime remain present until that
observation is recorded and teardown completes.
