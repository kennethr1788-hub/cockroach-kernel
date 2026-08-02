# PDH-3 R12 R6 PF-4 retry attempt 01 blocked receipt R1

Status: `PF4_RETRY_ATTEMPT_01_BLOCKED__TEARDOWN_GREEN`

UTC created: `2026-08-02T10:55:00Z`

## Bound execution

- packet SHA-256:
  `5afd8dc0f027211fed6361569da254ebfcfaa60fb6ae4bc8945e07d63d0a2a0a`;
- independent GLM 5.2 preflight: GREEN on that exact hash;
- campaign: `ck-pdh3-r12-preflight-r6-pf4-usmo-r1`;
- attempt: 1;
- Pod ID: `scdti1prghpxbv`;
- created: `2026-08-02T10:48:25Z`;
- closed: `2026-08-02T10:50:13Z`;
- main bundle uploaded: false;
- measured 24-hour clock started: false.

## Returned worker and measured result

- Secure Cloud L40S;
- datacenter: `US-MO-1`;
- provider readback: 16 vCPU / 125 GiB / `$0.99/hour`;
- provider readback SHA-256:
  `b755b932c074aa8cbc6d0c9dab1474136d98ec011c625bc68d04491f2bf0b76d`;
- exact 16-CPU affinity application/readback: GREEN;
- real cgroup v2 effective CPU quota: 13;
- fixed PF-4 minimum: 16;
- PF-4 verdict: BLOCKED;
- all other PF-4 checks: GREEN, including RAM, disk, fsync, sequential and
  sustained I/O, random-sync IOPS, process/resource accounting, network
  observer capability, and residue.

Evidence:

| Artifact | SHA-256 |
|---|---|
| `PF4_CAPABILITY_RECEIPT.json` | `7b2114d7e12f830a3c91395b450beb07b40a4b7636d70ed69a6607980890e8bf` |
| `PF4_FAILURE_RECEIPT.json` | `7b2114d7e12f830a3c91395b450beb07b40a4b7636d70ed69a6607980890e8bf` |
| `PF4_ONLY_TERMINAL.json` | `af03f9f71ba4e27c43b85f50445e710e634aed6cfcb3762eebb9acb8fcf904ae` |
| `attempt-01/lifecycle.ndjson` | `affbd7b04cb954afada0e223896e806c1843b03dc0e53ea1008910824bc88e65` |
| `pf4-post-delete-inventory.json` | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |
| `attempt-ledger.json` | `3e79229df624f68c5f58ebbca8a653380d38f61ea7f9b56a5833719382460816` |

## Teardown

- worker deleted: yes;
- exact ID absent: yes;
- campaign inventory: `[]`;
- lifecycle terminal event: `TEARDOWN_GREEN`;
- lifecycle terminal event hash:
  `7f1557436ac8d92d8bb5c54cad239942c70d80731f360318a67e3b2e1b97963a`;
- terminal receipt hash:
  `1de30a5c15f74a721aaa1cc84cf939183873514517e78da80b07334edc125166`.

## Diagnosis and next correction

Pinning `US-MO-1` did not force the historical 32-vCPU shape. The scheduler
returned a 16-vCPU machine and the container quota again exposed only 13
effective CPUs. This is the second consecutive occurrence of the same
load-bearing capability failure. Blind placement retries are therefore not a
defensible correction.

Current official RunPod GraphQL documentation exposes `minVcpuCount` together
with `stopAfter` and `terminateAfter` on
`PodFindAndDeployOnDemandInput`. The current official `runpodctl` source exposes
the deadline fields but omits a CLI binding for `minVcpuCount`.

The smallest prospective correction is a host-local, credential-safe GraphQL
creation path using an Authorization header, `minVcpuCount: 24`, unchanged
Secure L40S/image/disk/volume/price/deadline constraints, and post-create
readback requiring at least 24 provider vCPUs. The fixed real cgroup minimum
remains 16. This repair requires new source hashes, tests, packet, and fresh
same-hash GLM 5.2 GREEN before another worker.

Official sources:

- `https://docs.runpod.io/sdks/graphql/manage-pods`;
- `https://docs.runpod.io/references/graphql-spec`;
- `https://github.com/runpod/runpodctl/blob/main/cmd/pod/create.go`;
- `https://github.com/runpod/runpodctl/blob/main/internal/api/graphql.go`.
