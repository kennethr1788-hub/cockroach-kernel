# Supplemental Generalization — Independent Final Review Packet R1

## Requested verdict

Review the completed campaign without authoring, editing, using tools, or
changing any gate. Return `GREEN` only if the evidence described below is
internally sufficient for the narrow supplemental claim and teardown/cost
boundaries passed. Otherwise return `NOT_GREEN` with exact blockers.

## Packet boundary

- Gate 6 remains `HARDENING_6_RUN1_GREEN` and immutable.
- This is supplemental evidence after Gate 6, not part of Gate 6 or Gate 7.
- Frozen Gate 6 product candidate:
  `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`.
- Preflight packet:
  `d9c770080aa9e066a371ff2d8c3c795509e342407828a281685e4ad837960098`.
- Preflight independent GLM 5.2 verdict: `GREEN`.

## Frozen acceptance versus result

| Acceptance | Result |
|---|---:|
| unique executions | 108/108 |
| equal-hash paired groups | 36/36 |
| canonical receipts | 108/108 |
| clean trial teardowns | 108/108 |
| residue bytes | 0 |
| unsafe acceptances | 0 |
| product exact manifests | 36/36 |
| product executable continuations | 36/36 |
| product exact/continuation by profile | 12/12 and 12/12 for each profile |

Profiles were 16 files / 128 KiB, 64 files / 4 MiB, and 128 files / 64 MiB.
Each crossed the six frozen state/loss classes, the three methods, and two
deterministic repetitions with rotated execution order. Campaign elapsed time
was 652.291 seconds. Aggregate semantic SHA-256 was
`a3194d291e18b0435dead0798b9178d286a5ec2328e93209ef7f5f375ca171c1`.

## Evidence integrity

- payload archive:
  `a3fe1f0aef6be48bf478d1e635f33c1345343d271a77d3f8fe94c9c601ddfe85`;
- retrieved evidence archive:
  `25942c52c309f927e271e941ae624ca509221cd02e8229cc4beda49594950849`;
- evidence-tree file:
  `22f4a30f8c024b916eecc1553959e709c3c6313eb3e6049b905ecf9834c6183c`;
- aggregate file:
  `51cedc50874f5639d1989204f21d62b64e4c587b15a3f6af7e80b902bafedc3f`;
- evidence manifest file:
  `c811f2cc7c98f6226b3026a85f12720e4acd93532bcf2eb425f1f818555faa30`;
- 108-event checkpoint file:
  `5e2b77c8e0cc9073e186ac72d5dd055ecf4fdd954cea2ec07fff97eaf5086ed5`;
- local validator semantic SHA-256:
  `7fe34ced61cc4f583a908053638ffdab1c734693db3ee29e318e9082a4795d6a`.

The remote archive and every internal tree hash were reverified locally. A
separate local validator revalidated canonical wrapper/base receipts, unique
coverage, all 36 within-pair hashes, cleanup, residue, unsafe acceptance,
product exactness, and executable continuation. Remote measured stderr was
zero bytes. Gitleaks and the private-path scan returned zero findings. The only
detect-secrets findings were expected receipt SHA-256 strings.

## Isolation and lifecycle

One CPU worker was used; no retry was needed. Returned shape was exact: 2 vCPU,
4 GiB RAM, zero GPU, exact image, 20-GiB disposable disk, zero persistent or
network volume, and `$0.06/hour`. Runtime was unprivileged UID 10001 with zero
effective capabilities, `NoNewPrivs=1`, seccomp mode 2, no inherited sockets,
and an `EPERM` socket canary. All payload/tool hashes matched.

The detached exact-ID guard ended in `TEARDOWN_GREEN` with final event hash
`2bb8f7926168a9175d7494c5fbb7ee03850eef03d56101ce8536ab0c57279f1a`.
Pod `0ifsdv5dcorh8z` was deleted; exact-ID lookup is absent; campaign running
and active all-status inventory are empty; no host process remains.

Paid lifetime was bounded to 865.026 seconds: no more than `$0.0144171000` at
the observed compute rate and `$0.0240285000` at the conservative active-rate
ceiling. Provider billing currently returns `[]`, so no exact charge is claimed.
This pending reconciliation is permitted only because prelaunch price, paid
lifetime, maximum bounded cost, deletion, and empty inventory are all direct.

The remote launch could not write its non-measured PID bookkeeping file because
the parent directory was root-owned. The already launched unprivileged process
completed; the defect was preserved and no rerun occurred. Progress/completion
were evidenced independently by 108 fsynced checkpoints, 108 canonical
receipts, aggregate/evidence manifests, process exit, zero stderr, and retrieved
hash verification. The lifecycle guard was independent of this PID file.

## Narrow claim and limitations

The only proposed claim is: the frozen product candidate preserved its measured
recovery and safety behavior across the controlled synthetic 128-KiB, 4-MiB,
and 64-MiB repository profiles on one disposable CPU worker. This is explicitly
team-authored synthetic evidence, not independent-user testing, production
scale, universal repository compatibility, population inference, arbitrary
uncaptured-byte recovery, or proof about Gate 7.

## Judge response schema

Return exactly:

```text
VERDICT: GREEN | NOT_GREEN | JUDGE_UNAVAILABLE
PACKET_SHA256: <exact hash supplied by caller>
BLOCKERS: <none or concise list>
RESIDUAL_RISKS: <concise list>
```
