# Hardening Gate 6 R3 — Superseded GLM plus AGY Preflight Receipt

- `STATUS`: `SUPERSEDED_NOT_GREEN`
- `PACKET_SHA256`: `bce79ec92f76469cbd11efb0a4fd6221ab3da7e3135b2370907800426b40e7be`
- `AGY_RESULT`: `GREEN; RECUSAL_CLEAR; EXACT_HASH`
- `GLM_ATTEMPT_1`: `NO_VERDICT; HTTP_200_EMPTY_RESPONSE; FINISH_REASON_LENGTH`
- `GLM_ATTEMPT_2_ROUTE`: `SERVED_BY_GLM_5_2`
- `GLM_ATTEMPT_2_RESULT`: `INVALID; ADOPTED_EMBEDDED_HISTORICAL_CLAUDE_IDENTITY; NO_GLM_CONTRACT`
- `CLASSIFICATION`: `JUDGE_BOUNDARY_VIOLATION_BY_IDENTITY_INSTRUCTION_CONTAMINATION`
- `RUNPOD_CREATED`: `no`
- `MEASURED_EXECUTIONS`: `0`
- `GATE7`: `FORBIDDEN`
- `UTC_RECORDED`: `2026-07-28T02:00:00Z`

The AGY verdict cannot be retained after the packet changes. The GLM route was
genuinely served by GLM 5.2, but its second output copied the embedded historical
Claude voice and recusal instead of acting as GLM under the top-level contract.
That output is preserved exactly and is not counted as a verdict. The packet is
superseded. The next revision removes raw historical judge voices, retains the
consolidated Claude recusal receipt, and strengthens the current-lane output
contract. Both GLM and AGY must review the new exact hash from scratch.
