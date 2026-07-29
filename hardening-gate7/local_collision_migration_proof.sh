#!/usr/bin/env bash
set -euo pipefail

base=$(cd "$(dirname "$0")/.." && pwd)
cockroach_bin="$base/p2-cleanroom/vendor/cockroach-v26.2.3/extracted.MC8vGd/cockroach-v26.2.3.darwin-11.0-arm64/cockroach"
sql_port=26357
http_port=18157
cockroach_pid=""

cleanup() {
  if [[ -n "$cockroach_pid" ]]; then
    kill -TERM "$cockroach_pid" 2>/dev/null || true
    for _ in {1..50}; do
      if ! kill -0 "$cockroach_pid" 2>/dev/null; then
        wait "$cockroach_pid" 2>/dev/null || true
        return
      fi
      sleep 0.1
    done
    kill -KILL "$cockroach_pid" 2>/dev/null || true
    wait "$cockroach_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

if lsof -nP -iTCP:"$sql_port" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "LOCAL_PROOF_PORT_BUSY" >&2
  exit 2
fi

(
  cd /tmp
  COCKROACH_SKIP_ENABLING_DIAGNOSTIC_REPORTING=true exec \
    "$cockroach_bin" start-single-node \
    --insecure \
    --listen-addr="127.0.0.1:${sql_port}" \
    --http-addr="127.0.0.1:${http_port}" \
    --store=type=mem,size=0.10 \
    --temp-dir=/tmp \
    --logtostderr=ERROR \
    >/dev/null 2>&1
) &
cockroach_pid=$!

ready=false
for _ in {1..40}; do
  if "$cockroach_bin" sql --insecure --host="127.0.0.1:${sql_port}" \
      --execute='SELECT 1' >/dev/null 2>&1; then
    ready=true
    break
  fi
  sleep 0.25
done
if [[ "$ready" != true ]]; then
  echo "LOCAL_PROOF_RUNTIME_NOT_READY" >&2
  exit 2
fi

"$cockroach_bin" sql --insecure --host="127.0.0.1:${sql_port}" \
  --execute='CREATE DATABASE cockroach_kernel' >/dev/null

git -C "$base" show HEAD:p9-cloud/migrations/001_cloud.sql | \
  "$cockroach_bin" sql --insecure --host="127.0.0.1:${sql_port}" \
  --database=cockroach_kernel >/dev/null

old_constraint=$(
  "$cockroach_bin" sql --insecure --host="127.0.0.1:${sql_port}" \
  --database=cockroach_kernel --format=tsv \
  --execute="SELECT count(*) FROM [SHOW CONSTRAINTS FROM ck.context_vectors] WHERE constraint_name='context_vectors_vector_digest_key'"
)
[[ "$old_constraint" == "1" ]]

"$cockroach_bin" sql --insecure --host="127.0.0.1:${sql_port}" \
  --database=cockroach_kernel \
  --file="$base/p9-cloud/migrations/003_collision_safe_vector_digest.sql" >/dev/null

zero=$(printf '00%.0s' {1..32})
task_a=$(printf '11%.0s' {1..32})
task_b=$(printf '12%.0s' {1..32})
state_a=$(printf '21%.0s' {1..32})
state_b=$(printf '22%.0s' {1..32})
event_a=$(printf '31%.0s' {1..32})
event_b=$(printf '32%.0s' {1..32})
shared_digest=$(printf 'ab%.0s' {1..32})
vector='[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]'

"$cockroach_bin" sql --insecure --host="127.0.0.1:${sql_port}" \
  --database=cockroach_kernel --execute="
INSERT INTO ck.tasks VALUES
  ('t1','c','{}',decode('${task_a}','hex'),decode('${state_a}','hex')),
  ('t2','c','{}',decode('${task_b}','hex'),decode('${state_b}','hex'));
INSERT INTO ck.trajectory_events VALUES
  ('e1','t1',0,decode('${zero}','hex'),decode('${state_a}','hex'),'{}',decode('${event_a}','hex')),
  ('e2','t2',0,decode('${zero}','hex'),decode('${state_b}','hex'),'{}',decode('${event_b}','hex'));
INSERT INTO ck.context_vectors VALUES
  ('v1','t1',decode('${event_a}','hex'),'c','${vector}'::VECTOR(64),decode('${shared_digest}','hex')),
  ('v2','t2',decode('${event_b}','hex'),'c','${vector}'::VECTOR(64),decode('${shared_digest}','hex'));
" >/dev/null

counts=$(
  "$cockroach_bin" sql --insecure --host="127.0.0.1:${sql_port}" \
  --database=cockroach_kernel --format=tsv \
  --execute='SELECT count(*), count(DISTINCT vector_id), count(DISTINCT (task_id,event_hash,namespace)), count(DISTINCT vector_digest) FROM ck.context_vectors'
)
[[ "$counts" == $'2\t2\t2\t1' ]]

new_constraint=$(
  "$cockroach_bin" sql --insecure --host="127.0.0.1:${sql_port}" \
  --database=cockroach_kernel --format=tsv \
  --execute="SELECT count(*) FROM [SHOW CONSTRAINTS FROM ck.context_vectors] WHERE constraint_name='context_vectors_vector_digest_key'"
)
digest_index=$(
  "$cockroach_bin" sql --insecure --host="127.0.0.1:${sql_port}" \
  --database=cockroach_kernel --format=tsv \
  --execute="SELECT count(*) FROM [SHOW INDEXES FROM ck.context_vectors] WHERE index_name='context_vectors_vector_digest_idx'"
)
[[ "$new_constraint" == "0" ]]
[[ "$digest_index" == "1" ]]

printf '%s\n' \
  'STATUS=GREEN' \
  'OLD_UNIQUE_DIGEST_CONSTRAINT=1' \
  'NEW_UNIQUE_DIGEST_CONSTRAINT=0' \
  'DIGEST_LOOKUP_INDEX=1' \
  'ROWS=2' \
  'UNIQUE_VECTOR_IDS=2' \
  'UNIQUE_LINKAGES=2' \
  'UNIQUE_VECTOR_DIGESTS=1' \
  'STORE=MEMORY_ONLY' \
  'NETWORK=LOOPBACK_ONLY'
