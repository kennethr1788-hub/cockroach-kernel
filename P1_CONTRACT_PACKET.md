# Cockroach Kernel — P1 Contract Packet

**Status:** `CK_P1_CONTRACT_GREEN`
**Project identity:** Cockroach Kernel (one project; internal capabilities are
not separately named products)
**Created UTC:** 2026-07-25T19:43:35Z

## Packet inputs

- Build plan: `COCKROACH_KERNEL_FULL_BUILD_TO_SUBMISSION_SEQUENCE_20260725_R1.md`
- Correction layer: `COCKROACH_KERNEL_PLAN_CORRECTIONS_20260725_R1.md`
- Stage 1 assignments: `COCKROACH_KERNEL_STAGE1_BUILDER_ASSIGNMENTS_20260725_R1.md`
- Rules URL: https://cockroachdb-ai.devpost.com/rules
- Rules snapshot SHA-256: `6032e19ff30e254ec7a8ca73e3da42cccb83d7ec5b42114c1067fdbef6a55aa6`
- Rules rechecked UTC: `2026-07-25T19:45:06Z`

Legacy planning labels are excluded from this contract. The submission is one
new project; prior concepts are not implementation or evidence.

## Unified promise and non-claims

Cockroach Kernel records an agent's declared work trajectory durably, evaluates
candidate continuations against deterministic evidence and safety rules, and
resumes only the maximum-provable continuation after declared loss.

It does not claim restoration of deleted bytes, prediction of the future,
consciousness, model identity, forensic recovery, or guaranteed correctness.

## Deterministic authority contract

State transitions are `DECLARE`, `RECORD`, `EVALUATE`, `PROMOTE`, `REFUSE`, and
`INVALID`. A candidate is promoted only when schema validation, receipt linkage,
integrity checks, policy checks, quorum requirements, and executable tests all
pass. The maximum-provable continuation is the longest candidate prefix meeting
all those checks. Missing quorum, policy veto, tampering, malformed input,
replay, and interrupted recovery fail closed.

Required vectors: safe promotion, unsafe refusal, malformed input, tampered
receipt, replayed one-use warrant, missing quorum, split vote, policy veto, and
interrupted commit.

## Vertical slice contract (`CK_P1_VERTICAL_SLICE_GREEN`)

One scripted trace must: intake a declared task; commit one trajectory event and
receipt to CockroachDB; invoke one least-privilege AWS Lambda worker; commit its
result and provenance; introduce one unsafe/tampered successor; produce
deterministic `REFUSE` or `PROMOTE`; terminate the active session; reconstruct
the maximum-provable continuation; and resume a fresh context.

Required evidence: script, receipt chain, CockroachDB query trace, Lambda
invocation trace, refusal/promotion vector, and fresh-context continuation.

## Tool selection contract (`CK_P1_TOOL_SELECTION_GREEN`)

1. CockroachDB Cloud Managed MCP Server: read-only/audited agent interaction
   with the declared cluster and receipt query trace.
2. CockroachDB Distributed Vector Indexing: retrieval of trajectory/context
   records from the same authoritative CockroachDB state; no separate vector
   database is authoritative.
3. AWS Lambda: one least-privilege worker invocation for bounded evaluation;
   no credentials in the repository and a local mock for clean-clone testing.

Tool use counts only after a receipt proves a meaningful operation. No service
is considered used merely because it is initialized.

## Builder handoff manifests

- **Kimi K3:** schema/fixture and non-authoritative persistence scaffolding.
- **Vibe:** retry, idempotency, failure-injection, corruption/replay, quorum,
  and evidence-budget harness.
- **Devstral:** tool-boundary fixtures, least-privilege matrix, local mocks,
  configuration schema, clean-clone and cost/teardown checklist.
- **Codex:** authority semantics, reconciliation, security, final merge, and
  judge packet.

These are bounded assignments, not completed implementation evidence. Each
handoff must include scope, forbidden paths, changed files, commands, raw tests,
limitations, and SHA-256 manifest.

## Codex reconciliation and conflict ledger

No worker output has yet been accepted. Codex must record each accepted,
rejected, or unresolved contribution and reconcile all hashes before merge.
Worker output cannot define authority or self-approve.

## Gate state

- `CK_P0_RULES_GREEN`: GREEN (`e81948d`)
- `CK_P1_VERTICAL_SLICE_GREEN`: OPEN — contract frozen; execution evidence absent
- `CK_P1_TOOL_SELECTION_GREEN`: OPEN — selection frozen; meaningful-use evidence absent
- `CK_P1_CONTRACT_GREEN`: GREEN — independent GLM review receipt `P1_JUDGE_RECEIPT.md`

No implementation, deployment, spend, or submission is authorized by this
packet alone.
