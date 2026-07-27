# Hardening Gate 3 Task Contract R1

- `STATUS`: `TASK_CONFIRMED_TRACE_NOT_YET_ARMED`
- `LAST_GREEN_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `TARGET_GATE`: `HARDENING_3_REAL_WORKFLOW_GREEN`
- `TARGET_CODEBASE`: disposable local clone of the Cockroach Kernel repository
- `SOURCE_COMMIT`: `ba1217c4d830a3c7633e352c0e10712d6b817cee`
- `DISPOSABLE_WORKSPACE`: `.hardening-runtime/gate3-real-workflow/workspace`
- `DATA_CLASS`: non-sensitive project source and synthetic evidence only
- `UTC_RECORDED`: `2026-07-27T19:24:06Z`

## Kenneth's task selection

Kenneth accepted the immediately preceding recommended Gate 3 task and directed
Codex to perform it. The concrete task is:

> Harden the existing CLI so a completed receipt set cannot be silently
> overwritten. The first `cockroach-kernel demo` execution into a clean output
> root must succeed. A second execution targeting that same root must fail
> closed with exit code `2` and one stable sanitized reason code while leaving
> the original receipt bytes unchanged. A new clean output root must continue
> to work normally. Failed writes must leave no temporary-file residue.

This is evidence-integrity hardening, not a new product feature.

## Executable acceptance contract

The isolated successor must prove all of the following:

1. `python3.12 -m unittest cockroach_kernel.test_cli cockroach_kernel.test_http_api`
   exits `0`;
2. the first CLI demo execution into a fresh output root exits `0`;
3. SHA-256 hashes are captured for both original receipts;
4. the second execution into the same root exits `2` with the frozen stable
   overwrite-refusal reason code;
5. the original receipt hashes remain byte-identical after the refusal;
6. no `*.tmp` or other partial write residue remains;
7. a demo execution into another fresh output root exits `0`.

## Human-owned edit

After the isolated trace is armed, Kenneth must personally type and save one
non-sensitive acceptance statement in the declared file:

`.hardening-runtime/gate3-real-workflow/workspace/GATE3_HUMAN_ACCEPTANCE.txt`

Chrome control and CUA may display or navigate to the file, but neither Codex
nor any automation may type or save Kenneth's statement. Direct file-state
evidence and Kenneth's confirmation are required before implementation begins.

## Kill line

Stop without implementation, loss simulation, cloud recording, promotion, or
cleanup if the declared human edit is absent; if any credential, HOME state,
private/client data, unrelated repository, canonical source checkout, or
undeclared external surface would be touched; or if the disposable-workspace
boundary cannot be proved.
