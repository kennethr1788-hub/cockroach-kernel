# Hardening Gate 4/5 — Sanitized Portability Repair Judge Packet R3

## Judge boundary

This is a sanitized, hash-bound verdict surface. The builder is not a judge.
Review the Gate 4 R2 amendment and Gate 5 R2 evidence candidate together.
Return only the required verdict object. Do not provide code, patches,
implementation plans, tool calls, deployment actions, prioritization, or
credential requests. You have no shell, filesystem, browser, network,
credential, implementation, or public-action authority.

- `TARGET_GATE_4`: `HARDENING_4_BASELINE_PROTOCOL_R2_GREEN`
- `TARGET_GATE_5`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_IMPLEMENTATION_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `CANDIDATE_PARENT_COMMIT`: `381e74fa5f6c1d55a743b6ccabf4c4674618eee2`
- `CANDIDATE_DIFF_SHA256`: `662980134ae0ab7516478b5247588940d21e4d2b609806407e72be0760b6231e`
- `PARENT_PROTOCOL_SHA256`: `12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`
- `AMENDED_PROTOCOL_SHA256`: `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `HARDENING_PLAN_SHA256`: `1ce953127138a35bd9588d686bbefefc0b012e8f2188a8fea736842030d57310`

The packet hash is supplied out of band and must be returned exactly.

## Required review questions

1. Does R2 eliminate platform-dependent common source bytes without changing
   scenario semantics or giving one method different information?
2. Does runtime-attested Python/Git provenance prevent false cross-platform
   identity while allowing Gate 6 to freeze exact Linux values before launch?
3. Does the two-hash Restic allowlist accept only the official 0.19.0 Darwin
   arm64 and Linux amd64 artifacts and bind each hash to its version output?
4. Are preflight and measured evidence modes explicit, canonical, disjoint,
   and fail-closed against Darwin or placeholder-candidate mislabeling?
5. Does the receipt validator require the correct provenance for every method?
6. Are the R1 fairness, pairing, methods, scenarios, metrics, timeout,
   no-tuning, raw-reporting, authority, and limitation clauses preserved?
7. Is the R2 candidate ready to be frozen for a later independently reviewed
   Linux Gate 6 preflight? Absence of Linux measured evidence is not a Gate 5
   defect and must not be converted into a success claim.

## Protocol amendment under review

R1 remains incorporated at exact SHA-256
`12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`.
R2 changes only these clauses:

- common executable bytes are exactly `["python3","tests/check.py"]`;
- the resolved isolated-path Python executable is versioned and hashed in all
  receipts;
- exact configured Git is used, versioned, and hashed instead of claiming a
  Darwin identity on Linux;
- Restic is accepted only at Darwin hash `f6c965a0...` with Darwin version
  output or Linux hash `ae7fe58a...` with Linux version output;
- receipt schema v2 requires `evidence_mode` and `runtime_platform`;
- `PREFLIGHT` requires the three existing preflight limitations;
- `MEASURED_GATE6` requires four disclosed synthetic/generic-compute
  limitations and fails closed unless runtime is Linux, commit is 40 lowercase
  hexadecimal characters, and campaign ID starts `ck-gate6-`;
- post-execution receipt relabeling remains forbidden;
- all R1 fairness and authority clauses remain binding.

The full amendment is hash-bound at
`a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`.

## Candidate behavior under review

Candidate source SHA-256 values:

```text
comparative.py=f9fa1d5ce7076c8fa96a1b5d9053f50c58902c557f1d6fbf340c0c356d12a1ec
run_smoke.py=91ad388ef6d4972cc2c6a248dd147eb1d93a38515a2c6d645ccb395b28fb3de6
test_comparative.py=605b0346a08d7181b563f29eb819dada0618fe7c980cf372d60435ca2d46c50f
verifier.py=a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40
seeds.json=e2116b9bbe68671072cc6419e494d722fb4e285493338421ea58a806676c6f6d
heldout_contract.py=b5de48cf64cddb505238b835d026fad6ed39917c129bf3b4194f430da1f69801
```

Load-bearing logic, rendered exactly in meaning:

```text
EVIDENCE_MODES = PREFLIGHT | MEASURED_GATE6
RESTIC_PROVENANCE[darwin_hash] = exact Darwin 0.19.0 version
RESTIC_PROVENANCE[linux_hash] = exact Linux 0.19.0 version
public.executable_command = [python3, tests/check.py]

