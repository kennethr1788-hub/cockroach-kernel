# S3 Preflight Judge Receipt R11

- `PACKET`: `S3_PREFLIGHT_PACKET_R11.md`
- `PACKET_SHA256`: `5904d8fb6cee6f8cfc57c051bb8bdc986671dd885cb339c5ed385f9ac86d44d4`
- `PACKET_BYTES`: `261586`
- `GLM_SERVED_MODEL`: `glm-4.7`
- `GLM_ROUTE`: `DIRECT_VERIFIED_PLAYBOOK_FALLBACK_AFTER_BOUNDED_GLM_5_2_FAILURES`
- `GLM_VERDICT`: `GREEN`
- `GLM_RAW_OUTPUT_SHA256`: `aca3b51ed485a04ca8b4d68425f9487c39a9287289ab3c7c748822c204684fba`
- `CLAUDE_SERVED_MODEL`: `claude-opus-4-8`
- `CLAUDE_VERDICT`: `GREEN`
- `CLAUDE_RAW_OUTPUT_SHA256`: `33003ff3dc960e7590c6a67963bb653859fdb24feb2364b07088a9ccfeb3854e`
- `CLAUDE_RECUSAL_CHECK`: `clear`
- `GLM_RECUSAL_CHECK`: `CLEAR`
- `GATE`: `S3_PREFLIGHT_R11_GREEN`
- `UTC_RECORDED`: `2026-07-27T03:26:57Z`

Both independent judges evaluated the exact R11 packet hash and returned GREEN
with no blockers. GLM 5.2 did not produce a countable result after bounded
current-playbook attempts: two responses exhausted their output budget before
content, one call hit the wrapper timeout, and one transport failed. The direct
served-model-verified GLM 4.7 fallback then returned substantive GREEN but
omitted the mandatory hash echo; that malformed result was invalidated. One
bounded schema-correction retry on the unchanged packet returned GREEN, the
exact packet hash, and clear recusal.

Claude identified two runtime facts that remain fail-closed before production:
the provider stop fuse must retain setup plus 43,200-second execution plus
retrieval/teardown margin, and the host AWS login must remain valid through the
final hourly cloud call. The AWS CLI has already demonstrated automatic token
refresh; AWS official documentation states the overall `aws login` session is
valid up to the IAM principal's configured duration, with a maximum of twelve
hours. The executor must revalidate identity immediately before production and
continue runtime identity checks through the coordinator path.

This receipt authorizes only A04 creation and the one production attempt inside
the frozen attempt, cost, credential, evidence, and teardown envelope. It does
not establish campaign-ready or production GREEN.
