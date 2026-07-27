# Hardening Gate 5 — Independent GLM Judge Receipt R2

- `VERDICT`: `GREEN`
- `JUDGE`: `GLM_4_7_DIRECT`
- `SERVED_MODEL`: `glm-4.7`
- `TARGET_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_GREEN`
- `PACKET_SHA256`: `8d72c554e3b23b1fafac05b265dd410406e76990b733b48ed9496ff05efaff29`
- `CANDIDATE_COMMIT`: `bd29bd23e831175aa54526b9e3c48bd04e8af3ed`
- `RAW_OUTPUT_SHA256`: `14ca7c68c2d0625f5b4218b682c3eee8eb7ea6e5aa208f82ae887850f49628fc`
- `STDERR_SHA256`: `3d6cc99569f37fabd00da60b0bb51340a75282320e786faae0a664290a857756`
- `FINDINGS`: `[]`
- `UTC_RECORDED`: `2026-07-27T21:29:29Z`

The response parsed after removing only the Markdown JSON fence. Its packet
hash, candidate commit, target gate, verdict enum, empty findings list, and
served-model line match the frozen R2 packet and direct-route requirement.
The judge was non-authoring and received no tools, filesystem, browser,
credential, deployment, or mutation authority.

The R1 attempt has no gate authority. The local egress guard rejected its raw
candidate diff before provider execution because credential-adjacent source
assignments were present; the empty output and exact rejection stderr remain
preserved. R2 retained the same candidate commit and evidence but excluded
those source lines from external egress.
