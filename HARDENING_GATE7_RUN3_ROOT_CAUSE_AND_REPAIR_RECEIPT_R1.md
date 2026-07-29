# Hardening Gate 7 Run 3 Root-Cause and Repair Receipt R1

- `STATUS`: `LOCAL_ROOT_CAUSE_AND_REPAIR_GREEN`
- `UTC_CREATED`: `2026-07-29T01:27:26Z`
- `PARENT_COMMIT`: `e1f7c63d427d0ce0627a8698d7466c06cd987a52`
- `REPAIRED_SOURCE_COMMIT`: `c8383c61cd599d10b02d861aabc764686a81d766`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `AUTHORIZATION_PROMPT_SHA256`: `a941c6e85d021d2ec77ea442765f4df724283af76f74c8b7f19ed91d077f8d30`
- `RUN2_FINAL_PACKET_SHA256`: `a27866a084b09d5d4a1e3aaa7202040897150348344e98f3d57fd92e8d1c24fd`
- `RUN2_HISTORY`: `IMMUTABLE; NOT RELABELED; NOT RESUMED`

## Reproduction

The Run 2 bulk files were executed in dependency order against an isolated
project-local CockroachDB v26.2.3 single-node runtime. Tasks, trajectory
events, and receipts completed. The vector stage failed with SQLSTATE `23505`
on `context_vectors_vector_digest_key`. The recorded stage outcomes were
`tasks=PASS`, `events=PASS`, `receipts=PASS`, and `vectors=FAIL`.

The old 20,000-row vector input set produced only 19,282 unique digests: 718
rows were duplicates, 708 digest values collided, and the maximum multiplicity
was three. The failure was deterministic and reproduced before behavior was
changed. It was not a timeout, memory ceiling, dimension error, or unexplained
provider failure.

- `VECTOR_ERROR_SHA256`: `3551203a9c98757528976da5df0662e7340ee573f062d450a31e3e4c15cd329a`
- `STAGE_RESULTS_SHA256`: `5d083e6dbff63c407f6ebe8fc67e2f2bce11e9c6659218f9892cff5f10344b0c`
- `POST_REPRO_CLEANUP_COUNTS_SHA256`: `58d9fffe639ec31e34a1032bd727a05a5b7d6983881706d28a39c24cd03a31bb`
- `POST_REPRO_COUNTS`: `0,0,0,0`

Local raw evidence remains under
`.hardening-runtime/gate7-r3/local-repro-r2/`. It is project-local,
synthetic, excluded from the transfer archive, and contains no credential.

## Smallest deterministic repair

The uniqueness constraint was preserved. Each synthetic vector input now
contains a single compound event-binding token, `t<task>s<sequence>`, so the
order-insensitive local projection receives one unique token per declared
task/event pair. Generation now fails before SQL emission if any vector digest
collides.

The controller writes one transaction per 250-row batch and retries only
SQLSTATE `40001`, at most three times. SQLSTATE `23505` and every other failure
remain non-retryable and fail closed.

Durable custody was added without changing product semantics:

- separate line-buffered controller stdout and stderr files;
- hash-chained canonical journal events with UTC and monotonic durations;
- fsync on every stage, batch, retry, and terminal event;
- sanitized SQLSTATE, operation family, exception type, batch index, exit
  status, and signal fields;
- canonical failure, result, cleanup, and terminal receipts;
- no GREEN without exact counts, a valid result receipt, cleanup PASS, and
  residue `0,0,0,0`.

## Packaged-helper repair

`bundle/s3-soak/freeze_evidence_manifest.py` is now part of the exact transfer
allowlist. Its relative path, byte size, mode, and SHA-256 are bound in the
source/transfer manifests. Archive validation rejects a missing, duplicated,
renamed, symlinked, altered, or unexpected member.

## Bound source hashes

- `hardening-gate7/build_expanded_bundle.py`: `d7832bb3a2baa9129bc9936de01e1d08456a40a75635b7e40147804156b87b4a`
- `hardening-gate7/live_bulk_controller.py`: `6c6332aaee57d1c1e0066b3f12cfddbc2f915c10f9acae1b69aec26f3211864c`
- `hardening-gate7/test_expanded_gate7.py`: `ebd1d1240cfa38e2f488aeb12d5b0c38fcbf4bf165f764fffa4bb6ee493726a4`
- `s3-soak/cloud_adapter.py`: `becb01384249db11412140692024ed57a228527566ad5821910a48b49bb26222`
- `s3-soak/hardening.py`: `cd1766541b11269bfe5f69f03866e1c163a1fa24821f2b0f2513e768a7f934f4`
- `s3-soak/test_hardening.py`: `fea82e00368b8ddeedff24abfb5389c2ef5c4f5f279a5e508215e92fba98708c`

## Boundary

This receipt closes the local repair defect only. It is not RunPod evidence,
does not authorize a worker before same-hash GLM/AGY preflight, and does not
mark Gate 7 GREEN.
