# Hardening Gate 2 Synthetic Reseed Receipt R2

- `STATUS`: `GREEN`
- `PARENT_COMMIT`: `c9f7e20e84a15617f8eb85db43f4bca28aae2511`
- `DATABASE`: `cockroach_kernel`
- `SOURCE_SET`: four preserved P9 seed/finalization SQL files
- `SOURCE_SET_MUTATION`: `none`
- `SECRET_VALUE_READ`: `false`
- `UTC_CLOSED`: `2026-07-27T18:45:00Z`

## Scope

Only the two preserved synthetic P9 branches were restored. Each branch now
has exactly one task, trajectory event, receipt, context vector, and worker
result. Projection rows were intentionally omitted because the public reader
does not use them.

## Source hashes

- promote seed: `c7b9990033b36f3ca04e47233709c88aa7d72d8888bf74f384eb8c6833131d11`;
- promote finalize: `a5aac6fef7cff7b3d4fadb4d0f7dd82696a6958bf6df4e167030d224ccbf33a3`;
- refuse seed: `a6bd2d17e5921bc510cbe041a98b1624e903c98e7fcfe8b94ac7754701bb2344`;
- refuse finalize: `96d7f9d3a5d3a959fa0cfadc8b442fb73ec8eebd6d104d8c852a805aaedc627`.

The browser SQL shell could not safely accept the original multi-statement
prepared transactions through accessibility typing. Direct single-row INSERTs
were therefore derived mechanically from the unchanged `EXECUTE p9_*`
argument lists and applied in foreign-key order.

## Fail-closed execution history

The immutable SQL-shell history contains rejected attempts:

- an event and receipt attempted before their parent task existed were rejected
  by foreign keys;
- multi-line transport converted formatting into invalid SQL and was rejected
  with SQLSTATE `42601`;
- one clipboard-contaminated vector attempt contained unrelated local command
  text and was rejected with SQLSTATE `42601`.

No rejected statement partially committed. The clipboard was cleared, later
operations used direct accessibility typing, and exact post-state queries were
run before any live retry. The rejected history was not deleted or presented
as successful evidence.

## Verified final linkage

The joined final result contains exactly two rows:

- `ck-p9-live-promote-r1` with receipt
  `2f30d74734954eab00ceee936c9996bc8a0881b55ee7027b2decccd4a0d6a8bc`,
  event `86c994860c7cef848aa4190951e6cd9353358c5a1fa8245b07033469a8aedcbd`,
  vector digest
  `d4a7e070ddd272ab040436d561edbb3ea88f0b2367515bfbf2cf418402a03271`,
  request `3c7d6d1bb56f5a3901dbfab9e83a0c1c5fb3d2e9fc8702986f0d5c10daae15ec`,
  response `d67f70944096a79c427e2086ed3bac723bef071ae3f5d21e70dcaa3eaeeb51f2`,
  and result `0489b0249c3eaa6081cdfa0576d460d583f9c71d9639a65d44cd55cb4438c979`;
- `ck-p9-live-refuse-r1` with receipt
  `b6d0fe2e5b004d67c3eea7ebc2ffb45d4defcd6184ec670f068915792aa884d8`,
  event `aebce260d27cd13f6d19d882f2987c5d74ad2397b120f123374e52d07e612ac9`,
  vector digest
  `b72c08c01327f9f38a6c4e62dbe803721099b4369af7ffc851453d814096b4cb`,
  request `07e049a9e3552aa5ead493cd728a81d190ddda26c35b77a22d99b3e78665e779`,
  response `4212a2cc26fe4fd7623ba80b8c9d2444d261c4d252d9be673e065b43ceac35ad`,
  and result `c84d932b66ca0dc749029e8c7970efa626940b447f85ed9f7c57dfb77462bfe3`.

Visual hash-linkage evidence:
`evidence/hardening-gate2-closeout-r1/sql-hash-linkage.png`, SHA-256
`1aa436a01abbef73ac3331cdfa04857461330c4338333c719463afe0e8616661`.
