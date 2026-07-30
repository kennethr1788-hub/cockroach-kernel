# EV1-T09 Preparation Attempt R1 — Failed Before Task Start

- `STATUS`: `PRESERVED_FAILED_PREPARATION_ATTEMPT`
- `TASK_ID`: `EV1-T09`
- `FAILURE`: `TypeError: extractall() got an unexpected keyword argument 'filter'`
- `FAILED_OPERATION`: `HOST_PYTHON_TARFILE_EXTRACTION_API_COMPATIBILITY`
- `SOURCE_ARCHIVE_CREATED`: `TRUE`
- `SOURCE_BYTES_EXTRACTED`: `FALSE`
- `TASK_WORK_STARTED`: `FALSE`
- `MEASURED_CAPTURE_STARTED`: `FALSE`
- `PRODUCT_CANDIDATE_TOUCHED`: `FALSE`
- `T07_T08_PRESERVATION`: `UNCHANGED`
- `REPAIR`: `Remove only the partial generated EV1-T09 root; retain the complete pre-extraction member validation and call the host-compatible extraction method without filter=.`

The script validated every archive member before attempting extraction: no
absolute path, parent traversal, symlink, or hard link was accepted. The host
Python rejected the newer keyword before extraction. This failed preparation
attempt is not a measured task result and may not be omitted from the campaign
history.
