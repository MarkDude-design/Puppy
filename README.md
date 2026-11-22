# Puppf

A minimal, evidence-first Linux boot spike: a kernel + initramfs pair under 4 MB that boots offline in a 128 MiB QEMU guest — built from pinned source, and re-proven by rebuilding it byte-for-byte on modest hardware.

Puppf is a learning and validation project: packet-based Buildroot experimentation, written acceptance criteria, and receipts-before-claims discipline. It is **not** a finished distribution, not a Puppy Linux fork or derivative, and not a security boundary — the guest is a disposable serial-only proof. The working name honors the method it draws from (see lineage below).

## What it is

- **Image pair:** bzImage (3,286,016 bytes) + BusyBox/musl initramfs (754,850 bytes), combined 4,040,866 bytes. Kernel 6.18.7, Buildroot 2026.08, BusyBox v1.38.0.
- **Behavior:** boots to a `PUPPF_INIT` banner on a serial console, prints a `HELLO seq=N uptime_s=N` heartbeat every 120 seconds, and runs a `PUPPF#` shell loop (shell exits restart the shell). Echo is off and line editing disabled: deliberate choices for the automated acceptance lanes; the human-usability variant is specified in the evidence thread and retired for this generation by owner ruling.
- **Guest settings:** 128 MiB RAM, TCG software emulation, no network, no host disks.

## Verified state (November 2026)

- **M1 accepted (2026-11-04):** hosted build #11 passed two genuine QEMU boots with signed provenance (clearsigned manifest, pinned key) and owner acceptance.
- **First native source build (2026-11-22):** built from source on a 4 GB RAM Celeron laptop with a one-job runner in about 5 hours; both resulting images were **byte-for-byte identical to accepted build #11** — confirmed by independent SHA-256 recomputation, and by extracting the binary `/init` from the delivered image and byte-comparing it to the reviewed source `overlay/init`.
- **Reproducibility scope:** two builds, two different hosts, matching bytes. That is a two-build fact, not a general reproducibility guarantee.
- **Testing doctrine (owner ruling, 2026-11-22):** for this generation and the next, testing is automated. Acceptance = mechanical ground truth (hash pins, two-boot checks, byte-level content assertions) plus cross-family model review with disagreements preserved verbatim.

## Start here

- **[Evidence and acceptance thread — issue #15](issues/15)** — the chronological record of every build, review, and ruling. Read from the top.
- **Actual binaries:** the accepted images live on the immutable [`artifacts/evoo-build-001`](tree/artifacts/evoo-build-001) branch with pinned `SHA256SUMS`.
- **Launcher:** [PR #21](pull/21) — pinned offline terminal launcher. Hash-verifies the evidence ZIP, copies images to a temp dir, restores the host terminal on Ctrl+C. Draft.
- **Native build runner:** [PR #25](pull/25) — explicit local Linux entrypoint. Preflight by default, one-job enforcement, resource checks, and it refuses to run when `GITHUB_ACTIONS` is set. Draft.
- **Workstation guide:** [PR #24](pull/24) — how the laptop was set up (Lubuntu) and how the accepted image is verified and run.
- **Serial test harness:** [PR #20](pull/20). **Origin and recovery archive:** [PR #23](pull/23).

## Launching the accepted image locally

- **One command, offline:** see [`puppy-p0a/LAUNCH.md`](puppy-p0a/LAUNCH.md). The launcher (`puppy-p0a/launch.py`) hash-verifies the original accepted build #11 evidence ZIP and both image members (64 MiB input bound, no archive-path extraction), copies only the two known images into a private temp directory, and starts QEMU under the same 128 MiB serial-only guest contract.
- **Without booting:** `--verify-only` checks accepted bytes with Python alone; `--check` also confirms host and QEMU presence. Neither starts the VM.
- **Cleanup contract:** Ctrl+C stops the VM, restores host terminal settings, and removes the temp copies. Guest `exit` only restarts the guest shell.
- **Status:** the first-user interactive demo is retired for this generation by the owner ruling recorded above; this launcher is the mechanical offline path.

## Repo map

- `puppy-p0a/` — the spike: Buildroot external tree (overlay, busybox.config, pinned source packet and hashes); launcher and local-build instructions live on the PR #21/#25 stack.
- `ci/` — the hosted Actions driver. Actions-only by design: do not spoof `GITHUB_ACTIONS` to run it locally — use the PR #25 native runner instead.
- `docs/workflow/runs/` — evidence receipts per run (e.g. `PUPPF-LOCAL-001/EVIDENCE-REVIEW.md`).

## Ground rules

- Claims trace to receipts: every acceptance statement links the evidence that produced it. Records are append-only; corrections supersede, never erase.
- No credential ever belongs in this tree; secrets live in repository settings only.
- Nothing in this repo claims a release, endorsement, or hardware-compatibility promise.

## Method lineage

This experiment draws inspiration from **Puppy Linux and Barry Kauler's** small, user-directed, rebuildable Linux approach. It is not designated a Puppy fork, derivative distribution, or Fedora distribution, and no affiliation or endorsement is implied.
