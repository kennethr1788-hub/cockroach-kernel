# PDH-3 Ubuntu Strace Provenance Receipt R1

- `DISTRIBUTION`: `Ubuntu 24.04 LTS Noble`
- `ARCHITECTURE`: `amd64`
- `OFFICIAL_PACKAGE_INDEX`:
  `https://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz`
- `OFFICIAL_PACKAGE_INDEX_SHA256`:
  `e0d7e4cbb09d2aa7f9e104a1488817417bc9d85f3e5d9a21156a52ec641ae531`
- `STRACE_PACKAGE`: `strace 6.8-0ubuntu2`
- `STRACE_DEB_SHA256`:
  `d588810ae26b06fee6678dc81e5b54f6efcde8e718e4589adb4d11d254b9820b`
- `STRACE_DEB_BYTES`: `584172`
- `STRACE_BINARY_SHA256`:
  `28f957c227012de0b18d1bd7fff2d396cb693ea60ed8013be68de071e84b5001`
- `STRACE_BINARY_BYTES`: `2087432`
- `LIBUNWIND_PACKAGE`: `libunwind8 1.6.2-3build1`
- `LIBUNWIND8_DEB_SHA256`:
  `658977d18976149b75391850ba0ccacaf7bde3201f0284189da50cd634334d17`
- `LIBUNWIND8_DEB_BYTES`: `55198`

Both packages were downloaded over HTTPS from paths named by the official
Ubuntu Noble package index. Their SHA-256 values match the index before
inclusion in the deterministic transfer archive.

The `.deb` files are not installed globally. On the disposable worker,
`dpkg-deb -x` extracts them under the campaign root. The trace wrapper accepts
only the extracted binary at the exact SHA-256 above. The worker performs no
package-registry request and receives no package credential.
