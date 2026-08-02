# PDH-3 R12 Preflight Platform Repair Amendment R1

Status: `FROZEN_FOR_INDEPENDENT_REVIEW__NO_RUNPOD_LAUNCH`

UTC frozen: `2026-08-02T07:28:24Z`

Builder: `Codex / Icarus`

Parent plan:
`PDH3_R12_EXTENSIVE_PREFLIGHT_PLAN_20260802_R1.md`

Parent plan SHA-256:
`a1214b4779fe1495de219ed0033421ac810390641cd97742deb61cd3957df3d9`

R5 blocked receipt:
`PDH3_R12_REMOTE_PREFLIGHT_BLOCKED_R5.md`

R5 blocked-receipt SHA-256:
`f36e0980ee37c1944116da378be5e79ca93f99afa43fc5173985340f4680fce7`

Repair implementation commit:
`97fca76bdb246c02ee4e14d1a4f846d4114071e5`

## 1. Verified R5 facts

R5 created one Secure Cloud L40S worker, Pod ID `5ommwuqsbffrl0`. The
provider response reported 32 vCPU and 125 GiB RAM. That shape is below the
frozen 4 GiB-per-vCPU floor because `125 / 32 == 3.90625`. The worker also did
not expose the exact unprivileged user/network/PID namespace capability frozen
in R5. The host lifecycle guard did not reach a validated, hash-chained `BOUND`
event because its credential was removed from the local guard environment.

PF-4 stopped before the main application bundle was uploaded. No product
workload ran and no 24-hour measured clock started. Evidence was retrieved,
the worker was deleted, exact-ID lookup returned absent, and active inventory
was empty. R5 remains immutable failed evidence.

## 2. Scope of this amendment

This is a prospective repair to PF-4 and the remote observer path. It does not
change the product candidate, target cardinality, 500-worker workload, SQL
latency thresholds, 15-minute growth gate, 24-hour duration, 24 fault cycles,
9,976 verifier executions, evidence requirements, or teardown law. It does
not retroactively reclassify R5.

This amendment does not authorize a worker. The R5 worker authorization was
consumed. A new paid worker requires a fresh, explicit operator authorization
over a separately frozen execution packet.

## 3. Effective resource accounting and returned-shape rejection

PF-4 now binds three resource surfaces:

1. provider-returned allocated vCPU and RAM;
2. cgroup v2 CPU quota/cpuset and memory maximum when finite; and
3. process CPU affinity.

Host `/proc/meminfo` and `os.cpu_count()` remain diagnostic only. Effective
vCPU is the minimum of the provider allocation and enforceable cgroup/affinity
limits. Effective RAM is the minimum of provider RAM and any finite cgroup
memory limit.

Before the main bundle is uploaded, the returned allocation must satisfy all
of the following:

- at least 16 effective vCPU;
- at least 94 GiB effective RAM;
- at least 4 GiB effective RAM per effective vCPU;
- exactly 250 GB disposable container disk;
- zero persistent/network volume;
- the frozen image, Secure Cloud, rate, name, and lifecycle deadlines.

A returned L40S shape such as 32 vCPU / 125 GiB is a mismatch. It must be
deleted before the main bundle upload and cannot be made compliant by ignoring
provider-returned CPU count or substituting host values. Sequential replacement
attempts, if any, require an explicit count/cost envelope in the later execution
packet and fresh operator authorization.

## 4. Prospective network-proof replacement

The exact unprivileged user/network/PID namespace requirement is removed from
PF-4 because the verified R5 RunPod container did not expose it. It is replaced
prospectively by the following bounded, hash-pinned, low-volume observation
mechanism:

- the bundled Ubuntu Noble `strace` and `libunwind8` artifacts are verified by
  SHA-256 and extracted into a generated campaign-local root without a global
  install;
- the observer launches before the tested process and `strace -f` follows that
  process tree across forks and threads;
- `connect`, `sendto`, and `sendmsg` destinations are classified;
- loopback, Unix, netlink, AF_UNSPEC, and destinationless sends on a connection
  whose connect was observed are permitted;
- any external or unparseable destination terminates the tested process group
  and makes the gate non-GREEN;
- trace bytes are parsed from an inherited pipe and hash-accounted but are not
  retained in full;
- 30-second hash-chained summaries, container network-counter deltas, and no
  more than 64 bounded raw trace samples are retained;
- observer loss terminates the descendant workload through the
  observer-to-tracer-to-workload parent-death chain;
