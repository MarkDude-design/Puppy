This supplies the implementation entrypoint required by the merged PUPPF-P0A-CI-001 route. It authors the pinned Buildroot configuration, serial guest, QEMU harness, negative fixtures, and receipt/manifest generation. Actual source authentication, compilation and guest acceptance remain unrun.

Refs #6 and route PR #7.

Allowed paths touched:
- `puppy-p0a/**`
- `docs/workflow/runs/PUPPF-P0A-002/**`

Authoring base: `5af56727d8c1a21acf38ae608a5291de83f667c4` (merged route on main).

Frozen packet SHA-256, verified using the repository checker:
`b0417934776c214ca3189c8822b85baf1e71fc262f66ada98bce2092f07c9c9b`

Checker SHA-256, pinned before execution and recorded in receipts:
`4287793c49e32589d71536d22f5cf311b8652106fc47c4e622d3cf8fe9c75de2`

Packet bytes, hash companion, workflow YAML and route notes are unchanged. The old BLOCKED branch and commit `ea0465207a5394d27e8b1383168bb368d8ce4553` remain preserved.

Implementation behavior to review:
- Runner-only `bash puppy-p0a/ci/run-ci.sh`; no local build or autonomous dispatch/retry.
- Buildroot 2026.08 archive authenticated with detached signature and pinned signer; verification/download failure produces BLOCKED without fallback. Signed-distribution Linux/BusyBox hashes must match the reviewed lock.
- Static BusyBox and serial-only custom init/kernel configuration, followed by two actual QEMU boots using unchanged artifacts, 128 MiB, no NIC/shares/drives, exact shell-output proof and frozen HELLO timing checks.
- Separate serial logs, host-arrival records, QEMU arguments, resolved configs, artifact sizes/hashes, source manifests and first receipt. Unknown usage is null; Z/Mark decisions remain pending.

Local authoring validation performed:
- 26 Python tests passed, including malformed/missing/reordered/duplicate HELLO, clock errors, timeout, echo-only shell false positives, checker tampering and source/harness failure cases.
- `bash -n`, `sh -n`, Python AST parsing and packet/checker digest checks passed.
- Tests mock QEMU launch failure; they do not boot a guest. Shellcheck was unavailable.

Honest gaps:
- Release archive/keyserver access, the release signature and pinned signer trust anchor still need runner/reviewer verification.
- Buildroot Kconfig resolution, compilation, hosted disk fit, payload size, serial shell and both real boots/timing have not been exercised.
- Route-owned checkout/preflight/APT failures precede the entrypoint and have workflow logs, not this driver's receipt.
- The committed receipt is `AUTHORED_NOT_RUN`, not acceptance or a passing build. No workflow run, S0 work, model/provider API call or merge was performed.

Please have Z review. Mark retains merge and manual workflow dispatch authority. Stop after this authoring handoff; any runner FAIL/BLOCKED receipt requires review and a fresh repair dispatch.
