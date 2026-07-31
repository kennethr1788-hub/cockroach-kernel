# PDH-1 Information-Boundary Final Review Packet R1

## Decision requested

Return `GREEN` or `BLOCKED` for
`PDH_1_INFORMATION_BOUNDARY_GREEN`. Judge evidence only. Do not propose code,
product changes, cloud work, or downstream execution.

## Frozen bindings

- Product candidate:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- PDH-0 packet:
  `17687d96e46002adca0f712a5b6355bac897e7d11ae11f6e2e5e0fca530f0006`
- Harness-repair preflight packet:
  `e22a3945b826dd9a78a6dba187e52a9dc16ca0e7f95dead7c9bd7f88a1668e7f`
- Frozen controller SHA-256:
  `3ef65df94c654cd183fbae5c5fbf4b566c79f7109e369484d90fc254fd22a6d9`
- Mechanical receipt file SHA-256:
  `9de60ade4e7ca403f4025802d8e1d71aeaec1819d5906e9d639cd4b5ca091b19`
- Mechanical receipt internal SHA-256:
  `c1d0a6b0fc090ac6b9263c6be08ced045bc2c7393c9d60a22521acc07c99f189`
- Report: `PDH_1_INFORMATION_BOUNDARY_REPORT_R1.md`
- Report SHA-256:
  `ee9a9e6c9d53d47581d16bfe9ca9c029720e4c8b2267da39cc6f6496fffe602f`

## Results

- 30 measured executions: B1–B6, five fresh roots each.
- 30 passed their frozen expected outcome.
- 30 roots were absent after teardown.
- All six cases had one identical semantic hash across five repeats.
- B1, B2, B3: exact recovered bytes.
- B4: `REFUSE / NO_SURVIVING_CANDIDATE`; zero oracle-byte
  materializations; no replacement candidate.
- B5: exact provable file plus explicit unrecovered ledger for the unavailable
  file.
- B6: `INVALID / REPRESENTATION_HASH_MISMATCH`; zero workspace/output
  mutation.
- Model calls: zero.
- Network: denied by OS profile and a failed loopback probe.
- Credentials: none in child environment.

## Preserved failures

One 30-execution attempt and one diagnostic canary failed before product import
due to a venv-launcher binding error in the evidence controller. Both receipts
remain preserved and excluded. A narrow controller repair was independently
reviewed before the successful measured campaign. Product code, cases,
thresholds, and expected outcomes did not change.

## Review criteria

1. B1–B3 are byte-exact recoveries from explicit representations.
2. B4 proves honest refusal and does not invent or materialize oracle bytes.
3. B5 does not overstate the recovered subset.
4. B6 rejects tamper without mutation.
5. Five-repeat semantics are deterministic.
6. Network, model, credential, root, and teardown boundaries are supported.
7. The claim remains limited to captured representations and does not imply
   arbitrary undelete, forensic recovery, or recovery from nothing.

## Required response

Return raw JSON only:

```json
{
  "verdict": "GREEN|BLOCKED",
  "packet_sha256": "<exact supplied packet hash>",
  "matrix_correctness": "SUPPORTED|UNSUPPORTED",
  "b4_no_invention": "SUPPORTED|UNSUPPORTED",
  "determinism": "SUPPORTED|UNSUPPORTED",
  "boundary_enforcement": "SUPPORTED|UNSUPPORTED",
  "claim_scope": "SUPPORTED|UNSUPPORTED",
  "blockers": [],
  "non_blocking_risks": [],
  "evidence_gaps": []
}
```
