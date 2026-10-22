# Puppf P0a — disposable Buildroot/QEMU implementation

This is implementation code awaiting Z review and Mark's manual GitHub Actions
dispatch. No successful source authentication, Buildroot build, payload size,
memory-use measurement or guest boot is asserted by this document. Synthetic
fixture results are checker self-tests only.

Puppy Linux and Barry Kauler inform the small, rebuildable method. This artifact
is not designated a Puppy/Fedora distribution or a security containment system.
The Buildroot image is a throwaway spike; configuration, tests and evidence are
the reusable outputs. P0b ACK, P0c UEFI/laptop, S0 and model APIs remain separate.

## Entry point and authorization

The existing, route-owned workflow on `ubuntu-24.04` invokes:

```sh
bash puppy-p0a/ci/run-ci.sh
```

Mark selects **build** in the manual workflow after reviewing/merging or selecting
the reviewed branch. Codex does not dispatch it. The driver requires
`GITHUB_ACTIONS=true`, `PUPPF_MODE=build`, `RUNNER_TEMP` and a fresh external
`PUPPF_EVIDENCE_DIR`; it refuses an existing receipt or first-run directory.
`PUPPF_EXPECTED_PACKET_SHA256` must match the dispatch's fixed expected digest.
There is no local build mode, cache reuse, paid fallback or automatic retry.

The workflow installs the host prerequisites. The driver checks QEMU x86-64,
gcc/g++, make, cpio, rsync, bc, flex, bison, git, Python 3.12+, GnuPG, binutils,
file, wget, tar, gzip/bzip2/xz, unzip, Perl, patch and awk. This includes tools
already provided by the standard hosted image. It records host versions,
CPU/memory/disk observations and runner metadata. Less than 10 GiB scratch free
causes BLOCKED for lead review; it does not delete other runner directories.
Compilation uses at most four jobs and a clean temporary output/download tree.

Failures in route-owned checkout/preflight/APT steps occur before this entrypoint
and can only have the YAML's logs, not this driver's receipt. The implementation
does not edit the workflow to conceal or work around that boundary.

## Source authentication and pins

`source-lock.json` pins Buildroot 2026.08, Linux 6.18.7, BusyBox 1.38.0 and the
repository packet checker's SHA-256. The checker is hashed **before** execution;
its actual digest and verification time are also recorded in the receipt.

