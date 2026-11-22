import importlib.util
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "diode.py"
spec = importlib.util.spec_from_file_location("diode", SCRIPT)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


class WireTests(unittest.TestCase):
    def test_exact_byte_limit_ascii_and_multibyte(self):
        overhead = len(d.message(1, ""))
        exact = d.message(1, "x" * (256 - overhead))
        self.assertEqual(256, len(exact))
        d.validate(exact)
        text = "é" * ((256 - overhead) // 2) + "x" * ((256 - overhead) % 2)
        self.assertEqual(256, len(d.message(1, text)))
        for text in ["x" * (257 - overhead), text + "x"]:
            with self.assertRaises(d.Rejected):
                d.message(1, text)

    def test_invalid_schema_types_and_rounds(self):
        base = {"v": 0, "round": 1, "kind": "MESSAGE", "text": "ok"}
        for key, value in [("v", False), ("v", 1), ("round", True), ("round", 1.0),
                           ("round", 0), ("round", 7), ("text", 123), ("kind", "ACK")]:
            with self.subTest(key=key, value=value), self.assertRaises(d.Rejected):
                d.validate(d.canonical({**base, key: value}))
        for value in [{**base, "extra": 1}, {"v": 0}, [], "hello", None]:
            with self.subTest(value=value), self.assertRaises(d.Rejected):
                d.validate(d.canonical(value))

    def test_bad_utf8_duplicate_keys_and_multiline(self):
        good = d.message(1, "ok")
        bad = [b'\xff\n', good[:-1], good + good, b'\n' + good,
               good.replace(b'"v":0', b'"v":0,"v":0'),
               good.replace(b'"ok"', b'"bad\\nline"'),
               good.replace(b'"ok"', b'"bad\\rline"'),
               good.replace(b'"ok"', b'"\\ud800"'), b'{}\r\n']
        for wire in bad:
            with self.subTest(wire=wire), self.assertRaises(d.Rejected):
                d.validate(wire)


class RelayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.root = self.parent / "run"
        self.relay = d.Relay(self.root)

    def first_message(self):
        self.relay.send("a_to_b", d.message(1, "hello"))
        return self.relay.receive("a_to_b")

    def test_modes_and_umask_restoration(self):
        old = os.umask(0)
        try:
            other = d.Relay(self.parent / "other")
            current = os.umask(0)
            self.assertEqual(0, current)
            other.send("a_to_b", d.message(1, "private"))
            other.stop()
            for path in [other.root, other.root / "a_to_b", other.root / "b_to_a"]:
                self.assertEqual(0o700, stat.S_IMODE(path.stat().st_mode))
            for path in [other.transcript, other.root / "STOP", other.root / "a_to_b/1.json"]:
                self.assertEqual(0o600, stat.S_IMODE(path.stat().st_mode))
        finally:
            os.umask(old)

    def test_transcript_appends_without_replacing_inode_or_prefix(self):
        identity = self.relay.transcript.stat().st_ino
        self.first_message()
        prefix = self.relay.transcript.read_bytes()
        self.relay.send("b_to_a", d.message(1, "reply"))
        self.relay.receive("b_to_a")
        data = self.relay.transcript.read_bytes()
        self.assertEqual(identity, self.relay.transcript.stat().st_ino)
        self.assertTrue(data.startswith(prefix))
        self.assertGreater(len(data), len(prefix))
        self.assertEqual(2, len(data.splitlines()))

    def test_duplicate_wrong_round_and_direction_rejected(self):
        for direction, wire in [("b_to_a", d.message(1, "bad")),
                                ("a_to_b", d.message(2, "bad")),
                                ("../escape", d.message(1, "bad"))]:
            with self.assertRaises(d.Rejected):
                self.relay.send(direction, wire)
        self.first_message()
        before = self.relay.transcript.read_bytes()
        with self.assertRaises(d.Rejected):
            self.relay.send("a_to_b", d.message(1, "duplicate"))
        self.assertEqual(before, self.relay.transcript.read_bytes())

    def test_leftover_and_stalled_spool_are_preserved(self):
        stale = self.root / "b_to_a/stale.json"
        d.exclusive_file(stale, b"leftover")
        with self.assertRaises(d.Rejected):
            self.relay.send("a_to_b", d.message(1, "no overwrite"))
        self.assertEqual(b"leftover", stale.read_bytes())
        self.assertEqual(b"", self.relay.transcript.read_bytes())
        stale.unlink()
        self.relay.send("a_to_b", d.message(1, "waiting"))
        with self.assertRaises(d.Rejected):
            self.relay.send("a_to_b", d.message(1, "replacement"))
        with self.assertRaises(d.Rejected):
            self.relay.receive("b_to_a")
        self.assertEqual("waiting", d.validate((self.root / "a_to_b/1.json").read_bytes())["text"])

    def test_stop_before_send_and_between_send_receive(self):
        self.relay.send("a_to_b", d.message(1, "pending"))
        self.relay.stop()
        for action in [lambda: self.relay.receive("a_to_b"),
                       lambda: self.relay.send("a_to_b", d.message(1, "late"))]:
            with self.assertRaises(d.Rejected):
                action()
        self.assertEqual(b"", self.relay.transcript.read_bytes())
        self.assertTrue((self.root / "a_to_b/1.json").exists())

    def test_stop_checked_immediately_before_transcript_append(self):
        self.relay.send("a_to_b", d.message(1, "pending"))
        original = self.relay._append
        def stopped(record):
            self.relay.stop()
            original(record)
        with patch.object(self.relay, "_append", stopped), self.assertRaises(d.Rejected):
            self.relay.receive("a_to_b")
        self.assertEqual(b"", self.relay.transcript.read_bytes())

    def test_six_round_cap_and_post_stop_are_enforced(self):
        for number in range(1, 7):
            for direction in d.Relay.directions:
                self.relay.send(direction, d.message(number, "ok"))
                self.relay.receive(direction)
        before = self.relay.transcript.read_bytes()
        self.assertEqual(12, len(before.splitlines()))
        self.assertTrue((self.root / "STOP").exists())
        with self.assertRaises(d.Rejected):
            self.relay.send("a_to_b", d.message(1, "after cap"))
        self.assertEqual(before, self.relay.transcript.read_bytes())

    def test_existing_root_never_overwritten(self):
        marker = self.root / "keep"
        marker.write_text("keep")
        with self.assertRaises(FileExistsError):
            d.Relay(self.root)
        link = self.parent / "link"
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(FileExistsError):
            d.Relay(link)
        self.assertEqual("keep", marker.read_text())

    def test_stop_refuses_replaced_root_without_external_write(self):
        outside = self.parent / "outside"
        outside.mkdir(mode=0o700)
        moved = self.parent / "moved"
        self.root.rename(moved)
        self.root.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(d.Rejected):
            self.relay.stop()
        self.assertFalse((outside / "STOP").exists())
        self.assertEqual(b"", (moved / "transcript.log").read_bytes())

    def test_spool_symlink_and_hardlink_do_not_write_target(self):
        target = self.parent / "target"
        target.write_bytes(d.message(1, "target"))
        target.chmod(0o600)
        self.relay.send("a_to_b", d.message(1, "pending"))
        queued = self.root / "a_to_b/1.json"
        queued.unlink()
        queued.symlink_to(target)
        with self.assertRaises((OSError, d.Rejected)):
            self.relay.receive("a_to_b")
        queued.unlink()
        os.link(target, queued)
        with self.assertRaises(d.Rejected):
            self.relay.receive("a_to_b")
        self.assertEqual(d.message(1, "target"), target.read_bytes())
        self.assertEqual(b"", self.relay.transcript.read_bytes())

    def test_transcript_replacement_or_hardlink_rejected(self):
        target = self.parent / "target"
        target.write_bytes(b"do not modify")
        target.chmod(0o600)
        self.relay.transcript.unlink()
        self.relay.transcript.symlink_to(target)
        self.relay.send("a_to_b", d.message(1, "ok"))
        with self.assertRaises((OSError, d.Rejected)):
            self.relay.receive("a_to_b")
        self.relay.transcript.unlink()
        os.link(target, self.relay.transcript)
        with self.assertRaises(d.Rejected):
            self.relay.receive("a_to_b")
        self.assertEqual(b"do not modify", target.read_bytes())

    def test_removed_message_and_extra_spool_file_refused(self):
        self.relay.send("a_to_b", d.message(1, "ok"))
        queued = self.root / "a_to_b/1.json"
        queued.unlink()
        with self.assertRaises(d.Rejected):
            self.relay.receive("a_to_b")
        d.exclusive_file(queued, d.message(1, "ok"))
        d.exclusive_file(self.root / "a_to_b/extra", b"leftover")
        with self.assertRaises(d.Rejected):
            self.relay.receive("a_to_b")
        self.assertEqual(b"", self.relay.transcript.read_bytes())


class MockRunTests(unittest.TestCase):
    def test_verifier_refuses_empty_or_unparsed_suite_without_mock_runs(self):
        sys.path.insert(0, str(SCRIPT.parent))
        self.addCleanup(lambda: sys.path.remove(str(SCRIPT.parent)))
        verify_spec = importlib.util.spec_from_file_location("s0_verify", SCRIPT.parent / "verify.py")
        verify = importlib.util.module_from_spec(verify_spec)
        verify_spec.loader.exec_module(verify)
        for stderr in [b"Ran 0 tests in 0s\nOK\n", b"no count"]:
            with self.subTest(stderr=stderr), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "evidence"
                completed = subprocess.CompletedProcess([], 0, stdout=b"", stderr=stderr)
                with patch.object(sys, "argv", ["verify.py", "--evidence-dir", str(root)]), \
                     patch.object(verify.subprocess, "run", return_value=completed), \
                     patch.object(verify, "run_mock") as mocked:
                    self.assertEqual(1, verify.main())
                mocked.assert_not_called()
                self.assertEqual("FAIL", json.loads((root / "test-results.json").read_text())["status"])

    def test_two_fresh_seeded_runs_match_without_network(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(socket, "socket", side_effect=AssertionError("network forbidden")):
            a, b = Path(tmp) / "a", Path(tmp) / "b"
            first, second = d.run_mock(a), d.run_mock(b)
            self.assertEqual(first, second)
            self.assertEqual((a / "transcript.log").read_bytes(), (b / "transcript.log").read_bytes())
            self.assertEqual(12, first["messages"])
            self.assertFalse(first["guest_boot_proved"])
            self.assertFalse(first["security_containment_proved"])

    def test_cli_result_and_existing_directory_no_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "run"
            command = [sys.executable, "-B", str(SCRIPT), "--run-dir", str(root)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(0, run.returncode, run.stdout + run.stderr)
            self.assertEqual("PASS", json.loads(run.stdout)["status"])
            self.assertEqual(0o600, stat.S_IMODE((root / "result.json").stat().st_mode))
            before = (root / "transcript.log").read_bytes()
            self.assertEqual(2, subprocess.run(command, capture_output=True).returncode)
            self.assertEqual(before, (root / "transcript.log").read_bytes())


if __name__ == "__main__":
    unittest.main()
