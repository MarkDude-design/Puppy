# Puppf M2 synthetic abnormal child-exit fixture — 2026-11-09 PT

**Question:** Does the unchanged PR #21 `run_console` structure propagate an abnormal child exit code while restoring a PTY that the child modified? Unlike earlier SIGINT-grandchild and parent-only SIGTERM negatives, this tests ordinary wait completion with child exit 7 and ECHO toggled.

**Environment:** Debian GNU/Linux 13 (trixie), Python 3.13.5, Linux PTY. Source copied directly from draft PR #21 `puppy-p0a/launch.py` `run_console` (not imported from live repo; standalone replicated structure). No QEMU binary and no accepted build #11 ZIP mounted.

**Executed:** `python3 /tmp/m2_exit_fixture.py` (equivalent to committed `fixture.py`; committed copy omits unused `time` import).

Exact observed output:

```
FIXTURE exit=7 restored=True
harness_exit=0
```

**Result:** PASS for this *synthetic* negative exit path: child status 7 propagated and PTY settings restored. Not a real QEMU guest boot, and not evidence for descendant cleanup or parent-only SIGTERM. The prior negative fixtures remain open as optional hardening/acceptance-scope review. No production source or PR #21 modification.

**Changed files:** `docs/workflow/experiments/m2-child-exit-20261109/fixture.py`, `RECEIPT.md` on separate branch only.

**NOT_RUN:** Real QEMU, ZIP verification, ACPI Rewrite #1, hosted CI, model calls. **BLOCKER:** `qemu-system-x86_64` absent and accepted ZIP unavailable in current container; earlier nontriggered hosted test plan already exists, so no duplicate workflow proposed. M1 accepted build #11 preserved; no rebuild, no dispatch, no merge, no paid spending, no credential access. Scheduled Chat task usage is not proven to draw down Work/Codex weekly allowance.
