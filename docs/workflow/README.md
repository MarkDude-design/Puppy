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


## Provenance, telemetry, and review separation (2026-10-21)

- `as_recorded`: hash copied from a trusted handoff or repeated by a reviewer. **Not independently checked**.
- `verified`: deterministic `check_packet.py` calculated SHA-256 from the *exact packet bytes* and compared it to the independently delivered expected hash. Record tool, resulting digest, and verification time. Matching an adjacent `.sha256` alone checks internal consistency, not authenticity.
- A reviewer model does not invent its own invocation usage. Mark or the calling client appends response usage/cost metadata to the receipt after the response; unavailable telemetry remains `null`. `Codex` labels the worker role, not the actual model identity. Record requested and observed model IDs separately or `null`.
- Cost totals come only from `python3 tools/workflow/cost_report.py path/to/receipt.json ...`. The explicit receipt `cost_items` ledger includes model usage, compute, coordination and review if attributable. Each item needs evidence; `cost_coverage: complete` is an accountable human claim, not a proof calculated by the script. Unaccounted lanes keep total and cost-per-accepted-result `null`; the observed-cost subtotal is labeled separately. Rejected work still costs money. Only Mark-accepted and reviewer-accepted results count.
- Z is the continuing collaborator/coordinator. An OpenRouter-hosted Mistral model is an optional, replaceable **reporting module**, not Z's seat or a substitute for review authority. It may summarize the script's results; it does not calculate or authorize them.
- Optional free-tier access or available credit does not demonstrate a metered call costs $0 or establish a spending cap. Preserve the recorded free-tier decision, provider details, and platform telemetry where actually available.
- A manual chat/paste ferry does not create an automatic connection between Codex and Z.
