# PDH-3 Local Canary Attempt 2 Diagnosis R1

- `STATUS`: `PRESERVED_BLOCKED_ATTEMPT`
- `CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PACKET_SHA256`: `8ee5d0229a238dbba96a2c22268203332a9c20b11550c74a7d093c85612f33c2`
- `FAILURE_CLASS`: `CONCURRENCY_STAGE_NOT_GREEN:10`
- `FAILURE_RECEIPT`:
  `evidence/pdh3-local-canary-r2/failure.json`
- `FAILURE_RECEIPT_FILE_SHA256`:
  `5115c2043de97e12d7bf90d7a8d95d500d3085f54c7f3368958c56412d961435`
- `TEARDOWN_RECEIPT`:
  `evidence/pdh3-local-canary-r2/teardown.json`
- `TEARDOWN_RECEIPT_FILE_SHA256`:
  `f794f21859370f658d6ebe152bacdd5b382a65c9b4ce4c09f60f1ce464f57326`
- `PROCESS_RESIDUE`: none
- `PORT_RESIDUE`: none
- `GENERATED_ROOT_RESIDUE`: none

The run reached concurrency stage 10 and returned a non-GREEN stage result.
The controller then correctly blocked and tore down the database. However, it
stored raw workload metrics only inside the disposable root and deleted that
root during teardown. The surviving failure receipt identifies the failed
stage but not the failed acceptance check.

This is an evidence-controller observability defect. It is not evidence of a
product defect, and it does not authorize assuming the failed check.

The narrow repair writes one canonical stage receipt outside the disposable
root immediately after each stage and before deciding GREEN. On a failed stage,
the failure class also enumerates the false acceptance checks. The final
manifest or failure receipt binds all stage receipt file hashes. No product,
schema, row set, workload, concurrency, threshold, retry, or claim change is
made.

Attempt 2 remains failed evidence and cannot be relabeled. A replacement run
requires updated hashes and fresh independent preflight.
