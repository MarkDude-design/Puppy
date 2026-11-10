# M2 isolated-group teardown — synthetic follow-on (2026-11-10)

**Seat:** Meraki, native ChatGPT (shared GitHub connector). **Status:** synthetic fixture SUPPORTED with a countercase; integration NOT_RUN. Not owner acceptance.

## Source and scope
- Reviewed draft [PR #21](https://github.com/MarkDude-design/Puppy/pull/21) `puppy-p0a/launch.py` (`run_console()`): ordinary `subprocess.Popen(argv)`, direct `terminate/kill`, terminal settings restored in `finally`.
- Earlier [negative fixture](https://github.com/MarkDude-design/Puppy/blob/experiment/meraki-m2-descendant-teardown-20261109/docs/workflow/experiments/m2-descendant-teardown-20261109/RECEIPT.md) showed an orphaned synthetic descendant on targeted SIGINT. The accepted M1 two-boot evidence and P0a pins are unchanged.
- New question: can a **separate child session/process group** permit bounded TERM→KILL cleanup of a synthetic child + long-lived descendant, without ever signaling the host's group, while restoring termios?
- Candidate outline (NOT a merged patch): start a synthetic child with `start_new_session=True`; after interrupt or ordinary direct-child exit, validate `child.pid != os.getpgrp()`, signal `os.killpg(child.pid, SIGTERM)`, wait for the direct child, then signal `os.killpg(child.pid, SIGKILL)` after a short grace period; always restore saved terminal settings. Only the observed candidate is being evaluated; this is **not** blanket advice to send signals to arbitrary PIDs/groups.

## Actual Linux execution — test 1
**Host:** Linux, Python 3.13.5, PTY; synthetic Python child and TERM-ignoring descendant. Executed local `pty_group_probe.py` (SHA256 `4bb532dd2ec4ea2f185e3686a506d607f97bd3739443de4c674f12dc2a1271f9`). It records `results.json` (SHA256 `01cf7bcaf06577ca6515afd6a9102bf1a1d5147697df952bd37989f2c384a786`).

Five cases and seven asserted checks **passed**:
| Case | PID-only control | Isolated-group candidate |
|---|---|---|
| Targeted wrapper SIGINT, child lingers | descendant **S (live)** | descendant **Z (not live)** |
| Direct child exits while descendant lingers | descendant **S (live)** | descendant **Z (not live)** |
| Repeated targeted SIGINT | not rerun as control | descendant **absent** |
| Parent wrapper returned zero | yes | yes |
| Synthetic PTY settings restored | yes | yes |

The fixture killed its own surviving control descendants in cleanup. A zombie state is not a running process, but is also **not** proof of prompt reaping by init; containers may leave orphan zombies until PID 1 reaps them.

## Actual Linux execution — test 2 / COUNTERCASE
Executed a distinct **controlling-PTY** harness using `pty.fork()` and real `^C` injected through the master FD (local `interactive_tty_probe.py`, SHA256 `a1540509906b5d4a29afb620ef7cc570af6451532a81f16dcf551f1c4f0af31f`). Child successfully read the interactive line `hello_pty` in group-isolated and PID-only modes; Ctrl+C reached the wrapper, restoration marker appeared, wrapper exited 0; group-isolated descendants were not live after cleanup.

**Falsifying / limiting observation:** The PID-only control's descendant was **not live** in the controlling-PTY case, unlike targeted-signal fixture 1. This held even in an attempted SIGINT/SIGTERM-resistant descendant case. The harness is not instrumented to distinguish terminal foreground-group signal effects from session hangup or process-exit effects; do **not** interpret that as proof PID-only cleanup always succeeds, or as evidence that the isolated-group candidate is necessary on the normal interactive path. The second harness's initial predicted `pid_resistant_descendant_leaks` assertion was **false**; preserved, not silently converted to PASS. Earlier probe had a parent wait-race and premature-signal readiness condition; those were fixed before the final recorded case set. Final raw `interactive_results.json` SHA256 `4c9aa16d948e573e268f1363ce5c832fefc35eaeeb7eff7c29e9ad32ce4d1349`.

## Boundaries / next discriminating experiment
- **No QEMU binary** on this host, no guest boot, and no accepted ZIP touched. Synthetic Python behavior cannot certify QEMU `-chardev stdio` behavior, terminal job control on real host shells, macOS support, or Windows/WSL.
- `start_new_session=True` may change controlling-terminal and signal semantics; a real QEMU interactive test against accepted build #11 is the required next gate **before** proposing a launcher patch.
- No PR #21 changes, no owner merge, CI dispatch, release, external API spend, credential use, or private-data publication. Baseline M1 ACCEPTED, M2 demo STILL PENDING.
- Reproducible local artifacts were executed and separately preserved with SHA256s; **this receipt contains summarized observations rather than a claim that committed GitHub code was rerun.**
- Hypothesis verdict: **SUPPORTED only for targeted-signal synthetic teardown; not established as a user-facing QEMU defect or universal fix.**
