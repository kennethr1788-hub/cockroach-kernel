# S1 Evidence Manifest

- local profile: P4 tests plus P3 integration, no CUDA, approximately 543 MB RSS;
- RunPodCTL: `2.7.2-309512b`;
- RunPodCTL SHA-256: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`;
- preflight pod list: `[]`;
- authenticated CPU quote: 2 vCPU / 8 GB at `$0.08/hour`;
- container quote: `$0.0002/GB-hour`, 20 GB frozen;
- template: official `runpod-ubuntu-2204`;
- transfer archive SHA-256: `ad77ef05e8ad121302fbcdbfa8f95ea4c227ad894285826f80dae6f2c3c069e4`;
- transfer archive bytes: `144439419`;
- Linux runtime archive SHA-256: `3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`;
- Linux runtime binary SHA-256: `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`;
- secret/private-path scans: no findings;
- short local driver exercise: semantic checkpoint passed and runtime residue was empty; not S1 duration evidence;
- worker/pod ID: `48bqdill8w3vt0`, stopped and deleted;
- returned worker: 2 vCPU / 4 GB, `$0.06/hour`, mismatched frozen RAM/price;
- payload uploaded: no;
- workload started: no;
- immediate exact billing result: unavailable (`[]`), not fabricated;
- second-lifecycle authorization: received, conditional on exact 2 vCPU / 4 GB
  at no more than `$0.06/hour` compute and `$0.065/hour` total active rate;
- second-lifecycle authenticated quote: smallest offered class was 2 vCPU /
  8 GB at `$0.08/hour`; authorized 2 vCPU / 4 GB class was not shown;
- second worker created: no; mandatory `RUNPOD_PRICE_DRIFT` preflight stop;
- second-lifecycle packet/judge: not created or requested because the price gate
  failed first;
- second-lifecycle preflight receipt:
  `S1_SECOND_LIFECYCLE_PREFLIGHT_RECEIPT.md`, SHA-256
  `fa7704775d76c8cfeb32e3a4de7e504304bb12e33dc922dd5a15724952d84a05`;
- later exact billing recheck: still unavailable (`[]`), not fabricated;
- R3 retry packet SHA-256:
  `82fc0dcdd38a814e40a39f85c57b1f35948d46792575c7fdd2db24283768ef87`;
- R3 attempt: one; Pod `wo1iq5wtk04q49`;
- R3 workload: technical GREEN, 61 receipts and 61 telemetry records;
- R3 final evidence hash:
  `7e712179b9b4e6204cfd9a8142cb7b37c4334342221eaca4ece2d060df8b98ef`;
- R3 evidence archive SHA-256:
  `72fb147adc9a61b8f6d0fe24539579599928994c1fac1514cb6a754f96d56865`;
- R3 local evidence tree SHA-256:
  `dc2cda67c3297c6a52ad00a25412b6621cff32b7fec78098cf027f786ae9e5b4`;
- R3 secret/private-path scans: no findings;
- R3 teardown: scoped running and all-status inventory `[]`, Pod get 404;
- exact provider billing: delayed (`[]`) for both S1 Pod IDs; authenticated
  console states billing is one hour behind;
- operator billing decision: Kenneth accepted the visible account-side charge
  and removed delayed itemization as a project-local blocker;
- final packet SHA-256:
  `46e6a9081c949d586d9ea4812a31e6baf033342bef380bdf4a8ed50e73cf25b1`;
- final independent GLM 5.2 verdict: GREEN;
- final S1 gate: `CK_S1_FOUNDATION_SOAK_GREEN`.
