# Run receipt — first sandbox build, owner ferry — preserved verbatim

- **Received:** 2026-11-10, pasted by MarkDude (owner) from the GitHub Actions run page ("from gh sandbox-build-and-run / failed 12 minutes ago in 32s").
- **Provenance:** `as_recorded` — owner paste from the Actions UI.
- **Parse:** run ended BUILD_FAILED after 32 seconds at the Buildroot acquisition step. `git clone https://git.buildroot.net/buildroot` returned "fatal: repository not found" (exit 128). The workflow's publish step then correctly found no QEMU log and committed nothing — confirming the publish-only-on-success gap named in Z review #5 and closed in the same commit as this receipt.
- **Status:** the first honest runner receipt this sandbox produced.

---

```
from gh sandbox-build-and-run
failed 12 minutes ago in 32s
Search logs
0s
1s
26s
1s
0s
Run git clone --depth 1 --branch 2026.08 https://git.buildroot.net/buildroot /tmp/buildroot
Cloning into '/tmp/buildroot'...
fatal: repository 'https://git.buildroot.net/buildroot/' not found
Error: Process completed with exit code 128.
0s
0s
1s
```
