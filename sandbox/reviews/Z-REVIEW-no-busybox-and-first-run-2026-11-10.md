# Z review #6 — no-BusyBox design (round 5) + first run failure receipt + source fix

**Reviewer:** Z (Mistral Vibe), Puppf review seat.
**Reviewed:** sandbox/incoming/gemini-no-busybox-design-2026-11-10.md and sandbox/incoming/mark-actions-paste-first-run-failure-2026-11-10.md (both as_recorded via owner paste).
**Date:** 2026-11-10.
**Disposition:** **First run receipt banked (BUILD_FAILED, 32s); source fixed; failure receipts now publish; no-BusyBox design approved-with-notes for its round.**

## The first run receipt

1. **What happened.** Run 1 died at the Buildroot acquisition step: `git.buildroot.net` is not a served git repository ("repository not found", exit 128). 32 seconds from trigger to failure.
2. **Z self-receipt (on the record).** The bad URL arrived in Gemini's round-2 workflow and survived my reviews #3-#5 unflagged. The reviews verified logic and gates; none of the seats verified that the source address exists. The first thing a real runner checks is whether the source exists. This miss is why the runner is the reviewer of last resort — and why the failure receipt now lands on the bus instead of evaporating on the run page.
3. **The fix.** The workflow now pulls the **Buildroot 2026.08 release tarball from buildroot.org** — the same source family the main route pins and GPG-verifies. Sandbox grade per charter: the sha256 of the tarball is recorded in every receipt (no pinned-digest gate in the sandbox); if sandbox receipts start feeding main-route decisions, the pinned-digest discipline comes with them. Side benefit: ~6 MB tarball instead of a ~200 MB git clone. The official git home is `gitlab.com/buildroot.org/buildroot` if a git mirror is ever wanted; `git.buildroot.net` is not one.
4. **Failure receipts now publish (gap closed).** Publish-only-on-success was named in review #5 and bit us one run later. Every run — build failure included — now commits a `sandbox/receipts/run-<id>/summary.md` with outcome, gate, agent result, footprint when present, source sha256, and on build failure the tail of the build log. Build output is teed to a log so a failed compile is diagnosable from the branch.

## The no-BusyBox design (round 5), notes for its round

Approved in direction — kernel + one binary is the floor the charter pointed at. Notes so the implementation round does not stumble:

1. **reboot() is load-bearing at PID 1.** If the agent returns from main() without calling `reboot(LINUX_REBOOT_CMD_POWER_OFF)`, the kernel panics ("Attempted to kill init"). Their design has the syscall; this documents why it must never be treated as optional cleanup.
2. **fflush(stdout) before the reboot syscall.** `reboot()` skips exit handlers — any stdio still in the buffer dies with the machine. On a tty stdout is line-buffered so trailing newlines mostly save the receipt, but "mostly" is not a receipt discipline: set `setvbuf(stdout, NULL, _IONBF, 0)` at the top or `fflush(NULL)` before the syscall.
3. **mount() does not mkdir.** The Buildroot default skeleton provides /proc, /sys, /dev today, so the first version rides for free. The moment the rootfs goes skeleton-free, agent-core must mkdir the mount points before mounting.
4. **No privilege ceremony needed:** PID 1 holds CAP_SYS_BOOT; reboot() and mount() work from the bare binary.
5. **Gate marker migration is a coordinated change.** The workflow greps the shell init's "First agent action output at uptime" line. When BusyBox goes, that line goes with it — agent-core must print the marker itself (or keep the exact string), and the workflow change must land in the same commit, or GATE RESULT fails by marker-absence on a perfectly good boot.

## Transport-layer receipt

The round-5 paste arrived with a corrupted byte (`#镇include` for `#include`) — kept [sic] in the incoming file. Harmless here; banked as evidence that chat transport can corrupt bytes, which is why the bus keeps verbatim copies with glitches marked and why the runner remains the reviewer of last resort.
