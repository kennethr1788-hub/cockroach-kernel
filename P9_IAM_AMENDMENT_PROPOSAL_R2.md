# P9 IAM Amendment Proposal R2

## Trigger

The first bounded AWS lifecycle created the exact role, log group, function, and
alarm, but the load-bearing IAM simulation failed before any invocation. The
reviewed policy resource ended in `:log-stream:*`. Both
`logs:CreateLogStream` and `logs:PutLogEvents` evaluated to `implicitDeny`.
The failure trap then deleted the exact role, function, log group, and alarm.
Read-only inventory confirmed that all four resources were absent.

## Authoritative correction

AWS's current CloudWatch Logs authorization reference identifies both required
actions as `log-stream` resource actions and documents the log-stream ARN
shape. The live AWS policy simulator additionally proved that this account's
effective Lambda logging resource must use the exact log-group ARN with AWS's
trailing stream wildcard:

`arn:aws:logs:us-west-2:${AWS_ACCOUNT_ID}:log-group:/aws/lambda/ck-p9-evaluator:*`

The prior `:log-stream:*` form evaluated to `implicitDeny`; the corrected
exact-log-group form evaluated to `allowed` for both required actions.

Official source:
`https://docs.aws.amazon.com/service-authorization/latest/reference/list_logs.html`

Snapshot SHA-256:
`88995a795da3a67549e4e720d36a33faaefd0d9fe18c39c3efa8529f692e1a8a`

Verified UTC: `2026-07-26T19:40:04Z`.

## Authority boundary

This amendment changes only the resource spelling used by the two already
approved logging actions. It does not add an action, service, region, account,
log group, function, trigger, URL, event source, secret, database permission,
network permission, or control-plane permission. The wildcard remains confined
to runtime-created streams under the exact project log group. `Resource: *`,
wildcard actions, `logs:CreateLogGroup`, and every non-logging action remain
forbidden.

## Retry acceptance

- all offline tests and secret/private-path scans pass after the amendment;
- a fresh custom-policy simulation returns `allowed` for the two exact actions
  on the corrected exact-log-group resource;
- the forbidden-action simulation returns only `implicitDeny`;
- one independent non-authoring GLM judge returns GREEN on the exact frozen
  retry packet hash;
- the retry recreates only the four exact project resources and repeats the
  full readback before any invocation.

## Kill line

If the corrected exact-log-group resource does not simulate and execute as
declared, roll back the four exact AWS resources and stop P9. Do not widen the
policy.
