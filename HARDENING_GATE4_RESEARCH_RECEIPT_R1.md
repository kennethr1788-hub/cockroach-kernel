# Hardening Gate 4 — Recovery Baseline Research Receipt R1

- `GATE`: `HARDENING_RUN_GATE_4_BASELINE_PROTOCOL`
- `PARENT_GATE`: `HARDENING_3_REAL_WORKFLOW_GREEN`
- `RESEARCH_MODE`: current official documentation plus local read-only runtime inventory
- `RESEARCHED_UTC`: `2026-07-27T20:16:53Z`
- `NETWORK_MUTATION`: none
- `PROVIDER_MUTATION`: none
- `DEPENDENCY_INSTALLATION`: none
- `HOME_MUTATION`: none
- `SELECTION`: `ORDINARY_GIT_REFERENCE` plus `GIT_PLUS_RESTIC_0_19_0`
- `GLOBAL_BEST_CLAIMED`: no

## Question

Which conventional recovery method is the strongest freely reproducible fit
for a benchmark where a developer workspace is deliberately lost, the recovery
store must survive outside that workspace, no paid account or private
credential may be required, and every trial must run identically on a disposable
Linux worker?

“Strongest” is scoped to that frozen benchmark, not to every backup product or
real deployment. The required fit criteria are:

1. open-source license permitting redistribution and reproducible testing;
2. local filesystem repository with no account or network service;
3. command-line capture and restore suitable for a deterministic harness;
4. named immutable snapshots or archives;
5. repository-integrity verification;
6. restore into a new empty destination;
7. support on the declared macOS development surface and Linux evidence worker;
8. ability to retain committed, uncommitted, and untracked workspace bytes;
9. no root privilege, daemon, filesystem snapshot, Docker, GPU, or paid service;
10. a configuration that can be disclosed completely and reproduced freely.

## Official sources read

### Git

- Git’s official book describes Git’s data model as snapshots rather than a
  generic backup of every current working-tree byte:
  `https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F`
- Official clone documentation defines cloning into a new directory:
  `https://git-scm.com/docs/git-clone`
- Official `git fsck` documentation defines repository object/connectivity
  checking:
  `https://git-scm.com/docs/git-fsck.html`
- Official `git restore` documentation describes restoring tracked paths from a
  commit or other tree:
  `https://git-scm.com/docs/git-restore.html`

Git is retained as the ordinary developer reference. It is not represented as
a backup of uncommitted or untracked bytes. The benchmark grants Git a durable
bare remote outside the loss root and pushes every explicit scenario commit,
so the reference is not defeated merely by deleting a local `.git` directory.

### Restic 0.19.0

- The signed Restic 0.19.0 release was published on 2026-06-09:
  `https://github.com/restic/restic/releases/tag/v0.19.0`
- Restic 0.19.0 backup documentation describes snapshots, relative-path
  behavior, explicit path-list inputs, and machine-readable operation:
  `https://restic.readthedocs.io/en/v0.19.0/040_backup.html`
- Restore documentation supports an exact snapshot/subfolder restored to a
  target directory and warns that an interrupted in-place restore can leave
  partial state:
  `https://restic.readthedocs.io/en/v0.19.0/050_restore.html`
- Repository documentation supports listing and selecting stored snapshots:
  `https://restic.readthedocs.io/en/v0.19.0/045_working_with_repos.html`
- Troubleshooting documentation identifies `restic check --read-data` as the
  repository/data-integrity check:
  `https://restic.readthedocs.io/en/v0.19.0/077_troubleshooting.html`
- The v0.19.0 source license is BSD 2-Clause:
  `https://github.com/restic/restic/blob/v0.19.0/LICENSE`

The 0.19.0 release also changed backup error handling so a missing top-level
source returns a nonzero result. That makes v0.19.0 preferable to an older
version in a fail-closed automated harness.

### Other credible mechanisms considered

