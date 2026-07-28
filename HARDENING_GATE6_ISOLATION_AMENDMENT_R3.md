# Hardening Gate 6 — Isolation and Platform Amendment R3

- `STATUS`: `FROZEN_FOR_INDEPENDENT_PREFLIGHT`
- `EXECUTION_REVISION`: `R3`
- `PARENT_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `PRIOR_BLOCKER`: `UNPRIVILEGED_NETWORK_NAMESPACE_UNAVAILABLE`
- `REPLACEMENT_MECHANISM`: `UNPRIVILEGED_NO_NEW_PRIVS_INHERITED_SECCOMP_BPF`
- `NETWORK_NAMESPACE_CLAIM`: `NOT_MADE`

## Evidence-driven change

R2 directly proved that the reviewed RunPod container rejects
`unshare --user --map-root-user --net --mount-proc` with `Operation not
permitted`. No measured row ran. R3 does not relabel that failure or claim a
namespace exists. It replaces the unavailable namespace with a kernel-enforced
network-denial boundary that an unprivileged process can install without a
capability, host firewall change, privileged container, or provider setting.

The immutable product candidate, six scenarios, three methods, three
repetitions, method rotation, success rules, comparator source, verifier, tool
versions, and 54-row evidence contract do not change. Only Gate 6 execution
infrastructure changes.

## Kernel contract

`hardening-gate6/seccomp_exec.py` must run on Linux x86_64 as UID/EUID 10001
with `CapEff=0`, no inherited socket file descriptor, and an empty fixed
environment. It then:

1. calls `prctl(PR_SET_NO_NEW_PRIVS, 1)`;
2. installs a classic seccomp-BPF filter using
   `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, ...)`;
3. kills a foreign syscall architecture;
4. returns `EPERM` for every declared x86_64 socket syscall and for alternate
   kernel paths that could create, submit, or acquire network work (`bpf`,
   `io_uring_*`, `pidfd_getfd`, `setns`, and `unshare`);
5. permits ordinary file, process, Git, Restic, and verifier operations;
6. proves `/proc/self/status` reports `NoNewPrivs=1` and `Seccomp=2`;
7. proves an AF_INET socket creation fails with `EPERM` and `/bin/true` can
   execute;
8. fsyncs a canonical hash-bound attestation; and
9. `exec`s the measured orchestrator without clearing the filter.

Linux seccomp filters and `no_new_privs` are inherited across fork and exec and
cannot be relaxed by the filtered unprivileged process. All 54 method children
therefore execute under the same kernel filter. The R3 runner independently
checks UID, capability state, kernel seccomp state, attestation bytes/hash, and
another real AF_INET denial before the first measured row.

## Pre-upload capability canary

Before any benchmark payload upload, a returned worker may receive only the
hash-bound `seccomp_exec.py` canary. Root may create the disposable UID 10001
and its output directory, then the canary must run as that user with a fixed
empty environment. A valid canary requires:

- exact script SHA-256;
- Linux x86_64;
- UID/EUID 10001 and nonzero;
- `CapEff=0000000000000000`;
- no inherited socket descriptor;
- `NoNewPrivs=1` and `Seccomp=2` after installation;
- filter-spec hash agreement;
- AF_INET creation denied with `EPERM`;
- child exec canary PASS; and
- canonical attestation hash agreement.

Failure before benchmark upload permits teardown and a sequential provider
retry. Three consecutive identical capability failures stop blind retrying for
bounded diagnosis and fresh review. Any mismatch, secret exposure, undeclared
egress, inability to delete, or unknown price is non-retryable.

## Limits and honest claims

This is process-tree network denial, not a network namespace, VM boundary,
container escape defense, host firewall, or proof about unrelated processes.
The remote root setup lane can use the already-open SSH control path; measured
code cannot create or acquire a network socket. The benchmark remains
synthetic, team-authored, `n=3` per class/method, and not population evidence.

Any judge rejection of this replacement mechanism preserves Gate 6 BLOCKED.
No fallback to an in-process monkeypatch, socket shim, root execution, or
unfiltered measurement is allowed.
