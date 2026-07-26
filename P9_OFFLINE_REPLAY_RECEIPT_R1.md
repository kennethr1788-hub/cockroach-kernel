# P9 Offline Replay Receipt R1

- UTC: `2026-07-26T13:51:26Z`
- PARENT_COMMIT: `3263e12bb578048cf95856881540295677db9e8a`
- HARNESS_SHA256: `b297cb126c502afa9ba685fbd9f8c9701ae1c6f3c5daa8305ff671ee7105aa3e`
- TEST_SHA256: `8c8264fe95661249edece97087226b201a47db9c3e3f2cb9d7ab3807f0ce085a`
- CLEAN_ROOT_1_RESULT_SHA256: `a6a331944a7950ee04e4ef51e867d62053bb9ba4cae9270af080ac49f34926bd`
- CLEAN_ROOT_2_RESULT_SHA256: `a6a331944a7950ee04e4ef51e867d62053bb9ba4cae9270af080ac49f34926bd`
- RESULT: `GREEN`

Both trials ran from distinct generated project-local roots with distinct empty
fake HOME directories. Their canonical output bytes matched exactly.

Observed deterministic result:

- Lambda delivery: `ACCEPTED`, status `ADVISORY`;
- changefeed projection: `PROJECTED`, cursor `1`;
- Managed MCP mock: one bounded read-only row;
- tampered candidate: local P4 verdict `REFUSE`, reason `HASH_MISMATCH`;
- valid candidate: local P4 verdict `PROMOTE`, reason `VERIFIED`;
- fresh-context capsule: `FRESH_CONTEXT_PASS`;
- internal result hash:
  `44cf46d6f65b359f08ddec57ccf708a215f974ee03a2015435fef6507be4e962`.

The generated roots were deleted after comparison. Post-trial scans found no
matching process or temporary root. This is keyless local mock/replay evidence,
not live Lambda, CockroachDB Cloud, changefeed, or Managed MCP evidence.
