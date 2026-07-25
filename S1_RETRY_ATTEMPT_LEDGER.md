# S1 Retry Attempt Ledger

- `CAMPAIGN_ID`: `CK-S1-20260725-FOUNDATION-R3`
- `PACKET`: `S1_RETRY_PACKET_R3.md`
- `PACKET_SHA256`: `82fc0dcdd38a814e40a39f85c57b1f35948d46792575c7fdd2db24283768ef87`
- `STATUS`: `ATTEMPT_01_WORKER_VERIFIED`
- `ATTEMPTS_USED`: `1`
- `EXTANT_S1_WORKERS`: `1`
- `WORKLOAD_STARTED`: `NO`
- `AGGREGATE_EXACT_CHARGE`: `UNAVAILABLE`
- `UTC_CREATED`: `2026-07-25T21:37:17Z`

Independent GLM 5.2 returned GREEN on the exact packet hash at
`2026-07-25T21:39:12Z`. Attempt 1 created Pod `wo1iq5wtk04q49`, which passed
all pre-upload worker checks. Creation retries are permanently closed.
