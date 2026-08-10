# Public export manifest R1

Status: `SANITIZED_PRIVATE_RELEASE_CANDIDATE`

This branch is a release candidate only. It has not been pushed or made public.

## Provenance

- Source branch: `submission-candidate-20260810`
- Source candidate head: `577ba6f11686a386c48ffc878686f31a35f63708`
- Export branch: `public-release-candidate-20260810`
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

## Verification required before public action

From a fresh clone of this branch, run the commands in
`RELEASE_JUDGE_PATH_CHECK_R1.md`, then perform a secret/private-path scan and
an anonymous clone check. Public visibility, video publication, and Devpost
submission remain separate gates.
