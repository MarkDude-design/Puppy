"""Offline desk-contract fixtures; no API calls or system changes."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "agent_desk" / "desk.py"
QUEUE = ROOT / "docs" / "agent-desk" / "queue.json"
spec = importlib.util.spec_from_file_location("agent_desk_tool", TOOL)
desk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(desk)


def sample():
    return json.loads(QUEUE.read_text(encoding="utf-8"))


class DeskTests(unittest.TestCase):
    def test_initial_two_plus_one(self):
        result = desk.validate(sample())
        self.assertEqual(result["planned_busy_slots"], ["H1", "H2"])
        self.assertEqual(result["standby_slots"], ["R"])
        self.assertEqual(result["actual_dispatches"], 0)

    def test_simulate_h2_to_reserve_no_mutation(self):
        src = sample()
        orig = copy.deepcopy(src)
        result = desk.simulate_failover(src, "H2")
        self.assertEqual(src, orig)
        self.assertTrue(result["simulation_only"])
        self.assertEqual(result["validation"]["planned_busy_slots"], ["H1", "R"])
        self.assertEqual({x["slot"]: x["state"] for x in result["proposal"]["tasks"]}["H2"],
                         "BLOCKED")

    def test_simulate_h1_to_reserve(self):
        result = desk.simulate_failover(sample(), "H1")
        self.assertEqual(result["validation"]["planned_busy_slots"], ["H2", "R"])

    def test_reject_third_ready_without_blocked(self):
        data = sample()
        data["tasks"][2]["state"] = "READY"
        with self.assertRaises(desk.InvalidDesk):
            desk.validate(data)

    def test_reject_duplicate_ids(self):
        data = sample()
        data["tasks"][1]["task_id"] = data["tasks"][0]["task_id"]
        with self.assertRaises(desk.InvalidDesk):
            desk.validate(data)

    def test_reject_same_slot(self):
        data = sample()
        data["tasks"][1]["slot"] = "H1"
        with self.assertRaises(desk.InvalidDesk):
            desk.validate(data)

    def test_reject_spend_authority(self):
        data = sample()
        data["paid_calls_allowed"] = True
        with self.assertRaises(desk.InvalidDesk):
            desk.validate(data)

    def test_reject_provider_in_non_dispatch(self):
        data = sample()
        data["tasks"][0]["provider"] = "example"
        with self.assertRaises(desk.InvalidDesk):
            desk.validate(data)

    def test_reject_fake_usage(self):
        data = sample()
        data["tasks"][1]["cost_usd"] = 0
        with self.assertRaises(desk.InvalidDesk):
            desk.validate(data)

    def test_reject_unsigned_base_ref(self):
        data = sample()
        data["source_commit"] = "main"
        with self.assertRaises(desk.InvalidDesk):
            desk.validate(data)

    def test_bad_failover_target(self):
        with self.assertRaises(desk.InvalidDesk):
            desk.simulate_failover(sample(), "R")

    def test_duplicate_json_key(self):
        with self.assertRaises(desk.InvalidDesk):
            json.loads('{"state":"READY","state":"BLOCKED"}',
                       object_pairs_hook=desk.no_duplicate_keys)

    def test_cli_validate(self):
        run = subprocess.run([sys.executable, str(TOOL), "validate", str(QUEUE)],
                             check=False, capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["actual_dispatches"], 0)

    def test_cli_rehearsal(self):
        run = subprocess.run([sys.executable, str(TOOL), "simulate-failover",
                              str(QUEUE), "--blocked", "H2"],
                             check=False, capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(json.loads(run.stdout)["simulation_only"])


if __name__ == "__main__":
    unittest.main()
