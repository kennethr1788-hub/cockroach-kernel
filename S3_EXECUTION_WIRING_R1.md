# S3 Exact Execution Wiring R1

- `STATUS`: `FROZEN_BEFORE_RUNPOD_CREATION`
- `SCHEMA_VERSION`: `s3-execution-wiring-v1`
- `RUNPODCTL_SHA256`: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`
- `THRESHOLDS_SHA256`: `14c4768ad450d34e5e44a5b8e5f5a602ef2b92fb5d0228b336f79b9d7e4bb006`
- `RESOURCE_ALLOWLIST_SHA256`: `a1993801ce17c4f4a5894720fcfab5cd96715f3f9b0ce03b3919430ea837e3aa`
- `UTC_FROZEN`: `2026-07-26T23:25:00Z`

Every angle-bracket value below is resolved once into a canonical attempt
receipt before execution. IDs must match the protocol identifier grammar;
epochs are base-10 integers; host, port, Pod ID, and PIDs come only from the
verified provider response or newly started process. No value is evaluated as
shell, SQL, URL, ARN, path traversal, or an extra argument.

## Creation

```text
/tmp/runpodctl-v2.7.2-darwin-arm64 pod create
  --compute-type cpu
  --template-id runpod-ubuntu-2204
  --image runpod/base:1.0.2-ubuntu2204
  --name <ATTEMPT_NAME>
  --container-disk-in-gb 20
  --volume-in-gb 0
  --ports 22/tcp
  --ssh
  --stop-after <STOP_ISO_UTC>
  --terminate-after <TERMINATE_ISO_UTC>
  --output json
```

The returned worker must be exactly 2 vCPU / 8 GiB, CPU-only, zero GPU and
zero volume, at no more than $0.10/hour including disk. A mismatch is deleted
before upload and may consume only a pre-start retry.

## Host-local exact-ID lifecycle guard

```text
screen -dmS <LIFECYCLE_SESSION> caffeinate -dimsu
  python3 s2-soak/lifecycle_guard.py
  --runpodctl /tmp/runpodctl-v2.7.2-darwin-arm64
  --runpodctl-sha256 a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037
  --pod-id <POD_ID>
  --pod-name <ATTEMPT_NAME>
  --campaign-prefix <CAMPAIGN_PREFIX>
  --stop-epoch <STOP_EPOCH>
  --delete-epoch <DELETE_EPOCH>
  --heartbeat-seconds 30
  --log <LOCAL_ATTEMPT_ROOT>/lifecycle.ndjson
```

## Host coordinator

```text
screen -dmS <COORDINATOR_SESSION> caffeinate -dimsu
  python3 s3-soak/host_coordinator.py
  --bridge-root <LOCAL_ATTEMPT_ROOT>/bridge
  --evidence-root <LOCAL_ATTEMPT_ROOT>/coordinator-evidence
  --campaign-id <CAMPAIGN_ID>
  --expected-requests 12
  --lambda-call-ceiling 12
  --cockroach-operation-ceiling 108
  --deadline-epoch <DELETE_EPOCH>
  --mode live
  --config <IGNORED_PROJECT_RUNTIME_CONFIG>
  --heartbeat-seconds 5
  --completion-marker <LOCAL_ATTEMPT_ROOT>/worker-complete
```

## SSH bridge

```text
screen -dmS <BRIDGE_SESSION> caffeinate -dimsu
  python3 s3-soak/remote_bridge.py
  --host <VERIFIED_SSH_HOST>
  --port <VERIFIED_SSH_PORT>
  --user root
  --identity <ATTEMPT_SCOPED_PRIVATE_KEY>
  --known-hosts <ATTEMPT_SCOPED_KNOWN_HOSTS>
  --remote-root /workspace/<CAMPAIGN_ID>/bridge
  --local-root <LOCAL_ATTEMPT_ROOT>/bridge
  --campaign-id <CAMPAIGN_ID>
  --expected-requests 12
  --deadline-epoch <DELETE_EPOCH>
  --heartbeat-seconds 30
  --log <LOCAL_ATTEMPT_ROOT>/bridge.ndjson
