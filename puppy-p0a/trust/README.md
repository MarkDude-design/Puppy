# Buildroot 2026.08 release-manifest key

This is a public verification certificate, not a project signing key or credential.

| Item | Recorded value |
|---|---|
| Official key source | https://buildroot.org/~jacmet/pubkey.gpg |
| Key bytes | 1686 |
| Key-file SHA256 | `085d1b664bc0a900b2c33aa509a7e4d6fa3b6018009cd9d3f8c62a03d7adfa7a` |
| Manifest signer | `AB07D806D2CE741FB886EE50B025BA8B59C36319` |
| Key type observed by GPG | DSA1024 signing primary; ElGamal2048 encryption subkey |
| Different annotated-tag signer | `F0A589A56CFE2C6D68E9471AED04E0FBE016E856` |
| Official checksum manifest | https://buildroot.org/downloads/buildroot-2026.08.tar.xz.sign |
| Manifest SHA256 | `0a81dd0e2e19bf28c9306e454caef66cfebee599f8a28c00e64f4b41820f6ae6` |
| Archive SHA256 authenticated by that manifest | `87aaca4164ea9d5c8085854953018263f7963f07c22e73a2a2185cc98c581c34` |

Meraki and Astra fetched the official public files afresh on November 3, 2026,
and independently ran actual GPG verification and archive-byte hash checks.
These findings are distinct from the historical October 27 review receipts.
The identity anchor here is the reviewed official HTTPS source and committed
byte/fingerprint pins, not Web-of-Trust certification or a keyserver lookup.
The manifest's mention of its own key URL is not a separate independent anchor.

The certificate is pinned for this exact historical release. Offline checks do
not discover later revocations or new upstream keys. No digest/key-policy override
is permitted; a platform refusing the legacy algorithm must report BLOCKED.
The verifier retains ordinary GPG expiry/revocation status checks and explicitly
rejects bad/expired/revoked signature status records. It does not switch to gpgv,
whose documented key-validity policy differs.

Sources: [official download page](https://buildroot.org/download.html),
[GnuPG verification commands](https://www.gnupg.org/documentation/manuals/gnupg/Operational-GPG-Commands.html),
[GnuPG gpgv policy comparison](https://www.gnupg.org/documentation/manuals/gnupg/gpgv.html).
