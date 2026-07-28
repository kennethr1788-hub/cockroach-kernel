# Supplemental Generalization Run Receipt R1

- `STATUS`: `SUPPLEMENTAL_GENERALIZATION_GREEN`
- `CAMPAIGN_ID`: `ck-supp-generalization-20260727-r1`
- `PARENT_GATE`: `HARDENING_6_RUN1_GREEN`
- `GATE6_CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `PREFLIGHT_PACKET_SHA256`: `d9c770080aa9e066a371ff2d8c3c795509e342407828a281685e4ad837960098`
- `PREFLIGHT_JUDGE`: `GLM 5.2 / GREEN`
- `FINAL_PACKET_SHA256`: `92f4eb2706990495220c678c9f0b48e27fc39a6d568e583df95511b7f927069c`
- `FINAL_JUDGE`: `GLM 5.2 / GREEN`
- `POD_ID`: `0ifsdv5dcorh8z`
- `ATTEMPTS_USED`: `1`

## Worker and lifecycle

- name: `ck-supp-gen-r1-a01`;
- image: `runpod/base:1.0.2-ubuntu2204`;
- CPU/RAM/GPU: 2 vCPU / 4 GiB / zero GPU;
- storage: 20-GiB disposable container disk / zero persistent or network volume;
- observed compute price: `$0.06/hour`;
- created: `2026-07-28T04:30:42.974Z`;
- exact-ID teardown GREEN: `2026-07-28T04:45:08Z`;
- bounded paid lifetime: `865.026 seconds`;
- compute cost at observed rate: no more than `$0.0144171000`;
- cost at conservative total-active-rate ceiling: no more than `$0.0240285000`;
- exact provider billing query: pending (`[]`), not represented as an exact charge;
- lifecycle final event: `TEARDOWN_GREEN`;
- lifecycle final event SHA-256: `2bb8f7926168a9175d7494c5fbb7ee03850eef03d56101ce8536ab0c57279f1a`;
- exact-ID lookup after deletion: absent;
- campaign running inventory: empty;
- campaign active all-status inventory: empty;
- host process residue: none.

The remote launch attempted to write a non-measured PID bookkeeping file in a
root-owned directory and received `Permission denied`. The already launched
unprivileged process continued and completed normally. This was preserved, not
repaired or rerun. Direct progress came from the append-only checkpoint chain,
and completion came from 108 canonical receipts, aggregate/evidence manifests,
zero-byte stderr, process exit, and retrieved hash verification. The independent
exact-ID lifecycle guard did not depend on the missing PID file.

## Measured result

- measured executions: `108`;
- unique profile/scenario/repetition/method combinations: `108`;
- paired groups with equal source/event/loss/allowed-information/seed hashes:
  `36/36`;
- canonical receipts: `108/108`;
- cleanup: `108/108`;
- residue bytes: `0`;
- unsafe acceptance: `0`;
- product exact manifest: `36/36`;
- product executable continuation: `36/36`;
- small product result: exact `12/12`, continuation `12/12`;
- medium product result: exact `12/12`, continuation `12/12`;
- large (64 MiB) product result: exact `12/12`, continuation `12/12`;
- measured campaign elapsed time: `652.2913569845259 seconds`;
- aggregate semantic SHA-256:
  `a3194d291e18b0435dead0798b9178d286a5ec2328e93209ef7f5f375ca171c1`;
- final checkpoint SHA-256:
  `5082cd2bbad5ecbf7eed12fb0f89d7e48f0d268cf03b96f7645d4fa11254e9b9`.

## Isolation and payload

- payload archive SHA-256:
  `a3fe1f0aef6be48bf478d1e635f33c1345343d271a77d3f8fe94c9c601ddfe85`;
- remote upload hash matched before extraction;
- every payload tree file matched before setup;
- runtime Python/Git/Restic/verifier/harness/runner hashes matched;
- unprivileged UID/EUID: `10001/10001`;
- effective capabilities: zero;
- `NoNewPrivs`: `1`;
- seccomp mode: `2`;
- socket canary: `DENIED_EPERM`;
- inherited socket descriptors: none;
- measured stderr bytes: `0`.

## Evidence hashes

- retrieved evidence archive:
  `25942c52c309f927e271e941ae624ca509221cd02e8229cc4beda49594950849`;
- evidence-tree file:
  `22f4a30f8c024b916eecc1553959e709c3c6313eb3e6049b905ecf9834c6183c`;
- aggregate file:
  `51cedc50874f5639d1989204f21d62b64e4c587b15a3f6af7e80b902bafedc3f`;
- evidence manifest file:
  `c811f2cc7c98f6226b3026a85f12720e4acd93532bcf2eb425f1f818555faa30`;
- checkpoint file:
  `5e2b77c8e0cc9073e186ac72d5dd055ecf4fdd954cea2ec07fff97eaf5086ed5`;
- isolation file:
  `7e8e1a83bb372e47278d4bed76d786bcd9f7b698ae7ab314202119761d3a9191`;
- lifecycle file:
  `95527d6b2533ce1901fc708cbf0d5cfe3a07efb594af64cf53938bfa6a8bb933`;
- local independent validator output:
  `f7809dc5bb823f91ae4d967113c54692a64a95c881ee18fa5fc2e73b6e997f51`;
- local validator semantic SHA-256:
  `7fe34ced61cc4f583a908053638ffdab1c734693db3ee29e318e9082a4795d6a`.

The local evidence tree recheck passed for every file. `gitleaks` found zero
leaks; the private-path/credential scan returned zero lines. `detect-secrets`
reported only expected high-entropy SHA-256 values in the canonical receipts.

## Claim boundary

This result supports controlled synthetic generalization across the frozen
128-KiB, 4-MiB, and 64-MiB profiles on one generic RunPod CPU worker. It is not
independent-user evidence, a production-scale result, universal recovery, or
proof of restoring uncaptured bytes. It does not modify Gate 6 and is not Gate
7.
