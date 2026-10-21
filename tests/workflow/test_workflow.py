"""Evidence and cost aggregation fixture tests, independent of build packets."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "tools/workflow/check_packet.py"
COST = ROOT / "tools/workflow/cost_report.py"


def check(path, digest):
    return subprocess.run([sys.executable, str(CHECKER), str(path), digest],
                          capture_output=True, text=True, timeout=10)


def receipt(task, value, complete, accepted=False):
    return {"task_id": task, "status": "ACCEPTED" if accepted else "FAILED",
            "review": {"decision": "ACCEPTED" if accepted else "REJECTED"},
            "acceptance": {"authority": "Mark", "decision": "ACCEPTED" if accepted else "PENDING"},
            "cost_coverage": "complete" if complete else "unknown",
            "cost_coverage_explanation": "all lanes accounted" if complete else None,
            "cost_items": [{"label": "all attributable work", "cost_usd": value}]}


class IntegrityFixtures(unittest.TestCase):
    def test_hash_correct_and_wrong(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "p.json"
            data = b'{"task_id":"X"}\n'
            path.write_bytes(data)
            digest = hashlib.sha256(data).hexdigest()
            self.assertEqual(check(path, digest).returncode, 0)
            path.write_bytes(data.replace(b'"X"', b'"Y"'))
            self.assertNotEqual(check(path, digest).returncode, 0)

    def test_matching_hash_invalid_packet(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "p.json"
            data = b'{"task_id":""}\n'
            path.write_bytes(data)
            self.assertNotEqual(check(path, hashlib.sha256(data).hexdigest()).returncode, 0)

    def test_bad_digest_format(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "p.json"
            path.write_text('{"task_id":"X"}', encoding="ascii")
            self.assertNotEqual(check(path, "invalid-hash").returncode, 0)


class CostFixtures(unittest.TestCase):
    def run_cost(self, receipts):
        with tempfile.TemporaryDirectory() as d:
            paths = []
            for i, r in enumerate(receipts):
                path = Path(d) / (str(i) + ".json")
                path.write_text(json.dumps(r), encoding="utf-8")
                paths.append(str(path))
            p = subprocess.run([sys.executable, str(COST), *paths],
                               capture_output=True, text=True, timeout=10)
            return p, json.loads(p.stdout) if p.returncode == 0 else None

    def test_one_accepted_plus_failed_attempt_costs(self):
        p, result = self.run_cost([receipt("A", "1.20", True, True),
                                   receipt("B", "0.30", True)])
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(result["accepted_result_count"], 1)
        self.assertEqual(result["cost_per_accepted_result_usd"], "1.50")

    def test_unknown_cost_not_zero(self):
        p, result = self.run_cost([receipt("A", None, False, True)])
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIsNone(result["total_attributable_cost_usd"])
        self.assertIsNone(result["cost_per_accepted_result_usd"])

    def test_no_accepted_result_not_divided(self):
        p, result = self.run_cost([receipt("A", "0", True)])
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIsNone(result["cost_per_accepted_result_usd"])

    def test_mark_and_reviewer_both_required(self):
        x = receipt("A", "0", True, True)
        x["acceptance"]["decision"] = "PENDING"
        p, result = self.run_cost([x])
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(result["accepted_result_count"], 0)

    def test_duplicate_task_rejected(self):
        p, _ = self.run_cost([receipt("A", "1", True), receipt("A", "2", True)])
        self.assertNotEqual(p.returncode, 0)


if __name__ == "__main__":
    unittest.main()
