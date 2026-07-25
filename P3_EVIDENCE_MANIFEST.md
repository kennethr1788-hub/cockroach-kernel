# P3 Evidence Manifest

- `UNIT_COMMAND`: `PYTHONPATH=p3-ledger python3 -m unittest discover -s p3-ledger -p 'test_*.py' -v`
- `UNIT_RESULT`: 5 tests, `OK`
- `INTEGRATION_COMMAND`: `python3 p3-ledger/run_integration.py`
- `INTEGRATION_RESULT`: exit 0; two fresh-root trials matched
- `TRIAL_A`: ready, event hash `30bbbf8fd2a03a4f1571c3850ebc2baadbb97f2d65f4f3f1bf3d188961b1bc39`, counts `1,1,1,3,1,CONSUMED`, duplicate/orphan rejected, warrant replay rejected
- `TRIAL_B`: same values as Trial A
- `BUDGET_HASH`: `74f110943dd90e9612ec0d7c8003271159ebfeb72afc56956028752926fcf88b`
- `CURRENT_COMMIT`: `7519884`
- `UTC`: `2026-07-25T20:44:14Z`

No process, socket, child, or temporary trial root remained after teardown.
