# Hardening Gate 7 Run 3 Regression Closeout R2

- `STATUS`: `GATE7_RUN3_REGRESSION_REPAIR_GREEN`
- `UTC_CREATED`: `2026-07-29T02:48:00Z`
- `PARENT_PACKET`: `HARDENING_GATE7_RUN3_PREFLIGHT_PACKET_R3.md`
- `PARENT_PACKET_SHA256`: `06ffb54d83b8c5dc9a37b88e4e16c42ab6b82e921a05cb0b0e9e6a26cc5260de`
- `GLM_R3`: `GREEN; RECUSAL_CLEAR`
- `AGY_R3`: `BLOCKED; RECUSAL_CLEAR`
- `REGRESSION_COMMIT`: `348d2b5cb0d20e3fcc47c673f0f177f3725caca4`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `RUNPOD_ATTEMPTS`: `0`
- `HIDDEN_SEED`: `ABSENT`

## AGY findings preserved

Canonical AGY 1.1.8 reviewed the exact R3 packet and returned `BLOCKED` for:

1. no regression test executing the complete successful 46,000-row
   `run_live` controller path; and
2. no regression test directly comparing repeated deterministic generator and
   controller output semantics.

The exact AGY output is preserved under the ignored runtime evidence root.

- stdout SHA-256:
  `442ef4858549fa0059864ae7fd106712435224f9df1a7390857ac573e6d72be7`;
- stderr SHA-256:
  `bf32ab8c082fa1aff618ee172c412b767bf7f636479cf49543749f2ba6ad30ee`.

No verdict was overridden and no RunPod worker was created.

## Smallest correction

Only `hardening-gate7/test_expanded_gate7.py` changed. Product and remote
workload source are unchanged.

The expanded generator test now builds the exact 46,000-row SQL workload twice
from clean roots using the same campaign identifier and requires identical:

- manifest objects;
- every generated SQL batch byte;
- query specification bytes;
- cleanup bytes; and
- all path-to-byte mappings.

A new full-controller test now executes `run_live` twice over the exact full
manifest with a deterministic in-memory SQL boundary. Each execution proves:

- 2,000 tasks, 20,000 events, 4,000 receipts, and 20,000 vectors;
- all 184 batch files executed exactly once;
- 200/200 vector queries;
- preclean and final cleanup;
- rollback count `0` and duplicate-idempotency count `1`;
- canonical GREEN result, cleanup, and terminal custody;
- terminal validation through `validate_terminal_evidence`; and
- identical stable result semantics, stable terminal semantics, and cleanup
  receipt bytes across the two runs.

Runtime journal hashes and linked receipt hashes are intentionally excluded
from the repeat comparison because they bind UTC and monotonic execution
metadata. Verdict, counts, hashes of deterministic inputs/outputs, latency
values supplied by the deterministic boundary, cleanup, and terminal semantics
remain compared.

Test source SHA-256:
`de5fc628f44c62bd849bf5b5b2dc2cd6849ca5a20eb94ad12d7e220188a55638`.

## Verification

- Gate 7 discovery: `19/19 PASS`, stderr SHA-256
  `04cf5ba2d01169cfc36ab8fcefc1597b8a3599c6ce3554bcd2d6c8c3258c144c`;
- S3 discovery: `18/18 PASS`, stderr SHA-256
  `b44595f9b28c4c5ff8c84456247ca7cc882f5e2bffe4268a83cca01df930a58d`;
- Python compilation: `PASS`;
- `git diff --check`: `PASS`;
- gitleaks over the changed test: zero findings;
- detect-secrets: two reviewed test SHA literals, zero credential-type
  findings;
- local CockroachDB/controller process: absent;
- ports `26327`, `26328`, and `8098`: closed.

## Transfer archive continuity

The test file is not shipped to the worker. Two fresh clean archive builds
remain byte-identical to each other and to the previously accepted archive:

- archive SHA-256:
  `d0a47c311ad14f16e1bed2df181bb3d6885accf155be7322a67829c201023b28`;
- payload-tree file SHA-256:
  `d21bf5c262f30049e29d31ee89d817bc4ee9755f3c76578e30739c90729c36bb`;
- transfer-manifest file SHA-256:
  `ec2e0da16a68b965301cde70a5d2eb28054d67ee6af617f0a7ef9549d026361c`;
- archive file count: `93`;
- packaged helper binding: unchanged and valid.

## Gate boundary

This closes only the two R3 test-evidence blockers locally. A new complete R4
packet must bind commit `348d2b5cb0d20e3fcc47c673f0f177f3725caca4`, the updated test bytes, this
receipt, and the preserved R3 verdicts. Exact-model GLM 5.2 and canonical AGY
must both return same-hash GREEN before any RunPod worker can be created.
