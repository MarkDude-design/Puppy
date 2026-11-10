# Received — no-BusyBox design (round 5) — preserved verbatim

- **Received:** 2026-11-10, pasted by MarkDude (owner) from the Gemini chat seat.
- **Provenance:** `as_recorded` — copied through chat transport.
- **Transport glitch, kept [sic]:** the received text contains `#镇include <sys/reboot.h>` — a corrupted byte in the include line (should be `#include`). The bus keeps corrupted bytes marked, not silently fixed; it is evidence of chat-transport byte corruption, harmless here because review caught it.
- **Z review:** see ../reviews/Z-REVIEW-no-busybox-and-first-run-2026-11-10.md

---

Committing receipts directly to sandbox/receipts/ with loop guards solves the visibility bottleneck. Having the actual run data sitting right on the branch means every seat reads the exact same ground truth.

If the TCG uptime gate passes, the next architectural leap is the no-BusyBox floor—eliminating BusyBox entirely and promoting agent-core to PID 1.

## The No-BusyBox Architecture (Kernel + 1 Binary)

When the agent binary itself runs as PID 1, it takes total control of the boot lifecycle via direct system calls, bypassing shell scripts and external utility binaries altogether:

**Direct Filesystem Mounting:** Instead of calling /bin/mount, agent-core invokes the mount() system call directly:

```c
mount("proc", "/proc", "proc", 0, NULL);
mount("sysfs", "/sys", "sysfs", 0, NULL);
mount("devtmpfs", "/dev", "devtmpfs", 0, NULL);
```

**Zero-Overhead Event Loop:** The agent starts its core logic immediately as the first userspace thread in existence, stripping out init scripts, environment setup overhead, and unused shell applets.

**Clean Termination via Syscall:** Instead of spawning /sbin/poweroff, PID 1 issues the reboot syscall directly:

```c
`#镇include <sys/reboot.h>`  [sic — transport-corrupted byte; should be #include <sys/reboot.h>]
// ...
reboot(LINUX_REBOOT_CMD_POWER_OFF);
```

We await the committed receipt on sandbox/gemini-lab-20261110 to see the actual TCG uptime and memory snapshot. Once those numbers land, we will know whether to trim the kernel fragment or drop BusyBox for the single-binary floor.
