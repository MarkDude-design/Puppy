#!/usr/bin/env python3
"""POSIX-only synthetic descendant teardown test; no QEMU, no production import.
Reproduces PR #21 run_console body at head 320ed447; compare before reuse.
"""
import os, pty, select, signal, subprocess, sys, termios, time

def run_console(argv):
    import termios
    original = termios.tcgetattr(sys.stdin.fileno())
    proc = None
    try:
        proc = subprocess.Popen(argv)  # Inherit the real terminal; no shell=True.
        return proc.wait()
    except KeyboardInterrupt:
        print("\\nStopping Puppf; guest changes are discarded.", flush=True)
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

if __name__ == "__main__" and len(sys.argv)>1 and sys.argv[1]=="parent":
    grandchild_code='import os,signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);print("GRANDCHILD="+str(os.getpid()),flush=True);time.sleep(30)'
    child_code='import subprocess,sys,time; p=subprocess.Popen([sys.executable,"-c",'+repr(grandchild_code)+']); print("CHILD="+str(__import__("os").getpid()),flush=True);time.sleep(30)'
    raise SystemExit(run_console([sys.executable,"-c",child_code]))

master,slave=pty.openpty();before=termios.tcgetattr(slave)
p=subprocess.Popen([sys.executable,__file__,"parent"],stdin=slave,stdout=slave,stderr=slave,start_new_session=True)
child=grandchild=None
try:
    output=b"";deadline=time.monotonic()+8
    while (b"CHILD=" not in output or b"GRANDCHILD=" not in output) and time.monotonic()<deadline:
        ready,_,_=select.select([master],[],[],.2)
        if ready:output+=os.read(master,4096)
    if b"CHILD=" not in output or b"GRANDCHILD=" not in output:raise RuntimeError("fixture setup failed "+repr(output))
    child=int(output.split(b"CHILD=")[1].splitlines()[0])
    grandchild=int(output.split(b"GRANDCHILD=")[1].splitlines()[0])
    os.kill(p.pid,signal.SIGINT);rc=p.wait(timeout=8)
    def state(pid):
        try:
            with open(f"/proc/{pid}/stat") as f:return f.read().split(") ")[1].split()[0]
        except FileNotFoundError:return "gone"
    time.sleep(.1)
    print("launcher_return",rc,"terminal_restored",termios.tcgetattr(slave)==before,
          "child_state",state(child),"grandchild_state",state(grandchild),flush=True)
    if state(grandchild) not in ("gone","Z"):
        print("NEGATIVE_REPRODUCED: orphan grandchild remains alive after launcher returned",flush=True)
    else:print("NO_ORPHAN_REPRODUCED",flush=True)
finally:
    if p.poll() is None:p.kill();p.wait()
    for pid in (grandchild,child):
        if pid:
            try:os.kill(pid,signal.SIGKILL)
            except ProcessLookupError:pass
    os.close(master);os.close(slave)
