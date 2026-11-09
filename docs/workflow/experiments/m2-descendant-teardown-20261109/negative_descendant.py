#!/usr/bin/env python3
"""Synthetic negative fixture for PR #21 run_console's direct-child teardown.

No QEMU, accepted image, provider, network, workflow or host installation.
Run: python3 docs/workflow/experiments/m2-descendant-teardown-20261109/negative_descendant.py
Expected as of PR #21: exit 1; live descendant detected and killed by harness.
"""
import os
import pty
import re
import select
import signal
import subprocess
import sys
import time
import termios

# The cleanup structure below is copied from the reviewed PR #21 launcher,
# but the subprocess is an invented Python fixture, NOT a QEMU guest.
child = """import os,sys,subprocess,time
p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"])
print('CHILD',os.getpid(),'DESC',p.pid,flush=True)
time.sleep(30)
"""
wrapper = """import subprocess,sys,termios,signal
original=termios.tcgetattr(sys.stdin.fileno());proc=None
try:
 proc=subprocess.Popen([sys.executable,'-u','-c',sys.argv[1]])
 proc.wait()
except KeyboardInterrupt:
 print('STOPPING',flush=True)
finally:
 previous_handler=signal.signal(signal.SIGINT,signal.SIG_IGN)
 try:
  if proc is not None and proc.poll() is None:
   proc.terminate()
   try:proc.wait(timeout=3)
   except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=3)
 finally:
  try:termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,original)
  finally:signal.signal(signal.SIGINT,previous_handler)
print('RESTORED',flush=True)
"""
master, slave = pty.openpty()
process = subprocess.Popen(
    [sys.executable, "-u", "-c", wrapper, child],
    stdin=slave, stdout=slave, stderr=slave, start_new_session=True)
os.close(slave)
output = b""
descendant = None
try:
    until = time.monotonic() + 5
    while time.monotonic() < until:
        readable, _, _ = select.select([master], [], [], .2)
        if readable:
            try:
                output += os.read(master, 4096)
            except OSError:
                break
            match = re.search(rb"CHILD (\d+) DESC (\d+)", output)
            if match:
                descendant = int(match.group(2))
                break
    if descendant is None:
        raise RuntimeError("Fixture did not start a descendant")
    os.kill(process.pid, signal.SIGINT)
    try:
        process.wait(timeout=4)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    time.sleep(.15)
    try:
        with open(f"/proc/{descendant}/stat", encoding="utf-8") as proc_stat:
            state = proc_stat.read().split(") ")[1][0]
    except FileNotFoundError:
        state = "absent"
    print("wrapper_exit", process.returncode, "descendant_state", state)
    print("captured", repr(output[-300:]))
    if state not in ("absent", "Z"):
        print("FAIL: direct-child teardown left synthetic descendant alive")
        sys.exit(1)
    print("PASS: no live descendant")
finally:
    if descendant is not None:
        try:
            os.kill(descendant, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process.poll() is None:
        process.kill()
        process.wait()
    os.close(master)
