# Puppf M2 cycle — descendant teardown negative fixture (2026-11-09)

**Seat:** Meraki. **Source:** draft PR #21 branch `work/puppf-m2-launcher-20261104`, launcher GitHub blob `2356251fcc645884594f23f9496b373ea862c364`. **Experiment branch:** `experiment/meraki-m2-descendant-teardown-20261109`. **Status:** NEGATIVE FIXTURE FOUND A NARROW ORPHAN CASE; NOT A QEMU BOOT, NOT AN M2 ACCEPTANCE OR A PROVEN NORMAL-QEMU BUG.

## Prior state checked
- Owner accepted M1 from build #11, run 41773110103, two real guest boots, source e0b5e0e4b206c30ca3bcbfcf08c764a2acf19808; ZIP SHA256 dd333e9d6fd6a7e02e757488c872c3eb8edabe1b334b5345fdf2fd96426917b2. Do not rebuild.
- Issue #15 records the M2 draft and an earlier **repeated Ctrl+C** defect fixed by Astra. The earlier tested fixture exercised direct child reaping/terminal restoration, not the exact case of a child spawning a second, long-lived process.
- Draft PR #21 unchanged. No prior matching descendant teardown fixture was found in a scoped repository text search (not a guarantee of exhaustive coverage).

## One falsifiable hypothesis
`run_console()` terminates and reaps its direct Popen child on SIGINT, but a child that spawns a long-lived same-process-group descendant can leave that descendant running after the wrapper returns. If no descendant survives, this hypothesis is falsified.

## Actual local synthetic execution
Environment: Linux x86_64, Python 3.13.5, root container, PTY. Ran a local script reproducing the exact PR #21 `run_console` interrupt/cleanup structure, with synthetic Python child that spawns another Python sleep process. Sent SIGINT to the wrapper after receiving both child PIDs; inspected descendant state in `/proc/<pid>/stat`; forcibly killed surviving descendant in fixture cleanup.

Command: `python3 /mnt/data/puppf_m2_cycle/negative_descendant.py`.
Observed: `wrapper_exit 0 descendant_pid 443 descendant_state S`; PTY tail contained `CHILD 433 DESC 443\r\nSTOPPING\r\nRESTORED\r\nGRANDCHILD 443\r\n`. Fixture explicitly printed `CLEANED_UP_LIVE_DESCENDANT` and `FAIL: direct-child termination left synthetic descendant alive`. **Process exit 1 expected for a detected negative case**; it is not a launcher suite failure. The process was cleaned up by the fixture. This is a real synthetic process/PTY test, not a simulated text-only answer.

Committed a **reviewable reproduction variant** at `docs/workflow/experiments/m2-descendant-teardown-20261109/negative_descendant.py`; this GitHub variant is semantically equivalent but was **NOT_RUN** after upload, so its output is not claimed. GitHub fetch-back required to verify committed bytes.

## Relevance / limits
The existing launcher starts QEMU without `start_new_session=True`, then calls `proc.terminate()` or `proc.kill()` on only the immediate process. A spawned child may survive. However **QEMU normally runs as a single process**, and this fixture does not establish QEMU spawns such descendants, that a guest boot is affected, or that the previously fixed repeated-interrupt test regressed. This is a narrowly demonstrated containment/cleanup edge case, not grounds to revoke M1 acceptance. A future fix should first decide whether process-group teardown is part of M2's contract, then use an isolated process group and test repeated Ctrl+C + descendant reaping without signaling the host group.

## Hosted boot availability
Direct container: `command -v qemu-system-x86_64` returned no path; `apt-cache policy qemu-system-x86` showed no candidate and `apt-get download qemu-system-x86` returned `E: Unable to locate package qemu-system-x86`. No install performed; no disposable QEMU guest run was possible here. The accepted Library ZIP is not mounted at `/mnt/data` in this environment; it was not modified or downloaded. No hosted workflow was triggered. A future *untriggered* CI experiment can use a manually approved GitHub Actions Ubuntu runner with `qemu-system-x86` and the exact pinned ZIP, run the PR #21 launcher under `script`/PTY, send guest commands and SIGINT, and collect serial transcript, terminal settings, process tree and cleanup; must be owner-triggered only after private ZIP transfer and permissions review. No workflow file added here.

## Scope and next action
Changed **only** the new experiment fixture and this receipt, not `launch.py`, PR #21, source pins, guest, accepted image, frozen packet, workflows or main. No model API calls, OpenRouter spend, CI dispatch, credential changes, publication, merge or paid host. Next reviewer can execute committed fixture on Linux and decide whether to patch launcher in a *different experiment branch*, not PR #21; do not claim a real QEMU boot without QEMU, accepted ZIP and logs.

**Allowance accounting:** No evidence that this scheduled ChatGPT task consumes the owner's Work/Codex weekly allowance.
