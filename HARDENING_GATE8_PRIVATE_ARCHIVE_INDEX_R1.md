# Hardening Gate 8 Private Raw-Evidence Archive Index R1

- `ARCHIVE_CLASS`: `LOCAL_PRIVATE_RAW_EVIDENCE`
- `PUBLIC_RELEASE_AUTHORIZED`: `false`
- `GIT_TRACKED`: `false`
- `ARCHIVE_FILE`: `cockroach-kernel-private-raw-evidence-r1.tar`
- `ARCHIVE_BYTES`: `4065280`
- `ARCHIVE_SHA256`: `717636adba545315e13930e331b4024c44c787f0b130532ad3f827ba8388837d`
- `SOURCE_FILE_COUNT`: `613`
- `SOURCE_BYTES`: `3167428`
- `SOURCE_MANIFEST_SHA256`: `e0eef65352d5396137e3faa96bd5f55cfcbbba6f24e4eac135223fa89cdda58e`
- `ARCHIVE_RECEIPT_SHA256`: `2614ddd2d3a3d2febd57f7f82d091af51b140775172d7eaf19cdcbdf4a06f7b2`
- `BUILD_TOOL`: `hardening-gate8/build_private_archive.py`
- `VERIFY_TOOL`: `hardening-gate8/verify_private_archive.py`

The archive contains the raw evidence required to recompute every Gate 8
public claim, including the Gate 3 live workflow, P9 live CockroachDB/AWS/MCP
evidence, R4 fresh-context black-box evidence, Gate 6 measured comparison,
Gate 7 Run 6 hidden/workload/cloud evidence, and the preserved blocked
closeouts for Gate 7 Runs 3–5.

The tar member names are repository-relative. Every member is bound by the
canonical source manifest embedded inside the archive. Hidden inputs, raw
oracle material, provider endpoints, account details, and private runtime
evidence remain local and are intentionally absent from the sanitized public
subset.
