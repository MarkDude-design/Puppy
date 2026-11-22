#!/usr/bin/env python3
"""Native Linux preflight/build. Reuses authentication and boot checks, never CI main()."""
import argparse
import json
import os
from pathlib import Path
import signal
import sys
import time

from driver import (Blocked, Failed, Run, TASK, REPO, PACKET, EXPECTED,
                    check_checker, sha256, utc, write_json)
from boot import boot_once

MIN_AVAILABLE_KIB = 1024 * 1024


class LocalRun(Run):
    def __init__(self, evidence):
        super().__init__(evidence)
        self.manifest.update(execution_mode="native-local", build_jobs=1,
                             build_timeout_seconds=86400)

    def command(self, argv, log, cwd=REPO, timeout=120, blocked=False):
        argv = list(map(str, argv))
        if argv and argv[0] == "make":
            # Buildroot passes BR2_JLEVEL to recursive package builds independently
            # of the top-level make jobserver. Limit BOTH.
            argv = [arg for arg in argv if not arg.startswith("-j")
                    and not arg.startswith("BR2_JLEVEL=")]
            argv += ["-j1", "BR2_JLEVEL=1"]
        if log == "build.log":
            timeout = 86400
        print("Running: " + log, flush=True)
        return super().command(argv, log, cwd=cwd, timeout=timeout, blocked=blocked)


def memory_check():
    values = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value = line.split(":", 1)
        values[key] = int(value.split()[0])
    if values["MemAvailable"] < MIN_AVAILABLE_KIB:
        raise Blocked("Less than 1 GiB available RAM. Close other apps and run a fresh preflight.")
    if values["MemTotal"] < 5 * 1024**2 and values["SwapTotal"] < 2 * 1024**2:
        raise Blocked("Host has under 5 GiB RAM and under 2 GiB swap; add swap before building.")


