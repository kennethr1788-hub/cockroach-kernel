# PDH-3 Final RunPod Authorization Receipt R1

- `OPERATOR`: Kenneth
- `UTC_RECORDED`: `2026-07-31T03:19:30Z`
- `PROVIDER`: RunPod
- `CLOUD`: Secure Cloud
- `GPU`: NVIDIA L40S
- `MEASURED_WORKLOAD`: 24 hours / 86,400 seconds
- `MAXIMUM_PAID_LIFETIME`: 28 hours / 100,800 seconds
- `AGGREGATE_COST_CEILING_USD`: `$35.00`
- `CURRENT_COMPUTE_RATE_CEILING_USD_HOUR`: `$0.99`
- `TOTAL_ACTIVE_RATE_CEILING_USD_HOUR`: `$1.10`
- `CONTAINER_DISK`: 250 GB disposable
- `PERSISTENT_OR_NETWORK_VOLUME`: none

## Exact operator authorization

> I approve one Secure Cloud L40S RunPod campaign with a 24-hour measured
> workload, 28-hour maximum paid lifetime, and $35 aggregate cost ceiling.

## Scope

This authorization permits:

- local implementation and preflight of the credential-free PDH-3 controller;
- bounded pre-workload creation retries for one verified Secure Cloud L40S;
- one measured workload after the worker and extracted bundle pass;
- provider charges inside the exact ceilings above;
- evidence retrieval, stop, termination, deletion, billing reconciliation,
  and zero-resource inventory verification.

It does not permit:

- AWS, CockroachDB Cloud, GitHub, package-registry, or model credentials in the
  worker;
- persistent/network volumes;
- client, private, or production data;
- a replacement after measured execution begins;
- a different GPU, cloud class, rate, duration, or aggregate spend;
- PDH-4, release, publication, or submission.

The router's paid-resource human gate is satisfied only for this exact
lifecycle. Independent preflight remains mandatory before worker creation.
