# Gate 7 Run 5 Track-Gate Linkage Amendment Packet R2

## Review authority

This is a same-hash, non-authoring review packet for independent GLM 5.2 and
AGY. The judges have no shell, write, browser, credential, deployment, or
implementation authority. They must decide whether the proposed mechanical
evidence-link repair preserves the frozen benchmark contract or constitutes
impermissible post-reveal tuning.

Return a verdict using the active judge lane's canonical validated output
schema. The caller supplies the exact packet SHA-256 outside this packet. Any
non-GREEN verdict, hash mismatch, identity mismatch, recusal, or refusal to
authorize Track 2 after only the exact patch keeps Track 2 blocked.

R1 received a substantive GLM 5.2 GREEN, but its AGY transport was invalid
because R1 embedded a JSON output schema that conflicted with AGY's pinned
verdict validator. R2 changes only this review-output instruction. The entire
technical packet, artifact bindings, proposed patch, and invariants below are
byte-identical to R1. R1's GLM verdict is stale for R2; both lanes must rerun.

## Frozen state

- Product candidate: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- Orchestration checkpoint: `602da9bff5f894e412df44642ce79579695b2939`
- Run 5 preflight packet SHA-256:
  `2b1af0712b00b373ae62b53365abc7268399bffc56f7196ba3c71801859cbe02`
- Run 5 preflight judges: GLM 5.2 GREEN and AGY Gemini 3.1 Pro High GREEN,
  same packet hash, recusal clear.
- Hidden seed: created once after `CAMPAIGN_READY`.
- Track 1: 84/84 PASS, zero safety failures, evidence sealed mode `0000`.
- Track 3: terminal GREEN, exact counts `[2000,20000,4000,20000]`, 200
  task-bound vector queries, 107 cleanup batches, residue `[0,0,0,0]`.
- Track 2: not started.
- Product code, hidden inputs, measured observations, thresholds, result
  records, cleanup records, and terminal records are immutable.
- No measured rerun or replacement worker is authorized.

## Exact artifact bindings

| Artifact | SHA-256 |
|---|---|
| Frozen start-gate source `hardening-gate7/run4_track_gate.py` | `5c8abdf600475826317d1fecfeef66dcaa8a423f99e1bcdb9d7522bef3e072c7` |
| Frozen Track 3 producer `hardening-gate7/live_bulk_controller.py` | `1007c219258f3bcbe9ca13e01e21c1e84da5f08646bb7294cb1ed9f7fcc89067` |
| Track 1 aggregate | `bacf97c3a9ba97e5a0a157e102e5b41ec1f2ee4ce64dbcfa83309c3c0e6aeec2` |
| Track 1 custody receipt | `204fcb8e436b9c48459a78a6dcc9da2b93f7db3c6cb45d3714184caf2a2656b5` |
| Track 3 terminal | `562db399ecee80ccac107fbd59d6b9ad1841909f44a2978eb920b5fbd483673b` |
| Track 3 result | `6fcd033316b0529dcd85fbcd2158031831beb2e2cbd2afcf25c1b96ff52ed7f9` |
| Track 3 cleanup | `04942c1ee19513fbdeb208811fea1f86ccf9efef7282ab080defdb75aa2a5343` |

All five canonical JSON receipts pass their embedded receipt-hash checks.

## Observed failure

The frozen start-gate exited `1` before creating a Track 2 authorization
marker:

```text
TrackGateError: TRACK3_CLEANUP_LINK_INVALID
```

Relevant canonical fields:

```json
{
  "terminal": {
    "status": "GREEN",
    "result_sha256": "6476d3d2cfd11312616be4754bee365106b4bb0a5d48447395e1f42356d2e19f",
    "receipt_sha256": "4f794bb1f7cb3389fcdaeae2ea5ae658feee92f5c0a143b82d72b889615884cc",
    "cleanup_receipt_sha256_field_present": false
  },
  "result": {
    "green": true,
    "result_sha256": "6476d3d2cfd11312616be4754bee365106b4bb0a5d48447395e1f42356d2e19f",
    "cleanup_receipt_sha256": "4289ab806ec23a360bc1fb28e5269c092de5c33c6d2aa3dbbcf6229e7c3d58a7",
    "actual_counts": [2000, 20000, 4000, 20000],
    "query_count": 200,
    "insert_total_ms": 208055,
    "residue_counts": [0, 0, 0, 0]
  },
  "cleanup": {
    "status": "PASS",
    "receipt_sha256": "4289ab806ec23a360bc1fb28e5269c092de5c33c6d2aa3dbbcf6229e7c3d58a7",
    "cleanup_batches": 107,
    "cleanup_retries": 0,
    "residue_counts": [0, 0, 0, 0]
  }
}
```

The terminal therefore binds the result exactly, and the result binds the
cleanup exactly. The producer never emits a direct terminal cleanup field on
its successful path. Its failure path does emit that field. The frozen gate
incorrectly requires the failure-path shape on successful evidence.

## Existing failing logic

```python
if terminal.get("result_sha256") != result["result_sha256"]:
    raise TrackGateError("TRACK3_RESULT_LINK_INVALID")
if terminal.get("cleanup_receipt_sha256") != cleanup["receipt_sha256"]:
    raise TrackGateError("TRACK3_CLEANUP_LINK_INVALID")
```

## Proposed exact amendment

Apply only this patch to the evidence gate:

```diff
 if terminal.get("result_sha256") != result["result_sha256"]:
     raise TrackGateError("TRACK3_RESULT_LINK_INVALID")
-if terminal.get("cleanup_receipt_sha256") != cleanup["receipt_sha256"]:
+if result.get("cleanup_receipt_sha256") != cleanup["receipt_sha256"]:
     raise TrackGateError("TRACK3_CLEANUP_LINK_INVALID")
+if not (
+    terminal.get("campaign_id") == result.get("campaign_id")
+    == cleanup.get("campaign_id")
+):
+    raise TrackGateError("TRACK3_CAMPAIGN_LINK_INVALID")
```

No other file or line may change. The repaired gate must be rerun over the
same five file hashes above. It must produce a new versioned start-gate marker
that additionally records:

- the original gate source hash;
- this amendment packet hash;
- all five immutable evidence file hashes;
- `linkage_mode=TERMINAL_TO_RESULT_TO_CLEANUP`;
- `measured_artifacts_modified=false`;
- `post_reveal_threshold_or_outcome_change=false`.

## Non-negotiable invariants

The amendment does not:

- change product code or behavior;
- change hidden inputs, oracle data, observations, scores, thresholds, counts,
  timing limits, or cleanup requirements;
- mutate or relabel any measured artifact;
- authorize a measured rerun or replacement worker;
- infer GREEN from the terminal label alone;
- remove any canonical receipt-hash validation;
- remove the zero-residue, count, Track 1 custody, or campaign linkage gates;
- start Track 2 before the exact repaired gate emits its bound marker.

The only question is whether verifying the producer's actual canonical chain
`terminal -> result -> cleanup` is an evidence-plumbing correction rather than
post-reveal outcome tuning. If it is not, return `NOT_GREEN` and Track 2 must
remain blocked.
