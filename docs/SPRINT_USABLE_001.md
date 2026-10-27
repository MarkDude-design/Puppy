# Puppf: usable-system sprint / Codex Agent Kit v0.1

**Prepared:** 2026-10-27. **Status:** candidate for Z and independent Astra-class review; no code execution or spend authorization implied. **Baseline examined:** `main` at `2eabc0e96b846d1f83235350c820c71a286d04a7`.

## Outcome and honest baseline

**Mark's explicit 2026-10-27 product choice: SERIAL/TERMINAL SHELL FIRST.** First user-visible deliverable: one documented **x86-64 bootable RAM-first Linux image** that actually reaches an **interactive serial/terminal shell in QEMU**, reports genuine uptime HELLOs, passes twice-boot acceptance with unchanged image hashes, and has a repeatable launch command. The user must be able to type a command, see its real response, and exit cleanly. A GUI, desktop environment, mouse support, window manager, graphical boot, physical laptop/USB boot, networking, package manager, persistent storage, or secure meeting chamber is **not required** and must not delay M1.

Already present: reviewed packets `PUPPF-P0A-002` and `PUPPF-S0-001`, exact-byte verification checker and receipts, host provisioning BLOCKED evidence, hosted Actions preflight route, and new **no-model** nonce/size/state/ACK mock acceptance scripts. Those mock tests are useful but are not actual boot results. A prior GitHub workflow runner-context startup failure was corrected in PR #9. Validate actual hosted run history and real artifact presence before claiming progress beyond this.

Sister repo `MarkDude-design/ALLurbaseRnotbelong2us` has a real Python OpenRouter API conversation bus (`start/turn/retry/error/stop` JSONL), published public `bus` branch for incident triage, and a Meraki–Z **native-seat Markdown ferry**. Do not conflate API proxies with Meraki/Z's existing chats, or public bus branches with private notebooks. No direct unattended native-seat transport is established by these repo files.

## Stage gates — product and team separated

| Milestone | What the user can do | Acceptance |
|---|---|---|
| M0 — ground truth | Read one actual repo status/blocked/runnable matrix | Exact main SHA, tool paths, observed CI run IDs, failing command/output and missing artifacts; no guessed result |
| M1 — real P0a (terminal FIRST) | Boot a tiny image in QEMU; type commands at the serial shell and see guest output | **Unchanged frozen P0a acceptance**: pinned Buildroot source, static BusyBox/initramfs, `-nic none`, 128MiB, 90s serial shell with fresh non-echo token, 3 real HELLOs at 120s cadence using absolute `/proc/uptime`, two boots, unchanged artifact SHA256, per-run logs, sum kernel+initramfs strictly <100000000 bytes. **No GUI required.** |
| M2 — easy terminal use | One-command QEMU launcher, tested host requirements, verified artifact location/link and short terminal demo | Someone unfamiliar with the build runs the launcher, types `uname -a`, reads `/proc/uptime`, sees real guest output, and exits/shuts down cleanly. No root-required host writes unless clearly justified; GUI remains a *later optional* milestone. |
| M3 — communication instrument | Host-only S0 mock file diode | Two spool dirs, permission checks, 256-byte JSON, six-round STOP, append-only deterministic twice-run transcript; **separate packet and acceptance** |
| M4 — model team | Codex calls bounded helper endpoints to inspect logs/propose patches | Provider ID and client usage logged; readonly review first, explicit per-run dollars, retries and cap; Z independently reviews |
| M5 — guest meeting room | Host models exchange controlled messages with the VM through limited guest-visible doors | Separate design/packet, deterministic safety/privacy tests, no security claim from `-nic none` alone |

**Priority order:** M0 truth audit → M1 real terminal-shell boot → M2 one-command terminal demo → optional GUI planning, S0, and helper services. No graphical dependencies in M1 or M2. M1 and M3 do not share acceptance. M4 is useful for implementation but is **not a prerequisite** to M1. Nothing in this paragraph changes the frozen P0a packet or its hash.