Buildroot's release archive and detached signature come from `buildroot.org`.
Its release public key comes from `keys.openpgp.org` and must match fingerprint
`F0A589A56CFE2C6D68E9471AED04E0FBE016E856`. This fingerprint was extracted from
upstream's annotated release tag object
`813cbac680a73092e1ebb86da72972c44573145c` (commit
`d5180309b1b66ef3b8eaccca70ad69be8e0729a1`) in the
[Buildroot upstream mirror](https://github.com/buildroot/buildroot/tree/2026.08).
Z should review this trust anchor as part of the implementation diff.

The runner uses an isolated GnuPG keyring, verifies the exact downloaded archive
signature and requires the pinned `VALIDSIG` signer before extracting anything.
TLS remains enabled. There is no insecure/alternate-source fallback. Inaccessible
key/signature/archive, wrong key or failed verification produces BLOCKED, not a
fabricated archive digest. The authenticated archive's SHA-256 is then recorded.
Availability and successful verification have **not** been tested locally.

The signed Buildroot distribution's QEMU Linux hash and BusyBox hash must match
our lock. Buildroot's force-check-hashes option remains enabled for dependent
downloads. Other package/toolchain versions are pinned by that authenticated
distribution and selected configuration; `package-info.json`, download digests,
resolved configs and compiler version output record what was actually built.
No bit-identical rebuild is claimed.

## Guest and actual boot checks

The custom kernel config disables networking, modules, block devices, DRM and
sound. The driver audits the resolved networking/static/serial settings and
checks BusyBox ELF program/dynamic headers for a dynamic loader or dependencies.
The runtime consists of a compressed initramfs, static BusyBox and `/init`.

`/init` mounts proc/sys/devtmpfs, binds the serial terminal, emits an init marker,
starts the 120-second heartbeat and provides an interactive serial shell. HELLO
uses integer **absolute kernel uptime from `/proc/uptime`**, never wall time.
Leading newlines keep asynchronous heartbeat records separate from shell prompts.

The host launches real QEMU with direct kernel/initramfs, TCG, 128 MiB, one vCPU,
`-nodefaults`, `-nic none`, no display, no monitor, no host drives/shares and no
restart. This is not UEFI or a complete ISO and does not establish containment.
The exact argument list is captured for each run.

Each boot requires:

- Prompt and exact fresh shell-token output within 90 host-monotonic seconds.
  The probe's input splits the token into two arguments; the full token is absent
  from the input command. Only a separate exact output line counts.
- Three HELLO records, exactly sequence 1,2,3, first guest uptime at most 15.
- Guest gaps 115–125 seconds and host-arrival gaps 105–150 seconds.
- A 390-second per-boot watchdog; no retired 240-second span floor.
- No panic, repeated init marker, shell restart or unexpected QEMU exit.

The driver stops its QEMU process after collecting the evidence and a short grace
interval. It then boots again with the same artifact hashes and guest settings,
using a different token and separate logs. It checks artifact hashes before/after
each boot and across runs. A failed first run stops immediately; there is no
second boot to turn a failure into a pass.

## Evidence, receipts and exits

The workflow uploads `$PUPPF_EVIDENCE_DIR` even on failure, under its existing
three-day retention policy. Mark must retain desired artifacts before expiry.
Only small image artifacts and sanitized evidence are uploaded, not build trees
or credentials. Outputs include:

- `receipt.json`: role Codex, attempt 1, checker hash, exact packet hash, actual
  checkout/run references, stage/stop reason and pending Z/Mark decisions.
- `build-manifest.json`, package/version/toolchain logs, resolved `configs/`,
  signature/key verification logs and dependency-download digests.
- `artifacts.json` and `artifacts/{bzImage,rootfs.cpio.gz}` with individual byte
  sizes and SHA-256; combined size must be strictly below 100,000,000 bytes.
- `run-1/` and `run-2/`: raw `serial.log`, timestamped `serial-events.jsonl`,
  `qemu-argv.json`, `shell-probe.json` and `test-results.json`.
- `fixture-results.json`, `checker-fixtures.log`, cross-run comparison and an
  evidence hash manifest. Workflow-owned live console logs are excluded from
  that manifest because their writers remain active until the script exits.

RAM allocation is recorded as 128 MiB. Guest resident use, minimum RAM, complete
ISO size and unavailable platform usage/cost remain null. Model self-report is
not telemetry. Exit 0 means this runner's checks passed with human review still
pending; exit 2 means BLOCKED; exit 1 means FAIL. The first receipt ends the run.
Further repairs require a fresh dispatch. Nothing accepts or merges its own work.

## Local authoring checks (no download, build or QEMU)

From the repository root:

```sh
bash -n puppy-p0a/ci/run-ci.sh
sh -n puppy-p0a/buildroot-external/overlay/init
python3 -B -m unittest discover -s puppy-p0a/tests -v
```

The fixture suite covers missing/reordered/duplicate/extra HELLO, malformed
uptime, first-uptime violation, independent guest/host timing errors, watchdog,
missing/late/early/duplicate shell output, echo-only false positives, panic/reboot,
modified checker, incorrect signer, unsafe archive paths and missing QEMU.
Its QEMU-launch failure test mocks the process; it does not start a guest.

## Honest gaps before manual runner evidence

Release/keyserver accessibility and archive signature validation, Buildroot
Kconfig resolution, compilation, runner disk fit, actual payload size, first
guest uptime, shell availability and both boots' timing are unmeasured. These
are runner tasks, not local-environment blockers or passing fixture results.
Shellcheck is optional and was unavailable in the authoring environment.
