# P2 Evidence Manifest

- `PACKET_PARENT_COMMIT`: `725c6c6ef6c7c7c14c950dba00a37a07ca47a093`
- `MIGRATION_SHA256`: `383d8dce1590b2309dc56017fe468a91098b9b5b38a1fe6e3cae7d1f30e961be`
- `FIXTURE_SHA256`: `a49612a43cd4c2cd303783dec1bc9d217587c9bf9d368abc997e2764eb282172`
- `CHECK_UTC`: `2026-07-25T20:17:15Z`

## Preflight commands and results

| Check | Command | Result |
|---|---|---|
| binary discovery | `command -v cockroach` | NOT FOUND |
| version | `cockroach version` | NOT RUN / no executable |
| live process scan | `pgrep -af '[c]ockroach'` then `ps` verification | no surviving CockroachDB process |
| AWS/local service scan | `pgrep -af '[l]ocalstack|[a]ws'` then `ps` verification | no surviving target service |
| clean clone trial 1 | bootstrap/migrate/seed/rollback/teardown | NOT RUN — blocked preflight |
| clean clone trial 2 | bootstrap/migrate/seed/rollback/teardown | NOT RUN — blocked preflight |

No credentials, live cluster, AWS, RunPod, HOME, or external volume was used.
