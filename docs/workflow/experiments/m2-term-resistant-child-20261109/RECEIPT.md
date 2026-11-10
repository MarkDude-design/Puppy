# Puppf M2 — TERM-resistant direct-child Ctrl+C escalation fixture
**Meraki independent cycle:** 2026-11-09, ~19:33 PT. **Result: synthetic PASS**, not a QEMU guest boot.

## Prior-cycle check
Read issue #15 comments through #6755279112 and unchanged draft PR #21 `puppy-p0a/launch.py`. Prior fixtures covered repeated Ctrl+C, SIGINT with surviving grandchild, parent-only SIGTERM with surviving direct child, and abnormal child exit status 7. This cycle isolates **a direct child that ignores SIGTERM**, requiring the wrapper's SIGKILL escalation after Ctrl+C.

## Falsifiable hypothesis
Under an interactive Linux pseudo-terminal, after SIGINT to the wrapper parent, a child that explicitly ignores SIGTERM and disables ECHO will be killed by the wrapper's three-second escalation; the wrapper restores the original terminal settings and returns zero. Fails if child survives, terminal differs, wrapper hangs, or nonzero exit.

## Actual executed test
Python 3.13.5; Linux container; stdlib `pty.fork`, `os.kill`, `termios`, `subprocess`. A temporary Python wrapper **replicated** PR #21 `run_console`'s `Popen`, `wait`, `KeyboardInterrupt`, `terminate`, `wait(timeout=3)`, `kill`, `wait(timeout=1)`, and terminal-restore structure. A temporary child installed `SIGTERM: SIG_IGN`, disabled ECHO, printed `READY`, then slept. Harness waited for `READY`, sent SIGINT to wrapper PID, collected PTY output, reaped wrapper, and checked child PID with `kill(pid,0)`. The two temporary scripts were generated under `tempfile.TemporaryDirectory`, not repository files.

Exact second-run output (3-second escalation):
```
wrapper_exit 0 child_pid 474 child_survived False
output 'CHILD 474\r\nREADY\r\nINTERRUPTED\r\nRESTORED True\r\n'
```
Harness asserted wrapper exit 0, no surviving child, and terminal restored; process exit **0**. An initial 0.5-second timeout run also passed; **the reported result uses the three-second timeout of PR #21**.

## Limits / NOT_RUN
This is a **synthetic replica**, not import/execution of actual PR #21 `run_console`, and not QEMU. It supports the narrow SIGTERM-resistant **direct-child** escalation path, not process-tree cleanup or actual guest terminal behavior. `qemu-system-x86_64`, Docker and Podman absent in current container; accepted ZIP absent from `/mnt/data`; `apt-cache policy qemu-system-x86` returned no candidate. **REAL QEMU BOOT BLOCKED**, not PASS. The separate existing review-only hosted plan already covers the manual QEMU pilot; no duplicate workflow or automatic trigger. ACPI/Rewrite #1 not investigated in this cycle because a distinct launcher regression was tested.

## Changes and gates
New branch `experiment/meraki-m2-term-resistant-child-20261109`; changed files: **this receipt only**. PR #21 untouched and draft; accepted M1 build #11 run 41773110103 not rebuilt. Original retained artifact `libfile_4d168bd731d88191b75d5c570f1dcad8`, expected SHA256 `dd333e9d6fd6a7e02e757488c872c3eb8edabe1b334b5345fdf2fd96426917b2`, not available for a fresh hash check here. No spending, model calls, secrets, publication, merge, or workflow dispatch. Scheduled Chat task usage is **not proven** to draw down Work/Codex weekly allowance.
