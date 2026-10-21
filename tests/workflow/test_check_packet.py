#!/usr/bin/env python3
"""Bounded tests of the packet integrity checker; no external dependencies."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "tools/workflow/check_packet.py"
PACKETS = ROOT / "docs/workflow/packets"


def invoke(path, digest):
    return subprocess.run(
        [sys.executable, str(CHECKER), str(path), digest],
        capture_output=True, text=True, timeout=10, check=False,
    )


class CheckerTests(unittest.TestCase):
    def test_checked_repository_packets(self):
        for task in ("PUPPF-P0A-001", "PUPPF-S0-001"):
            with self.subTest(task=task):
                path = PACKETS / (task + ".json")
                digest_file = PACKETS / (task + ".json.sha256")
                line = digest_file.read_text(encoding="ascii").strip().split()
                self.assertEqual(line[1], task + ".json")
                self.assertEqual(len(line[0]), 64)
                output = invoke(path, line[0])
                self.assertEqual(output.returncode, 0, output.stderr)
                payload = json.loads(output.stdout)
                self.assertEqual(payload["task_id"], task)
                self.assertEqual(payload["integrity"], "PASS")

    def test_corrupt_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            good = b'{"task_id":"GOOD"}\n'
            path.write_bytes(good)
            digest = hashlib.sha256(good).hexdigest()
            self.assertEqual(invoke(path, digest).returncode, 0)
            path.write_bytes(good.replace(b"GOOD", b"EVIL"))
            self.assertNotEqual(invoke(path, digest).returncode, 0)

    def test_invalid_json_rejected_even_with_matching_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            raw = b'{broken}\n'
            path.write_bytes(raw)
            self.assertNotEqual(invoke(path, hashlib.sha256(raw).hexdigest()).returncode, 0)

    def test_empty_task_id_rejected_even_with_matching_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            raw = b'{"task_id":""}\n'
            path.write_bytes(raw)
            self.assertNotEqual(invoke(path, hashlib.sha256(raw).hexdigest()).returncode, 0)

    def test_bad_digest_format_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            path.write_text('{"task_id":"A"}\n', encoding="ascii")
            self.assertNotEqual(invoke(path, "not-a-digest").returncode, 0)


if __name__ == "__main__":
    unittest.main()
