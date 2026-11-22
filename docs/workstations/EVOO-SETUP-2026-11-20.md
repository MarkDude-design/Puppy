# EVOO Puppf workstation setup — 2026-11-20

Status: prepared instructions; nothing installed on Mark's laptop by this session.
6.1 Astra review REQUESTED / NOT PERFORMED: exact model unavailable in this session.
6.2 Astra review: completed on prepared document; two requested corrections incorporated below.
Review is advisory; no laptop installation or real WSL boot was observed.
No hardware formatting, Windows replacement, credential changes, merge or build dispatch.

## Hardware and corrected project state

Owner's photograph: Intel Celeron N4000, 4 GB RAM (3.83 GB usable), x64 Windows.
Latest storage photo: C: 56.8 GB total, 27.0 GB used, **29.7 GB already free**.
Videos occupy 2.65 GB in that photo; removing them is optional and not needed for the first console demo.
Owner also has a 64 GB microSD and may buy a larger one. Actual card speed, filesystem,
capacity compatibility, and bootability are unverified.

M1 was accepted November 4 after build #11 passed two genuine QEMU boots.
Owner receipt: https://github.com/MarkDude-design/Puppy/issues/15#issuecomment-6630735320
Saved image pair totals 4,040,866 bytes. No rebuild is needed for first use.
The older README and November 20 bus note describing the signing-key blocker are stale.
M2 launcher PR #21 remains a draft, unmerged; first real interactive launcher demo
and WSL compatibility remain unproven:
https://github.com/MarkDude-design/Puppy/pull/21

## Two suggestions

| Route | Purpose | Tradeoff |
| --- | --- | --- |
| 1. Keep Windows; add WSL2 + Ubuntu 24.04 | Recommended first: run accepted image and verify console | Reversible installation; Windows and Linux share tight 4 GB RAM; WSL2 needs firmware virtualization |
| 2. Native lightweight Linux from external media | Later: dedicate more RAM/CPU to sustained source builds | Requires tested USB boot, hardware compatibility and explicit installation target; built-in microSD boot cannot be assumed |

Start with route 1. Keep the microSD for original ZIPs and compressed snapshots.
A larger card increases capacity, not necessarily speed. Measure before purchasing for performance.
For route 2, first try a live USB without installing; check Wi-Fi, keyboard, touchpad,
storage and shutdown. A native ext4 build volume is appropriate. An external USB SSD
is a possible later improvement, not a prerequisite for this first demo.
A local full Buildroot build's capacity and completion time are NOT established by these photos.

## Minimal apps

| App/tool | Install location | Purpose |
| --- | --- | --- |
| Existing Edge or Chrome | Windows; already visible in screenshot | ChatGPT at https://chatgpt.com and Le Chat at https://chat.mistral.ai |
| Windows Terminal | Windows; use existing installation or Microsoft Store | PowerShell and Ubuntu terminals |
| WSL2 + Ubuntu-24.04 | Windows feature + Linux distribution | Host the POSIX launcher and QEMU |
| git, python3, qemu-system-x86, ca-certificates | Inside Ubuntu | Fetch reviewed source, verify accepted image, emulate x86 guest |
| Mistral Vibe CLI | Optional later inside Ubuntu | Agent access to local files/commands, beyond browser chat |

Browser chat is enough to start GPT and Mistral assistance. No local model weights are needed.
A browser conversation does not automatically gain access to this laptop's files or terminal.
Optional agent CLIs require their own setup/authentication; subscription/API entitlements
must be checked before calls. Never put API keys or account credentials on the public bus.
Mistral's current official Vibe installation/authentication instructions:
https://docs.mistral.ai/vibe/code/cli/install-setup
CLI installation and metered calls are not part of the first boot checklist.

## Step 1 — inspect Windows (Mark, on the EVOO)

Open Start, search **Terminal**, choose PowerShell. Run these read-only checks:

~~~powershell
Get-Volume -DriveLetter C | Select-Object DriveLetter, Size, SizeRemaining
Get-CimInstance Win32_Processor | Select-Object Name, VirtualizationFirmwareEnabled
wsl --version
wsl --status
wsl --list --verbose
~~~

