# PUPPF-M1-SOURCE-003 — source-authentication and extraction repair

Date: 2026-11-03. Base: `394a6ae4b4ca925611641d846d2c6699df7b663f`.
Status: SOURCE AUTHENTICATED / EXTRACTION VERIFIED / BUILD AND BOOTS NOT RUN.

Mark directed this work window to Puppf with Astra. Meraki implemented one
unmerged repair for issue #15, extending the original key-fetch-only proposal to
the complete required signed-manifest/archive binding. An additional extraction
blocker was found by actually running that path and fixed in the same source
boundary. This does not change the frozen P0a packet, backend version, guest
acceptance, workflow dispatch rules, spending or release authority.

## What changed and why

1. The old key pin came from a Git tag. The archive's clearsigned checksum manifest
   uses a different upstream key. The public release certificate is now an exact
   byte-pinned fixture, with the tag signer retained separately.
2. The old verifier used the detached-signature invocation on a clearsigned
   checksum document. The new helper authenticates the manifest itself with GPG,
   requires successful command exit plus dedicated exact-signer status, then
   binds one exact-basename SHA256 to the downloaded archive and its reviewed pin.
3. Actual source extraction exposed the upstream guest-skeleton symlink
   `/etc/init.d/sysv-rcs`, which Python's ordinary data filter rejects. The new
   extractor preserves regular-file filtering, preflights the entire inventory,
   and creates all symlinks last. That one absolute-link exception requires exact
   path, target and authenticated archive bytes. No blanket trusted extraction
   flag or weakened signature check was added.

The public-only GPG flow uses an isolated dearmored ring, preserving normal GPG
key-validity checks. It does not ignore the observed gpg-agent import error, run
an agent daemon, switch to gpgv, or supply weak-algorithm policy overrides.

## Actual evidence

- Meraki freshly fetched the official key, manifest and 6,115,596-byte archive;
  the new helper and full `Run.verify_release` path authenticated and extracted
  those bytes. The signed archive SHA256 is
  `87aaca4164ea9d5c8085854953018263f7963f07c22e73a2a2185cc98c581c34`.
- Astra independently fetched the official files, ran the staged production
  helper, extracted the official archive in a separate fresh directory, and
  compared all 211 symlink path/target pairs. Source identity/pin checks and
  extraction are proven at this scope; no compile or guest result is inferred.
- Actual extracted Makefile declares Buildroot2026.08. The signed distribution's
  Linux6.18.7 and BusyBox1.38.0 archive/hash rows match the unchanged lock.
- Separate synthetic signed fixtures exercise actual GPG and actual driver
  success/failure paths. Negative cases assert extraction is not invoked after
  verification failure. They are not substituted for real-source evidence.

Files in this directory preserve current deterministic test output, packet hash,
real GPG status/command evidence, source results, independent Astra evidence and
review, next-stage preflight, and a SHA256 manifest. No source tarball, private key
or compiled guest image is published here. Raw local workspace paths in command
logs identify this scratch run; they are not guaranteed durable artifact URLs.

## Acceptance and boundaries

The original Actions failure at key download remains historical. This repair
does not convert that failed run into a success. The previously failed local
extraction is recorded as a separate observation; later passing evidence has its
own fresh source root.

The upstream certificate uses legacy DSA1024. Verification used the host's normal
GPG policy; environments rejecting it remain BLOCKED. The reviewed HTTPS source
and pins are the trust anchors, not Web-of-Trust identity certification. Offline
certificate verification does not discover later revocations. The source-work
directory is trusted/private during extraction; hostile concurrent mutation of
that destination or source archive is outside this test's model.

This environment currently lacks QEMU, cpio and other required build tools.
The existing entrypoint is intentionally GitHub-runner-only; no runner identity
was forged and no hosted workflow was dispatched. Provider billing/usage is
unknown rather than inferred zero; no external metered model API was invoked.

## One next owner action

Mark reviews/merges the source fix and manually starts **one build-mode run** of
`puppf-p0a-build.yml` on the reviewed revision, per the existing issue #15 work
order and `puppy-p0a/README.md`. Keep the successful artifact/receipt before its
three-day Actions retention expires. Inspect the first actual failure if any;
do not treat an authoring test pass as the terminal-shell milestone. A complete
M1 still requires the real build and two unchanged-artifact serial-shell boots
under the frozen P0a checks. M2 remains the small user-facing launcher afterward.
