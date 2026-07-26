# S2 Final Claude Invalid Attempt R1

- `INTENDED_PACKET_SHA256`: `46e1135cd285f0023a12b10bd033808c3f628e577f737f905ef2a27789fdfb9f`
- `WRAPPER_RETURNED_SHA256`: `31348f3d391625029915f07010ec62ebc90c1585cad5f24cc9d7df7e85a5a52b`
- `SERVED_MODEL`: `claude-opus-4-8`
- `SUBSTANTIVE_VERDICT`: `GREEN`
- `GATE_VALIDITY`: `INVALID_HASH`

The first invocation prepended role text before the frozen packet. The wrapper
correctly hashed the complete stdin and returned a different SHA-256. That
result is preserved but cannot count. The packet and evidence were not changed;
Claude was rerun with only the exact frozen packet bytes.
