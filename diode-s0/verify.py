#!/usr/bin/env python3
"""Automated S0 verification only; no model, network, guest or build."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from diode import canonical, exclusive_file, run_mock

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
EXPECTED = "7f80843cb214413532c13258e1ca29c093e82d48a8d09c078289175f6b46a611"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, required=True,
                        help="Fresh directory; parent must already exist")
    args = parser.parse_args()
    root = args.evidence_dir
    root.mkdir(mode=0o700)
    packet = REPO / "docs/workflow/packets/PUPPF-S0-001.json"
    digest = hashlib.sha256(packet.read_bytes()).hexdigest()
    if digest != EXPECTED:
        raise SystemExit("Packet hash mismatch; no test dispatched")
    exclusive_file(root / "packet-check.txt", canonical({"sha256": digest, "integrity": "PASS"}))
    tests = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s",
                            str(HERE / "tests"), "-v"], capture_output=True)
    exclusive_file(root / "tests.log", tests.stdout + tests.stderr)
    count = re.search(rb"Ran (\d+) tests", tests.stderr)
    results = {"status": "FAIL", "unit_tests": int(count[1]) if count else None,
               "test_exit": tests.returncode, "packet_sha256": digest,
               "guest_boot_proved": False, "evidence_kind": "host_mock_only"}
    if tests.returncode == 0 and count and int(count[1]) > 0:
        one = run_mock(root / "run-1", seed=41)
        two = run_mock(root / "run-2", seed=41)
        a, b = [(root / name / "transcript.log").read_bytes() for name in ("run-1", "run-2")]
        results.update(run_1=one, run_2=two, transcripts_byte_identical=a == b)
        results["status"] = "PASS" if a == b and one == two else "FAIL"
    exclusive_file(root / "test-results.json", canonical(results))
    print(json.dumps(results, indent=2))
    return 0 if results["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
