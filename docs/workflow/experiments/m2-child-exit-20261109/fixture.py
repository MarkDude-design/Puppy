import os, pty, select, signal, subprocess, sys, termios
# Replicate unchanged run_console from draft PR #21; synthetic child, not QEMU.
def run_console(argv):
    original = termios.tcgetattr(sys.stdin.fileno())
    proc = None
    try:
        proc = subprocess.Popen(argv)
        return proc.wait()
    except KeyboardInterrupt:
        print('\nStopping Puppf; guest changes are discarded.', flush=True)
        return 0
    finally:
        previous_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            if proc is not None and proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill(); proc.wait(timeout=3)
        finally:
            try: termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, original)
            finally: signal.signal(signal.SIGINT, previous_handler)

pid, fd = pty.fork()
if pid == 0:
    before = termios.tcgetattr(0)
    status = run_console([sys.executable,'-c','import sys,termios; a=termios.tcgetattr(0); a[3] &= ~termios.ECHO; termios.tcsetattr(0,termios.TCSANOW,a); sys.exit(7)'])
    after = termios.tcgetattr(0)
    print('FIXTURE exit='+str(status)+' restored='+str(before==after),flush=True)
    os._exit(0 if status==7 and before==after else 9)
output=b''
while True:
    r,_,_=select.select([fd],[],[],3)
    if not r:break
    try: chunk=os.read(fd,4096)
    except OSError:break
    if not chunk:break
    output+=chunk
_,st=os.waitpid(pid,0)
print(output.decode(errors='replace').strip())
print('harness_exit='+str(os.waitstatus_to_exitcode(st)))
assert os.waitstatus_to_exitcode(st)==0 and b'FIXTURE exit=7 restored=True' in output
