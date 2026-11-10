# Z review #2 — Gemini one-static-binary floor proposal

**Reviewer:** Z (Mistral Vibe), Puppf review seat.
**Reviewed:** sandbox/incoming/gemini-one-binary-floor-proposal-2026-11-10.md (as_recorded via owner paste).
**Date:** 2026-11-10.
**Disposition:** **Approved for sandbox implementation** per the branch charter — free experimentation, nothing transfers to the main route without normal gates. This is the first sandbox proposal that respects the pinned stack. Three design gaps and one acceptance-math correction below; none block starting.

## What it is, honestly placed

Initramfs-only RAM OS: pinned Buildroot 2026.08 / Linux 6.18.7 / BusyBox 1.38.0, whole rootfs in the boot path, QEMU -kernel/-initrd, no bootloader/ISO/squashfs, agent at or behind PID 1. Structurally this is the main route's skeleton (P0a is also Buildroot → QEMU direct boot). The deltas that make it a real sandbox experiment:

1. PID 1 = static agent binary (main route: BusyBox init).
2. Initramfs linked into the kernel image (main route: external initrd).
3. Timing-first acceptance (boot-to-first-agent-action) — the main route has never measured this as a target.

## Findings (fix during the build; they are now the implementer's design calls)

1. **Double initramfs path.** BR2_TARGET_ROOTFS_INITRAMFS (embedded in bzImage) AND an external -initrd rootfs.cpio.gz are both specified. A modern kernel lets the external initrd overwrite the embedded one, so it boots — but pick one. Recommended: **external initrd only** (drop INITRAMFS), so an agent-core change never relinks the kernel. Iteration speed is the sandbox's whole advantage.
2. **No recipe yet for getting agent-core and /init into the rootfs.** The defconfig has no BR2_ROOTFS_OVERLAY and no package recipe. Decide: overlay carrying a prebuilt static binary (fast, less honest about the toolchain) or a proper Buildroot package .mk (honest static build). Either way the defconfig needs BR2_STATIC_LIBS=y — without it the "static" agent links uClibc shared and the one-binary floor claim fails at boot.
3. **Run-end condition undefined.** panic=1 + -no-reboot makes QEMU exit when PID 1 exits — but a persistent agent (the idle-RSS measurement) never exits. Define the receipt's end: agent self-exits after logging metrics, or a watchdog timeout wraps the QEMU invocation (the main route's watchdog doctrine).
4. **Timing target vs hosted-runner reality — the hardware receipt.** GitHub-hosted runners expose no /dev/kvm; QEMU runs pure TCG emulation. The main route's own spike already measured hosted-runner boots in whole seconds (first-heartbeat gate uptime_s <= 15 s). An 800 ms cold-boot target is not reachable on TCG by code quality; it is a KVM/bare-metal number. Recommended dual gate:
   - **Primary (hosted runner, TCG):** guest /proc/uptime at the agent's first output line (uptime_s), target < 5 s. Same metric as the main route, so numbers stay comparable.
   - **Aspirational (KVM/bare-metal, logged when such hardware exists):** < 800 ms.
   Also: host `time` around QEMU measures process lifetime, not boot-to-agent. Parse the serial log for the agent's first line and log in-guest uptime_s alongside host wall time.
5. **RSS at idle, concretized.** Guest RSS has no swap semantics; log /proc/meminfo MemTotal/MemFree at first agent action, plus agent-core VmRSS from /proc/self/status if the agent can print it.

## What's good

- The static-wrapper-then-exec /init is the cleanest possible version of the one-binary floor.
- Keeping the main route's pins makes sandbox receipts speak the same vocabulary as main-route receipts.
- The < 15 MB combined footprint target is a real, cheap, honest metric. Keep it.

## To the Gemini seat

Approved. Findings 1-3 are your design decisions now; finding 4 is the one that changes your acceptance math. Deliver via Mark ferry or branch access. A run that misses the TCG number is not a failed experiment — re-read the charter: failures are data.
