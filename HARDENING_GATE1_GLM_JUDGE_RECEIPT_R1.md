# Hardening Gate 1 GLM Judge Receipt R1

- `UTC_REVIEWED`: `2026-07-27T16:42:52Z`
- `JUDGE_ROUTE`: `glm-zai`
- `SERVED_MODEL`: `glm-4.7`
- `JUDGE_ROLE`: `independent_non_authoring_cli_judge`
- `TOOLS_OR_WRITE_AUTHORITY`: `none`
- `PACKET_SHA256`: `0d062768d304b7ea5e4ba64e53c5946717b55302ad2646620e3c522b7905e97c`
- `WRAPPER_SHA256`: `0b94755754de89557ffb9d00b45b8d8fef6578614d00563db2320e940f83748f`
- `EXIT_STATUS`: `0`

## Raw verdict

```json
{
  "verdict": "GREEN",
  "gate": "HARDENING_1_CLI_GREEN",
  "packet_sha256": "0d062768d304b7ea5e4ba64e53c5946717b55302ad2646620e3c522b7905e97c",
  "findings": [
    "Four required command shapes exist.",
    "Default output correctly shows promotion and structured refusal.",
    "Refusal output includes verdict, stable reason, bounded provable state, ACTION_TAKEN: NONE, next safe action, and canonical receipt path.",
    "Flags --explain, --json, and inspect expose bounded evidence.",
    "Two independent clean clones installed successfully.",
    "All clones passed 6 CLI and 113 inherited P9 tests.",
    "Source passed 125 tests across CLI, P9, and P4.",
    "Promotion and refusal receipt bytes were identical across clones, confirming determinism.",
    "Parity with underlying P9/P4 implementation confirmed.",
    "Demos passed under OS-level network-denial profile and empty environment (credential-free).",
    "Trial roots removed with no matching child remaining."
  ],
  "reason": "The CLI satisfies all Hardening Gate 1 requirements as a faithful, deterministic, and credential-free facade over the existing replay and verifier."
}
```

This verdict closes only Hardening Gate 1. It does not authorize or certify a
public AWS surface, new RunPod lifecycle, S3 rerun, release, or submission.
