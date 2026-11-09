# Puppf M2 Cycle 02 — foreground-terminal Ctrl+C (synthetic)

Date: 2026-11-09 (Pacific). Meraki. **Independent from Cycle 01** (`experiment/puppf-m2-descendant-cleanup-20261109`). Source: draft PR #21 head `320ed447f8b951d2215f0b7ac5967874b616750e`; this experimental branch forked from that immutable SHA. PR #21 unchanged.

## Falsifiable question

When Ctrl+C originates from a *foreground pseudo-terminal* (rather than Cycle 01's direct `kill(launcher, SIGINT)`), can the launcher handle SIGINT and terminate a direct child that **ignores SIGINT**, without relying on the child to exit on its own?

Expected: terminal emits SIGINT to the foreground process group; launcher catches KeyboardInterrupt, sends SIGTERM to its direct child, and restores terminal state. This does **not** test grandchildren or actual QEMU.

## Actual test

Host: Debian GNU/Linux 13 container, Python 3, POSIX `pty.fork`. A standalone Python fixture copied the relevant `run_console` control-flow structure from PR #21, **not** an executed GitHub checkout. `pty.fork()` made the launcher a session/foreground-group leader; launcher `Popen` created a direct child in that same group. Child installed `SIG_IGN` for SIGINT. Harness wrote ASCII ETX (`0x03`) to the PTY master only after both processes printed PID/PGID. Thus the test is distinct from Cycle 01's PID-targeted signal. It read launcher output and forcibly cleaned the PTY process group afterward. Two executions, second after adding a short read-drain delay, same substantive outcome.

Observed excerpt:

```
signal_sent True exit None
LAUNCHER 469 469 479
CHILD 479 469
^CINTERRUPTED
CLEAN -15
```

**PASS (narrow):** PTY-originated Ctrl+C reached launcher; SIGINT-ignoring direct child was terminated with SIGTERM (reported `-15`); launcher executed the cleanup path. **NOT_PROVEN:** launcher exit status (harness sampled `waitpid(WNOHANG)` before it had reaped, hence `None`); terminal-attribute equivalence was not independently measured; process-grandchild handling was not tested; exact PR checkout was not executed; no QEMU boot occurred. The printed CLEAN line proves cleanup code ran, not that terminal state was restored to an independently verified byte-for-byte baseline.

## Environment and blocker

`command -v qemu-system-x86_64` returned no executable. Bounded `timeout 24s apt-get update -qq` returned **124** with no useful index output; host could not obtain package metadata. No package install, hosted dispatch or new guest boot. Accepted M1 build #11 remains valid; no rebuild attempted.

## Changed paths and authority

Only this experiment receipt at `docs/workflow/runs/PUPPF-M2-FOREGROUND-SIGINT-002/RECEIPT.md` on `experiment/puppf-m2-foreground-sigint-20261109`. Local standalone fixture `foreground_sigint.py` was executed and syntax-checked; it is **not** committed in this receipt-only cycle. PR #21, frozen P0a packet, guest image, workflows and main untouched. No spending, publication, credentials, model calls or workflow trigger.

## Next discriminating question

On an authorized QEMU-equipped disposable host, does **the exact PR #21 launcher** accept a real PTY Ctrl+C and return control to the terminal with verified terminal attributes, while the accepted image runs `uname -a`, `cat /proc/uptime`, and `echo Hello_Puppf`? Do not count this synthetic process test as a guest boot or M2 acceptance.

Scheduled Chat automation usage is **not proven** to draw down Work/Codex weekly allowance.
