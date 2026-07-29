# Hardening Gate 7 Run 3 Preflight Blocked Receipt R1

- `STATUS`: `HARDENING_7_RUN3_BLOCKED`
- `BLOCKER`: `AGY_JUDGE_BINARY_DRIFT`
- `UTC_CREATED`: `2026-07-29T01:44:59Z`
- `LAST_GREEN_GATE`: `GATE7_RUN3_LOCAL_REPAIR_GREEN`
- `CURRENT_COMMIT`: `a7ffa36ed82664fe9443df9aa553cd26bd031566`
- `REPAIRED_SOURCE_COMMIT`: `c8383c61cd599d10b02d861aabc764686a81d766`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PREFLIGHT_PACKET`: `HARDENING_GATE7_RUN3_PREFLIGHT_PACKET_R2.md`
- `PREFLIGHT_PACKET_SHA256`: `ba08a143db1304a6a5f9ae60708a774658609a4e8d1ebfe2bb4dcb1b966d4383`
- `RUNPOD_ATTEMPTS`: `0`
- `RUNPOD_ACTIVE_INVENTORY`: `[]`
- `HIDDEN_SEED`: `ABSENT`
- `MEASURED_TRACKS`: `NOT_STARTED`

## Packet history

Run 3 packet R1 remains preserved at commit
`78ad42f191888513b3caef07030189bb1fe43a46`. Its first GLM attempt was
blocked locally by the egress sanitizer before provider execution because
embedded exact source contained credential-like lexical test identifiers. No
provider verdict was produced or counted.

R2 retained the exact source hashes and used clearly disclosed lexical aliases
only in displayed source excerpts. The canonical egress gateway returned
`allow`; gitleaks returned zero findings. R2 was committed without changing
the product candidate, workload, thresholds, or local evidence.

## GLM lane

The first R2 GLM provider result returned the correct packet hash and GREEN but
misidentified its `judge_model` as `agy-judge`. It is invalid and preserved.

- `INVALID_RAW_SHA256`: `59d61dde0c83b4f2508666cfcf530668164135779717e1b4b99ff00bca6398bb`
- `INVALID_STDERR_SHA256`: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`

The second R2 attempt was invoked with wrapper-bound identity instructions.
The direct wrapper independently proved `served by glm-5.2`; fallback was
disabled; the result returned the exact packet hash, `GREEN`, and
`recusal_clear=true`.

- `MODEL`: `glm-5.2`
- `VERDICT`: `GREEN`
- `PACKET_SHA256_RETURNED`: `ba08a143db1304a6a5f9ae60708a774658609a4e8d1ebfe2bb4dcb1b966d4383`
- `RECUSAL_CLEAR`: `true`
- `VALID_RAW_SHA256`: `28dd30abe1c1dd1adfee2fa109a3ac50a17a337d46843e0607a5b33da25ed2ee`
- `VALID_STDERR_SHA256`: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`

## AGY lane

The installed canonical `agy-judge` wrapper remained unchanged at SHA-256
`217cad1a22d4ca63d356fbe97dfa4caaf9475a5c619232af329b8d00d2a6df15`.
Before the packet invocation, its wrapper fixture tests passed and the live
model inventory exposed `gemini-3.1-pro-high`.

During this session the underlying signed AGY binary auto-updated from the
reviewed 1.1.5 binary to version 1.1.8, SHA-256
`251662551657dd0955428dd31536e7adf84c1cb4d53f20b6dca8bf8714762ff9`.
The canonical wrapper correctly rejected the new binary because its reviewed
pin is the former 1.1.5 SHA-256. No AGY provider execution occurred and stdout
was empty.

- `AGY_VERDICT`: `UNAVAILABLE; NOT_GREEN`
- `AGY_STDOUT_SHA256`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `AGY_STDERR_SHA256`: `ba0e786c8d8ccc4f2073a5c279e43e53dfcb785e6904f6fd088d63483e50e2df`
- `AGY_ERROR`: `AGY binary hash drifted; re-review before use`

No wrapper pin, HOME runtime, global playbook, or judge configuration was
modified. Bare AGY was not substituted for the canonical judge route.

## Gate result

The prompt requires same-hash exact-model GLM 5.2 and canonical AGY GREEN
before any RunPod worker is created. GLM is GREEN; AGY is unavailable. The
preflight is therefore BLOCKED. Local repair evidence remains valid, but no
provider campaign, hidden seed, or measured work is authorized.

## Resume action

Separately authorize and independently requalify the canonical AGY judge route
for the signed version 1.1.8 binary, including binary/release provenance,
wrapper fixtures, deny-all settings, authenticated model inventory, exact
Gemini 3.1 Pro High backend binding, provider-response proof, and negative tool
probes. Do not merely replace the hash.

After that route is independently GREEN, rerun canonical `agy-judge` over the
unchanged packet SHA-256
`ba08a143db1304a6a5f9ae60708a774658609a4e8d1ebfe2bb4dcb1b966d4383`.
If any packet byte or judge contract changes, freeze a new packet and rerun
both GLM 5.2 and AGY on the new same hash. Create no RunPod worker until both
valid results are GREEN.
