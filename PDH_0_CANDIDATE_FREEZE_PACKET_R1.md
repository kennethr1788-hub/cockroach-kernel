# PDH-0 Candidate Freeze Independent Review Packet R1

## Decision requested

Return `GREEN` or `BLOCKED` for beginning the local PDH-1 information-boundary
campaign. This packet grants no implementation, tool, public-action, cloud,
credential, paid-execution, or product-mutation authority.

## Frozen authority

- Parent gate: `EV1_AGGREGATE_EVIDENCE_GREEN`
- Product candidate: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- Product tree: `1cbe660a4c6f248b04c7b9db8410f3d0ed1e5ba8`
- Plan SHA-256:
  `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- Parent manifest: `PDH_0_PARENT_MANIFEST_R1.json`
- Parent manifest SHA-256:
  `ab8b0e27b1b0347fbe65bce1ceee53228799af5f3abd2e75454e92d823b23cc2`

## Mechanical evidence

Two fresh detached worktrees at the candidate commit each passed:

1. Python `3.12.13` virtual-environment creation.
2. `pip install .`
3. `cockroach-kernel --help`
4. `cockroach-kernel recover --help`
5. `cockroach-kernel demo --explain`
6. Installed import of `cockroach_kernel.recovery_surface`.
7. Exact worktree teardown.

Same-root repeated demo output was byte-identical. Whole-output hashes differ
across roots only because the human-readable output includes the absolute
receipt paths. Path-excluded behavior and embedded source-result hashes are
stable.

## Outcome-class compatibility

The evidence layer does not replace product reasons:

| Evidence class | Frozen product result |
|---|---|
| `RECOVERED_EXACT` | `PROMOTE / MAX_PROVEN_PREFIX`, empty unrecovered ledger |
| `RECOVERED_MAXIMUM_PROVABLE_SUBSET` | `PROMOTE / MAX_PROVEN_PREFIX`, nonempty unrecovered ledger |
| `UNRECOVERABLE_NO_SURVIVING_REPRESENTATION` | `REFUSE / NO_SURVIVING_CANDIDATE` |
| `INVALID_TAMPERED_EVIDENCE` | `INVALID / REPRESENTATION_HASH_MISMATCH` |
| `INVALID_UNSAFE_INPUT` | product `INVALID` with the exact stable unsafe-input reason |

No outcome class requires product modification.

## PDH-1 execution boundary

- Thirty local measured executions: B1–B6, five fresh roots each.
- Synthetic bytes only.
- Frozen candidate public `recover` command only.
- `/usr/bin/sandbox-exec` with a hashed `(deny network*)` Seatbelt profile.
- Zero models and zero credentials.
- B4 missing bytes retained only in controller memory; never written or passed
  to the product process.
- Before/after file-write manifests, product reason codes, custody state,
  output hashes, model-call count, network count, and teardown state recorded.
- No HOME, private memory, client data, production data, public action, cloud
  resource, or paid execution.

## Known limitation disclosed

The supported installed CLI path passes. A broad diagnostic of the optional
HTTP facade’s installed-package tests exposed source-tree-only imports for
optional P9 modules. PDH-0 and PDH-1 do not use that HTTP facade. If PDH-3 or
PDH-4 later requires that installed facade, the campaign must stop and open a
separate product-revision gate; this packet cannot waive that.

## Kill line

Return `BLOCKED` if the candidate is not actually fixed, if an outcome class
changes product semantics, if the B4 oracle is exposed to the product, if
network denial is not directly proved, if local roots can touch forbidden
state, or if this packet is used to authorize paid/cloud work.

## Required response

Return exactly one JSON object:

```json
{
  "verdict": "GREEN|BLOCKED",
  "packet_sha256": "<exact supplied packet hash>",
  "candidate_binding": "SUPPORTED|UNSUPPORTED",
  "outcome_mapping": "SUPPORTED|UNSUPPORTED",
  "pdh1_boundary": "SUPPORTED|UNSUPPORTED",
  "blockers": [],
  "non_blocking_risks": [],
  "evidence_required": []
}
```
