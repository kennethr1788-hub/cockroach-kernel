# Hardening Gate 7 Run 3 A01 Pre-Measurement Setup Receipt R1

- UTC closed: `2026-07-29T04:28:45Z`
- worker: `0jihcbgqjjndw8` / `ck-g7r3-20260729-a01`
- packet SHA-256: `5274e5f8c35383ff26f283764ba64385c3e3e5d5711da07a9b20735c6ccba7c9`
- hidden seed created: `NO`
- measured execution started: `NO`
- immutable transfer payload changed: `NO`
- product candidate changed: `NO`

## Preserved setup failures

1. The first remote extraction command used an unsafe shell-quoting form for
   `awk` under `set -u`. It stopped before extraction. The same immutable archive
   was then checked with `cut`, extracted, and matched all 93 frozen member
   hashes.
2. The archive had no directory entries and extraction occurred under umask
   `077`, leaving parent directories unreadable to the two unprivileged users.
   Only the intended production directory traversal/read permissions were set to
   `0755`; no file bytes changed.
3. The first isolation canary could not traverse the campaign parent directory.
   The campaign root was set to `0755`, then the two fixed public canaries passed
   under the frozen seccomp filter. No hidden input existed.
4. The first bulk-generator verification looked for `bulk-manifest.json`; the
   immutable generator had correctly emitted `manifest.json`. The existing
   output was validated without regeneration.
5. The first host coordinator invocation failed before writing any evidence
   because its custody directory had been pre-created while `CheckpointCustody`
   requires exclusive creation. The replacement coordinator uses new,
   previously nonexistent `coordinator-evidence-r2` and `custody-r2` paths.
6. One screen-launch attempt used unsupported macOS Screen option `-Logfile` and
   created no coordinator process. The succeeding launch uses shell redirection
   to a dedicated stdout file.

All six events occurred before hidden-seed creation and before measured work.
They are classified as setup/orchestration corrections permitted by the frozen
retry law. No result was discarded, no measured execution was restarted, and
none changes the candidate, packet, hidden inputs, scoring, or thresholds.

## Closed condition

The succeeding coordinator, bridge, exact-ID lifecycle guard, and coordinator
guard are all detached and advancing. Their exact snapshot hashes and terminal
acceptance are bound by `HARDENING_GATE7_RUN3_CAMPAIGN_READY_RECEIPT_R1.md`.
