import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

CI = Path(__file__).resolve().parents[1] / "ci"
sys.path.insert(0, str(CI))
spec = importlib.util.spec_from_file_location("local_builder", CI / "local.py")
local = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local)


class LocalBuildControls(unittest.TestCase):
    def test_make_limits_top_level_and_recursive_jobs(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = local.LocalRun(tmp)
            with patch.object(local.Run, "command", return_value="") as execute:
                run.command(["make", "-C", "/fixture", "-j4"], "build.log")
            argv = execute.call_args.args[0]
            self.assertIn("-j1", argv)
            self.assertIn("BR2_JLEVEL=1", argv)
            self.assertNotIn("-j4", argv)
            self.assertEqual(86400, execute.call_args.kwargs["timeout"])

    def test_existing_run_refused_and_contents_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "keep"
            marker.write_text("old attempt")
            with self.assertRaises(FileExistsError):
                local.local_paths(tmp)
            self.assertEqual("old attempt", marker.read_text())

    def test_checkout_run_directory_rejected(self):
        with self.assertRaises(local.Blocked):
            local.local_paths(local.REPO / "accidental-build")

    def test_low_swap_is_actionable_block(self):
        mem = "MemAvailable: 1572864 kB\nMemTotal: 3774874 kB\nSwapTotal: 523264 kB\n"
        with patch.object(Path, "read_text", return_value=mem):
            with self.assertRaisesRegex(local.Blocked, "swap"):
                local.memory_check()

    def test_preflight_never_downloads_or_builds(self):
        def command(run, argv, log, **kwargs):
            if log == "checkout-commit.log":
                return "fixture-commit"
            if log == "checkout-status.log":
                return ""
            return ""
        def host(run):
            run.manifest["host"] = {"free_disk_bytes": 46 * 1024**3}
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "fresh"
            with patch.object(local.os, "geteuid", return_value=1000), \
                 patch.dict(local.os.environ, {"GITHUB_ACTIONS": "false"}), \
                 patch.object(local.LocalRun, "command", command), \
                 patch.object(local.LocalRun, "host_check", host), \
                 patch.object(local, "memory_check"), \
                 patch.object(local.LocalRun, "verify_release") as download, \
                 patch.object(local.LocalRun, "build") as build:
                self.assertEqual(0, local.main(["--run-dir", str(target)]))
            download.assert_not_called()
            build.assert_not_called()
            receipt = json.loads((target / "evidence/local-receipt.json").read_text())
            self.assertEqual("PREFLIGHT_PASS", receipt["status"])
            self.assertFalse(receipt["guest_boot_proved"])
            self.assertEqual(0, receipt["build_attempt_count"])


if __name__ == "__main__":
    unittest.main()
