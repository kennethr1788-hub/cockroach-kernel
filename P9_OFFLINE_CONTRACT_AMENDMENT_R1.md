# P9 Offline Contract Amendment R1

- PARENT: `P9_OFFLINE_CONTRACT_R1.md`
- PROPOSAL_SHA256: `df4d2c32f75f14c9ca4ec91dcc18a5706bfddf200bb6b4a47a9a206b1b5d6912`
- INDEPENDENT_VERDICT: `GREEN`
- SCOPE: offline IAM templates only

The R1 wildcard stop condition remains unchanged except for one exact,
independently reviewed implementation clarification: the Lambda execution role
may use `log-stream:*` only beneath
`/aws/lambda/ck-p9-evaluator` in `us-west-2` and the live AWS account. Wildcard
actions, global resources, wildcard services/accounts/regions/log groups, and
any other wildcard remain blocked.

This amendment does not modify the canonical execution prompt or plan. It does
not authorize AWS mutation. Live account-ID substitution, policy simulation,
role readback, retention readback, and negative permission tests remain required.
