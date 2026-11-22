# Native Linux source-build candidate

This adds a local entrypoint; the CI driver, source pins, accepted image and
interactive launcher remain unchanged. Run it as a regular user, without sudo.
Default mode is preflight only. No GITHUB_ACTIONS spoofing is needed.

The local entrypoint reuses source authentication, safe extraction, static/config
audits and two QEMU boot checks from the reviewed CI implementation. Both top-level
make and recursive Buildroot jobs are limited to one. Compile timeout is 24 hours,
not an estimate. Logs and output stay in a fresh directory outside the checkout;
nothing is deleted automatically or retried.

## Before building

Use internal ext4 storage. The EVOO observation was 46 GB free, 3.6 GiB RAM,
1.5 GiB MemAvailable and 511 MiB swap. Only one Wi-Fi radio was connected;
this does not diagnose earlier network failures.

Preflight requires 20 GiB free, 1 GiB MemAvailable, and at least 2 GiB total swap
on hosts with under 5 GiB RAM. Close Firefox before compiling. These conservative
thresholds are operational checks, not demonstrated minimum build requirements.

Install host prerequisites (Git, Python and QEMU were installed earlier):

```sh
sudo apt install build-essential bc bison flex cpio rsync file wget unzip bzip2 xz-utils perl patch gpg
```

Preflight, from a clean checkout of this candidate:

```sh
python3 -B puppy-p0a/ci/local.py --run-dir "$HOME/puppf-runs/preflight-$(date +%Y%m%d-%H%M%S)"
```

Preflight validates packet/checker, host tools and Perl modules, available
resources, and the local fixture suite. It downloads no sources, does not compile,
and does not boot QEMU. It writes local evidence. BLOCKED is actionable; inspect
local-receipt.json and referenced logs. Do not bypass a signing/hash failure.

## Explicit build

After a passing local preflight, use another fresh run directory:

```sh
python3 -B puppy-p0a/ci/local.py --run-dir "$HOME/puppf-runs/build-$(date +%Y%m%d-%H%M%S)" --build
```

This repeats preflight, downloads authenticated source, builds once and runs two
boot checks. Each source download can fail on unreliable Wi-Fi; no automatic
fallback or retry is implemented. Keep failure evidence, fix the cause and use
a fresh directory for a separately chosen attempt. Ctrl+C terminates the active
build command process group through the existing command runner and records an
interrupted result. Do not run through a pipe that hides the entrypoint's status.

The entrypoint prints log names as stages advance. In another terminal, use
`tail -f /path/to/run/evidence/build.log` for compile progress. Work trees remain
in run/work, artifacts and logs in run/evidence. No result is uploaded automatically.

This candidate has fixture validation, not a completed native source build.
A fresh image must earn its own two-boot evidence. It is not expected to match
accepted build #11 bit for bit. Human review/acceptance stays separate.
