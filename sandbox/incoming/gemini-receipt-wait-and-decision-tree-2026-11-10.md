# Received — round 3 follow-up / decision tree — preserved verbatim

- **Received:** 2026-11-10, pasted by MarkDude (owner) from the Gemini chat seat.
- **Provenance:** `as_recorded` — copied through chat transport.
- **Z review:** see ../reviews/Z-REVIEW-round3-followup-2026-11-10.md
- **Correction on record:** the run log does NOT land in the repository as received — it lands in Actions artifacts. Z wired receipt publication to the sandbox branch in this commit (annotated), making the statement below true going forward.

---

Z's catch on the compile step keeps the runner honest—relying on host `gcc -static` before the overlay copy ensures `/bin/agent-core` is genuinely ready to execute when PID 1 reaches it, rather than failing silently into the stub branch.

Leaving the kernel defconfig untouched until we see the actual TCG boot number is the right call; kconfig's silent drop of unknown symbols means our custom fragment wouldn't have done anything anyway.

Now we wait for the run log to land in the sandbox repository. When the metrics hit, we'll design strictly around what the numbers say:

* **If the uptime gate passes (`uptime_s < 5.0`):** We pivot from boot timing to footprint optimization (stripping unnecessary BusyBox applets and shrinking the raw `rootfs.cpio.gz` size).
* **If the uptime gate misses:** We introduce the minimal kernel config fragment (`kernel-trim.config`) to strip out high-overhead subsystems and bring TCG boot well under the 5-second threshold.
