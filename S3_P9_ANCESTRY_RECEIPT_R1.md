# S3 P9 Ancestry Receipt R1

- `P9_IMPLEMENTATION_COMMIT`: `cbd58b3af9e1ce5c4ddf8885866b88e7e7c1ca0f`
- `P9_PACKET_PARENT_COMMIT`: `61d77d1704a3f074427f9f82b300abaaa201f79c`
- `P9_RELEASE_CHECKPOINT_COMMIT`: `fc296743dd97699a78a4777c8affcd47930f92e6`
- `P9_RELEASE_TAG`: `ck-p9-integration-green-r1`
- `IMPLEMENTATION_IS_ANCESTOR_OF_PACKET_PARENT`: `GREEN`
- `PACKET_PARENT_IS_ANCESTOR_OF_RELEASE_CHECKPOINT`: `GREEN`
- `UTC_VERIFIED`: `2026-07-27T00:35:00Z`

The three P9 commit values are not competing claims. The first is the code and
live-evidence implementation commit, the second adds the final clean-clone
receipts and is the parent at packet freeze, and the third closes and tags the
P9 gate. Both ancestry checks passed with `git merge-base --is-ancestor`.
