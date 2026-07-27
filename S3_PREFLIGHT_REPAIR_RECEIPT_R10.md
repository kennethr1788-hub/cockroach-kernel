# S3 Preflight Repair Receipt R10

- `PARENT_PACKET`: `S3_PREFLIGHT_PACKET_R9.md`
- `PARENT_PACKET_SHA256`: `71a28d96fa12ef8710a2b9d8d33723bc7b4e6851fe53c2ef0aba4a745119bae2`
- `R9_GLM_VERDICT`: `GREEN_INVALIDATED_BY_R10_PACKET_CHANGE`
- `R9_CLAUDE_VERDICT`: `GREEN_INVALIDATED_BY_R10_PACKET_CHANGE`
- `OPERATOR_DIRECTION`: `NO_ARBITRARY_CAMPAIGN_READY_OR_RETRY_CLOCK_DEADLINES`
- `STATUS`: `R10_ARBITRARY_DEADLINES_REMOVED_JUDGES_PENDING`
- `RUNPOD_ACTIVE_RESOURCES`: `NONE`
- `UTC_RECORDED`: `2026-07-27T01:41:30Z`

## Correction

R10 removes the arbitrary wall-clock fields `creation_not_before_*`,
`campaign_ready_deadline_*`, and `retry_window_end_*`. Project progress no
longer expires at a self-imposed UTC cutoff. Sequential retry authority remains
bounded mechanically by:

- at most eight total creation attempts;
- one worker at a time;
- one production attempt;
- `$3.00` aggregate RunPod exposure;
- `$0.10/hour` active-rate ceiling;
- no replacement after production begins;
- teardown proof before another attempt.

The 43,200-second production duration remains the test definition, not a
completion deadline. Provider-native auto-stop and auto-terminate timestamps
remain mandatory safety fuses so a paid worker cannot run unattended. R10
freezes those fuses at `2026-07-27T15:15:00Z` and
`2026-07-27T15:25:00Z`; creation before `2026-07-27T01:25:00Z` is already
impossible, so even the final fuse remains under the 14-hour paid-lifetime
ceiling. The explicit `delete_epoch` remains equal to the terminate epoch.

No source, bundle, threshold, worker shape, rate, campaign identifier, attempt
name, credential boundary, cloud operation, evidence schema, or teardown rule
changes. Attempt A03 is forbidden until fresh GLM and Claude GREEN verdicts
exist over one R10 packet hash.
