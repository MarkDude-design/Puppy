#!/usr/bin/env python3
"""Launch the accepted Puppf images locally, without a build or network request."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import zipfile


PIN_FILE = Path(__file__).with_name("accepted-build.json")
MAX_ZIP_BYTES = 64 * 1024 * 1024


class LaunchError(Exception):
    pass


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def prepare_images(bundle, destination, pins):
    """Read just two known members; never extract archive paths or execute logs."""
    bundle, destination = Path(bundle), Path(destination)
    # Hold one descriptor from hashing through member reads, so replacing the
    # bundle pathname cannot switch the authenticated file underneath us.
    with bundle.open("rb") as source:
        source.seek(0, 2)
        size = source.tell()
        if size > MAX_ZIP_BYTES:
            raise LaunchError("Evidence ZIP exceeds the 64 MiB input limit.")
        source.seek(0)
        h = hashlib.sha256()
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
        if h.hexdigest() != pins["evidence_zip_sha256"]:
            raise LaunchError("Evidence ZIP differs from accepted build #11; download the original ZIP.")
        source.seek(0)
        with zipfile.ZipFile(source) as archive:
            names = archive.namelist()
            images = []
            for row in pins["images"]:
                if names.count(row["member"]) != 1:
                    raise LaunchError("Missing or duplicate image member: " + row["member"])
                info = archive.getinfo(row["member"])
                if info.file_size != row["bytes"] or info.flag_bits & 1:
                    raise LaunchError("Unexpected image size or encrypted member.")
                with archive.open(info) as image:
                    data = image.read(row["bytes"] + 1)
                if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
                    raise LaunchError("Image bytes differ from the accepted build.")
                path = destination / row["filename"]
                with path.open("xb") as output:
                    output.write(data)
                images.append(path)
    return images


def qemu_command(executable, kernel, initramfs):
    return [executable, "-machine", "pc,accel=tcg", "-cpu", "qemu64", "-smp", "1",
            "-m", "128", "-nodefaults", "-no-user-config", "-display", "none", "-monitor", "none",
            "-chardev", "stdio,id=puppf_console,signal=on", "-serial", "chardev:puppf_console",
            "-nic", "none", "-no-reboot", "-kernel", str(kernel), "-initrd", str(initramfs),
            "-append", "console=ttyS0,115200 rdinit=/init panic=-1 quiet"]


def run_console(argv):
    # Restore the user's terminal even if QEMU crashes or Ctrl+C interrupts us.
    import termios
    original = termios.tcgetattr(sys.stdin.fileno())
    proc = None
    try:
        proc = subprocess.Popen(argv)  # Inherit the real terminal; no shell=True.
        return proc.wait()
    except KeyboardInterrupt:
        print("\nStopping Puppf; guest changes are discarded.", flush=True)
        return 0
    finally:
        # Repeated Ctrl+C must not interrupt escalation or terminal restoration.
        previous_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            if proc is not None and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=3)
        finally:
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, original)
            finally:
                signal.signal(signal.SIGINT, previous_handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True,
                        help="Original accepted build #11 evidence ZIP (no login or downloads by this command)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--verify-only", action="store_true", help="Verify ZIP and image bytes, then exit")
    mode.add_argument("--check", action="store_true", help="Also check host/QEMU prerequisites; do not boot")
    args = parser.parse_args(argv)
    try:
        pins = json.loads(PIN_FILE.read_text())
        with tempfile.TemporaryDirectory(prefix="puppf-") as temp:
            kernel, initramfs = prepare_images(args.evidence, temp, pins)
            print("Verified accepted build #11: kernel + initramfs = 4,040,866 bytes.", flush=True)
            if args.verify_only:
                return 0
            if sys.platform not in ("linux", "darwin"):
                raise LaunchError("This launcher needs Linux or macOS. On Windows, use a WSL terminal.")
            executable = shutil.which("qemu-system-x86_64")
            if executable is None:
                raise LaunchError("qemu-system-x86_64 is missing. Install QEMU using your host's package manager; see LAUNCH.md.")
            if args.check:
                print("Host prerequisite found: " + executable)
                print("QEMU has not been started; interactive demo remains a separate check.")
                return 0
            if not sys.stdin.isatty() or not sys.stdout.isatty():
                raise LaunchError("Open an interactive terminal to launch Puppf; piped input/output is unsupported.")
            print("Puppf: disposable shell, 128 MiB RAM, no network or host drives.")
            print("At PUPPF#, type stty echo and Enter once to see subsequent commands as you type.")
            print("Try: uname -a  |  cat /proc/uptime  |  echo Hello_Puppf")
            print("Press Ctrl+C to stop the VM and return here. Guest 'exit' restarts its shell.", flush=True)
            return run_console(qemu_command(executable, kernel, initramfs))
    except (LaunchError, OSError, ValueError, KeyError, zipfile.BadZipFile, RuntimeError) as error:
        print("Puppf: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
