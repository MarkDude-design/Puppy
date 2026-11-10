# RECEIPT: Reproducibility of Pinned P0a Builds

## Question
Do two clean, sequential builds of the pinned P0a source (Buildroot 2026.08, Linux 6.18.7, BusyBox 1.38.0) within the same GitHub Actions runner environment produce bit-identical artifact digests (SHA-256 for `bzImage` and `rootfs.cpio.gz`)?

## Hypothesis
The builds will produce **non-identical** digests due to subtle non-determinism in the build environment (e.g., filesystem timestamps, build order variations, or environment variable leakage), despite pinned sources and Buildroot's reproducibility features. *(Note: A result of identical digests is equally valid and informative, confirming strict determinism).*

## Discriminating Test
1. Execute the P0a build process twice in the same GitHub Actions job, ensuring a complete wipe of the build directory and environment between runs.
2. Capture the SHA-256 digests of the resulting `bzImage` and `rootfs.cpio.gz` from Run 1 and Run 2.
3. Compare the digests using a strict string equality check.

## Expected Output
- **Deterministic**: `DIGEST_RUN1 == DIGEST_RUN2` for both artifacts.
- **Non-deterministic**: `DIGEST_RUN1 != DIGEST_RUN2` for one or both artifacts.

## STOP Condition
The test halts immediately after the second build completes and the digest comparison is evaluated and logged. No third build or automatic retry is attempted.

## Actual Result
ACTUAL RESULT:
- bzImage Match: YES
- rootfs Match: YES
- Run 1 bzImage: `75bb3de22351a5e97c601650210dcbdcbf385ad69c9bd1bfb90b4832a628bfe7`
- Run 2 bzImage: `75bb3de22351a5e97c601650210dcbdcbf385ad69c9bd1bfb90b4832a628bfe7`
- Run 1 rootfs: `2d51be705deca6b606c6e2de15311d7669576b52d12e83801e670981aa1c089e`
- Run 2 rootfs: `2d51be705deca6b606c6e2de15311d7669576b52d12e83801e670981aa1c089e`

Conclusion: REFUTED: digests are bit-identical across clean builds; the non-determinism hypothesis is not supported.
*(To be populated by the GitHub Actions runner upon execution of `test-reproducibility.sh`. Negative results are welcome and preserved.)*
