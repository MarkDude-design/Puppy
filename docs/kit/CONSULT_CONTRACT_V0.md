# KIT consult contract v0 — Mistral, Groq, native subagents and other helpers

**Status:** interface proposal, not a deployed service. No new API call/authorization is created by this text.

## Two distinct ways to ask for help

**Route N — native-seat ferry (default):** KIT writes a short public-safe GitHub question pinned to a repo commit; Meraki or the continuing Z/Mistral collaborator reads it on an actual invocation and writes an attributable reply. Puppy issue #11 has the existing hashed mailbox, but follow its exact byte/hash-prev chain to append. This does **not** automatically wake the other chat and does not require choosing an OpenRouter model ID.

**Route A — agent/model consultation (optional):** KIT may delegate read-only independent questions to native Codex subagents if the active Codex host actually exposes those capabilities. Or Z can use its own Groq lane or AllUrBase Z Desk diff/man API runner. External model proxies are not the human-established Meraki and Z seats; resolve and record actual requested/observed models. Do not copy a key to Puppf. A review from a separate context is not proof of different model weights.

## Minimal bounded input packet

- task_id and parent_task_id (or null)
- originating seat and target seat/agent; route: native_ferry, native_subagent, or external_consult
- source repository and **actual observed commit SHA**
- one explicit question with testable review criteria
- a few named allowed evidence paths/URLs, with immutable refs and content SHA256 when measured; never give an inaccessible reference and call it evidence
- named read/write limits (review-only means no edits), excluded areas, privacy/publication classification
- maximum response length, stop rule and parent task ID
- external API: paid-call allowance **false unless explicitly authorized**; specific provider/model and a caller-enforced per-call cost ceiling
- output destination for the child/consult receipt

A Markdown note is enough for first use. A JSON schema and cryptographic packet hash can follow only when a tool dispatch genuinely requires exact bytes; hash verifies content integrity, not identity or independence.

## Expected output and parent relay

Reviewer returns COMPLETE, BLOCKED or NEEDS_CLARITY, with exact question answered, material findings, evidence links, uncertainty, one discriminating next check, actual role/model identity if observed, and a raw response reference/hash when available. The caller captures actual provider usage/cost separately after the response; absent fields remain null.

The **parent** owns one relay receipt, citing the unedited child output. Z may add a separate disposition; Groq under Z should first inspect independent evidence before seeing Z's preferred verdict where possible. An unresolved meaningful dissent stays visible. A model answer is not a verification that a build/log/test actually ran.

## Cost and publication rails

The Puppf project ceiling is $50 but an individual external call still needs a named task and approved budget route. AllUrBase Z Desk has its **own** pre-existing soft ceiling and public bus publication; neither its OpenRouter secret nor its budget automatically transfers to Puppf.

Never submit source tokens, private notebooks, personal records, proprietary conversations, account secrets or sensitive logs to a public issue, public Actions input or public bus transcript. A simple secret-pattern filter is a useful rejection check but not a guarantee of safety. An HTTP error/retry event stays evidence; no loop retries indefinitely or silently changes provider.

## Trial after G0

One question only: given the actual latest P0a failing step and source snapshot, which **one** smallest change could produce a falsifiable improvement? Z reviews directly first, using native ferry. Invoke a specialist only when independent review is likely to change the work. Stop at one receipt; KIT does not self-approve or merge.
