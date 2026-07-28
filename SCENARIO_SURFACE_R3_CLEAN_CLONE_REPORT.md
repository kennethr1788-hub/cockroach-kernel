# Scenario Surface R3 Clean-Clone Report

- `STATUS`: `R3_CLEAN_CLONE_GREEN`
- `UTC_CREATED`: `2026-07-28T06:38:21Z`
- `CANDIDATE_COMMIT`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `TRIALS`: `2 independent local --no-local Git clones`
- `PYTHON`: `3.12.13`
- `INSTALL_COMMAND`: `python -m pip install --no-deps <clean-clone>`
- `PUBLIC_ENTRYPOINT`: `cockroach-kernel`
- `VALID_SCENARIOS`: `4/4 exit 0`
- `FRESH_CONTEXT`: `4/4 true`
- `REPLAY_CONTROLS`: `2/2 exit 1; WARRANT_REPLAY`
- `DISTINCT_INPUT_BINDING`: `2/2 request and summary hashes differ`
- `REPRESENTATION_ROOT_UNCHANGED`: `4/4 true`
- `NETWORK_USED`: `false`
- `CREDENTIALS_USED`: `false`
- `SCENARIO_TEARDOWN`: `2/2 true`
- `CLONE_ROOT_TEARDOWN`: `2/2 true`
- `HIDDEN_SEED_CREATED`: `NO`
- `HIDDEN_EXECUTIONS`: `0`

Each clone installed the exact candidate without source edits, captured
top-level and `recover` help, ran two distinct typed scenarios through the
installed console script, confirmed different request bytes produced different
deterministic summary hashes, confirmed the representation roots remained
unchanged, and refused a fresh-process replay. Both scenario roots and both
clean-clone roots were removed by bounded temporary-directory teardown.

The fixture controller prepared synthetic typed records. Product execution used
only the installed `cockroach-kernel` entrypoint. No private credentials,
hosted service, Docker, RunPod, paid account, source edit, or hidden state was
required.
