# EV1-T06 Guarded Execution Preflight R1

- `STATUS`: `GREEN_DELETION_NOT_STARTED`
- `RUNNER_SHA256`: `9158451861ba0febc6691b6320543eddc01953836f729b8077937ee2e28f5abe`
- `CAPTURE_RECEIPT_SHA256`: `8fb15d80b7831a648d4a52a3f975eb162525d4a38d6cf0cd16e74a10fbad8664`
- `LOCAL_PREFLIGHT_RECEIPT_SHA256`: `a13dc5248e8bc674fab915a909778e4494a3b96300ecf0a851e72990bffd16b5`
- `PACKET_SHA256`: `8f8aa8398fdff0d94898a942f7973bd4d3bf98df1be97e144e90dccf4fe6671f`
- `GLM_5_2`: `GREEN`
- `AGY`: `GREEN`
- `SAME_PACKET`: `TRUE`
- `RECUSAL`: `CLEAR`
- `ORIGINAL_PRESENT`: `TRUE`
- `DELETION_STARTED`: `FALSE`

The first GLM output was substantively GREEN but its Markdown formatting did
not match the validator. That raw output was preserved unchanged. The validator
was corrected only to accept bold labels and backticks; the packet and verdict
did not change. AGY then returned GREEN over the identical packet.
