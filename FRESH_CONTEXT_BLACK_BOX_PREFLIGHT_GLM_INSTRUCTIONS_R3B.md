# Independent GLM 5.2 Final R3B Public-Fixture Preflight Review

You are the independent, non-authoring final preflight judge. Review only the
exact packet bytes appended after these instructions. Do not write code,
patches, execution plans, or hidden cases. Do not use tools or infer missing
evidence.

- `TARGET_PACKET`: `FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_PACKET_R3B.md`
- `TARGET_PACKET_SHA256`: `2a273eabffa107e0056c512dcc10b6f34398220fe97c949924552e9843bfb8f0`
- `REQUESTED_MODEL`: `glm-5.2`
- `HIDDEN_SEED_CREATED`: `NO`
- `HIDDEN_EXECUTIONS`: `0`

Reject mixed candidate, plan, profile, preflight, or evidence bindings.
Determine whether this exact candidate and fixed public-fixture preflight meet
the execution prompt's `BLACK_BOX_R3_PREFLIGHT_GREEN` requirements. Verify the
scenario-driven installed interface, 304 tests, two clean clones, deterministic
scenario binding, deny-default Seatbelt enforcement, 5 allow and 12 denied
canaries with complete telemetry, eight telemetry-fault tests, nine residue
mutations plus clean control, ten scorer rejections plus allowed discovery,
hash/scan/teardown integrity, zero product drift, honest limitations, zero
hidden seed/session, and the stop boundary.

This is not black-box campaign success and cannot authorize hidden generation,
actor calls, spend, public claims, Gate 7, or product mutation.

Return exactly:

```text
VERDICT: GREEN | NOT_GREEN | BLOCKED
SERVED_MODEL: glm-5.2
PACKET_SHA256: 2a273eabffa107e0056c512dcc10b6f34398220fe97c949924552e9843bfb8f0
RECUSAL: CLEAR | REQUIRED
BLOCKERS:
- <none or exact blocker>
NON_BLOCKING_LIMITATIONS:
- <none or evidence-bounded limitation>
NEXT_ACTION:
- obtain separate hidden-campaign authorization | stop and repair exact blocker
```

GREEN certifies only the fixed public-fixture preflight boundary.
