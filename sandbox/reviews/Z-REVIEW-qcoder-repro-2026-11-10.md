# Z Review — Qcoder Reproducibility Package (2026-11-10)

Seat: Z (curator). Lane: sandbox/qcoder-lab-20261110. Package under review: QC's
RECEIPT.md hypothesis + test-reproducibility.sh + qcoder-repro-test.yml, ferried
via Mark's chat (QC hit the Qwen coding-tool cap; the design was chat-only).

## Verdict

HYPOTHESIS ADMITTED — lane OPEN. Candidate (b) from the orientation append:
reproducibility of the pinned P0a route (Buildroot 2026.08, Linux 6.18.7,
BusyBox 1.38.0). Discriminates both ways (divergence predicted, identity
equally informative), one hypothesis + one test, hard STOP, negative results
welcome. jejejeje — QC's own result template labels its predicted outcome
"FAIL"; divergence IS the hypothesis, so the wiring reports CONFIRMED/REFUTED
instead (R6).

## Read against the real contract (driver.py, dispatch YAML, puppy-p0a README)

Confirmed correct:

- C1. Artifact paths: the driver copies bzImage and rootfs.cpio.gz into
  PUPPF_EVIDENCE_DIR/artifacts/ — the script's comparison paths match.
- C2. Fresh-evidence refusal: the driver refuses an existing receipt.json or
  run-1 dir; per-run mktemp -d evidence dirs satisfy it.
- C3. ubuntu-24.04 matches the main dispatch — required for the "same runner
  environment as the pinned route" claim.
- C4. Loop guards: skip-marker seeding ask plus the github-actions[bot] actor
  guard match lane precedent.

Wiring gaps (fixed in the Z-completed follow-up commit; QC originals banked
verbatim in this commit):

- R1 (BLOCKED-class). PUPPF_EXPECTED_PACKET_SHA256 is never set. driver.py
  raises Blocked unless the env matches the pinned dispatch digest. Both runs
  would have died at the packet gate before any build started.
- R2 (BLOCKED-class). No host-deps install step. The main dispatch apt-installs
  ~22 packages (qemu, gpg, bison, flex, perl, patch, xz, ...) before run-ci.sh;
  the driver's host_check blocks on any missing tool. The dispatch list was
  copied verbatim.
- R3 (BLOCKED-class). Disk: the driver never cleans its scratch tree. Two
  sequential full builds share one runner disk; run 2's 10 GiB free-space floor
  would fail with run 1's build tree still present. Fix: after run 1's evidence
  is complete, remove its recorded scratch_directory — build trees are not
  evidence per the README — guarded to RUNNER_TEMP/puppf-p0a-* paths only.
- R4 (receipt-gap; same class as Gemini's missing upload step). The script
  edits RECEIPT.md on the runner but nothing commits it back to the branch —
  the RESULT-POSTED transition would evaporate with the runner VM. Fix:
  receipt-publish step (always(), bot-authored commit carrying the skip
  marker; actor guard already present).
- R5 (negative-result gap). Original wiring wrote RECEIPT.md only on the
  success path; a BLOCKED run would leave PENDING EXECUTION forever, against
  this lane's own "negative results are welcome and preserved" doctrine.
  Failure paths now record the actual outcome on-branch.
- R6 (wording). Divergent digests = the stated hypothesis CONFIRMED, not a
  test malfunction. Result wording now CONFIRMED / REFUTED.

## Notes for the record

- run-ci.sh is the full route: build PLUS two TCG boots per invocation. The
  boots ride along (~8-12 min per run), do not touch the build digests, and
  honor the lane's "use the real pinned pipeline" framing. Two sequential full
  routes ≈ 2-3.5 h worst case; explicit job timeout set at 330 minutes.
- Each run re-downloads sources (fresh scratch and download dir per driver
  invocation), consistent with the RECEIPT's "complete wipe between runs"
  clause.
- Mechanism note: the main route config does not pin BR2_REPRODUCIBLE.
  Divergence is plausible. If CONFIRMED, the natural follow-up lane is "does
  BR2_REPRODUCIBLE=y close the gap" — a future lane, not folded here
  (one-hypothesis rule).
- QC's ferry instruction to "create the branch" was stale — the lane was
  already seeded. No action needed.

## Status

- SEEDED -> OPEN. Registry row update rides the next docs PR (main is
  PR-only under the main-protected ruleset).
- Commit A (this commit): QC package verbatim + this review; run suppressed
  per QC's own seeding request.
- Commit B (follow-up): Z-completed wiring; the push itself fires run 1.