## Codex Agent Kit v0.1: minimal rather than an orchestration platform

**Owner:** Meraki routes packet designs/evidence; Codex writes implementation on reviewed task branches; Z checks ordinary results/assignments; Astra is a separate, independent exception/architecture review **when available and explicitly invoked**, not a hidden always-on process; Groq and API-hosted Mistral are optional fresh-context helper models. Mark retains merge, spend, execution, acceptance, private/public posture.

A proposed lightweight adapter accepts `task_id`, `source_commit`, `inputs`, `allowed_paths`, `question`, `model_requested`, `provider`, `max_output_tokens`, and `max_cost_usd`. It returns an **untrusted suggestion**, observed model/provider metadata, caller-captured usage, error class, retry receipts, hashes of supplied context, and `STOP/BLOCKED/PROPOSED`. Only deterministic scripts decide test pass/fail. Each helper has no repo write token or auto-merge capability.

Select helper from capability, not identity theater: Mistral for spec compression, short code review or prose; Groq for fresh-context log triage; other models only if explicitly configured and useful. If an API is unavailable, preserve a manual GitHub Markdown review as first-class fallback. Never silently relabel an API model as Z, Meraki, or Astra.

### Helper lanes with tight inputs

1. **TRIAGE**: Read `failure.log`, `manifest.json`, failing command and a bounded code excerpt (not full repo). Return first actual failure with quoted evidence line, likely cause marked hypothesis, a single suggested check, and stop condition.
2. **REVIEW**: Read frozen packet, exact source SHA, proposed patch and negative-test result. Identify contradictions and smallest concrete gaps. No self-review of helper-written patch.
3. **PATCH_SUGGEST**: Only after explicit task authorization; return a patch limited to named paths plus tests to run; Codex checks it. The helper never pushes directly.
4. **REPORT**: Summarize *deterministic* receipts and error events. Cost arithmetic comes from scripts, not a language model.

Stop after the first verifiable receipt, uncertain model/provider identity, exhausted budget, repeated auth/rate-limit problems beyond configured retries, missing input/permission, or an out-of-scope edit request. Preserve every failure rather than inventing PASS.

### Bus compatibility

Adopt AllUrBase's **event vocabulary** (`start/turn/retry/error/stop`) and error-report usability as inspiration, but keep Puppf's **packet/receipt ledger** as authority. A future versioned projector can show both without rewriting raw bus events or letting the experimental instrument coordinate its own construction. Use run-local sequence, actor, UTC, source ref, packet SHA provenance, and optional error code; don't invent a global order from timestamps.

## Budget policy — separate Puppf envelope, possible later expansion (not automatic purchases)

Total *new discretionary* spend across this Puppf sprint may be **up to $50 with Mark's explicit per-service approval**; it is not an open-ended API key permission. Initial allocation: $0 to GitHub-hosted public-repo standard Actions, $0 to S0 mock, $0 to native Markdown ferry. Keep remainder as reserve. If needed, propose a single capped API-helper pilot (suggested **$5 maximum**) only after provider availability, current exact model ID, price/cost evidence, storage/data policy and a key-enforced limit are confirmed with Mark. No permanent VM rental yet; choose it if hosted storage/timeout/debug interaction demonstrably becomes the gate. AllUrBase's existing $10 proxy budget stays separate.

**Cost honesty:** unavailable subscription usage or host billing = `null`, not free; caller collects telemetry *after* model response; record actual accepted result and rejected attempts; use deterministic receipt arithmetic.


**Budget clarification (Mark, 2026-10-27):** Puppf's earlier $50 initial discretionary envelope is separate from AllUrBase's existing money and Island's independent funding plans. Mark sees potential Puppf support of roughly **$500**, partly through donated work/cycles/services; Island might reach roughly **$1,000 by Christmas 2026**, but none of those are confirmed deposits, hard budgets, or spending authority. Do not co-mingle provider keys, receipts, pre-existing credit, donated capacity, or project cost reports. Each new paid provider still needs a named task and specific cap.

