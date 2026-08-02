# PDH-3 R12 Paid Preflight GLM Receipt R1

- Served model: `glm-5.2`
- Packet SHA-256:
  `cfedeb1a611abbb4eff80830c62da8ec7f90675e927200dbd79a71f1ebb0f2be`
- Threshold-amendment SHA-256:
  `012716a1a377a938bc8ca20b84631b6450f407c635748929d91db59ff675e2e1`
- Verdict: `GREEN`
- Critical findings: `NONE`
- High findings: `NONE`
- Required corrections: `NONE`
- Authority: one bounded R12 paid preflight only; no retry and no 24-hour
  measured campaign.

The first identical-packet request returned HTTP 200 with empty content and
`finish_reason=length`; it is preserved as `JUDGE_UNAVAILABLE` and did not
count. The successful retry used a larger response allowance without changing
either target document or hash.

Raw output: `PDH3_R12_REMOTE_PREFLIGHT_GLM_RAW_R1.txt`
