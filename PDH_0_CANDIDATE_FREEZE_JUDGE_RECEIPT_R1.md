# PDH-0 Candidate Freeze Judge Receipt R1

- `STATUS`: `PDH_0_CANDIDATE_FREEZE_GREEN`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PACKET`: `PDH_0_CANDIDATE_FREEZE_PACKET_R1.md`
- `PACKET_SHA256`:
  `17687d96e46002adca0f712a5b6355bac897e7d11ae11f6e2e5e0fca530f0006`
- `PARENT_MANIFEST_SHA256`:
  `ab8b0e27b1b0347fbe65bce1ceee53228799af5f3abd2e75454e92d823b23cc2`
- `JUDGE`: `GLM 5.2`
- `SERVED_MODEL`: `glm-5.2`
- `RAW_VALID_RESPONSE_SHA256`:
  `96c4ee4875499e5ddba245d594cd5a2067f653696116cf88729855e8c1167220`
- `VERDICT`: `GREEN`
- `CANDIDATE_BINDING`: `SUPPORTED`
- `OUTCOME_MAPPING`: `SUPPORTED`
- `PDH1_BOUNDARY`: `SUPPORTED`
- `BLOCKERS`: `[]`

The first same-packet invocation returned the same substantive GREEN fields but
appended a Markdown fence. It is preserved as invalid output at
`PDH_0_CANDIDATE_FREEZE_GLM_ATTEMPT1_INVALID_R1.txt`, SHA-256
`9b529f7f69d63386897d9c8479d3344ef1b90b5c0d03f0bf7737aaa258f2945a`.
It does not count as the gate receipt.

The valid response preserves one non-blocking limitation: the optional HTTP
facade’s installed-package imports require a separate product-revision gate if
PDH-3 or PDH-4 later invokes that installed surface. This gate authorizes only
the local PDH-1 information-boundary campaign.
