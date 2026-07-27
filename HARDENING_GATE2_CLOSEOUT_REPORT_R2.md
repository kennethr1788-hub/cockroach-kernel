# Hardening Gate 2 Closeout Report R2

- `TECHNICAL_STATUS`: `GREEN`
- `GATE_STATUS`: `PENDING_FINAL_INDEPENDENT_GLM`
- `LAST_GREEN_GATE`: `HARDENING_1_CLI_GREEN`
- `PARENT_COMMIT`: `c9f7e20e84a15617f8eb85db43f4bca28aae2511`
- `PUBLIC_ENDPOINT`: `https://6rhijj3d37.execute-api.us-west-2.amazonaws.com`
- `LIVE_RESULT_SHA256`: `41c8a8f0733aa9ca9885ad4e3bdb5ae185a859f912d6ab4bd4ebfbae6e69e948`
- `LIVE_MANIFEST_SHA256`: `56dceaf6b54f9b9dfc4713ff510350b9f82a47f04b0ff86d12061c02146a5522`
- `CLOSEOUT_MANIFEST_HASH`: `d930fdc1b7b86363bca7ef95f181240be4ee20bf78c7046331f8e91487f807dd`
- `SECRET_VALUE_READ`: `false`
- `UTC_REPORTED`: `2026-07-27T18:51:00Z`

## Live behavior

The append-only revision-2 proof returned `LIVE_BEHAVIOR_GREEN`.

- public promote: HTTP 200, `PROMOTE`, `VERIFIED`, action
  `VERIFIED_CONTINUATION_AVAILABLE`;
- public refusal: HTTP 200, `REFUSE`, `HASH_MISMATCH`, action `NONE`;
- final authority: `P4_DETERMINISTIC_VERIFIER`;
- cloud/model status: `ADVISORY`;
- five identical direct promote results;
- five identical direct refusal results;
- direct and public method/body/query/route negatives passed;
- live and keyless replay verdict/reason pairs matched;
- judges need no AWS, CockroachDB, or paid-account credential.

The first live attempt remains immutable evidence of a fail-closed 503 when the
synthetic rows were absent. No false promotion occurred.

## CockroachDB proof

- Real persistent layer: CockroachDB `cockroach_kernel`.
- Primary region: `aws-us-west-2`.
- Zones: `aws-us-west-2a`, `aws-us-west-2b`, `aws-us-west-2c`, and
  `aws-us-west-2d`.
- Table locality: `REGIONAL BY TABLE IN PRIMARY REGION`.
- Required operations: transactional receipt linkage and VECTOR(64) distance
  retrieval.
- Vector index exists: `context_vectors_vector_idx` using `vector_l2_ops`.
- For the two-row frozen demo, the optimizer selected the exact
  task/event/namespace index before top-k rather than the global vector index.
- The linkage plan also records optimizer recommendations for a scaled dataset;
  these are an honest scaling limitation, not needed for the bounded two-row
  judge demo.
- SQL identity boundary: schema `USAGE` plus `SELECT` on only `tasks`,
  `receipts`, `context_vectors`, and `worker_results`; no write privilege.
- Existing S1 evidence proves SQLSTATE 40001 handling, duplicate idempotency,
  restart recovery, determinism, quarantine exclusion, and rollback across all
  61 checkpoints.
- Existing P9 MCP evidence is hash-bound in the closeout cross-phase receipt.

## AWS proof

- HTTP API exposes only anonymous `GET /demo/promote` and
  `GET /demo/refuse`.
- Lambda: Python 3.12, 256 MiB, eight-second timeout, one environment key name,
  no stored environment credential value.
- IAM actions: exact log-stream writes plus exact project-secret read only.
- Stage throttle: 0.05 requests/second, burst 2.
- Log retention: one day.
- Alarms: Lambda error threshold 1/minute and invocation threshold 5,000/day;
  both enabled and `OK` at closeout.
- Observed metrics: 19 invocations, zero Lambda errors, zero Lambda throttles.
- CloudWatch logs contain 19 matching START/END/REPORT request triplets.
- The secret was read only by the deployed Lambda; Codex recorded metadata and
  never called `GetSecretValue` or exposed the value.

## Cost, access, and residual risk

The no-free-tier projection through `2026-09-15T21:00:00Z` is
`$10.055554584967524`, below the authorized `$12.00` ceiling. It assumes the
full eight-second Lambda timeout at every stage-accepted request, a cold secret
lookup on every invocation, two alarms, conservative log and transfer sizes,
and current published AWS rates.

Stage throttling is best-effort and does not create a provider-enforced total
spend cap for arbitrary anonymous ingress. This denial-of-wallet residual was
explicitly accepted before deployment. The manual kill line is to delete API
`6rhijj3d37` first, then delete the Lambda, alarms, log group, inline role
policy/role, revoke the five SQL grants, remove the SQL identity, and finally
delete the project secret after access is no longer required. Every deletion
must be followed by exact absence readback. No teardown is executed now because
the authorization requires judge access through the stated end time.

## Validation

- `python3 -m py_compile hardening-gate2/live_test.py hardening-gate2/collect_closeout.py`: PASS;
- `python3 -m unittest cockroach_kernel.test_http_api cockroach_kernel.test_cli`: 12/12 PASS;
- `gitleaks` on both new evidence trees: zero findings;
- `detect-secrets` on the new scripts and evidence: zero findings;
- private-path/account-id text scan: zero findings;
- CUA session `ck-gate2-diagnosis` ended with `active: false`;
- secret value read: false.

## Evidence

- live evidence: `evidence/hardening-gate2-live-r2/`;
- closeout evidence: `evidence/hardening-gate2-closeout-r1/`;
- synthetic reseed receipt: `HARDENING_GATE2_RESEED_RECEIPT_R2.md`;
- preserved failed attempt: `HARDENING_GATE2_LIVE_ATTEMPT_R1.md`;
- deployment receipt: `HARDENING_GATE2_AWS_DEPLOYMENT_RECEIPT_R1.md`.

No Gate 2 GREEN claim is made until one independent GLM returns GREEN over the
exact frozen final packet hash.
