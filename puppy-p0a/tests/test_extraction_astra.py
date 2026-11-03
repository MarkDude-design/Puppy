"""Adversarial archive fixtures for the source-only extraction boundary."""
import io
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ci"))
from driver import Blocked, unpack_release


RELEASE = "buildroot-2026.08"
GUEST_LINK = RELEASE + "/package/skeleton-init-openrc/skeleton/etc/runlevels/default/sysv-rcs"


class AstraExtractionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="puppf-extract-astra-")
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.archive = self.folder / "fixture.tar.xz"
        self.destination = self.folder / "destination"
        self.destination.mkdir()
        self.release = self.destination / RELEASE

    def write_archive(self, entries):
        with tarfile.open(self.archive, "w:xz") as stream:
            for kind, name, value in entries:
                item = tarfile.TarInfo(name)
                if kind == "file":
                    data = value.encode("ascii")
                    item.size = len(data)
                    stream.addfile(item, io.BytesIO(data))
                    continue
                item.type = {"dir": tarfile.DIRTYPE, "link": tarfile.SYMTYPE,
                             "hardlink": tarfile.LNKTYPE, "fifo": tarfile.FIFOTYPE,
                             "device": tarfile.CHRTYPE}[kind]
                if kind == "dir":
                    item.mode = value
                else:
                    item.linkname = value
                stream.addfile(item)

    def assert_rejected_before_release_created(self, entries):
        self.write_archive(entries)
        with self.assertRaises((Blocked, tarfile.FilterError)):
            unpack_release(self.archive, self.destination)
        self.assertFalse(os.path.lexists(self.release))

    def test_all_regular_data_exists_before_any_link_creation(self):
        self.write_archive([
            ("dir", RELEASE, 0o775),
            ("link", RELEASE + "/early-link", "payload"),
            ("file", RELEASE + "/payload", "synthetic contents"),
            ("file", RELEASE + "/last-file", "last regular data"),
            ("dir", RELEASE, 0o755),
        ])
        original = Path.symlink_to
        created = []

        def observe(path, target, *args, **kwargs):
            self.assertEqual((self.release / "payload").read_text(), "synthetic contents")
            self.assertEqual((self.release / "last-file").read_text(), "last regular data")
            created.append((path.name, target))
            return original(path, target, *args, **kwargs)

        with patch.object(Path, "symlink_to", observe):
            result = unpack_release(self.archive, self.destination)
        self.assertEqual(result, self.release)
        self.assertEqual(created, [("early-link", "payload")])
        self.assertEqual(os.readlink(self.release / "early-link"), "payload")

    def test_exact_guest_link_pair_still_requires_reviewed_archive_bytes(self):
        self.assert_rejected_before_release_created([
            ("file", RELEASE + "/safe", "never extracted"),
            ("link", GUEST_LINK, "/etc/init.d/sysv-rcs"),
        ])

    def test_unreviewed_absolute_link_path_or_target_is_rejected(self):
        for name, target in ((RELEASE + "/other-link", "/etc/init.d/sysv-rcs"),
                             (GUEST_LINK, "/unreviewed/target")):
            with self.subTest(name=name, target=target):
                self.assert_rejected_before_release_created([("link", name, target)])

    def test_relative_link_cannot_escape_release_into_work_directory(self):
        outside = self.destination / "outside"
        outside.write_text("SYNTHETIC CANARY")
        self.assert_rejected_before_release_created([
            ("file", RELEASE + "/payload", "must remain unextracted"),
            ("link", RELEASE + "/escape", "../outside"),
        ])
        self.assertEqual(outside.read_text(), "SYNTHETIC CANARY")

    def test_symlink_ancestor_is_rejected_in_either_archive_order(self):
        link = ("link", RELEASE + "/alias", "real")
        child = ("file", RELEASE + "/alias/child", "must not write through link")
        for entries in ([link, child], [child, link]):
            with self.subTest(entries=entries):
                self.assert_rejected_before_release_created(entries)

    def test_symlink_chain_is_checked_before_dotdot_normalization(self):
        outside = self.destination / "outside"
        outside.write_text("SYNTHETIC CANARY")
        self.assert_rejected_before_release_created([
            ("link", RELEASE + "/a", "."),
            ("link", RELEASE + "/evil", "a/../outside"),
        ])
        self.assertEqual(outside.read_text(), "SYNTHETIC CANARY")

    def test_relative_alias_and_self_cycle_are_rejected(self):
        for entries in ([
                ("file", RELEASE + "/payload", "contents"),
                ("link", RELEASE + "/a", "payload"),
                ("link", RELEASE + "/b", "a"),
            ], [("link", RELEASE + "/self", "self")]):
            with self.subTest(entries=entries):
                self.assert_rejected_before_release_created(entries)

    def test_preexisting_dangling_release_symlink_is_rejected(self):
        outside = self.folder / "nonexistent-outside"
        self.release.symlink_to(outside)
        self.write_archive([("file", RELEASE + "/payload", "contents")])
        with self.assertRaisesRegex(Blocked, "fresh release root"):
            unpack_release(self.archive, self.destination)
        self.assertTrue(self.release.is_symlink())
        self.assertFalse(outside.exists())

    def test_duplicate_files_links_and_type_conflicts_are_rejected(self):
        name = RELEASE + "/same"
        for entries in ([
                ("file", name, "first"), ("file", name, "second"),
            ], [
                ("dir", name, 0o755), ("file", name, "replacement"),
            ], [
                ("link", name, "."), ("link", name, "."),
            ]):
            with self.subTest(entries=entries):
                self.assert_rejected_before_release_created(entries)

    def test_hardlinks_and_special_files_are_rejected_before_writes(self):
        for kind in ("hardlink", "fifo", "device"):
            with self.subTest(kind=kind):
                self.assert_rejected_before_release_created([
                    ("file", RELEASE + "/payload", "contents"),
                    (kind, RELEASE + "/special", RELEASE + "/payload"),
                ])

    def test_release_root_cannot_be_file_or_symlink(self):
        for kind, target in (("file", "contents"), ("link", ".")):
            with self.subTest(kind=kind):
                self.assert_rejected_before_release_created([(kind, RELEASE, target)])

    def test_non_normal_member_paths_are_rejected_before_writes(self):
        for name in (RELEASE + "/x/../payload", RELEASE + "//payload",
                     RELEASE + "/./payload", "../outside", "/" + RELEASE + "/payload"):
            with self.subTest(name=name):
                self.assert_rejected_before_release_created([("file", name, "contents")])


if __name__ == "__main__":
    unittest.main()
