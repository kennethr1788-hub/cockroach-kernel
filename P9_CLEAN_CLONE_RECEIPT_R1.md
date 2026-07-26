# P9 Clean Clone Receipt R1

- UTC: `2026-07-26T13:52:36Z`
- IMPLEMENTATION_COMMIT: `c8cc768ecec3d6faea7cf2fc3b485e276e445e86`
- TRIAL_COUNT: `2`
- TESTS_PER_TRIAL: `95`
- REPLAY_SHA256_TRIAL_1: `a6a331944a7950ee04e4ef51e867d62053bb9ba4cae9270af080ac49f34926bd`
- REPLAY_SHA256_TRIAL_2: `a6a331944a7950ee04e4ef51e867d62053bb9ba4cae9270af080ac49f34926bd`
- RESULT: `GREEN`

Each trial used a separate `--no-hardlinks` local clone and ran the full P9
unittest suite, Python compilation, and keyless replay. Commit-only project
scans found no secret, private absolute path, symlink, socket, device, FIFO, or
other special file in `p9-cloud`.

`gitleaks` and `detect-secrets` found no leak in the P9 surface. Both generated
clone roots were deleted. Post-trial scans found no matching process or root.

An additional host test ran the same 95 tests and replay with Python `3.12.13`;
the internal replay result hash remained
`44cf46d6f65b359f08ddec57ccf708a215f974ee03a2015435fef6507be4e962`.

This is local clean-clone evidence only. The cloud integration remains blocked.
