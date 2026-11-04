"""Real local pipes/processes, scripted time; never a kernel or QEMU boot.

The child is a local Python serial fixture. A separate control pipe releases
one output fragment at a time, so deadlines and chunk boundaries are reproducible
without sleeping for the guest's four-minute heartbeat sequence. The production
reader, stdin probe, line parser, checker and process-group cleanup still run.
"""
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ci"))
import boot


SERIAL_FIXTURE = r'''
import json
import os
import subprocess
import sys

remainder = b""
with os.fdopen(int(sys.argv[1])) as control:
    for line in control:
        step = json.loads(line)
        if step["action"] == "exit":
            sys.exit(0)
        if step["action"] == "emit":
            output = step["text"].encode()
        elif step["action"] in ("probe", "echo"):
            command = sys.stdin.buffer.readline()
            if step["action"] == "echo":
                output = command
            else:
                # Actual host shell printf, explicitly not guest execution.
                output = subprocess.run(
                    ["/bin/sh"], input=command, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, check=True).stdout
                if "take" in step:
                    output, remainder = output[:step["take"]], output[step["take"]:]
        elif step["action"] == "rest":
            output, remainder = remainder, b""
        else:
            raise RuntimeError("unknown fixture action")
        sys.stdout.buffer.write(output)
        sys.stdout.buffer.flush()
'''


@unittest.skipUnless(os.name == "posix", "process-group harness requires POSIX")
class SerialProcessTests(unittest.TestCase):
    def exercise(self, steps):
        clock = SimpleNamespace(now=0.0)
        processes = []
        control_read, control_write = os.pipe()
        control = os.fdopen(control_write, "w")
        real_popen = subprocess.Popen
        steps = iter(steps)

        def launch(argv, **kwargs):
            proc = real_popen(argv, pass_fds=(control_read,), **kwargs)
            processes.append(proc)
            return proc

        class ScriptedSelector:
            def __enter__(self):
                self.selector = selectors.DefaultSelector()
                return self

            def __exit__(self, *args):
                self.selector.close()

            def register(self, *args):
                return self.selector.register(*args)

            def select(self, timeout):
                try:
                    step = next(steps)
                except StopIteration as error:
                    raise AssertionError("fixture ended before harness stopped") from error
                clock.now = step["at"]
                if step["action"] == "reader_error":
                    raise OSError("scripted serial reader failure")
                if step["action"] == "idle":
                    return []
                control.write(json.dumps(step) + "\n")
                control.flush()
                ready = self.selector.select(timeout=5)
                if not ready:
                    raise AssertionError("local serial fixture failed to respond")
                return ready

        try:
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                for name in ("kernel", "initramfs"):
                    (root / name).write_bytes(b"synthetic payload; not bootable\n")
                argv = [sys.executable, "-u", "-c", SERIAL_FIXTURE, str(control_read)]
                with patch.object(boot, "qemu_argv", return_value=argv), \
                        patch.object(boot.subprocess, "Popen", side_effect=launch), \
                        patch.object(boot, "selectors", SimpleNamespace(
                            DefaultSelector=ScriptedSelector,
                            EVENT_READ=selectors.EVENT_READ)), \
                        patch.object(boot, "time", SimpleNamespace(monotonic=lambda: clock.now)):
                    result = boot.boot_once(root / "kernel", root / "initramfs", root / "run")
                saved = json.loads((root / "run/test-results.json").read_text())
                self.assertEqual(result, saved)
                self.assertEqual(1, len(processes))
                self.assertIsNotNone(processes[0].poll(), "fixture child leaked")
                self.assertTrue(processes[0].stdin.closed)
                self.assertTrue(processes[0].stdout.closed)
                serial = (root / "run/serial.log").read_bytes()
                return result, serial
        finally:
            control.close()
            os.close(control_read)
            for proc in processes:
                if proc.poll() is None:
                    os.killpg(proc.pid, 9)
                    proc.wait(timeout=5)

    def normal_steps(self):
        return [
            {"at": 0.5, "action": "emit", "text": "\nPUPPF_INIT\nHELLO seq=1 uptime_s=1\nPUP"},
            {"at": 1, "action": "emit", "text": "PF# "},
            {"at": 2, "action": "probe", "take": 12},
            {"at": 2.1, "action": "rest"},
            {"at": 120.5, "action": "emit", "text": "\nHELLO seq=2 uptime_s=121\n"},
            {"at": 240.5, "action": "emit", "text": "\nHELLO seq=3 uptime_s=241\n"},
            {"at": 241.6, "action": "idle"},
        ]

    def assert_failed(self, steps, message):
        result, _ = self.exercise(steps)
        self.assertEqual("FAIL", result["status"], result)
        self.assertTrue(any(message in error for error in result["errors"]), result)
        return result

    def test_fragmented_prompt_and_token_pass_with_host_cleanup(self):
        result, serial = self.exercise(self.normal_steps())
        self.assertEqual("PASS", result["status"], result)
        self.assertTrue(result["host_stopped_qemu"])
        self.assertLess(result["qemu_returncode"], 0)
        self.assertIn(b"HELLO seq=3 uptime_s=241\n", serial)
        self.assertEqual([120, 120], result["host_gaps_s"])
        self.assertEqual(result["artifact_sha256_before"], result["artifact_sha256_after"])

    def test_echo_only_process_cannot_prove_shell_output(self):
        steps = self.normal_steps()[:2]
        steps.extend([{"at": 2, "action": "echo"}, {"at": 90.1, "action": "idle"}])
        self.assert_failed(steps, "shell token")

    def test_missing_prompt_stops_and_reaps_process(self):
        steps = [self.normal_steps()[0], {"at": 90.1, "action": "idle"}]
        self.assert_failed(steps, "shell prompt")

    def test_prompt_arriving_across_deadline_fails(self):
        steps = self.normal_steps()
        steps[1]["at"] = 90.01
        self.assert_failed(steps[:2], "shell prompt")

    def test_serial_reader_error_still_reaps_process(self):
        steps = self.normal_steps()[:2]
        steps.append({"at": 2, "action": "reader_error"})
        result = self.assert_failed(steps, "scripted serial reader failure")
        self.assertTrue(result["host_stopped_qemu"])

    def test_process_exit_after_valid_serial_is_failure(self):
        steps = self.normal_steps()
        steps[-1] = {"at": 240.6, "action": "exit"}
        result = self.assert_failed(steps, "QEMU exited")
        self.assertFalse(result["host_stopped_qemu"])
        self.assertEqual(0, result["qemu_returncode"])

    def test_duplicate_heartbeat_during_grace_is_rejected(self):
        steps = self.normal_steps()
        steps.insert(-1, {"at": 240.6, "action": "emit", "text": "HELLO seq=3 uptime_s=241\n"})
        self.assert_failed(steps, "sequences")

    def test_partial_panic_during_grace_is_preserved_and_rejected(self):
        steps = self.normal_steps()
        steps.insert(-1, {"at": 240.6, "action": "emit", "text": "Kernel panic - fixture"})
        result, serial = self.exercise(steps)
        self.assertEqual("FAIL", result["status"], result)
        self.assertIn("guest panic, reboot or shell restart", result["errors"])
        self.assertTrue(serial.endswith(b"Kernel panic - fixture"))

    def test_watchdog_stops_and_reaps_hung_process(self):
        steps = self.normal_steps()[:4]
        steps.append({"at": 390, "action": "idle"})
        result = self.assert_failed(steps, "watchdog")
        self.assertTrue(result["timed_out"])
        self.assertTrue(result["host_stopped_qemu"])


if __name__ == "__main__":
    unittest.main()
