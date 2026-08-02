# PDH-3 R12 R6 CPU-affinity preflight packet R1

Status: `FROZEN_FOR_EXACT_HASH_GLM_5_2_REVIEW__NO_WORKER_AUTHORIZED`

UTC frozen: `2026-08-02T09:35:32Z`

Builder: `Codex / Icarus`

Decision requested: determine whether this prospective CPU-affinity amendment
is safe, fail-closed, sufficiently tested, and suitable for a future paid PF-4
attempt. This packet cannot authorize or launch a worker and cannot mark R6 or
the 24-hour campaign GREEN.

## 1. Authority and immutable prior failure

Current packet authorization:

- `PDH3_R12_R6_CPU_AFFINITY_AUTHORIZATION_20260802_R1.md`;
- SHA-256:
  `004ad82eaf53935eadb68f5117a6c9561bfccbd288c1da403f69f0a1e1280426`;
- operator authority is limited to a new compliant-shape or prospective
  CPU-affinity packet;
- paid provider mutation is explicitly outside this packet.

Prior replacement attempt:

- `PDH3_R12_R6_REPLACEMENT_ATTEMPT_01_BLOCKED_RECEIPT_20260802_R1.md`;
- SHA-256:
  `5dd09f3b5c914e410ac0cf6a983f0d28e04d2482404bbaa9d9ca334b1008483f`;
- returned shape: 32 vCPU / 125 GiB;
- blocker: raw shape failed 4 GiB per returned vCPU;
- main bundle uploaded: false;
- measured 24-hour clock started: false;
- Pod ID `zby5qthlswc7cy`: deleted, exact-ID absent, inventory empty;
- lifecycle: `TEARDOWN_GREEN`.

The earlier paid-lifecycle envelope and absolute dates are not silently reused.
A future launch needs fresh operator authority and current deadlines.

## 2. Prospective amendment

Amendment:

- `PDH3_R12_R6_CPU_AFFINITY_AMENDMENT_20260802_R1.md`.
- SHA-256:
  `eb66d5f8632686c015f79c45215b234fc362863f43fc515af87d6bab4c356e55`.

The amendment retains 4 GiB per effective CPU and computes:

```text
effective_vcpu_limit = min(provider_vcpus, floor(provider_memory_gib / 4))
```

For the observed 32-vCPU/125-GiB class, the only accepted cap is 31 CPUs.
The provider readback must still satisfy every non-CPU shape, cloud, image,
disk, volume, GPU, rate, and minimum-resource gate.

The mask is applied and read back through the Linux affinity API before PF-4
continues. The descendant chain is independently checked at the detached
observer PID, runner process, every CockroachDB startup PID, and every current
CockroachDB PID after node restart. Missing or mismatched proof is terminal.

## 3. Candidate and source bindings

Implementation commit:
`8465880b3753e700217231c59ad43f3362ecdd6d`

Branch: `evidence/external-validity-r1`

The unrelated untracked `heap_profiler/` path is excluded from source,
payload, tests, and packet evidence.

