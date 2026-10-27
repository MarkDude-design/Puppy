# Two-helper desk: reproducible offline test receipt

**Observed:** 2026-10-27. **Scope:** PR #14, offline only. This receipt does not demonstrate native subagent/paid API availability, actual Z review, reserve network failover, CI integration or P0a QEMU boot.

## Environment and source

- Python: `3.13.5`
- Execution: local isolated Python environment used by Meraki during review (not GitHub-hosted Actions and not Codex).
- Command: `python3 -m unittest discover -s tests/agent_desk -v`
- Output: `Ran 21 tests in 2.885s`, `OK`, **process exit code 0**.
- Exact files reconstructed from GitHub PR head and **Git blob SHA matched** against stored GitHub files before executing:
  - `tools/agent_desk/desk.py`: **8020 bytes**, git blob SHA `463e984d4989b0f8a2b7ea03fbd822baa147cc42`
  - `tests/agent_desk/test_desk.py`: **6259 bytes**, git blob SHA `5f597c17917b5544e305a29697430acc17af13b8`
  - `docs/agent-desk/queue.json`: **1965 bytes**, git blob SHA `ebb5257b481bcc02febcd4cfdce454c586af0197`
- Original prior PR revision at `456a6d5e5bf6a78bc42e8429a590086c477d2b42` also passed **17/17** offline tests (matching its then-current blob hashes) before backup correction.

## Important issue found and corrected in this branch

The previous `simulate_failover` would mark `R` as replacing H2 but leave R's generic task question and sparse inputs intact. A handoff could therefore widen/change the problem while claiming to be a transparent replacement.

- Simulation now **copies the blocked H1/H2 task's exact question, inputs, word cap and read-only flag** to R.
- Validation requires a named `replaces` target (`H1` or `H2`) that is **actually BLOCKED**, with matching inherited task fields.
- Four negative/proof tests were added to reject a missing/wrong target or altered question and verify exact inheritance; **21/21** pass.

## What the tests establish, and do not

PASS: planning queue `2 active + 1 standby`; accidental third planned helper rejection; duplicate IDs/slots; false zero-cost rejection; paid call denied; invalid model/provider assignment rejection; offline route-combo preview; simulated reserve replacement with bounded inheritance.

NOT TESTED: real agent invocation, model identity, provider billing, GitHub CI, log retrieval from P0a Actions run #10, Z's actual disposition, any real QEMU serial output. Queue's `READY` state is **planning**, not live dispatch authorization.

**Next:** Z reviews this changed PR head and receipt; Codex inspects the real earliest failing P0a Actions line in [M0 issue #13](https://github.com/MarkDude-design/Puppy/issues/13). A first live two-helper trial requires actual output/provenance from two separate helper routes, with a reserve only when one blocks. Mark retains spending, merge, execution and acceptance gates.
