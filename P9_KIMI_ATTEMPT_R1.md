# P9 Kimi Attempt R1

- RESULT: `BLOCKED_BEFORE_MODEL_EXECUTION`
- FAILURE: `managed K3 max-effort contract missing`
- SOURCE_WRAPPER_SHA256: `d21dc965c06729079571b26389afa00f6d731f35532f4ec0752e10d3712468ee`
- OBSERVED_MODEL: `kimi-code/k3`
- OBSERVED_DEFAULT_EFFORT: `high`
- OBSERVED_SUPPORTED_EFFORTS: `low`, `high`, `max`
- REPOSITORY_MUTATION: none
- HOME_MUTATION: none
- CREDENTIAL_EXTRACTION: none

The canonical wrapper rejected the managed model before execution because it required
the source HOME configuration's default effort to equal `max`, even though the same
model entry explicitly supports `max`. This is wrapper/configuration drift, not a
model execution failure.

The proposed correction is project-local and fail-closed: verify the exact canonical
wrapper hash, require `max` in the declared supported efforts, and set `default_effort`
to `max` only in the isolated copied runtime configuration. The canonical HOME wrapper,
HOME Kimi configuration, and OAuth credential files remain unmodified.
