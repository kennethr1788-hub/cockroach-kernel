# EV1-T05 Execution Preflight Attempt 1 R1

- `STATUS`: `LOCAL_PREFLIGHT_BLOCKED_NO_DELETION`
- `TASK_ID`: `EV1-T05`
- `BLOCKER`: `PRODUCT_FIXTURE_TMP_ALREADY_EXISTS`
- `CAPTURE_STATUS`: `GREEN_EXECUTION_NOT_STARTED`
- `DELETION_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`
- `ORIGINAL_WORKSPACE_PRESENT`: `TRUE`
- `FAILED_TEMP_ROOT_PRESENT`: `FALSE; MOVED_TO_PROJECT_LOCAL_SNAPSHOT`
- `SNAPSHOT_RELATIVE_PATH`: `.ev1-runtime/EV1-T05/control/PREFLIGHT_ATTEMPT1_SNAPSHOT`

The product fixture created its declared `tmp` directory before the T05 runner
reached the same directory-creation line. The runner used non-idempotent
`mkdir`, which raised `Errno 17` before the product canary invocation, dependency
canary, task deletion, or recovery. The exact synthetic fixture was moved into
the project-local control root and preserved with these hashes:

- `product-canary/request.json`: `0ea63971758885285aafdcc084f8b41f2528548b82aeaaae74648baa6ee5b2d5`
- `product-canary/representations/candidate-ev1-t05-predelete/notes/human.md`: `3d62824a3bce112794c75f1fff4fd63519e2362ac81739862251c24e3a081ecb`
- `product-canary/representations/candidate-ev1-t05-predelete/src/feature.py`: `eefc15b3849a14e672d62cc40e322674d8886c41956c254f933d13e327667e78`
- `product-canary/representations/candidate-ev1-t05-predelete/state/uncommitted.txt`: `1411f9a26a3ae88605ad5e24bbf8943a3c1072908f6055a7934b511e7f297176`

The only permitted correction is idempotent creation of that already-declared
fixture-local directory. The capture, task state, product candidate, dependency
graph, acceptance commands, thresholds, and deletion target remain unchanged.
