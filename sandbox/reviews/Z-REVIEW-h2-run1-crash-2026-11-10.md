# Z Review #10 — H2 Run 1 Crash Parse: Dead Kernel URL + Curator's Dropped Guard (2026-11-10)

Seat: Z (curator). Lane: sandbox/qmax-lab-20261110. Subject: H2 run 1 —
red at 31 seconds, exit 1, evidence artifact 873 bytes, no receipt spliced,
no branch commit. Owner pasted the run page; banked verbatim below.

## Run page as pasted by the owner (verbatim)

    Qmax H2 Discriminating Check
    qmax lab: Z-completed wiring — receipt self-publish, honest exit code… #1
    Triggered via push 18 minutes ago
    pushed 3effd2e sandbox/qmax-lab-20261110
    Status: Failure — Total duration 31s — Artifacts 1
    Annotations: 1 error and 1 warning
    h2-discrimination: Process completed with exit code 1.
    h2-discrimination: Node.js 20 is deprecated. The following actions target
    Node.js 20 but are being forced to run on Node.js 24: actions/checkout@v4,
    actions/upload-artifact@v4.
    Artifact: h2-evidence, 873 bytes, sha256:8e8751de6179e2115c911942176232157eaafea102cceac31a8a8916cd1ba5d9

## Root-cause chain (verified, not guessed)

1. The test-kernel URL is dead. QC's script fetched the Ubuntu jammy
   legacy-netboot installer kernel; that path returns Apache 404 today
   (verified live, 2026-11-10). URL rot under a chat-delivered design —
   the one class of staleness a code review cannot see.
2. wget -O left an EMPTY target file despite the failure, so the [ -f ]
   check accepted a zero-byte "kernel".
3. QEMU refused the empty kernel and exited 1 in well under a second.
4. The v1 Z-completion had DROPPED the seat's original set +e guard around
   exactly that QEMU call, so the exit hard-killed the script under set -e —
   before the summary was written, before the receipt splice, before publish.
   A red run with zero on-branch receipt: the exact outcome the failure-
   capture doctrine forbids.

The 873-byte artifact corroborates: only tiny log files — no ~10 MB kernel
ever landed in the evidence dir.

## Ownership

Third wiring-side miss today, and the second one mine. The seat's design was
sound; the URL rotted under it, and my "hardening" removed the very guard
that would have kept the failure legible. jejejeje — the curator keeps paying
tuition to the same runner. Banked without edits.

## Fixes applied in this commit (script v2)

- V1. Kernel source swapped to the Alpine netboot vmlinuz-lts
  (dl-cdn.alpinelinux.org, verified live 2026-11-10; lts kernel 6.12.115,
  refreshed Nov 5), with wget -L --tries=2 and a validation gate: the guest
  leg only runs if the downloaded file exceeds 2 MiB. A failed or empty
  download now yields an honest SKIPPED leg, never a fake run.
- V2. The set +e guard around the guest QEMU call restored — expected
  nonzero exits (QEMU error, timeout 124) are captured, not fatal.
- V3. An ERR trap now splices a failure entry into RECEIPT.md before any
  unexpected exit — this lane will not produce receiptless runs again.
- TIMEOUT raised 15 -> 30 s: single-vCPU pure TCG needs headroom to reach
  the first panic; the discriminator (host < 5s vs sustained guest with
  populated log) is unchanged, and the receipt's expected "Duration >= 5s"
  still holds.

## Notes

- The round-2 boundary probe workflow downloads the SAME dead jammy URL in
  its own "Download test kernel" step — the arm-time plan now includes the
  identical source swap + validation before that probe may fire.
- The Node 20 deprecation warning is GitHub runner platform noise; harmless
  here, worth a pin bump whenever the action versions are next touched.
- This push fires H2 run 2. Expected: both legs actually run for the first
  time — host leg fast-fail, guest leg panic-loop until the 30s timeout with
  a populated serial log, receipt self-published either way.
