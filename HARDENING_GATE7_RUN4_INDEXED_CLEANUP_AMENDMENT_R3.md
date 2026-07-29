# Gate 7 Run 4 Indexed Cleanup Amendment R3

- `STATUS`: `LOCALLY_AND_LIVE_RECOVERY_GREEN_FULL_CANARY_REQUIRED`
- `UTC_CREATED`: `2026-07-29T05:45:01Z`
- `PARENT_CANARY`: `PUBLIC_CANARY_R2_BLOCKED`
- `RUNPOD_CREATION`: `FORBIDDEN`
- `HIDDEN_SEED`: `ABSENT`

## Amendment

Vector cleanup is no longer grouped by 250 task identifiers, which could
expand to 2,500 indexed vector deletions in one transaction. It now consists
of exactly 80 deterministic cleanup files. Each file performs one transaction:

```sql
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
DELETE FROM ck.context_vectors
WHERE vector_id LIKE '<campaign-prefix>%'
ORDER BY vector_id
LIMIT 250;
COMMIT;
```

The filter and ordering use the indexed primary identifier. The 80-file bound
is sufficient for exactly 20,000 vector records. Receipt, event, and task
cleanup stays at 250 task identifiers per transaction. Total planned cleanup
batches are exactly 107.

## Direct proof

- Entire Gate 7 suite: `21/21 PASS` in `37.428s`.
- Indexed cleanup recovery against R2's live full-workload residue:
  `107/107 PASS` in `86,681 ms`.
- Cleanup retries: `0`.
- Final residue: `[0,0,0,0]`.
- Source SHA-256: `a4aac833a58274de10a4a044704f318698169194b5e0430eee134e9afb2e3017`.
- Test SHA-256: `e4ec423c4208605180ffb467044ed0699a93572af99ff016825a2e7979122a42`.

## Fail-closed boundary

Timeouts remain blocked outcomes and are not retried as if commit state were
known. SQLSTATE `40001` retry remains bounded. R2 remains blocked. One new
public full 46,000-row canary must complete from clean prestate through its own
canonical 107-batch cleanup and terminal receipt before the Run 4 packet can
be frozen.
