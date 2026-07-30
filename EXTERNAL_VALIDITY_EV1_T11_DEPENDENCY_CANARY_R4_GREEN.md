# EV1-T11 Dependency Canary R4 — Green

- `STATUS`: `EV1_T11_DEPENDENCY_CANARY_R4_GREEN`
- `SOURCE_COMMIT`: `ee6862f7d65d24d4de11eda8306d29356873b529`
- `CANARY_RECEIPT_FILE_SHA256`: `e9ec4056a738bfad2b6a1d8a6eb5d82ec30a7dcd843fc480a312f2a39bc50f3a`
- `CANARY_RECEIPT_SHA256`: `d0db196763cab9888086191c0260543bd447cd0bde55d672fc4bc26927ef0476`
- `DEPENDENCY_MANIFEST_SHA256`: `bda7fc8f96d452960e7174cc6b84f05708f763ebf2e10dbdd40a1eca87b06dbe`
- `DECLARED_LINKS_SHA256`: `aa1ad61037ef49847a9de65f3c92ce2d91f9fe989b202f25f88d720e0e6490b8`
- `PNPM_TEST_LOG_SHA256`: `2854da45e864226ca19a7d687ecc3d72bba7124820c56c4b0babb1e3c5aa8581`
- `TEST_FILES`: `84_OF_84_PASS`
- `TESTS`: `1475_PASS; 7_SKIP; 0_FAIL`
- `NETWORK`: `DENIED_SEATBELT`
- `INSTALL_COMMAND_EXECUTED`: `NO`
- `LIFECYCLE_SCRIPT_EXECUTED`: `NO`
- `BROKEN_OR_ESCAPE_LINKS`: `0`
- `TEMPORARY_ROOT`: `ABSENT_AFTER_TEST`
- `TASK_WORK_STARTED`: `NO`

The surviving dependency bytes came from the failed EV1-T09 implicit-install
attempt and remain ineligible as EV1-T09 acceptance evidence. R4 requalified
those exact bytes only as an offline T11 test runtime. It copy-on-write cloned
the tree into a fresh exact-commit source export and reconstructed 36 links from
declared package manifests using pnpm's actual workspace, root-direct, and
private-hoist topology. No install, lifecycle script, network access, source
mutation, or product-candidate mutation occurred.

R1 is preserved as unevaluable. R2 is preserved as a three-suite dependency
topology failure. R3 is preserved as a pre-test resolver classification failure.
Only R4 is eligible as the T11 runtime prerequisite.
