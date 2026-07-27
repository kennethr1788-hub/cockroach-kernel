# Hardening Gate 1 CLI Packet R1

## Independent review contract

Review only whether the judge-facing CLI is a faithful, deterministic,
credential-free facade over the existing replay and verifier. Do not propose
implementation, deploy anything, or treat replay as live cloud evidence.

- `TARGET_GATE`: `HARDENING_1_CLI_GREEN`
- `PARENT_GATE`: `HARDENING_0_CLOSEOUT_GREEN`
- `IMPLEMENTATION_COMMIT`: `ae3fe17922d9d6dfcb81d69e2080455f597f4cba`
- `UNDERLYING_S3_RESULT`: `CK_S3_BLOCKED`
- `HARDENING_PLAN_SHA256`: `1ce953127138a35bd9588d686bbefefc0b012e8f2188a8fea736842030d57310`
- `PYPROJECT_SHA256`: `ef4c4b3698de59947d603bcf078a1f55e8425507bc6c1bb99ff8ee029886a074`
- `CLI_SHA256`: `98c0dc51de474a472d49fe014910bfb7d30454a851ba390e66ebe1aeea5a9caf`
- `CLI_TEST_SHA256`: `94204c3627bb66bea93648709e63cfeb759e2b18a4e420ef7102c0941f39281c`
- `P9_REPLAY_ADAPTER_SHA256`: `4e66640f33cc5ec7e6f82e1f03acc50f8fec825c7928937e95caecc9c7dd3b62`
- `EVIDENCE_FILE`: `HARDENING_GATE1_CLI_EVIDENCE_R1.md`
- `EVIDENCE_SHA256`: `494385af055634b07c0c2fcc0fcce71774ccc3898d8031a9d3d51c36a464ac64`

## Acceptance evidence

- four required command shapes exist;
- default output shows both promotion and structured refusal;
- refusal includes verdict, stable reason, bounded provable state,
  `ACTION_TAKEN: NONE`, next safe action, and canonical receipt path;
- `--explain`, `--json`, and `inspect` expose bounded evidence;
- two independent clean clones installed successfully;
- each clean clone passed 6 CLI and 113 inherited P9 tests;
- source passed 125 tests across CLI, P9, and P4;
- promotion and refusal receipt bytes were identical across clones;
- promotion/fresh-context and refusal/no-action parity matches the underlying
  P9/P4 implementation;
- both installed demos passed under an OS-level network-denial profile and an
  empty environment;
- both trial roots were removed and no matching child remains.

## Explicit boundary

The CLI always labels the path `KEYLESS_LOCAL_REPLAY`. It makes no live-cloud,
S3-completion, public-deployment, or public-user claim. A GREEN verdict closes
only Hardening Gate 1.

## Required verdict schema

```json
{
  "verdict": "GREEN|NOT_GREEN|BLOCKED",
  "gate": "HARDENING_1_CLI_GREEN",
  "packet_sha256": "<exact packet hash>",
  "findings": ["<bounded finding>"],
  "reason": "<concise reason>"
}
```
