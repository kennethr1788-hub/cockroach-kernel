# Public export scan classification R1

The sanitized export was scanned with `gitleaks dir` and `detect-secrets`.

- `gitleaks dir`: no leaks found.
- `detect-secrets`: 13 `Hex High Entropy String` findings.

All 13 findings are fixed synthetic or provenance hashes:

- `p7-recovery/fixtures/*.json`: deterministic synthetic receipt, manifest,
  trajectory, and feature-content SHA-256 values;
- `p9-cloud/live_deployment_readback.json`: the deployed Lambda archive
  SHA-256, not a credential or token.

The scan found no API key, password, cookie, private key, OAuth grant, account
credential, or connection string. The classification is evidence for the
export gate; it does not suppress scanning rules or convert an unresolved
finding into a claim of cleanliness.
