# Hidden Campaign Local Actor Route Preflight R2

- `STATUS`: `ROUTE_PROVEN_PENDING_SAME_HASH_REVIEW`
- `UTC`: `2026-07-28T07:48:55Z`
- `ACTOR_RUNTIME`: `Ollama 0.30.11`
- `ENDPOINT`: `http://127.0.0.1:11434`
- `ENDPOINT_SCOPE`: `loopback only; proxy use disabled in controller`
- `MODEL`: `qwen2.5-coder:7b`
- `MODEL_DIGEST_EXPECTED`: `dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364`
- `MODEL_DIGEST_OBSERVED`: `dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364`
- `MODEL_CLASS`: `Qwen2.5 Coder 7.6B / GGUF / Q4_K_M / 32768 context`
- `TAGS_RESPONSE_SHA256`: `e42ccfeb2ec613f2a6fa0646941a44954c969cd666dec6f7733827e16110480b`
- `PUBLIC_SMOKE_SESSION_ID`: `r2-public-route-smoke`
- `PUBLIC_SMOKE_SESSION_IDENTITY`: `92893e0b16e7d48a5a6222d2d0aa61672c92cdab3084feb19c04c62eddcd60c7`
- `PUBLIC_SMOKE_REQUEST_SHA256`: `6917f40471ff3d64221ccf278f0d8c99b4695cbad9741f9dafb6222467ebe639`
- `PUBLIC_SMOKE_RESPONSE_SHA256`: `e2987333ce5e7b21ba8fb6fbdb770f001464ba8d98ba80663b7192d8ffaaddfe`
- `PUBLIC_SMOKE_RESULT`: `STOP / empty argv / schema-valid`
- `TOOLS_EXPOSED`: `0`
- `CONTEXT_SUPPLIED_OR_REUSED`: `NO`
- `KEEP_ALIVE`: `0`
- `POST_SMOKE_OLLAMA_PS`: `empty`
- `INCREMENTAL_COST`: `$0`
- `EXTERNAL_EGRESS`: `NONE`
- `HIDDEN_SEED_CREATED`: `NO`
- `HIDDEN_EXECUTIONS`: `0`

Every later actor request must reverify the exact tag and digest before the
seed is created, bind a unique controller-generated session identifier into
the request, require the response model field to match exactly, validate the
closed response schema, and unload the model after the request. A local actor
invocation identifier is not described as an external provider session.
