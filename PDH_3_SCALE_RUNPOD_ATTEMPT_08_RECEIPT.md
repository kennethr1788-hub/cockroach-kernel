# PDH-3 Scale RunPod Attempt 08 Receipt

- `STATUS`: `BLOCKED_PREMEASUREMENT`
- `ATTEMPT`: `08`
- `CAMPAIGN_ID`: `ck-pdh3-scale-r8-relaunch`
- `POD_NAME`: `ck-pdh3-scale-r8-relaunch-01`
- `POD_ID`: `eo9deg7xgys6a8`
- `PACKET_SHA256`: `0cbb17643ef36f16b001e8aeff0e4323f4d93eb8a85370eea0cc6a92ccbaaf12`
- `BUNDLE_SHA256`: `41f35db9e23e008670295755eb5e40d11dc407b0820bb29c88d804e2f3505ecc`
- `MEASURED_CLOCK_STARTED`: `false`
- `WORKLOAD_EXECUTED`: `false`
- `BLOCKER`: `OUTPUT_ALREADY_EXISTS`
- `REMOTE_FAILURE_UTC`: `2026-07-31T19:36:01Z`
- `FIRST_DELETE_ATTEMPT_UTC`: `2026-07-31T19:36:52Z`
- `RECEIPT_CREATED_UTC`: `2026-07-31T19:52:09Z`
- `PROVIDER_RESOURCE_STATUS`: `DELETED`
- `CURRENT_ACTIVE_INVENTORY`: `EMPTY_VERIFIED_2026-07-31T19:45Z_OR_LATER`

## Failure mechanism

The frozen traced command placed `--trace-prefix` and `--receipt` below the
controller output directory. The tracing wrapper created that parent before it
started the child controller. The controller then correctly rejected the
pre-existing output directory with `CampaignError: OUTPUT_ALREADY_EXISTS`.
The target-scale setup and the 24-hour measured clock never began.

This attempt is failed evidence. It is not a campaign result and cannot support
any reliability, performance, scale, or teardown-parser claim.

## Teardown disclosure

The supervisor retrieved the remote failure archive and invoked deletion. The
provider then returned a RunPodCTL v2.7.2 command-scoped wrapper containing an
exact nested numeric `404` Pod-not-found record, followed by Cobra usage text.
The frozen parser did not accept that provider rendering and therefore did not
emit its own teardown-GREEN receipt. Separate provider inventory contained no
matching campaign resource, and a fresh live active inventory check returned
`[]`. The physical paid resource is deleted; the frozen Attempt 08 proof path
remains blocked exactly as recorded.

## Conservative cost treatment

No exact provider invoice is claimed. For authorization accounting, Attempt 08
is conservatively bounded from the amended launch-window start
`2026-07-31T19:31:03Z` through the first successful delete invocation at
`2026-07-31T19:36:52Z`: 349 seconds at the frozen active-rate ceiling
`$1.0247222222222223/hour`. Adding that entire interval to Attempts 01–07 gives
a prior-cost upper bound of `$1.7172636574074076`. One further full 28-hour
replacement at the same ceiling produces an aggregate upper bound of
`$30.40948587962963`, leaving `$4.5905141203703685` beneath Kenneth's existing
`$35` aggregate ceiling. This is an upper envelope, not a provider invoice.

## Evidence bindings

| Evidence | SHA-256 |
|---|---|
| `.pdh3-runtime/r8-launch-amendments/20260731T192519Z/PDH_3_SCALE_RUNPOD_PREFLIGHT_PACKET_R8.md` | `0cbb17643ef36f16b001e8aeff0e4323f4d93eb8a85370eea0cc6a92ccbaaf12` |
| `.pdh3-runtime/r8-launch-amendments/20260731T192519Z/PDH_3_SCALE_RUNPOD_PREFLIGHT_BINDINGS_R8.json` | `20fb3a29d1b675dfd18afa9251dea818cd050fb1882c7cf34a5ede3aa70929f0` |
| `.pdh3-runtime/r8/concrete-runtime-commands.json` | `a7050e8b0ff81959b6b29d7737d6967d5f064e53ea3c91b286bca03877795b2c` |
| `.pdh3-runtime/r8/retrieval/final-state.json` | `88fec105b4e75936a7d36d9fcd68f2a8f94bceb6a43c54a3ca0883747d1dd8c7` |
| `.pdh3-runtime/r8/retrieval/final-evidence.tgz` | `90ee3e02d95c7090edf38a5626da732f6f2ebb19273407f7681b3a986c52f656` |
| `.pdh3-runtime/r8/retrieval/final-evidence.tgz.sha256` | `2eddc495a26ee7ae612d9dbc2d6db2c7d0e9c68ca67e2525e604d18ec3cc72d7` |
| `.pdh3-runtime/r8/supervisor.ndjson` | `fc0e20dc2af771252ff615fd1a622b451187cadc1b301da8b5b1a9ec09843f51` |
| `.pdh3-runtime/r8/lifecycle-guard.ndjson` | `d1e16a437f76967cc7bf7be8a11125fb26ffd8348de4d955806677c5ea6bcaba` |
| `.pdh3-runtime/r8/retrieval/provider-get-011.json` | `995f80ad51d81a5acaa979b93adb0b36ab0083a2cffe950c47aeb4b491b0c8ab` |
| `.pdh3-runtime/r8/retrieval/provider-list-011.json` | `56360c40e8f1e945597a743892d8da165384f08ebd8515d3e96b71a2bb08eb30` |

## Repair boundary

The smallest defensible repair moves the trace prefix and tracing receipt
outside the controller output directory, while keeping all paths under the
same remote campaign root. It also parses only the exact RunPodCTL v2.7.2
command-scoped 404 wrapper; arbitrary trailing text or unstructured 404 text
remains rejected. Attempt 08 is preserved unchanged and may not be relabeled.
