# PDH-3 Runtime Cleanup Receipt — R1

This is the frozen pre-deletion manifest for a project-local cleanup. It preserves all receipts, manifests, logs, final/checkpoint/custody evidence, source, Git history, the exact deployed R5 bundle, the current repaired candidate bundle, and the operator-owned `heap_profiler/` directory.

```json
{
  "archive_bytes": 6047077230,
  "archive_count": 42,
  "archive_target_list_sha256": "64f2726bcd16e16cb1a55c3c545af7bcadc23ffe39ee11e0003b4bc60bde6e01",
  "archive_targets": [
    {
      "bytes": 143953890,
      "path": ".pdh3-runtime/r10-relaunch/20260801T185301Z/pdh3-scale-bundle-r10-final.tgz",
      "sha256": "538854b565a3581986579a72c98b185a58b86e23f9f4a183a61ef83873587a1a"
    },
    {
      "bytes": 143953890,
      "path": ".pdh3-runtime/r10-relaunch/20260801T185301Z/pdh3-scale-bundle-r10.tgz",
      "sha256": "538854b565a3581986579a72c98b185a58b86e23f9f4a183a61ef83873587a1a"
    },
    {
      "bytes": 143954644,
      "path": ".pdh3-runtime/r11-relaunch/20260801T222658Z/pdh3-scale-bundle-r11.tgz",
      "sha256": "c8ddf3d9794ed489eda157551b8eef8d7004e640a76c6e4f865deef1baed9f96"
    },
    {
      "bytes": 143954644,
      "path": ".pdh3-runtime/r11-relaunch/20260801T224548Z/pdh3-scale-bundle-r11b.tgz",
      "sha256": "c8ddf3d9794ed489eda157551b8eef8d7004e640a76c6e4f865deef1baed9f96"
    },
    {
      "bytes": 143981919,
      "path": ".pdh3-runtime/r12-preflight/cli-verify-r1/archive.tgz",
      "sha256": "5f0fcd166717b122ac170cbc3f0b8a1b5b6567af85a78ed30291406ca7856332"
    },
    {
      "bytes": 143990873,
      "path": ".pdh3-runtime/r12-preflight/full-r6-linux-portable-20260802-r1/a/pdh3-r12-bundle.tgz",
      "sha256": "27b12ba16c3bfbda3400cda8d8bdd35b6f89fa95cae8e0fb051fb39082722ef8"
    },
    {
      "bytes": 143990873,
      "path": ".pdh3-runtime/r12-preflight/full-r6-linux-portable-20260802-r1/b/pdh3-r12-bundle.tgz",
      "sha256": "27b12ba16c3bfbda3400cda8d8bdd35b6f89fa95cae8e0fb051fb39082722ef8"
    },
    {
      "bytes": 143989823,
      "path": ".pdh3-runtime/r12-preflight/full-r6-minvcpu-20260802-r1/a/pdh3-r12-bundle.tgz",
      "sha256": "018ed0af97b7e533ad6fdec316db006c1990628dcab2a94c42980c199cbfa2ae"
    },
    {
      "bytes": 143989823,
      "path": ".pdh3-runtime/r12-preflight/full-r6-minvcpu-20260802-r1/b/pdh3-r12-bundle.tgz",
      "sha256": "018ed0af97b7e533ad6fdec316db006c1990628dcab2a94c42980c199cbfa2ae"
    },
    {
      "bytes": 143990721,
      "path": ".pdh3-runtime/r12-preflight/full-r6-smoke-diagnostic-20260802-r1/a/pdh3-r12-bundle.tgz",
      "sha256": "333488646b1635f2979373512a4d577c0a28a1272345a065d9904f8cd51d59f8"
    },
    {
      "bytes": 143990721,
      "path": ".pdh3-runtime/r12-preflight/full-r6-smoke-diagnostic-20260802-r1/b/pdh3-r12-bundle.tgz",
      "sha256": "333488646b1635f2979373512a4d577c0a28a1272345a065d9904f8cd51d59f8"
    },
    {
      "bytes": 143990825,
      "path": ".pdh3-runtime/r12-preflight/full-r6-tracer-lib-20260802-r1/b/pdh3-r12-bundle.tgz",
      "sha256": "06bbc9567967998bee21e5c5cd42e44b688c52e3ca4b8a0d78577eaad06b9a99"
    },
    {
      "bytes": 143954644,
      "path": ".pdh3-runtime/r12-preflight/pf0/pdh3-r12-baseline-bundle.tgz",
      "sha256": "c8ddf3d9794ed489eda157551b8eef8d7004e640a76c6e4f865deef1baed9f96"
    },
    {
      "bytes": 143976400,
      "path": ".pdh3-runtime/r12-preflight/pf0-r2/pdh3-r12-bundle-a.tgz",
      "sha256": "afb4ea0e3d7677303437e81222fed8c614d3f8396b58feb718a880e7e0553e59"
    },
    {
      "bytes": 143976400,
      "path": ".pdh3-runtime/r12-preflight/pf0-r2/pdh3-r12-bundle-b.tgz",
      "sha256": "afb4ea0e3d7677303437e81222fed8c614d3f8396b58feb718a880e7e0553e59"
    },
    {
      "bytes": 143981423,
      "path": ".pdh3-runtime/r12-preflight/pf0-r3/pdh3-r12-bundle-a.tgz",
      "sha256": "7def8766a66264ca86cfc9a1c351dce7e4ee97d29a1e27a4ad43501e187ca8fb"
    },
    {
      "bytes": 143981423,
      "path": ".pdh3-runtime/r12-preflight/pf0-r3/pdh3-r12-bundle-b.tgz",
      "sha256": "7def8766a66264ca86cfc9a1c351dce7e4ee97d29a1e27a4ad43501e187ca8fb"
    },
    {
      "bytes": 143981780,
      "path": ".pdh3-runtime/r12-preflight/pf0-r4/pdh3-r12-bundle-a.tgz",
      "sha256": "94476b35fe1e443d81741ed97c48d5211dd48b6c4b6b052e54751653a6b5e38f"
    },
    {
      "bytes": 143981780,
      "path": ".pdh3-runtime/r12-preflight/pf0-r4/pdh3-r12-bundle-b.tgz",
      "sha256": "94476b35fe1e443d81741ed97c48d5211dd48b6c4b6b052e54751653a6b5e38f"
    },
    {
      "bytes": 143981919,
      "path": ".pdh3-runtime/r12-preflight/pf0-r5/pdh3-r12-bundle-a.tgz",
      "sha256": "5f0fcd166717b122ac170cbc3f0b8a1b5b6567af85a78ed30291406ca7856332"
    },
    {
      "bytes": 143981919,
      "path": ".pdh3-runtime/r12-preflight/pf0-r5/pdh3-r12-bundle-b.tgz",
      "sha256": "5f0fcd166717b122ac170cbc3f0b8a1b5b6567af85a78ed30291406ca7856332"
    },
    {
      "bytes": 143984638,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6/pdh3-r12-bundle-a.tgz",
      "sha256": "6d4e77e26f945b983e019e12c50acb0a0bb409069fa77c25e3c2fbe7f380719d"
    },
    {
      "bytes": 143984638,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6/pdh3-r12-bundle-b.tgz",
      "sha256": "6d4e77e26f945b983e019e12c50acb0a0bb409069fa77c25e3c2fbe7f380719d"
    },
    {
      "bytes": 143984891,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-controller/pdh3-r12-bundle-a.tgz",
      "sha256": "728e4592475f5c18e88e18a02d6230dff27d77316ce6eee599e07a8f01fe9e98"
    },
    {
      "bytes": 143984891,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-controller/pdh3-r12-bundle-b.tgz",
      "sha256": "728e4592475f5c18e88e18a02d6230dff27d77316ce6eee599e07a8f01fe9e98"
    },
    {
      "bytes": 143984895,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-controller-r2/pdh3-r12-bundle-a.tgz",
      "sha256": "0847ffaa0c5effae453a18dc7be7e28dd0ab7085a92483cf40ccad2fe3e7daf1"
    },
    {
      "bytes": 143984895,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-controller-r2/pdh3-r12-bundle-b.tgz",
      "sha256": "0847ffaa0c5effae453a18dc7be7e28dd0ab7085a92483cf40ccad2fe3e7daf1"
    },
    {
      "bytes": 143984633,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-repaired/pdh3-r12-bundle-a.tgz",
      "sha256": "69b5923882c459baf93b4a0baec458648adfc56671528dbf2c2623eceff9faaf"
    },
    {
      "bytes": 143984633,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-repaired/pdh3-r12-bundle-b.tgz",
      "sha256": "69b5923882c459baf93b4a0baec458648adfc56671528dbf2c2623eceff9faaf"
    },
    {
      "bytes": 143986739,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-replacement-r1/a/pdh3-r12-bundle.tgz",
      "sha256": "d0bbf38305e9752b20f45e59ed7ce9b7822776838a8ee13a3dcc0176c1f18efc"
    },
    {
      "bytes": 143986739,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-replacement-r1/b/pdh3-r12-bundle.tgz",
      "sha256": "d0bbf38305e9752b20f45e59ed7ce9b7822776838a8ee13a3dcc0176c1f18efc"
    },
    {
      "bytes": 143986735,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-replacement-r2/a/pdh3-r12-bundle.tgz",
      "sha256": "3152cd00011d1c8c23d873a051b3651407379699ffb9e180a3581f86b44a3418"
    },
    {
      "bytes": 143986735,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-replacement-r2/b/pdh3-r12-bundle.tgz",
      "sha256": "3152cd00011d1c8c23d873a051b3651407379699ffb9e180a3581f86b44a3418"
    },
    {
      "bytes": 143989825,
      "path": ".pdh3-runtime/r12-preflight/pf4-affinity-20260802-r1/pdh3-r12-bundle.tgz",
      "sha256": "1f5cdf99e09c9010a9f0544947a0920c0004357f3bcf2f2c2a02ffe1da6b85df"
    },
    {
      "bytes": 143989823,
      "path": ".pdh3-runtime/r12-preflight/pf4-retry-minvcpu-20260802-r2/pdh3-r12-bundle.tgz",
      "sha256": "5a72110740335cd76128343db28eb26741d5b54f1a1b7ea22dd9a87fd754e1f0"
    },
    {
      "bytes": 143989827,
      "path": ".pdh3-runtime/r12-preflight/pf4-retry-usmo-20260802-r1/pdh3-r12-bundle.tgz",
      "sha256": "b9df3cffa961e9ab082df0582d7bf259cf1c90bf162ebb5df0ac37f56566aca3"
    },
    {
      "bytes": 143990837,
      "path": ".pdh3-runtime/r12-preflight/r6-r5-repair-bundle-r1/b/pdh3-r12-bundle.tgz",
      "sha256": "52619301a9aa0b88e5c2e3e52d668e6485ae105eb1c0f86405d681a5945be7a6"
    },
    {
      "bytes": 143951794,
      "path": ".pdh3-runtime/r8-relaunch-r8/20260801T110300Z/pdh3-scale-bundle-r8.tgz",
      "sha256": "3f98351e2bc52f2618c74b3692aea3faceb27d6071f0163c2773c070f323f91b"
    },
    {
      "bytes": 143951988,
      "path": ".pdh3-runtime/r8-relaunch-r8/20260801T111536Z/pdh3-scale-bundle-r8.tgz",
      "sha256": "0ca257a38ddb49a812ba2252459f3ae900b83aa674f2f2883b709ea599258c15"
    },
    {
      "bytes": 143951988,
      "path": ".pdh3-runtime/r8-relaunch-r8/20260801T111933Z/pdh3-scale-bundle-r8.tgz",
      "sha256": "0ca257a38ddb49a812ba2252459f3ae900b83aa674f2f2883b709ea599258c15"
    },
    {
      "bytes": 143952876,
      "path": ".pdh3-runtime/r9-relaunch/20260801T165000Z/pdh3-scale-bundle-r9.tgz",
      "sha256": "1e50f4a9acf7e484b34126ae51c0425fbb908a7b520fdfab63fb72cad4fa0c76"
    },
    {
      "bytes": 143952876,
      "path": ".pdh3-runtime/r9-relaunch/20260801T170000Z/pdh3-scale-bundle-r9.tgz",
      "sha256": "1e50f4a9acf7e484b34126ae51c0425fbb908a7b520fdfab63fb72cad4fa0c76"
    }
  ],
  "extracted_directory_bytes": 12847571349,
  "extracted_directory_count": 43,
  "extracted_directory_targets": [
    {
      "bytes": 58915,
      "path": ".pdh3-runtime/preflight-r1/extracted-smoke"
    },
    {
      "bytes": 57245,
      "path": ".pdh3-runtime/preflight-r2/extracted-smoke"
    },
    {
      "bytes": 57245,
      "path": ".pdh3-runtime/preflight-r3/extracted-smoke"
    },
    {
      "bytes": 57245,
      "path": ".pdh3-runtime/preflight-r4/extracted-smoke"
    },
    {
      "bytes": 57245,
      "path": ".pdh3-runtime/preflight-r5/extracted-smoke"
    },
    {
      "bytes": 57245,
      "path": ".pdh3-runtime/preflight-r6/extracted-smoke"
    },
    {
      "bytes": 57245,
      "path": ".pdh3-runtime/preflight-r7/extracted-smoke"
    },
    {
      "bytes": 356657635,
      "path": ".pdh3-runtime/r10-relaunch/20260801T185301Z/extracted-smoke-r10"
    },
    {
      "bytes": 356657761,
      "path": ".pdh3-runtime/r10-relaunch/20260801T185301Z/extracted-smoke-r10-final"
    },
    {
      "bytes": 356669334,
      "path": ".pdh3-runtime/r11-relaunch/20260801T222658Z/extracted-smoke-r11"
    },
    {
      "bytes": 356669355,
      "path": ".pdh3-runtime/r11-relaunch/20260801T224548Z/extracted-smoke-r11b"
    },
    {
      "bytes": 356902944,
      "path": ".pdh3-runtime/r12-preflight/cli-verify-r1/extracted"
    },
    {
      "bytes": 356974251,
      "path": ".pdh3-runtime/r12-preflight/full-r6-minvcpu-20260802-r1/a/extracted"
    },
    {
      "bytes": 356974251,
      "path": ".pdh3-runtime/r12-preflight/full-r6-minvcpu-20260802-r1/b/extracted"
    },
    {
      "bytes": 356668998,
      "path": ".pdh3-runtime/r12-preflight/pf0/extracted-smoke"
    },
    {
      "bytes": 356845811,
      "path": ".pdh3-runtime/r12-preflight/pf0-r2/extracted-smoke-a"
    },
    {
      "bytes": 356845811,
      "path": ".pdh3-runtime/r12-preflight/pf0-r2/extracted-smoke-b"
    },
    {
      "bytes": 356898821,
      "path": ".pdh3-runtime/r12-preflight/pf0-r3/extracted-smoke-a"
    },
    {
      "bytes": 356898821,
      "path": ".pdh3-runtime/r12-preflight/pf0-r3/extracted-smoke-b"
    },
    {
      "bytes": 356900691,
      "path": ".pdh3-runtime/r12-preflight/pf0-r4/extracted-smoke-a"
    },
    {
      "bytes": 356900691,
      "path": ".pdh3-runtime/r12-preflight/pf0-r4/extracted-smoke-b"
    },
    {
      "bytes": 356902977,
      "path": ".pdh3-runtime/r12-preflight/pf0-r5/extracted-smoke-a"
    },
    {
      "bytes": 356902977,
      "path": ".pdh3-runtime/r12-preflight/pf0-r5/extracted-smoke-b"
    },
    {
      "bytes": 356926349,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6/extracted-smoke-a"
    },
    {
      "bytes": 356926349,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6/extracted-smoke-b"
    },
    {
      "bytes": 356930348,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-controller/extracted-smoke-a"
    },
    {
      "bytes": 356930348,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-controller/extracted-smoke-b"
    },
    {
      "bytes": 356930447,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-controller-r2/extracted-smoke-a"
    },
    {
      "bytes": 356930447,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-controller-r2/extracted-smoke-b"
    },
    {
      "bytes": 356927151,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-repaired/extracted-smoke-a"
    },
    {
      "bytes": 356927151,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-repaired/extracted-smoke-b"
    },
    {
      "bytes": 356944753,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-replacement-r1/a/extracted-smoke"
    },
    {
      "bytes": 356944753,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-replacement-r1/b/extracted-smoke"
    },
    {
      "bytes": 356944753,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-replacement-r2/a/extracted-smoke"
    },
    {
      "bytes": 356944753,
      "path": ".pdh3-runtime/r12-preflight/pf0-r6-replacement-r2/b/extracted-smoke"
    },
    {
      "bytes": 356974076,
      "path": ".pdh3-runtime/r12-preflight/pf4-affinity-20260802-r1/extracted"
    },
    {
      "bytes": 356974251,
      "path": ".pdh3-runtime/r12-preflight/pf4-retry-minvcpu-20260802-r2/extracted"
    },
    {
      "bytes": 356974146,
      "path": ".pdh3-runtime/r12-preflight/pf4-retry-usmo-20260802-r1/extracted"
    },
    {
      "bytes": 356983639,
      "path": ".pdh3-runtime/r12-preflight/r6-r5-repair-bundle-r1/a/smoke-root"
    },
    {
      "bytes": 356851576,
      "path": ".pdh3-runtime/r8-relaunch-r8/20260801T110300Z/extracted-smoke"
    },
    {
      "bytes": 356640898,
      "path": ".pdh3-runtime/r8-relaunch-r8/20260801T111536Z/extracted-smoke"
    },
    {
      "bytes": 356640898,
      "path": ".pdh3-runtime/r8-relaunch-r8/20260801T111933Z/extracted-smoke"
    },
    {
      "bytes": 356650749,
      "path": ".pdh3-runtime/r9-relaunch/20260801T165000Z/extracted-smoke"
    }
  ],
  "extracted_target_list_sha256": "a8a75024a0ba15500697eae42e39e83cbb4dc7ac5b7251a87818a69adbca34e2",
  "preconditions": {
    "matching_processes_absent": true,
    "runpod_inventory_empty": true
  },
  "preserved_classes": [
    "all JSON receipts and manifests",
    "all logs and stdout/stderr",
    "all final-evidence.tgz archives",
    "all checkpoint-*.tgz archives",
    "all custody/evidence archives",
    "source and Git history",
    "operator-owned heap_profiler/"
  ],
  "retained_archives": [
    {
      "bytes": 143990825,
      "path": ".pdh3-runtime/r12-preflight/full-r6-tracer-lib-20260802-r1/a/pdh3-r12-bundle.tgz",
      "sha256": "06bbc9567967998bee21e5c5cd42e44b688c52e3ca4b8a0d78577eaad06b9a99"
    },
    {
      "bytes": 143990837,
      "path": ".pdh3-runtime/r12-preflight/r6-r5-repair-bundle-r1/a/pdh3-r12-bundle.tgz",
      "sha256": "52619301a9aa0b88e5c2e3e52d668e6485ae105eb1c0f86405d681a5945be7a6"
    }
  ],
  "scope": ".pdh3-runtime only",
  "status": "FROZEN_BEFORE_DELETION",
  "utc": "2026-08-02T13:02:00Z",
  "version": "ck-pdh3-runtime-cleanup-plan-v1"
}
```

