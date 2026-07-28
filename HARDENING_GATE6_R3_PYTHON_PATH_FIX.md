# Hardening Gate 6 R3 — Resolved Python Tool Path Fix

- `STATUS`: `LOCAL_FIX_GREEN_AWAITING_INDEPENDENT_PREFLIGHT`
- `FAILED_ATTEMPT`: `iyr2mi9jf9p6p7; DELETED`
- `PYTHON_BINARY_SHA256`: `d6bca2b84e73c7775a0dd5e6a76899cfe4ee62863d7c8f88513811d1fda23f49`
- `OLD_RECORDED_PATH`: `/usr/bin/python3`
- `RESOLVED_RECORDED_PATH`: `/usr/bin/python3.10`
- `NEW_TOOL_PROVENANCE_SHA256`: `44fbfb5a5bab61f600e6931fe30be63577de6b7f1738fa66d469f3a58218983c`
- `NEW_WIRING_SHA256`: `145a8f7331b1a02a787799b91c9c531fdb7b5ef2fcefc207afa952a45fe805f9`
- `R3_FOCUSED_TESTS`: `6/6 PASS`
- `FULL_REGRESSION`: `273/273 PASS ACROSS 24 TEST FILES`
- `FULL_REGRESSION_RESULT_MANIFEST_SHA256`: `c0303fe8bbd7f297b3211d34c8fedafa977f3aa47bd6114af010383fbf7c85ad`
- `RUNPOD_RUNNING_INVENTORY`: `[]`
- `UTC_RECORDED`: `2026-07-28T02:47:52Z`

The validator intentionally resolves each supplied tool path before comparing
it to the provenance record. The image's `/usr/bin/python3` is a symlink to
`/usr/bin/python3.10`; attempts 01 and 02 directly verified the resolved binary
hash and version. The provenance and measured wiring now bind and pass the
resolved path. No binary bytes, model, candidate, verifier, comparison,
scenario, manifest, seccomp boundary, or acceptance rule changed.
