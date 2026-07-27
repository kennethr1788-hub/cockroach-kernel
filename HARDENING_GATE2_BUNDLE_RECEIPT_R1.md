# Hardening Gate 2 Bundle Receipt R1

- `UTC_RECORDED`: `2026-07-27T17:39:41Z`
- `RESULT`: `GREEN`
- `PYTHON`: `3.12.13`
- `LOCAL_CLI_HTTP_TESTS`: `12/12 PASS`
- `BUNDLE_SMOKE`: `GREEN`
- `ARCHIVE`: `.hardening-runtime/gate2-bundle/ck-hardening-demo.zip`
- `ARCHIVE_SHA256`: `1fbcaf5b79a648653a26669b224d78f50239380c0318506c01a5a2df21df3f58`
- `ARCHIVE_BYTES`: `460879`
- `ARCHIVE_FILE_COUNT`: `109`
- `MANIFEST_SHA256`: `6a78d87f920deb277e205cd9d113947e4871bab43aab0153fdd9a1644ed3bbbc`
- `HANDLER`: `cockroach_kernel.http_api.lambda_handler`
- `HOME_PIP_CACHE_RESIDUE`: `0`
- `AWS_MUTATIONS`: `0`
- `COCKROACHDB_MUTATIONS`: `0`

The first build attempt exposed a missing path-based verifier copy and wrote one
generated project wheel plus its origin metadata into pip's user cache. No
cloud mutation occurred. The two exact generated cache files were unlinked and
their exact now-empty build cache directory removed. The builder now disables
pip's user cache and copies only the required verifier source into the bundle.
The rebuilt installed tree passed promotion and refusal smoke checks.

Installed distributions recorded by the canonical bundle manifest:

- `asn1crypto==1.5.1`
- `cockroach-kernel==0.1.0`
- `pg8000==1.31.5`
- `python-dateutil==2.9.0.post0`
- `scramp==1.4.15`
- `six==1.17.0`

This receipt proves only the local deployment bundle. It does not prove the
live public demo or Gate 2 GREEN.