PREFLIGHT limitations =
  LOCAL_SYNTHETIC_PREFLIGHT; NOT_LIVE_AWS; NOT_GATE6_MEASURED_EVIDENCE

MEASURED_GATE6 limitations =
  SYNTHETIC_PAIRED_COMPARATIVE; NOT_LIVE_AWS; NOT_PRODUCT_SCALE;
  RUNPOD_GENERIC_COMPUTE

if measured and platform != Linux: block
if measured and candidate_commit is not exactly 40 lowercase hex: block
if measured and campaign_id does not start ck-gate6-: block

each adapter records resolved Python version/hash
each Git-bearing adapter uses and records one configured Git version/hash
Restic verifies observed binary hash and matching version before repository init
validator requires the exact tool key set per method and valid SHA-256 values
```

No candidate code receives expected hidden result data, another method's
custody, credentials, AWS/Cockroach state, model output, or post-result tuning.
The unchanged P4 verifier remains the only product promotion/refusal authority.

## Mechanical evidence

- Candidate commit: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`.
- Compile: `PASS`.
- Comparative contract tests: `7/7 PASS`.
- Broader non-live regressions: `264/264 PASS`.
- Exact-candidate smoke receipts: `18/18 VALID`.
- Semantic repeats: `3/3 PASS`.
- Pair source/event/loss hash matches: `6/6` for each category.
- Python provenance: `18/18`.
- Network-deny probe: `BLOCKED`.
- Cleanup: `18/18`; residue bytes: `0`.
- Internal summary SHA-256:
  `781531c80ce1415ca208c4f2119cb57be660db73276f556610f1b57dd83b7c1b`.
- Raw summary SHA-256:
  `f79137a47eac4a634044f8b5dec23e4e93c1a94e163b0343190a14c5aa6998d3`.
- Raw evidence manifest SHA-256:
  `f88a0d6f86d4f3e1b5c96d85f64e845da47a4790ae33b9d14838f54e36e1b487`.
- Git diff check: `PASS`; Gitleaks: `NO_LEAKS`; detect-secrets:
  `ONLY_UNVERIFIED_SHA256_TEST_OR_PROVENANCE_VALUES`.
- RunPod workers created: `0`; public actions: `0`.

The exact Linux Restic archive and binary hashes were reverified locally. The
Linux binary is not executed on Darwin. Gate 6 must execute it on the reviewed
Linux worker, attest Linux Git/Python/Restic values, prove network denial, and
obtain the separately required Gate 6 preflight verdicts before measurement.

## Known limitations

- This is a Gate 5 Darwin preflight, not Linux measured evidence.
- No 54-row campaign has run.
- Dynamic Git/Python provenance is not an open allowlist: Gate 6 must freeze
  the one exact observed Linux tuple in its preflight packet and receipts must
  match it.
- The comparator is local Restic at every completed checkpoint; it is not
  off-site backup or interruption-during-capture evidence.
- The experiment remains small, synthetic, author-designed, and unsuitable
  for population or global-superiority claims.
- Historical R1 evidence remains historical and cannot be relabeled R2.

## Required verdict schema

Return exactly one JSON object:

```json
{"verdict":"GREEN|NOT_GREEN|BLOCKED","packet_sha256":"<exact supplied hash>","candidate_commit":"8718fbecc2b145ff36ce8c3ed655e92b5906aeab","gate4":"GREEN|NOT_GREEN|BLOCKED","gate5":"GREEN|NOT_GREEN|BLOCKED","findings":[{"severity":"CRITICAL|HIGH|MEDIUM|LOW","acceptance_condition":"<condition>","evidence":"<packet evidence>"}],"summary":"<concise verdict>"}
```

`GREEN` is valid only if both `gate4` and `gate5` are `GREEN` and no critical
or high finding remains. Do not infer Gate 6 measured success.
