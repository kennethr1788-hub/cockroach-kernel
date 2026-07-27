# Hardening Gate 5 Status

- `STATUS`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `LAST_GREEN_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `NEXT_TARGET`: `HARDENING_6_RUN1_R2_PREFLIGHT`
- `PARENT_GATE`: `HARDENING_4_BASELINE_PROTOCOL_R2_GREEN`
- `CANDIDATE_IMPLEMENTATION_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `GATE4_PROTOCOL_SHA256`: `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`
- `EVIDENCE_REPORT`: `HARDENING_GATE5_EVIDENCE_REPORT_R2.md`
- `FINAL_PACKET_SHA256`: `41efeb9270b76a0d4e1f711d5b1ab3270ecd92d32eccce93f07bef8a6ba036c0`
- `LOCAL_SMOKE_SUMMARY_SHA256`: `781531c80ce1415ca208c4f2119cb57be660db73276f556610f1b57dd83b7c1b`
- `JUDGE_STATE`: `GLM_5_2_GREEN; CLAUDE_OPUS_4_8_GREEN_RECUSAL_CLEAR`
- `GLM_RAW_SHA256`: `aeb7368a182fd1ad4cdfc615e0e31828c1ec80a1e36418ca585b9c1b5d6cc644`
- `CLAUDE_RAW_SHA256`: `120f440b93e0ed0557910bda585bf2958dad5d12a377acb145cdd704766907b4`
- `BLOCKERS`: `none`
- `UTC_RECORDED`: `2026-07-27T22:57:33Z`

The R2 candidate preserves all original Gate 5 obligations and repairs the
five Linux portability/evidence defects that blocked Gate 6. It produced 18
exact-candidate preflight receipts plus three semantic repeats under network
denial with zero trial residue. Independent GLM 5.2 and exact Claude Opus 4.8
returned GREEN over one sanitized packet hash; Claude recusal is clear.

This status does not claim Gate 6, a measured 54-execution campaign, a baseline
or product winner, Linux RunPod execution, S3-R2, release, or submission.
Behaviorally relevant changes after candidate commit `8718fbe` invalidate new
downstream evidence and require another candidate. Gate 6 R2 still requires a
separate Linux preflight packet and its declared same-hash reviews before any
RunPod worker.
