# P7 Evidence Manifest

- `UTC_CREATED`: `2026-07-26T01:23:38Z`
- `IMPLEMENTATION_COMMIT`: `08de647c4f910cdd22905980511702bd20eeffb1`
- `PARENT_GATE`: `CK_P6_QUORUM_GREEN`
- `TARGET_GATE`: `CK_P7_RECOVERY_GREEN`

## Mechanical evidence

Commands:

```text
python3 p7-recovery/make_fixtures.py
python3 -m py_compile p7-recovery/*.py
(cd p7-recovery && PYTHONWARNINGS=error python3 -m unittest -v)
python3 p7-recovery/run_integration.py
```

Results:

- 20 canonical fixtures regenerated deterministically.
- Python compilation passed.
- Unit tests: 29/29 PASS in 0.012 seconds.
- CockroachDB integration: two independent fresh roots PASS with identical
  verdict semantics.
- Both trials observed an empty active workspace after declared loss.
- Both selected `cand-p7-alpha`, reconstructed only `docs/notes.md` and
  `src/feature.py`, and verified their actual bytes in a fresh child process.
- Both left the primary and interrupted warrants `CONSUMED`; replay returned
  no update; the interrupted warrant produced zero recovery rows.
- Both retained `data/state.json` as `NO_PROVEN_REPRESENTATION`.
- Both recorded table counts `1 1 2 2 1 1 1` and then dropped the disposable
  database and removed the generated root.

Canonical integration output:

```json
[{"active_files_after_loss":[],"consume_interrupt":true,"consume_main":true,"counts":"1\t1\t2\t2\t1\t1\t1","fresh_context":{"ok":true,"reason":"FRESH_CONTEXT_PASS"},"interrupt_recoveries":"0","interrupt_state":"CONSUMED","label":"p7-trial-a","main_state":"CONSUMED","replay_interrupt_empty":true,"replay_main_empty":true,"selected_candidate":"cand-p7-alpha","successor_files":["docs/notes.md","src/feature.py"],"unrecovered":[{"path":"data/state.json","reason":"NO_PROVEN_REPRESENTATION"}]},{"active_files_after_loss":[],"consume_interrupt":true,"consume_main":true,"counts":"1\t1\t2\t2\t1\t1\t1","fresh_context":{"ok":true,"reason":"FRESH_CONTEXT_PASS"},"interrupt_recoveries":"0","interrupt_state":"CONSUMED","label":"p7-trial-b","main_state":"CONSUMED","replay_interrupt_empty":true,"replay_main_empty":true,"selected_candidate":"cand-p7-alpha","successor_files":["docs/notes.md","src/feature.py"],"unrecovered":[{"path":"data/state.json","reason":"NO_PROVEN_REPRESENTATION"}]}]
```

## Runtime

- CockroachDB version: `v26.2.3`, Darwin arm64.
- CockroachDB binary SHA-256:
  `9e6448bfb19c5811ea565020fc84bf7e1ed8fc0c8236ab8512a48e141018aa5c`.
- Runtime is the already-vendored, checksum-verified P2 binary. P7 performed no
  package installation and used no cloud service or credential.

## Safety and residue

- `gitleaks detect --no-git --source p7-recovery`: exit 0, no leaks found.
- `detect-secrets scan p7-recovery --all-files`: exit 0. Its findings are the
  intentional synthetic SHA-256 fields in canonical fixtures; no credential
  detector produced a verified secret.
- Private-path/content `rg` scan: empty.
- Generated `p7-trial-*` roots after both trials: none.
- Symlinks under `p7-recovery`: none.
- `git diff --check`: clean.
- No HOME, live memory, Qdrant, StateV2, launchd, RunPod, AWS, production data,
  client data, public repository, or later-phase surface was accessed.

## Source hash ledger

```text
13091a711cdafaf4cff3c5a803b992ed81e89c44cf03969384c89c5e03c75573  p7-recovery/fresh_context.py
933592eea49b59679bf2805d5352af6ef071ed7a967311a8531fba1ade69a3b3  p7-recovery/make_fixtures.py
97971f48852e94ada7ecabb7dd0390442b4bde11f38fbdb069b10d396355fd34  p7-recovery/records.py
de6d5d5e80c54714bf990b602345cc21884daaec75fba29b54ff1aa10634503e  p7-recovery/run_integration.py
2833522ee337b0a5c9be9dcc6c0285daf744c4334cdec09aaa112c6a6d2c27a2  p7-recovery/test_records.py
2c70db1248f41344c293a5055f0cedfe33979da341a76dfb6575ddb42a842c52  p7-recovery/migrations/001_recovery.sql
```

The 20 fixture hashes are included in the exact judge packet. The packet also
embeds the complete contract, contribution ledger, source, migration, tests,
fixtures, and raw result summary. No claim is made that unavailable bytes were
recovered or that this is filesystem undelete.
