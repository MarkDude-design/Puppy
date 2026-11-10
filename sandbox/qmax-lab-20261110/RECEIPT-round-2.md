# RECEIPT.md: Qmax H2 Boundary Probe (Round 2)

## Question
How fast can a guest failure exit look host-like? (Where is the real boundary between a host environment failure and a guest implementation failure in a TCG environment?)

## Hypothesis
A guest failure configured with `panic=1` and `-no-reboot` will exit significantly faster than a timeout, but will strictly take longer than a host failure (e.g., invalid path) because QEMU must successfully load and begin executing the kernel binary. The fundamental discriminator is not a fixed time threshold, but the presence of the kernel's early boot stub output (e.g., "Decompressing Linux") in the serial log, which occurs before any panic can be triggered.

## Test
Run two QEMU invocations via `.github/workflows/qmax-h2-boundary.yml`:
1. **Host Failure Simulation:** `qemu-system-x86_64 -nographic -kernel /nonexistent -no-reboot`. Record exit code, time, and serial log size.
2. **Fast Guest Failure Simulation:** `qemu-system-x86_64 -nographic -kernel <valid_kernel> -append "console=ttyS0 panic=1" -no-reboot`. Record exit code, time, and serial log size.
Compare `T_host` vs `T_guest` and check serial log for "Decompressing Linux".

## Expected Output
- Host test: Exit != 0, T_host < 0.5s, Serial Log Size == 0.
- Guest test: Exit != 0 (typically 1), T_guest > T_host, Serial Log contains "Decompressing Linux".

## STOP Condition
Both QEMU runs complete. Runner splices actual results into this RECEIPT.md and commits with [skip ci].

## Actual Result
**[AWAITING RUNNER SPLICE]**
