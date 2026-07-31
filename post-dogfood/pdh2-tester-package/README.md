# Blinded Disposable Recovery Trial

This is a private, synthetic, disposable test project. Do not use real,
personal, client, employer, credential, production, or confidential data.

## Objective

Implement `normalize_event_label` in `src/event_labels.py` so the frozen tests
pass.

The function must:

- require a string;
- trim leading and trailing whitespace;
- lowercase ASCII letters;
- replace each run of spaces or underscores with one hyphen;
- reject an empty result;
- reject characters outside lowercase ASCII letters, digits, and hyphens;
- return the normalized label.

## Required work-state mix

After the tests pass:

1. Commit only the completed `src/event_labels.py`.
2. Add one personally written sentence to `docs/CONTINUATION.md`, save it, and
   leave that tracked file modified but uncommitted.
3. Create and save an untracked `notes/handoff.md` containing two personally
   written sentences describing what the next developer should verify.

Do not use a model or the recovery product to write either personally written
item. Do not reveal their content to the builder.

## Acceptance

```bash
python3.12 -m unittest discover -s tests -v
```

Stop after the acceptance command passes and the three work classes exist.
Follow the separately supplied recovery instructions. Report any ambiguity or
failure; do not repair the package or substitute another task.
