# Puppf first handoff

**Candidate branch:** `work/puppf-bootstrap-001` (pre-implementation workflow only). Mark retains merge and acceptance.

## Checks before dispatch

```sh
git rev-parse HEAD
python3 -m unittest discover -s tests/workflow -v
python3 tools/workflow/check_packet.py docs/workflow/packets/PUPPF-P0A-001.json 40ae0a3c3e53dc854a19f763b4c9bb82949f851a258b830ed0a05c993a72ab1c
python3 tools/workflow/check_packet.py docs/workflow/packets/PUPPF-S0-001.json 125581e30ab7a7f4bb54e04a6b6b1663c22fac8cb8df564bcd2a54f3c5835973
```

These hashes are tied to packet **version 1**; verify against trusted handoff, not just adjacent `.sha256` files. Packet contents are proposals until Mark authorizes dispatch and the exact source/working branch commit is recorded in the receipt.

### Track A host preflight (no install by this document)

Inspect with `uname -a`, `qemu-system-x86_64 --version`, `gcc --version`, `make --version`, and `command -v` for each required Buildroot host tool. See the [2026.08 manual system requirements](https://buildroot.buildroot.org/downloads/manual/manual.html#requirement-mandatory). Required Buildroot tools include `which sed make binutils gcc g++ bash patch gzip bzip2 perl tar cpio unzip rsync file bc find awk wget`. Linux kernel configurations may additionally need `flex` and `bison`. QEMU is required for this experiment even though it is not a Buildroot host prerequisite.

Use the [Buildroot release page](https://buildroot.org/download.html) for 2026.08 tarball plus signature. Verify downloaded archive with known trusted digest or signature (and record actual digest). Do not put a guessed checksum in the config. Pin dependent kernel/BusyBox sources within Buildroot and record exact versions. Preserve downloads cache outside repository.

### Proposed Codex order

1. Worker A / P0a: preflight, build, actual serial shell and heartbeat, twice boot, evidence receipt. Stop after first completed receipt, passing or BLOCKED; no automatic merge.
2. Worker B / S0: independent host-only mock build and two-run transcript proof. Host deps or failure of P0a do **not** gate S0. Worker is still **one packet at a time**, with distinct branch/receipt.
3. Z performs ordinary-result review, Astra handles ambiguity/authority/security exceptions, Meraki checks evidence, Mark accepts and merges.
4. Later third packet for the guest transplant **only after both independent first acceptances**.

A passing fixture is not guest evidence. A passing boot is not containment evidence. The diode never carries its own construction coordination.

**Open gates:** Mark must authorize actual implementation/execution and any host dependency installation; Z/Codex worker assignment to be recorded; any metered API run needs a numeric cap or existing-budget authorization. This bootstrap makes no claim of successful build, VM run, or saved cost.
