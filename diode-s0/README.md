# S0: bounded host-file messaging mock

This exercises the frozen PUPPF-S0-001 packet using Python's standard library.
It is a **sequential, single-process cooperative mock**, not an enforced data
diode, security boundary, model conversation or guest integration.

Two private spools (`a_to_b`, `b_to_a`) carry alternating JSON messages. Every
wire message is one UTF-8 JSON line, at most256 bytes including the final LF.
The exact schema is v=0, round=1..6, kind=MESSAGE, text=string; duplicate/unknown
fields, boolean integers, embedded CR/LF, bad encoding and wrong rounds fail.
Each round has one message in each direction, then the next round. After12
messages the relay writes STOP and refuses further sends/receives.

Root/spools are0700, regular files0600. The caller umask is restored after
setup. Roots must be fresh: existing directories/symlinks are refused. Spool
leftovers block; messages are never overwritten or automatically retried.
Receive appends one canonical directional record to the existing transcript
using O_APPEND, then removes the consumed spool file. STOP is checked before
send, receive and transcript append. Manual STOP intentionally leaves any
queued message intact. Do not remove STOP and attempt to resume an instance.

Paths are operator-selected under a trusted parent on POSIX/Linux. Symlink,
hardlink, FIFO, directory-replacement and permission checks catch the covered
mistakes; they are **not** race-free protection against a hostile concurrent
process. Transcript records have no volatile timestamps and are not tamperproof.
A crash can leave a transcript/queue mismatch: retain that run and start fresh,
never replay it as if transactional delivery had been proved. No polling worker
is started; an empty/wrong/stalled spool is rejected synchronously.

## Run without the laptop or a rebuild

From the repo root, choosing a NEW directory whose parent exists:

```sh
python3 -B diode-s0/verify.py --evidence-dir /tmp/puppf-s0-review-001
```

This verifies the frozen packet hash, runs negative tests, executes two fresh
six-round mocks with seed41, and compares canonical transcripts byte-for-byte.
Results/logs stay in that directory. Reusing the path is refused. No sudo,
dependency installation, QEMU, network, external API or paid model is involved.
The fixed responders produce strings from a seeded PRNG and string reversal;
they do not interpret text as code, a shell command or an instruction.

For one mock alone:

```sh
python3 -B diode-s0/diode.py --run-dir /tmp/puppf-s0-mock-001
```

Runtime filesystem modes are tested on the actual temporary spools. Checked-in
evidence copies are readable repository records; Git does not preserve0600.

## Review and authority

The frozen packet is unchanged. Its older PENDING Mark/human-acceptance fields
are superseded for this generation and the next by the owner directions recorded
in Puppy issue15 comments7075115503/7075977777 and the2026-11-22 continuation
instruction. One implementation worker prepared this candidate; a separate
read-only GPT-family review found and verified a STOP-path fix. Z's Mistral-family
review is the next pipeline step. No pending human keyboard exercise is a gate.

Spool permissions/determinism passing does not pass P0a boot, authorize guest
transplant, demonstrate model collaboration or certify isolation. Existing
accepted images, launcher and source-build code are unchanged by this candidate.