```

## Coordinator guard

```text
screen -dmS <COORDINATOR_GUARD_SESSION> caffeinate -dimsu
  python3 s3-soak/coordinator_guard.py
  --coordinator-pid <COORDINATOR_PID>
  --bridge-pid <BRIDGE_PID>
  --runpod-guard-pid <LIFECYCLE_GUARD_PID>
  --coordinator-log <LOCAL_ATTEMPT_ROOT>/coordinator-evidence/coordinator.ndjson
  --bridge-log <LOCAL_ATTEMPT_ROOT>/bridge.ndjson
  --runpod-guard-log <LOCAL_ATTEMPT_ROOT>/lifecycle.ndjson
  --completion-marker <LOCAL_ATTEMPT_ROOT>/worker-complete
  --protocol-file s3-soak/protocol.py
  --protocol-sha256 20bfeac7bf3923394fa193343c904b67bde3efee62561b530fad6ff96d41178c
  --resource-allowlist S3_RESOURCE_ALLOWLIST_R1.json
  --resource-allowlist-sha256 a1993801ce17c4f4a5894720fcfab5cd96715f3f9b0ce03b3919430ea837e3aa
  --lambda-call-ceiling 12
  --cockroach-operation-ceiling 108
  --runpodctl /tmp/runpodctl-v2.7.2-darwin-arm64
  --runpodctl-sha256 a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037
  --pod-id <POD_ID>
  --pod-name <ATTEMPT_NAME>
  --campaign-prefix <CAMPAIGN_PREFIX>
  --deadline-epoch <DELETE_EPOCH>
  --stale-seconds 90
  --startup-grace-seconds 60
  --log <LOCAL_ATTEMPT_ROOT>/coordinator-guard.ndjson
  --stop-marker <LOCAL_ATTEMPT_ROOT>/stop.json
```

## Remote production worker

```text
python3 s3-soak/worker.py
  --cockroach-bin runtime/cockroach-v26.2.3.linux-amd64/cockroach
  --output-root /workspace/<CAMPAIGN_ID>/production
  --bridge-root /workspace/<CAMPAIGN_ID>/bridge
  --campaign-id <CAMPAIGN_ID>
  --duration-seconds 43200
  --checkpoint-seconds 300
  --safety-seconds 900
  --hourly-seconds 3600
  --coordinator-timeout-seconds 300
  --database-growth-limit-bytes 536870912
  --evidence-growth-limit-bytes 16777216
  --rss-limit-bytes 1610612736
  --open-files-limit 128
  --production
```

The remote command is passed as a fixed argument vector over verified SSH; it
is not constructed from worker content. The 60-second Linux smoke uses fresh
roots and the same explicit thresholds scaled only in duration/cadence. The
production timer starts only after `S3_CAMPAIGN_READY` is receipted.

## Post-start image/runtime evidence

```text
/tmp/runpodctl-v2.7.2-darwin-arm64 pod get <POD_ID> --output json
/usr/bin/ssh <PINNED_SSH_OPTIONS> root@<VERIFIED_SSH_HOST>
  uname -m
  cat /etc/os-release
  sha256sum /bin/bash /usr/bin/python3
```

The provider JSON must echo the exact configured image name. Registry index and
linux/amd64 manifest digests are preserved from the preflight lookup. RunPod
does not expose a cryptographic image-digest readback for this CPU Pod surface;
the receipt must state that limitation and may not claim stronger proof.

## Completion and teardown

After the worker exits GREEN and its complete evidence tree is retrieved and
hash-verified, the host creates the local completion marker. The coordinator
must then emit `COORDINATOR_GREEN`, the bridge must emit `BRIDGE_GREEN`, and the
coordinator guard must emit `COORDINATOR_GUARD_GREEN`. The exact-ID lifecycle
guard or explicit closeout then stops/deletes the Pod with bounded retries.
Exact-ID absence plus empty S3-scoped running/all-status inventory is required.

If any PID, hash, call count, deadline, path root, provider identity, evidence
count, or resource limit differs, execution stops and the Pod is torn down.
