# EV1-T05 Preparation Attempt 1 R1

- `STATUS`: `PREPARATION_BLOCKED_PLATFORM_CALIBRATION`
- `TASK_ID`: `EV1-T05`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `SOURCE_COMMIT`: `2c088ba8599c75cb02fbd61dfcf259d000729131`
- `BACKLOG_SHA256`: `6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5`
- `DEPENDENCY_LOCK_SHA256`: `7e0238617f56ecd9ab4c99bcc6d41a8a7e4c2635707c19247ddf082b94eacd7a`
- `DEPENDENCY_LOCK_VERSION`: `3`
- `DEPENDENCY_PACKAGE_ENTRIES`: `119`
- `PINNED_NEXT_VERSION`: `16.2.12`
- `CAPTURE_STARTED`: `FALSE`
- `DELETION_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`

The public-registry dependency-resolution phase succeeded inside the project-local
T05 control root with lifecycle scripts disabled. `npm ci`, the exact dependency
tree, and baseline typecheck passed. The expected missing `test:signal-schema`
script also failed as calibrated.

Baseline production build did not pass under the fixed `(deny network*)`
Seatbelt profile. Next 16.2.12 defaults to Turbopack, whose CSS build worker tried
to bind an internal port. Seatbelt denied the bind with `Operation not permitted`.
This is a platform/verifier calibration failure, not a T05 task failure.

Raw hashes:

- lock generation: `6f77b30ecd5d25564da3a6d97ffe04c5316d5f0419e4e189a86a5d6210c45156`
- dependency install: `e4e3907cbaf1349e7b09741bc31688971f24b693b805a33fb0cac02f4480f39b`
- baseline typecheck: `8c0af875a1ab948857b68d4f22b66e9bce86deedfdf47d7ba6ea1d528e01bbda`
- blocked Turbopack build: `1b829ce9f63a3865d1ec699a9bfea60069152555ed2b68aef409919dec09fffd`
- expected missing-test result: `5a7fec33b6dca9ea2e8450cf002203ab29ed6ac82ab64d23d9d285c3f30b4763`

An official local CLI capability check showed `next build --webpack`. A bounded
diagnostic under the identical Seatbelt profile passed in webpack mode. That
diagnostic also exposed Next's mandatory first-build `tsconfig.json` adaptation.
Preparation R2 must therefore freeze both the webpack build mode and the generated
TypeScript configuration into the disposable baseline before task work, reuse the
exact R1 lock/cache offline, and preserve all R1 evidence unchanged.

Separately, the earlier source probe's unexpected npm HOME debug log remains
preserved byte-exact with SHA-256
`a822f559f20a7f33eb30f4b56055b4524f2bacc46c371dc7edde3c02f4d8e485`.
Its original HOME path is absent. No T05 task code was written in this attempt.
