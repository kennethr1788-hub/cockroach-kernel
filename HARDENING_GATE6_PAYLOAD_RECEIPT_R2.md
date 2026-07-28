# Hardening Gate 6 — Payload Receipt R2

- `STATUS`: `PAYLOAD_GREEN_FOR_PREFLIGHT_REVIEW`
- `EXECUTION_REVISION`: `R2`
- `SOURCE_COMMIT`: `3558ce481d609ccf755f57758b74cd6e67305dad`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `PAYLOAD_PATH_LOCAL_PRIVATE`: `.hardening-runtime/gate6-r2/ck-gate6-r2-payload.tar.gz`
- `PAYLOAD_BYTES`: `14224525`
- `PAYLOAD_SHA256`: `d9b98d5c66596501f2f46a7e87f54994518325b1acacca1768561652772cf283`
- `PAYLOAD_TREE_MANIFEST_SHA256`: `a686863a6e413b632de1b8965865879f19c910081d63ddc239a18acf25dbac8d`
- `FILE_COUNT_EXCLUDING_TREE_MANIFEST`: `11`
- `UTC_RECORDED`: `2026-07-28T00:28:00Z`

## Included

- Gate 4 R1 plus R2 protocols;
- exact 54-row R2 execution manifest and execution plan;
- public-safe Gate 3 hash reference;
- frozen Linux tool provenance;
- exact candidate comparative source and deterministic verifier;
- Gate 6 R2 orchestration;
- official Restic 0.19.0 Linux amd64 binary;
- hash-bound Ubuntu Jammy Git amd64 package.

## Excluded

Credentials, OAuth or AWS sessions, CockroachDB secrets, SSH material, HOME
state, private/raw Gate 3 evidence, provider responses, unrelated source,
sealed Gate 7 vectors, client data, persistent volumes, and cloud configuration.

## Mechanical verification

- archive extraction: `PASS`;
- all `11/11` tree-manifest entries: `PASS`;
- Gitleaks: `0` findings;
- detect-secrets: `0` findings;
- private-path scan: no private path, account identifier, credential value, or
  key material. The `14` lexical matches are policy descriptions and the
  candidate's trial-local CSPRNG Restic-password implementation; no secret
  bytes exist before each isolated trial creates and later destroys them.
- Gitleaks output SHA-256:
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`.
- detect-secrets output SHA-256:
  `bfe885a805a694d3c8a6a74fe2d375caf6f7d833d07574c62adf11079a65a29f`. <!-- gitleaks:allow -->
- classified lexical scan SHA-256:
  `3729241caa8b3708ee109a2aef1c6af04dc5a757dca7790dba67a538a2b7890f`.

This receipt authorizes only independent preflight review. Upload remains
forbidden until the same-hash required quorum is GREEN and a returned worker
passes the reviewed provider envelope.
