# Hidden Campaign Actor Route Preflight R1

- `STATUS`: `ACTOR_ROUTE_READY_PENDING_INDEPENDENT_REVIEW`
- `UTC`: `2026-07-28T07:38:11Z`
- `CONTROLLER_COMMIT`: `c70914d042380fd57f7db498084a7025c1a1aa24`
- `CODEX_CLI_VERSION`: `0.144.5`
- `CODEX_COMMAND_PATH`: `/Users/kennethruedas/.npm-global/bin/codex`
- `CODEX_COMMAND_SHA256`: `134063e133f0b4244fa3b251acf973d4fe4b4aeeacbdc135211bf480f59f1477`
- `MODEL_PIN`: `gpt-5.6-sol`
- `REASONING_EFFORT`: `high`
- `SESSION_MODE`: `ephemeral; no resume; one invocation`
- `THREAD_ID`: `019fa7a8-e4b6-72d3-b62b-2039cb73eccd`
- `EXIT`: `0`
- `SCHEMA_RESULT`: `STOP / empty argv / actor route ready`
- `TOOL_EVENTS`: `0`
- `INPUT_TOKENS`: `17001`
- `OUTPUT_TOKENS`: `25`
- `REASONING_OUTPUT_TOKENS`: `0`
- `ACTOR_RESPONSE_SCHEMA_SHA256`: `66504ab173115e21e96dfb132a7f8ad7b2cfcabf0886f08d8b56052e385df0d9`
- `CONTROLLER_SHA256`: `7d2207d784a5cf38d3b7e0ce82870d48eee45ce86111524cc9329528d8fe94f9`
- `HIDDEN_SEED_CREATED`: `NO`
- `HIDDEN_EXECUTIONS`: `0`

The route disables shell, unified execution, browser, apps, plugins, computer
use, multi-agent, image generation, and in-app browser features. The actor sees
only a synthetic prompt and returns a schema-validated proposal. The controller
alone invokes the public recovery command under the frozen Seatbelt profile.

The CLI event stream identifies a unique fresh thread and successful explicitly
pinned model request. This Codex CLI version does not emit a separate
provider-served-model field; therefore the final evidence must label identity as
`explicit model pin gpt-5.6-sol via official Codex CLI 0.144.5`, not claim a
second independent served-model header.

Observed cache/state warnings were non-terminal and no session was persisted
because `--ephemeral` was used. No actor tool call occurred.
