# Received proposal — preserved verbatim

- **Received:** 2026-11-10, pasted by MarkDude (owner) from the Gemini chat seat.
- **Provenance:** `as_recorded` — copied through chat transport; no execution claimed.
- **Z review:** see ../reviews/Z-REVIEW-gemini-one-binary-floor-2026-11-10.md

---

Z's review hits the nail on the head. Using debootstrap introduced a heavy distribution model that completely bypassed the pinned Buildroot 2026.08, Linux 6.18.7, and BusyBox 1.38.0 stack, failing right where standard distros rely on hidden package management. That feedback is precisely why sandboxes exist.

Let's shift to an architecture that respects the actual constraints and pushes into the unexplored territory: The One-Static-Binary Floor with Direct Kernel-Initramfs Boot (Zero ISO, Zero SquashFS overhead, direct QEMU execution).

## The Sandbox Experiment: Direct Kernel + Initramfs RAM OS

Instead of building an ISO via GRUB, we bypass bootloaders entirely. We configure Buildroot to bake the entire root filesystem directly into a compressed initramfs (rootfs.cpio.gz) compiled into the Linux 6.18.7 kernel image, and boot QEMU in seconds with -kernel and -initrd.

To achieve the one-static-binary floor, PID 1 can either be a statically compiled agent binary itself or a minimal static C wrapper that mounts pseudo-filesystems (proc, sysfs) and immediately execs the agent.

### 1. Buildroot Configuration Adjustments (configs/puppy_agent_defconfig)

To strip out unnecessary userland fluff and enforce an initramfs-only target:

```
BR2_x86_64=y
BR2_TOOLCHAIN_BUILDROOT_UCLIBC=y
BR2_LINUX_KERNEL=y
BR2_LINUX_KERNEL_CUSTOM_VERSION=y
BR2_LINUX_KERNEL_CUSTOM_VERSION_VALUE="6.18.7"
BR2_LINUX_KERNEL_DEFCONFIG="x86_64"
BR2_TARGET_ROOTFS_INITRAMFS=y
BR2_TARGET_ROOTFS_CPIO=y
BR2_TARGET_ROOTFS_CPIO_GZIP=y
# Strip package bloat; keep only BusyBox and static agent requirements
BR2_PACKAGE_BUSYBOX=y
```

### 2. Custom Minimal Init (/init inside the Initramfs)

If PID 1 is a static shell script or a static binary, it initializes the bare minimum needed for agent execution:

```sh
#!/bin/sh
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev

echo "=== Puppf Agent Micro-OS Booted ==="
echo "Running kernel: $(uname -r)"

# Execute the static agent binary directly
exec /bin/agent-core
```

### 3. Direct QEMU Acceptance Run & Timing Receipt

To test the boot-to-first-agent-action timing without ISO mounting overhead, the QEMU invocation command captures the exact performance receipt:

```sh
time qemu-system-x86_64 \
  -kernel output/images/bzImage \
  -initrd output/images/rootfs.cpio.gz \
  -nographic \
  -append "console=ttyS0 panic=1" \
  -m 256M \
  -no-reboot
```

Expected Receipt Metrics to Log:

- **Artifact Footprint:** bzImage + rootfs.cpio.gz combined size (target: < 15MB).
- **Cold Boot to Agent Execution:** Measured via time utility from process spawn to exec /bin/agent-core initialization (target: < 800ms).
- **Memory Footprint:** Resident Set Size (RSS) inside QEMU at idle.
