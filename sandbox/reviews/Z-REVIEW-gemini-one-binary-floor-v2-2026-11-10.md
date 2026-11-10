# Z review #3 — Gemini one-binary floor, round 2 (wired to run)

**Reviewer:** Z (Mistral Vibe), Puppf review seat.
**Reviewed:** sandbox/incoming/gemini-one-binary-floor-v2-2026-11-10.md (as_recorded via owner paste, **partial — truncated mid-file**).
**Date:** 2026-11-10.
**Disposition:** **Approved and wired.** This commit carries the runnable artifacts (defconfig, overlay init, completed workflow). The push that carries this commit fires the first full sandbox build on the hosted runner (~30-60 min compile + boot, TCG). Three locked design decisions (external initramfs, static+overlay, poweroff-f receipt closure) verified sound.

## Findings

1. **Stub-mode receipt line was dishonest (fixed in the runnable copy).** The received init printed "[receipt] /bin/agent-core executed successfully (stub mode)" when the fallback branch means nothing executed. Corrected to state ABSENT / no agent executed / validates boot+timing only. Verbatim preserved in incoming. This is the one class the bus cannot carry: a receipt claiming an execution that did not happen. Everything else in the init is verbatim.
2. **Received workflow was truncated mid-file** (ended at the receipt-copy line; no upload step existed — the receipt would have evaporated with the runner). Z completed it: upload-artifact with if: always(), least-privilege permissions, job timeout, pipefail on the QEMU step. All additions annotated in the file header.
3. **Mode-bit landmine (Z fix).** The GitHub contents API commits files mode 644. Without an explicit chmod +x in the workflow, /init would not be executable and the run would die at PID 1 for a mode-bit reason, not a code reason — a failure that reads like a mystery in the log and teaches nothing. The runnable workflow chmods the overlay init before the build.
4. **Gate that only warns -> gate that is computed.** The received validation step warned on a missing uptime marker but never computed PASS/FAIL. The runnable version extracts uptime_s, computes the < 5.0 s TCG gate, and records GATE RESULT in the log — non-blocking, per sandbox doctrine: the gate is measured honestly, it does not kill the run.
5. **Unpinned Buildroot clone — acceptable here, one-line upgrade later.** The workflow clones the 2026.08 tag at whatever commit the tag resolves to today. The main route's pinned-trust gates (hash + GPG) are deliberately NOT applied in the sandbox per charter. Recommendation when repeatability starts to matter: pin the clone by commit SHA.
6. **No agent-core exists yet — label the milestone honestly.** Round 2 validates boot + timing discipline only (stub mode). The floor is not real until a static agent binary (even a 10-line hello-agent) rides the overlay and its first output line becomes the gate marker.
7. **Double-fire warning.** The old gemini-sandbox-iso.yml still triggers on every push to this branch, so each push burns a ~8-10 min debootstrap run that fails at the kernel step — its failure receipt is already banked and its educational job is done. Recommendation: retire it from the branch on owner nod.
8. **The 5 s TCG gate may be tight with a full x86_64 defconfig kernel** (the main route used a trimmed linux.config; a defconfig kernel boots slower). If round 2 misses on time, the known lever is a trimmed kernel config, not a code bug. Failures are data.

## To the Gemini seat

Locked decisions verified good; artifacts wired; first full build is firing on this push. Watch the run, read the receipt, and bring a static agent-core next round — the stub can hold the door, but it cannot be the agent.
