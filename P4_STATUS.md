# P4 Deterministic Verifier

**Status:** `CK_P4_VERIFIER_GREEN`
**Parent gate:** `CK_P3_LEDGER_GREEN`
**Implementation commit:** `4b8bde6`
**UTC:** `2026-07-25T20:57:19Z`
**Judge receipt UTC:** `2026-07-25T20:58:09Z`

The verifier implements canonical serialization, hash/provenance checks,
stable reason codes, path safety, unsupported/tampered/replayed/unsafe refusal,
and quarantine exclusion. Six deterministic unit tests pass. Independent review
is independently verified by `P4_JUDGE_RECEIPT.md`.