def local_paths(base):
    base = Path(base).expanduser().resolve()
    if base == REPO or REPO in base.parents:
        raise Blocked("Run directory must be outside the source checkout.")
    # Refuse existing directories, including partial attempts. No automatic retry,
    # cleanup or reuse of another run's downloads/output.
    base.mkdir(parents=True, exist_ok=False)
    evidence, work = base / "evidence", base / "work"
    evidence.mkdir()
    work.mkdir()
    if evidence.stat().st_dev != work.stat().st_dev:
        raise Blocked("Evidence and build work must share a filesystem.")
    return base, evidence, work


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path,
                        help="Fresh directory outside checkout, on internal Linux storage")
    parser.add_argument("--build", action="store_true",
                        help="Authenticate/download, compile once, then run two boot checks")
    args = parser.parse_args(argv)
    if sys.platform != "linux" or os.geteuid() == 0:
        print("Use a regular-user native Linux terminal, without sudo.", file=sys.stderr)
        return 2
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print("This is the local entrypoint; use the existing CI entrypoint in Actions.", file=sys.stderr)
        return 2
    try:
        base, evidence, work = local_paths(args.run_dir)
    except (Blocked, OSError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    run = LocalRun(evidence)
    start = time.monotonic()
    receipt = {"execution_mode": "native-local", "status": "BLOCKED",
               "started_at_utc": utc(), "build_requested": args.build,
               "build_jobs": 1, "acceptance": "NOT_DECLARED",
               "model_cost": None, "guest_boot_proved": False}
    code = 2
    stage = "preflight"
    old_term = signal.getsignal(signal.SIGTERM)
    # Run.command handles KeyboardInterrupt by terminating its subprocess group.
    def interrupt(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupt)
    try:
        receipt["checkout_commit"] = run.command(
            ["git", "rev-parse", "HEAD"], "checkout-commit.log").strip()
        dirty = run.command(["git", "status", "--porcelain", "--untracked-files=normal"],
                            "checkout-status.log").strip()
        if dirty:
            raise Blocked("Source checkout is dirty; preserve it and use a clean checkout.")
        lock = json.loads((TASK / "source-lock.json").read_text())
        checker = REPO / "tools/workflow/check_packet.py"
        check_checker(checker, lock["packet_checker_sha256"])
        if sha256(PACKET) != EXPECTED:
            raise Blocked("Frozen packet SHA-256 differs.")
        run.command([sys.executable, str(checker), str(PACKET), EXPECTED],
                    "packet-check.log", blocked=True)
        run.manifest.update(source_lock=lock, checkout_commit=receipt["checkout_commit"],
                            scratch_directory=str(work),
                            implementation_files=[
                                {"path": str(p.relative_to(REPO)), "sha256": sha256(p)}
                                for p in sorted(TASK.rglob("*"))
                                if p.is_file() and "__pycache__" not in p.parts])
        run.host_check()
        # The CI check's 10 GiB threshold remains, local mode is more conservative.
        if run.manifest["host"]["free_disk_bytes"] < 20 * 1024**3:
            raise Blocked("Less than 20 GiB free on the local build filesystem.")
        memory_check()
        run.command([sys.executable, "-B", "-m", "unittest", "discover",
                     "-s", str(TASK / "tests"), "-v"], "checker-fixtures.log", timeout=300)
        receipt["preflight"] = "PASS"
        if not args.build:
            receipt.update(status="PREFLIGHT_PASS",
                           stop_reason="No downloads, compilation or QEMU boot requested.")
            code = 0
        else:
            stage = "source_authentication"
            root = run.verify_release(lock, work)
            stage = "compilation"
            kernel, initramfs = run.build(root, lock, work)
            artifacts_path = evidence / "artifacts.json"
            artifacts = json.loads(artifacts_path.read_text())
            artifacts["storage"] = "local run evidence/artifacts; not uploaded"
            write_json(artifacts_path, artifacts)
            stage = "two_boot_checks"
            results = []
            expected = {"kernel": sha256(kernel), "initramfs": sha256(initramfs)}
            for number in (1, 2):
                if {"kernel": sha256(kernel), "initramfs": sha256(initramfs)} != expected:
                    raise Failed("Artifact changed before boot.")
                result = boot_once(kernel, initramfs, evidence / ("run-" + str(number)))
                results.append(result)
                if result["status"] != "PASS":
                    raise Failed("Boot check failed; see run-" + str(number))
            if results[0]["artifact_sha256_before"] != results[1]["artifact_sha256_before"]:
                raise Failed("Artifacts changed between boots.")
            write_json(evidence / "cross-run-comparison.json",
                       {"status": "PASS", "results": results, "same_artifact_hashes": True})
            receipt.update(status="PASS", guest_boot_proved=True,
                           stop_reason="Local build and two boot checks passed; human review pending.")
            code = 0
    except Blocked as exc:
        receipt.update(status="BLOCKED", stop_reason=str(exc))
    except KeyboardInterrupt:
        receipt.update(status="INTERRUPTED", stop_reason="Stopped by user or SIGTERM.")
        code = 130
    except Exception as exc:
        receipt.update(status="FAIL", stop_reason=type(exc).__name__ + ": " + str(exc))
        code = 1
    finally:
        signal.signal(signal.SIGTERM, old_term)
        run.save()
        receipt.update(stage=stage, finished_at_utc=utc(),
                       elapsed_seconds=time.monotonic() - start,
                       build_attempt_count=run.manifest["build_attempt_count"],
                       artifacts=run.manifest["artifact_manifest"],
                       evidence_dir=str(evidence), work_dir=str(work))
        write_json(evidence / "local-receipt.json", receipt)
        write_json(evidence / "evidence-manifest.json", {
            "files": [{"path": str(p.relative_to(evidence)), "sha256": sha256(p),
                       "bytes": p.stat().st_size}
                      for p in sorted(evidence.rglob("*"))
                      if p.is_file() and p.name != "evidence-manifest.json"]})
        print(json.dumps(receipt, indent=2), flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
