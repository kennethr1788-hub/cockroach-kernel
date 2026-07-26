# S2 Final Judge Panel R1

- `PACKET_SHA256`: `46e1135cd285f0023a12b10bd033808c3f628e577f737f905ef2a27789fdfb9f`
- `GLM_5_2`: `GREEN`
- `CLAUDE_OPUS_4_8`: `GREEN`
- `AGY_GEMINI_3_1_PRO_HIGH`: `GREEN`
- `ALL_VALID_VERDICTS_SAME_HASH`: `YES`
- `INVALID_RESULTS_CARRIED_FORWARD`: `NO`
- `FINAL_PANEL`: `GREEN`
- `P8_STATUS`: `NOT_STARTED`
- `BAND_B_STATUS`: `OPEN`

The first Claude attempt is separately preserved and excluded because its
stdin included a role preamble and therefore had the wrong wrapper hash. The
valid rerun used only the exact frozen packet bytes. No judge authored or
modified implementation, evidence, or the packet.
