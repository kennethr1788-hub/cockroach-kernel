# PDH-1 Information-Boundary Final Judge Receipt R1

- `STATUS`: `PDH_1_INFORMATION_BOUNDARY_GREEN`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `MEASURED_EXECUTIONS`: `30`
- `MECHANICAL_PASS`: `30`
- `MECHANICAL_FAIL`: `0`
- `PACKET_SHA256`:
  `b60bfad7f54f10796a28dc2db2f5b642472341afdbfe11e2c8b45c9fe28acc02`
- `MECHANICAL_RECEIPT_FILE_SHA256`:
  `9de60ade4e7ca403f4025802d8e1d71aeaec1819d5906e9d639cd4b5ca091b19`
- `JUDGE`: `GLM 5.2`
- `SERVED_MODEL`: `glm-5.2`
- `RAW_RESPONSE_SHA256`:
  `684cff8a1a1b5d42db1a7bd5e2e82219cfc5b17ef675451a2b4ee29aeb169514`
- `VERDICT`: `GREEN`
- `MATRIX_CORRECTNESS`: `SUPPORTED`
- `B4_NO_INVENTION`: `SUPPORTED`
- `DETERMINISM`: `SUPPORTED`
- `BOUNDARY_ENFORCEMENT`: `SUPPORTED`
- `CLAIM_SCOPE`: `SUPPORTED`
- `BLOCKERS`: `[]`
- `EVIDENCE_GAPS`: `[]`

The valid non-blocking risk preserves the initial pre-import evidence-controller
failures and the narrow independently reviewed venv-launcher repair. Those
attempts are excluded from the measured denominator and remain in the evidence
tree.

## Supported claim

> Across 30 frozen local executions, explicitly captured representations were
> restored byte-exactly, partial evidence restored only its provable subset,
> absent evidence produced a deterministic refusal without inventing bytes,
> and tampered evidence was rejected without mutation.

This does not support arbitrary undelete, forensic disk recovery, zero-data-loss
recovery, or recovery from nothing.