If WSL is absent, errors from the last three commands are useful evidence, not a broken laptop.
Check Windows version with **Win+R**, enter **winver**.
The supported install command needs Windows 10 build 19041 or later, or Windows 11.
If Windows Terminal is absent, use Start > Windows PowerShell for Windows commands
and Start > Ubuntu 24.04 for Linux commands.
Open **Task Manager > Performance > CPU**, record **Virtualization: Enabled/Disabled**.
If disabled, stop before changing firmware and identify the exact EVOO model and its instructions.
Do not publish device/product IDs, account names or personal file listings.

## Step 2 — install WSL if needed (Mark, on the EVOO)

Keep Windows. Save open work first. Open **Terminal > Run as administrator**.
If WSL already exists, inspect installed distributions before adding another.

~~~powershell
wsl --list --online
~~~

If Ubuntu-24.04 is listed and no suitable Ubuntu instance already exists:

~~~powershell
wsl --install -d Ubuntu-24.04
~~~

Restart if prompted. Open **Ubuntu 24.04** from Start and create its Linux username/password locally.
The Windows administrator prompt and Linux password are entered on the laptop, never in chat.
If the current WSL app is too old for the distribution package, use Microsoft's supported
`wsl --update` route and retry only after reading the actual error.
Canonical's current tar-format Ubuntu package requires WSL app 2.4.10 or newer.
Confirm with `wsl --list --verbose` that Ubuntu runs as VERSION 2.

Optional starting resource budget for this 4 GB machine:
merge the following into an existing **%UserProfile%\.wslconfig**; do not overwrite other settings.

~~~ini
[wsl2]
memory=2GB
processors=2
swap=1GB
~~~

These are proposed limits, not laptop-tested tuning. Swap consumes internal disk and may be slow.
To apply changed limits, save work in all WSL sessions, then run `wsl --shutdown`
in PowerShell; it stops all WSL distributions. Reopen Ubuntu afterward.

## Step 3 — install only the first-demo tools (Ubuntu terminal)

~~~sh
sudo apt-get update
sudo apt-get install --no-install-recommends git python3 qemu-system-x86 ca-certificates
python3 --version
qemu-system-x86_64 --version
free -h
df -h "$HOME"
~~~

Keep Linux source/checkouts in Ubuntu's Linux home, not /mnt/c or a OneDrive sync folder.
Use one AI browser tab at a time during QEMU testing if memory is tight.
The launcher uses software emulation; it does not require nested KVM.
WSL2 itself still requires virtualization support.

## Step 4 — obtain exact inputs (no new build)

