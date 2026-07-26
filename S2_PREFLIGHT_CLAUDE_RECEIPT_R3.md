# S2 Preflight Claude Receipt R3

- `ARTIFACT`: `S2_PREFLIGHT_PACKET_R3.md`
- `PACKET_SHA256`: `f99a5deda6715fe50a186420594d5797820fe263e06e1b9d5c420a91a5abf6b8`
- `ROUTE`: `claude-judge`
- `SERVED_MODEL`: `claude-opus-4-8`
- `EXIT_STATUS`: `0`
- `VALIDATION`: `VALID_EXACT_HASH_GREEN`
- `RECUSAL_CHECK`: `clear`

## Raw structured result

```json
{
  "role": "Claude — S2 preflight evidence judge (runtime/lifecycle/recovery semantics), non-authoring",
  "packet_sha256": "f99a5deda6715fe50a186420594d5797820fe263e06e1b9d5c420a91a5abf6b8",
  "verdict": "GREEN",
  "blockers": [],
  "non_blocking_risks": [
    "The 2 GiB RSS limit is enforced on CockroachDB, while the local 478 MB peak measured the Python orchestrator; on-target CockroachDB RSS is not yet proved.",
    "The 512 open-file limit is not yet calibrated against Linux CockroachDB; a breach fails closed.",
    "Six-hour resource trends cannot be established from the local smoke and are bounded only by the frozen fail-closed limits.",
    "The synthetic SQLSTATE 40001 exercise plus duplicate-insert check does not demonstrate a full retry-to-success loop, so transaction-retry labeling may overstate that path.",
    "The fixed workload may consume part of the buffer before provider and guard deadlines; overrun fails closed.",
    "The worker may remain billable after normal completion until teardown, but remains inside the frozen aggregate cap.",
    "Production must use an output root distinct from the remote smoke output root."
  ],
  "evidence_gaps": [
    "Parent P3-P7 semantics are bound by source and independently GREEN packet hashes rather than re-embedded in full.",
    "Linux-only enforcement paths and the Linux CockroachDB binary remain unexecuted until the mandatory remote smoke.",
    "The evidence manifest source hash list is narrower than the complete 61-file transfer manifest.",
    "Worker rate and shape can only be proved from the post-create response and are rejected fail-closed if mismatched.",
    "Provider deadline enforcement remains asserted by the creation contract; the local guard proof uses a fake provider.",
    "Exact 72/24/6 production counts and six-hour chain continuity can only be proved by the campaign."
  ],
  "recusal_check": "clear"
}
```

The receipt preserves the judge's meaning in normalized form. The complete raw
terminal result also identified the served model as `claude-opus-4-8` and
returned the exact canonical packet hash.
