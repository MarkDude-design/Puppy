# Puppf Dispatch and Review — finalized packet candidates (2026-10-21)

## Clean-base rule

Review and merge **workflow baseline PR #3 before this stacked packet PR**. Its exact pinned source is:
`15e458aa99b3f1345d9120b476f8c23301a2e235`.

This packet branch descends from that commit; no packet contains the commit that carries itself. The implementation worker must also record the exact checkout/start commit, which will be the dispatch branch head or a subsequently approved task branch. Do not treat the baseline commit alone as the implementation checkout.

## Final packets — exact bytes

| Track | Packet | SHA-256 |
| --- | --- | --- |
| P0a boot | `docs/workflow/packets/PUPPF-P0A-002.json` | `b0417934776c214ca3189c8822b85baf1e71fc262f66ada98bce2092f07c9c9b` |
| S0 host diode | `docs/workflow/packets/PUPPF-S0-001.json` | `7f80843cb214413532c13258e1ca29c093e82d48a8d09c078289175f6b46a611` |

Before worker dispatch, deterministic tooling must recalculate packet SHA-256 on exact raw bytes and compare to the digest **independently delivered here**. A model reviewer who merely repeats these digests records `as_recorded`, not `verified`. If anyone changes any packet byte, version and re-hash it, then amend the handoff. No silent patch to a dispatched packet.

```sh
git rev-parse HEAD
python3 -m unittest discover -s tests/workflow -v
python3 tools/workflow/check_packet.py docs/workflow/packets/PUPPF-P0A-002.json b0417934776c214ca3189c8822b85baf1e71fc262f66ada98bce2092f07c9c9b
python3 tools/workflow/check_packet.py docs/workflow/packets/PUPPF-S0-001.json 7f80843cb214413532c13258e1ca29c093e82d48a8d09c078289175f6b46a611
```

### First P0a boot

- Buildroot 2026.08 is a candidate backend, **not** a release designation or a pinned verified tarball digest yet. Verify its official current archive and signature/checksum before build; record host/toolchain versions, archive digests and config.
- Host needs Linux build tools and QEMU; dependencies have not been checked/installed in this repo. `-nic none` and absence of host-device access are runtime requirements.
- First heartbeat `uptime_s` is **absolute guest kernel monotonic uptime**, seconds read from `/proc/uptime`, *not* time since `/init`. First record requires `uptime_s <=15`. The older 240-second span floor is explicitly retired.
- Test a freshly generated shell token's **output line**; terminal command echo does not count. Echo-only fixture must fail.
- Run twice, preserving `run-1/serial.log`, `run-1/test-results.json`, `run-2/serial.log`, `run-2/test-results.json`; artifacts and hashes must match between boots.
- No guest model/runtime, network, security-containment claim, media write, or P0b ACK.

### Host diode

Host-only standard-library mock, no QEMU, no model API, no paid calls. Two spools with permissions, one-line <=256B JSON, append-only transcript, STOP, six-round cap, fixed seeds and twice-run byte-for-byte transcript comparison. A guest transplant waits for a third, separately approved packet.

## Model lane and receipt rules

Codex is the worker **role**. Record the actual model requested, the identity observed and the identity evidence separately, or `null`. Model answer self-reported usage is not platform telemetry. Only Mark or the calling client attaches response metadata afterward. Keep unknown cost/usage `null`.

Z-the-collaborator owns routine review and disposition. The replaceable OpenRouter Mistral module is an optional digest/summarizer, not Z. Groq may give a fresh-context read-only review, never self-verify or authorize acceptance. Astra reviews material ambiguity and authority/security claims. No automatic live bridge connects these sessions.

Cost totals are computed deterministically with `tools/workflow/cost_report.py` from receipts, cost coverage, reviewer decisions and Mark's accepted-result decision. The OR module can summarize script output, but not manufacture the underlying numbers.

**Separate gates remaining:** Z's dispositions, Mark's explicit worker-dispatch/execution authorization, host dependency installation decision, and numeric cap or documented budget authority *before any metered external-model call*. Mark retains merge, public posture and final acceptance.

## Evidence status

Packet SHA companion consistency checked after GitHub writes using deterministic digest calculation. Fixture suite not yet executed on a host. No QEMU boot, model call, host deps install, guest media write, or expense is claimed by this handoff. The Castle PR #7 pilot remains untouched.
