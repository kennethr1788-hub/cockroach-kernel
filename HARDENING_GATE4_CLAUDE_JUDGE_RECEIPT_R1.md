# Hardening Gate 4 Claude Judge Receipt R1

- `STATUS`: `VALID_GREEN`
- `JUDGE_ROLE`: `harness/lifecycle semantics and baseline-comparability judge`
- `JUDGE_AUTHORITY`: `non-authoring verdict only`
- `JUDGE_ROUTE`: `claude-judge`
- `SERVED_MODEL`: `claude-opus-4-8`
- `EFFORT`: `max`
- `TOOLS`: `none`
- `PACKET`: `HARDENING_GATE4_JUDGE_PACKET_R1.md`
- `PACKET_SHA256`: `484686e1c02ef84c82a5433c6365559d1683502f9e92fb39d9a039a4b327429d`
- `RAW_OUTPUT`: `HARDENING_GATE4_CLAUDE_JUDGE_RAW_R1.json`
- `RAW_OUTPUT_SHA256`: `375aff0fdf679ee210b81124a4908609e4e4f23132d022ffcf4fe5ffb3b75247`
- `STDERR_SHA256`: `c6dea656f0336e75a49164fdfd39a7ef9db366b633581d0bc82b708a31bf5e64`
- `VERDICT`: `GREEN`
- `BLOCKERS`: `none`
- `RECUSAL_CHECK`: `clear`
- `UTC_RECORDED`: `2026-07-27T20:30:50Z`

## Independence and route proof

Codex authored the protocol and research packet. Claude did not author or shape
the work under review. Before invocation:

- the native launcher resolved to pinned Claude Code `2.1.214`;
- its binary SHA-256 matched
  `59796dd18e9d77f1256f367db6d28ce4bd9cd5968e402ad3a327aac36abc6dec`;
- the judge wrapper SHA-256 matched
  `b4605f1f3a24119ccacc9a87214009e23969ece829e17dd14300b9419b91d42f`;
- the route smoke returned GREEN with served model `claude-opus-4-8`;
- the final wrapper reported served model `claude-opus-4-8` and exited zero.

The wrapper supplied an empty tool set, safe mode, no session persistence,
deny-all HOME writes, a structured output schema, and exact packet hash/model
verification. The raw output passes that schema and has no blockers.

## Non-blocking risks and Gate 5 carry-forward

Claude preserved five disclosed risks: self-authored scenarios, exact placement
of integrity checks inside the timed window, local rather than live-cloud
product mode, conventional selection semantics in the stale/conflict class, and
small/single-worker/single-baseline generalization limits.

Its evidence gaps are explicitly Gate 5 implementation obligations rather than
Gate 4 protocol defects:

1. freeze timing symmetry for Git and Restic integrity checks;
2. verify embedded hashes and official platform binary provenance;
3. freeze generator, scorer, schemas, adapters, isolation, timeouts, receipts,
   and deterministic local smoke;
4. emit sample execution receipts and paired-table output;
5. instantiate and prove the product’s equivalent outside-workspace custody
   layout.

Gate 4 GREEN does not claim those artifacts already exist.

