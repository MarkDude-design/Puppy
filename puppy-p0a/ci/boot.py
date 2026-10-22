"""Two-boot building block: actual QEMU serial bytes, never a host emulator."""
import hashlib
import json
import os
from pathlib import Path
import secrets
import selectors
import signal
import subprocess
import time

from acceptance import PROMPT, check_run


def sha256(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def qemu_argv(kernel, initramfs):
    return ["qemu-system-x86_64", "-machine", "pc,accel=tcg", "-cpu", "qemu64",
            "-smp", "1", "-m", "128", "-nodefaults", "-display", "none",
            "-monitor", "none", "-serial", "stdio", "-nic", "none", "-no-reboot",
            "-kernel", str(Path(kernel).resolve()), "-initrd", str(Path(initramfs).resolve()),
            "-append", "console=ttyS0,115200 rdinit=/init panic=-1 quiet"]


def shell_command(token):
    # The full token is absent from input bytes, even if terminal echo is enabled.
    middle = len(token) // 2
    return f"printf '\\n%s%s\\n' '{token[:middle]}' '{token[middle:]}'\n".encode()


def boot_once(kernel, initramfs, directory):
    directory = Path(directory)
    directory.mkdir()  # Existing evidence must never be silently overwritten.
    argv = qemu_argv(kernel, initramfs)
    hashes = {"kernel": sha256(kernel), "initramfs": sha256(initramfs)}
    (directory / "qemu-argv.json").write_text(json.dumps(argv, indent=2) + "\n")
    token = "PUPPF_TOKEN_" + secrets.token_hex(16)
    command = shell_command(token)
    (directory / "shell-probe.json").write_text(json.dumps(
        {"token": token, "command": command.decode(), "not_p0b_ack": True}, indent=2) + "\n")
    events, pending, tail = [], b"", b""
    prompt_at = sent_at = complete_at = None
    timed_out = exited = host_stopped = False
    start = time.monotonic()
    proc = None
    try:
        with (directory / "serial.log").open("wb") as raw, \
                (directory / "serial-events.jsonl").open("w") as arrivals:
            proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, start_new_session=True)
            with selectors.DefaultSelector() as selector:
                os.set_blocking(proc.stdout.fileno(), False)
                selector.register(proc.stdout, selectors.EVENT_READ)
                while True:
                    now = time.monotonic() - start
                    if now >= 390:
                        timed_out = True
                        break
                    if prompt_at is None and now > 90:
                        break
                    if sent_at is not None and now > 90 and not any(e["text"] == token for e in events):
                        break
                    if complete_at is not None and now - complete_at >= 1:
                        break  # Capture a grace interval for immediate extra/duplicate output.
                    for key, _ in selector.select(timeout=0.1):
                        data = os.read(key.fileobj.fileno(), 65536)
                        if not data:
                            exited = True
                            break
                        at = time.monotonic() - start
                        raw.write(data)
                        raw.flush()
                        tail = (tail + data)[-65536:]
                        if prompt_at is None and PROMPT in tail:
                            prompt_at = at
                            proc.stdin.write(command)
                            proc.stdin.flush()
                            sent_at = time.monotonic() - start
                        pending += data
                        while b"\n" in pending:
                            line, pending = pending.split(b"\n", 1)
                            event = {"at_s": at, "text": line.rstrip(b"\r").decode("utf-8", errors="replace")}
                            events.append(event)
                            arrivals.write(json.dumps(event) + "\n")
                        arrivals.flush()
                        count = sum(e["text"].startswith("HELLO") for e in events)
                        if count >= 3 and any(e["text"] == token for e in events):
                            complete_at = complete_at if complete_at is not None else at
                    if exited:
                        break
            elapsed = time.monotonic() - start
            if pending:
                event = {"at_s": elapsed, "text": pending.rstrip(b"\r").decode("utf-8", errors="replace")}
                events.append(event)
                arrivals.write(json.dumps(event) + "\n")
        result = check_run(events, token, prompt_at, sent_at, elapsed, timed_out, exited)
    except Exception as exc:
        result = {"status": "FAIL", "errors": [f"{type(exc).__name__}: {exc}"],
                  "elapsed_s": time.monotonic() - start}
    finally:
        if proc is not None:
            if proc.poll() is None:
                host_stopped = True
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait(timeout=5)
            if proc.stdin:
                try:
                    proc.stdin.close()
                except BrokenPipeError:
                    pass
            if proc.stdout:
                proc.stdout.close()
    result.update({"evidence_kind": "actual_qemu_serial_observation" if proc is not None else "qemu_launch_failure", "qemu_argv": argv,
                   "host_stopped_qemu": host_stopped,
                   "qemu_returncode": proc.returncode if proc is not None else None,
                   "ram_allocation_mib": 128, "artifact_sha256_before": hashes,
                   "artifact_sha256_after": {"kernel": sha256(kernel), "initramfs": sha256(initramfs)},
                   "serial_sha256": sha256(directory / "serial.log"),
                   "guest_resident_memory_bytes": None, "minimum_ram_mib": None})
    if result["artifact_sha256_after"] != hashes:
        result["status"] = "FAIL"
        result["errors"].append("artifact bytes changed during boot")
    if proc is not None and not host_stopped:
        result["status"] = "FAIL"
        result["errors"].append("QEMU ended without the planned host stop")
    (directory / "test-results.json").write_text(json.dumps(result, indent=2) + "\n")
    return result
