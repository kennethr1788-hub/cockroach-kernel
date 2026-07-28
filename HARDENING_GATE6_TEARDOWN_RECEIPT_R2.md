# Hardening Gate 6 — Teardown Receipt R2

- `STATUS`: `TEARDOWN_GREEN_FOR_BLOCKED_ATTEMPT`
- `POD_ID`: `2sh4lx37f6r73g`
- `EXACT_ID_LOOKUP`: `ABSENT`
- `RUNNING_INVENTORY_SHA256`: `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`
- `ALL_STATUS_INVENTORY_SHA256`: `a760ba1a9f93166d740aca8443e55a56c4526ed0d91e98338f787435d92f296f`
- `CAMPAIGN_RUNNING_COUNT`: `0`
- `CAMPAIGN_ACTIVE_ALL_STATUS_COUNT`: `0`
- `LOCAL_CAMPAIGN_PROCESS_COUNT`: `0`
- `GITLEAKS_FINDINGS`: `0`
- `DETECT_SECRETS_FINDINGS`: `0`
- `RAW_PROVIDER_FILES_WITH_LOCAL_IDENTITY_PATH_LABELS`: `2`
- `PRIVATE_IDENTITY_BYTES_READ_OR_COMMITTED`: `no`
- `HOME_RUNTIME_MUTATED`: `no`
- `UTC_RECORDED`: `2026-07-28T00:58:13Z`

The two private runtime files containing local identity-path labels are the raw
provider Pod and SSH metadata responses. They remain under ignored private
evidence custody, contain no copied identity bytes, and are represented publicly
only by hashes. No runtime or evidence file was promoted to HOME.
