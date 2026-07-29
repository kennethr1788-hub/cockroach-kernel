# Gate 7 Run 5 Track-Gate Test-Fixture Packet R1

## Review boundary

This is a same-hash, non-authoring technical review. Track 2 is stopped. The
judges must decide whether the exact test-only patch below is a legitimate
fixture-schema correction or impermissible post-reveal tuning. Judges have no
write, shell, browser, credential, deployment, or implementation authority.

## Parent amendment

- Parent amendment packet SHA-256:
  `8dafbdbce31ce58fe79018be11723a6279f1adb12e0ae411347cc61ec61d2b98`
- Parent review: GLM 5.2 GREEN and AGY Gemini 3.1 Pro High GREEN, same hash,
  recusal clear.
- Reviewed patched gate SHA-256:
  `1498c65b2d9cf3e54e3a8680723594459a6cf7b1566343c4b91f2602d9ce9508`
- Existing test source SHA-256:
  `00f7b79896c9fe3a84fb08ca0d15d08a568d099562b105ba9effd2a8c7e22743`
- Product code, hidden inputs, measured Track 1/Track 3 evidence, thresholds,
  outcomes, and cleanup records remain immutable.

## Direct failure

After applying the exact independently approved gate patch, the full expanded
suite ran 20 tests: 19 passed and one failed before any Track 2 marker existed.
The failing test was:

```text
test_measured_track2_gate_requires_green_sealed_and_zero_residue
TrackGateError: TRACK3_CLEANUP_LINK_INVALID
```

The test fixture constructs a successful producer chain in a shape the actual
frozen producer never emits: it places `cleanup_receipt_sha256` on the terminal
and omits it from the result. The real immutable measured records are the
opposite and were bound in the parent packet:

```text
terminal.result_sha256 -> result.result_sha256
result.cleanup_receipt_sha256 -> cleanup.receipt_sha256
```

The cleanup-residue negative branch repeats the same stale fixture shape by
rebinding the changed cleanup receipt on the terminal rather than the result.

## Proposed exact test-only patch

```diff
 result_record = hashed({
     "version": "unit-result",
     "campaign_id": campaign_id + "-track3",
     "green": True,
     "actual_counts": [2000, 20000, 4000, 20000],
+    "cleanup_receipt_sha256": cleanup_record["receipt_sha256"],
 }, "result_sha256")
 terminal_record = hashed({
     "version": "unit-terminal",
     "campaign_id": campaign_id + "-track3",
     "status": "GREEN",
     "result_sha256": result_record["result_sha256"],
-    "cleanup_receipt_sha256": cleanup_record["receipt_sha256"],
 }, "receipt_sha256")
@@
 changed_cleanup = hashed(body, "receipt_sha256")
 case_records["cleanup.json"] = changed_cleanup
-terminal_body = {key: value for key, value in terminal_record.items()
-                 if key != "receipt_sha256"}
-terminal_body["cleanup_receipt_sha256"] = changed_cleanup["receipt_sha256"]
-case_records["terminal.json"] = hashed(terminal_body, "receipt_sha256")
+result_body = {key: value for key, value in result_record.items()
+               if key != "result_sha256"}
+result_body["cleanup_receipt_sha256"] = changed_cleanup["receipt_sha256"]
+case_records["result.json"] = hashed(result_body, "result_sha256")
```

No production, benchmark, generator, scoring, threshold, or evidence-gate file
may change. After the exact patch, all 20 expanded tests and the repaired gate
over the same five immutable measured file hashes must pass. A separate bound
marker must still record the parent amendment packet hash, original gate hash,
all five evidence hashes, transitive linkage mode, and both negative
post-reveal attestations.

The review question is whether updating this one synthetic unit fixture to the
already-frozen producer's canonical success schema preserves test strength and
benchmark fairness.
