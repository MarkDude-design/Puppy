# PUPPF-P0A-002 — optional Groq / GPT-OSS fresh-context review

**READ ONLY.** One review model, no web, no repository browsing, no programming, no delegation.

The human/calling client supplies the exact full final packet `docs/workflow/packets/PUPPF-P0A-002.json` and this repository's current `README.md`. The expected digest is `b0417934776c214ca3189c8822b85baf1e71fc262f66ada98bce2092f07c9c9b`. The reviewer **MUST record that digest as `as_recorded`**, unless independent deterministic tooling was actually used on the exact bytes. Do not claim hash verification by parroting the expected value.

Check testability, contradictions, unknowns that prevent dispatch, scope creep into P0b/P0c/S0/Chamber/networked HELLO, first-HELLO clock origin, echo-only failure fixture, and distinct run-1/run-2 evidence. Give only concrete findings, not praise or a restatement.

Output a **single JSON object** containing `task_id`, `recorded_packet_sha256`, `hash_provenance`, `result` (`PASS` or `NEEDS_REVISION`), and `findings` (array of objects with `severity`, `location`, `issue`, `suggested_fix`). Limit reply to 7000 characters.

**Do not include platform usage fields in the reviewer answer.** Mark or the calling client records exact console route/model ID, time, usage and cost metadata from the provider's response separately *afterward*. If absent, usage/cost remain `null`. Free tier selection is not proof of complete cost coverage; no $10 call-volume claim.

This is a manual ferry. It does not connect Codex and Z directly. The reviewer never authorizes execution/spend/merge or accepts its own findings; Z records dispositions, Mark decides acceptance.
