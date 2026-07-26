# P9 Authentication Resolution Receipt

- `UTC`: `2026-07-26T12:22:31Z`
- `RESULT`: `GREEN`
- `CLOSED_BLOCKER`: `AUTH_HUMAN_GATE`
- `LAST_GREEN_GATE`: `CK_P8_GOLDEN_GREEN`
- `VERIFIED_PARENT_COMMIT`: `499479aa147a24828f4812e566a8f9248d26ac21`
- `AUTHORIZATION_SHA256`: `cb46e382f98d9a4d52a882a3d35f1b0ae4db9047e07f713d2212196dc3204214`

## Human evidence

Kenneth stated in the current Codex conversation:

> I personally signed in to AWS Console and CockroachDB Cloud. Both authenticated dashboards are open in Chrome.

## Visible verification

- AWS title: `Console Home | Console Home | us-east-2`.
- AWS visible heading: `Console Home`.
- AWS sign-in/password form present: `false`.
- CockroachDB title: `cockroach-kernel | CockroachDB Cloud`.
- CockroachDB cluster marker: `cockroach-kernel`.
- CockroachDB overview marker: present.
- CockroachDB provider marker: AWS.
- CockroachDB region marker: `us-west-2` / Oregon.
- CockroachDB sign-in/password form present: `false`.

The verification was limited to visible page state. No cookies, passwords,
tokens, API keys, MFA values, browser storage, or account credentials were
read, extracted, displayed, or recorded.

## Rules recheck

- Official URL: <https://cockroachdb-ai.devpost.com/rules>
- Re-read UTC: `2026-07-26T12:22:31Z`.
- Captured raw HTML bytes: `102825`.
- Selected raw source SHA-256:
  `90625d03fbaafe8821a894472f2ed451f27be0879414fcad6d58f251ce5fee8b`.
- Immediate second-fetch SHA-256:
  `6f3a77e44a628a561a06fab5e858e0bbc6600e02dfb6d313fc12c88d58d199bf`.

The two raw HTML captures differed only in request-variant page material found
in the bounded diff: New Relic timing, CSRF token, and Mixpanel identifier.
The official rules text was re-read and no substantive change was detected in
the submission period, required CockroachDB/AWS integration, repository/demo/
video requirements, testing-access terms, or judging criteria. Raw HTML hash
equality is therefore not used alone as a rule-version verdict.

## Boundary and next action

This receipt closes only the authentication human gate. It does not prove
service quotas, free-tier eligibility, resource availability, cost, IAM/SQL
least privilege, Managed MCP availability, vector/changefeed support, P9
integration, or any S3 requirement.

`NEXT_ALLOWED_ACTION`: perform the remaining read-only P9 platform preflight,
resolve the cross-region contract, freeze the P9 packet, and obtain the required
independent judge verdict before creating or changing any cloud resource.

