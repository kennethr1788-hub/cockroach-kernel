# Hardening Gate 6 — Preflight Egress Block Receipt R2

- `STATUS`: `PREFLIGHT_JUDGE_CALLS_BLOCKED_BEFORE_PROVIDER_EXECUTION`
- `PACKET_SHA256`: `1fd134ff0bf56f489e6875bcd3ffe5edb791418e75b58fa6bee7731b34661650`
- `PACKET_PATH`: `HARDENING_GATE6_PREFLIGHT_PACKET_R2.md`
- `GLM_EXIT_STATUS`: `3`
- `CLAUDE_EXIT_STATUS`: `2`
- `PROVIDER_EXECUTION`: `NO`
- `JUDGE_VERDICT_EXISTS`: `NO`
- `UTC_RECORDED`: `2026-07-28T00:37:19Z`

## Raw local boundary output

```text
GLM:
egress-gateway: blocked glm-zai:glm-5.2 egress: secret assignment
glm-zai: egress gateway blocked prompt before provider execution

Claude:
egress-gateway: blocked claude-opus-judge egress: secret assignment
claude-judge: egress gateway blocked the packet
```

The only assignment matching the local boundary rule is the candidate's
trial-local Restic-password path plus CSPRNG generation. It contains no static
secret, provider credential, or reusable value. The immutable candidate will
not be modified, and the egress gateway will not be weakened or bypassed.

The next packet may omit the raw candidate comparative source only because its
exact source hash and prior same-hash Gate 5 GLM/Claude GREEN receipts remain
included. The new Gate 6 packet must disclose that the judges are evaluating
the execution, lifecycle, isolation, pairing, and evidence design—not
re-adjudicating candidate source already frozen at Gate 5.

## R3 boundary result

- `PACKET_SHA256`: `95f00d6410a116b832aab94a3809f746cdb2e157795eca1344c8a9bd41d1fed6`
- `GLM_EXIT_STATUS`: `3`
- `CLAUDE_EXIT_STATUS`: `2`
- `PROVIDER_EXECUTION`: `NO`
- `JUDGE_VERDICT_EXISTS`: `NO`
- `UTC_RECORDED`: `2026-07-28T00:39:46Z`

```text
GLM:
egress-gateway: blocked glm-zai:glm-5.2 egress: provider token
glm-zai: egress gateway blocked prompt before provider execution

Claude:
egress-gateway: blocked claude-opus-judge egress: provider token
claude-judge: egress gateway blocked the packet
```

Local inspection against the reviewed gateway regex identified the sole match
as a historical Gate 5 prose label beginning with the GLM family prefix and
containing digits. It is not a provider token. The historical report remains
unchanged; the R4 packet excludes that redundant report and retains the Gate 5
status, checkpoint, judge receipt, and exact report hash through the source
binding. The egress rule is not changed or bypassed.
