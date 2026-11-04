# M2 launcher candidate — November 4, 2026

Base: accepted M1 merge `e0b5e0e4b206c30ca3bcbfcf08c764a2acf19808`.
Status: REVIEW CANDIDATE; FIRST-USER INTERACTIVE QEMU DEMO PENDING.

Mark accepted M1 and authorized M2 in [owner record 6630735320](https://github.com/MarkDude-design/Puppy/issues/15#issuecomment-6630735320).
This candidate adds an offline local Python launcher for accepted build #11,
exact ZIP/image pins, a short demo, explicit host requirements and terminal
cleanup. It updates stale status documentation and records the login post-mortem.
Frozen packet, guest image, source lock, builder, hosted workflow and pending
PR #20 are unchanged. No new hosted run or paid provider was invoked.

## Evidence

- 197 tests passed: 15 launcher, 59 core, 94 frozen acceptance, 8 workflow and
  21 agent-desk. Logs and exit codes are included. The existing 182 are regression
  checks; they are not 182 new launcher cases.
- `launch.py --verify-only` authenticated the actual original accepted ZIP and
  its kernel/initramfs. This exercised production byte validation.
- Actual `--check` returned exit 2 because this workspace lacks QEMU. That is
  recorded as BLOCKED for interactive wrapper testing, not a passing boot.
- Real Python child processes over a pseudo-terminal tested failure propagation,
  Ctrl+C, a repeated interrupt with a stubborn child, reaping and terminal
  restoration. These are process integration tests, not QEMU emulation.
- Astra independently reviewed artifact handling and reproduced/falsified the
  original repeated-interrupt cleanup. After the fix, it independently tested
  interrupts to the whole fixture process group and confirmed child reaping and
  exact terminal restoration. Its final review follows verbatim below.

M1's two real boots remain preserved separately. There is no evidence here of
M2's unfamiliar-user typing demo, native Windows use, WSL/macOS compatibility,
minimum memory, bit-identical rebuild, containment or release acceptance. QEMU
presence checks do not prove its version or compatibility. The supported first
wrapper target is a Linux/macOS terminal with Python 3.10+; host demo is pending.

## Independent Astra final review — verbatim

**No remaining in-scope blocker.**

Found and reproduced a repeated-Ctrl+C bug that left the child running and terminal unrestored. The fix now passes independent process-group interruption testing: exit 0, child reaped, terminal restored. All 15 launcher tests passed.

Confirmed `-no-user-config` is present, documented, and covered by the argument test. Artifact verification and extraction remain narrowly bound to the accepted ZIP and image hashes.

M2’s actual interactive QEMU demo remains pending, accurately stated in `LAUNCH.md`. Review was read-only; no files changed by me.

## Review identity and next gate

Astra is the same explicitly invited native `gpt-6-astra` reviewer from M1,
using a separate prompt on shared workspace/tool infrastructure. The reviewer
performed its own bounded reproduction; this is not a claim of independent
security principals or a separate provider bill. Meraki wrote the implementation
and regression test. No provider billing telemetry is inferred from native usage.

Next: review this PR, then perform the [interactive demo](../../../../puppy-p0a/LAUNCH.md)
on the user's chosen QEMU-equipped machine. Record host/QEMU versions, real
`uname -a`, `/proc/uptime`, `echo` output and return to host after Ctrl+C. Keep
M2 acceptance with Mark; no automatic merge, release, installation or dispatch.
