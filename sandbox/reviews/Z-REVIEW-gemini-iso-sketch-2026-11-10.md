# Z review — Gemini "Build Minimal Agent Linux ISO" sketch

**Reviewer:** Z (Mistral Vibe), Puppf review seat.
**Reviewed:** sandbox/incoming/gemini-build-minimal-agent-linux-iso-2026-11-10.yml (verbatim, as_recorded via owner paste).
**Date:** 2026-11-10.
**Disposition:** Received as a **sandbox exhibit**, not a main-route candidate. No merge recommended in current form. Sandbox trial chartered on this branch by Mark — see ../README.md.

## Findings

1. **Never executed; step 5 cannot succeed as written.** `debootstrap --variant=minbase` installs no kernel. `/tmp/rootfs/lib/modules` is empty and `/tmp/rootfs/boot/vmlinuz-*` does not exist, so "Prepare Kernel and Initramfs" fails (empty `ls`, failed `cp`). Prediction: first run of the branch-local copy fails at this step. This is a fixture-of-the-mind, not a tested artifact — the exact class Puppf's fixtures-vs-runner separation exists to catch.
2. **"RAM Mode" is a label, not a behavior.** `boot=live` requires Debian live-boot initramfs scripts to locate and mount `filesystem.squashfs`; a stock initrd does not have them, and the grub.cfg never references the squashfs. Best case even with a kernel present: boot stops in the initramfs. No RAM-load claim is earned until a boot proves it.
3. **Zero trust chain.** debootstrap pulls whatever is current from deb.debian.org at run minute — no version pins, no signatures, no digests. The main route's product is pinned trust (Buildroot 2026.08 / Linux 6.18.7 / BusyBox 1.38.0, byte-pinned key, one acceptable VALIDSIG). This recipe builds an anonymous Debian-of-the-day.
4. **No gates.** Push-trigger auto-burns a full build per commit (main route: owner-dispatch only); `ubuntu-latest` drifts (we pin ubuntu-24.04); actions pinned to tags, not SHAs; no timeout, no permissions block, no concurrency guard; exit 0 means "a file exists," never "it booted."

## Where the idea fits

- The `agent-overlay` injection step is the same idea as our Buildroot external overlay — sound pattern.
- The squashfs → `grub-mkrescue` route is the standard ISO shape and a legitimate P0c-shaped sketch (UEFI/laptop/ISO lane). If something proves out in the sandbox, it earns a normal packet, pinned gates, two boots, and receipts before any transfer to the main route. Nothing from the sandbox transfers by default.

## Challenge to the Gemini seat

Repair the ISO path if you like — but the real ask is ideas we did NOT take: initramfs-only RAM OS (no squashfs/ISO at all), musl/static or Alpine apk base, the one-static-binary floor, a reproducible Nix/Guix build expression, or boot-to-first-agent-action timing runs. Whatever you try, produce a receipt: exact commands, run logs, artifact sizes, honest failure lines. A real failed run beats plausible YAML every time.
