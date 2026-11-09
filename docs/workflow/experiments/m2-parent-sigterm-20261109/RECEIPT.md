# Puppf M2: parent-only SIGTERM teardown negative fixture

**Date:** 2026-11-09 PT. **Seat:** Meraki (GPT-6 native session). **Status:** SYNTHETIC NEGATIVE CASE REPRODUCED; real QEMU boot BLOCKED. **Source under review:** draft [PR #21](https://github.com/MarkDude-design/Puppy/pull/21), `work/puppf-m2-launcher-20261104`, `puppy-p0a/launch.py`. **Experiment:** `experiment/meraki-m2-parent-sigterm-20261109` (separate branch; original PR not edited).

## Check against prior work

- M1 is **accepted**, build #11 [run 41773110103](https://github.com/MarkDude-design/Puppy/actions/runs/41773110103), accepted ZIP SHA-256 `dd333e9d6fd6a7e02e757488c872c3eb8edabe1b334b5345fdf2fd96426917b2`; no rebuild or duplicate hosted build.
- PR #21's Astra-reviewed repeated Ctrl+C direct-child cleanup remains the earlier positive result. [Meraki's preceding cycle](https://github.com/MarkDude-design/Puppy/issues/15#issuecomment-6748111629) tested **SIGINT with a grandchild**. **This cycle is distinct:** the wrapper itself receives **SIGTERM**, while its **direct** synthetic child receives no signal. The signal and child topology are different.
- Source inspection: `run_console` handles `KeyboardInterrupt`, then uses a `finally` to terminate/reap the direct Popen child. It has **no explicit SIGTERM handler**. On default SIGTERM the Python process is terminated before Python `finally` executes.

## One falsifiable question

**Hypothesis:** If an external supervisor sends SIGTERM to only the Puppf launcher parent (not its whole process group), the wrapper terminates without running its Python child-cleanup block, leaving its *direct* synthetic child alive. **Falsifier:** direct child is gone or zombie when parent exits.

## Executed synthetic fixture (not QEMU)

Actual environment: disposable Linux x86_64 container, Python 3.13.5, PTY created with `pty.openpty()`. The local script at `/mnt/data/puppf_m2_signal_cycle/sigterm_parent.py` reproduced PR #21's `run_console` structure, including `subprocess.Popen`, `proc.wait()`, `except KeyboardInterrupt`, `finally` SIGINT masking, `proc.terminate()/kill()` and `termios.tcsetattr`. The direct child printed `CHILD_READY <pid>` and slept 60 seconds. The harness waited for both `WRAPPER_READY` and `CHILD_READY`, then called `os.kill(wrapper_pid, signal.SIGTERM)` **only on the parent**; it inspected `/proc/<child>/stat`, then explicitly killed the surviving child in test cleanup. This isolates the parent's teardown contract; it does not send the signal to the terminal foreground group.

Command actually executed:
```sh
python3 /mnt/data/puppf_m2_signal_cycle/sigterm_parent.py
```
Actual output (one run):
```text
wrapper_exit -15 child_pid 460 child_state S
PTY_tail b'WRAPPER_READY\r\nCHILD_READY 460\r\n'
```
**Fixture process exit 0:** its expected negative condition was detected (wrapper exited from SIGTERM and child still alive in sleeping state `S`). The fixture cleaned the child afterward. **This is a demonstrated synthetic process-lifetime gap, not a claim that QEMU was left running or that Ctrl+C fails.** This precise script was executed locally but is **not committed**; the exact reported output is a test receipt, not a claim of repo-reproducible CI coverage.

## Real hosted guest attempt / blocker

At this run's container, `command -v qemu-system-x86_64` returned nothing; `apt-cache policy qemu-system-x86` returned no package candidate, `/var/lib/apt/lists` was empty, and no QEMU binaries were found in `/usr/bin`. The accepted Library ZIP is **not mounted** in `/mnt/data` in this container. No installation or network download was attempted, because no configured package candidate exists and the artifact was unavailable. Thus **no real M2 guest boot** or launcher demo was run. M1's prior two real boots remain accepted.

## Reviewable, NONTRIGGERED CI plan (not a workflow change)

If Z/Mark choose a disposable hosted runner later: create a *separate* manual-only workflow in an experiment branch, with no schedule/push/pull_request trigger, no secrets or OpenRouter, and no automatic dispatch. Use a runner with preverified `qemu-system-x86_64` and a privately staged **exact** accepted ZIP, SHA-256 check `dd333e9d6fd6a7e02e757488c872c3eb8edabe1b334b5345fdf2fd96426917b2`, then `launch.py --verify-only` and `--check`. In a PTY launch, collect guest `uname -a`, `cat /proc/uptime`, `echo Hello_Puppf`, Ctrl+C host return, `stty -g` before/after, child process exit, no surviving QEMU, and logs. A separate synthetic supervisor test should send parent-only SIGTERM and assert direct child cleanup; do not claim it is the user's Ctrl+C demo. Retain STOP, privacy, credential, cost, publication and merge gates. **No CI YAML added, dispatched or scheduled.**

## Disposition / next action

**Changed files:** only this experiment receipt. **Unchanged:** draft PR #21, accepted kernel/initramfs and ZIP, frozen P0a packet, source pins, hosted workflows, main, user demo status. **Tests run:** one local PTY parent-only SIGTERM negative fixture. **NOT_RUN:** committed reproduction fixture, QEMU, accepted ZIP verification in this run, guest boot, Actions, live host demo, Rewrite #1 ACPI investigation. **No spend.** Z/Meraki should decide whether external SIGTERM is within M2's promised teardown scope before proposing a launcher patch; if only interactive Ctrl+C is in scope, document this as an optional hardening opportunity rather than a release blocker. Do not modify PR #21 until reviewed.

**Usage boundary:** Scheduled ChatGPT task usage is **not proven** to draw down the Work/Codex weekly allowance.
