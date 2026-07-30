# EV1-T09 Capture Attempt R1 Failed

- `STATUS`: `PRESERVED_NON_DESTRUCTIVE_CAPTURE_FAILURE`
- `TASK_ID`: `EV1-T09`
- `ORIGINAL_WORKSPACE`: `PRESENT_UNCHANGED`
- `DELETION_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`
- `FAILURE`: `DEPENDENCY_SHAPE_INVALID:DEPENDENCY_TSC_MISSING`
- `CAUSE`: `The reused T06 dependency-shape helper required TypeScript even though T09's frozen acceptance runtime contains only pinned Prettier.`
- `BASELINE_SNAPSHOT`: `410_FILES_PRESERVED_FOR_EXACT_REVALIDATION`
- `CAPTURE_RECEIPT`: `NOT_CREATED`
- `REPAIR_SCOPE`: `T09-specific dependency shape plus exact preserved-baseline verification; no product, task, threshold, or claim change.`

The failure occurred before representation creation, request creation, deletion,
or recovery. The original disposable workspace remains present with its exact
declared state. The generated 410-file ordinary-Git baseline snapshot is
preserved and may be reused only after byte-for-byte comparison with the bound
baseline commit.
