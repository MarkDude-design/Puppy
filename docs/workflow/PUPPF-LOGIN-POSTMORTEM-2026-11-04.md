# Puppf login interruption: post-mortem

Written November 4 after build #11 succeeded. Scope: the path from an approved
source repair to one actual hosted build. This is an evidence-based operational
review; no product bug or authentication root cause has been established.

## Outcome

PR #19 merged at `e0b5e0e4b206c30ca3bcbfcf08c764a2acf19808`. Mark approved one
build. After access recovery, that build started November 3 at 8:25 p.m. PST and
finished successfully at 9:13 p.m. PST. Both QEMU boot checks passed. Z reviewed
the run/code/digest, then Mark accepted M1 and authorized M2 on November 4.
No duplicate build was dispatched by this conversation or its documented phone
recovery handoff. The preserved build artifact is the result, not the login UI.

## What the record establishes

| Observation | What remains unknown |
| --- | --- |
| Connected GitHub operations could merge and read Actions, but exposed no fresh dispatch action. | Whether another future connector version supplies dispatch; do not generalize this to all GitHub access. |
| The cloud browser was signed out while connector access worked. | Why it was signed out; the usage reset causing it is unproven. |
| One browser-auth guidance read was stopped by automatic approval review reporting a usage limit; the normal call later succeeded. | Reset propagation/accounting behavior. This was a review-service failure, not an unsafe-action verdict. |
| Mark reported Android kept receiving replies while the usage/Get Pro notice obstructed the view and blocked composer submission; laptop continuation worked. | App, account-state, cache, or service cause. No controlled client comparison was run. |
| Google sign-in advanced through multiple phone matching challenges, followed by GitHub's emailed device check. | Why another matching challenge appeared; no resend/restart action was observed in those particular model-controlled steps. |
| Secure code entry returned declined and was paused. Later password sign-in visibly failed; manual sign-in ultimately reached the signed-in workflow page. | A declined result alone does not identify user intent or a client failure. No credential values are in this report. |
| An unsupported workflow-specific read URL failed; the repository Actions-runs endpoint worked. | No authentication failure can be inferred from that URL-validator rejection. |

Mark's identity joke was conversational humor, not a proposed replacement for
GitHub authentication. Authorization to build and the site's authentication
requirements are separate facts.

## What made recovery expensive

The execution route had an avoidable surprise: successful connector writes were
treated as encouraging evidence that launch was close, before the fresh-dispatch
capability gap and separate browser session were made concrete. Repeated thread
transitions then required re-establishing both project state and live access.
The chat could retain the work while its client or authentication surface was
blocked; calling all of these a cold start obscured which problem needed fixing.

The original incident log and the phone-thread checkpoint prevented a worse
failure: rerunning old failed source, double dispatching, reusing expired
verification numbers, or losing the already granted one-build authorization.
The model stopped on declined authentication rather than silently retrying.
Manual sign-in finally worked; that does not prove it was the only viable route.

## Changes to our working method

1. **Check the action route first.** Establish whether the connector supports
   the exact mutation and whether a separate authenticated browser is required
   before announcing a launch is imminent.
2. **Warm start = restore access/session.** Carry run URL/status, source commit,
   authorization scope, current owner, next action, and a live-session caveat.
   Inspect current state; never preserve codes, cookies, passwords, or matching
   numbers in a handoff.
3. **Cold start = reconstruct continuity.** Recover decisions, reasons, voice,
   unfinished ideas and source horizons separately from the login checklist.
   Mark's broader notebook project remains a separate piece of work.
4. **One owner, one dispatch.** Immediately post the new run URL and consumed
   authorization. Other threads follow the run rather than starting another.
5. **Local use should stay local.** M2 takes an already downloaded, pinned ZIP;
   launching it should require neither a new GitHub login nor a rebuild.
6. **Use explicit checkpoints.** Signed in, dispatched, building, boot checks
   passed, independently reviewed, owner accepted are distinct states. A green
   job is not automatically a release, and a retained chat is not a live session.

## Source trail

- [Original interruption log](https://github.com/MarkDude-design/Puppy/issues/15#issuecomment-6619049148)
- [Phone recovery checkpoint](https://github.com/MarkDude-design/Puppy/issues/15#issuecomment-6619466426)
- [Actual launch receipt](https://github.com/MarkDude-design/Puppy/issues/15#issuecomment-6622530515)
- [Run #11](https://github.com/MarkDude-design/Puppy/actions/runs/41773110103)
- [Artifact inspection](https://github.com/MarkDude-design/Puppy/issues/15#issuecomment-6630237332)
- [Z review and its limits](https://github.com/MarkDude-design/Puppy/issues/15#issuecomment-6630340753)
- [Mark acceptance and M2 authorization](https://github.com/MarkDude-design/Puppy/issues/15#issuecomment-6630735320)

These support the observed sequence and fixes above. They do not establish an
Android root cause, prove that a reset signed out a browser, or predict that a
new thread will inherit another thread's authenticated session.
