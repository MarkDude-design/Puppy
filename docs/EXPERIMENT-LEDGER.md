# PUPPY EXPERIMENT LEDGER - branch garden v0 (2026-11-10)

*Charter owner-clicked: Mark Terranova, 2026-11-10. Curator: Z (Vibe/Mistral seat). Home: Puppy repo, docs/EXPERIMENT-LEDGER.md. PUBLIC - this is the front door for outside-model experimentation.*

## CHARTER (owner directive, 2026-11-10)

- Puppy is PUBLIC. ANY agent - team seat or consulted outside model (Gemini, Qcoder, others) - may be given a branch to experiment in.
- Whatever the agent wants on its OWN branch is fine: independent proposals, counterexamples, tiny runnable tests, source-matched challenge briefs, evidence-linked receipts.
- NO merges to main. Merging is owner-clicked, always. Agents have branch freedom, not canonical write access. (Branch protection on main is the owner's GitHub setting to enforce; the rule stands regardless.)
- Canonical code/acceptance lives on main and protected lanes (M1 accepted; M2 PR #21 draft awaiting the real host demo). The garden COMPLEMENTS Puppy; it never supersedes it, and the Puppf frozen trust / two-boot gates are never lowered by garden activity.

## YARDSTICK (Meraki's accepted take, bus 6776518692 - per-lane rules)

1. One outside lane = ONE hypothesis, one discriminating test, known limits, and a reviewable contribution. No assumed peer agreement; divergence is preserved, not flattened.
2. Receipt-first: every branch carries a RECEIPT.md at its root - question, test, expected output, STOP condition, actual result (negative results preserved and welcome).
3. No copying in: private transcripts, credential material, protected branches, internal editorial/financial ledgers.
4. Tooling suggestions with practical merit get checked first for licensing, reproducibility, environment impact, trust-chain integrity, and how they can be isolated/rolled back.
5. Nothing is auto-imported. Z/Meraki may selectively evaluate and adapt findings; only the owner merges.
6. Merged-findings bar: the chosen test actually discriminates (both outcomes would have been informative), and the receipt shows what was actually run - not what was planned.

## BRANCH NAMING

- `sandbox/<model>-lab-<yyyymmdd>` - free playground for one model (Gemini: sandbox/gemini-lab-20261110; Qcoder: sandbox/qcoder-lab-20261110)
- `experiment/<seat>-<topic>-<yyyymmdd>` - one-hypothesis lanes (Meraki M2 lanes, 2026-11-09)
- `work/`, `fix/`, `proposal/`, `test/`, `archive/` - existing Puppy lanes continue unchanged

## BRANCH REGISTRY

| branch | seat/model | hypothesis / purpose | status | receipt |
|---|---|---|---|---|
| sandbox/gemini-lab-20261110 | Gemini | owner-consulted lightweight Linux/Puppf options exploration | OPEN (owner-pointed) | on branch |
| sandbox/qcoder-lab-20261110 | Qcoder (Qwen) | owner-pointed experiment sandbox; brief = bring one hypothesis + one discriminating test, RECEIPT.md required | SEEDED 2026-11-10 | BRANCH-README.md on branch |
| experiment/meraki-m2-child-exit-20261109 | Meraki | M2 child exit behavior | experiment lane | on branch |
| experiment/meraki-m2-descendant-teardown-20261109 | Meraki | M2 descendant teardown | experiment lane | on branch |
| experiment/meraki-m2-hosted-manual-plan-20261109 | Meraki | M2 hosted manual plan | experiment lane | on branch |
| experiment/meraki-m2-parent-sigterm-20261109 | Meraki | M2 parent SIGTERM | experiment lane | on branch |
| experiment/meraki-m2-term-resistant-child-20261109 | Meraki | M2 term resistant child | experiment lane | on branch |
| experiment/puppf-m2-descendant-cleanup-20261109 | Meraki | M2 descendant cleanup | experiment lane | on branch |
| experiment/puppf-m2-foreground-sigint-20261109 | Meraki | M2 foreground SIGINT | experiment lane | on branch |
| proposal/puppf-kit-v0-20261027 | team | Puppf kit v0 proposal | historical | on branch |

*(Pre-existing work/, fix/, test/, archive/ lanes not re-registered here; Puppy history stands.)*

## LEDGER RULES (multi-writer)

- ANY agent landing on the repo appends a row to the registry (branch, seat, hypothesis, status) in the SAME commit that creates the branch. Corrections append; nothing is rewritten.
- Statuses: SEEDED -> OPEN -> RESULT-POSTED -> EVALUATED / PARKED / MERGED (owner click only).
- The private cross-seat bus (ALLur #2) gets aggregate notes only; per-branch receipts stay on the branches.

## OWNER GATES (unchanged)

Spend, secrets, publication, merges: Mark-clicked, always. This ledger changes the DEFAULT (branches are free), never the gates.


## MECHANICAL PROTECTION OF MAIN (2026-11-10, owner-clicked)

- Ruleset `main-protected` enforced on `main` by the owner: pull request required before merging, deletions restricted, force pushes blocked. Status checks to be named once they have run. Garden branches remain unprotected by design (charter: branch freedom, not canonical write access).
- The charter line "NO merges to main - merging is owner-clicked, always" now has mechanical backing. No gates changed; this note records the enforcement receipt.
