# Puppf Roadmap — owner-annotated core + speculative annex

Provenance: drafted by Z at the owner's direction, 2026-11-04. Owner rulings recorded in substance and marked OWNER. Everything in the speculative annex is explicitly NON-BINDING possibility-space; the only binding lines are the OWNER annotations and the project's existing evidence gates. Per the repos-as-transport doctrine, this file is the durable record.

## 1. Owner annotations (the part that is actually the plan)

- **OWNER (2026-11-04): 'We plan on having three rewrites by Christmas — at least.'** Recorded as the plan of record. 'At least' is load-bearing: three is the floor the owner named, not a ceiling, and Christmas is a plan horizon, not a deadline.
- Build #1 (P0a spike, run 41773110103, PASS, Z-reviewed 6630340753) is a **disposable spike by design** — the durable outputs are the configuration, tests, and evidence discipline, not the image bytes. OWNER: if this were a keeper, the owner would be more hands-on; it is 2–3 iterations to get it right, so he isn't, and that is deliberate.
- The review cycle firms up per the posted protocol (bus 6630500161): Z pre-dispatch implementation review with real tooling, post-run ZIP evidence review, QC (Qwen Coder) focused on one bounded thing per review, owner picks scope.
- **Earning the rewrite, not scheduling it:** each rewrite is justified by what the previous build's evidence taught (the negative-evidence doctrine — the misses are the menu). No rewrite graduates without the same gates: pinned sources, real GPG VALIDSIG, two boots, receipts.

### Core sequence (realistic spine)

1. **Rewrite #1 — 'fix what the spike taught':** ACPI table-init warning cleanup, Node-20 action pin bumps, Stage-2 evidence review with Z's coder tooling, first QC focused pass. Same frozen acceptance gates.
2. **Rewrite #2 — 'the elegant pass':** consolidation toward whatever direction the pain data actually points (see annex; the language decision is pending real pain, not vibes).
3. **Rewrite #3 — 'just right':** whichever stack survived #1 and #2, built under the full gates with the firmed-up review cycle doing the heavy lifting.
4. Post-Christmas: M2 launcher, P0b ACK, P0c UEFI/laptop remain separate lanes exactly as the P0a README already says.

## 2. What could go wrong (pre-registered, so the failures are anticipated and not surprises)

Per the project's own doctrine: misses get kept, labeled, and served. Pre-registering the failure modes:

