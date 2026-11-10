# Puppf Sandbox — Gemini Build Lab (2026-11-10)

**Status: SANDBOX. This branch is not the main route.**
Chartered by Mark (owner), 2026-11-10, for the Gemini seat to try build ideas with free usage.

## Ground rules (limited to build scope)

- Everything on this branch is disposable experiment territory. Push freely, break freely.
- Scope = build/CI experiments on this branch only. No PRs to `main` — Mark gates all merges. Do not modify the main-route workflow (`puppf-p0a-build.yml`) or packet/receipt files.
- No secrets, no API keys, no paid external calls. GitHub-hosted runner usage on this branch is authorized free usage — failures are data, burn is fine.
- Sandbox results are not main-route evidence. Anything that proves out here earns a normal packet + review + pinned-gates build before any transfer.

## Where Puppf is (status update for incoming seats)

- Method-first: pinned sources (Buildroot 2026.08, Linux 6.18.7, BusyBox 1.38.0), GPG `VALIDSIG` trust chain, receipts, two-boot QEMU acceptance.
- P0a boot spike: PASS (Actions run 41773110103), disposable by design; current lane is rewrite #1 per docs/ROADMAP.md ("fix what the spike taught").
- Separate future lanes: P0b ACK, P0c UEFI/laptop/ISO, S0 host-side diode, M2 launcher experiments.
- Governance and seat roles: docs/workflow/README.md. Main-route dispatch stays with Mark.

## Where your idea fits

Your debootstrap → squashfs → ISO sketch (received 2026-11-10) is preserved verbatim at `sandbox/incoming/gemini-build-minimal-agent-linux-iso-2026-11-10.yml`, reviewed at `sandbox/reviews/Z-REVIEW-gemini-iso-sketch-2026-11-10.md`. Headline: as written it has never executed and is predicted to fail at "Prepare Kernel and Initramfs" (minbase ships no kernel). A runnable branch-local copy lives at `.github/workflows/gemini-sandbox-iso.yml` with three Z annotations (trigger scoped to this branch, least-privilege permissions, short artifact retention). The push that carries this commit fires the first run — keep that log; the failure is your first receipt.

## The challenge

Don't just repair the ISO path. Try ideas we did NOT take:

- initramfs-only RAM OS — kernel + initramfs, no squashfs, no ISO, straight to your agent
- musl/static or Alpine `apk` base instead of debootstrap
- the one-binary floor: one static agent binary + a kernel — smallest booting system you can produce
- a reproducible build as a Nix or Guix expression
- boot-to-first-agent-action timing — fastest measured boot you can get

Whatever you try: produce a receipt — exact commands, run logs, artifact sizes, honest failure lines. A real failed run beats plausible YAML every time.
