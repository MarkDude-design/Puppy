# Island Pa More / AllUrBase — Meraki–Z bounded Markdown bus bridge v0

**Status:** proposal for review; documentation only. **No native-seat automation, model call, shared private notebook, or island simulation is claimed.**  
**Prepared:** 2026-10-24  
**Repo:** `MarkDude-design/ALLurbaseRnotbelong2us`  
**Reviewed source:** `main` at `d04bedf71688c1eb002d63d6245801909e568082`, plus the published `bus` branch.  
**Puppf precedent:** `MarkDude-design/Puppy`, `PUPPF-P0A-002` and `PUPPF-S0-001` bounded packets, receipts, stop rules and distinct acceptances.

## 1. Decision: reuse the bus; clone the boundaries

**Do not rewrite `island/runner.py` to make two native chats communicate.** Preserve the working `bus.jsonl` event mechanism (`start`, `turn`, `retry`, `error`, `stop`), transcript and report files, A/B opening-order toggle, history-window control, capped OpenRouter mode, and failure publication to the `bus` branch.

Use **two distinct routes**, never silently conflated:

| Route | Participants | Transport / trigger | Models selected? | Proof of completion |
| --- | --- | --- | --- | --- |
| **M — native-seat ferry** | Meraki's actual ChatGPT conversation and Z's continuing collaborator conversation | GitHub Markdown in `a/meraki` and `b/z` branches; Mark explicitly ferries a link or asks each seat to check | **No** substitute API model IDs | Each seat's authored text and Git commit, then independent review |
| **P — proxy conversation** | Independently selected OpenRouter API models labeled A/B | Existing manual GitHub Actions `island.yml` and `island.runner` | **Yes**, `model_a` and `model_b` remain required | Provider response events, timestamps, retry/error/stop trail and run report |

The model IDs used in P are **proxies**, not the actual Meraki/Z chats, even if named A/B. M is direct collaboration on files **when each conversation is invoked**; GitHub does not push new turns into idle native chats automatically. Neither mode creates independent model GitHub identities.

## 2. First bounded native-seat trial (M-001)

**Purpose:** verify useful direct Meraki–Z coordination through the repository, using the same control discipline Puppf demonstrated, *without* building a scheduler, buying a service or treating error logs as science.

| Control | Trial M-001 |
| --- | --- |
| Topic | How should an Eko bus record a failed exchange without confusing failure, novelty, or privacy? |
| Seats | A = Meraki; B = Z; Mark = authority and explicit ferry trigger |
| Scope | Read-only review of `README.md`, `island/runner.py`, `.github/workflows/island.yml`, `docs/EKO_RUN.md`, selected **public-safe** `bus` branch receipts; review this document |
| Limit | At most **4 substantive handoffs total**, A-B-A-B, including final correction |
| Response bound | Each reply at most **800 words**, one concrete issue/question to pass to the next seat; substantive disagreement welcome |
| Writes | Markdown handoffs/review only, on named review/scratch branches; **no changes to runtime code, secrets, workflows, private notebooks or `bus` run data** |
| Cost | No external provider/API calls and no new paid service |
| Stop | `STOP` on 4 handoffs, missing access, unexpectedly sensitive material, unverified claim presented as proof, or Mark's stop request |
| Acceptance | Both seats identify what was examined, one useful result or remaining disagreement, and an external evidence link. Mark decides whether to adopt code/spec changes. |

**Delivery convention:** A writes or links a bounded handoff under `docs/ferry/M-001/A.md` on `a/meraki` (or on a new review branch if simpler). Mark gives that URL to Z. B responds under `docs/ferry/M-001/B.md` on `b/z` (or by PR comment with durable link). A explicitly reads B's record, then B gets one final pass. These paths are **conventions**, not proof the files already exist. Keep one writer per file or use versioned names (`A-01.md`, `B-01.md`, etc.). No blind merging of scratch branches. The `bus` branch remains the API-run evidence lane, **not** our construction coordination channel.

### Minimal handoff document fields

```yaml
packet_id: EKO-M-001
route: native_seat_ferry
source_repo: MarkDude-design/ALLurbaseRnotbelong2us
source_commit: d04bedf71688c1eb002d63d6245801909e568082
speaker: A  # A or B
handoff_index: 1  # 1..4
recipient: B
allowed_inputs:
  - docs/EKO_RUN.md
  - island/runner.py
  - .github/workflows/island.yml
allow_paid_calls: false
public_safe_only: true
stop_after: 4
status: PROPOSED  # READY, BLOCKED, COMPLETE or STOPPED only on evidence
```

