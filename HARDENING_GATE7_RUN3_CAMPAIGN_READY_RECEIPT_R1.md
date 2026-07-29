# Hardening Gate 7 Run 3 Campaign Ready Receipt R1

`GATE7_RUN3_CAMPAIGN_READY_GREEN`

- UTC frozen: `2026-07-29T04:28:45Z`
- pre-checkpoint commit: `6dc1bf428f69b57697242ae985834b6725c041c8`
- authorization SHA-256: `a941c6e85d021d2ec77ea442765f4df724283af76f74c8b7f19ed91d077f8d30`
- preflight packet SHA-256: `5274e5f8c35383ff26f283764ba64385c3e3e5d5711da07a9b20735c6ccba7c9`
- product candidate: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- worker: `0jihcbgqjjndw8` / `ck-g7r3-20260729-a01`
- worker state: `RUNNING`
- returned shape: `CPU; 2 vCPU; 4 GiB RAM; 0 GPU`
- image: `runpod/base:1.0.2-ubuntu2204`
- disk/volumes: `20 GiB disposable; 0 persistent; no network volume`
- compute rate: `$0.06/hour`
- stop/terminate request: `2026-07-29T12:13:43Z` / `2026-07-29T12:43:43Z`
- provider deadline readback: `NOT EXPOSED; exact creation request preserved`
- hidden seed created: `NO`
- measured execution started: `NO`

## Direct readiness evidence

- AWS and CockroachDB sanitized readiness: `GREEN`
- readiness receipt SHA-256: `b1be5f9cbc9ed6642822d7bdd40296b737eb14177e6e1bb65346d32a4d199c2b`
- readiness file SHA-256: `0a995781180a9d4b9ddc6e7644f40995d79d46da3c77074104cf92adb51e268f`
- credential bytes recorded: `false`
- current Pod record SHA-256: `e615f31466ff1dab4cff713dc7d77ee0c06608a08dede02750dafc4a22ae8113`
- SSH trust-record file SHA-256: `2646ed57387c10239c46ac88f32d118083b4cb1dc7a720cb85bd3587c6ae583f`
- immutable archive SHA-256: `d0a47c311ad14f16e1bed2df181bb3d6885accf155be7322a67829c201023b28`
- extracted production manifest SHA-256: `f4e986b28f3133b6f11f089979f6024fc907075d3ded75263f6728b0058cf6df`
- extracted member comparison: `93/93 paths and hashes match`
- CockroachDB archive SHA-256: `3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`
- CockroachDB binary SHA-256: `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`

## Isolation and fixed canaries

- runner identity: `uid=1001(ckrunner)`
- oracle identity: `uid=1000(ckoracle)`
- isolation attestation SHA-256: `201dfafcd5657408ee25ffd8495890a62c17ddb6445daea1b5c240eded61f750`
- isolation receipt file SHA-256: `fd1625d2f3afb627d8a7de0770b8918e8db628d8ea25c149a2a9affb0c807d29`
- isolation result: `no_new_privs=1; CapEff=0; no inherited sockets; network socket denied EPERM`
- fixed public canary `B-1-2`: `PROMOTE / MAX_PROVEN_PREFIX / PASS`
- `B-1-2` observation file SHA-256: `1a3b318d14442d68ae2d639ed6c558a122e7edde53b3f2b69d403936dc98875a`
- fixed public canary `D-FILE-LP1`: `INVALID / AGGREGATE_LIMIT_EXCEEDED / PASS`
- `D-FILE-LP1` observation file SHA-256: `abddab33c7938832d9f605bc3ee6d750654a25d3ea67cf9439c8d9ca6aae232a`
- both canaries: `fresh process; model not invoked; network denial bound`

## Repaired bulk smoke

- manifest file SHA-256: `9270bb5df7f58a067375b4ae10bda2415b25334ae035b6a4066f7866754e7e03`
- exact counts: `2,000 tasks; 20,000 events; 4,000 receipts; 20,000 vectors; 200 queries`
- unique vector digests: `20,000`
- SQL batch files: `184`
- synthetic-only: `true`

## Advancing guards at freeze

- exact-ID lifecycle: sequence `45`, event `HEARTBEAT`, event hash
  `8ed718d3f37727724af5a2f1744f8b749f94fde611f255aca0ca726d64a696d8`
- bridge: sequence `39`, event `HEARTBEAT`, event hash
  `2a768eaad1906abb8e918b2deacad92d62500b158813475b30ddae8398694d00`
- coordinator: sequence `17`, event `HEARTBEAT`, event hash
  `2e731d5641997c928b8edec18b84e8cd57de6c66d452982480fa04d61f246b31`
- coordinator guard: sequence `14`, event `HEARTBEAT`, event hash
  `15b2ee82232d66a0aaf98f5abc2619ef80a2dcf9213e94b27e51d99b31aede26`
- coordinator ceilings: `12 Lambda calls; 108 CockroachDB operations`
- protocol SHA-256: `20bfeac7bf3923394fa193343c904b67bde3efee62561b530fad6ff96d41178c`
- resource allowlist SHA-256: `a1993801ce17c4f4a5894720fcfab5cd96715f3f9b0ce03b3919430ea837e3aa`
- RunPodctl SHA-256: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`

## One-way boundary

Direct local and remote scans found no hidden-seed file and no measured worker,
expanded-campaign, or bulk-controller process. The next allowed action is to
create one CSPRNG hidden seed, copy only the hidden inputs and input manifest to
the runner, then start the three frozen measured tracks exactly once. After that
point replacement, tuning, regeneration, and rerun are forbidden.
