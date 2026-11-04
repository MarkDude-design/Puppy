# Source authentication fixtures

`upstream/buildroot-2026.08.tar.xz.sign` is the unmodified small public upstream
clearsigned checksum manifest. Its hash and key source are recorded in
`../../trust/README.md`. Tests pair it with a synthetic archive and require a
hash-mismatch failure, so a real good signature cannot accidentally prove that a
fake archive is authentic. The actual 6,115,596-byte upstream archive is not copied
into the repository.

`source-auth/` contains synthetic RSA2048 public keys, signed manifests and a tiny
tar.xz encoded as base64 text. They are explicitly **not Buildroot releases**.
Actual GPG verifies these fixtures in the production helper/driver tests; only
the network download is replaced with local fixture reads. Wrong hash/name/key,
duplicate and malformed entries remain cryptographically valid signed negative
fixtures where applicable. Tests assert extraction is never invoked on failure.

`generate_source_fixtures.py` authored these files with PGPy0.6.0 in an isolated
scratch-only dependency directory. Private fixture keys were generated in memory
and never saved. The generated metadata pins each fixture and labels its origin.
PGPy is needed only for deliberate regeneration, not production or the tests.
Fresh generation uses new random keys and updates metadata; identical regenerated
bytes are not promised. Do not run the generator in the normal test suite.
