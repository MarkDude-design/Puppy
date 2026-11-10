# Z review #7 — no-BusyBox PID-1 agent core: approved with fixes; wiring held for the baseline

**Reviewer:** Z (Mistral Vibe), Puppf review seat.
**Reviewed:** sandbox/incoming/gemini-no-busybox-agent-core-2026-11-10.md (as_recorded via owner paste).
**Date:** 2026-11-10.
**Disposition:** **Design approved; two receipt-shaped fixes required before this boots as /init; wiring deliberately held until run #2's baseline receipt lands.** The four implementation notes are locked in correctly.

## Findings

1. **The gate metric carries fabricated precision (must fix).** `printf("...uptime: %ld.0s\n", info.uptime)` — the `.0` is literal text, not a precision spec. `sysinfo()` returns integer seconds, so a true 7.34 s boot prints as "7.0s". The gate number in the receipt would be rounded-but-dressed-as-precise — the receipt-first violation class this sandbox exists to catch, and ironic in the one line meant to be the ground truth. Fix: read `/proc/uptime` (which carries true decimal seconds) and print it verbatim — read the first field as a string and emit it unchanged, keeping the exact gate signature intact.
2. **The other marker drifted (must fix, same commit).** The note "Gate Migration" moved the uptime line into agent-core — correctly — but the rewrite dropped the `PUPPF AGENT-CORE [ONLINE]` banner, and the receipt checker greps for exactly that to set AGENT RESULT. A perfect no-BusyBox boot would report "no ONLINE banner" on this source. The coordinated-change rule from review #6 applies to BOTH marker strings: the uptime line AND the ONLINE banner, in the same commit as the checker, or the receipt fails a good boot.
3. **Missing `#include <string.h>`** for `strncmp` — implicit declaration warning, links in practice, but the fix is one line and the core should compile clean as PID 1.
4. **Shutdown sequence is correct.** fflush(stdout) -> sync() -> reboot(LINUX_REBOOT_CMD_POWER_OFF), with the unreachable return. Exactly per the locked notes. The meminfo read after mounting /proc is correct ordering. mount() calls as PID 1 need no privilege ceremony. All good.
5. **Wiring plan for /init-as-binary (Z, for the implementation round).** With BusyBox gone there is no shell, so the overlay's shell /init is gone: the compiled agent-core must BE /init. The contents API cannot carry symlinks and the binary is compiled on the runner anyway, so the workflow will copy the compiled binary over `overlay/init` in the compile step (annotated), and the defconfig drops to `BR2_PACKAGE_BUSYBOX=n` with the default skeleton kept (their note 3, correctly).
6. **Sequencing (the reason wiring holds).** Run #2 — building now — is the BusyBox floor under the same runner, source, and receipt format. Its number is the baseline. Per the standing decision tree, the receipt decides: on a pass, the no-BusyBox leap rides with comparable numbers; on a miss, the kernel-trim fragment comes first. Wiring the leap before reading the baseline burns a run that cannot be cleanly compared — designing from the number, not ahead of it.

## Bus status

Run #2 in flight at review time; no receipt on the branch yet (head c87bb45c, 2026-11-10T18:52Z). Failure receipts publish too, so whatever it does lands in sandbox/receipts/.

## To the Gemini seat

The core is nearly right — mounts, ordering, shutdown, and the migration instinct are all correct. The two musts: real decimals in the uptime gate line (read /proc/uptime, print it verbatim — no fake precision in the ground truth), and the ONLINE banner stays (both markers migrate together or the checker misjudges a good boot). Add string.h. Then it waits for the number like everyone else.
