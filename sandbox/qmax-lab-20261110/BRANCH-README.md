# sandbox/qmax-lab-20261110 — Q 3.8 MAX lane

Experiment-garden lane under docs/EXPERIMENT-LEDGER.md (main). Charter: one
hypothesis + one discriminating test per lane; RECEIPT.md at lane root;
negative results welcome and preserved; merges are owner-clicked; garden work
never lowers the frozen gates.

- Seat: Q 3.8 MAX (second Qwen seat; the first seat "Qcoder (Qwen)" holds
  sandbox/qcoder-lab-20261110 with the OPEN reproducibility hypothesis — two
  seats answered the same brief with different candidates; divergence
  preserved per the yardstick).
- Hypothesis (H2, desk-queue candidate): runner-environment failure can be
  strictly distinguished from guest-implementation failure by QEMU exit time
  + serial-log population (host failure = fast nonzero exit + 0-byte serial
  log; guest failure = sustained run + serial log carrying guest sentinel
  strings).
- Receipt: sandbox/qmax-lab-20261110/RECEIPT.md
- Z review: sandbox/reviews/Z-REVIEW-qmax-h2-2026-11-10.md
- Status: SEEDED -> OPEN on Z wiring (2026-11-10); run 1 armed.
