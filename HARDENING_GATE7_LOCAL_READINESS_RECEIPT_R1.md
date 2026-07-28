# Hardening Gate 7 — Local Readiness Receipt R1

- `UTC_CREATED`: `2026-07-28T04:01:49Z`
- `PARENT_HEAD`: `48414abba6f90094ebd7a1455d0694fb0fe04950`
- `REMOTE_MAIN`: `48414abba6f90094ebd7a1455d0694fb0fe04950`
- `EVIDENCE_CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `RUNPOD_RUNNING_INVENTORY`: `[]`
- `RUNPOD_CREATED`: `NO`
- `SPEND_INCURRED`: `NO`
- `HELD_OUT_SALT_CREATED`: `NO`
- `HELD_OUT_VECTORS_GENERATED`: `NO`

## Source bindings

- `hardening-gate5/heldout_contract.py`:
  `b5de48cf64cddb505238b835d026fad6ed39917c129bf3b4194f430da1f69801`
- `p4-verifier/verifier.py`:
  `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`
- `p7-recovery/records.py`:
  `97971f48852e94ada7ecabb7dd0390442b4bde11f38fbdb069b10d396355fd34`

## Mechanical results

```text
p4-verifier: 6/6 PASS
hardening-gate5 comparative/held-out contract tests: 7/7 PASS
p7-recovery: 29/29 PASS
known tampered-receipt vector: REFUSE / HASH_MISMATCH PASS
known replayed-warrant vector: REFUSE / REPLAYED_TICKET PASS
local HEAD equals private remote main: PASS
evidence candidate object exists: PASS
RunPod running inventory empty: PASS
```

Known-vector hashes:

- tampered receipt:
  `40864ad869ac2ae23950cd459db0e0a36861b23f8d268903e47863a26db30093`
- replayed warrant:
  `1429cb40c57bb5b822e580046511250198fadb7a9de02de194fdef4865a23880`

## RunPod CLI state

- global binary: `/Users/kennethruedas/.local/bin/runpodctl`
- global version: `2.6.1-32e9aec`
- global SHA-256:
  `34f900d090c68ec04b129c7eebb7c904f14c5b47789d8483846dbef5ec5518fb`
- approved for Gate 7: `NO`
- verified temporary binary: `/tmp/runpodctl-v2.7.2-darwin-arm64`
- temporary version: `2.7.2-309512b`
- temporary SHA-256:
  `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`
- required action: reverify the temporary binary immediately before launch or
  stage a freshly downloaded sandbox-local current binary; do not mutate the
  global installation.

## Current outcome

```text
HARDENING_7_PREFLIGHT_OPEN
RUNPOD_CREATION_FORBIDDEN
```

The known-vector contract and parent custody are healthy. The campaign is not
ready to launch because the 43-trial runner, valid controls, interruption proof,
canonical aggregate, exact profiled live-memory workload, lifecycle envelope,
same-hash GLM/AGY preflight, and Gate 7 spend authorization remain open.
