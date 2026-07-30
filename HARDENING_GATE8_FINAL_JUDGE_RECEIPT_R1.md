# Hardening Gate 8 Final Judge Receipt R1

- `UTC_RECORDED`: `2026-07-30T06:54:00Z`
- `PACKET`: `HARDENING_GATE8_FINAL_PACKET_R2.md`
- `PACKET_SHA256`: `887cc444cb94ec94c2e9ffeed71f8f1113656e8cb799aa190687d592790fe0aa`
- `PACKET_COMMIT`: `667132a5e6f88456604c15eb37daacaffd151923`
- `GLM_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RECUSAL`: `clear`
- `GLM_BLOCKERS`: `none`
- `GLM_EVIDENCE_GAPS`: `none`
- `GLM_REQUIRED_RERUNS`: `none`
- `GLM_RAW_SHA256`: `e77e1ab0b787602aaaa2884cf6b103e623609f9a4d047277ac976e806fb596c0`
- `GLM_STDERR_SHA256`: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`
- `AGY_PROVIDER_PATH`: `Gemini 3.1 Pro (High)`
- `AGY_SERVED_MODEL_METADATA`: `unavailable in CLI 1.1.8; not overstated`
- `AGY_VERDICT`: `GREEN`
- `AGY_RECUSAL`: `clear`
- `AGY_BLOCKERS`: `none`
- `AGY_EVIDENCE_GAPS`: `none`
- `AGY_REQUIRED_RERUNS`: `none`
- `AGY_RAW_SHA256`: `115bd165934339bc5b890088c827f73a1aad50a5d59159d9f6667dfd70f65c96`
- `AGY_STDERR_SHA256`: `bf32ab8c082fa1aff618ee172c412b767bf7f636479cf49543749f2ba6ad30ee`
- `SAME_HASH`: `true`
- `GATE_RESULT`: `HARDENING_8_EVIDENCE_PACKAGE_GREEN`

Both lanes independently retained the same non-blocking boundaries: the
CockroachDB workload is bounded and single-region, real-workflow evidence has
one operator, model-actor campaigns are synthetic, and competition-scale proof
does not establish unlimited production longevity.

The R1 attempts remain preserved but do not count: GLM used the wrong packet
hash/model label, and AGY failed wrapper schema validation. R2 reran the full
panel on one corrected frozen packet; no stale R1 verdict was retained.
