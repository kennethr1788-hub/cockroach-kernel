# PDH-3 R12 R6 paid preflight attempt 01 blocked receipt R1

Status: `PDH3_R12_R6_BLOCKED`

- blocker: `PF4_PLATFORM_CAPABILITY_MISMATCH`;
- failure stage: `PF4_CAPABILITY`;
- last independently GREEN gate: `R6_R2_SAME_HASH_GLM_5_2_GREEN`;
- implementation commit at launch:
  `4942888e9de13bf53eea368eae75810bcfc600d7`;
- packet SHA-256:
  `29ffc52144045a12afdea754a5183c9c39d8739d3b936547b00e74b9906e8fbb`;
- runtime-config SHA-256:
  `e7999d50ef67c49393c28a5954a56156d8ab97493daf5b7e44fbfd05fae8c129`;
- direct GLM 5.2 raw verdict SHA-256:
  `7993750670e2b0f3d12648342d29fb674548bfa1dc1457f00625bb224e3a88ea`;
- authorization-envelope SHA-256:
  `e5fb1b999a84339b780a8c299817c9fa11b0aba38e582db766a2301e6594455b`.

## Provider lifecycle

- provider Pod ID: `qv3ve5s5i9eil1`;
- provider Pod name: `ck-pdh3-r12-preflight-r6-20260802b-01`;
- returned worker: Secure Cloud L40S, 16 allocated vCPU, 188 GiB
  allocated RAM, 250-GB disposable container disk, zero persistent/network
  volume, `$0.99/hour`;
- worker-ready receipt UTC: `2026-08-02T08:27:53Z`;
- lifecycle `TEARDOWN_GREEN` UTC: `2026-08-02T08:28:30Z`;
- closeout verification UTC: `2026-08-02T08:28:49Z`;
- worker created: `true`;
- minimal PF-4 payload uploaded: `true`;
- main project bundle uploaded: `false`;
- product preflight workload started: `false`;
- 24-hour measured campaign started: `false`;
- worker deleted: `true`;
- exact-ID lookup after deletion: absent;
- active campaign inventory after deletion: `[]`;
- exact attributable provider charge: `unavailable`; the returned rate and
  observed lifecycle are recorded, but no invoice amount is inferred.

## PF-4 result

The worker passed the declared CPU, RAM, disk-total, disk-available,
disk-used-fraction, sequential-write, sustained-write, fsync, random-sync,
process-tree, monotonic-clock, and benchmark-residue checks. Observed values
included:

- 16 effective vCPU;
- 201,863,462,912 effective RAM bytes;
- 268,435,456,000 total disposable disk bytes;
- sequential throughput `6264.647819701981 MiB/s`;
- sustained throughput `6227.869439422365 MiB/s`;
- fsync p99 `0.172408 ms`;
- random-sync throughput `7131.509572615842 IOPS`.

Two required checks failed:

1. `cgroup`: `/sys/fs/cgroup/cpu.stat`, `memory.current`, `memory.events`,
   `io.stat`, and `pids.current` were all absent on the returned container.
   The frozen probe requires all five cgroup-v2 root files.
2. `streaming_network_observer`: the pinned observer returned `1`; its stderr
   SHA-256 was
   `42982b7f8634b5ba4fca5a0b90b762e128314f37594967503837f4eeed9fecc1`,
   and no network probe or capability receipt was emitted. The current PF-4
   retrieval path retained the command hash and receipt-level hashes but did
   not retrieve the observer's raw stderr, so the provider-side submechanism
   is not asserted.

The PF-4 capability receipt is therefore honestly non-GREEN. The main bundle
was never uploaded, so this attempt is not product-workload evidence.

## Credential boundary

Kenneth authorized reading the existing host RunPod config solely to inject the
API key into the local controller process environment. The key was not printed,
placed in argv, committed, or written into R6 evidence. The lifecycle guard's
project-local config shim contains an empty `apikey` field and the same
non-secret API URL as the host config. A byte-for-byte scan of the full R6
runtime found zero copies of the host API key after closeout.

## Evidence hashes

- create response SHA-256:
  `834c5f08ceb7eef17aad0ba5ba7a80cf0a02662aabbb50c43eadc0d24fc52c79`;
- detailed Pod receipt SHA-256:
  `dc181aef0b56854e1250fa7a3a5cdbbf878c75ee11214aa2ab65beea74b4bb1f`;
- PF-4 failure receipt SHA-256:
  `e2d6784d717192a2ffb2e2bc0ac434c7904fec69531b2fc760ad162afce99fd4`;
- orchestrator blocked receipt SHA-256:
  `ddb3f8fbe7db6d106f4ba227a4134d7ee40a11a4811acfc840fe20d6f67567fa`;
- delete response SHA-256:
  `83dcbbdddacd556b5cf51d90c163f716b9d9541573480896c9023085b3085bfd`;
- lifecycle hash chain SHA-256:
  `a77bb0371bfbd0085f107e5a10491ca1c8df8040bc2bb5b680c54c00c8546d78`;
- PF-4 command stderr SHA-256:
  `03fa3e4f6dd41ffb60bcad4e5b4c49e5927bc22f41a6a3caeab37cf33861623c`.

Before the provider attempt, a detached host launcher was reaped by the local
execution surface after creating only the empty runtime directory. A supervised
retry then failed closed because the directory existed. Those host-only
artifacts were preserved under:

`.pdh3-runtime/r12-preflight/r6-20260802b-host-launch-fail-20260802T082554Z/`

No provider mutation occurred in either host-only failure.

## Retry and resume boundary

Section 7 of the frozen R2 packet requires PF-4 to stop without replacement on
any semantic failure. Attempt 01 is therefore consumed and attempts 02-03 may
not be used to repeat this platform mismatch under the same packet hash.

A replacement preflight requires a prospective platform amendment that:

1. discovers and binds the provider's actual cgroup accounting interface
   without weakening resource-accounting requirements;
2. retrieves the network observer's raw stdout, stderr, and partial evidence
   before teardown;
3. proves the pinned observer on the selected Secure Cloud surface through a
   smallest paid capability canary;
4. freezes a new packet and receives fresh same-hash independent GREEN; and
5. receives a fresh operator authorization bound to that new packet.

Until those steps pass, the exact status is `PDH3_R12_R6_BLOCKED`. The
24-hour campaign is not authorized to start from this evidence.
