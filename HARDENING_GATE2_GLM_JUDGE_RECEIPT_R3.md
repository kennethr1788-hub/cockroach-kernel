# Hardening Gate 2 Final GLM Judge Receipt R3

- `VERDICT`: `GREEN`
- `TARGET_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `PACKET`: `HARDENING_GATE2_FINAL_GLM_PACKET_R3.md`
- `PACKET_SHA256`: `5c7624937bdae41f64dbd5e2c66f34afc3326fdacfdb1484ef118c964e386b41`
- `PACKET_COMMIT`: `802d33fe476f848eb68a2a63475200033a32f708`
- `IMPLEMENTATION_EVIDENCE_COMMIT`: `471bc6d3c1fb6a88e1eba0ae064d897a72b42b4b`
- `SERVED_MODEL`: `glm-5.2`
- `SERVED_MODEL_VERIFICATION`: direct wrapper response field verified by `glm-zai`
- `RAW_OUTPUT`: `HARDENING_GATE2_GLM_JUDGE_RAW_R3.txt`
- `RAW_OUTPUT_SHA256`: `10a9c7fb4d52568f6fec9192192a69b574b5a957f0814bf763ffed3e9701bd45`
- `UTC_RECEIVED`: `2026-07-27T19:00:53Z`
- `JUDGE_ROLE`: independent, non-authoring, no tools or implementation authority

Local validation parsed the returned JSON and required all of:

- verdict exactly `GREEN`;
- packet hash exactly equal to the frozen R3 file hash;
- nine findings present;
- wrapper exit code zero;
- wrapper-served model exactly `glm-5.2`.

The model-generated JSON field `model: glm-final-judge` is a descriptive label,
not model-identity evidence. The transport wrapper's verified served-model
field is controlling.

R1 and R2 were blocked by the local outbound safety gateway before provider
execution because embedded evidence contained sensitive-field assignment
syntax. They produced no judge verdict. R3 removed raw credential-handling
source and exposed only sanitized findings, hashes, metrics, and boundaries.
The underlying implementation/evidence commit did not change.

The independent verdict states that the narrow Gate 2 target is supported and
that the disclosed scaling, denial-of-wallet, deferred-teardown, and preserved
failure limitations are compatible with that target.

Post-capture scanning returned zero gitleaks findings. `detect-secrets` flagged
the 64-character `packet_sha256` on raw-output line 5 as one unverified
high-entropy hexadecimal string. It is the public packet digest shown above,
not authentication material; the raw judge output remains unmodified.
