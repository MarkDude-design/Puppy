# Puppf M2 experimental cycle 01 — descendant teardown boundary

Date: 2026-11-09 (Pacific). Seat: Meraki. Source: draft PR #21 head `320ed447f8b951d2215f0b7ac5967874b616750e`; experiment branch forked from that SHA. No changes to PR #21.

## Falsifiable question
Does the exact `run_console` control flow from PR #21 ensure that a child *and a surviving grandchild* are terminated when Ctrl+C interrupts the launcher? Expected by current code: only the direct child is terminated/reaped, so a grandchild that ignores SIGTERM may remain alive. This tests process-tree cleanup, **not** whether real QEMU spawns children.

## Actual execution
Host: Debian GNU/Linux 13 (trixie), Python 3, POSIX pseudo-terminal. The test harness reproduces PR #21's `run_console` function verbatim in a standalone local fixture; **it did not execute a GitHub checkout**. Parent launcher process starts a Python child, which starts a Python grandchild that ignores SIGTERM. Both print PIDs. Harness sends SIGINT to launcher, waits for its return, checks PTY terminal state and both PIDs, then kills any surviving descendants in a `finally` cleanup. One run, no retries.

Observed stdout:

```text
launcher_return 0 terminal_restored True child_state gone grandchild_state S
NEGATIVE_REPRODUCED: orphan grandchild remains alive after launcher returned
```

**FAIL** for the strong hypothetical invariant "launcher Ctrl+C terminates all descendants." **PASS** for narrower existing guarantees: launcher returned 0, direct child exited, PTY restored. The surviving grandchild was explicitly killed by the test harness. This is a real negative result, not a claim of a QEMU bug or a regression against existing stated M2 acceptance criteria.

## Confounds and scope
- A synthetic Python process tree is not QEMU. QEMU's normal process topology may have no grandchild, so this is an edge-case review, not an M2 merge blocker by itself.
- SIGINT was delivered to the launcher PID; this is not identical to a terminal foreground-process-group Ctrl+C event.
- A copied function is not an execution of the exact repository checkout; code correspondence is manually checked against `puppy-p0a/launch.py` at PR head.
- `/proc/<pid>/stat` state `S` is a live sleeping process, not a zombie.
- No QEMU guest boot was run. This host lacks `qemu-system-x86_64`; `apt-get update -qq` was attempted with a 22-second bound and timed out (exit 124, no useful package-index output). No package installation or external VM dispatch occurred.
- M1 already accepted from [build #11](https://github.com/MarkDude-design/Puppy/actions/runs/41773110103). M2 remains a draft candidate.

## Changed paths
Only this receipt and a standalone experimental fixture under `docs/workflow/runs/PUPPF-M2-DESCENDANT-001/` on the experiment branch. Original PR #21, accepted source, guest image, workflow and frozen packet untouched.

## Recommendation and next discriminating question
Do **not** change production launcher to kill arbitrary process groups without verifying terminal foreground-group behavior. Next: under a real QEMU-equipped disposable host, does QEMU remain a single direct child throughout Ctrl+C teardown, and do shell commands `uname -a`, `cat /proc/uptime`, `echo Hello_Puppf` work through PR #21's wrapper? If yes, this synthetic descendant failure may be documented as out-of-scope defense-in-depth rather than a blocker.

No paid calls, credentials, publication, merge, workflow dispatch or guest rebuild. Scheduled Chat automation usage is **not proven** to consume Work/Codex weekly allowance.
