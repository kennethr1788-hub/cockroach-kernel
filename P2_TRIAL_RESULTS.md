# P2 Trial Results

Both trials used the same project-local v26.2.3 arm64 binary, synthetic
migration, and synthetic fixture. Stores were created under fresh temporary
roots and deleted after teardown.

| Trial | Root | Ready | Version | Fixture SHA-256 | Tables | Rollback | Cockroach process remains | Residue | Result |
|---|---|---:|---|---|---:|---|---:|---:|---|
| 1 | `p2-cleanroom/runtime/trial9.PnFx7U` | 1 | v26.2.3 | `a49612a43cd4c2cd303783dec1bc9d217587c9bf9d368abc997e2764eb282172` | 2 | PASS | 0 | 0 | PASS |
| 2 | `p2-cleanroom/runtime/trial10.Q9WL0l` | 1 | v26.2.3 | `a49612a43cd4c2cd303783dec1bc9d217587c9bf9d368abc997e2764eb282172` | 2 | PASS | 0 | 0 | PASS |

The runtime directory was empty after both teardowns. No credentials, live
cluster, AWS, RunPod, HOME, or external volume was used.
