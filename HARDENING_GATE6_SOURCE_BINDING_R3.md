# Hardening Gate 6 — Source and Policy Binding R3

- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `COMPARATIVE_SHA256`: `f9fa1d5ce7076c8fa96a1b5d9053f50c58902c557f1d6fbf340c0c356d12a1ec`
- `VERIFIER_SHA256`: `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`
- `GATE4_PROTOCOL_R2_SHA256`: `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`
- `LINUX_TOOL_PROVENANCE_R3_SHA256`: `6d1def307f36102e54778a6c7ef240ebb0375ed4c4aaf6536a33cd194b54eb3b`
- `SECCOMP_LAUNCHER_SHA256`: `64a4c1d7e68238dbeb4959a8bc52cba0b0aaa5499131a145e0b31d5cb8c52ab3`
- `R3_RUNNER_SHA256`: `9ad46f17706ac1ec931ae6084a41faac98802561190efa3031e7595eff13c2f3`
- `R3_MANIFEST_FILE_SHA256`: `a4c7c12c135475b712199916a8257b90543a1dd2b346e15bb6519f1d9ec80d3d`
- `R3_MANIFEST_EMBEDDED_SHA256`: `1e73682e0eb880c95f5826d731cf6c1b6fe1f61e342bfb2d36c7fd1d3600d711`
- `LIFECYCLE_GUARD_SHA256`: `4644aa756f47c3d53b82c239657ce22605d4a9caab3e6a8651c4f459d95c6f0c`
- `RUNPOD_POLICY_SHA256`: `6dfe19f3fd8be6c86f864190f633ec6052ce0276cad94fa76386b73a19031694`
- `RUNPODCTL_SHA256`: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`

`git diff` from the immutable candidate commit across the comparative source,
deterministic verifier, and scenario seeds is empty. R3 adds only orchestration,
isolation, lifecycle, and evidence infrastructure. The product candidate and
comparison semantics are unchanged.
