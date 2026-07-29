# Gate 7 Run 3 Blocked Closeout

- `STATUS`: `HARDENING_7_RUN3_BLOCKED`
- `UTC_CLOSED`: `2026-07-29T04:51:00Z`
- `LAST_GREEN_GATE`: `GATE7_RUN3_R5_PREFLIGHT_GREEN`
- `MEASURED_START_COMMIT`: `7fe478bf0c65c5cea544b8cbaa57189dbee1b070`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PREFLIGHT_PACKET_SHA256`: `5274e5f8c35383ff26f283764ba64385c3e3e5d5711da07a9b20735c6ccba7c9`
- `AUTHORIZATION_PROMPT_SHA256`: `a941c6e85d021d2ec77ea442765f4df724283af76f74c8b7f19ed91d077f8d30`
- `RUNPOD_ATTEMPTS`: `1`
- `POD_ID`: `0jihcbgqjjndw8`
- `POD_STATE`: `DELETED; EXACT_ID_ABSENT; CAMPAIGN_INVENTORY_EMPTY`
- `FINAL_JUDGE_PACKET`: `NOT_REACHED`

## Terminal blocker

Run 3 crossed the hidden-input and measured-execution boundary. It is therefore
immutable historical evidence and cannot be relabeled or resumed.

The host coordinator accepted request 2 at `2026-07-29T04:44:29Z` and blocked at
`2026-07-29T04:45:35Z` in `POSTTRIAL_CLEANUP`. The canonical failure receipt
classifies the exception as `UNKNOWN_EXTERNAL_COMMAND`; the failure string binds
to `STAGE_FAILED:POSTTRIAL_CLEANUP:UNKNOWN_EXTERNAL_COMMAND`. The trial-local
cleanup receipt is independently `PASS` with `ZERO_TRIAL_RESIDUE`.

The 46,000-row bulk track had already proved exact inserted counts of
`[2000,20000,4000,20000]` and completed all 80 vector batches, including 20
observed SQLSTATE `40001` retries. Its monolithic cleanup command then exceeded
the 300-second subprocess timeout and emitted `TERMINAL_FAIL`. The fail-closed
second cleanup completed in 222,046 ms and proved residue counts `[0,0,0,0]`.
Because the first cleanup failed, no canonical bulk GREEN result was emitted.

The directly evidenced mechanism is overlapping database-heavy cleanup work plus
a monolithic bulk cleanup transaction whose observed duration exceeded its
bounded timeout. A server-side lock graph was not captured, so no narrower lock
cause is claimed.

## Measured tracks

- `TRACK_1`: `84_OF_84_OBSERVED_GREEN_BEFORE_FAILURE; REMOTE_RAW_AND_SCORED_EVIDENCE_NOT_RETRIEVED; NOT_USABLE_FOR_FINAL_GATE`
- `TRACK_2`: `BLOCKED_AFTER_1_OF_12_CLOUD_EXCHANGES; ONE_HOUR_SCHEDULE_INCOMPLETE; REMOTE_EVIDENCE_NOT_RETRIEVED`
- `TRACK_3`: `46000_ROWS_INSERTED_AND_COUNTED; VECTOR_STAGE_COMPLETE; 20_SERIALIZATION_RETRIES_RECOVERED; CLEANUP_TIMEOUT; FAIL_CLOSED_SECOND_CLEANUP_PASS; ZERO_RESIDUE; RESULT_NOT_GREEN`

No result is averaged against another. Gate 7 is blocked.

## Teardown and cost

- Worker created: `2026-07-29T04:14:33Z`
- Lifecycle guard bound: `2026-07-29T04:15:10Z`
- Guard teardown GREEN: `2026-07-29T04:45:52Z`
- Observed rate: `$0.06/hour`
- Conservative paid lifetime used for math: `1,879 seconds`
- Mathematical maximum from that lifetime and rate: `$0.031317`
- Provider itemization: `PENDING; NOT FABRICATED`
- RunPod exact-ID and campaign inventory: `[]`
- Screen inventory: empty
- Residual bridge process: terminated after Pod deletion; final process scan empty
- CockroachDB synthetic bulk residue: `[0,0,0,0]`

## Preserved evidence

See `HARDENING_GATE7_RUN3_BLOCKED_EVIDENCE_MANIFEST_R1.json`. Runtime artifacts
remain under `.hardening-runtime/gate7-r3/attempt-a01/`; the manifest excludes
the private AWS identity artifact and records only sanitized evidence paths.

## Authorized recovery boundary

Kenneth separately authorized a new rerun after this failure. That authorization
does not permit reusing this hidden seed, tuning this failed campaign, or
relabeling Run 3. The next safe action is a new Run 4 candidate that:

1. replaces monolithic bulk cleanup with deterministic bounded batches;
2. proves cleanup from a full 46,000-row local-compatible fixture;
3. schedules Track 3 to finish and clean before Track 2 begins database-heavy
   live exchanges;
4. freezes a new packet and receives same-hash GLM 5.2 and AGY GREEN;
5. creates a new worker and a newly committed CSPRNG hidden seed; and
6. runs exactly one new measured campaign, stopping again before Gate 8.
