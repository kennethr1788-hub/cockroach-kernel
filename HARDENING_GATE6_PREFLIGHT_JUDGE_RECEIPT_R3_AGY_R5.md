# Hardening Gate 6 R3 — Attempt-03 Same-Hash Preflight Receipt

- `STATUS`: `PREFLIGHT_GREEN`
- `PACKET_SHA256`: `0e047e3abfd69cc5660c88a283eb8595e869dee575eadaa34409b74dfec5f468`
- `GLM_SERVED_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RECUSAL`: `clear`
- `GLM_VALID_RAW_SHA256`: `4ac316a0aeb75ca8857f96490885ae57a904b4aba0d78c83d07c6d49c261b752`
- `GLM_VALID_STDERR_SHA256`: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`
- `GLM_INVALID_ATTEMPT_1`: `PLACEHOLDER_TEMPLATE; NOT_COUNTED; RAW_SHA256_a6884f85ee9e34274cca69b856d1fe412e10b27fa0a43b58ccbcd99425f008cb`
- `GLM_INVALID_ATTEMPT_2`: `EMPTY_FINISH_REASON_LENGTH; NOT_COUNTED; RAW_SHA256_e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; STDERR_SHA256_fe590c1b1c98947e0c4331ea877ef623c98a631974c0775f7ac9031d03b816b1`
- `AGY_MODEL`: `Gemini 3.1 Pro (High)`
- `AGY_VERDICT`: `GREEN`
- `AGY_RECUSAL`: `clear`
- `AGY_RAW_SHA256`: `42643b42a57f4bb970138e3a93902eba3a20cbc516b751c199b816689b4f551d`
- `AGY_STDERR_SHA256`: `704cd697e3c35f59e1936b327608c169e0648d6966e31ac5a99ade7b5816186e`
- `CLAUDE`: `RECUSAL_REQUIRED_PRESERVED_NOT_COUNTED`
- `RUNPOD_RUNNING_INVENTORY`: `[]`
- `MEASURED_EXECUTIONS`: `0`
- `UTC_RECORDED`: `2026-07-28T02:57:43Z`

Only the third GLM invocation produced a valid, fully populated contract. Both
counted judges bind the same exact packet hash with GREEN and recusal clear.
This authorizes attempt 03 and its pre-payload capability canary. Payload upload
remains conditional on canary GREEN, and final same-hash review remains required.
