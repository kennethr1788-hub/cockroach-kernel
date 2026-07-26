# P9 Offline Architecture Packet R1

## Identity and boundary

- STATUS_CLAIMED: `P9_OFFLINE_RUNWAY_CANDIDATE`
- LIVE_P9_STATUS: `BLOCKED`
- LIVE_BLOCKER: `AWS_ACCOUNT_SETUP_HUMAN_GATE`
- LAST_GREEN_GATE: `CK_P8_GOLDEN_GREEN`
- IMPLEMENTATION_COMMIT: `c8cc768ecec3d6faea7cf2fc3b485e276e445e86`
- PLAN_SHA256: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- AUTHORIZATION_SHA256: `cb46e382f98d9a4d52a882a3d35f1b0ae4db9047e07f713d2212196dc3204214`
- AWS_INCREMENTAL_COST: `$0.00`
- RUNPOD_ATTEMPTS: `0`

This packet requests a non-final independent architecture verdict only. It may
authorize no cloud mutation and cannot produce `CK_P9_INTEGRATION_GREEN`.

## Implemented offline surface

- strict 16 KiB canonical Lambda request/response records;
- pure standard-library advisory evaluator with no network/process/environment/
  credential/model/random/time access;
- deterministic 64-dimensional bounded token-feature projection, explicitly
  not described as a neural embedding;
- local Lambda timeout/throttle/malformed/duplicate/stale mocks;
- exact read-only MCP query allowlist and adversarial refusal classes;
- bounded SQLSTATE 40001 retry, idempotency conflict, invocation cap, and byte
  accounting;
- deterministic changefeed projection, restart cursor, lag/hash/conflict, and
  no-write-back model;
- CockroachDB v26.2 schema, VECTOR(64) index, exact runtime grants, and read-only
  MCP view;
- Lambda resource, trust, execution-role, cost, retention, and MCP templates;
- keyless end-to-end mock/replay using the existing P4 verifier as sole local
  verdict authority and a hash-bound fresh-context capsule.

## Mechanical evidence

- Python 3.12.13: 95 tests GREEN; replay GREEN.
- System Python 3.9.6 compatibility: 95 tests GREEN; replay GREEN.
- Two clean clones: 95 tests each; byte-identical replay SHA-256
  `a6a331944a7950ee04e4ef51e867d62053bb9ba4cae9270af080ac49f34926bd`.
- Local CockroachDB v26.2.3: seven `ck` tables/views and one vector index created.
- Runtime role trial: SELECT on MCP view passed; CREATE and UPDATE denied.
- P9 source: gitleaks and detect-secrets clean; no private absolute path,
  symlink, special file, process, listener, or generated-root residue.

Evidence receipts:

- `P9_OFFLINE_SQL_TRIAL_RECEIPT_R1.md`
- `P9_OFFLINE_REPLAY_RECEIPT_R1.md`
- `P9_CLEAN_CLONE_RECEIPT_R1.md`
- `P9_IAM_AMENDMENT_JUDGE_RECEIPT_R1.md`
- `P9_KIMI_REQUALIFICATION_JUDGE_RECEIPT_R1.md`
- `P9_DEVSTRAL_OUTPUT_R1.md`
- `P9_VIBE_ATTEMPT_RECEIPT_R1.md`

## Builder disposition

- Kimi K3 supplied the primary records/evaluator/vector foundation and partial
  mocks/migration/tests in two bounded attempts. Both attempts timed out; Codex
  reviewed, corrected, completed, and mechanically verified the result.
- Devstral returned a typed advisory design. Its Secrets Manager suggestion was
  rejected because it violated the no-network evaluator contract.
- Vibe made no repository change after two token-limit failures. No third retry
  or budget escalation was used. Codex owns the reliability layer.
- Codex owns integration, corrections, tests, SQL/IAM artifacts, and replay.

## IAM amendment

Independent GLM approved one narrow AWS-required exception: `log-stream:*`
only under the exact `/aws/lambda/ck-p9-evaluator` log group in `us-west-2` and
the live account. Wildcard actions, global resources, and every broader
wildcard remain forbidden. Live substitution and IAM simulation remain gates.

## Live-only blockers and required proofs

1. Kenneth completes AWS account setup; Lambda Functions opens in `us-west-2`.
2. Re-read account/region identity without recording sensitive account data.
3. Substitute the live account ID locally without committing it.
4. Simulate/read back IAM; prove no permission beyond exact log streams.
5. Recheck Lambda quotas, current prices, free-access path, and `$5` bound.
6. Deploy and read back exact Lambda memory/timeout/concurrency/URL/log retention.
7. Apply schema/grants to the declared live CockroachDB cluster using hidden
   human credential entry; never expose or retain credential bytes.
8. Prove real transaction, VECTOR(64) retrieval, sinkless changefeed, and
   cleanup/restart behavior.
9. Prove Managed MCP OAuth is read-only, single-cluster, one-view scoped, and
   visibly auditable. If its authorization cannot prove that scope, do not count it.
10. Run the live vertical slice and failure branch, freeze the final P9 packet,
    and obtain required GLM plus AGY GREEN on the same hash.

## Verdict request

Return `GREEN` only if this offline architecture is coherent, fail-closed,
least-privilege, deterministic, locally runnable, and correctly preserves all
live-only claims as blocked. Return `NOT_GREEN` for any offline defect. A GREEN
is named `P9_OFFLINE_ARCHITECTURE_GREEN`, never P9 integration GREEN.
