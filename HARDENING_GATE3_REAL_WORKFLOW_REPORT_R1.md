# Hardening Gate 3 Real Workflow Report R1

- `STATUS`: `AWAITING_INDEPENDENT_GLM_REVIEW`
- `CAMPAIGN_ID`: `CK-G3-20260727T192406Z`
- `TASK_ID`: `ck-g3-real-workflow-r1`
- `LAST_GREEN_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `TARGET_GATE`: `HARDENING_3_REAL_WORKFLOW_GREEN`
- `EVIDENCE_CLASS`: `SINGLE_OPERATOR_REAL_WORKFLOW_EVIDENCE`
- `BASE_COMMIT`: `ba1217c4d830a3c7633e352c0e10712d6b817cee`
- `DISPOSABLE_AGENT_COMMIT`: `f8b2e5d7e15352bf2762bd000875a85a0b56a75b`
- `PRELOSS_CHECKPOINT_COMMIT`: `8a2e151615d9d1a327de5439dd19561e51fd6be0`
- `CAPTURE_RECEIPT_SHA256`: `c4ae85a6ef201d98f2079b077f0d86784c905cb93539128d2bee371b8d326ee0`
- `LOSS_RECEIPT_SHA256`: `0d1b614458234496784c31f91cfe0474887fb4a0f5b4eca226fab5444999e9ba`
- `CONTINUATION_RECEIPT_SHA256`: `cb2bcc1df56f6a88276b2a685fc9f3bc5e30816bb54d151091364d384d06a050`
- `RESIDUE_RECEIPT_SHA256`: `03be225cf64c4a741e683b3f725725be97372c22e1740b58f6901ee254162249`
- `EVIDENCE_MANIFEST_RECORD_HASH`: `bdb98a84fc39da166c2bd071249f5491b60be6763b9a8d56b7104368ec2b487e`
- `EVIDENCE_MANIFEST_FILE_SHA256`: `0c4596c5e4cc42eed4838d110b25f0b9c3e6933e1bf4c427f4e87192590f7d75`

## Ten-step trace

1. Kenneth's concrete task was frozen: refuse repeated CLI demo receipt-set
   writes without changing the existing bytes or leaving partial residue.
2. Codex produced useful committed progress in `cockroach_kernel/cli.py` and a
   useful uncommitted edge-case test in `cockroach_kernel/test_cli.py`.
3. The product recorded the declared trajectory through one real AWS Lambda
   advisory invocation and one CockroachDB transaction containing a task,
   event, immutable receipt, vector, worker result, and projection.
4. Kenneth independently typed and saved the declared human edit. Its bytes
   are not copied into the public report; SHA-256 binds them.
5. The exact disposable workspace was deleted after all three work objects
   were rehashed against content-addressed custody outside it.
6. A fresh OS process ran with an empty temporary HOME and no conversation
   input. It received only the custody root, the exact local base repository,
   and the successor target.
7. Five P4 verdicts returned `PROMOTE / VERIFIED`; the P7 selector returned
   `PROMOTE / MAX_PROVEN_PREFIX`; the one-use warrant was consumed before
   successor materialization.
8. The fresh process reconstructed and continued without Kenneth restating
   the task. Committed agent, uncommitted agent, and human units were retained.
9. Fourteen tests passed. A first demo run exited `0`; the second run against
   the same output root exited `2` with `OUTPUT_ALREADY_EXISTS`; both original
   receipt hashes were unchanged; dot-file residue was empty; a fresh output
   root exited `0`.
10. Promotion, unrecovered-work, replay, loss, continuation, and residue
    receipts were preserved. Replay exited `2` with `WARRANT_REPLAY` before a
    successor was created. The original and both successor roots, plus the
    temporary HOME, are absent; custody remains.

## Measured result

- Declared work units: `3`
- Provable work units: `3`
- Retained work units: `3`
- Lost work units: `0` file-content units
- Committed agent unit retained: `yes`
- Uncommitted agent unit retained: `yes`
- Independent human unit retained: `yes`
- Task restatement required: `no`
- Loss-to-verified-continuation wall clock: `23,981 ms`
- Executable checks passed: `14/14`
- Second-run overwrite refusal: exit `2`, reason `OUTPUT_ALREADY_EXISTS`
- Original receipt mutation: `none`
- Temporary write residue: `none`
- Replay mutation: `none`
- Unrecovered ledger items: `0`
- Live Cockroach readback counts for task/event/receipt/vector/result/projection:
  `1/1/1/1/1/1`
- Live count output SHA-256:
  `6e9bbe0b10cb5a5674c0cdd32a4b2da4eae7be296c25aa488eb475ed7ad1f246`

## Cloud and authority boundary

AWS Lambda emitted advisory observations only. The response was validated and
hash-bound to the request before the CockroachDB transaction. CockroachDB is
the persistent live trajectory/evidence ledger. Local P4/P7 deterministic
logic alone selected the candidate and authorized reconstruction. No cloud or
model output decided pass/fail or performed deletion.

The live Gate 3 rows are intentionally retained as immutable evidence. The
least-privilege runtime identity has `SELECT` and `INSERT` but no `DELETE` on
the relevant tables; retained evidence is therefore declared state, not
temporary residue.

## Honest limitations and failed attempts

- The disposable Git branch and local commit object were not reconstructed.
  The changed file bytes represented by that commit were retained exactly.
- The orchestrating Codex conversation remained active. What was destroyed was
  the disposable workspace and its local Git session. The continuation proof
  is a fresh OS process with no conversation input; it is not proof that this
  orchestration conversation was terminated.
- The first fresh-process launch never started because its sanitized `PATH`
  omitted the project Python location. The warrant remained `ISSUED` and no
  successor existed. The corrected launch changed only `PATH` and succeeded.
- The first cleanup receipt attempt deleted the verified successor and then
  stopped because macOS resolves `/tmp` through `/private/tmp`. Custody was
  intact. The cleanup was made idempotent, the exact empty temporary HOME was
  removed, and the final residue receipt passed.
- This is one single-operator trace, not public-user research or proof of
  population-wide usability.

## Gate boundary

This report does not self-approve Gate 3. `HARDENING_3_REAL_WORKFLOW_GREEN`
may be recorded only if an independent GLM judge returns GREEN over the exact
frozen packet hash and its verdict is preserved unchanged.