- the capability canary proves only tracer extraction, process-tree following,
  loopback classification, receipt creation, and clean termination;
- the 15-minute PF-7 canary must project no more than 1 GiB of retained
  network-proof evidence over 24 hours before a final campaign packet can be
  frozen.

The public and internal claim boundary is explicit: this is observation plus
fail-closed termination after an observed syscall, not a preventive firewall,
network namespace, or proof that no packet could have left before detection.
It covers only the launched synthetic workload process tree. Unrelated
container control-plane processes and encrypted payload content are outside its
claim. No artifact may describe the campaign as `network denied` or as proving
preventive egress isolation.

## 5. Host lifecycle repair

The RunPod API credential remains only on the operator host. A new host-only
launcher:

- creates an empty generated HOME for the local guard;
- passes only an allowlisted environment plus `RUNPOD_API_KEY` to the local
  exact-ID guard;
- never places the credential in argv, logs, receipts, the transfer archive, or
  the worker;
- double-forks and proves PPID 1;
- validates the entire hash chain; and
- declares startup GREEN only after an exact identity-matching `BOUND` event.

`GUARD_BLOCKED`, tampering, premature exit, timeout, or identity mismatch is a
terminal non-GREEN result. File existence, PPID detachment, or a process being
alive is not sufficient evidence of lifecycle readiness.

## 6. Rebuilt candidate evidence

Two independent builds over commit `97fca76` produced the same archive:

- archive bytes: `143984633`;
- archive SHA-256:
  `69b5923882c459baf93b4a0baec458648adfc56671528dbf2c2623eceff9faaf`;
- archive-verification SHA-256:
  `b171670d006f975bd328a9a6c8e91fa3ba9ade2a5bfd930c0bac2d75a78c58a4`;
- manifest SHA-256:
  `549101b20ab9d28082c7a0fbe7a7a318b01dbb3526953dd29e1f9047791ab741`;
- source-set SHA-256:
  `5c6da7e7228f0949e473d7ac5c9e548718cfd5da17002961cd0106e5db595a25`;
- host-only source-set SHA-256:
  `eb7ffb4c81ff8df94c2e72f17cf90cbd6d712d0ba8c3d2a3027b030d2599444f`;
- attempt-history manifest SHA-256:
  `72877c307496cd57d910385c8aa898c779d449170f7134478eb5d2a2702cbe1e`.

Both extracted-bundle smoke suites returned GREEN. Their evidence class is
`EXTRACTED_BUNDLE_INTEGRITY_SMOKE_ONLY`; they do not prove Linux observer
behavior, target-scale execution, remote hardware, or a 24-hour campaign.

The platform repair has 41 focused R12 tests GREEN, and the two extracted
smokes each compiled 33 Python files and ran the frozen 12-program smoke
matrix. These tests are implementation evidence, not an independent gate.

## 7. Non-negotiable next-gate order

1. independent review of this exact amendment and its bound source hashes;
2. freeze a new paid-preflight execution packet with exact current price,
   creation-attempt count, absolute provider stop/terminate deadlines, and
   aggregate cost ceiling;
3. fresh human authorization for that paid packet;
4. fresh same-hash independent preflight review;
5. only then create a worker;
6. reject and delete a mismatched returned shape before the main bundle upload;
7. run repaired PF-4;
8. upload the main bundle only after PF-4 GREEN;
9. run PF-2R through PF-7 and final same-hash independent review;
10. freeze and independently review a separate final 24-hour packet;
11. start the 24-hour clock only when every preflight gate is directly GREEN.

No result from this amendment alone authorizes a worker or certifies any
remote stage.

## 8. Judge question

Return exactly:

```text
SERVED_MODEL: glm-5.2
TARGET_AMENDMENT_SHA256: <exact hash supplied with request>
TARGET_IMPLEMENTATION_COMMIT: 97fca76bdb246c02ee4e14d1a4f846d4114071e5
VERDICT: GREEN | NOT_GREEN | BLOCKED | JUDGE_UNAVAILABLE
CRITICAL_FINDINGS:
- <finding or NONE>
HIGH_FINDINGS:
- <finding or NONE>
REQUIRED_CORRECTIONS:
- <correction or NONE>
RATIONALE: <concise evidence-based explanation>
```

GREEN means only that this prospective repair is coherent enough to use in a
new paid-preflight packet. It does not approve RunPod creation or the 24-hour
campaign.
