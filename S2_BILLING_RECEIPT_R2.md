# S2 Billing and Exposure Receipt R2

- `PRIOR_ATTEMPT_CALCULATED_MAXIMUM_USD`: `0.003825000`
- `REPLACEMENT_RETURNED_COMPUTE_RATE_USD_PER_HOUR`: `0.060000000`
- `FROZEN_MAX_ACTIVE_RATE_USD_PER_HOUR`: `0.085000000`
- `REPLACEMENT_CONSERVATIVE_LIFETIME_SECONDS`: `22086.752`
- `REPLACEMENT_CALCULATED_MAXIMUM_USD`: `0.521492756`
- `AGGREGATE_CALCULATED_MAXIMUM_USD`: `0.525317756`
- `AGGREGATE_EXPOSURE_CEILING_USD`: `2.000000000`
- `PROVIDER_ITEMIZATION_QUERY`: `[]`
- `VALUE_CLASSIFICATION`: `CALCULATED_MAXIMUM`
- `EXACT_CHARGE`: `NOT_CLAIMED`
- `RESIDUAL_PAID_RESOURCE`: `NONE`
- `RESULT`: `GREEN_UNDER_DELAYED_ITEMIZATION_CLAUSE`

The conservative lifetime runs from provider creation at
`2026-07-26T03:20:25.248Z` through the later detached-guard teardown proof at
`2026-07-26T09:28:32Z`, and charges that whole interval at the larger frozen
active-rate ceiling rather than the lower returned compute rate. Provider
itemization was still delayed at closeout. The execution prompt explicitly
makes delayed itemization non-blocking when rate, timestamps, maximum exposure,
and zero residue are proved. No exact charge is fabricated.
