"""Offline fixtures exercise real GPG and the actual pre-extraction verifier."""
import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ci"))
import driver
from driver import Blocked, Run
from source_verification import (SourceVerificationError, authenticate_archive,
                                 manifest_digest, valid_signature)


FIXTURES = Path(__file__).parent / "fixtures" / "source-auth"
METADATA = json.loads((FIXTURES / "metadata.json").read_text())
BASENAME = METADATA["archive_basename"]


def fixture_archive_bytes():
    return base64.b64decode((FIXTURES / (BASENAME + ".b64")).read_text().strip(), validate=True)


def fixture_release():
    return dict(archive_basename=BASENAME, archive_sha256=METADATA["archive_sha256"],
                signer_fingerprint=METADATA["signer_fingerprint"],
                public_key_sha256=METADATA["public_key_sha256"],
                public_key_path="fixture-public-key.asc",
                archive_url="https://fixture.invalid/" + BASENAME,
                signature_url="https://fixture.invalid/manifest.sign",
                public_key_url="https://fixture.invalid/public-key.asc")


def status_fixture():
    key = METADATA["signer_fingerprint"]
    return ("[GNUPG:] PLAINTEXT 74 0\n[GNUPG:] NEWSIG\n[GNUPG:] GOODSIG fixture\n"
            f"[GNUPG:] VALIDSIG {key} 2026-10-01 1790812800 0 4 0 1 8 01 {key}\n")


class SourceAuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="puppf-auth-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        self.work = self.root / "work"
        self.work.mkdir()
        self.archive = self.work / BASENAME
        self.archive.write_bytes(fixture_archive_bytes())
        self.manifest = self.root / "fixture.sign"
        self.manifest.write_bytes((FIXTURES / "valid.sign").read_bytes())
        self.key = self.root / "fixture-key.asc"
        self.key.write_bytes((FIXTURES / "fixture-public-key.asc").read_bytes())
        self.release = fixture_release()
        self.run = Run(self.evidence)

    def verify(self):
        return authenticate_archive(self.archive, self.manifest, self.key, self.release,
                                    self.evidence, self.work, self.run.command)

    def test_actual_gpg_positive_synthetic_archive(self):
        result = self.verify()
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(result["archive_sha256"], self.release["archive_sha256"])
        self.assertTrue((self.evidence / "verified-checksums.txt").exists())
        self.assertEqual((self.work / "gnupg").stat().st_mode & 0o777, 0o700)
        self.assertTrue(all(command["exit_code"] == 0 for command in self.run.commands))
        self.assertFalse(any("gpgv" in command["argv"] for command in self.run.commands))

    def test_actual_driver_positive_extracts_after_verification(self):
        def download_fixture(url, path, maximum):
            if url == self.release["archive_url"]:
                Path(path).write_bytes(fixture_archive_bytes())
            elif url == self.release["signature_url"]:
                Path(path).write_bytes((FIXTURES / "valid.sign").read_bytes())
            else:
                raise AssertionError("unexpected keyserver/network request")
        with patch.object(driver, "TASK", FIXTURES), patch.object(driver, "download", download_fixture):
            result = self.run.verify_release(dict(buildroot=self.release), self.work)
        self.assertTrue((result / "SYNTHETIC.txt").exists())
        self.assertEqual(self.run.manifest["source_authentication"]["status"], "VERIFIED")

    def test_actual_driver_negative_cases_never_extract(self):
        variants = ["wrong-hash", "wrong-name", "missing", "duplicate-identical",
                    "duplicate-conflicting", "malformed", "path-name", "wrong-signer"]
        for name in variants:
            with self.subTest(name=name), tempfile.TemporaryDirectory(prefix="puppf-driver-negative-") as folder:
                root = Path(folder); evidence = root / "evidence"; evidence.mkdir()
                work = root / "work"; work.mkdir()
                run = Run(evidence)
                release = fixture_release()

                def download_fixture(url, path, maximum):
                    Path(path).write_bytes(fixture_archive_bytes() if url == release["archive_url"]
                                           else (FIXTURES / (name + ".sign")).read_bytes())
                with patch.object(driver, "TASK", FIXTURES), patch.object(driver, "download", download_fixture), \
                        patch.object(driver, "unpack_release") as extract:
                    with self.assertRaises(Blocked):
                        run.verify_release(dict(buildroot=release), work)
                    extract.assert_not_called()
                self.assertEqual(run.manifest["source_authentication"], "NOT_RUN")

    def test_missing_key_and_changed_key_fail_before_gpg(self):
        self.key.write_bytes(self.key.read_bytes() + b"corruption")
        with patch.object(self.run, "command") as command:
            with self.assertRaises(SourceVerificationError): self.verify()
            command.assert_not_called()
        self.key.unlink()
        with self.assertRaises(OSError): self.verify()

    def test_wrong_primary_fingerprint_fails(self):
        self.release["signer_fingerprint"] = "F0A589A56CFE2C6D68E9471AED04E0FBE016E856"
        with self.assertRaises(SourceVerificationError): self.verify()
        self.assertEqual(len(self.run.commands), 1)

    def test_archive_byte_mismatch_and_extra_lock_pin_are_checked(self):
        self.archive.write_bytes(self.archive.read_bytes() + b"tampered")
        with self.assertRaises(SourceVerificationError): self.verify()
        self.assertFalse((self.evidence / "verified-checksums.txt").exists())

    def test_tampered_signature_output_is_never_consumed(self):
        text = self.manifest.read_text()
        digest = self.release["archive_sha256"]
        self.manifest.write_text(text.replace(digest, "0" * 64, 1))
        with patch("source_verification.manifest_digest") as parser:
            with self.assertRaises(Blocked): self.verify()
            parser.assert_not_called()
        self.assertTrue((self.evidence / "checksums.quarantined.txt").exists())
        self.assertFalse((self.evidence / "verified-checksums.txt").exists())

    def test_unsigned_suffix_and_multiple_containers_rejected_before_gpg(self):
        original = self.manifest.read_bytes()
        for contents in (original + b"SHA256: unsigned\n", original + original):
            with self.subTest(bytes=len(contents)):
                self.manifest.write_bytes(contents)
                with patch.object(self.run, "command") as command:
                    with self.assertRaises(SourceVerificationError): self.verify()
                    command.assert_not_called()

    def test_real_upstream_manifest_verified_offline_without_archive_claim(self):
        repo = Path(__file__).resolve().parents[1]
        upstream = repo / "tests/fixtures/upstream/buildroot-2026.08.tar.xz.sign"
        key = repo / "trust/buildroot-2026.08-release-key.asc"
        release = json.loads((repo / "source-lock.json").read_text())["buildroot"]
        self.manifest.write_bytes(upstream.read_bytes())
        self.key.write_bytes(key.read_bytes())
        self.release = release
        # A tiny synthetic archive must be rejected despite a real good upstream signature.
        with self.assertRaisesRegex(SourceVerificationError, "archive SHA256"):
            self.verify()
        status = (self.evidence / "manifest-status.log").read_text()
        self.assertTrue(valid_signature(status, release["signer_fingerprint"]))
        self.assertFalse((self.evidence / "verified-checksums.txt").exists())


