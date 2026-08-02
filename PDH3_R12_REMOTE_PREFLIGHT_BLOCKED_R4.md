# PDH-3 R12 remote preflight blocked receipt R4

Status: `PDH3_R12_PREFLIGHT_BLOCKED`

- blocker: `RUNPOD_CAPACITY_UNAVAILABLE_SINGLE_ATTEMPT_CONSUMED`
- failure stage: `PF4_CREATE`
- last GREEN gate: `R12_R4_SAME_HASH_GLM_GREEN`
- packet SHA-256: `63d9558e8a42b9813d5baa4b6caba0e931f3a185fa51eb502f2f29220b082e97`
- threshold amendment SHA-256: `012716a1a377a938bc8ca20b84631b6450f407c635748929d91db59ff675e2e1`
- implementation commit at attempt: `2fbc38fc651504b6bdf6f5aa5e70e93a6cba8523`
- creation request UTC: `2026-08-02T06:47:49Z`
- closeout verification UTC: `2026-08-02T06:48:28Z`
- provider error: `This machine does not have the resources to deploy your pod. Please try a different machine`
- provider Pod ID assigned: `false`
- worker created: `false`
- upload began: `false`
- PF4 capability execution began: `false`
- final 24-hour measured campaign began: `false`
- active provider inventory after failure: `[]`
- local orchestrator, SSH, transfer, lifecycle-guard, and workload processes remaining: `0`
- exact attributable provider charge: `unavailable`; no worker record was returned
- current provider spend rate after failure: `$0.002/hour` (sanitized provider readback; not attributed to this attempt)
- retries authorized by R4: `0`

## Evidence hashes

- empty create stdout SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- create stderr SHA-256: `27677b4fd78be9bc20fa3157a4ecd68966d8d036b2a4718c3b0c2bcbe4159749`
- orchestrator blocked receipt SHA-256: `f0303eb7a83ff2775b5b564ada389c673882137312a8dba5dff4fc6b9c638e8a`
- precreate active-inventory receipt SHA-256: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- sanitized precreate account receipt SHA-256: `a33ba8f8d851d13c21aa1d5f9f8114c8ab4002b4cd7b2658f22318442b38f574`

## Resume boundary

The R4 single creation attempt is consumed even though RunPod did not assign a
Pod ID. No automatic retry is permitted. Resume only after Kenneth explicitly
authorizes a fresh creation attempt and a new same-hash packet binds current
inventory, worker choice, timing, price, cost ceiling, and teardown deadlines.
The final 24-hour measured campaign remains separately unauthorized.
