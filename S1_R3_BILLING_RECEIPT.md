# S1 R3 Billing Reconciliation Receipt

- `RESULT`: `OPERATOR_ACCEPTED_DELAYED_ITEMIZATION`
- `BLOCKER`: `NONE`
- `PRIOR_POD_ID`: `48bqdill8w3vt0`
- `R3_POD_ID`: `wo1iq5wtk04q49`
- `FINAL_QUERY_UTC`: `2026-07-25T22:47:27Z`
- `PRIOR_EXACT_CHARGE`: `UNAVAILABLE`
- `R3_EXACT_CHARGE`: `UNAVAILABLE`
- `AGGREGATE_EXACT_CHARGE`: `UNAVAILABLE`

Pod-scoped billing queries returned `[]` for both Pod IDs at immediate
closeout and for six bounded reconciliation attempts from
`2026-07-25T22:46:30Z` through `2026-07-25T22:47:27Z`.

Recorded rates and lifecycle times yield non-authoritative estimates only:

- R3 lifecycle seconds: 3,930.039;
- R3 estimated charge at $0.064/hour active rate: $0.069867360;
- prior failed lifecycle estimated upper charge: $0.000248889;
- aggregate estimated upper charge: $0.070116249;
- authorized aggregate ceiling: $0.30.

These estimates are below the ceiling but are not substituted for the missing
provider charge. The authenticated billing page disclosed that billing data is
one hour behind. Kenneth explicitly confirmed that he sees and accepts the
account-side charge and removed delayed itemization as an S1 blocker. The exact
per-Pod value remains honestly marked unavailable at closeout.
