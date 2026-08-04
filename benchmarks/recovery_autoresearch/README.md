# Recovery evaluation harness

This is an offline, fixed-budget evidence harness inspired by Karpathy’s
autoresearch protocol. It is deliberately separate from the product runtime.

- `manifest.json` freezes the evaluator, metrics, immutable files, and budget.
- `run.py` executes the evaluator, appends hash-bound JSONL results, and marks
  each run `keep`, `discard`, or `crash`.
- The evaluator and recovery authority are read-only; only the declared
  scenario/config scope may evolve in a future campaign.
- No model, network, cloud credential, database connection, or product
  mutation is allowed.
- A timeout is a crash and immutable evaluator changes abort the campaign.

Example:

```bash
python3 benchmarks/recovery_autoresearch/run.py \
  --output /tmp/ck-recovery-results.jsonl \
  --iterations 1 --budget-seconds 300
```

The result records platform, Python version, commit, manifest hash, metric
tuple, resource/evidence bytes, and output hashes. Hidden scenarios must be
generated only after this manifest is frozen; never tune after reveal.
