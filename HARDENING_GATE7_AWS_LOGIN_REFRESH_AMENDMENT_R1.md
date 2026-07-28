# Hardening Gate 7 AWS Login Refresh Amendment R1

## Classification

- `SCOPE`: `GATE7_HOST_ORCHESTRATION_ONLY`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PRODUCT_MUTATION`: `NO`
- `REMOTE_PAYLOAD_MUTATION`: `NO`
- `BENCHMARK_SEMANTICS_MUTATION`: `NO`
- `THRESHOLD_RELAXATION`: `NO`
- `MEASURED_EXECUTION_STARTED`: `NO`
- `HIDDEN_SEED_EXISTS`: `NO`
- `PRIOR_PACKET_SHA256`: `4fd89d699dccd0d3e15451fab40435ad2e9b3f7300061ff8791913dc4b7ecf44`
- `AUTHORITY`: `The Gate 7 authorization permits a provider/lifecycle orchestration correction before hidden generation when it leaves product and benchmark behavior unchanged and receives fresh same-hash GLM/AGY GREEN.`

## Defect

The static session gate treated the expiration of one AWS access credential as
the expiration of the entire `aws login` session. The installed AWS CLI issues
15-minute access credentials but automatically refreshes them while the login
refresh token remains valid. Repeated human login cannot make one rotating
access credential span the one-hour track, so the old check tests the wrong
object.

Primary AWS documentation:

- `https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html`
- `https://docs.aws.amazon.com/sdkref/latest/guide/feature-login-credentials.html`

The installed `aws login help` output independently states that temporary
credentials are refreshed automatically while the refresh token remains valid.
No credential or token bytes were placed in evidence or sent to any judge.

## Narrow correction

The host coordinator retains the legacy static-expiration mode and adds one
explicit `--aws-login-auto-refresh` mode. That mode:

1. proves the configured `ck-s3` provider type is `login`;
2. proves the installed AWS CLI advertises automatic refresh;
3. records only hashes and stable metadata, never credential bytes;
4. makes no future-expiration claim at campaign start;
5. runs all twelve frozen Lambda/Cockroach exchanges under the existing strict
   ceilings;
6. records the actual wall-clock epoch of the final cloud exchange;
7. waits the full frozen 900-second post-exchange margin using heartbeat and
   deadline checks;
8. performs one sanitized, read-only `sts get-caller-identity` probe after that
   margin; and
9. blocks the coordinator unless that post-margin probe succeeds.

This is stronger than projecting a future expiry: the margin is established by
a real provider call after the required interval. The post-margin probe is not
a Lambda invocation, is not a scored row, and does not change the 3,600-second
remote workload. It is an orchestration closeout check.

## Preserved boundaries

- exactly 84 hidden scored executions;
- exactly one 3,600-second live worker track;
- exactly 12 Lambda calls and 108 CockroachDB operations;
- unchanged 46,000-row synthetic bulk workload;
- unchanged one-worker, rate, disk, volume, network, and teardown ceilings;
- no credential or cloud client on RunPod;
- no hidden seed before `CAMPAIGN_READY`;
- no measured rerun, replacement, tuning, threshold change, or product edit;
- final GLM/AGY same-hash review remains mandatory.

## Kill line

Stop before hidden generation if either independent judge rejects this
amendment, the active provider is not `login`, the installed CLI lacks the
automatic-refresh contract, AWS/Cockroach readiness is not GREEN, or any A03
hash/isolation/lifecycle prerequisite drifts. During execution, a failed
refresh or post-margin identity probe blocks Gate 7 and triggers evidence
preservation plus teardown.
