# Public export manifest R1

Status: `PUBLIC_RELEASE_VERIFIED_R3`

This branch is the sanitized public release. The immutable commit/tree binding
is held in the external R5 release packet; this manifest deliberately does not
hard-code its own commit and therefore cannot become self-stale after a normal
metadata commit.

## Provenance

- Export branch: `public-release-candidate-20260810`
- Public release identity: verify with `git rev-parse HEAD` and
  `git rev-parse HEAD^{tree}`; the exact values are recorded in the external
  R5 release packet and its binding.
- Export construction: explicit Git allowlist; historical audit/runtime paths
  were removed from this branch, not copied into a public repository.

## Retained surface

The export retains only:

- `LICENSE`, `README.md`, `pyproject.toml`, and `.gitignore`;
- `COCKROACH_AWS_CLAIMS_R2.md`, `DEVPOST_SUBMISSION_DRAFT.md`, and the local
  release/judge-path receipts;
- `SCENARIO_SURFACE_R3_CONTRACT.md`;
- `cockroach_kernel/`;
- `p4-verifier/`;
- `p7-recovery/`;
- `p9-cloud/`, including the corrected readback-aligned
  `deployment_manifest.json`;
- `skills/`, `examples/`, `live_lambda_handler.py`, and
  `test_live_lambda_handler.py`.

The retained tree contains no provider credentials, private keys, cookies,
HOME runtime state, raw RunPod evidence, raw judge transcripts, or client data.
The deployment readback is retained only as bounded evidence; the claims
manifest remains the authority for what may be stated publicly.

## Removed surface

Removed from this release branch:

- historical phase plans, judge packets, raw judge outputs, and human-gate
  receipts;
- RunPod lifecycle, soak, telemetry, and retrieved evidence trees;
- external-validity campaigns and disposable test archives;
- stale claim manifest R1 and the contradictory deployment manifest (replaced
  by the readback-aligned advisory manifest);
- provider credentials/configuration, local runtime state, and unrelated
  project artifacts.

## Verified public surfaces

- Repository: `https://github.com/kennethr1788-hub/cockroach-kernel/tree/public-release-candidate-20260810`
- Functional demo: `https://2et5iaygrpngfnesptlncnfjha0ixyjz.lambda-url.us-west-2.on.aws/demo/promote`
- Video: `https://youtu.be/vNYngdxJyS8`

## Verification record

An anonymous clone of this branch resolved to the exact commit/tree recorded in
the external R5 release packet. The clean-clone CLI path, public demo routes,
and public video were verified separately. Devpost field entry and final
submission remain human-controlled actions.
