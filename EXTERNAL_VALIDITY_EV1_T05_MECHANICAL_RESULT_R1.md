# EV1-T05 Mechanical Result R1

- `STATUS`: `PASS_OPERATOR_OBSERVATION_REQUIRED`
- `TASK_ID`: `EV1-T05`
- `TASK_EXECUTION_FILE_SHA256`: `db67858de3fedbe31eeb5cde61104988dcc6df68c263f30f4f35a0d267de8985`
- `TASK_EXECUTION_RECEIPT_SHA256`: `75bd558c71bf633962b567cebf5dc19bd0a89110a76627d8a10727365df9de8c`
- `PRODUCT_VERDICT`: `PROMOTE`
- `STABLE_REASON`: `MAX_PROVEN_PREFIX`
- `FRESH_CONTEXT`: `PASS`
- `DECLARED_FILES_RECOVERED_BYTE_EXACT`: `5_OF_5`
- `EMPTY_HISTORY_SUCCESSOR`: `TRUE`
- `ORIGINAL_WORKSPACE_ABSENT`: `TRUE`
- `OUTSIDE_CANARY_SURVIVED`: `TRUE`
- `NETWORK_USED_BY_PRODUCT`: `FALSE`
- `CREDENTIALS_USED_BY_PRODUCT`: `FALSE`
- `POST_LOSS_TASK_RESTATEMENT_WORDS`: `0`
- `POST_LOSS_MANUAL_INTERVENTIONS`: `0`
- `UNSAFE_MUTATIONS`: `0`
- `UNAUTHORIZED_PATH_ACCESSES`: `0`
- `PROCESS_RESIDUE`: `0`
- `CAMPAIGN_TEARDOWN`: `PENDING_AFTER_OBSERVATION_AND_FINAL_AUDIT`

## Restored work

- `lib/signalSchema.ts`: `d184205b5880071e0d48f186035d4791b86e70157dd13dd036067935562f6d4d`
- `lib/signals.ts`: `05dc771ef5c724e964d0ea9e873d14bc34480c2f93e5d3b5863085c28bf51676`
- `package.json`: `040461072c0e939e2e48f050b7d8e5fa8618b94a553d4e387a2af2f82f653f58`
- `scripts/run-signal-schema.mjs`: `82786737ed3887f529d782b5d7412dcf144c9e0d62260cb0bcf753db44ae959a`
- `scripts/signal-schema-cases.cjs`: `a31bf5f04a43c836adc40750fcf93b7502ac2673f324ad58697094352878c1c3`

## Successor acceptance

- strict schema suite: `PASS`; eight adversarial cases and the actual 12-record
  dataset; log SHA-256
  `229c21d068f1496925f83d8331ccffca76c474f9f516169ff05a3fd808701ae4`
- typecheck: `PASS`; log SHA-256
  `8c0af875a1ab948857b68d4f22b66e9bce86deedfdf47d7ba6ea1d528e01bbda`
- production build: `PASS`; log SHA-256
  `b79f6cccaa7e0fcf7721ffdbe62a78f895ece01cae21cdef196c666484412b35`

The successor contains no `.git` directory. Eighteen ordinary-Git-equivalent
baseline files were recreated from the separately attributed baseline snapshot;
they are not counted as recovered task work. The product restored only the five
human-declared task files. The execution root and successor remain preserved
until Kenneth supplies the two human observations and the final independent
objective-evidence audit completes.
