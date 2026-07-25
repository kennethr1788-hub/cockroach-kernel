# S1 Retry Attempt 01 Receipt

- `CAMPAIGN_ID`: `CK-S1-20260725-FOUNDATION-R3`
- `ATTEMPT`: `1`
- `ATTEMPT_NAME`: `ck-s1-20260725-r3-a01`
- `POD_ID`: `wo1iq5wtk04q49`
- `PACKET_SHA256`: `82fc0dcdd38a814e40a39f85c57b1f35948d46792575c7fdd2db24283768ef87`
- `CREATED_UTC`: `2026-07-25T21:40:03.961Z`
- `SSH_READY_UTC`: `2026-07-25T21:40:47Z`
- `RESULT`: `WORKER_VERIFIED`

## Provider properties

- compute type: CPU;
- vCPU: 2;
- RAM: 4 GB provider allocation;
- compute rate: $0.06/hour;
- active rate including 20 GB storage: $0.064/hour;
- image: `runpod/base:1.0.2-ubuntu2204`;
- container disk: 20 GB;
- persistent/network volume: 0 GB / none;
- GPU count: 0;
- Secure Cloud region: `US-NC-1`;
- provider desired status: `RUNNING`;
- create command accepted exact auto-stop `2026-07-26T00:05:00Z` and
  auto-terminate `2026-07-26T00:10:00Z` flags; the Pod read schema does not
  echo deadline fields.

The returned worker is one of the two independently approved shapes. Remote
probe confirmed Linux x86_64, 2 CPUs, Python 3.10.12, a 20 GB container
filesystem, and only the provider `.cache` entry in `/workspace`. No payload
had been uploaded at verification.

## Raw-evidence hashes

- create response SHA-256:
  `bcd3abf3d0fadc624da7eac982ac515780e27c0cbd66d538f757c69bb7f96737`;
- Pod get response SHA-256:
  `7e44d9a7523adb10e9cb98f9e01406069876598d8141b96bd0a83a3b0910730e`;
- SSH info response SHA-256:
  `55b5cfab467cebf86cea9a2b9c58933ce0ab1db3c6fab129811a6ae64847f423`;
- pinned known-hosts SHA-256:
  `a8dfebe7264202efd81aa677c0a5ea589d9b8639452809884fd0ff908e8cd41b`.

Creation retries are permanently closed for this campaign. This receipt does
not claim workload or final S1 GREEN.
