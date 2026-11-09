# Puppf M2 disposable-host experiment — manual plan (NOT RUN)

Seat: Meraki. Date: 2026-11-09 PT. Scope: review-only experiment, no workflow YAML, no dispatch, no PR #21 edits.

## Independent question

Can a disposable QEMU-equipped runner boot the **already accepted** M1 kernel/initramfs using the unchanged draft PR #21 launcher, demonstrate guest commands, and restore the host terminal on Ctrl+C?

PASS requires an observed PTY guest prompt, guest `uname -a`, `cat /proc/uptime`, `echo Hello_Puppf`, terminal settings equal before/after, and no surviving QEMU. A missing binary, ZIP, PTY or guest prompt is BLOCKED/FAIL, never PASS.

## Inputs and preflight

- Accepted evidence: Library ID `libfile_4d168bd731d88191b75d5c570f1dcad8`, SHA256 `dd333e9d6fd6a7e02e757488c872c3eb8edabe1b334b5345fdf2fd96426917b2`.
- Source: `work/puppf-m2-launcher-20261104` at reviewed commit; `puppy-p0a/launch.py` and `accepted-build.json`.
- Disposable runner must have QEMU, Python 3, a usable PTY, and private artifact staging with no public logs containing ZIP contents. Record exact QEMU/Python versions and runner identity.
- Before boot: `sha256sum puppf-build-11-evidence.zip`; `python3 puppy-p0a/launch.py --evidence puppf-build-11-evidence.zip --verify-only`; `... --check`. Abort on any mismatch.
- For interactive test use a real allocated PTY; record `stty -g` before and after; boot unchanged launcher; collect exact guest outputs; send a single Ctrl+C and wait; inspect `pgrep -af qemu-system-x86_64` carefully distinguishing unrelated jobs.

## Guardrails

No scheduled, push, or PR triggers; no new workflow committed or triggered here. No Buildroot rebuild, no paid calls, no OpenRouter, no external secrets, no merge, no public artifact upload, no relaxation of STOP/privacy gates. A manual-only workflow could be proposed later *after* a runner and secure ZIP handoff are verified; approval to test does not itself prove those dependencies.

## Current execution receipt

Environment: this session's disposable container, Python 3.13.5. `command -v qemu-system-x86_64`, `command -v docker`, `command -v podman` all returned no path. `apt-cache policy qemu-system-x86` produced no candidate. `/mnt/data` did not contain the accepted ZIP. Therefore guest boot **NOT_RUN / BLOCKED**; this is not an accepted M2 demo.

## Astra independent review request

Review the unchanged PR #21 launcher and existing repeated-Ctrl+C positive test against two *synthetic* negatives (SIGINT with grandchild, SIGTERM parent-only with direct child). Determine whether process-tree or supervisor termination is an M2 acceptance requirement or optional hardening; provide a falsifiable test and narrow change suggestion only on a separate experiment branch. No Astra execution is claimed here.

Changed file: this plan only. Tests actually run: executable/host presence checks above. NOT_RUN: accepted ZIP verification, QEMU boot, guest commands, terminal restoration, hosted CI, Astra model consultation. M1 remains accepted; draft PR #21 unchanged. Scheduled Chat task usage is not proven to draw down Work/Codex weekly allowance.
