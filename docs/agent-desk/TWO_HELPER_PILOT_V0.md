# Puppf Two-Helper Desk v0 — experimental lane

**Status:** proposed, non-executing coordination layer. Separate from the terminal-first build in main and from [usable-system sprint PR #12](https://github.com/MarkDude-design/Puppy/pull/12). This is deliberately not a new agent platform, shared API key, or paid dispatch.

## Decision

**Codex implements. At least two other callable agent lanes support the build**, on small, distinguishable tasks before we add a third active helper. Z is the continuing collaborator/coordinator and may use a manual GitHub ferry if the agent service isn't accessible. Meraki owns technical routing and checks evidence; Mark controls spending, merges and acceptance. The two helper roles are **not** replaced by the Z/Meraki reviews.

| Slot | First small job | Suitable execution route | Permitted output |
|---|---|---|---|
| H1 — **diff** | Check the exact failure snippet, version pins and acceptance claims for stale assumptions, unsupported absolutes, bad arithmetic | Optional API-hosted Mistral / native Codex subagent if available; otherwise Z ferries a bounded review | Evidence-linked findings and ONE small suggested fix, **no write** |
| H2 — **triage** | Independently identify the earliest *observed* failing CI/build step and the smallest falsifiable next test | Groq or another independently invoked model / native subagent; if inaccessible, manual review | Evidence-linked hypothesis + first discriminating test, **no write** |
| R — **reserve** | Replacement only if an active helper is inaccessible, rate-limited or blocked; no third simultaneous lane | Different provider or alternate native context, as actually available | Same named task and bounds; record substitution; **no write** |

"Two active" refers to **two outside helper tasks**, not two substitute personalities with the same context, and not two API IDs pretending to be the continuing Meraki/Z seats. A helper is not considered *used* until its actual output is recorded. Reserve is **standby**, not automatic expansion; one helper/one task/one receipt.

**Default starting configuration:** H1 + H2 are assigned **different kinds of checks** on the same public-safe P0a failing run. Their initial input snippets should be source-matched but reviews independently elicited; do not show a helper the other's conclusion before it reports. Codex consumes both reports but does not get to self-certify implementation. Z records agreement/disagreement and gives a small next action; Meraki decides architecture in-frame. Mark retains merge, billing and acceptance.

## Lightweight desk workflow

1. **Z-desk intake:** record `task_id`, source **commit**, public-safe log or test path, one question, expected check, max words, and what must remain unchanged. Use `docs/agent-desk/queue.json` as a small, offline-validated queue example—not a server.
2. **Bounded handoff:** route task to H1 and H2, using *either* native seat manually, native Codex subagents (only if actually supported), *or* explicit API invocation with approved provider/model and cost. Do not assume native chats receive pushes automatically. No default model IDs or credentials.
3. **Parallelism cap:** at most two active external helper slots. When one blocks, Z can mark it BLOCKED, record the cause and choose reserve R **as replacement**, not a third parallel helper.
4. **First receipts:** preserve returned text verbatim, tool-observed model/provider, reviewer identity if available, error/429 and retry events, caller-side usage. Cost without telemetry is `null`, never fake `0`. Keep known subtotal separate from total/coverage.
5. **Decision:** Z desk summarizes areas of agreement, any material dissent, and next *one* Codex-sized action; Meraki checks the scope and evidence. Codex opens an ordinary implementation PR and attaches real test receipts. Mark decides merge.
6. **STOP:** any missing input, leak risk, uncertain authorization, first completed review round, provider/spend cap, or explicitly recorded halt. Rerunning failures without new evidence is not progress.

## Shared tools, without copying the entire other project

- AllUrBase Z Desk already has callable `diff` and `man` modes, rate-limit receipts, provider model identity and a public `bus` evidence lane: [current source](https://github.com/MarkDude-design/ALLurbaseRnotbelong2us/blob/main/island/z_desk.py), [workflow](https://github.com/MarkDude-design/ALLurbaseRnotbelong2us/blob/main/.github/workflows/z-desk.yml). Reuse its *method*. Do **not** transfer its funded key, standing spending orders, default model IDs, public-run publication, or project budget.
- Puppf KIT already has a separate [consult-contract proposal](https://github.com/MarkDude-design/Puppy/blob/proposal/puppf-kit-v0-20261027/docs/kit/CONSULT_CONTRACT_V0.md) and a hashed [issue #11 mailbox](https://github.com/MarkDude-design/Puppy/issues/11). Reconcile them before building a live connector. Don't accidentally append to #11 without following its hash-previous byte contract.
- Puppf's frozen `PUPPF-P0A-002` source packet and real QEMU double-boot acceptance **do not change**. The helper desk cannot turn fixture passes into real boot passes.
- The public GitHub branch is NOT a private notebook. Never put credentials, customer data, private journals or personal observations in a consultation. A simple string secret filter is not proof of safe disclosure.

## Experiment knobs, *not* a giant model roster

Pilot A: H1 detail-review + H2 independent CI failure triage; compare findings. Pilot B after recording A: swap the helper **routes** while keeping identical task criteria; preserve provider/model changes as confounds. Pilot C: intentionally mark H2 BLOCKED and exercise reserve R **instead**; inspect receipts and continuity. Avoid a hardcoded default list of model versions. Different API providers/models can be substituted only by an approved dispatch choice.

Native Meraki↔Z messages remain a separate manual ferry. A Z desk can run entirely with Markdown and the offline queue validator if no API helper can be reached; don't claim two callable agents were contacted unless they actually responded.

## Minimal initial tasks

- **H1:** Given the most recent P0a Actions failure, compare the first failing line against frozen packet acceptance and test fixtures; return up to three specific discrepancies, with source lines. Stop.
- **H2:** From the *same* run/job ID, independently give one hypothesis and one check distinguishing infrastructure failure from guest implementation failure; include exact quoted log lines, no unwarranted architecture change. Stop.
- **Codex after Z's synthesis:** one bounded edit or one truthful BLOCKED receipt; not a bus rewrite.
- **Reserve drill:** dry-run an unavailable H2 and a reserve replacement via `tools/agent_desk/desk.py`; this emits no API calls.

## Budget and contributions: separate ledgers

| Project/lane | Status | Discretionary authority |
|---|---|---|
| **Puppf / Puppy** | Earlier **$50** working envelope; Mark says larger build support could be around **$500**, partly covered by other people / donated cycles / services | **$500 is a possible future scale**, not money spent, pledged, received, or blanket API authority. Per-service authorization still required. |
| **AllUrBase** | Existing independent funds/credit and separate GAS/desk arrangements | No access or transfer to Puppf; preserve its own receipts, limits and approvals. |
| **Island** | Separate funding envisioned; **perhaps $1,000 by Christmas 2026, maybe more** | Forecast/possibility, not cash in hand or authorization; never silently fund Puppf or AllUrBase from it. |

Track any donated GPU/VM/cycles as **in-kind** (supplier, useful hours, limits, source/date, estimated market value only if documented). Do not treat promised cycles as available capacity. Ask Mark for a specific paid-service approval (amount, provider, cap, task ID) before calling it. Distinguish project-wide envelope from an actual provider key hard cap; local post-response soft cap cannot prevent a final completion from exceeding it.

## What this branch does / does not do

This branch proposes a small **offline queue validator** and sample H1/H2/R task descriptions, testable without an API key or model selection. It does not instantiate two remote models, create a scheduler, share secrets, start a QEMU build or authorize any charges. Review of this branch is independent of M1 product acceptance.

**Acceptance for v0:** validate a 2-active/1-reserve queue, reject accidental 3-active tasks or duplicate IDs, report safe reasons for blocked/standby swaps, run tests, and let Z hand off real prompts using the existing GitHub ferry. First *actual* multi-agent success still requires two separately observable helper receipts, not just schema tests.
