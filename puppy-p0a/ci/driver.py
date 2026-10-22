"""Manual hosted-runner entrypoint. No local build mode or retry loop."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request

from boot import boot_once, sha256


TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parent
PACKET = REPO / "docs/workflow/packets/PUPPF-P0A-002.json"
EXPECTED = "b0417934776c214ca3189c8822b85baf1e71fc262f66ada98bce2092f07c9c9b"


class Blocked(RuntimeError):
    pass


class Failed(RuntimeError):
    pass


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def config_values(path):
    return dict(line.split("=", 1) for line in Path(path).read_text().splitlines()
                if line and not line.startswith("#") and "=" in line)


class HTTPSRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not newurl.startswith("https://"):
            raise Blocked("source download redirected away from HTTPS")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(url, path, maximum_bytes):
    if not url.startswith("https://"):
        raise Blocked("non-HTTPS source URL")
    opener = urllib.request.build_opener(HTTPSRedirect())
    total = 0
    try:
        with opener.open(url, timeout=60) as response, Path(path).open("xb") as out:
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > maximum_bytes:
                    raise Blocked("source download exceeds its size guard")
                out.write(chunk)
    except Exception as exc:
        raise Blocked(f"source download failed ({url}): {exc}") from exc


def valid_signature(status, fingerprint):
    for line in status.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[:2] == ["[GNUPG:]", "VALIDSIG"]:
            if fingerprint in (fields[2], fields[-1]):
                return True
    return False


def is_release_makefile(text):
    return bool(re.search(r"^(?:export\s+)?BR2_VERSION\s*:?=\s*2026\.08$", text, re.M))


def check_checker(path, expected):
    actual = sha256(path)
    if actual != expected:
        raise Blocked("repository packet checker differs from reviewed SHA-256")
    return actual


def unpack_release(archive, destination):
    with tarfile.open(archive, "r:xz") as stream:
        for member in stream.getmembers():
            if Path(member.name).parts[0] != "buildroot-2026.08":
                raise Blocked("unexpected Buildroot archive root")
        stream.extractall(destination, filter="data")
    return Path(destination) / "buildroot-2026.08"


class Run:
    def __init__(self, evidence):
        self.evidence = Path(evidence)
        self.commands = []
        self.manifest = {"task_id": "PUPPF-P0A-002", "started_at_utc": utc(),
                         "commands": self.commands, "build_attempt_count": 0,
                         "source_authentication": "NOT_RUN", "host": {},
                         "artifact_manifest": [], "bit_identical_rebuild_tested": False}

    def save(self):
        write_json(self.evidence / "build-manifest.json", self.manifest)

    def command(self, argv, log, cwd=REPO, timeout=120, blocked=False):
        row = {"argv": list(map(str, argv)), "cwd": str(cwd), "log": log,
               "started_at_utc": utc(), "timeout_seconds": timeout}
        self.commands.append(row)
        self.save()
        start = time.monotonic()
        with (self.evidence / log).open("wb") as output:
            proc = subprocess.Popen(row["argv"], cwd=cwd, stdin=subprocess.DEVNULL,
                                    stdout=output, stderr=subprocess.STDOUT,
                                    start_new_session=True)
            try:
                code = proc.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                code = -signal.SIGTERM
        row.update(exit_code=code, elapsed_seconds=time.monotonic() - start)
        self.save()
        if code != 0:
            error = Blocked if blocked else Failed
            raise error(f"command failed ({code}); see {log}")
        return (self.evidence / log).read_text(errors="replace")

    def verify_release(self, lock, work):
        release = lock["buildroot"]
        verification = self.evidence / "source-verification"
        verification.mkdir()
        archive = work / "buildroot-2026.08.tar.xz"
        signature = verification / "buildroot-2026.08.tar.xz.sign"
        key = verification / "release-key.asc"
        download(release["archive_url"], archive, 100_000_000)
        download(release["signature_url"], signature, 1_000_000)
        download(release["public_key_url"], key, 1_000_000)
        homedir = work / "gnupg"
        homedir.mkdir(mode=0o700)
        gpg = ["gpg", "--homedir", str(homedir), "--batch", "--no-auto-key-retrieve"]
        listing = self.command(gpg + ["--with-colons", "--import-options", "show-only",
                                      "--import", str(key)], "key-inspection.log", blocked=True)
        fingerprints = [line.split(":")[9] for line in listing.splitlines()
                        if line.startswith("fpr:")]
        if release["signer_fingerprint"] not in fingerprints:
            raise Blocked("downloaded public key does not match pinned fingerprint")
        self.command(gpg + ["--import", str(key)], "key-import.log", blocked=True)
        status = self.command(gpg + ["--status-fd", "1", "--verify", str(signature), str(archive)],
                              "archive-verification.log", blocked=True)
        if not valid_signature(status, release["signer_fingerprint"]):
            raise Blocked("release signature lacks expected VALIDSIG signer")
        self.manifest["source_authentication"] = {
            "status": "VERIFIED", "method": "detached OpenPGP signature with pinned fingerprint",
            "archive_sha256": sha256(archive), "signature_sha256": sha256(signature),
            "public_key_sha256": sha256(key), "signer_fingerprint": release["signer_fingerprint"],
            "archive_url": release["archive_url"], "signature_url": release["signature_url"],
            "key_url": release["public_key_url"], "verified_at_utc": utc()}
        self.save()
        return unpack_release(archive, work)

    def host_check(self):
        required = ["qemu-system-x86_64", "gcc", "g++", "make", "cpio", "rsync", "bc",
                    "flex", "bison", "git", "python3", "gpg", "readelf", "file", "wget",
                    "tar", "gzip", "bzip2", "xz", "unzip", "perl", "patch", "awk",
                    "which", "sed", "diff", "cmp", "find", "xargs", "bash", "as", "ld"]
        missing = [name for name in required if shutil.which(name) is None]
        self.manifest["host"] = {
            "platform": platform.platform(), "machine": platform.machine(),
            "cpu_count": os.cpu_count(), "free_disk_bytes": shutil.disk_usage(self.evidence).free,
            "memory_observation": Path("/proc/meminfo").read_text(),
            "tools": {name: shutil.which(name) for name in required},
            "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "github_server_url": os.environ.get("GITHUB_SERVER_URL"),
            "github_repository": os.environ.get("GITHUB_REPOSITORY"),
            "github_sha": os.environ.get("GITHUB_SHA"),
            "runner_os": os.environ.get("RUNNER_OS"),
            "runner_arch": os.environ.get("RUNNER_ARCH"),
            "runner_image_version": os.environ.get("ImageVersion"),
            "runner_image_os": os.environ.get("ImageOS")}
        self.save()
        if missing:
            raise Blocked("missing host tools after workflow install: " + ", ".join(missing))
        if platform.machine() != "x86_64":
            raise Blocked("runner architecture is not x86-64")
        if self.manifest["host"]["free_disk_bytes"] < 10 * 1024**3:
            raise Blocked("less than 10 GiB scratch free; request runner disk review")
        self.command(["perl", "-e", "require Data::Dumper; require English; require ExtUtils::MakeMaker; "
                      "require Thread::Queue; require FindBin; require IPC::Cmd;"],
                     "host-perl-modules.log", blocked=True)
        for tool in ["qemu-system-x86_64", "gcc", "g++", "make", "git", "gpg", "python3"]:
            self.command([tool, "--version"], "host-" + tool + ".log", blocked=True)

    def build(self, root, lock, work):
        if not is_release_makefile((root / "Makefile").read_text()):
            raise Blocked("signed archive does not declare Buildroot 2026.08")
        # These hashes come from the signed distribution, not a changed expectation.
        for name, hashfile in [("linux", root / "board/qemu/patches/linux/linux.hash"),
                               ("busybox", root / "package/busybox/busybox.hash")]:
            expected = lock[name]
            lines = [line.split() for line in hashfile.read_text().splitlines()]
            if ["sha256", expected["sha256"], expected["archive"]] not in lines:
                raise Blocked(f"signed distribution {name} pin differs from reviewed lock")
        if not re.search(r"^BUSYBOX_VERSION\s*=\s*1\.38\.0$",
                         (root / "package/busybox/busybox.mk").read_text(), re.M):
            raise Blocked("signed distribution has an unexpected BusyBox version")
        output, downloads = work / "output", work / "downloads"
        common = ["make", "-C", str(root), "O=" + str(output),
                  "BR2_EXTERNAL=" + str(TASK / "buildroot-external"),
                  "BR2_DL_DIR=" + str(downloads)]
        self.command(common + ["puppf_defconfig"], "buildroot-configure.log", timeout=180)
        self.manifest["build_attempt_count"] = 1
        self.save()
        self.command(common + ["-j" + str(min(4, os.cpu_count() or 1))], "build.log", timeout=8400)
        self.command(common + ["--no-print-directory", "-s", "show-info"], "package-info.json")
        configs = self.evidence / "configs"
        configs.mkdir()
        linux = output / "build/linux-6.18.7"
        busybox = output / "build/busybox-1.38.0"
        for path, name in [(output / ".config", "buildroot.config"),
                           (linux / ".config", "linux.config"),
                           (busybox / ".config", "busybox.config")]:
            shutil.copyfile(path, configs / name)
        br, kernel, bb = (config_values(configs / n) for n in
                          ["buildroot.config", "linux.config", "busybox.config"])
        if (br.get("BR2_STATIC_LIBS") != "y" or bb.get("CONFIG_STATIC") != "y"
                or kernel.get("CONFIG_NET") in ("y", "m")
                or kernel.get("CONFIG_DRM") in ("y", "m")
                or kernel.get("CONFIG_SERIAL_8250_CONSOLE") != "y"
                or kernel.get("CONFIG_PROC_FS") != "y"
                or any(br.get(k) == "y" for k in ["BR2_PACKAGE_PYTHON3", "BR2_PACKAGE_XORG7", "BR2_PACKAGE_OPENSSH"])):
            raise Failed("resolved configuration violates minimal static/no-network runtime")
        executable = output / "target/bin/busybox"
        elf = self.command(["readelf", "-l", str(executable)], "busybox-program-headers.log")
        dynamic = self.command(["readelf", "-d", str(executable)], "busybox-dynamic-section.log")
        if re.search(r"\bINTERP\b", elf) or "(NEEDED)" in dynamic:
            raise Failed("BusyBox is not a self-contained static ELF")
        compilers = list((output / "host/bin").glob("x86_64-*-gcc"))
        if not compilers:
            raise Failed("target toolchain version unavailable")
        self.command([str(compilers[0]), "--version"], "target-toolchain.log")
        artifact_dir = self.evidence / "artifacts"
        artifact_dir.mkdir()
        artifacts = []
        for filename in ["bzImage", "rootfs.cpio.gz"]:
            source = output / "images" / filename
            if not source.is_file() or source.stat().st_size == 0:
                raise Failed("missing real artifact " + filename)
            shutil.copyfile(source, artifact_dir / filename)
            artifacts.append({"name": filename, "bytes": source.stat().st_size,
                              "sha256": sha256(source), "retained_location": "artifacts/" + filename})
        self.manifest["artifact_manifest"] = artifacts
        self.save()
        write_json(self.evidence / "artifacts.json", {
            "artifacts": artifacts, "combined_payload_bytes": sum(a["bytes"] for a in artifacts),
            "complete_iso_bytes": None, "ram_allocation_mib": 128,
            "minimum_ram_mib": None, "guest_resident_memory_bytes": None,
            "storage": "GitHub workflow artifact, retention configured by route-owned YAML"})
        if sum(a["bytes"] for a in artifacts) >= 100_000_000:
            raise Failed("kernel plus compressed initramfs exceeds strict payload ceiling")
        with (artifact_dir / "rootfs.cpio.gz").open("rb") as f:
            if f.read(2) != b"\x1f\x8b":
                raise Failed("initramfs is not gzip compressed")
        # Hash every downloaded source retained in the clean Buildroot download tree.
        self.manifest["downloads"] = [
            {"path": str(p.relative_to(downloads)), "bytes": p.stat().st_size, "sha256": sha256(p)}
            for p in sorted(downloads.rglob("*"))
            if p.is_file() and p.stat().st_size and not p.name.endswith(".lock")]
        for name in ["linux", "busybox"]:
            source = next((p for p in downloads.rglob(lock[name]["archive"]) if p.is_file()), None)
            if source is None or sha256(source) != lock[name]["sha256"]:
                raise Failed(name + " archive does not match reviewed source pin")
        self.manifest["artifact_manifest"] = artifacts
        self.manifest["source_versions"] = {
            "Buildroot": "2026.08", "Linux": "6.18.7", "BusyBox": "1.38.0",
            "other_packages": "package-info.json", "toolchain": "target-toolchain.log"}
        self.save()
        return artifact_dir / "bzImage", artifact_dir / "rootfs.cpio.gz"


def main():
    # Reject accidental local execution before creating a runner receipt.
    if (os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("PUPPF_MODE") != "build"
            or not os.environ.get("PUPPF_EVIDENCE_DIR") or not os.environ.get("RUNNER_TEMP")):
        print("Runner-only build entrypoint; requires Mark's manual Actions build dispatch.", file=sys.stderr)
        return 2
    evidence = Path(os.environ["PUPPF_EVIDENCE_DIR"]).resolve()
    if REPO == evidence or REPO in evidence.parents:
        print("Evidence must be outside the checkout.", file=sys.stderr)
        return 2
    evidence.mkdir(parents=True, exist_ok=True)
    if (evidence / "receipt.json").exists() or (evidence / "run-1").exists():
        print("Existing dispatch evidence; refusing overwrite/retry.", file=sys.stderr)
        return 2
    run = Run(evidence)
    start = time.monotonic()
    receipt = json.loads((REPO / "docs/workflow/receipt-template.json").read_text())
    receipt.update(task_id="PUPPF-P0A-002", worker_role="Codex", attempt_count=1,
                   repair_attempt_count=0, started_at_utc=utc(), usage=None,
                   cost_coverage="unknown", cost_items=[], status="BLOCKED",
                   model_requested=None, model_observed=None,
                   model_identity_source="Provider/runtime identity telemetry unavailable",
                   source_base_commit="15e458aa99b3f1345d9120b476f8c23301a2e235",
                   packet_sha256=EXPECTED, packet_hash_provenance="as_recorded")
    exit_code = 2
    try:
        commit = run.command(["git", "rev-parse", "HEAD"], "checkout-commit.log").strip()
        receipt.update(implementation_start_commit=commit, result_commit=commit)
        run.manifest["checkout_commit"] = commit
        checker = REPO / "tools/workflow/check_packet.py"
        checker_hash = sha256(checker)
        receipt["packet_checker_sha256"] = checker_hash
        lock = json.loads((TASK / "source-lock.json").read_text())
        check_checker(checker, lock["packet_checker_sha256"])
        if os.environ.get("PUPPF_EXPECTED_PACKET_SHA256") != EXPECTED:
            raise Blocked("workflow's independent packet digest differs from dispatch")
        run.command([sys.executable, str(checker), str(PACKET), EXPECTED], "packet-check.log", blocked=True)
        if sha256(PACKET) != EXPECTED:
            raise Blocked("independent exact-byte packet check failed")
        receipt.update(packet_hash_provenance="verified", packet_hash_verification={
            "actual_sha256": EXPECTED, "tool": "tools/workflow/check_packet.py",
            "checker_sha256": checker_hash, "verified_at_utc": utc()})
        run.manifest["source_lock"] = lock
        run.manifest["implementation_files"] = [
            {"path": str(p.relative_to(REPO)), "sha256": sha256(p)}
            for p in sorted(TASK.rglob("*")) if p.is_file() and "__pycache__" not in p.parts]
        run.host_check()
        run.command([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(TASK / "tests"), "-v"],
                    "checker-fixtures.log")
        write_json(evidence / "fixture-results.json", {"status": "PASS", "evidence_kind": "checker_self_test_only",
                                                     "log": "checker-fixtures.log", "guest_boot_proved": False})
        work = Path(tempfile.mkdtemp(prefix="puppf-p0a-", dir=os.environ["RUNNER_TEMP"]))
        run.manifest["scratch_directory"] = str(work)
        root = run.verify_release(lock, work)
        kernel, initramfs = run.build(root, lock, work)
        results = []
        for number in [1, 2]:
            expected_hashes = {"kernel": run.manifest["artifact_manifest"][0]["sha256"],
                               "initramfs": run.manifest["artifact_manifest"][1]["sha256"]}
            if {"kernel": sha256(kernel), "initramfs": sha256(initramfs)} != expected_hashes:
                raise Failed("artifact bytes changed before boot " + str(number))
            result = boot_once(kernel, initramfs, evidence / f"run-{number}")
            results.append(result)
            if result["status"] != "PASS":
                raise Failed(f"boot {number} acceptance failed; see run-{number}/test-results.json")
        if results[0]["artifact_sha256_before"] != results[1]["artifact_sha256_before"]:
            raise Failed("artifacts changed between independent boots")
        write_json(evidence / "cross-run-comparison.json", {
            "status": "PASS", "same_artifact_hashes": True,
            "run_1": results[0], "run_2": results[1],
            "acceptance_authority": "Z review and Mark acceptance remain pending"})
        receipt.update(status="PASS", stop_reason="Two boot checks passed; STOP for Z review and Mark acceptance.",
                       test_evidence=[{"path": f"run-{n}/test-results.json", "status": "PASS"} for n in [1, 2]])
        exit_code = 0
    except Blocked as exc:
        receipt.update(status="BLOCKED", stop_reason=str(exc))
    except BaseException as exc:
        receipt.update(status="FAIL", stop_reason=f"{type(exc).__name__}: {exc}")
        exit_code = 1
    finally:
        run.save()
        receipt.update(finished_at_utc=utc(), elapsed_seconds=time.monotonic() - start,
                       build_attempt_count=run.manifest["build_attempt_count"],
                       artifact_manifest=run.manifest["artifact_manifest"],
                       cost_coverage_explanation="Caller telemetry unavailable; no inferred zero cost or savings.")
        write_json(evidence / "receipt.json", receipt)
        files = [{"path": str(p.relative_to(evidence)), "bytes": p.stat().st_size, "sha256": sha256(p)}
                 for p in sorted(evidence.rglob("*")) if p.is_file() and p.name != "evidence-manifest.json"
                 and p.name not in ["build-console.log", "runner-preflight.log"]]
        write_json(evidence / "evidence-manifest.json", {"files": files,
                   "exclusions": ["evidence-manifest.json (self reference)", "build-console.log and runner-preflight.log (workflow-owned live logs)"]})
        print(json.dumps({"task_id": "PUPPF-P0A-002", "status": receipt["status"],
                          "reason": receipt["stop_reason"], "evidence_dir": str(evidence)}))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
