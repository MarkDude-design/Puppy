"""Artifact rejection tests and real POSIX process/terminal cleanup; no guest mock PASS."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "puppy-p0a/launch.py"
spec = importlib.util.spec_from_file_location("puppf_launcher", SOURCE)
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / "evidence.zip"
        self.dest = self.root / "images"
        self.dest.mkdir()
        self.entries = [("artifacts/bzImage", b"test kernel"), ("artifacts/rootfs.cpio.gz", b"test initramfs")]
        self.pins = {"images": [{"member": n, "filename": n.split("/")[-1], "bytes": len(b),
                                 "sha256": hashlib.sha256(b).hexdigest()} for n, b in self.entries]}
        self.write_bundle()

    def write_bundle(self, entries=None):
        with zipfile.ZipFile(self.bundle, "w") as archive:
            for n, b in (self.entries if entries is None else entries):
                archive.writestr(n, b)
        self.pins["evidence_zip_sha256"] = launcher.digest(self.bundle)

    def test_verified_images_only_no_archive_path_extraction(self):
        self.write_bundle(self.entries + [("../do-not-extract", b"extra"), ("logs/script.py", b"raise Exception()")])
        paths = launcher.prepare_images(self.bundle, self.dest, self.pins)
        self.assertEqual([p.read_bytes() for p in paths], [b for _, b in self.entries])
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()), ["bzImage", "rootfs.cpio.gz"])
        self.assertFalse((self.root / "do-not-extract").exists())

    def test_changed_bundle_rejected_before_member_writes(self):
        with self.bundle.open("ab") as stream:
            stream.write(b"tampering")
        with self.assertRaisesRegex(launcher.LaunchError, "differs"):
            launcher.prepare_images(self.bundle, self.dest, self.pins)
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_wrong_image_hash_rejected_even_when_bundle_hash_matches(self):
        self.pins["images"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(launcher.LaunchError, "Image bytes"):
            launcher.prepare_images(self.bundle, self.dest, self.pins)

    def test_missing_image_rejected(self):
        self.write_bundle(self.entries[:1])
        with self.assertRaisesRegex(launcher.LaunchError, "Missing or duplicate"):
            launcher.prepare_images(self.bundle, self.dest, self.pins)

    def test_duplicate_image_rejected(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            self.write_bundle(self.entries + self.entries[:1])
        with self.assertRaisesRegex(launcher.LaunchError, "Missing or duplicate"):
            launcher.prepare_images(self.bundle, self.dest, self.pins)

    def test_unexpected_size_rejected(self):
        self.pins["images"][0]["bytes"] += 1
        with self.assertRaisesRegex(launcher.LaunchError, "size"):
            launcher.prepare_images(self.bundle, self.dest, self.pins)

    def test_existing_output_not_overwritten(self):
        (self.dest / "bzImage").write_bytes(b"keep")
        with self.assertRaises(FileExistsError):
            launcher.prepare_images(self.bundle, self.dest, self.pins)
        self.assertEqual((self.dest / "bzImage").read_bytes(), b"keep")

    def test_bounded_zip_rejected_before_hash(self):
        with patch.object(launcher, "MAX_ZIP_BYTES", 1):
            with self.assertRaisesRegex(launcher.LaunchError, "limit"):
                launcher.prepare_images(self.bundle, self.dest, self.pins)

    def invoke(self, options, qemu=None):
        pins = self.root / "pins.json"
        pins.write_text(json.dumps(self.pins))
        out, err = io.StringIO(), io.StringIO()
        with patch.object(launcher, "PIN_FILE", pins), patch.object(launcher.shutil, "which", return_value=qemu), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            result = launcher.main(["--evidence", str(self.bundle), *options])
        return result, out.getvalue(), err.getvalue()

    def test_verify_only_does_not_need_qemu(self):
        result, _, err = self.invoke(["--verify-only"])
        self.assertEqual(result, 0, err)

    def test_missing_qemu_clear_error_and_no_boot(self):
        result, _, err = self.invoke(["--check"])
        self.assertEqual(result, 2)
        self.assertIn("qemu-system-x86_64 is missing", err)

    def test_noninteractive_launch_rejected(self):
        with patch.object(sys.stdin, "isatty", return_value=False):
            result, _, err = self.invoke([], qemu="/known/qemu")
        self.assertEqual(result, 2)
        self.assertIn("interactive terminal", err)

    def test_host_argv_preserves_offline_serial_contract(self):
        args = launcher.qemu_command("/qemu", Path("/tmp/kernel with spaces"), Path("/tmp/rootfs"))
        for flag, value in [("-m", "128"), ("-nic", "none"), ("-monitor", "none"), ("-display", "none")]:
            self.assertEqual(args[args.index(flag) + 1], value)
        self.assertIn("stdio,id=puppf_console,signal=on", args)
        self.assertIn("-no-user-config", args)
        self.assertEqual(args[args.index("-kernel") + 1], "/tmp/kernel with spaces")
        self.assertFalse(any(s in args for s in ("-drive", "-hda", "-virtfs", "-netdev", "-enable-kvm")))


@unittest.skipUnless(sys.platform in ("linux", "darwin"), "POSIX terminal behavior")
class RealConsoleTests(unittest.TestCase):
    def test_ctrl_c_reaps_child_and_restores_terminal(self):
        self.console_cleanup(stubborn=False)

    def test_repeated_ctrl_c_kills_stubborn_child_and_restores_terminal(self):
        self.console_cleanup(stubborn=True)

    def console_cleanup(self, stubborn):
        import pty
        import termios
        master, slave = pty.openpty()
        self.addCleanup(os.close, master)
        self.addCleanup(os.close, slave)
        before = termios.tcgetattr(slave)
        child_code = ("import os,termios,time,signal; "
                      + ("signal.signal(signal.SIGTERM,signal.SIG_IGN); " if stubborn else "")
                      + "a=termios.tcgetattr(0); a[3] &= ~termios.ECHO; termios.tcsetattr(0,termios.TCSANOW,a); print('CHILD_PID='+str(os.getpid()),flush=True); time.sleep(60)")
        parent_code = ("import importlib.util,sys; s=importlib.util.spec_from_file_location('launcher',sys.argv[1]); "
                       "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                       "raise SystemExit(m.run_console([sys.executable,'-c',sys.argv[2]]))")
        process = subprocess.Popen([sys.executable, "-c", parent_code, str(SOURCE), child_code],
                                   stdin=slave, stdout=slave, stderr=slave, start_new_session=True)
        child_pid = None
        try:
            data = b""
            deadline = time.monotonic() + 10
            while b"CHILD_PID=" not in data or b"\n" not in data:
                if time.monotonic() > deadline:
                    self.fail("console child did not start")
                ready, _, _ = select.select([master], [], [], 0.1)
                if ready:
                    data += os.read(master, 4096)
            child_pid = int(data.split(b"CHILD_PID=")[1].splitlines()[0])
            os.kill(process.pid, signal.SIGINT)
            if stubborn:
                # Wait for cleanup to begin before delivering another interrupt.
                while b"Stopping Puppf" not in data:
                    if time.monotonic() > deadline:
                        self.fail("console did not enter cleanup")
                    ready, _, _ = select.select([master], [], [], 0.1)
                    if ready:
                        data += os.read(master, 4096)
                time.sleep(0.1)
                os.kill(process.pid, signal.SIGINT)
            self.assertEqual(process.wait(timeout=10), 0)
            self.assertEqual(termios.tcgetattr(slave), before)
            with self.assertRaises(ProcessLookupError):
                os.kill(child_pid, 0)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            if child_pid is not None:
                try:
                    os.kill(child_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_real_child_failure_exit_is_returned(self):
        import pty
        master, slave = pty.openpty()
        try:
            parent = ("import importlib.util,sys; s=importlib.util.spec_from_file_location('l',sys.argv[1]); "
                      "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                      "raise SystemExit(m.run_console([sys.executable,'-c','raise SystemExit(7)']))")
            p = subprocess.run([sys.executable, "-c", parent, str(SOURCE)], stdin=slave, stdout=slave,
                               stderr=slave, timeout=10)
            self.assertEqual(p.returncode, 7)
        finally:
            os.close(master)
            os.close(slave)


if __name__ == "__main__":
    unittest.main()
