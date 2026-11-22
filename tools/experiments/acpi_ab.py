#!/usr/bin/env python3
"""Pinned-image ACPI A/B experiment; never builds or changes the accepted runtime."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "puppy-p0a/ci"))
import boot

PINS = {"bzImage": "75bb3de22351a5e97c601650210dcbdcbf385ad69c9bd1bfb90b4832a628bfe7",
        "rootfs.cpio.gz": "2d51be705deca6b606c6e2de15311d7669576b52d12e83801e670981aa1c089e"}


def candidate_argv(argv):
    argv = list(argv)
    if argv.count("-append") != 1:
        raise ValueError("Expected one kernel command line")
    index = argv.index("-append") + 1
    if any(word.startswith("acpi=") for word in argv[index].split()):
        raise ValueError("Control already specifies an ACPI mode")
    argv[index] += " acpi=off"
    return argv


def image_hashes(images):
    actual = {name: boot.sha256(images / name) for name in PINS}
    if actual != PINS:
        raise ValueError("Images differ from accepted build #11")
    return actual


def warning_count(serial):
    return len(re.findall(rb"(?m)^(?:ACPI Error:|ACPI: Unable to load)", serial))


def experiment(images, evidence, report):
    kernel, initramfs = images / "bzImage", images / "rootfs.cpio.gz"
    original = boot.qemu_argv
    for mode in ("control", "acpi-off"):
        for number in (1, 2):
            image_hashes(images)
            folder = evidence / (mode + "-" + str(number))
            print("Starting " + folder.name + " (about four minutes)", flush=True)
            if mode == "control":
                result = boot.boot_once(kernel, initramfs, folder)
            else:
                with patch.object(boot, "qemu_argv", side_effect=lambda k, i: candidate_argv(original(k, i))):
                    result = boot.boot_once(kernel, initramfs, folder)
            image_hashes(images)
            warnings = warning_count((folder / "serial.log").read_bytes())
            row = {"mode": mode, "run": number, "status": result["status"],
                   "acpi_warning_lines": warnings,
                   "test_results": folder.name + "/test-results.json"}
            report["boots"].append(row)
            if result["status"] != "PASS":
                report.update(status="FAIL", reason="Functional boot check failed: " + folder.name)
                return 1
            if mode == "control" and warnings == 0:
                report.update(status="NOT_REPRODUCED", reason="Control lacks target warnings; stop without cleanup claim")
                return 2
            if mode == "acpi-off" and warnings:
                report.update(status="FAIL", reason="Candidate still emits target warnings")
                return 1
    report.update(status="PASS", reason="Two controls reproduce warnings; two acpi=off boots pass with no target warnings")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path, help="Fresh directory outside checkout")
    parser.add_argument("--run", action="store_true", help="Perform four real QEMU boots; default is preflight only")
    args = parser.parse_args(argv)
    evidence, images = args.run_dir.expanduser().resolve(), args.images.expanduser().resolve()
    if evidence == REPO or REPO in evidence.parents:
        print("BLOCKED: evidence must be outside checkout", file=sys.stderr)
        return 2
    try:
        evidence.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    report = {"task": "PUPPF-REWRITE1-ACPI-001", "status": "BLOCKED", "boots": [],
              "run_requested": args.run, "source_builds": 0, "acceptance": "NOT_DECLARED",
              "comparison": "Kernel acpi=off only; raw logs retained, no output filtering",
              "limits": "Serial-only QEMU feature-disable candidate, not hardware/root-cause repair"}
    start, code = time.monotonic(), 2
    old_term = signal.getsignal(signal.SIGTERM)
    def interrupt(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupt)
    try:
        report["image_sha256"] = image_hashes(images)
        qemu = shutil.which("qemu-system-x86_64")
        if qemu is None:
            raise ValueError("qemu-system-x86_64 missing; no boot attempted")
        report["qemu_version"] = subprocess.check_output([qemu, "--version"], text=True, timeout=10).splitlines()[0]
        report["checkout_commit"] = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
        if args.run:
            code = experiment(images, evidence, report)
        else:
            report.update(status="PREFLIGHT_PASS", reason="No boots requested")
            code = 0
    except KeyboardInterrupt:
        report.update(status="INTERRUPTED", reason="User/SIGTERM interruption; retain partial boot evidence")
        code = 130
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        report.update(status="BLOCKED", reason=type(exc).__name__ + ": " + str(exc))
    finally:
        signal.signal(signal.SIGTERM, old_term)
        report["elapsed_seconds"] = time.monotonic() - start
        (evidence / "receipt.json").write_text(json.dumps(report, indent=2) + "\n")
        manifest = [{"path": str(p.relative_to(evidence)), "bytes": p.stat().st_size,
                     "sha256": boot.sha256(p)} for p in sorted(evidence.rglob("*")) if p.is_file()]
        (evidence / "sha256-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps(report, indent=2), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
