# Z Review #9 — Run #2 Receipt Parse: Headers ABI Mismatch + Publish Race (2026-11-10)

Seat: Z (curator). Lane: sandbox/gemini-lab-20261110. Receipt: run 42879586450,
attempt 1 — BANKED VERBATIM at sandbox/receipts/run-42879586450/ (summary.md +
build-tail.log), owner-extracted from the Actions artifact because of F2 below.

## Outcome

BUILD FAILED at ~16 minutes. GATE RESULT: NOT RUN. AGENT RESULT: NOT RUN.
Correction to the earlier suspicion: this was NOT the 120-minute wall — the
run died on its own error, well inside budget. The clock was never the suspect;
the config was.

## F1 — the build abort (root cause, confirmed from the log tail)

The defconfig pinned the KERNEL (BR2_LINUX_KERNEL_CUSTOM_VERSION_VALUE=
"6.18.7") but never selected the TOOLCHAIN's kernel headers. With nothing
selecting any BR2_TOOLCHAIN_HEADERS_AT_LEAST_* level, the ABI expectation fell
back to Buildroot's "2.6" floor while the linux-headers package installed
6.18.7. check-kernel-headers.sh (strict) aborted:

    Incorrect selection of kernel headers: expected 2.6.x, got 6.18.x

Fix applied in this commit:

    BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_6_18=y
    BR2_DEFAULT_KERNEL_HEADERS="6.18.7"

Symbol names verified against Buildroot's own toolchain/linux-headers Kconfig
(6.18 headers support confirmed present; CUSTOM_6_18 selects
TOOLCHAIN_HEADERS_AT_LEAST_6_18, which lifts the recorded expectation off the
2.6 floor). Headers and kernel are now pinned to the same 6.18.7 — one source
of truth, per the pinned-source doctrine.

## F2 — the silent publish (root cause, confirmed from branch history)

The run DID generate its receipt — but the publish step pushes without
rebasing. At publish time (~19:08Z) the remote had already advanced (the
round-6 bank landed 18:55Z, mid-run), so the plain git push was rejected
non-fast-forward and the receipt never reached the branch. The owner extracted
it from the run artifact (retention 7 days). Fix applied in this commit:
git pull --rebase before push in the publish step. Mid-run branch movement is
normal on this lane — curator banks land whenever reviews complete — so the
publish step must tolerate it.

## Ownership

F1 is a WIRING-SIDE miss. The defconfig came from the seat's round-2 proposal
and was banked and wired without checking the headers selection. The runner
caught what the seat, the curator, and three review rounds all missed.
jejejeje — the reviewer's own gap, caught by the machine, banked without edits.
This is the receipts-first design doing exactly its job: plausible-but-never-
executed config is the failure class, and the discriminator is the run itself.

## Sequencing

This is a BUILD-FAILED receipt, not a baseline pass. The round-7 no-BusyBox
core stays HELD. Migration arms when a receipt shows GATE and AGENT actually
RUN — i.e., the build completes far enough to boot QEMU at all. A failing
gate is still a baseline (it means the pipeline reached the floor); an aborted
build is not.

## Run #3 (armed by this push)

Fixed headers + fixed publish. Expected shape: build proceeds past
linux-headers into toolchain and kernel; a full uclibc + 6.18.7 build on a
hosted runner is roughly 20-90 minutes, inside the 120-minute budget. Then
the lane's first-ever QEMU attempt, and the first receipt with real GATE and
AGENT results — pass or fail, it is the baseline the migration has been
waiting for.
