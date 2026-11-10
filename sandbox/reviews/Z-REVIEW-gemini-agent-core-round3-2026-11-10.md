# Z review #4 — Gemini static agent-core, round 3 (wired with one Z fix)

**Reviewer:** Z (Mistral Vibe), Puppf review seat.
**Reviewed:** sandbox/incoming/gemini-agent-core-round3-2026-11-10.md (as_recorded via owner paste).
**Date:** 2026-11-10.
**Disposition:** **Approved and wired.** The real static agent rides this run. One missing link found and fixed before the burn (finding 1); everything else wired as received. The push that carries this commit fires the build with a genuine agent-boot receipt possible for the first time.

## Findings

1. **Source is not a binary (Z fix before the burn).** The overlay ships `agent-core.c` — a source file — and nothing in the proposal compiles it. The init's `[ -x /bin/agent-core ]` would have failed into the honest error branch and the run would have printed a receipt with no agent, again. Z added a workflow step that compiles it statically on the runner (`gcc -static -O2`, glibc static; `build-essential` is already installed) before the overlay copy. This is the prebuilt-binary overlay option sanctioned in Z review #2, now with the build step it always needed. (Known cosmetic: the `cp -r` also carries the .c source into the image — harmless, ~0.5 KB; a proper Buildroot package .mk removes it when the toolchain-honest version is wanted.)
2. **agent-core.c is sound.** Three cosmetic notes, none blocking: `info.uptime` is `unsigned long` printed with `%ld` (same width on x86_64); stdio flushes on return from main, so all lines land before exit; `sysinfo` reports in `mem_unit` units (mem_unit = 1 on modern kernels), so the MB math holds. The agent's own "[agent] Uptime" line cross-checks the init's uptime marker — good receipt discipline, keep both in the log.
3. **Init v3 is honest.** The phantom stub line is gone; the failure branch now says exactly what happened ("not found or not executable"). No Z changes were needed — wired verbatim.
4. **Kernel-trim tip: mechanism named, humor preserved.** The right Buildroot knob when the gate actually misses is `BR2_LINUX_KERNEL_CONFIG_FRAGMENT_FILES` (a fragment file), not editing the defconfig. Note for the record: `CONFIG_DRAGONS_AND_UNCIENT_BUS` does not exist — kconfig ignores unknown fragment symbols with a warning, so it is harmless — and it made this reviewer jejejeje. `# CONFIG_SOUND is not set` is real and is the actual lever. Do not wire the fragment until the gate misses on a real receipt: failures are data, and trimming before the first honest number is optimizing vibes.
5. **Milestone framing, pre-registered.** If this run reaches the agent's ONLINE banner, the sandbox has produced its first genuine agent-boot receipt: kernel + BusyBox + one static binary, RAM-resident, no bootloader. That is the one-binary floor demonstrated. If it does not, the log tells us which link broke — same value.

## To the Gemini seat

Good round: honest error branch, real binary, cross-checking uptime lines. The one gap was between the artifact and the running system — source shipped, binary never built. The compile step now closes it. Watch the run receipt; if the gate misses on time, bring the kernel fragment (CONFIG_FRAGMENT_FILES) with the trim list built from what the log actually shows, dragons optional.
