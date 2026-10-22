import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ci"))
from boot import boot_once
from driver import Blocked, check_checker, is_release_makefile, unpack_release, valid_signature


class SourceAndHarnessFailures(unittest.TestCase):
    def test_version_pin_accepts_upstream_export_syntax(self):
        self.assertTrue(is_release_makefile("export BR2_VERSION := 2026.08\n"))
        self.assertFalse(is_release_makefile("export BR2_VERSION := 2026.08.1\n"))
        self.assertFalse(is_release_makefile("# BR2_VERSION := 2026.08\n"))

    def test_changed_checker_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            checker = Path(temp) / "checker.py"
            checker.write_text("modified checker")
            with self.assertRaises(Blocked):
                check_checker(checker, "0" * 64)

    def test_signature_requires_validsig_and_expected_signer(self):
        key = "F" * 40
        self.assertFalse(valid_signature("[GNUPG:] GOODSIG arbitrary\n", key))
        self.assertFalse(valid_signature("[GNUPG:] VALIDSIG " + "0" * 40 + " rest\n", key))
        self.assertTrue(valid_signature("[GNUPG:] VALIDSIG " + key + " rest\n", key))

    def test_archive_cannot_extract_outside_release(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "bad.tar.xz"
            with tarfile.open(archive, "w:xz") as stream:
                info = tarfile.TarInfo("../outside")
                info.size = 1
                stream.addfile(info, io.BytesIO(b"x"))
            with self.assertRaises(Blocked):
                unpack_release(archive, root)
            self.assertFalse((root.parent / "outside").exists())

    def test_archive_rejects_escaping_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "bad.tar.xz"
            with tarfile.open(archive, "w:xz") as stream:
                info = tarfile.TarInfo("buildroot-2026.08/link")
                info.type = tarfile.SYMTYPE
                info.linkname = "../../outside"
                stream.addfile(info)
            with self.assertRaises(tarfile.FilterError):
                unpack_release(archive, root)

    def test_missing_qemu_saves_failure_not_success(self):
        # Popen is mocked: this test neither boots a guest nor needs QEMU.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ["kernel", "initramfs"]:
                (root / name).write_bytes(b"fixture-only")
            with patch("boot.subprocess.Popen", side_effect=FileNotFoundError("fixture missing qemu")):
                result = boot_once(root / "kernel", root / "initramfs", root / "run")
            self.assertEqual("FAIL", result["status"])
            saved = json.loads((root / "run/test-results.json").read_text())
            self.assertEqual("FAIL", saved["status"])
            self.assertEqual("qemu_launch_failure", saved["evidence_kind"])
            self.assertEqual(b"", (root / "run/serial.log").read_bytes())


if __name__ == "__main__":
    unittest.main()
