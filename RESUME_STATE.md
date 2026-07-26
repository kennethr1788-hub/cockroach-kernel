# Resume State

- `CURRENT_PHASE`: `S2_REPLACEMENT_PREFLIGHT`
- `LAST_GREEN_GATE`: `CK_P7_RECOVERY_GREEN`
- `NEXT_ALLOWED_ACTION`: freeze machine-readable runtime hashes and a replacement S2 packet, then obtain GLM plus Claude GREEN on one exact hash
- `FORBIDDEN_ACTIONS`: replacement worker creation before the new same-hash preflight gate; P8 or later; AWS; public actions; HOME/live-memory mutation
- `CURRENT_COMMIT`: `f763685183a6abc07ff1f587433da79b0c5fa8ad`
- `PENDING_BLOCKERS`: replacement preflight packet and required GLM plus Claude verdicts are open
- `REQUIRED_JUDGE_STATE`: GLM and Claude GREEN on the same exact replacement-preflight packet before worker creation
- `REPLACEMENT_AUTHORIZATION_SHA256`: `7661fd8de8284cfd69dfcf584f05e6b0584bb736047e626d594a4595047e486e`
