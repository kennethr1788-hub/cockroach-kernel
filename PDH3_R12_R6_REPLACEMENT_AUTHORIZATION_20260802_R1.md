# PDH-3 R12 R6 replacement authorization receipt R1

Status: `OPERATOR_AUTHORIZATION_RECORDED`

UTC recorded: `2026-08-02T09:03:00Z`

Operator: Kenneth

Exact operator statement:

> okay i authorize another attempt for another run pod run prior to the new run examine the failures and correct them make a new preflight and have glm review prior to the launch

## Bound interpretation

This records authorization for exactly one replacement R6 paid-preflight
creation attempt after failure analysis, corrective implementation, a new
frozen preflight packet, and direct independent GLM 5.2 GREEN over that exact
packet hash.

The unchanged outer envelope is
`PDH3_R12_R6_AUTHORIZATION_ENVELOPE_20260802_R1.md` at SHA-256
`e5fb1b999a84339b780a8c299817c9fa11b0aba38e582db766a2301e6594455b`.
It supplies the existing Secure Cloud L40S, rate, aggregate-cost, disposable
disk, zero-volume, synthetic-data, evidence-retrieval, and teardown limits.

This receipt does not authorize:

- more than one replacement creation attempt;
- replacement after PF-4 or main-bundle upload;
- a 24-hour measured campaign;
- a higher rate or spend ceiling;
- persistent or network volume;
- credentials inside the Pod;
- product or threshold changes;
- public release or submission.

The existing operator authorization to read `~/.runpod/config.toml` remains
limited to injecting the API key into the local controller process environment.
The credential may not be printed, persisted, logged, transferred, or committed.
