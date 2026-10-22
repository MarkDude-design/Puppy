"""Synthetic observations test the checker; none is a QEMU boot claim."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ci"))
from acceptance import check_run
from boot import qemu_argv, shell_command


class AcceptanceFixtures(unittest.TestCase):
    def setUp(self):
        self.observation = json.loads((Path(__file__).parent / "fixtures/valid-observation.json").read_text())

    def assert_rejected(self, observation=None, contains=None):
        result = check_run(**(observation or self.observation))
        self.assertEqual("FAIL", result["status"], result)
        if contains:
            self.assertTrue(any(contains in error for error in result["errors"]), result)

    def test_valid_control(self):
        self.assertEqual("PASS", check_run(**self.observation)["status"])

    def test_retired_240_second_floor_is_not_reintroduced(self):
        self.observation["events"][-2].update(text="HELLO seq=2 uptime_s=116", at_s=116)
        self.observation["events"][-1].update(text="HELLO seq=3 uptime_s=231", at_s=231)
        self.observation["elapsed"] = 232
        self.assertEqual("PASS", check_run(**self.observation)["status"])

    def test_missing_heartbeat(self):
        self.observation["events"].pop()
        self.assert_rejected(contains="sequences")

    def test_reordered_heartbeat(self):
        self.observation["events"][-2]["text"] = "HELLO seq=3 uptime_s=121"
        self.observation["events"][-1]["text"] = "HELLO seq=2 uptime_s=241"
        self.assert_rejected(contains="sequences")

    def test_duplicate_and_extra_heartbeat(self):
        for line in ["HELLO seq=2 uptime_s=241", "HELLO seq=4 uptime_s=241"]:
            with self.subTest(line=line):
                observation = copy.deepcopy(self.observation)
                observation["events"].append({"at_s": 241.5, "text": line})
                self.assert_rejected(observation, "sequences")

    def test_malformed_and_negative_uptime(self):
        for uptime in ["oops", "-1", "1.5", "nan", "01"]:
            with self.subTest(uptime=uptime):
                observation = copy.deepcopy(self.observation)
                observation["events"][1]["text"] = "HELLO seq=1 uptime_s=" + uptime
                self.assert_rejected(observation, "malformed")

    def test_absolute_first_uptime_not_init_relative(self):
        self.observation["events"][1]["text"] = "HELLO seq=1 uptime_s=16"
        self.assert_rejected(contains="absolute")

    def test_guest_interval(self):
        self.observation["events"][-1]["text"] = "HELLO seq=3 uptime_s=247"
        self.assert_rejected(contains="guest uptime interval")

    def test_host_interval_independent_of_guest(self):
        self.observation["events"][-1]["at_s"] = 280
        self.observation["elapsed"] = 281
        self.assert_rejected(contains="host arrival")

    def test_watchdog(self):
        self.observation["timed_out"] = True
        self.assert_rejected(contains="watchdog")

    def test_missing_shell_output(self):
        self.observation["events"].pop(3)
        self.assert_rejected(contains="shell token")

    def test_echo_only_is_not_output(self):
        # Full token visible in an echoed command, with no emitted output line.
        self.observation["events"][3]["text"] = "PUPPF# printf '%s\\n' '" + self.observation["token"] + "'"
        self.assert_rejected(contains="shell token")

    def test_duplicate_shell_output(self):
        self.observation["events"].insert(4, {"at_s": 3.5, "text": self.observation["token"]})
        self.assert_rejected(contains="shell token")

    def test_missing_and_late_prompt(self):
        for prompt in [None, 90.01]:
            with self.subTest(prompt=prompt):
                observation = copy.deepcopy(self.observation)
                observation["prompt_at"] = prompt
                self.assert_rejected(observation, "shell prompt")

    def test_output_before_probe_cannot_pass(self):
        self.observation["token_sent_at"] = 4
        self.assert_rejected(contains="shell token")

    def test_qemu_exit_is_failure(self):
        self.observation["qemu_exited"] = True
        self.assert_rejected(contains="QEMU exited")

    def test_reboot_and_panic(self):
        for text in ["PUPPF_INIT", "Kernel panic - not syncing", "PUPPF_SHELL_RESTART"]:
            with self.subTest(text=text):
                observation = copy.deepcopy(self.observation)
                observation["events"].append({"at_s": 241.5, "text": text})
                self.assert_rejected(observation)

    def test_invalid_host_clock_data(self):
        for at in [float("nan"), -1, True, 400, 0.1]:
            with self.subTest(at=at):
                observation = copy.deepcopy(self.observation)
                observation["events"][-1]["at_s"] = at
                self.assert_rejected(observation, "host arrival record")

    def test_launcher_has_no_network_or_shares(self):
        argv = qemu_argv("kernel", "initramfs")
        self.assertEqual("128", argv[argv.index("-m") + 1])
        self.assertEqual("none", argv[argv.index("-nic") + 1])
        self.assertIn("-nodefaults", argv)
        self.assertIn("-no-reboot", argv)
        self.assertEqual("pc,accel=tcg", argv[argv.index("-machine") + 1])
        for forbidden in ["-drive", "-hda", "-virtfs", "-fsdev", "-netdev", "-device"]:
            self.assertNotIn(forbidden, argv)

    def test_probe_input_cannot_echo_full_token(self):
        command = shell_command(self.observation["token"])
        self.assertNotIn(self.observation["token"].encode(), command)
        self.assertTrue(command.startswith(b"printf "))


if __name__ == "__main__":
    unittest.main()
