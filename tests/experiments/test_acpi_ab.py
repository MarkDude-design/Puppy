import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / "tools/experiments/acpi_ab.py"
spec = importlib.util.spec_from_file_location("acpi_ab", SCRIPT)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class AcpiExperimentTests(unittest.TestCase):
    def test_candidate_changes_exactly_kernel_append(self):
        control = a.boot.qemu_argv("kernel", "rootfs")
        candidate = a.candidate_argv(control)
        changes = [i for i in range(len(control)) if control[i] != candidate[i]]
        self.assertEqual([control.index("-append") + 1], changes)
        self.assertEqual(control[changes[0]] + " acpi=off", candidate[changes[0]])
        self.assertNotIn("acpi=off", control)

    def test_control_cannot_already_disable_acpi(self):
        with self.assertRaises(ValueError):
            a.candidate_argv(["qemu", "-append", "quiet acpi=off"])

    def fake_boot(self, statuses=None, control_warn=True, candidate_warn=False):
        statuses = iter(statuses or ["PASS"] * 4)
        def run(kernel, initramfs, folder):
            folder.mkdir()
            candidate = "acpi=off" in a.boot.qemu_argv(kernel, initramfs)[-1]
            warning = candidate_warn if candidate else control_warn
            (folder / "serial.log").write_bytes(b"ACPI Error: fixture\n" if warning else b"PUPPF_INIT\n")
            return {"status": next(statuses)}
        return run

    def run_fake(self, statuses=None, **kwargs):
        with tempfile.TemporaryDirectory() as temp:
            report = {"boots": []}
            with patch.object(a, "image_hashes", return_value=a.PINS), \
                 patch.object(a.boot, "boot_once", side_effect=self.fake_boot(statuses, **kwargs)):
                code = a.experiment(Path(temp), Path(temp), report)
            return code, report

    def test_four_functional_boots_and_warning_comparison(self):
        code, result = self.run_fake()
        self.assertEqual(0, code)
        self.assertEqual("PASS", result["status"])
        self.assertEqual([1, 1, 0, 0], [x["acpi_warning_lines"] for x in result["boots"]])

    def test_no_reproduction_stops_before_candidate(self):
        code, result = self.run_fake(control_warn=False)
        self.assertEqual(2, code)
        self.assertEqual("NOT_REPRODUCED", result["status"])
        self.assertEqual(1, len(result["boots"]))

    def test_failed_control_prevents_candidate(self):
        code, result = self.run_fake(statuses=["FAIL"])
        self.assertEqual(1, code)
        self.assertEqual(1, len(result["boots"]))

    def test_candidate_functional_fail_or_warning_is_failure(self):
        for statuses, warn in [(["PASS", "PASS", "FAIL"], False), (None, True)]:
            with self.subTest(statuses=statuses):
                code, result = self.run_fake(statuses, candidate_warn=warn)
                self.assertEqual(1, code)
                self.assertEqual("FAIL", result["status"])
                self.assertEqual(3, len(result["boots"]))

    def test_missing_qemu_and_hash_mismatch_never_boot(self):
        for hash_error in [None, ValueError("fixture hash mismatch")]:
            with self.subTest(hash_error=hash_error), tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "fresh"
                with patch.object(a, "image_hashes", side_effect=hash_error, return_value=a.PINS), \
                     patch.object(a.shutil, "which", return_value=None), \
                     patch.object(a.boot, "boot_once") as boot:
                    self.assertEqual(2, a.main(["--images", temp, "--run-dir", str(path), "--run"]))
                    boot.assert_not_called()
                self.assertEqual("BLOCKED", json.loads((path / "receipt.json").read_text())["status"])

    def test_existing_evidence_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            marker = Path(temp) / "keep"
            marker.write_text("keep")
            self.assertEqual(2, a.main(["--images", temp, "--run-dir", temp, "--run"]))
            self.assertEqual("keep", marker.read_text())


if __name__ == "__main__":
    unittest.main()
