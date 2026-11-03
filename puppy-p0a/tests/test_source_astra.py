"""Independent source-authentication boundary regressions; no build or boot."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ci"))
from source_verification import (SourceVerificationError, authenticate_archive,
                                 check_container, manifest_digest,
                                 signature_record)
from test_source_authentication import fixture_archive_bytes, fixture_release


FIXTURES = Path(__file__).with_name("fixtures") / "source-auth"


class AstraSourceBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="puppf-astra-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.evidence = self.root / "evidence"
        self.work = self.root / "work"
        self.evidence.mkdir()
        self.work.mkdir()
        self.release = fixture_release()
        self.archive = self.work / self.release["archive_basename"]
        self.archive.write_bytes(fixture_archive_bytes())
        self.calls = []

    def command(self, argv, log, **unused):
        self.calls.append(list(argv))
        completed = subprocess.run(argv, capture_output=True, text=True, timeout=20)
        (self.evidence / log).write_text(completed.stdout + completed.stderr)
        if completed.returncode:
            raise SourceVerificationError(f"real GPG failed: {completed.returncode}")
        return completed.stdout

    def authenticate(self, command=None, archive=None, manifest=None):
        return authenticate_archive(
            archive or self.archive,
            manifest or FIXTURES / "valid.sign",
            FIXTURES / "fixture-public-key.asc", self.release,
            self.evidence, self.work, command or self.command)

    def test_real_verification_output_is_quarantined_until_command_success(self):
        class CommandFailure(RuntimeError):
            pass

        def fail_after_output(argv, log, **options):
            result = self.command(argv, log, **options)
            if "--decrypt" in argv:
                self.assertTrue((self.evidence / "manifest-status.log").is_file())
                self.assertTrue((self.evidence / "checksums.quarantined.txt").is_file())
                raise CommandFailure("simulated failed command with genuine output")
            return result

        with self.assertRaises(CommandFailure):
            self.authenticate(command=fail_after_output)
        self.assertFalse((self.evidence / "verified-checksums.txt").exists())

    def test_successful_command_stdout_cannot_substitute_for_status_file(self):
        def remove_status(argv, log, **options):
            result = self.command(argv, log, **options)
            if "--decrypt" in argv:
                path = self.evidence / "manifest-status.log"
                genuine_status = path.read_text()
                path.unlink()
                return genuine_status
            return result

        with self.assertRaisesRegex(SourceVerificationError, "missing or malformed"):
            self.authenticate(command=remove_status)
        self.assertFalse((self.evidence / "verified-checksums.txt").exists())

    def test_preexisting_status_cannot_be_reused_or_overwritten(self):
        status = self.evidence / "manifest-status.log"
        status.write_text("STALE STATUS MUST NOT BE REUSED\n")
        with self.assertRaisesRegex(SourceVerificationError, "preexisting"):
            self.authenticate()
        self.assertEqual(status.read_text(), "STALE STATUS MUST NOT BE REUSED\n")
        self.assertFalse(any("--decrypt" in argv for argv in self.calls))

    def test_real_signature_cannot_authorize_archive_with_wrong_local_basename(self):
        archive = self.root / "renamed.tar.xz"
        archive.write_bytes(fixture_archive_bytes())
        with self.assertRaisesRegex(SourceVerificationError, "basename differs"):
            self.authenticate(archive=archive)
        self.assertTrue((self.evidence / "manifest-status.log").is_file())
        self.assertFalse((self.evidence / "verified-checksums.txt").exists())

    def test_reviewed_archive_pin_is_independent_of_valid_signed_manifest(self):
        self.release["archive_sha256"] = "0" * 64
        with self.assertRaisesRegex(SourceVerificationError, "reviewed lock"):
            self.authenticate()
        self.assertTrue((self.evidence / "checksums.quarantined.txt").is_file())
        self.assertFalse((self.evidence / "verified-checksums.txt").exists())

    def test_unsigned_checksum_suffix_is_rejected_before_gpg(self):
        manifest = self.root / "unsigned-suffix.sign"
        manifest.write_bytes((FIXTURES / "valid.sign").read_bytes()
                             + b"\nSHA256: " + b"0" * 64
                             + b"  buildroot-2026.08.tar.xz\n")
        with self.assertRaisesRegex(SourceVerificationError, "unsigned data"):
            self.authenticate(manifest=manifest)
        self.assertEqual(self.calls, [])

    def test_two_complete_signed_containers_are_rejected_before_gpg(self):
        manifest = self.root / "two-containers.sign"
        manifest.write_bytes((FIXTURES / "valid.sign").read_bytes() * 2)
        with self.assertRaisesRegex(SourceVerificationError, "one clearsigned"):
            check_container(manifest)

    def test_manifest_fields_cannot_be_joined_across_lines(self):
        basename = self.release["archive_basename"]
        digest = self.release["archive_sha256"]
        for value in (f"SHA256:\n{digest}  {basename}\n",
                      f"SHA256: {digest}\n{basename}\n",
                      f"SHA256: {digest[:32]}\n{digest[32:]}  {basename}\n"):
            with self.subTest(value=value):
                with self.assertRaises(SourceVerificationError):
                    manifest_digest(value, basename)

    def test_malformed_digest_entry_is_not_hidden_by_later_valid_entry(self):
        basename = self.release["archive_basename"]
        text = (f"SHA256: malformed  {basename}\n"
                f"SHA256: {self.release['archive_sha256']}  {basename}\n")
        with self.assertRaisesRegex(SourceVerificationError, "malformed"):
            manifest_digest(text, basename)

    def test_valid_signature_cannot_mask_bad_status_or_authorize_subkey(self):
        record = self.authenticate()
        self.assertEqual(record["status"], "VERIFIED")
        status = (self.evidence / "manifest-status.log").read_text()
        expected = self.release["signer_fingerprint"]
        for bad in ("BADSIG", "ERRSIG", "REVKEYSIG", "EXPKEYSIG", "EXPSIG",
                    "ERROR", "FAILURE", "NO_PUBKEY"):
            with self.subTest(bad=bad):
                self.assertIsNone(signature_record(status + f"[GNUPG:] {bad} synthetic\n", expected))
        # Keeping the expected primary fingerprint in the last field must not
        # authorize a different signing fingerprint in the first field.
        delegated = status.replace("VALIDSIG " + expected, "VALIDSIG " + "0" * 40)
        self.assertIsNone(signature_record(delegated, expected))


if __name__ == "__main__":
    unittest.main()
