# Received proposal, round 3 — preserved verbatim

- **Received:** 2026-11-10, pasted by MarkDude (owner) from the Gemini chat seat.
- **Provenance:** `as_recorded` — copied through chat transport; no execution claimed.
- **Z review:** see ../reviews/Z-REVIEW-gemini-agent-core-round3-2026-11-10.md
- **Gap found by Z before wiring:** the overlay ships `agent-core.c` (source); nothing in the proposal compiles it, so the init's `-x` check would have failed into the honest error branch. Z added a static compile step to the workflow (annotated). Everything else wired as received.

---

Z's adjustments keep the sandbox honest: no phantom claims about unexecuted binaries, strict receipt gates, and a clear path toward trimming the standard x86_64 kernel defconfig if TCG emulation stretches boot times past the 5-second gate.

To turn this run into a genuine agent test, we replace the shell stub with a 10-line static C agent (agent-core.c) that reads its environment, dumps the sandbox state, and exits cleanly to close the receipt.

## The Static Agent Core (board/puppf/overlay/bin/agent-core.c)

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/sysinfo.h>

int main() {
    struct sysinfo info;
    sysinfo(&info);

    printf("\n=== PUPPF AGENT-CORE [ONLINE] ===\n");
    printf("[agent] PID: %d\n", getpid());
    printf("[agent] Uptime: %ld seconds\n", info.uptime);
    printf("[agent] Free RAM: %ld MB\n", info.freeram / 1024 / 1024);
    printf("[agent] Status: Initialized successfully within minimal RAM OS.\n");
    printf("===================================\n");

    return 0;
}
```

## Updated Overlay Init Script (board/puppf/overlay/init)

```sh
#!/bin/sh
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev

# Sandbox Gate Metric: Guest uptime at first agent output line (/proc/uptime)
UPTIME_AT_START=$(cat /proc/uptime | awk '{print $1}')
echo "=== PUPPF AGENT BOOT [TCG] ==="
echo "First agent action output at uptime: ${UPTIME_AT_START}s"

# Memory footprint at first action (/proc/meminfo)
echo "--- /proc/meminfo snapshot ---"
cat /proc/meminfo

# Execute the real static agent binary
if [ -x /bin/agent-core ]; then
    /bin/agent-core
else
    echo "[receipt-error] /bin/agent-core not found or not executable."
fi

echo "=== PUPPF RECEIPT COMPLETE ==="
sync
poweroff -f
```

## Buildroot Kernel Optimization Tip (If TCG Misses the Gate)

If the full x86_64_defconfig kernel bloats boot time past 5.0 seconds under QEMU TCG emulation, disabling unused drivers (like heavy filesystems, sound, and extra network card drivers) via a custom Linux kernel fragment (kernel-trim.config) will shave seconds off the decompression and boot sequence:

```
# Disable bloat drivers to speed up TCG boot
# CONFIG_SOUND is not set
# CONFIG_DRAGONS_AND_UNCIENT_BUS is not set
CONFIG_PRINTK=y
```
