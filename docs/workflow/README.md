# Puppf workflow, v0

The deliverable is a reusable, measurable **team workflow**, exercised by a small Linux boot and an independent host-file diode. The actual image is a throwaway learning spike.

## Ownership and gates

- Mark: scope, execution, spend, acceptance, merge, naming and public release. This bootstrap branch does not grant merge authority.
- Meraki: technical lead, packet boundaries, design choices within approved scope, verification of evidence.
- Z / Mistral Vibe: spec compression, reviewer of ordinary results, assignment tie-break and disposition record.
- Codex: sole implementation worker; one packet at a time, stopping at the first complete receipt.
- Astra: independent review of security/authority claims, spec conflicts and ambiguous failures. Read-only recommendations.
- Groq (not xAI Grok): bounded read-only packet review and log triage; Tier 1 model execution only with a recorded cap.

## Bounded dispatch

1. Establish starting repo commit before writing implementation; record exact source commit in packet.
2. Give one worker **only** a specific packet, its expected SHA-256 from trusted chat/issue handoff, and named files. Verify with `python3 tools/workflow/check_packet.py docs/workflow/packets/NAME.json SHA256`.
3. Stop on mismatch, missing permissions, absent dependencies/access, new scope/architecture need, exhausted budget, or after two failed repairs following initial failure.
4. Preserve branch + commit, exact build/test commands, attempt counts, output logs, hashes, and a receipt.
5. Z reviews ordinary outcomes; Astra reviews conflicts/unsafe claims; Mark decides acceptance and merges. No automatic merge.
6. Different track = different packet and acceptance. A passing diode fixture does not pass the boot test. A booting guest is not a containment guarantee.

Coordinate the **build** using repo packets and receipts (chat may carry only task ID, commit, SHA-256). Never route build coordination through the experimental diode itself.

## Honest measurement

Cost and provider usage without reliable evidence are `null`, not zero. Record elapsed seconds separately from self-reported human minutes. Include reviews/repair/coordination costs when known. Cost per accepted result is undefined before acceptance and remains null if necessary costs are unknown. No efficiency claim until comparable work is measured.

## Provenance and next tracks

The packet checker and receipt discipline are adapted from [Castle workflow pilot PR #7](https://github.com/MarkDude-design/lightbringers-castle/pull/7). This repository carries the method without copying Castle's unrelated history.

- **P0a:** direct QEMU kernel + initramfs + BusyBox serial boot, actual timed HELLO and two-boot acceptance; no network or model API.
- **S0 v0:** host-only mock file diode, no QEMU, no external provider or paid run; determinism and STOP proofs.
- **Later:** model-backed Tier 0, capped Groq Tier 1, and separately reviewed guest transplant. No guest-chamber security claims in v0.

No successful builds or experiments are asserted by this bootstrap.
