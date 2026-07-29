# Hardening Gate 7 Run 3 AWS Refresh Required R1

- UTC: `2026-07-29T03:03:25Z`
- phase: `HARDENING_7_RUN3_PREFLIGHT_GREEN`
- current commit: `02da56305e146cd555116e9a942e6d3c2b1f68c6`
- product candidate: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- preflight packet SHA-256: `5274e5f8c35383ff26f283764ba64385c3e3e5d5711da07a9b20735c6ccba7c9`
- preflight judges: `GLM_5_2_GREEN; AGY_1_1_8_GREEN; SAME_HASH; RECUSAL_CLEAR`
- CockroachDB read-only readiness: `GREEN`
- AWS read-only readiness: `HUMAN_ACTION_REQUIRED`
- AWS return code: `255`
- AWS failure class: `UNKNOWN_EXTERNAL_COMMAND`
- AWS failure-output SHA-256: `8918626fb25f7587c2e58f09168f9aa6e1e61f22fb29027d059b0c1049515316`
- sanitized readiness receipt SHA-256: `f01fd27e5c091ab3a46e84eb881e29fe709217cba8ed9ba6c6d4ff8770723e5e`
- RunPod active inventory: `[]`
- RunPod worker created: `NO`
- RunPod charge incurred by Run 3: `$0.00`

The project-local AWS login has expired. This is a human authentication gate,
not a product-test failure. Do not create a paid worker before a fresh read-only
`sts get-caller-identity` probe and the CockroachDB probe both return GREEN.

## Human action

From the project root, execute:

```bash
AWS_CONFIG_FILE="$PWD/.s3-runtime/aws-auth/config" \
AWS_LOGIN_CACHE_DIRECTORY="$PWD/.s3-runtime/aws-auth/login-cache" \
AWS_SHARED_CREDENTIALS_FILE=/dev/null \
.s3-runtime/aws-expanded-r1/aws-cli.pkg/Payload/aws-cli/aws login \
  --profile ck-s3 \
  --region us-west-2
```

Complete the browser authentication personally, then report `Done`. Resume by
rerunning `hardening-gate7/preflight_live_check.py`; continue into the bounded
RunPod creation envelope only if it returns GREEN.