class SignatureAndManifestParserTests(unittest.TestCase):
    def test_dedicated_status_needs_one_complete_expected_signature(self):
        key = METADATA["signer_fingerprint"]
        status = status_fixture()
        self.assertTrue(valid_signature(status, key))
        variants = [status + status, status + "[GNUPG:] BADSIG bad\n",
                    status.replace(key, "F" * 40),
                    status.replace(" 4 0 1 8 01 ", " 4 0 1 2 01 "),
                    status.replace(" 4 0 1 8 01 ", " 4 0 1 8 00 "),
                    status.replace("[GNUPG:] NEWSIG\n", ""),
                    f"[GNUPG:] VALIDSIG {key} rest\n"]
        for raw in variants:
            with self.subTest(raw=raw): self.assertFalse(valid_signature(raw, key))
        for tag in ["ERRSIG", "NO_PUBKEY", "EXPKEYSIG", "REVKEYSIG", "EXPSIG", "FAILURE", "ERROR"]:
            self.assertFalse(valid_signature(status + f"[GNUPG:] {tag} detail\n", key))

    def test_manifest_exact_basename_and_unique_entry(self):
        digest = METADATA["archive_sha256"]
        line = f"SHA256: {digest}  {BASENAME}"
        self.assertEqual(manifest_digest(line + "\n", BASENAME), digest)
        bad = [line + "\n" + line, line.replace(BASENAME, "x" + BASENAME),
               line.replace(BASENAME, "../" + BASENAME), line.replace("SHA256:", "SHA256:\n"),
               line.replace(digest, "bad"), " " + line, ""]
        for text in bad:
            with self.subTest(text=text):
                with self.assertRaises(SourceVerificationError): manifest_digest(text, BASENAME)


if __name__ == "__main__":
    unittest.main()
