# Public export manifest R1

Status: `PUBLIC_RELEASE_VERIFIED_R2`

This branch is the sanitized public release. Historical R1 provenance fields
are superseded by the immutable release identity below.

## Provenance

- Export branch: `public-release-candidate-20260810`
- Public release commit: `3053166d2dc2909e7329e35e5621bffa2907f23e`
- Public release tree: `0d25af55cde4fbf58789c520293156c656e65d29`
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

An anonymous clone of this branch resolved to the release commit and tree
above. The clean-clone CLI path, public demo routes, and public video were
verified separately. Devpost field entry and final submission remain
human-controlled actions.
