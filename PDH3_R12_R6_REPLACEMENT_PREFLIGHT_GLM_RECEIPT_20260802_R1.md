# PDH-3 R12 R6 replacement preflight GLM receipt R1

Status: `GLM_5_2_GREEN__ONE_REPLACEMENT_PREFLIGHT_ONLY`

UTC completed: `2026-08-02T09:05:31Z`

Judge route: direct `glm-zai`

Served model: `glm-5.2`

Target packet:
`PDH3_R12_R6_REPLACEMENT_PREFLIGHT_PACKET_20260802_R1.md`

Target packet SHA-256:
`0bec28d822bcf61ebb9560fc172eb8933428bbd1773c1d33a120c508a8362802`

Raw output path:
`.pdh3-runtime/r12-preflight/pf0-r6-replacement-r2/glm-preflight-raw.txt`

Raw output SHA-256:
`2ca6a726052bdb0e2970e6524731e28016221d9b42d320cc584cb172f4cc282c`

Validated result:

```text
SERVED_MODEL: glm-5.2
TARGET_PACKET_SHA256: 0bec28d822bcf61ebb9560fc172eb8933428bbd1773c1d33a120c508a8362802
VERDICT: GREEN
BLOCKERS:
- none
NON_BLOCKING_RISKS:
- Secure Cloud L40S stock is currently listed as "Low", which could lead to a launch window miss if provider capacity depletes before the single creation attempt is executed.
EVIDENCE_REQUIRED:
- none
```

Mechanical validation proved exactly one served-model field, one target hash,
one verdict, no contradictory verdict, and wrapper-reported served model
`glm-5.2`.

This result authorizes only the single replacement R6 paid preflight bound to
the target packet. It does not authorize a second creation attempt, a 24-hour
campaign, or a final GREEN declaration by the builder.
