# EVOO local-build preparation — Meraki, 2026-11-21

## Owner-provided laptop evidence

Installed Lubuntu on EVOO EV-C-116-7BK; native Linux preference supersedes WSL.
Git 2.53.0, Python 3.14.4, QEMU 10.2.1.
Accepted ZIP verification passed with 4,040,866 bytes of kernel + initramfs.
Interactive guest output included Linux 6.18.7, uptime, periodic HELLO and
`Hello_Puppf`. Following the requested Ctrl+C return check, Mark supplied
`host-ok`. This is owner-mediated local evidence, not agent execution on the laptop.
QEMU survivor/PID inspection and a second clean full cycle were not supplied;
no full M2 acceptance is declared. Mark explicitly says the M2 receipt is not a
blocker for build preparation and attributes some earlier input errors to typing.

Root filesystem: 57G total, 7.5G used, 46G available.
RAM: 3.6Gi total, 1.5Gi available; swap 511Mi, unused.
Only one Wi-Fi interface connected, second disconnected. No cause for network
failures is established; no Wi-Fi settings were changed by this session.
Removable FAT card identified separately from internal eMMC. Accepted ZIP copied
to the card and owner-provided SHA256 matched
dd333e9d6fd6a7e02e757488c872c3eb8edabe1b334b5345fdf2fd96426917b2.
Do not publish hardware serials or credentials.

## Candidate implementation and validation

Added local.py as a separate entrypoint/subclass. Existing driver.py, source lock,
guest, launcher and accepted ZIP unchanged. Preflight-only default, explicit
--build, fresh external local paths, clean checkout, one top-level make job AND
BR2_JLEVEL=1, 24-hour compile limit, host resource checks, authenticated sources,
existing config/static audits and two real QEMU boot checks when executed.
Retains work/logs; no automatic retries/deletions/uploads. No CI impersonation.

Local fixture validation in shared Codex workspace:
64 unittest tests passed, including five new local controls for recursive job
limits, preserved/refused existing run, checkout path rejection, actionable
low-swap block, and preflight not downloading/compiling.
These tests do not demonstrate a source download, compilation, QEMU boot or
laptop performance through this new entrypoint. Actual laptop preflight pending.
No paid API, workflow dispatch, merge, or source build performed.

Astra 6 versus 6.2 role-direction work belongs to another Meraki thread; this
receipt concerns Puppf and does not change those roles.
