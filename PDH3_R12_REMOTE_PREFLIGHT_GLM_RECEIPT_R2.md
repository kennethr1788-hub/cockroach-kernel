# PDH-3 R12 Paid Preflight GLM Receipt R2

- Served model: `glm-5.2`
- Packet SHA-256:
  `f00418ed8aa702dfd3433cccf4e88a47c8420a3a5d96b36c5b72745613ee9958`
- Threshold-amendment SHA-256:
  `012716a1a377a938bc8ca20b84631b6450f407c635748929d91db59ff675e2e1`
- Verdict: `GREEN`
- Critical findings: `NONE`
- High findings: `NONE`
- Required corrections: `NONE`
- Authority: one bounded R12 paid preflight only; no retry and no 24-hour
  measured campaign.

R1 was invalidated before worker creation when the local prelaunch audit found
that its scrubbed environment omitted Ubuntu's sbin locations. No creation
attempt was consumed. R2 binds the repaired source, deterministic rebuilt
archive, and replacement absolute launch/deletion window.

Raw output: `PDH3_R12_REMOTE_PREFLIGHT_GLM_RAW_R2.txt`
