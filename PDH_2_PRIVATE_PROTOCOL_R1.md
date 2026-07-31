# PDH-2 Private Protocol R1

## Status

`FROZEN_PACKAGE_CANDIDATE_AWAITING_EXTERNAL_TESTER`

This file is not part of the blinded tester packet.

## Candidate and parent gate

- Product candidate:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- Parent gate: `PDH_1_INFORMATION_BOUNDARY_GREEN`
- PDH-1 packet:
  `b60bfad7f54f10796a28dc2db2f5b642472341afdbfe11e2c8b45c9fe28acc02`
- Tester package root:
  `post-dogfood/pdh2-tester-package`
- Tester package manifest hash:
  `c265620cf866eabce00aa53bf5554a8312902c8a8a296c9bd4f243af84254077`

## Blinding

The external tester receives only:

1. the tester package;
2. the public installation/recovery instructions;
3. the allowed-root and teardown boundary;
4. the consent and observation form.

The tester does not receive product source, architecture, expected file hashes,
prior results, internal receipts, thresholds, or the roadmap.

## Frozen trial

1. Tester implements the prescribed function and passes the frozen tests.
2. Tester commits only `src/event_labels.py`.
3. Tester personally edits and visibly saves `docs/CONTINUATION.md` without
   committing it.
4. Tester personally creates and visibly saves untracked `notes/handoff.md`.
5. Controller records the exact three work classes and hashes without exposing
   content to the builder.
6. Product captures only the declared disposable root.
7. Original process terminates; only the disposable workspace is removed.
8. A context-empty fresh process invokes the documented public recovery path.
9. Frozen acceptance runs.
10. Controller records exact hashes, empty-history successor, recovery time,
    restatement words, interventions, residue, and teardown.

## Fixed acceptance

- all three declared work classes restored byte-exactly;
- frozen unittest suite passes;
- no task restatement;
- no builder intervention after loss;
- tester confirms the result is usable;
- no undeclared state read;
- exact package revocation and teardown;
- independent final evidence review GREEN.

## Human gate

Kenneth must select a real external developer and obtain explicit consent. The
tester must be free to report failure. A model, agent, the builder, Kenneth, or
an invented persona cannot satisfy the external-tester identity.

## Kill line

Stop on expected-hash exposure, model-authored “human” work, builder assistance
after loss, tester substitution, failed-task replacement, private data,
undeclared reads, or incomplete teardown.
