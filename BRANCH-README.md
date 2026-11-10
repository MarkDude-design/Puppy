# sandbox/qcoder-lab-20261110 - Qcoder experiment sandbox

Owner-pointed sandbox for Qcoder (Qwen). Free rein on THIS branch - anything you want: proposals, counterexamples, runnable tests, demos. The other rules:

1. Read docs/EXPERIMENT-LEDGER.md (on main) - it is the charter and registry.
2. One hypothesis at a time; build one discriminating test for it; know your limits.
3. Keep a RECEIPT.md at this branch root: question, test, expected output, STOP condition, actual result. Negative results are welcome and preserved.
4. Do NOT merge to main (you cannot; merging is owner-clicked). Do not copy credentials, private transcripts, or internal ledgers into this repo.
5. Append your row to the registry table in docs/EXPERIMENT-LEDGER.md on main in the same commit where you begin work.

Seeded by Z (Vibe/Mistral seat), 2026-11-10, per owner directive.

## Orientation (curator append, 2026-11-10)

### Where the project is

- Main route: Buildroot 2026.08 / Linux 6.18.7 / BusyBox 1.38.0, pinned trust (GPG VALIDSIG, byte-pinned key), two-boot QEMU acceptance. P0a spike PASS, disposable by design; rewrite #1 ("fix what the spike taught") is the active lane. M1 accepted; M2 PR #21 draft awaits the real host demo.
- Governance and seat roles: docs/workflow/README.md. Roadmap: docs/ROADMAP.md.
- Garden territory complements, never supersedes; the frozen trust / two-boot gates are never lowered by garden activity.

### Lanes already taken (avoid collisions; divergence stays preserved)

- Gemini (sandbox/gemini-lab-20261110): debootstrap->squashfs->ISO sketch (tried, failed at the kernel step - receipt banked); one-static-binary floor (initramfs-only, static agent, TCG boot gate uptime_s < 5 s on GitHub runners) - run #2 in flight; no-BusyBox PID-1 core - banked with two review fixes, waiting on the baseline number.
- Meraki: M2 launcher experiment lanes (see the registry).

### Mechanics learned on the Gemini lane (read before you build)

- GitHub-hosted runners have NO /dev/kvm: QEMU runs pure TCG emulation. Plan gates as TCG numbers; hardware-realistic targets get logged as aspirational alongside.
- Pushes to this branch are cheap: workflows carried from main are manual-dispatch plus tiny fixtures. If you ADD a push-triggered workflow, guard the receipt-push loop ([skip ci] in receipt commit messages; skip the job when the actor is github-actions[bot]) or the branch will burn minutes in a circle.
- Receipt-first, run-what-you-show: the receipt records what actually ran, not what was planned. Plausible-but-never-executed YAML has already been caught twice on the Gemini lane; the runner is the reviewer of last resort.
- Sources: prefer release tarballs over git clones (git.buildroot.net cost one run, 32 s, exit 128); buildroot.org is the source family the main route pins.

### Candidate hypothesis sources (pointers, not prescriptions)

- The agent desk queue (docs/agent-desk/queue.json) holds bounded read-only questions; H2 is literally a discriminating-test ask: identify one falsifiable check that distinguishes GitHub-runner/Buildroot environment failure from actual guest/serial implementation failure.
- Reproducibility: same pinned source, two clean builds - identical artifact digests or not? Both outcomes are informative, which satisfies the yardstick's discriminating-test bar by construction.
- Anything not on the taken list. The yardstick's one-hypothesis rule is the only constraint.

Status lifecycle: SEEDED -> OPEN -> RESULT-POSTED -> EVALUATED / PARKED / MERGED (owner click only). Update the registry row by appending.
