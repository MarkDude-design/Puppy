# Try Puppf in a terminal

M1 is accepted: build #11 compiled and passed both real serial-shell boots. This
M2 launcher is a review candidate. A first-user interactive demo through this
wrapper is still required before calling M2 accepted.

## What you need

- A Linux or macOS terminal, Python 3.10 or later, and `qemu-system-x86_64` on PATH.
  QEMU 8.2.2 was used for M1's hosted boots. This wrapper has not yet been boot
  tested with QEMU on Linux/macOS; WSL and Apple Silicon are also untested.
- A checkout of this launcher and its adjacent `accepted-build.json`.
- The **original evidence ZIP for accepted build #11**. Keep it zipped.

On Debian/Ubuntu, QEMU's system-x86 package is named `qemu-system-x86`; on macOS,
Homebrew's package is `qemu`. Install through your host's normal package manager
if needed. The launcher installs nothing and makes no network requests.

Get the accepted ZIP from [run #11's artifact](https://github.com/MarkDude-design/Puppy/actions/runs/41773110103/artifacts/13296779743)
before November 6 at 9:13 p.m. PST, or from the retained
[puppf-build-11-evidence.zip](https://chatgpt.com/library?file_id=libfile_4d168bd731d88191b75d5c570f1dcad8&account_id=personal).
The GitHub download can require sign-in; the local launcher itself does not.
If the saved filename differs, pass its actual path. Do not unzip and re-zip it:
the launcher requires the exact accepted ZIP digest and both image hashes.

## Launch

From the repository root, substitute the ZIP's actual location:

```sh
python3 puppy-p0a/launch.py --evidence ~/Downloads/puppf-build-11-evidence.zip
```

The launcher verifies the ZIP and image bytes, copies only the two known image
members into a private temporary directory, and starts QEMU. It never extracts
arbitrary archive paths, runs evidence scripts, rebuilds, or dispatches Actions.
The accepted kernel and initramfs total **4,040,866 bytes**. They are identified
in `accepted-build.json`, bound to run #11 and its source commit.

## Thirty-second demo

At `PUPPF#`, first type `stty echo` and press Enter. You will not see that first
command as you type it: the accepted init script disables echo. It enables
visible typing for this guest session without modifying the accepted image.
Then type each line and read its real guest output:

```sh
uname -a
cat /proc/uptime
echo Hello_Puppf
```

The guest emits another HELLO every 120 seconds, so one may interrupt a prompt.
If you skip `stty echo`, commands still work; they just are not shown while you
type. That is existing M1 image behavior.

**Press Ctrl+C to stop the VM and return to your host terminal.** This launcher
reserves Ctrl+C for stopping QEMU, rather than interrupting a guest command. It
restores host terminal settings and removes temporary image copies afterward.
Guest `exit` restarts the guest shell because PID 1 keeps it alive; it does not
close the VM. Guest changes disappear when QEMU stops. The original ZIP stays.

## Check without booting

```sh
python3 puppy-p0a/launch.py --evidence ~/Downloads/puppf-build-11-evidence.zip --verify-only
python3 puppy-p0a/launch.py --evidence ~/Downloads/puppf-build-11-evidence.zip --check
```

`--verify-only` checks accepted bytes without requiring QEMU. `--check` also
checks the host platform and QEMU executable's presence; it does not execute
QEMU or establish compatibility/boot success. Missing files, changed bytes,
missing QEMU, or noninteractive launch produce a clear error and exit 2. QEMU's
own nonzero return is propagated; a deliberate Ctrl+C returns 0.

## VM settings and scope

One x86-64 CPU, software emulation (TCG), 128 MiB allocated, serial console, no
display, no monitor, no NIC, no host disks or shared folders. The explicit stdio
character device enables terminal signals for Ctrl+C; `-no-user-config` prevents
implicit host QEMU configuration from adding devices. The guest contract matches
M1. QEMU documents these options in its
[invocation reference](https://www.qemu.org/docs/master/system/qemu-manpage.html).
This is a disposable experiment, not a security containment product or release.
No ISO, hardware boot, persistence, networking, GUI, or model API is added.

M1's two boots prove the accepted image under its hosted command. Launcher tests
prove byte rejection, argument construction and cleanup of real local child
processes through a pseudo-terminal. Those child processes are Python fixtures,
not QEMU. This workspace lacks QEMU, so the first real interactive wrapper demo
is explicitly pending. Record host OS/QEMU version, the three guest responses,
and return to the host after Ctrl+C; do not infer that demo from test counts.
