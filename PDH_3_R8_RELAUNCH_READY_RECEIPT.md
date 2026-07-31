# PDH-3 R8 Relaunch-Ready Receipt

- `STATUS`: `PDH3_R8_RELAUNCH_READY`
- `UTC_VERIFIED`: `2026-07-31T19:14:32Z`
- `PAID_WORKER_CREATED`: `false`
- `CURRENT_RUNNING_RUNPOD_INVENTORY`: `[]`
- `PACKET_SHA256`: `3615d8606e5678946634f6166c5bdd41e34fbdb21266d39f3396e2c3f11b6d95`
- `PACKET_BYTES`: `204069`
- `BINDINGS_FILE_SHA256`: `bffa146712862ab05d166674e2e1f24543be533f79f530bcb5067b8e3d25f138`
- `BINDINGS_INTERNAL_SHA256`: `403b24b6e7080ad56e5ef2f57f51074aebd0b2d4ccffad6a2878bfa9e01388c9`
- `SOURCE_SET_SHA256`: `0dfa7de63297d27640ab8308c5fd4067e21985c6724b23b822c470894290ce6f`
- `BUNDLE_SHA256`: `41f35db9e23e008670295755eb5e40d11dc407b0820bb29c88d804e2f3505ecc`
- `LOCAL_TESTS`: `125/125 GREEN`
- `GLM_PREFLIGHT`: `GREEN`
- `AGY_PREFLIGHT`: `GREEN`
- `JUDGE_PACKET_IDENTITY`: `IDENTICAL`
- `LOCAL_CHECKLIST_ITEMS`: `21/21 GREEN`
- `REMOTE_GATE_R8_08`: `OPEN_UNTIL_WORKER_EXECUTION`
- `REMOTE_GATE_R8_10`: `OPEN_UNTIL_WORKER_EXECUTION`
- `PRECREATE_RECHECK`: `MANDATORY_IMMEDIATELY_BEFORE_CREATE`

## Proven relaunch envelope

The frozen provider evidence selects one available Secure Cloud L40S with
48 GiB VRAM, 16 vCPU, 94 GiB RAM, and a 250 GiB disposable container disk.
The measured active-rate projection is `$1.0247222222222223/hour`; the prior
plus replacement aggregate projection is `$29.029242`, below the authorized
`$35.00` ceiling. Provider-native stop and terminate deadlines remain safety
fuses, not project-completion deadlines.

The worker may be created only after the exact precreation refresh again proves
empty running inventory, an eligible offer and rate, the pinned RunPodCTL hash,
and valid future lifecycle timestamps. After creation, R8-08 and R8-10 must pass
on the real worker before the 24-hour measured clock begins. Failure retrieves
evidence and deletes the worker; it cannot be converted to GREEN.

No paid worker was created while producing this receipt.
