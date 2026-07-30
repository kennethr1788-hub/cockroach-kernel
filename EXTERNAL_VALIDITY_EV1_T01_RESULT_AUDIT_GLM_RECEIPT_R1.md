# EV1-T01 GLM Result Audit Receipt R1

- `STATUS`: `INVALID_IDENTITY_LABEL; PRESERVED`
- `UTC_RECORDED`: `2026-07-30T15:27:58Z`
- `TARGET_PACKET_SHA256`: `6e5f1c1edc0d3bb8438120ea824557a75071bc55807da376c336c6f3b4cfa533`
- `RAW_OUTPUT_FILE_SHA256`: `45a61860a1461e866564a9abc38d560ae7b605ba40752fcc7f2c1b0fc4b236ff`
- `R2_AMENDMENT_SHA256`: `d55a9eaa7984e7b07988ba54dc5bec5f40a210d52e17034b2febb6bf46f8e258`
- `R2_COMPOSED_INPUT_SHA256`: `989a2e866dd9464dcc82d039d199b45085b254e263e2254503a6f9cc058d56b9`
- `TRANSPORT_EXIT`: `0`
- `TRANSPORT_SERVED_MODEL`: `glm-5.2`
- `GENERATED_MODEL_LABEL`: `Claude 3.5 Sonnet (Anthropic)`
- `VERDICT_COUNTED`: `FALSE`
- `SUBSTANTIVE_OPINION`: `All three conservative conclusions were marked supported, but the result cannot count because the generated identity field contradicts verified transport identity.`
- `NEXT_ACTION`: `Use a frozen output-contract amendment that removes model self-identification, preserve the same evidence packet unchanged, and perform one bounded R2 audit through verified glm-5.2 transport.`

The transport-level served-model evidence is authoritative for route identity.
The model's prose cannot override it. Because R1 required the model to report
its own identity and it returned a contradictory family, the structured result
is invalid even though its reasoning was evidence-aligned.