- Kopia’s official documentation describes open-source encrypted snapshots,
  local filesystem repositories, snapshot verification, and snapshot restore:
  `https://kopia.io/docs/`
  `https://kopia.io/docs/repositories/`
  `https://kopia.io/docs/reference/command-line/common/snapshot-verify/`
  `https://kopia.io/docs/reference/command-line/common/restore/`
- BorgBackup 1.4.5’s official quick start describes local repositories,
  encrypted deduplicated archives, `borg check`, and extraction:
  `https://borgbackup.readthedocs.io/en/stable/quickstart.html`
  `https://borgbackup.readthedocs.io/en/stable/usage/check.html`
- Apple’s official Time Machine documentation describes automatic backups and
  restoring files to the same or another Mac:
  `https://support.apple.com/en-us/104984`

Kopia and Borg are credible alternatives; they are not scored or disparaged.
Restic is selected because it satisfies every frozen fit criterion with a
single already-qualified command-line binary, direct exact-snapshot restore,
an explicit full-data integrity command, a local repository, and no daemon or
platform-specific filesystem feature. Time Machine is a credible macOS user
baseline but is not freely reproducible on the Linux evidence worker and
requires Apple-specific storage/runtime behavior, so it is out of scope for the
paired RunPod campaign.

This is an experiment-design choice, not proof that Restic is universally
better than Kopia, Borg, Time Machine, APFS snapshots, or managed backup
services.

## Local read-only inventory

Observed on the development host without installing or modifying anything:

```text
ARCH=arm64
MACOS=26.5.1
GIT=git version 2.50.1 (Apple Git-155)
GIT_PATH=/usr/bin/git
GIT_SHA256=179301dcb41ea78accc3fa0048a7e6f6710d891945a751a34addd622020c1818
RESTIC=restic 0.19.0 compiled with go1.26.4 on darwin/arm64
RESTIC_PATH=USER_LOCAL_BINARY_ABSOLUTE_PATH_WITHHELD_FROM_JUDGE_PACKET
RESTIC_SHA256=f6c965a0f7f59464614130d79246479d48e2aa6780c34d27df6e48c8ee0308bd
RESTIC_SIZE_BYTES=29739714
```

The absolute local Restic path is provenance only. It is forbidden from the
public or remote payload. Gate 5 must copy or download the exact official
platform binaries into project-local custody, verify published release
provenance and SHA-256, record the BSD 2-Clause notice, and freeze the Linux
binary used by the RunPod campaign. Gate 4 does not install or redistribute a
binary.

## Selection conclusion

The qualified conventional method is **Git plus Restic 0.19.0**:

- Git preserves every explicit committed-and-pushed snapshot;
- Restic receives a completed full-workspace snapshot at every frozen
  observable checkpoint available to the product;
- the Restic repository, its ephemeral password file, and the Git bare remote
  live outside the disposable workspace but inside the trial root;
- every completed Restic snapshot is retained for the duration of the trial;
- recovery names an exact snapshot ID and restores into a new empty successor;
- the restored manifest and executable success test, not Restic’s exit status
  alone, determine recovered behavior.

This comparator is expected to be very strong at byte recovery and may beat the
product on content retention or latency. A comparator win must be preserved.
The product’s policy/trajectory claims are scored separately so conventional
tools are never failed for a capability they do not claim.

## Research limitations

- The selection did not benchmark Restic against Kopia or Borg; it is a
  protocol-fit decision.
- Local storage avoids network/provider variance but does not test off-site
  disaster recovery.
- A completed checkpoint is a best-case conventional backup condition. Loss
  during capture belongs in the separately held-out interruption campaign.
- Synthetic workspace sizes do not establish performance on large monorepos,
  databases, sparse files, filesystem metadata edge cases, or hardware loss.
- No current official source establishes that any selected tool preserves a
  developer’s intended trajectory. That construct remains separate from byte
  restoration.
