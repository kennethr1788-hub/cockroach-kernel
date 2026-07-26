# S2 Transfer and Inventory Receipt R1

- `UTC_CREATED`: `2026-07-26T01:50:24Z`
- `IMPLEMENTATION_COMMIT`: `19979c92ca54a744b88317d043644f04f1b51892`
- `CAMPAIGN_ID`: `CK-S2-20260726-ORCHESTRATION-R1`
- `ATTEMPT_PREFIX`: `ck-s2-20260726-r1-`
- `TRANSFER_ARCHIVE`: `/tmp/ck-s2-20260726-r1.tar.gz`
- `TRANSFER_BYTES`: `144473579`
- `TRANSFER_SHA256`: `a35a6786b5d88393ee13cad83ad742759062c0b7b567062aa9bfbbbd3c725273`
- `TREE_MANIFEST`: `/tmp/ck-s2-payload-r1.manifest.sha256`
- `TREE_MANIFEST_LINES`: `61`
- `TREE_MANIFEST_SHA256`: `c3cc695f261bfef6a1ccbd8aa86e688d4f9bcdb06c2361cd50dbcb9ec96cd1c0`
- `LINUX_RUNTIME_ARCHIVE_SHA256`:
  `3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`
- `LINUX_RUNTIME_BINARY_SHA256`:
  `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`

## Transfer contents

Only Git-committed P3–P7 source/migrations/fixtures, S2 workload source and
README, and the already-checksum-verified CockroachDB v26.2.3 Linux archive are
present. Local smoke outputs, lifecycle credentials, CLI state, HOME files,
model configuration, account details, AWS, Qdrant, StateV2, client data, and
unrelated source are excluded.

- symlinks: zero;
- private/absolute-home path scan: zero findings;
- gitleaks: exit 0, no leaks;
- detect-secrets: zero files and zero findings;
- detect-secrets report SHA-256:
  `56f86775e23c8ff584aa0271db73706cb2c406da9154c27aaf5666fd68564e5d`.

Remote extraction must regenerate the 61-line sorted SHA-256 manifest and
match its hash before any smoke or workload execution. The Linux runtime
archive and extracted binary must separately match their frozen hashes.

## Authenticated provider inventory

- Verified RunPod CLI path: `/tmp/runpodctl-v2.7.2-darwin-arm64`.
- Version: `2.7.2-309512b`.
- SHA-256:
  `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`.
- Official public CPU template: `runpod-ubuntu-2204`.
- Exact image: `runpod/base:1.0.2-ubuntu2204`.
- S2-active inventory at freeze: empty.
- Unrelated active inventory: one resource, preserved and out of scope.
- Unrelated pre-existing network volume: one, preserved and never attached.
- Historical authenticated CPU return rates visible in current provider
  inventory: $0.06, $0.08, and $0.11/hour. Only a returned 2-vCPU/4-GiB worker
  at no more than $0.06 or 2-vCPU/8-GiB worker at no more than $0.08 is
  accepted. Every other return is deleted before upload.

The CLI exposes the official CPU template but not a pre-create live CPU shape
quote. Therefore the exact creation response is the authoritative current
inventory/price proof. This is fail-closed: no upload occurs until the returned
shape, compute rate, image, disk, volume, GPU count, name, and deadlines match
the independently approved envelope.

## Frozen lifecycle and spend

- First attempt not before: `2026-07-26T02:10:00Z`.
- First attempt deadline: `2026-07-26T02:20:00Z`.
- Retry-window hard end: `2026-07-26T03:05:00Z`.
- Campaign-ready/workload-start deadline: `2026-07-26T03:20:00Z`.
- Provider stop-after: `2026-07-26T10:00:00Z`.
- Provider terminate-after: `2026-07-26T10:10:00Z`.
- Detached guard stop epoch: `1785060000`.
- Detached guard delete epoch: `1785060600`.
- Maximum creation attempts: eight, sequential, one S2 worker at a time.
- Accepted compute: CPU only, exactly 2 vCPU and 4 or 8 GiB RAM.
- Maximum compute rate: $0.08/hour.
- Maximum active rate including 20 GB disposable storage: $0.085/hour.
- Maximum successful-worker paid lifetime: eight hours.
- Maximum aggregate exposure: $0.75, below the prompt ceiling of $2.00.
- Persistent/network volume: none; GPU: zero.

Attempt names are `ck-s2-20260726-r1-a01` through `a08`. The creation request
family is:

```text
/tmp/runpodctl-v2.7.2-darwin-arm64 pod create --compute-type cpu --template-id runpod-ubuntu-2204 --container-disk-in-gb 20 --volume-in-gb 0 --name <attempt> --stop-after 2026-07-26T10:00:00Z --terminate-after 2026-07-26T10:10:00Z --output json
```

No worker exists yet. Creation is forbidden until GLM and Claude return GREEN
on the exact frozen S2 preflight packet hash.
