# PDH-3 Production-Shaped Scale RunPod Preflight Judge Receipt R7

- `UTC_REVIEWED`: `2026-07-31T04:39:57Z`
- `JUDGE_ROUTE`: `glm-zai`
- `SERVED_MODEL`: `glm-5.2`
- `ROLE`: `independent non-authoring preflight judge`
- `PACKET_SHA256`:
  `f5dd2ee116960f6383facf91228ee0b8b81718d6341607f9f427211cbcc38b0b`
- `PACKET_BYTES`: `105014`
- `BINDINGS_FILE_SHA256`:
  `9f3468aaf7727e2df9c482679138662349f9fe32293c66f1e8c7d7a6a97d23b9`
- `RAW_OUTPUT_SHA256`:
  `193738b3f30b6292676b0160ddf858b962f78e66fba06fb156994d5a5502b0c2`
- `CANONICAL_OUTPUT_SHA256`:
  `19bc8f4ef1584302fa449929a6a0d9983c0883598e9c2f9014ed7ce8b6b76157`
- `VERDICT`: `GREEN`
- `CANDIDATE_IMMUTABILITY`: `GREEN`
- `WORKLOAD_AND_THRESHOLDS`: `GREEN`
- `CREDENTIAL_AND_DATA_BOUNDARY`: `GREEN`
- `LIFECYCLE_AND_COST`: `GREEN`
- `EVIDENCE_AND_TEARDOWN`: `GREEN`
- `BLOCKERS`: `[]`
- `LIMITATIONS`: `["EXPECTED_PAID_EVIDENCE_GAP"]`

The expected gap is the not-yet-run paid campaign. The judge reviewed the
exact R7 packet after the Attempt 04 false-positive evidence and the
destinationless connected-send repair were incorporated. This receipt
authorizes provider creation within the frozen packet; it is not evidence that
the measured campaign has run or passed.
