# Hardening Gate 6 — Execution Plan R3

- `TARGET_GATE`: `HARDENING_6_RUN1_GREEN`
- `EXECUTION_REVISION`: `R3`
- `PARENT_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `CAMPAIGN_ID`: `ck-gate6-20260727-run1-r3`
- `MEASURED_EXECUTIONS`: `54`
- `PAIRED_GROUPS`: `18`
- `RUNPOD_WORKERS`: `one successful measured worker; at most eight sequential pre-payload attempts in this campaign`
- `AGY_REQUIRED`: `false`

## Acceptance and kill line

Close GREEN only if all 54 canonical receipts, all 18 equal-information pairs,
raw aggregation, inherited kernel network denial, candidate and tool hashes,
evidence custody, exact-ID teardown, empty campaign inventory, and same-hash
GLM plus Claude final reviews pass. A favorable product score is not itself an
acceptance condition.

Kill before measurement on candidate, contract, tool, script, filter, canary,
payload, price, or lifecycle drift; unequal paired inputs/budgets; inherited
socket state; unavailable kernel seccomp; or a non-GREEN required preflight
judge. Kill during the campaign on any invalid row or receipt, false promotion,
unsafe acceptance, mutation after loss/refusal, nondeterminism, residue,
checkpoint failure, network-denial failure, or inability to guarantee worker
deletion.

## Frozen comparison

`HARDENING_GATE6_EXECUTION_MANIFEST_R3.json` contains each
`(scenario_class, repetition, method)` tuple exactly once. It preserves the
Gate 5 scenario-index rotation and identical candidate/comparator behavior.
Every row uses a fresh process and trial root. The common candidate harness
emits the receipt; Gate 6 only validates, fsyncs a checkpoint, and aggregates.

## Isolation

The exact R3 amendment and reviewed `seccomp_exec.py` control the boundary.
The capability canary runs before the full payload. Once the payload is
uploaded, creation retries permanently end. The successful worker runs one
non-measured smoke and then the 54-row campaign as unprivileged UID 10001 under
the inherited filter. `run_campaign_r3.py` fails closed unless the kernel and
attestation wall is directly present.

## Evidence

Preserve the canary attestation, remote script hash, tool hash wall, non-measured
smoke, 54 raw receipts, 54-event checkpoint chain, 18 paired reports, aggregate,
raw stdout/stderr, remote and retrieved tree manifests, lifecycle chain,
provider responses, billing bounds, exact-ID absence, inventories, and secret/
private-path scans. Evidence labels must distinguish canary, smoke, and measured
rows. Gate 3 human trace remains separate and is never pooled.

## Required independent judges

Before worker creation and after teardown, GLM 5.2 and Claude Opus 4.8 review
the same exact sanitized packet hash as non-authoring judges. They have no
shell, write, credential, deployment, browser, or implementation authority.
Both must return GREEN with recusal clear. The builder never self-approves.

No model, prompt, untrusted content, memory write, agent dispatch, or external
egress occurs inside the measured workload, so a separate Wall-7/AGY lane is
not required for this offline benchmark.