**Agent staffing correction (Mark, 2026-10-27):** Build support should have **at least two additional bounded helper-agent lanes** besides Codex's implementation lane, with a **reserve backup** and Z-desk coordination for small independent tasks. Do not add more than two simultaneously active outside helpers in the first trial. See the separate sandbox branch `experiment/puppf-two-helper-desk-v0`. This does not delay terminal-first M1; helpers are accountable for concrete source/log findings, not prose-only success claims.

## Immediate worker assignment: M0 before implementation

Codex (no metered helper yet): inspect current `main`, GitHub Actions history/run artifacts, existing `puppy-p0a/**` and acceptance tools. Report a factual matrix: **implemented, tested with fixtures, tested by actual runner, booted twice, missing**. Identify the *one* smallest change set required to make actual hosted P0a boot pass. Preserve the frozen packet bytes. Include run/job URLs and first failing log lines if available.

Then open one M1 branch and PR, implement only permitted P0a/CI evidence paths with bounded build/test cycles. Do not create a generic multi-agent platform first, do not rewrite the AllUrBase runner, and do not use M4 spending to replace missing deterministic tests.

### Evidence and review

- Keep `PUPPF-P0A-002` exact-byte SHA-256 `b0417934776c214ca3189c8822b85baf1e71fc262f66ada98bce2092f07c9c9b` frozen. A route-only addendum is not a license to change acceptance.
- Read platform job logs before declaring `BLOCKED`; differentiate workflow syntax/startup error from compile, network, QEMU, serial-check or resource failure.
- Attach `run-1/serial.log`, `run-2/serial.log`, per-run results, QEMU command, source/build manifest, timeouts, artifact SHA256 and byte sizes, test fixtures, working tree/commit refs and STOP/FAIL/PASS receipt.
- Any previous build attempts keep their own immutable receipts. No retrospective editing to make an old BLOCKED run successful.

## Material gathered from other projects

- **Castle:** small source packets, retry/STOP discipline, reviewer independence; not Castle's unrelated history.
- **AllUrBase/Eko:** human-readable failure bus and branch pickup; API proxies distinct from continuing chats; public science ledger separate from private notebook material; context limits and rate-limit handling.
- **Puppf:** separate P0a vs S0 acceptance; read-only GitHub-hosted CI preflight/build; no-model acceptance scripts; independent hash provenance.
- **Project Spiral and KolibriOS:** interesting later demo/test targets, not required for M1; adding them now would dilute the first product.
- **Team lessons:** give Z and Meraki room to disagree, favor simple Markdown communication, allow bounded optional model reviewers without a model roster or mandatory middle layer.

## Explicit questions for Mark (no blocker to M0)

**Resolved by Mark:** serial/terminal shell is the first usable milestone (2026-10-27). This is a deliberate decision, not a temporary unanswered preference. The near-term demo is interactive text, with a simple QEMU launcher; a graphical follow-up requires a separate scope/packet after terminal evidence exists.

**Remaining non-blocking defaults:** for optional M4 API calls share *public code/log excerpts only*, not private notebook material. Keep initial build artifacts as reviewable GitHub Actions artifacts; a public GitHub Release still needs Mark's separate publication approval.

## Transition to a fresh chat

Start a new ChatGPT conversation within the **Puppf project** and paste or link `docs/SPRINT_USABLE_001.md`. This preserves the working source of truth in GitHub and avoids treating one giant chat as the scheduler. Request "Meraki: execute M0 and draft a bounded M1 Codex handoff for the **terminal-first interactive serial shell**; do not require a GUI; keep merge, spend, publication gates with me." No assumption that creating this document has created a new ChatGPT conversation.

**Current approval:** This is an architecture proposal, not an execution, API spending, build or merge authorization. Review by Z/Mark before expanding implementation scope.
