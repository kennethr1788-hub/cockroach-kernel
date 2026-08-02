# PDH-3 R12 R6 host credential binding required R1

Status: `HOST_CREDENTIAL_BINDING_REQUIRED__NO_WORKER_CREATED`

Verified UTC: `2026-08-02T08:02:19Z`

- frozen packet SHA-256:
  `29ffc52144045a12afdea754a5183c9c39d8739d3b936547b00e74b9906e8fbb`;
- exact-packet direct GLM 5.2 verdict: `GREEN`;
- runtime config SHA-256:
  `e7999d50ef67c49393c28a5954a56156d8ab97493daf5b7e44fbfd05fae8c129`;
- authenticated RunPod CLI: `GREEN`;
- current Pod inventory: `[]`;
- `RUNPOD_API_KEY` in the current task process environment: `ABSENT`;
- worker created: `false`;
- paid mutation performed: `false`.

The repaired controller checks the host-only environment binding before every
provider mutation. The authenticated CLI config is not extracted, copied, or
committed. Kenneth must place the existing key into the detached controller's
environment through hidden terminal input. The key must not be pasted into
Codex, written to a file, placed in argv, printed, or committed.

Run this exact block in macOS Terminal. Input is hidden. The command may be
started before the frozen `2026-08-02T08:20:00Z` launch-window start; the
controller will wait. It will fail closed after `2026-08-02T09:05:00Z`.

```zsh
cd /Users/kennethruedas/sandbox/cockroach-kernel-build-20260725

read -s "PDH3_R12_R6_KEY?RunPod API key (hidden): "
echo

RUNPOD_API_KEY="$PDH3_R12_R6_KEY" \
PDH3_R12_R6_CONFIG="$PWD/.pdh3-runtime/r12-preflight/r6-config-20260802b.json" \
/usr/bin/nohup /usr/bin/caffeinate -dimsu /usr/bin/python3 \
  "$PWD/post-dogfood/pdh3_r12_r6_orchestrator.py" \
  > "$PWD/.pdh3-runtime/r12-preflight/r6-20260802b-orchestrator.log" 2>&1 &

print -r -- $! > "$PWD/.pdh3-runtime/r12-preflight/r6-20260802b-orchestrator.pid"
unset PDH3_R12_R6_KEY
echo "R6 controller staged; secret unset from the interactive shell."
```

After Kenneth reports `Done`, Icarus must verify the PID, packet/config hashes,
first controller state, provider inventory, and lifecycle guard before
reporting that a worker is actually running.
