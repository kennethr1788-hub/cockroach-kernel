# P9 AWS Eventual-Consistency Amendment R1

## Correction

Replace the single immediate log-stream read with a bounded observation poll:

- maximum observation window: 90 seconds;
- interval: 5 seconds;
- maximum checks: 19, including the initial check;
- no additional Lambda invocation during the poll;
- no resource, permission, timeout, concurrency, trigger, URL, or alarm change;
- success only when the exact log group exposes at least one stream;
- failure after the window invokes the existing exact-resource rollback.

The poll addresses CloudWatch control-plane visibility only. It cannot restart
the function, extend the request budget, invoke a third time, or widen IAM.

## Evidence boundary

The previous two successful live responses remain preserved as killed-lifecycle
evidence and do not green P9. The next lifecycle must independently recreate
the exact resources, repeat two sequential invocations, observe the exact log
stream within the bounded window, retrieve raw evidence, and pass teardown or
preservation readback.

## Kill line

If the stream is not visible within 90 seconds, or any existing gate changes,
roll back the exact four resources and stop. Do not increase the window or
widen the logging policy without a new packet and independent review.
