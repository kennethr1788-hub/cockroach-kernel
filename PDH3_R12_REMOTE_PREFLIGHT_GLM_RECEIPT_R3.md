# PDH-3 R12 Paid Preflight GLM Receipt R3

- Served model: `glm-5.2`
- Packet SHA-256:
  `1e3db984d08c00ee58be04573c7f5b19742a659ea162c2fcfc09d3e21981755e`
- Threshold-amendment SHA-256:
  `012716a1a377a938bc8ca20b84631b6450f407c635748929d91db59ff675e2e1`
- Verdict: `GREEN`
- Critical findings: `NONE`
- High findings: `NONE`
- Required corrections: `NONE`
- Authority: one bounded R12 paid preflight only; no retry and no 24-hour
  measured campaign.

R2 was invalidated before worker creation because the host would have
pre-created a launcher-owned acknowledgement root and transferred an unbound
remote verifier helper. No creation attempt was consumed. R3 binds the
launcher-owned root lifecycle and archive-contained verifier mode.

Raw output: `PDH3_R12_REMOTE_PREFLIGHT_GLM_RAW_R3.txt`
