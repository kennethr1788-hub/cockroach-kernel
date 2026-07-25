# S1 Retry Attempt Ledger

- `CAMPAIGN_ID`: `CK-S1-20260725-FOUNDATION-R3`
- `PACKET`: `S1_RETRY_PACKET_R3.md`
- `PACKET_SHA256`: `82fc0dcdd38a814e40a39f85c57b1f35948d46792575c7fdd2db24283768ef87`
- `STATUS`: `CK_S1_FOUNDATION_SOAK_GREEN`
- `ATTEMPTS_USED`: `1`
- `EXTANT_S1_WORKERS`: `0`
- `WORKLOAD_STARTED`: `YES`
- `POD_ID`: `wo1iq5wtk04q49`
- `REMOTE_PID`: `153`
- `WORKLOAD_START_UTC`: `2026-07-25T21:43:22Z`
- `WORKLOAD_RESULT`: `GREEN`, 61/61 checkpoints
- `POD_TEARDOWN`: `GREEN`, deleted and scoped inventory empty
- `AGGREGATE_EXACT_CHARGE`: `UNAVAILABLE`
- `AGGREGATE_ESTIMATED_UPPER_USD`: `0.070116249`
- `UTC_CREATED`: `2026-07-25T21:37:17Z`

Independent GLM 5.2 returned GREEN on the exact packet hash at
`2026-07-25T21:39:12Z`. Attempt 1 created Pod `wo1iq5wtk04q49`, which passed
all pre-upload worker checks. Creation retries are permanently closed.

The immutable payload and runtime hashes passed remote verification. The
single authorized 3,600-second workload started at `2026-07-25T21:43:22Z`.
No replacement is permitted.

The workload completed technically GREEN, evidence retrieval and hashes passed,
and Pod teardown is verified. Exact itemized billing was delayed; Kenneth
explicitly accepted the visible account-side charge and removed that delay as a
blocker. S1 awaits final independent review.

Independent GLM 5.2 returned GREEN on final packet SHA-256
`46e6a9081c949d586d9ea4812a31e6baf033342bef380bdf4a8ed50e73cf25b1`
at `2026-07-25T22:52:29Z`. The campaign is closed.
