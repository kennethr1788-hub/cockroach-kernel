# Hardening Gate 3 Trace Preflight R1

- `STATUS`: `TRACE_ARMED_HUMAN_EDIT_REQUIRED`
- `CAMPAIGN_ID`: `CK-G3-20260727T192406Z`
- `LAST_GREEN_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `TARGET_GATE`: `HARDENING_3_REAL_WORKFLOW_GREEN`
- `TASK_CONTRACT`: `HARDENING_GATE3_TASK_CONTRACT_R1.md`
- `TASK_CONTRACT_SHA256`: `3a9a2b7f1dc305ff0099e51e5716c2dc0ac523190ea9ecc83196382b8dfea290`
- `SOURCE_COMMIT`: `ba1217c4d830a3c7633e352c0e10712d6b817cee`
- `WORKSPACE_RELATIVE_PATH`: `.hardening-runtime/gate3-real-workflow/workspace`
- `WORKSPACE_INITIAL_BRANCH`: `main`
- `WORKSPACE_INITIAL_STATUS`: clean
- `WORKSPACE_NETWORK_REMOTE`: none
- `TRACE_ARMED_UTC`: `2026-07-27T19:24:06Z`

## Declared workflow

The disposable workspace is a local no-hardlink clone of the clean source
commit. Its network remote was removed before any task work. The custody root
stays outside the disposable workspace. Only project source, synthetic inputs,
canonical receipts, and sanitized command metadata may enter the trace.

The declared human-edit file is:

`.hardening-runtime/gate3-real-workflow/workspace/GATE3_HUMAN_ACCEPTANCE.txt`

Its model-created placeholder is not human evidence. Kenneth must personally
add one sentence after `KENNETH_ACCEPTANCE:` and save it. Codex may display the
file through Chrome/CUA but may not type, paste, dictate, or save that sentence.

## Allowed actions before the human edit

- inspect the disposable clone and the declared file;
- display the declared file for Kenneth;
- record read-only hashes and UI state;
- update the canonical blocker and resume artifacts;
- commit and push the preflight contract and blocker receipts.

## Forbidden actions before the human edit

- implementation or tests representing task progress;
- AWS or CockroachDB trajectory mutation;
- declared loss or deletion of the disposable workspace;
- fresh-context continuation, promotion, or refusal;
- automation of Kenneth's required edit;
- credentials, private/client data, HOME state, unrelated repositories, public
  actions, release, submission, RunPod, or additional cloud spend.

## Resume condition

Resume only after both direct file-state evidence and Kenneth's explicit
confirmation establish that he personally made and saved the independent edit.
Then freeze its SHA-256 before any agent implementation begins.