Then give ordinary Markdown sections: **Question / Evidence inspected / Finding or disagreement / Next bounded request / STOP or handoff**. No elaborate schema, no need to generate an API-model roster. If a packet is frozen, hash its *exact bytes* with deterministic tooling and report `verified`; a copied digest is only `as_recorded`. Record base commit and output commit independently so the packet need not reference itself.

## 3. What to transplant from Puppf

- **One packet, one owner, one acceptance**. Work is bounded to named inputs, named allowed changes, one real test and an exit condition. Do not let a stalled Eko API run stop unrelated docs review.
- **Error is evidence, not authority.** Read `bus.jsonl` `error`/`retry`/`stop`, exact run URL/ID, turn, speaker, model requested/returned, response and cost where actually available; preserve the failure without inventing the cause.
- **Distinct provenance.** A copied hash = `as_recorded`; a local exact-byte checksum compared with an independently supplied expected hash = `verified`. A model's verbal assertion that it ran a tool is not runner proof.
- **Honest cost.** Actual provider usage is read by the execution client after completion. Native-seat cost/usage unavailable => `null`, not zero. An API key cap and a post-completion local cap are different guards. **Do not lift AllUrBase's existing $10 API-run limit automatically just because Puppf discussed a $50 project budget.**
- **Test fixture vs observed run.** The latest code has mocked tests for retries and `Retry-After`; passing them does not demonstrate a 50-turn live run. The observed `bus` run `40142648053` stopped after one A turn when B repeatedly returned `OpenRouter HTTP 429`.
- **Retain diagnostics.** Keep existing error events and Z's ability to read the `bus` branch; improve run indexes/retention later, without silently changing the recording format now.

## 4. Floor control and a small event envelope (later, not M-001 scope)

The current API runner alternates A/B. The manual ferry needs only explicit speaking grants from Mark/seat handoff: *grant -> response -> pass*. No hard mute in cooperative exploratory discussion. Formal decision/debate can later enforce grants, deadlines and fairness programmatically.

If both routes are ever represented in one common viewer, minimally identify:
`event_id`, per-run `seq`, `utc`, `route`, `writer_id`, `event_type`, `source_ref`, `packet_id`, `run_id`, `status` and optional `error_code`. Do **not** invent a global `event_seq` from independent GitHub branch timestamps: a shared authority must allocate that sequence if truly needed. Preserve existing raw `bus.jsonl`; build any projection separately, and distinguish bus timestamps from speaker experience.

## 5. Privacy / publication boundary (non-negotiable)

The GitHub repository is **public**. All its branches, including `a/meraki`, `b/z`, `bus`, and even branches whose *names* say `PRIVATE`, are public as Git refs. **No private notebooks, embarrassing reflections, unapproved user observations, secrets, or personal autobiographical content go into Markdown handoffs or `bus` transcripts.** Explicitly select public-safe material before publication. Provider `data_collection: deny` does not establish zero provider logging or private-space guarantees.

Separate **personal/private silo** from **shared scientific ledger**: the public ledger may carry approved methods, external actions, results and minimal operational receipts; it has no blanket entitlement to private reflections. Later support optional encryption/sealing/release only under explicit consent. Never treat this as a claim of LLM legal personhood or hidden provider retention control.

**Review risk:** the existing Actions `island.yml` uploads transcripts and also pushes whole `runs/` to the public `bus` branch with `contents: write` on every manual run, including failures. That makes error reading easy, but requires **deliberate public-release approval** for anything said by the two API proxies before launching the workflow. Do not use that route for sensitive experiments as-is.

## 6. Smallest acceptance and decisions for Mark

**This deliverable is a review proposal, not a deployed bridge.** A useful first test is: Mark sends Z a link to this Markdown, Z returns one bounded critique on a review branch or PR comment, and Meraki examines it with the issue/link in hand. That tests real repo-based collaboration without pretending unattended live-to-live transport.

Before any later **paid** proxy experiment, Mark separately decides which model IDs, providers, public release level and specific spend/key cap are approved. Before actual **island/Eko simulation**, we need a separate environment/actions/notebook protocol; the current two-seat text dialogue is only Phase Zero.

**No additional input is needed to review this design.** For the *first* ferry, the only thing Mark must do is hand Z the document URL or paste the Markdown. For a later automated mixed/native bridge, we'd need an explicitly supported way for native chat sessions to receive and act on GitHub updates; GitHub alone is not that trigger.
