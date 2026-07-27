# Hardening Gate 1 CLI Evidence R1

- `UTC_RECORDED`: `2026-07-27T16:40:45Z`
- `IMPLEMENTATION_COMMIT`: `ae3fe17922d9d6dfcb81d69e2080455f597f4cba`
- `PARENT_GATE`: `HARDENING_0_CLOSEOUT_GREEN`
- `TARGET_GATE`: `HARDENING_1_CLI_GREEN`
- `RUNTIME`: `Python 3.12`
- `RUNTIME_DEPENDENCIES`: `none`
- `BUILD_BACKEND`: `setuptools==75.6.0`
- `CONSOLE_SCRIPT`: `cockroach-kernel = cockroach_kernel.cli:main`

## Commands implemented

```text
cockroach-kernel demo
cockroach-kernel demo --explain
cockroach-kernel demo --json
cockroach-kernel inspect <receipt>
```

The commands are a thin facade over the frozen P9 keyless replay and P4
deterministic verifier. They do not add cloud, model, database, or mutation
authority.

## Mechanical verification

- source CLI tests: `6/6 PASS`;
- inherited P9 tests: `113/113 PASS`;
- inherited P4 verifier tests: `6/6 PASS`;
- source total: `125/125 PASS`;
- clean-clone trials: `2`;
- CLI tests per clean clone: `6/6 PASS`;
- inherited P9 tests per clean clone: `113/113 PASS`;
- install command: `python3.12 -m venv <venv>` then
  `<venv>/bin/python -m pip install --no-cache-dir <clone>`;
- each installed CLI was executed with an empty environment and explicit PATH;
- each installed CLI was also executed under `/usr/bin/sandbox-exec` with
  `(version 1)(allow default)(deny network*)`;
- network-denial profile SHA-256:
  `80de7c41c4cac0234db39d259c29450b17c4e5768f24bc7dd9f9f8c75d2c12a3`.

## Deterministic parity

- canonical `demo --json` SHA-256, both clones:
  `5611657a09747307eed0a5c482b8f25855de153c3707eb93b5dd85e893c130fb`;
- promotion receipt SHA-256, both clones:
  `eb1ea7a909b0cab76e8e7ef711c9dfe493affdf7f420ff43066fc75d525965bc`;
- refusal receipt SHA-256, both clones:
  `f94310e76ffc8c99c335e577f14117fe017dc277658fed0f0d79e8ef13404afd`;
- promotion verdict/reason: `PROMOTE / VERIFIED`;
- promotion fresh-context result: `true / FRESH_CONTEXT_PASS`;
- refusal verdict/reason: `REFUSE / HASH_MISMATCH`;
- refusal action: `NONE`;
- replay label: `KEYLESS_LOCAL_REPLAY`;
- network used: `false`;
- credentials used: `false`.

`inspect` reproduced the exact canonical receipt bytes for both branches. A
tampered receipt returned `INVALID / RECEIPT_HASH_MISMATCH` with
`ACTION_TAKEN: NONE`.

## Cleanup and limitations

Both fresh-clone roots were deleted after comparison. No clone root, socket,
FIFO, device, child CLI process, credential, or paid resource remains. The
source clones contained only normal pip-generated `build/` and `.egg-info/`
files after installation; the complete temporary roots were then removed.

This evidence proves a deterministic keyless replay CLI. It does not prove a
public AWS deployment, live cloud behavior, public user research, S3 GREEN, or
submission readiness.
