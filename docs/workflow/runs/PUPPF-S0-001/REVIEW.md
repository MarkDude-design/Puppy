# Read-only review — S0 candidate

Native s0_review agent, shared workspace/tools and GPT-family context.
One implementation worker; reviewer made no edits. This is not Z's separate
Mistral-family review or a security certification.

Packet5847 bytes verified against independent handoff digest. Independent probes
covered exact256-byte wire and multibyte overflow, duplicate fields, boolean
integers, malformed/multiline/UTF8, rounds, STOP interruption, stale spools,
umask0 permissions, symlink/hardlink/FIFO refusal, append-prefix preservation
and fresh deterministic mocks.

Original concrete finding: replacing the root with a symlink let stop() create
STOP outside the run. Worker factored directory-identity validation and applied
it to stop(). Reviewer re-ran the original reproduction: now rejected with
spool/root directory changed; external STOP absent. Regression added.

Final core suite17/17 PASS. Reviewer disposition: no remaining blocker in the
sequential cooperative host-mock scope. No hostile-process concurrency,
tamperproof logging, model collaboration, guest integration or isolation claim.

Verification-wrapper/documentation follow-up review recorded separately in the
PR conversation if returned after this file. No new implementation work required
by the completed evidence.

## Final wrapper follow-up (supersedes initial17-test count)

Reviewer reproduced exit0 after zero discovered tests. Worker now requires a
parsed strictly-positive count before mocks. Added zero/missing-count regression.
Reviewer independently verified both reject with FAIL/exit1 and execute no mocks.
Final18/18 suite PASS; supplementary automated run is verification-002. Its two
transcripts have the same1068 bytes/hash as the original run. Two bounded repairs
used; implementation stops here for Z. No further runtime scope added.