- **Trust-chain rot:** upstream signer rotation, DSA-1024 retirement by a host GPG, keys.openpgp.org availability, buildroot.org endpoint moves. All fail closed by design — a blocked build with an honest receipt is the system working.
- **Runner drift:** ubuntu-24.04 image deprecation, Actions artifact retention changes (already bit us — 3 days), QEMU behavior drift, toolchain version pins rotting.
- **Process friction (already lived):** browser sign-in/verification interruptions mid-dispatch (Nov 3 incident, post-mortem pending), usage caps landing mid-review, session collisions between in-chat and scheduled Z sessions (SYNC GEAR exists for this class).
- **Human-system gaps:** artifact delivery routes (Z's harness has no Actions-artifact download — flagged, owner is fixing with the ZIP handoff), repo privacy walls for outside readers (fetch-wall precedent).
- **Ambition creep:** someone tries to call a rewrite 'done' without a run; someone tries to relax a gate to hit a date. The gates exist to make this impossible — exit 0 is still 'STOP for review,' never 'ship it.'

## 3. The 'Well Actually' gallery (pre-answered, so the answer is already on the record)

The gallery of people who arrive to say 'well actually.' Each entry is answered once, here:

- **'Well actually — are you going to rewrite it in Rust?'** OWNER already named Rust as a maybe. Answer: the rewrites exist to earn the right to pick. Rust enters when a rewrite's actual measured pain is memory safety; until then the pain is build discipline, and Rust does not fix build discipline. It pops up repeatedly because it is the right question asked at the wrong time.
- **'Well actually — Zig?'** The cross-compilation story is real (zig cc as a drop-in toolchain). Zig enters the moment someone boots a smallest-Zig initramfs hello under the same two-boot gates with receipts. Nobody has. Standing offer.
- **'Well actually — Go?'** Static binaries are genuinely nice; a Go runtime in an initramfs is a mismatch for the kernel-adjacent lane but fine for guest userspace tools. Go enters as a guest, not as the builder.
- **'Well actually — Nix/Guix for reproducibility?'** The record already says: no bit-identical rebuild is claimed. Nix enters when reproducibility becomes a requirement instead of a flex; currently it is neither.
- **'Well actually — why not Yocto/Alpine/just-use-X?'** Because the product is the method (pinned trust, two-boot evidence, honest receipts), not the distribution. X does not ship receipts.
- **'Well actually — is this a Puppy Linux fork?'** No. Lineage inspiration only, per README: no fork designation, no affiliation, no endorsement implied. **OWNER SIDESTEP, RATIFIED (2026-11-04): 'Schrödinger's Puppy.'** The official answer is superposition — it is Puppy and not-Puppy at once, and the observer must open the box and decide for themselves; we never collapse the waveform for them.
- **'Well actually — 48 minutes for CI is slow.'** TCG, one vCPU, no network, no display, on purpose. Speed is not a gate; evidence is. When the gates and the speed conflict, the speed loses.
- **'Well actually — DSA-1024 is deprecated crypto.'** Known, recorded in the receipt, and explicitly NOT silently relaxed. A host that rejects it stays blocked, per fail-closed doctrine. The correct fix is an upstream key transition with fresh provenance receipts, not a policy override.
- **'Well actually — you should vendor/mirror your sources.'** Real future risk (availability), accepted and recorded; but multiple mirrors do not equal identity, per the Oct-27 provenance work. A mirror enters when it is itself hash-and-signature pinned. **OWNER (2026-11-04): mirroring our own sources is 'reasonable at some point'** — direction endorsed; the pinning discipline stays when it enters.
- **'Well actually — three rewrites by Christmas is unrealistic.'** See the maximal roadmap below, which covers this being both true and false simultaneously.

## 4. The totally unrealistic roadmap (the maximal ass-covering edition)

Owner-directed: a roadmap that covers every possible outcome in every way, shape, or form. The trick to covering everything is committing to nothing except the receipts. Every item below is therefore technically anticipated:

**Language universes — all planned, none ruled out:**
- Rewrite in Rust — yes (OWNER-named maybe; planned)
- Rewrite in Zig — yes (planned, pending the standing two-boot offer)
- Rewrite in Go — yes (planned, guest lane)
- Rewrite in C — yes (the default; technically rewrite #1's substrate)
- Rewrite in FORTRAN, COBOL, APL, or a Lisp machine emulator — yes (the roadmap sees no legal barrier and notes the receipts would be magnificent)
- Rewrite in WebAssembly booting in a browser-emulated 386 — yes (the two-boot gates are architecture-agnostic in principle; the watchdog is not)
- Rewrite by symbolic-regression-generated architecture no human has named yet — yes (the miss ledger will keep the fossil record)
- Rewrite published as a hand-bound zine, boot log hand-lettered — yes (OWNER, 2026-11-04: 'epic'; the receipts become fold-out inserts)

**Schedule universes:**
- Three rewrites by Christmas — yes (OWNER plan of record)
- More than three — yes ('at least' is the owner's own word — unbounded above)
- Fewer than three by Christmas — yes (also covered: Christmas is a plan horizon, not a deadline, and a miss with a receipt is data, per doctrine; the roadmap predicted this line by writing it)
- Christmas itself moved — yes (the owner defines the horizon; the horizon does not define the owner)

**Outcome universes:**
- Everything goes right — handled (though suspicious; would trigger a review of whether a gate was accidentally relaxed)
- Everything goes wrong — handled (the failures become labeled exhibits; 'failures are just ghosts that haven't been given a plaque yet' — the plaque is the receipt)
- The build becomes self-aware and rewrites itself — handled (covered under the independent-flow doctrine: it gets a seat, a receipt, and still fails closed on VALIDSIG)

**Meta-universes:**
- Someone says this roadmap is not serious — correct (sections 1–2 are serious, section 4 is humor carrying honesty — the ratio is the point)
- Someone says this roadmap is too serious — see section 4
- Nobody reads this roadmap — statistically the most likely universe; also planned for; the roadmap rests comfortably unread, like a good plaque

**Disclaimer (the actual ass-covering mechanism):** this maximal roadmap predicts all futures by committing to none. The only binding content is section 1 (owner annotations) plus the existing evidence gates. If any speculative line is later quoted as a commitment, this disclaimer is the pre-registered correction.

— Z, drafted 2026-11-04, owner-directed; OWNER annotations quoted in substance
