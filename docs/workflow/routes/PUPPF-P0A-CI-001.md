# P0a CI runner route addendum — 2026-10-21

**Route decision (Meraki lead):** Use a standard GitHub-hosted `ubuntu-24.04` runner as the build/test **machine** for the already-authorized P0a learning spike, instead of attempting to overcome Codex's restricted host. Codex remains the **implementation author**. Z reviews ordinary results, Astra resolves material exception/security claims, Mark controls merging and manual run authorization.

## Why a separate route addendum

The already merged, Z-approved `docs/workflow/packets/PUPPF-P0A-002.json` is immutable. Its SHA-256 stays `b0417934776c214ca3189c8822b85baf1e71fc262f66ada98bce2092f07c9c9b`. This file **only changes the execution venue and names the minimal extra workflow path**. It does **not** change kernel, shell, heartbeat, timing, RAM, size, serial evidence, repair rules, or acceptance. A changed acceptance condition requires new packet version/hash and Z/Mark disposition.

## Why this runner and how to use it

- Public `MarkDude-design/Puppy`, standard hosted `ubuntu-24.04`: 4 vCPU, 16 GiB RAM, 14 GiB runner SSD, six-hour GitHub-hosted maximum per job. **This first job is capped lower at 180 minutes** and records disk/CPU/memory preflight. Buildroot may not fit in 14 GiB; make the first failure honest and propose disk relief separately.
- The workflow is `workflow_dispatch` **only**. No `push`, `pull_request`, `pull_request_target`, untrusted fork builds, cron, self-hosted runner or SSH. It requires Mark's click (or separately authorized GitHub action). It is discoverable when this workflow file is on the repository's **default branch**; after merging, Mark can explicitly choose a reviewed code branch from the Run workflow dropdown.
- Workflow token is read-only `contents: read`, and nothing needs secrets or persistent cloud credentials. No automatic merge, release, external network/model provider invocation, or physical media writes.
- `sudo apt-get` is allowed *inside this disposable GitHub VM* for Buildroot/QEMU dependencies; no external Codex host APT access is required. Verify Buildroot 2026.08 official source and signature/digest on-run. Failed download or bad authentication => BLOCKED/FAIL, never an insecure fallback.
- Provenance: hosted logs are externally timestamped and linkable **evidence**, but not inherently unfakeable or independent proof of guest state; scripts/fixtures must establish actual QEMU serial output and artifact hashes.

## Narrow allowed-path extension to the frozen P0a packet

Apart from existing `puppy-p0a/**` and `docs/workflow/runs/PUPPF-P0A-002/**`, the **only** newly proposed implementation write path is `.github/workflows/puppf-p0a-build.yml`. This route addendum itself lives at `docs/workflow/routes/PUPPF-P0A-CI-001.md` and is lead-prepared for Mark's PR approval. Other workflow changes require fresh review. Codex must work on an independent implementation branch and open a PR; do not write to main.

## CI entrypoint contract

The route YAML installed by this addendum invokes `bash puppy-p0a/ci/run-ci.sh`. **That script does not yet exist** and must be implemented by Codex on an independent branch before a manual run is meaningful. An absent entrypoint is a hard failure, not a pretend test.

Runner env:
- `PUPPF_EVIDENCE_DIR` is a fresh path under `RUNNER_TEMP` for logs/results/artifacts; upload only sanitized evidence.
- Input packet file and independent hash are read-only. CI checks exact bytes using `tools/workflow/check_packet.py`.
- `run-ci.sh` orchestrates download/signature or trusted digest checks, pinned Buildroot config, build, two separate QEMU boots using unchanged artifacts, checker fixtures, final receipt/manifest, and nonzero exit if acceptance fails.
- Preserve `run-1/serial.log` + `run-1/test-results.json`, `run-2/serial.log` + `run-2/test-results.json` plus manifest, artifact byte sizes+SHA-256 and QEMU argument captures. No shell echo-only false positives. First `HELLO seq=1` must use absolute guest `/proc/uptime <=15` seconds.
- Runtime `-nic none`, no shares, host block devices or guest networking. 128 MiB guest allocation; serial shell within 90s; 3 HELLOs, uptime gaps 115-125s, host-arrival gaps 105-150s, watchdog 390s each; retired 240s total span floor remains retired.
- Upload logs/receipts regardless of pass/fail (`if: always()`) and preserve small artifacts up to the existing packet's size ceiling, subject to runner storage/retention limits; use a 3-day retention by default. Capture logs before process exit, and don't print secrets.

## Money/authority

Mark has set a **project ceiling of $50** for extra services if needed. This authorizes investigation and planning for a paid fallback, *not* automatic API purchases, external VMs or unlimited metered agent runs. Standard GitHub-hosted compute for a public repo is free under current official GitHub documentation; artifact/cache storage quota and any nonstandard services must still be accounted for. Record unknown Codex subscription/compute usage as `null`, not zero. Do not hire another model or spend unless the free lane encounters an actual blocker and Mark authorizes a specific paid service.

## Sequence and stop

1. Meraki prepares this CI route and a manual-only workflow PR; Mark reviews/merges.
2. Codex authors `puppy-p0a/**` with named source paths, Buildroot pins/checks, guest scripts, QEMU launcher, real fixture acceptance, and honest receipts in a **separate** implementation PR; Z reviews that PR; Mark merges or chooses reviewed branch for manual workflow dispatch.
3. Mark manually runs the Actions workflow on the reviewed branch; collect run URL/job SHA/runner version and artifact checksums. No automatic retry/repair loops.
4. Z reviews one full receipt or BLOCKED report; Astra handles exceptional evidence disputes; Mark alone accepts or merges. After first failure, at most two bounded repair attempts, per frozen packet.
5. S0 remains independent; Codex is one worker and handles one assigned packet at a time. It can move to S0 after submitting the P0a work/receipt, not silently build both.

**Prior worker environment BLOCKED receipt:** `ea0465207a5394d27e8b1383168bb368d8ce4553` on `work/puppf-p0a-002-20261022`. Keep it preserved and Z-reviewed; it is not a failed Linux image.

## Sources for current platform terms

- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow
- https://docs.github.com/en/actions/reference/security/secure-use
- https://buildroot.org/download.html
