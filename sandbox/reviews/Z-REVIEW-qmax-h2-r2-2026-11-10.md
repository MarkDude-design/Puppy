# Z Review — Q 3.8 MAX, H2 Round 2 Boundary Probe (2026-11-10)

Seat: Z (curator). Lane: sandbox/qmax-lab-20261110. Package under review:
round-2 RECEIPT + tools/boundary_probe.sh + .github/workflows/
qmax-h2-boundary.yml. Banked verbatim in this commit.

## Verdict

ROUND 2 ADMITTED — WIRING HELD for round 1's baseline. Round 1's receipt is
still PENDING on the lane root (run fired 20:06Z; nothing on the bus at bank
time). One open test at a time per lane: round 2 arms the moment round 1
RESULT-POSTs (Gemini-lane precedent). The round-2 receipt is staged at
RECEIPT-round-2.md; at arm time it is promoted to the lane root and round 1's
spliced receipt archives as RECEIPT-round-1.md.

## What the seat improved on — visibly, without being asked twice

- A1: actor guard, permissions contents:write, no hardcoded checkout ref,
  self-publishing receipt with the suppression marker, red-on-FAIL, honest
  SKIPPED leg — the round-1 review carried over.
- A2: chmod-before-run remembered (the contents-API mode-644 landmine).
- A3: the -no-reboot override is explicit and reasoned — round 1's timeout
  loop was load-bearing THERE; the fast-exit boundary is the point HERE.
- A4: the hypothesis genuinely sharpened: the discriminator is the kernel's
  early boot stub output, not a time constant. This survives the case where
  both failure modes exit fast — the exact blind spot of round 1's 5s rule.

## Wiring gaps (fixed in the Z-completed arm-time commit; verbatim banked here)

- W1 (hard — would-be red run with a lost receipt). The splice step seds
  RECEIPT.md at repo ROOT; the lane receipt lives at
  sandbox/qmax-lab-20261110/RECEIPT.md. sed and git add would both fail.
- W2 (evidence vanishes). No Upload Evidence step — the raw serial logs,
  including the load-bearing "Decompressing Linux" line, die with the VM.
  Upload re-added (always(), ./evidence/, 3-day retention).
- W3 (regressions vs the wired round-1 file). ubuntu-latest unpinned again,
  no paths filter (any lane push fires a probe), no timeout-minutes, no
  concurrency, no pull --rebase before the publish push. All re-applied at
  arm time. Note for round 3: the Z-wired round-1 workflow is public on this
  branch — read it before authoring; it already carries every fix.
- W4 (prediction duel — deliberately NOT fixed). The receipt predicts guest
  "Exit != 0 (typically 1)" and the FAIL predicate fires when GUEST_EXIT is
  0. Z's counter-prediction: with panic=1 + -no-reboot, the guest's
  post-panic reset makes QEMU exit 0 (clean quit on -no-reboot), so the
  guest leg may render red even when the boundary discrimination succeeds.
  Left as-authored ON PURPOSE: the runner arbitrates between the seat's
  prediction and the curator's. If the result is red with a populated log
  and T_guest > T_host, the finding is "the exit-code clause mispredicts;
  time + decompression-output discriminate correctly" — that IS the round-2
  result, and round 3 refines the predicate. Neither prediction is verified
  until a receipt says so.

## Registry

One qmax row stands; the round label updates in the next docs PR (after
PR #22 merges — still pending the owner click). The seat's proposed
additional registry row is declined: the lane is the row; rounds are its
receipt lineage (RECEIPT-round-1.md, RECEIPT-round-2.md, ...).

## Arm-time plan (recorded so the next session can execute it cold)

1. Confirm round 1 RESULT-POSTED on the lane root (bot splice commit).
2. Commit (armed, no suppression marker): archive RECEIPT.md ->
   RECEIPT-round-1.md; promote RECEIPT-round-2.md -> RECEIPT.md; install the
   Z-completed qmax-h2-boundary.yml (W1 path fix, W2 upload, W3 hardening,
   W4 logic untouched); append BRANCH-README status line. The lane-root
   receipt change fires the probe via the paths filter.
