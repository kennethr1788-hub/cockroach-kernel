# Hardening Gate 6 R3 — Attempt 03 Success and Teardown Receipt

- `STATUS`: `MEASURED_GREEN; TEARDOWN_GREEN; FINAL_REVIEW_PENDING`
- `POD_ID`: `18hf13p5qu4pov`
- `POD_NAME`: `ck-gate6-20260727-r3-a03`
- `CREATED_UTC`: `2026-07-28T03:01:17.956Z`
- `MEASURED_START_UTC`: `2026-07-28T03:07:05Z`
- `TEARDOWN_GREEN_UTC`: `2026-07-28T03:13:07Z`
- `WORKER`: `CPU; 2_VCPU; 4_GIB; 0_GPU; 0_VOLUME; 20_GIB_CONTAINER_DISK`
- `IMAGE`: `runpod/base:1.0.2-ubuntu2204`
- `RATE_USD_PER_HOUR`: `0.06`
- `KNOWN_LIFETIME_SECONDS_MAX`: `709.044`
- `BOUNDED_COMPUTE_COST_USD_MAX`: `0.0118174`
- `BOUNDED_COST_AT_ACTIVE_RATE_CEILING_USD_MAX`: `0.0196956667`
- `EXACT_PROVIDER_CHARGE`: `PENDING; BILLING_QUERY_RETURNED_EMPTY_AFTER_DELETION`
- `CAPABILITY_CANARY`: `GREEN`
- `CANARY_RECORD_SHA256`: `8940387642d55e1fa43e70e193417cedf2ac94fb713abad7bc2141004e16744d`
- `CANARY_FILE_SHA256`: `7e8e1a83bb372e47278d4bed76d786bcd9f7b698ae7ab314202119761d3a9191`
- `PAYLOAD_ARCHIVE_SHA256`: `c3958a5847f1cd8d35bb66c89700d0412eda72c5c28bbda41e67cf6cef44403a`
- `PAYLOAD_TREE_SHA256`: `6bb049a13904dc2d7b447d9193cf1574f83dd2d3ed622f347d8fd6e3913a95a3`
- `POST_UPLOAD_SMOKE`: `GREEN; EXACT_CANDIDATE_8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `MEASURED_EXECUTIONS`: `54`
- `UNIQUE_COMBINATIONS`: `54`
- `PAIR_COUNT`: `18`
- `MEASURED_PROCESS_EXIT`: `0`
- `MEASURED_STDERR_BYTES`: `0`
- `REMOTE_EVIDENCE_ARCHIVE_SHA256`: `1ed09238a554b6ddb333d8adfafd554a55205f9c45fa5b2487a03645367814e5`
- `AGGREGATE_SHA256`: `25fa143dfd7b489ac2a5d79cba974ce944d12609d8f7e6f1c6a42e87fe53325f`
- `FINAL_CHECKPOINT_SHA256`: `f0da23ae0aa4654a1365c396de742db0fca6ff231c4493e29c5bd75cddd3ef11`
- `LIFECYCLE_CHAIN_FILE_SHA256`: `ea88f74fc6a86b9e41fc9924d97a4b42b4899959f086868574b53199f44d300b`
- `LIFECYCLE_FINAL_EVENT_SHA256`: `6aae4655b242e54e66b14dd15dd152a4197f3b9d4203bb847c0f147eb60de3c0`
- `STOP_RESULT`: `success`
- `DELETE_RESULT`: `success`
- `EXACT_ID_LOOKUP_AFTER_DELETE`: `not_found`
- `CAMPAIGN_ACTIVE_INVENTORY_AFTER_DELETE`: `[]`
- `DETACHED_GUARD_AFTER_DELETE`: `stopped`
- `GATE7`: `FORBIDDEN`

The measured campaign ran as the frozen candidate under an unprivileged UID,
zero effective capabilities, `no_new_privs`, and a kernel seccomp filter that
returned `EPERM` for network socket creation. This is not a network namespace,
and the evidence preserves that limitation. The campaign is synthetic paired
comparative evidence, not live AWS or population-scale evidence. Exact provider
billing remained delayed; the known lifetime and conservative active-rate bound
are recorded without fabricating a charge. Gate 6 remains pending until GLM 5.2
and AGY independently return GREEN over one exact final packet hash.
