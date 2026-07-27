# Hardening Gate 5 — Runtime and Evidence Boundaries R1

- Comparative mode is local, deterministic, synthetic, and network denied.
- Every execution has a fresh generated root, trial-local HOME, no inherited
  AWS/Cockroach credentials, no SSH agent, and no shared cache or repository.
- Darwin preflight runs under `/usr/bin/sandbox-exec` with a fixed
  `(deny network*)` profile and a forbidden-egress probe.
- Linux measured work is frozen to `unshare --user --map-root-user --net
  --mount-proc`; its availability and forbidden-egress probe are mandatory
  RunPod preflight checks before any measured Gate 6 execution.
- Product custody, Git bare remote, and Restic repository receive equivalent
  survival scope: outside the disposable workspace but inside the trial root.
- The product uses the unchanged P4 deterministic verifier. No model, AWS
  result, baseline adapter, or scorer can promote or refuse a candidate.
- Private evidence: raw S3 chains, provider/account metadata, raw live logs,
  private lifecycle receipts, and any credential-adjacent artifacts.
- Public-safe evidence: sanitized canonical comparative receipts, aggregate
  hashes, stable reason codes, dependency/license manifest, limitations, and
  claim-to-evidence mappings after a separate Gate 8 scan.
- Forbidden in all evidence: credential bytes, passwords, cookies, OAuth
  grants, raw environment dumps, absolute HOME paths, client/private data, and
  expected hidden Gate 7 vector material before candidate freeze.
