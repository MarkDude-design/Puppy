# Text-Linux origin and measurement brief — historical source

Archived 2026-10-28 from the Meraki Castle/Ring conversation. This file preserves original design intent for later project archaeology. It is not a replacement for current Puppf packets, locks, acceptance criteria, or security instructions. It makes no new successful-build, boot, USB, size, or reproducibility claim.

## Why this project was chosen

Mark wanted a small text-only Linux experiment, informed by old Puppy Linux experience, as a real task through the Team workflow. A nearby t3os announcement prompted comparison and collaboration rather than a requirement to win a personality contest. Credit existing Linux components and Puppy/Barry Kauler method lineage. The Linux/MINIX/Tanenbaum analogy was a gesture toward learning through construction, not a claim of code derivation or architectural equivalence.

The workflow itself was the durable objective: a bounded packet, implementation, measured result, review, and revision. The guest was to become a testable artifact rather than another planning-only deliverable.

## Original baseline requested

- x86_64 Linux with text/serial console, minimal userspace (BusyBox preferred), functioning init, and deliberate shutdown.
- One documented QEMU machine/boot configuration to start.
- A guest-generated readiness marker, a human-equivalent console input producing HELLO and build/source identity, and display of a bundled read-only task description.
- First a working baseline; then a self-booting artifact suitable for later USB testing. Direct QEMU kernel loading alone did not establish USB bootability.
- Buildroot was a preferred established tool, not a requirement to design a new distribution framework. Pinned sources, configs, commands, checksums, and licenses were part of the receipt.

## Original size and filesystem comparison

Hypothesis/target: complete self-booting image below 60,000,000 bytes. Preserve a working miss and report real measurements rather than removing necessary functionality for a claim.

Report kernel, initial/root filesystem, bootloader and other boot files, complete logical image bytes, uncompressed root bytes, any distinct download/archive size, configured guest RAM, and observed memory information. Sparse allocation or a compressed download is not the complete bootable-image size.

Intended storage was approximately 0.5 GB USB; exact image bytes and capacity requirements were to be stated. No physical-drive write was authorized in that task.

After baseline success, compare one SquashFS variant using substantially the same userspace. Show that the guest actually uses it. Distinguish a compressed root from loadable application modules. Compare boot behavior, complete size, RAM configuration, and required components. A .sfs extension alone is not a result.

Original work bound: one baseline, one filesystem variant, at most two further measured minimization revisions. Failed variants and useful reviewer seeds remain evidence. Model runtimes, TLS, networking, clients, credentials, and weights were not to be implied by a small boot-only baseline.

## Original execution and verification requirements

- No guest networking, listeners, remote control, credentials, MCP, host writable shares, or host disks. One VM at a time; finite boot timeout and bounded console output.
- Host downloads/build dependencies are separate from guest capabilities. Use pinned official sources and available integrity verification; no remote installer piped into a shell.
- Keep outputs/caches out of Git. A draft source PR was not a public release grant.
- The harness distinguishes build failure, failed guest start, timeout/panic, readiness, HELLO response, and shutdown. Expected readiness must come from the guest rather than launcher text.
- A negative control should reject a missing readiness marker or broken startup. Preserve failures; do not add skips or expected failures to manufacture green verification.
- Record actual commands, host tools, artifacts, hashes, durations, sizes, and outcomes. Claim bit-for-bit reproducibility only after matching repeated builds.
- If network, compiler, or virtualization prevents execution, report the precise blocker and deliver a complete recipe with diagnostics; do not fabricate a boot or size receipt.

## Separate proposed paid minimization experiment

Mark later authorized up to $0.25 for a separate useful experiment, expressing a preference to spend roughly 5–15 cents on actual work. The carried Codex brief proposed up to three independently generated improvement tickets against the same frozen evidence, two calls each, maximum six calls, with shared cumulative accounting. It suggested a named paid worker and an economy reviewer subject to fresh qualification.

The work was to reduce an actual built image while preserving functionality, or address a concrete baseline blocker; compare proposals; have Codex implement the best supported bounded idea; rebuild and measure. It did not authorize padding calls to achieve a billing floor or ignoring a failing gate.

Complete accounting, actual model identity, STOP/lock checks, conservative next-pair reservation, and no uncertain transport retries remained required. Candidate comparison did not automatically stop at its first valid pair; that was a distinct comparison specification, unlike the earlier Castle batch. The archive does not establish that these calls ran or that $0.25 remains available now.

## Separate Team communication experiment

The host-side two-endpoint exchange was deliberately uncoupled from the boot milestone. Tiny guest/channel transplantation was a later option. Mock-first message delivery, transcript, STOP, explicit byte/turn caps, and channel-assigned identity were independent work; do not enlarge the boot task to include a relay without a new scoped assignment.

## Current continuation

This origin brief predates the repository's later Puppf packets and Agent Desk/workflow documents. Consult current main and the relevant task packet before acting. Old suggestions to place an experiment under Castle were contextual; this archive's project home is now MarkDude-design/Puppy.

END TEXT LINUX ORIGIN BRIEF
