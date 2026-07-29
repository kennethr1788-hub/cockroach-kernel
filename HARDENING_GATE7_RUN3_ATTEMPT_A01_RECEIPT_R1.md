# Hardening Gate 7 Run 3 Attempt A01 Receipt R1

- pod ID: `0jihcbgqjjndw8`
- pod name: `ck-g7r3-20260729-a01`
- created UTC: `2026-07-29T04:14:33.558Z`
- desired status: `RUNNING`
- compute rate: `$0.06/hour`
- returned shape: `CPU; 2 vCPU; 4 GiB RAM; 0 GPU`
- image: `runpod/base:1.0.2-ubuntu2204`
- container disk: `20 GiB`
- attached volume: `0 GiB`
- network volume: `null`
- secure cloud: `true`
- data center: `US-CA-2`
- provider stop fuse: `2026-07-29T12:13:43Z`
- provider terminate fuse: `2026-07-29T12:43:43Z`
- lifecycle guard: `BOUND_AND_ADVANCING`
- lifecycle session: `ckg7r3-a01-lifecycle`
- first advancing event hash: `e7d4e3e042d9aa603dddbcbf0229e94d51e695005e30bf9d1df0e44100784f3d`
- SSH readiness: `READY`
- SSH host-key scans: `2 IDENTICAL`
- upload started: `NO`
- hidden seed exists: `NO`
- measured execution started: `NO`

A01 matches every accepted provider property. Its exact-ID guard was started
before upload and is advancing. The worker remains subject to extracted-bundle,
isolation, packaged-helper, CockroachDB, AWS, and no-residue checks before it
can become `CAMPAIGN_READY`.