| File | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_cpu_affinity.py` | `87de9fb5d02fb1eee468601058086e34dfd4a553765b312672f59584e61dd707` |
| `post-dogfood/pdh3_r12_r6_launch_pf4.py` | `672d6205f510a5972f683688f0146f4f955daf88599a70c7ce9cf1e4eb7b8ae0` |
| `post-dogfood/pdh3_r12_r6_run_pf4.py` | `a01f93e9994ece2e4eadd5bd3c4b7b7121ae971973955ccd21ae153b28c1fc81` |
| `post-dogfood/pdh3_r12_remote_capability.py` | `ee271da20d92a1251e2804287dbcfd585c5441b4f1f61cf21bc5e62fd6d96d0d` |
| `post-dogfood/pdh3_r12_remote_launcher.py` | `f5fcc15188f4b7540567c8af30d90d21320bd89450f566c3c6e4921a6e5868f7` |
| `post-dogfood/pdh3_r12_remote_preflight.py` | `65c16b701869ab9f4a9e8a774b25c08d19333d6546c766588660c210c3022e44` |
| `post-dogfood/pdh3_r12_r6_run_pf2r_pf7.py` | `1f12a441543f5ed4528ca9afb1cc9f9dacffea48e434c71259e0e72736e7b2d6` |
| `post-dogfood/build_pdh3_scale_bundle.py` | `ca6fafa852a8cb62cf2c689d9607e4cd57c18930a65a35d87fb31a94dd482781` |
| `post-dogfood/test_pdh3_r12_cpu_affinity.py` | `aed261b92fd9a61968e04bd5248fe392a61b3b5f64cdb1914d31995506207af0` |
| `post-dogfood/test_pdh3_r12_r6_launch_pf4.py` | `ee2e057124d60dc2e79851ada74a48e3fbd83c1b17a466d3602677999bac153a` |
| `post-dogfood/test_pdh3_r12_remote_capability.py` | `0a4efe476f4d1268b6aad93214e6029e9d21c851014c33b67156fe196f87b950` |
| `post-dogfood/test_pdh3_r12_remote_launcher.py` | `98a5a7b27c4c8c272df0808bda6b8921b1621265d89467b2f3d30f2c995988c5` |
| `post-dogfood/test_pdh3_r12_remote_preflight.py` | `4054497549f2d8a9fd819dbeaf7a1c29bd323a9e5d87d7abfbe40df9a3af8515` |
| `post-dogfood/test_build_pdh3_scale_bundle.py` | `52ff86f852a5a9ae827196b78c9ce3b31133db3c130942008074fe1e99c14b41` |

## 4. Direct local verification

Focused verification:

- 58 `test_pdh3_r12*.py` tests: GREEN;
- plan derivation 32/125 → 31: GREEN;
- 16/188 → 16: GREEN;
- memory below 94 GiB and vCPU below 16: rejected;
- exact apply/readback logic: GREEN under injected Linux affinity interfaces;
- setter no-op and wrong child count: rejected;
- host readback, launcher arguments, and environment binding: GREEN;
- three live CockroachDB PIDs: accepted only with exact masks;
- dead node or child mismatch: rejected;
- changed Python modules compile: GREEN;
- `git diff --check`: GREEN.

The local tests do not claim an actual Linux/RunPod affinity application.

Two independent deterministic bundle builds:

- archive SHA-256:
  `1f5cdf99e09c9010a9f0544947a0920c0004357f3bcf2f2c2a02ffe1da6b85df`;
- archive bytes: `143989825`;
- bundle-receipt file SHA-256:
  `76c5e92d6e712a454424111bafa05e4592d1c5adee5e62948772695c0e696cd6`;
- embedded receipt SHA-256:
  `5c545f5a9f4db29e89a84eff6694d93c249140477c97dbe6a8fdb8f7c6075b31`;
- manifest SHA-256:
  `d8ff6e6a35878e5f31ffbe009f6069e1d051251a5128fc4090d86f2e6fd68020`;
- remote source-set SHA-256:
  `1f00bc9490445e688482f1c7699580da2f604e967298ee6276fbcbfb07605728`;
- host-only bindings SHA-256:
  `875215fcf69ac35c20f802fd6c3351a9273a7f144e8949bb47f66882377c206d`;
- archive verification SHA-256:
  `21d96dfd67c7c7ac492628a52d4a2ff1c947fed4612e1246c81a3a18e281a602`;
- both archives and both bundle receipts are byte-identical.

Each extracted copy compiled 35 Python files and passed all 13 bundled smoke
tests. The smoke receipts are not described as byte-identical because their
recorded temporary paths differ. They are reduced package-integrity evidence,
not remote scale or Linux-affinity evidence.

## 5. Preserved gates and prohibited reinterpretations

The target-scale cardinality, query mix, concurrency stages, latency limits,
growth limits, exactness checks, vector checks, fault/reconciliation semantics,
off-worker checkpointing, retrieval-before-delete, and teardown requirements
are unchanged.

Prohibited:

- accepting the 32/125 shape as 32 effective CPUs;
- weakening 4 GiB per effective CPU;
- using a label without kernel application/readback;
- falling back if Linux affinity is absent or denied;
- omitting detached-child, runner, initial-node, or post-restart-node proof;
- retuning after remote results;
- calling local mocks provider proof;
- reusing stale deadlines or launching from this packet.

## 6. Required future paid-PF-4 evidence

Before any future main-bundle upload, a freshly authorized worker must produce:

1. exact provider readback and a deterministic plan hash;
2. successful Linux `sched_setaffinity` and exact `sched_getaffinity` readback;
3. observed effective resource and 4-GiB ratio checks;
4. minimal PF-4 I/O, network-observer, accounting, and residue GREEN;
5. a lifecycle guard bound to the exact Pod ID and fresh deadlines;
6. preserved raw streams and mandatory deletion on any failure.

PF-2R through PF-7 must then publish the parent, cluster-start, and post-restart
affinity receipts. Until those exist, the correct state is
`CPU_AFFINITY_PACKET_GREEN_PENDING_PAID_PF4_AUTHORIZATION`, not R6 GREEN.

## 7. Independent-review request

GLM 5.2 receives this exact packet only as sanitized, non-authoring input. It
has no shell, write, repository, credential, browser, provider, or approval
authority.

Return exactly one structured verdict:

```json
{
  "packet_sha256": "<exact hash>",
  "judge": "GLM 5.2",
  "verdict": "GREEN|NOT_GREEN|INSUFFICIENT_EVIDENCE",
  "affinity_math": "GREEN|NOT_GREEN",
  "kernel_enforcement": "GREEN|NOT_GREEN",
  "inheritance_proof": "GREEN|NOT_GREEN",
  "fail_closed_semantics": "GREEN|NOT_GREEN",
  "threshold_preservation": "GREEN|NOT_GREEN",
  "evidence_classification": "GREEN|NOT_GREEN",
  "authority_boundary": "GREEN|NOT_GREEN",
  "findings": []
}
```

Any hash mismatch, missing dimension, tool request, implementation direction,
or attempt to authorize a worker invalidates the review.
