# Z Review — Q 3.8 MAX, H2 Host-vs-Guest Discrimination (2026-11-10)

Seat: Z (curator). Lane: sandbox/qmax-lab-20261110 (NEW — see R1). Package
under review: RECEIPT.md + tools/boot_gate_h2.sh + .github/workflows/
qcoder-h2.yml, ferried via Mark's chat. This is the SECOND Qwen seat to answer
the same brief; the first (Qcoder) took reproducibility and is OPEN with a run
in flight. Divergence preserved — one hypothesis per lane means a new branch.

## Verdict

HYPOTHESIS ADMITTED — lane OPEN. The discriminator (QEMU exit time + serial-log
population: host failure = fast nonzero exit + 0-byte log; guest failure =
sustained run + log carrying guest sentinel strings) is falsifiable, cheap
(~3 min of runner time, no pinned-source build), and resolves a real ambiguity
for the TCG boot gate. Both simulations are synthetic on purpose — the lane
measures the failure-signature space, not the pinned source. Thresholds (5s,
0 bytes, panic string) are empirical constants, frozen in the receipt — fine
for a discriminator. STOP condition honored: two runs, one summary, done.

## Structural catch

- R1 (lane collision — the big one). The delivery targets
  sandbox/qcoder-lab-20261110, which is OCCUPIED by the first Q seat's OPEN
  reproducibility hypothesis (run in flight). Banking H2 there would break the
  one-hypothesis rule and its hardcoded checkout ref would pull the wrong
  lane's code. Moved to a new lane, sandbox/qmax-lab-20261110. The registry
  gets a second Q row (Q 3.8 MAX) rather than overwriting the Qcoder row —
  the registry-row text QC sent would have relabeled the occupied lane.

## Design read (things QC got right)

- C1. The guest-failure signature actually works as designed, via a subtlety
  worth naming: panic=1 with NO -no-reboot means the kernel panics, the guest
  resets, panics again — looping until the timeout kills QEMU at exit 124
  with a populated serial log. That loop is what produces the expected
  output; do not "fix" it with -no-reboot without redesigning the expectation
  (with -no-reboot QEMU exits ~0 in seconds and duration stops discriminating
  — log population alone would carry the signal).
- C2. Explicit -serial file: alongside -nographic: the explicit -serial wins;
  stdout is captured separately. Correct.
- C3. Test 1's serial-log size reads 0 whether or not QEMU creates the file
  before failing (stat guarded with a 0 fallback). Correct.
- C4. The final guest check short-circuits on the missing-vmlinuz condition
  before touching durations. Sound shell.

## Wiring gaps (fixed in the Z-completed commit; originals banked verbatim)

- R2 (receipt-gap — third seat in a row with this one). The receipt's actual
  result stays PENDING on the branch; RESULT-POSTED depended on a human
  pasting the log and a second round-trip. Same class as Gemini's missing
  upload and QC#1's unpublishable receipt. Fix: the runner now splices the
  H2 summary into RECEIPT.md itself and a publish step commits it (actor
  guard + bot commit carrying the suppression marker; loop-safe).
- R3 (silent green). The original script always exited 0, so a FAILED
  discrimination would render a green checkmark — the worst possible signal
  for a test whose whole job is telling failures apart. Now FAIL exits
  nonzero: red run, receipt still published, evidence still uploaded.
- R4 (skip path honesty). If the test-kernel download fails, the guest leg is
  skipped — but the summary printed "FAIL: Guest failure pattern unexpected"
  for a test that never ran. Now prints SKIPPED, distinct from FAIL.
- R5 (workflow hardening). No paths filter (any push to the lane would fire
  it), hardcoded checkout ref (now follows the push), ubuntu-latest unpinned
  (now 24.04 for determinism), no timeout-minutes (now 30), no concurrency
  group, no permissions block (contents: write added, needed only for the
  publish step).
- R6 (cosmetic, left as-authored in the bank). The receipt's LaTeX-style math
  renders literally in GitHub markdown. Meaning intact.

## Notes for the record

- Both legs run on a hosted runner with no /dev/kvm — pure TCG, which is
  exactly the environment class H2 is discriminating about. Consistent.
- The test kernel is a throwaway Ubuntu netboot kernel over HTTPS, not the
  pinned source — acceptable because the lane measures failure signatures,
  not the pinned route. No GPG lane for it; if the lane ever graduates toward
  the pinned source, the trust chain applies.
- Main-route relevance: if the signature holds, the desk queue's boot-gate
  consumers can adopt exit-time + log-population as the triage; QC's exact
  thresholds stay frozen here for evaluation.

## Status

- SEEDED -> OPEN. Registry row (new, second Q row) rides the next docs PR to
  main, after PR #22 merges (both touch the ledger; no stacking).
- Commit A (this commit): QC package verbatim + lane README + this review;
  run suppressed per seeding convention.
- Commit B (follow-up): Z-completed wiring; the push fires H2 run 1.
