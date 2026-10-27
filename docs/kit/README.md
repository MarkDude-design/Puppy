# Puppf KIT v0 — build-first team harness

**Status: REVIEW PROPOSAL; 2026-10-27.** KIT is the established short name for the Codex implementation and verification seat. This proposal does not install, dispatch, spend, merge, or certify anything.

## Mission: a usable Puppf boot kit soon

The first deliverable is a **downloadable, inspectable, offline x86-64 QEMU boot kit**, not a general-purpose distribution, container boundary, or model runtime. One versioned bundle should eventually contain the real kernel, compressed initramfs, static BusyBox guest, launch script, SHA256SUMS, source/license provenance, and a concise human README.

First prove the already frozen P0a acceptance on **two real QEMU boots with the same artifact hashes**. Both boots need serial shell proof that cannot be passed by terminal command echo, three actual HELLO records with correct absolute kernel uptime and 120s cadence, separate run-1/run-2 logs, 128 MiB allocation, networkless guest (-nic none), and payload sum strictly below 100,000,000 bytes. The old 240s span floor remains retired. Size below 60MB is an optional stretch goal, not a change to P0a pass/fail. Mark separately accepts packaging, name and public release.

P0b correlated ACK, the S0 file diode, SquashFS, EFI/laptop boot, a GUI, and KolibriOS-in-OS are **future independent packets**, not blockers for this first kit. No model needs to run inside the guest.

## Evidence already on Puppy main

- Frozen PUPPF-P0A-002 SHA256: b0417934776c214ca3189c8822b85baf1e71fc262f66ada98bce2092f07c9c9b. Do not edit it in KIT v0.
- The Buildroot/QEMU runner exists: .github/workflows/puppf-p0a-build.yml and puppy-p0a/ci/driver.py, run-ci.sh. Actual successful two-boot execution has **not been independently verified in this proposal**. Inspect the live Actions run and artifact logs rather than inferring success from merged code.
- Puppy PR #10 reports 120 passing mock/no-model acceptance tests. Those are valuable *fixtures*, not serial-console guest evidence. Avoid rebuilding an existing checker.
- Earlier Codex APT/proxy BLOCKED receipt (commit ea04652) is host-provisioning history, not a failure of compiled Linux.
- The Eko/Meraki-Z bus comparison document is **already uploaded on Puppy main** as EKO_MERAKI_Z_BUS_BRIDGE_V0.md, commit 2eabc0e. Mark need not upload it again.

## What we adopt from other projects

**AllUrBase/Eko:** Keep its real JSONL event model, retry/error/stop receipts, public bus pickup, evidence-first log diagnosis, and tested backoff/Retry-After. **Do not fork the whole conversation runner into Puppf.** It is an implementation reference for error events, not a dependency for boot. The public bus is never a private notebook.

**Puppf:** Keep packet hashes with verified versus as_recorded provenance, distinct source and execution commits, unknown usage/cost as null, honest STOP/BLOCKED outcomes, two independent acceptances, and no instrument measuring its own construction. This is the project's accepted method.

**Native team communications:** Puppy issue #11 is the existing hashed mailbox for Meraki, Z, and other seats. No second competing bus is required. GitHub stores and carries Markdown; it does not autonomously wake an idle native model session.

**Z Desk:** AllUrBase has a real two-role consult runner (diff for small details, man for deeper challenge) with caller-side cost and error receipts. That is an optional **API model instrument**, not Z's continuing Mistral collaborator voice. Groq is managed by Z; Meraki supplies bounded evidence and consumes independent findings.

**KIT:** Codex implements, verifies, builds CI and can consult bounded reviewers or native subagents when actually available. A fresh-context subagent is not guaranteed to be a different underlying model, free, or equipped with all parent tools. Thing One/Two are run-scoped aliases; the receipt preserves actual IDs.

## Authority and money

Mark: goal, success criteria, privacy/public release, $50 initial Puppf ceiling (can be amended), secrets, paid-provider authorization and final acceptance/merge unless a specific fixer delegation is recorded. Meraki: project technical lead, packets and architecture. Z: continuing collaborator, spec compression, ordinary review and assignment tie-break. KIT/Codex: one implementation owner per file, bounded tests and receipts, no self-spend/self-merge. Groq: Z-controlled independent review. Astra: independent exception/architecture reviewer **when an actual review route is available**; this chat does not claim an Astra session ran.

**$50 is a ceiling, not a measured spend or automatic paid-service mandate.** Use standard public GitHub-hosted Actions and existing authorized connections first. Any new paid provider must have a named task, model/transport, specific maximum charge and recorded approval. No copying OpenRouter or GitHub PAT secrets out of AllUrBase; do not inherit its separate $10/$20 policies or GAS MODE. Unknown API/subscription/compute charges remain null, not invented zero.

## Small steps toward first useful artifact

**G0 — observe first:** KIT reads actual P0a Actions run ID, failing job/log, checkout SHA, preserved artifacts and test evidence. Classify PASS (two boots proved), FAIL (real code/test failure), BLOCKED (external prerequisite), or UNKNOWN (not enough evidence). Produce one reviewable receipt. No rerun yet.

**G1 — smallest repair:** If needed, a single narrow fix on a task branch, deterministic tests, one bounded reviewer/consult if it genuinely changes the diagnosis, Z disposition, Mark/recorded fixer merge, manual Actions run. The existing frozen repair/STOP limits remain. A green test suite alone is not a boot.

**G2 — boot-kit packaging:** Only after a verified two-boot result, make a reproducible-from-sources QEMU launcher bundle with hashes and instructions; test a fresh download/launch. Mark approves any public binary release. Record measured bytes and host requirements, not guessed specifications.

**G3 — expansions:** separate P0b, S0, laptop, SquashFS and eventual model/diode transplant work. No expansion simply because people have shown interest.

## Contributors

Invite interested people to submit narrow issues and PRs for log triage, packaging docs, small build fixes or QEMU compatibility. Protect main and never expose Actions secrets/write tokens to untrusted PR execution; no self-hosted public-PR runner. A volunteer need not pick an AI model to report an error.

Start with KIT-G0-001 in FIRST_HANDOFF.md. The consult interface and independent Astra request are separate documents. No wide AGENTS.md policy and no elaborate hierarchy needed before actual utility is demonstrated.