From the browser signed into Mark's own account, download the retained original:
[puppf-build-11-evidence.zip](https://chatgpt.com/library?file_id=libfile_4d168bd731d88191b75d5c570f1dcad8&account_id=personal).
The old GitHub artifact link had short retention; do not depend on its continued availability.
Keep the ZIP unchanged; do not unzip/re-zip it.

In Ubuntu, obtain the reviewed launcher candidate without merging:

If Puppy already exists there, stop and choose a separate directory before running this block.
The commands stop advancing if clone, fetch or checkout fails:

~~~sh
mkdir -p "$HOME/puppf-work" &&
cd "$HOME/puppf-work" &&
git clone --no-checkout https://github.com/MarkDude-design/Puppy.git &&
cd Puppy &&
git fetch origin refs/pull/21/head &&
git checkout --detach 320ed447f8b951d2215f0b7ac5967874b616750e &&
git rev-parse HEAD
~~~

If Puppy already exists, use a separate directory; do not overwrite local edits.
The expected checkout is 320ed447f8b951d2215f0b7ac5967874b616750e, the PR #21 candidate.
Do not substitute main, which does not yet contain launch.py.

Place the original ZIP at **$HOME/puppf-work/puppf-build-11-evidence.zip**.
You can open Ubuntu's home from Windows Explorer by running `explorer.exe .`
from `cd "$HOME/puppf-work"`, then copy the downloaded ZIP into that folder.

Expected original ZIP SHA-256:
`dd333e9d6fd6a7e02e757488c872c3eb8edabe1b334b5345fdf2fd96426917b2`.

From the Puppy checkout:

~~~sh
python3 puppy-p0a/launch.py --evidence "$HOME/puppf-work/puppf-build-11-evidence.zip" --verify-only
python3 puppy-p0a/launch.py --evidence "$HOME/puppf-work/puppf-build-11-evidence.zip" --check
~~~

Both must exit successfully before any interactive boot. --check checks executable presence,
not actual QEMU compatibility. Record versions and exact errors; do not bypass hash failures.

## Step 5 — first actual console demo, after reviews

The requested 6.1 Astra review remains outstanding until a real review is supplied.
Record 6.2's disposition separately. Reviews do not establish host readiness.
When review findings are resolved and the laptop prechecks pass, in an interactive Ubuntu terminal,
record existing QEMU processes before launching:

~~~sh
pgrep -af '[q]emu-system-x86_64'
python3 puppy-p0a/launch.py --evidence "$HOME/puppf-work/puppf-build-11-evidence.zip"
printf 'Launcher exit status: %s\n' "$?"
pgrep -af '[q]emu-system-x86_64'
~~~

At PUPPF#, type `stty echo` once (that first command is invisible while typing), then:

~~~sh
uname -a
cat /proc/uptime
echo Hello_Puppf
~~~

Press **Ctrl+C** to return to Ubuntu. Confirm host typing works and no new QEMU instance survives (compare the process lists).
The exit-status and process-list commands above execute after the launcher returns.
A pgrep exit of 1 with no output means no matching process.
Record real guest output, host/QEMU versions, exit status and terminal cleanup.
Failure or unresponsive interaction means STOP with the actual error; not M2 acceptance.
A 128 MiB offline guest is used, with no host disks/shared directories.
The guest receives no host disks or shared folders. Host installation, downloads,
swap and temporary files do write laptop storage. No bootable media is flashed.
M2 acceptance remains Mark's decision.

## Step 6 — later source build

The existing CI driver deliberately requires GitHub Actions variables, disposable-runner
paths and build mode. **Do not spoof GITHUB_ACTIONS or run run-ci.sh as a local shortcut.**
Its current builder chooses up to four jobs and only checks a 10 GiB disk floor;
those settings do not prove suitability for this 4 GB Windows host.

Prepare a separately reviewed local-runner adaptation with explicit output paths,
a one-job starting limit, disk/RAM checks and the same source/signature validation.
Reuse frozen packet, source versions and two-boot acceptance. Measure actual disk peak,
elapsed time and swap before increasing parallelism or promising a larger build.
No such adaptation or source build is claimed by this setup document.

## Storage and backup

- Internal: Windows + WSL distribution + first-demo checkout and small accepted image.
  Keep room for Windows maintenance; recheck free space after installing.
- microSD: original accepted ZIP and compressed snapshots initially. Treat it as removable.
  Do not put a live WSL virtual disk or active Linux build tree on an untested card.
- Native Linux later: build on a native Linux filesystem such as ext4.
  FAT/exFAT do not preserve all Linux build-tree semantics.
- OneDrive: upload compressed snapshots, final artifacts and logs after work stops.
  Cloud capacity is not working disk space. Do not sync the live WSL virtual disk/build tree.
  Exclude credentials, agent authentication directories and private personal material.
- No card formatting, OS deletion or firmware changes are included in these commands.

## Evidence and reviews

Prepared in ChatGPT; no connection to the EVOO's operating system has been established.
Installing in this cloud workspace would not install anything on the laptop.
Astra 6.1: REQUESTED, exact model unavailable; no substitute is represented as that review.
Astra 6.2: read-only review completed on the concrete document. Requested fail-fast
checkout commands and precise host-storage wording; both incorporated. Recommended
capturing launcher exit status and before/after QEMU process lists; incorporated.
Native review billing telemetry: null/unknown; no external provider API call initiated.
Laptop installs / artifact verification / real demo / local source build: NOT RUN here.

Official references:
- https://learn.microsoft.com/en-us/windows/wsl/install
- https://learn.microsoft.com/en-us/windows/wsl/wsl-config
- https://learn.microsoft.com/en-us/windows/wsl/filesystems
- https://ubuntu.com/wsl/docs/latest/howto/install-ubuntu-wsl2/
- https://docs.mistral.ai/vibe/code/cli/install-setup
- https://buildroot.org/downloads/manual/manual.html
