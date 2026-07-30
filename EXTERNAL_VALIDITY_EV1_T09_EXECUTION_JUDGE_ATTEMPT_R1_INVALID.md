# EV1-T09 Execution Judge Attempt R1 Invalid

- `STATUS`: `INVALID_TRANSPORT_NO_VERDICT`
- `PACKET_SHA256`: `341a54c7528213f76896237b2387dd1dfdf2845fb472ebac2929a7fdea1b6f50`
- `JUDGE_ROUTE`: `DIRECT_GLM_5_2`
- `SERVED_MODEL`: `glm-5.2`
- `PROCESS_EXIT`: `1`
- `FAILURE`: `HTTP 200 empty response content; finish_reason=length`
- `RAW_SHA256`: `fe590c1b1c98947e0c4331ea877ef623c98a631974c0775f7ac9031d03b816b1`
- `AGY_INVOKED`: `FALSE`
- `VERDICT`: `NONE`
- `PACKET_CHANGED`: `FALSE`
- `DELETION_STARTED`: `FALSE`

The provider returned no review content and therefore no verdict. R2 changes
only the maximum judge response allowance from 8,192 to 32,768 tokens. It does
not change the packet, product, runner, task, thresholds, or decision criteria.
