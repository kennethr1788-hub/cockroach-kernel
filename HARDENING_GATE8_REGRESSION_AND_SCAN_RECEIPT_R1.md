# Hardening Gate 8 Regression and Scan Receipt R1

- `UTC_VERIFIED`: `2026-07-30T06:44:28Z`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `GATE7_SUITE`: `24_OF_24_PASS`
- `GATE7_TEST_LOG_SHA256`: `75d809ff6571631f99e45fa71d378f18cc3375a1c48bd992118b0c2830937347`
- `P9_CLOUD_CONTRACT_SUITE`: `8_OF_8_PASS`
- `P9_TEST_LOG_SHA256`: `bb00d194408b67eb166a709ac7e747896d41b304354f91085d99c3cb5b58b97a`
- `S3_PROTOCOL_HARDENING_SUITE`: `19_OF_19_PASS`
- `S3_TEST_LOG_SHA256`: `975e49b71eef9f5c71fc323e673fbd647825d0fa3d546683ac2681ce30bf11ad`
- `GITLEAKS_PUBLIC_SUBSET`: `GREEN_NO_LEAKS`
- `GITLEAKS_LOG_SHA256`: `027b04a49d38536a8fafc4c647430a4f70db262c82fdd21565a2856d8fa73c19`
- `DETECT_SECRETS_PUBLIC_SUBSET`: `GREEN_ZERO_FINDINGS`
- `DETECT_SECRETS_LOG_SHA256`: `ce405ef9038ee9705c6ec5e88870a4ef0e23ebbf3d8a3e371e8567e3887653ff`
- `MECHANICAL_PACKAGE_STATUS`: `GREEN`
- `MECHANICAL_RECEIPT_SHA256`: `84fc994692c8df0ec5c66d0cd0b98e35b9b59e8aa0fad00028c8200e7f431e97`
- `PRIVATE_ARCHIVE_VERIFICATION`: `GREEN_613_OF_613`

The first diagnostic command used repository-wide `unittest discover`. That
command is not a valid project test surface because separate suites require
their own module roots; it produced import-path errors and is not treated as a
product failure or as passing evidence. The three exact frozen regression
commands above were then rerun and passed without product changes.

The test and scan logs remain in the ignored local Gate 8 runtime. This receipt
binds their hashes without publishing raw local runtime material.
