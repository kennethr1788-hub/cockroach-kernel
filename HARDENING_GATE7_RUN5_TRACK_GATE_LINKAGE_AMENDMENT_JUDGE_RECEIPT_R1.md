# Gate 7 Run 5 Track-Gate Linkage Amendment Judge Receipt R1

- `STATUS`: `GREEN`
- `UTC_RECORDED`: `2026-07-29T22:48:00Z`
- `PACKET`: `HARDENING_GATE7_RUN5_TRACK_GATE_LINKAGE_AMENDMENT_PACKET_R3.md`
- `PACKET_SHA256`: `8dafbdbce31ce58fe79018be11723a6279f1adb12e0ae411347cc61ec61d2b98`
- `GLM_MODEL`: `GLM 5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_PACKET_HASH_MATCH`: `YES`
- `GLM_RECUSAL_CLEAR`: `YES`
- `GLM_TRACK2_AUTHORIZED_AFTER_EXACT_PATCH`: `YES`
- `GLM_RAW_SHA256`: `0d32dc093439476c8a62678965244d3f5c9183db5bdbb936f7f50ef355b6b7d6`
- `GLM_SERVED_MODEL_EVIDENCE`: `glm-zai: served by glm-5.2`
- `AGY_MODEL`: `Gemini 3.1 Pro (High)`
- `AGY_VERDICT`: `GREEN`
- `AGY_PACKET_HASH_MATCH`: `YES`
- `AGY_RECUSAL_CLEAR`: `YES`
- `AGY_BLOCKERS`: `NONE`
- `AGY_EVIDENCE_GAPS`: `NONE`
- `AGY_REQUIRED_RERUNS`: `NONE`
- `AGY_RAW_SHA256`: `768ff174ad4653db252a2ce16059609df5a7ad401b7fea333d5cf656bb260f4f`
- `AGY_PROVIDER_BINDING_STDERR_SHA256`: `bf32ab8c082fa1aff618ee172c412b767bf7f636479cf49543749f2ba6ad30ee`

R1 and R2 AGY calls were transport-invalid and produced no accepted verdict.
The first two R3 GLM calls were also invalid for the frozen schema (`PASS`
instead of `GREEN`, then a generic identity label). They do not count. The
final R3 GLM output and the R3 AGY output above are the only accepted results.

Both independent non-authoring lanes reviewed the same R3 packet hash. They
classified the exact change as an evidence-plumbing repair that preserves the
canonical `terminal -> result -> cleanup` chain, does not alter measured
artifacts or thresholds, and strengthens campaign linkage. Track 2 is
authorized only after the exact reviewed patch is applied and a new marker
binds the immutable evidence hashes and negative post-reveal attestations.
